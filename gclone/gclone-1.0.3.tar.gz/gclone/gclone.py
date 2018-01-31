import argparse

# PyGithub
from github import Github

class Gclone(object):
    """gclone command line state. Provides output and handles user input."""
    STATE_LIST = 'list'
    STATE_FULL_NAME_MATCH = 'full_match'
    STATE_FULL_NAME_NO_MATCH = 'full_no_match'
    STATE_NONE = 'none'

    def __init__(self, keyword, repos):
        self._update_state(keyword, repos)

    def needs_input(self):
        """Return whether we are in a state that requires user input."""
        return self._state in [self.STATE_LIST, self.STATE_FULL_NAME_NO_MATCH]

    def handle_input(self, user_input):
        """Handle user input.

        Parameters
        ----------
        user_input : str

        Raises
        ------
        IndexError or TypeError
            If number choice is invalid.
        KeyError
            If 'y/n' input is invalid.
        """
        if user_input.isdecimal():
            i = int(user_input) - 1
            if i < 0:
                raise IndexError('negative index not allowed')
        else:
            i = user_input.lower()
        self._clone_url = self._get_choices()[i]

    def get_clone_url(self):
        """Return github clone url or None."""
        return self._clone_url

    def get_output(self):
        """Return output based on current state."""
        return self._outputs.get(self._state, None)

    def _update_state(self, keyword, repos):
        self._keyword = keyword
        self._repos = repos
        self._clone_url = None
        repo_words = keyword.split('/')
        full_name = True if len(repo_words) == 2 else False
        self._state = self.STATE_LIST
        if full_name:
            match = [repo for repo in self._repos if repo.full_name == keyword]
            if len(match) == 1:
                self._state = self.STATE_FULL_NAME_MATCH
                self._clone_repo = match[0]
                self._clone_url = match[0].clone_url
        if len(repos) == 0:
            if full_name:
                self._state = self.STATE_FULL_NAME_NO_MATCH
            else:
                self._state = self.STATE_NONE
        self._outputs = {
                self.STATE_NONE: 'No repositories found.',
                self.STATE_LIST: self._get_list_output(),
                self.STATE_FULL_NAME_NO_MATCH: self._get_no_match_output()
                }

    def _get_choices(self):
        """Return choices for selection by user input."""
        if self._state == self.STATE_LIST:
            return [repo.clone_url for repo in self._repos]
        else:
            return {'y': self._get_no_match_url(), 'n': None}

    def _get_no_match_url(self):
        gh_url_format = 'https://github.com/{}.git'
        return gh_url_format.format(self._keyword)

    def _get_no_match_output(self):
        clone_url = self._get_no_match_url()
        return "Repository not found. Clone '{}' ? (y/n) ".format(clone_url)

    def _get_list_output(self):
        longest = 0
        lefts = []
        i = 1
        for repo in self._repos:
            # Set length of string to make items line up evenly
            key_len = 4
            key = '({})'.format(i).rjust(key_len)
            left = '{} {}'.format(key, repo.full_name)
            lefts.append(left)
            length = len(left)
            if length > longest:
                longest = length
            i += 1

        lines = []
        for x in range(len(self._repos)):
            repo = self._repos[x]
            left = lefts[x].ljust(longest)
            data = '{}  {}'.format(left, repo.description)
            lines.append(data)

        lines.append('Clone which repository? ')
        return '\n'.join(lines)

class Gsearch(object):
    """Search for github repositories."""
    LIMIT_MAX = 99
    LIMIT_DEFAULT = 10

    SORT_CHOICES = ['stars', 'forks', 'updated']
    ORDER_CHOICES = ['desc', 'asc']

    def __init__(self):
        self._github = Github()

    def search(self, query, **kwargs):
        """Search for github repositories.

        Parameters
        ----------
        query : str

        Other Parameters
        ----------------
        sort : {'stars', 'forks', 'updated'}, optional
        order : {'asc', 'desc'}, optional
        limit : int, optional
            Max number of results (default is 10).

        Returns
        -------
        list
            List of repositories or an empty list.
        """
        limit = kwargs.pop('limit', self.LIMIT_DEFAULT)
        limit = min(limit, self.LIMIT_MAX)
        results = self._github.search_repositories(query, **kwargs)
        try:
            repos = [repo for repo in results[:limit]]
        except IndexError:
            repos = []

        return repos
