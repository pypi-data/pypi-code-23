"""Plex syncing"""
from plexapi.myplex import MyPlexAccount
from plexapi.video import Movie, Episode
import plexapi.utils
import json
import time
import logging
import argparse

logger = logging.getLogger("plex-sync")
logger.addHandler(logging.NullHandler())

SECONDS_90_DAYS = 7776000

def mark_watched(server, item, watched=True):
    if watched:
        logger.debug("Marking item %s watched on %s", item, server.friendlyName)
        server.library.fetchItem(item).markWatched()
    else:
        logger.debug("Marking item %s unwatched on %s", item, server.friendlyName)
        server.library.fetchItem(item).markUnwatched()

def mark_unwatched(server, item):
    mark_watched(server, item, watched=False)

def set_view_offset(server, item, offset):
    logger.debug("Setting view offset to %d on %s", offset, server.friendlyName)
    server.library.fetchItem(item).updateProgress(time=offset, state='stopped')

def load_data_file(file_name):
    logger.debug("Loading data file %s", file_name)
    with open(file_name, mode='r') as input_file:
        return json.load(input_file)

def save_data_file(file_name, data):
    logger.debug("Saving data file %s", file_name)
    with open(file_name, mode='w') as output_file:
        json.dump(data, output_file)

def _filter_to_videos(sequence):
    """Filters a sequence to only include objects that are Movies or Episodes.
    """

    for element in sequence:
        if isinstance(element, (Movie, Episode)):
            yield element

def load_sync_list(servers, last_sync_time):
    """Loads a list of GUIDs that should have their statuses synced.

    Uses the on-deck and watch history lists to avoid parsing the entire library.
    
    Arguments:
        servers {list(Server)} -- the list of servers from which to pull GUIDs
        last_sync_time {int} -- the last time that sync was performed (history items
            before this time will be ignored)
    """

    logger.info("Loading sync list.")
    sync_list = []
    # Query each server
    for plex in servers:
        server_name = plex.friendlyName
        logger.debug("Loading data from %s", server_name)
        logger.debug("Loading history")
        history = plex.fetchItems('/status/sessions/history/all', viewedAt__gt=last_sync_time)
        logger.debug("Loading on deck")
        on_deck = plex.library.onDeck()

        # Filter the lists to only include GUIDs from Movies and TV Shows
        history_guids = [hist.guid for hist in _filter_to_videos(history) if hist.guid is not None]
        on_deck_guids = [deck.guid for deck in _filter_to_videos(on_deck) if deck.guid is not None]

        sync_list.extend(history_guids)
        sync_list.extend(on_deck_guids)

    # Eliminate duplicate GUIDs
    sync_list = list(set(sync_list))
    return sync_list


def lookup_key(server, guid):
    """Looks up the key for the given GUID on the provided server.

    Returns None if it cannot be found.
    """

    logger.debug("Looking up key for guid %s on %s", guid, server.friendlyName)
    result = server.query(key='/library/all{}'.format(plexapi.utils.joinArgs({'guid': guid})))
    try:
        result = server.findItems(result)[0]
    except IndexError:
        logger.error("Could not locate guid %s on %s.", guid, server.friendlyName)
        return None
    logger.debug("Parsed as %s with key %s", result, result.key)
    return result.key

def create_changeset(servers, sync_list, previous_state):
    """Loads playback state for each media element in the sync list.
    """
    logger.info("Creating changeset.")
    media_state = {}
    changeset = {}

    # Initialize changeset
    for server in servers:
        changeset[server.friendlyName] = []

    # Process each sync item
    for guid in sync_list:
        previous = None
        if previous_state is not None and guid in previous_state:
            previous = previous_state[guid]

        # Gather state from each server
        current = _get_states_from_servers(servers, guid)

        contributing_server_names = current.keys()

        new_state = {}

        _merge_watched_states(current, contributing_server_names, previous, new_state)
        _merge_view_offset(previous, current, contributing_server_names, new_state)
        _assemble_changeset(contributing_server_names, current, new_state, changeset)

        # Save new state
        media_state[guid] = new_state

    return media_state, changeset

def _assemble_changeset(contributing_server_names, current, new_state, changeset):
    # Assemble changeset
    for server_name in contributing_server_names:
        changes = {
            'Title': current[server_name]['Title']
        }
        has_changed = False
        if current[server_name]['Is Watched'] != new_state['Is Watched']:
            changes['Is Watched'] = new_state['Is Watched']
            has_changed = True
        if current[server_name]['View Offset'] != new_state['View Offset']:
            changes['View Offset'] = new_state['View Offset']
            # Force the item to be marked watched again if it is watched and the new
            # view offset is 0. This handles the edge case where setting the view
            # offset to 0 does not work.
            if changes['View Offset'] == 0:
                changes['Is Watched'] = new_state['Is Watched']
            has_changed = True
        if has_changed:
            changes['Key'] = current[server_name]['Key']
            changeset[server_name].append(changes)

def _merge_view_offset(previous, current, contributing_server_names, new_state):
    # Merge view offset
    if (previous is None) or (previous['View Offset'] == 0):
        # There was no previous state or the previous state had no view offset
        # The new offset is the larger of the view offsets
        new_state['View Offset'] = max(
            [current[server_name]['View Offset'] for server_name in contributing_server_names]
        )
    elif (previous is not None) and (previous['View Offset'] > 0):
        # There was a previous view offset
        # The new offset is the largest of the view offsets that are different from
        # the previous
        new_view_offsets = set([current[server_name]['View Offset'] for server_name in contributing_server_names]) - \
            set([previous['View Offset']])
        if new_view_offsets:
            new_state['View Offset'] = max(new_view_offsets)
        else:
            new_state['View Offset'] = previous['View Offset']
    else:
        new_state['View Offset'] = 0

def _merge_watched_states(current, contributing_server_names, previous, new_state):
    watched_count = sum([current[server_name]['Is Watched'] for server_name in contributing_server_names])
    one_is_watched = bool(watched_count > 0)
    all_are_watched = bool(watched_count == len(contributing_server_names))

    # Merge watched state
    if ((previous is None) or (not previous['Is Watched'])) and one_is_watched:
        # There was no previous state or the previous state was unwatched, and
        # at least one server is now reporting a watched state
        new_state['Is Watched'] = True
    elif ((previous is not None) and (previous['Is Watched'] is True)) and not all_are_watched:
        # The previous state was watched, and now at least one server is reporting not watched
        new_state['Is Watched'] = False
    elif previous is not None:
        new_state['Is Watched'] = previous['Is Watched']
    else:
        new_state['Is Watched'] = False

def _get_states_from_servers(servers, guid):
    value = {}
    for server in servers:
        key = lookup_key(server, guid)
        if key is None:
            continue
        media = server.fetchItem(key)
        value[server.friendlyName] = {
            'Title': media.title,
            'View Offset': media.viewOffset,
            'Is Watched': media.isWatched,
            'Key': media.key
        }
    return value

def apply_changeset(servers, global_changeset, dry_run):
    logger.info("Applying changset.")
    for server in servers:
        server_name = server.friendlyName
        server_changeset = global_changeset[server_name]
        for changeset in server_changeset:
            title = changeset['Title']
            if 'Is Watched' in changeset:
                new_value = "watched" if changeset['Is Watched'] else "unwatched"
                logger.info("Setting %s as %s on %s.", title, new_value, server_name)
                if not dry_run:
                    mark_watched(server, changeset['Key'], watched=changeset['Is Watched'])
            if 'View Offset' in changeset:
                logger.info("Setting %s view position as %s on %s.", title, changeset['View Offset'], server_name)
                if not dry_run:
                    set_view_offset(server, changeset['Key'], changeset['View Offset'])

def main():
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="Syncs media status between Plex servers.")
    parser.add_argument(
        '-t', '--token',
        action='store',
        help='the Plex token for the user to sync',
        required=True
    )
    parser.add_argument(
        '-s', '--server-name',
        action='append',
        help='a server name to sync',
        required=True
    )
    parser.add_argument(
        '-d', '--data-file',
        action='store',
        help='the data file containing previous states for the given user'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help="don't apply any changes, just print what would happen"
    )
    args = parser.parse_args()
    token = args.token
    server_names = args.server_name
    data_file_name = args.data_file
    dry_run = args.dry_run

    if not data_file_name:
        data_file_name = "plex_states_{0}.json".format(token)

    new_data = {
        'Last Sync Time': int(time.time())
    }
    previous_data = None
    last_sync_time = int(time.time() - SECONDS_90_DAYS)
    try:
        data_file = load_data_file(data_file_name)
        if 'Last Sync Time' in data_file:
            last_sync_time = data_file['Last Sync Time']
        previous_data = data_file['State']
    except FileNotFoundError:
        logger.warning("Previous data file not found. Starting fresh.")

    account = MyPlexAccount(token=token)
    servers = []
    for server_name in server_names:
        servers.append(account.resource(server_name).connect())

    sync_list = load_sync_list(servers, last_sync_time)
    new_state, changeset = create_changeset(servers, sync_list, previous_data)
    apply_changeset(servers, changeset, dry_run)

    new_data['State'] = new_state
    if not dry_run:
        save_data_file(data_file_name, new_data)

if __name__ == "__main__":
    main()
