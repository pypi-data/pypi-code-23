# Copyright 2017 Interana, Inc.
'''
ia tier rebalance
'''

from base import CommandHandler, SubCommandHandler, DoResult
from interana.utils.shared_parsers import add_output_parameters, add_run_mode
import json


class TierHandler(CommandHandler):

    name = 'tier'
    description = 'Commands for cross-tier work.'

    def __init__(self):
        CommandHandler.__init__(self)

        self.register_subcommands(Rebalance(),
                                  StopRebalance())


class StopRebalance(SubCommandHandler):

    name = 'stop-rebalance'
    description = 'Stop ongoing string shard rebalancing (only applicable to string-tier rebalance)'

    def parser_setup(self, sps):
        parser = self.init_parser(sps)
        add_output_parameters(parser)
        parser.add_argument(
            'tier',
            help='tier to operate on',
            choices=['string'],
            type=str
        )
        return parser

    def do(self):
        if self.args.tier == 'data':
            print 'stopping data tier rebalance not supported'
        elif self.args.tier == 'string':
            return self.process_string_tier_rebalance_stop()
        else:
            print 'unknown tier'

    def process_string_tier_rebalance_stop(self):
        res = self.post('{hostname}/api/string_tier_resize/stop_rebalance')
        content = json.loads(res.content)

        headers = ['Message']
        entries = [['stopped string tier rebalance']] if content.get('success') else [[content['msg']]]

        return DoResult(headers=headers, entries=entries)


class Rebalance(SubCommandHandler):

    name = 'rebalance'
    description = 'Balance data or string shards across available nodes'

    def parser_setup(self, sps):
        parser = self.init_parser(sps)
        add_output_parameters(parser)
        parser.add_argument(
            'tier',
            help='tier to operate on',
            choices=['data', 'string'],
            type=str
        )
        group = parser.add_mutually_exclusive_group()
        group.add_argument(
            '-s',
            '--status',
            action='store_true',
            help='report current progress, does not change configuration'
        )
        group.add_argument(
            '--exclude',
            help='comma separated list of hosts to clear during rebalance',
            type=str
        )
        parser.add_argument(
            '--shard-layout-id',
            help='data shard layout to operate on (only applicable to data-tier rebalance)',
            type=int,
        )
        add_run_mode(parser)

        return parser

    def do(self):
        if self.args.tier == 'data':
            return self.process_data_tier()
        elif self.args.tier == 'string':
            return self.process_string_tier()
        else:
            print 'unknown tier'

    def process_data_tier(self):
        if self.args.status:
            return self.process_data_tier_status()
        else:
            return self.process_data_tier_rebalance()


    def process_data_tier_status(self):
        params = {'shard_layout_id': self.args.shard_layout_id}
        res = self.post('{hostname}/api/data_tier_resize/status', data=params)
        content = json.loads(res.content)

        done = True
        errors = False

        if content.get('success'):
            headers = [
                'Host', 'Status', 'Events', 'Shard Path', 'Destination Host'
            ]
            entries = []
            for c in content.get('data', []):
                if c.get('host'):
                    if c.get('status') == 'ok':
                        if str(c.get('events')) != '0':
                            done = False
                    else:
                        errors = True

                entries.append([
                    c.get('host', ''), c.get('status', ''), c.get('events', ''),
                    c.get('shard_path', ''), c.get('destination_host', '')
                ])
        else:
            headers = ['Message']
            entries = [[content['msg']]]

        if done:
            if errors:
                status = 'Rebalance is not in progress - some nodes failed to respond.'
            else:
                status = 'Rebalance is not in progress.'
        else:
            if errors:
                status = 'Rebalance is in progress - some nodes failed to respond.'
            else:
                status = 'Rebalance is in progress.'

        return DoResult(headers=headers, entries=entries, message=status)

    def process_data_tier_rebalance(self):
        params = {
            'shard_layout_id': self.args.shard_layout_id,
            'exclude': self.args.exclude,
            'run': self.args.run
        }

        res = self.post('{hostname}/api/data_tier_resize/rebalance', data=params)
        content = json.loads(res.content)

        if content.get('success'):
            headers = ['Shard Layout ID', 'Shard ID', 'Old Host', 'New Host']
            entries = []
            for sli, changes in content.get('data', {}).items():
                for row in changes:
                    entries.append([sli, row[0], row[1], row[2]])
        else:
            headers = ['Message']
            entries = [[content['msg']]]

        if not self.args.run:
            next_action = 'This is a preview mode. Rerun with --run option for changes to take effect.'
        else:
            next_action = 'The changes have been committed. Run with --status option to monitor the progress.'
        return DoResult(headers=headers, entries=entries, message=next_action)

    def process_string_tier(self):
        if self.args.status:
            return self.process_string_tier_status()
        else:
            return self.process_string_tier_rebalance()

    def process_string_tier_status(self):
        res = self.post('{hostname}/api/string_tier_resize/status')
        content = json.loads(res.content)
        if content.get('success'):
            data = content['data']
            if data['rounds_left'] == 0:
                headers = ['Status']
                status = 'No Rebalance is in progress.'
                entries = [[status]]
            else:
                headers = ['Total Number of Shards to Move', 'Rounds Left', 'Number of Shards Moving', 'Status']
                status = 'Rebalance is in progress.'
                entries = [[
                    '{0} out of {1} on this cluster.'.format(
                        data['shards_to_move'], data['total_num_shards']
                    ),
                    data['rounds_left'],
                    '{0} out of {1} for this round.'.format(
                        data['shards_moving'], data['shards_to_move_in_cur_round']
                    ),
                    status
                ]]

        else:
            headers = ['Message']
            entries = [[content['msg']]]

        return DoResult(headers=headers, entries=entries)

    def process_string_tier_rebalance(self):
        params = {
            'exclude': self.args.exclude,
            'run': self.args.run
        }

        res = self.post('{hostname}/api/string_tier_resize/rebalance', data=params)
        content = json.loads(res.content)

        if content.get('success'):
            data = content.get('data')
            num_hosts = len(data['target_hosts'])
            num_rounds = len(data['plan']) if data.get('plan') else 0

            headers = ['Number of Target Hosts', 'Rounds of Transfer Needed']
            entries = [[num_hosts, num_rounds]]

            if not self.args.run:
                headers.append('Status')

                status = 'Not running yet.' if num_rounds > 0 else 'No Rebalance is needed.'
                entries[0].append(status)

                next_action = 'This is a preview mode. Rerun with --run option for changes to take effect.'
            else:
                headers += ['Rounds Left', 'Number of Shards to Move', 'Status']

                status = 'Started.' if num_rounds > 0 else 'No Rebalance is needed.'
                entries[0] += [data['status']['rounds_left'], data['status']['shards_to_move'], status]

                next_action = 'The changes have been committed. Run with --status option to monitor the progress.'

        else:
            headers = ['Message']
            entries = [[content['msg']]]

        return DoResult(headers=headers, entries=entries, message=next_action)
