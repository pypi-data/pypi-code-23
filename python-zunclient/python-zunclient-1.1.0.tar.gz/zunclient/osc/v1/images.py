# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import logging

from osc_lib.command import command
from osc_lib import utils

from zunclient.common import utils as zun_utils


def _image_columns(image):
    return image._info.keys()


def _get_client(obj, parsed_args):
    obj.log.debug("take_action(%s)" % parsed_args)
    return obj.app.client_manager.container


class ListImage(command.Lister):
    """List available images"""

    log = logging.getLogger(__name__ + ".ListImage")

    def get_parser(self, prog_name):
        parser = super(ListImage, self).get_parser(prog_name)
        parser.add_argument(
            '--marker',
            metavar='<marker>',
            default=None,
            help='The last image UUID of the previous page; '
                 'displays list of images after "marker".')
        parser.add_argument(
            '--limit',
            metavar='<limit>',
            type=int,
            help='Maximum number of images to return')
        parser.add_argument(
            '--sort-key',
            metavar='<sort-key>',
            help='Column to sort results by')
        parser.add_argument(
            '--sort-dir',
            metavar='<sort-dir>',
            choices=['desc', 'asc'],
            help='Direction to sort. "asc" or "desc".')
        return parser

    def take_action(self, parsed_args):
        client = _get_client(self, parsed_args)
        opts = {}
        opts['marker'] = parsed_args.marker
        opts['limit'] = parsed_args.limit
        opts['sort_key'] = parsed_args.sort_key
        opts['sort_dir'] = parsed_args.sort_dir
        opts = zun_utils.remove_null_parms(**opts)
        images = client.images.list(**opts)
        columns = ('uuid', 'image_id', 'repo', 'tag', 'size')
        return (columns, (utils.get_item_properties(image, columns)
                          for image in images))


class PullImage(command.ShowOne):
    """Pull specified image"""

    log = logging.getLogger(__name__ + ".PullImage")

    def get_parser(self, prog_name):
        parser = super(PullImage, self).get_parser(prog_name)
        parser.add_argument(
            'image',
            metavar='<image>',
            help='Name of the image')
        return parser

    def take_action(self, parsed_args):
        client = _get_client(self, parsed_args)
        opts = {}
        opts['repo'] = parsed_args.image
        image = client.images.create(**opts)
        columns = _image_columns(image)
        return columns, utils.get_item_properties(image, columns)


class SearchImage(command.Lister):
    """Search specified image"""

    log = logging.getLogger(__name__ + ".SearchImage")

    def get_parser(self, prog_name):
        parser = super(SearchImage, self).get_parser(prog_name)
        parser.add_argument(
            '--image-driver',
            metavar='<image-driver>',
            help='Name of the image driver')
        parser.add_argument(
            'image_name',
            metavar='<image_name>',
            help='Name of the image')
        return parser

    def take_action(self, parsed_args):
        client = _get_client(self, parsed_args)
        opts = {}
        opts['image_driver'] = parsed_args.image_driver
        opts['image'] = parsed_args.image_name
        opts = zun_utils.remove_null_parms(**opts)
        images = client.images.search_image(**opts)
        columns = ('ID', 'Name', 'Tags', 'Status', 'Size', 'Metadata')
        return (columns, (utils.get_item_properties(image, columns)
                          for image in images))
