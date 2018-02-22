# Copyright 2017 Interana, Inc.
from base import CommandHandler, SubCommandHandler


class LookupHandler(CommandHandler):

    name = 'lookup'
    description = 'Commands for managing lookup tables for a customer'

    def __init__(self):
        CommandHandler.__init__(self)

        self.register_subcommands(LookupCreate(),
                                  LookupList(),
                                  LookupUpdate(),
                                  LookupDelete(),
                                  LookupRestore(),
                                  LookupAttach(),
                                  LookupDetach())


class LookupCreate(SubCommandHandler):

    name = 'create'
    description = 'Create a new lookup table.'

    def parser_setup(self, sps):
        parser = self.init_parser(sps)
        return parser


class LookupList(SubCommandHandler):

    name = 'list'
    description = 'List existing lookup tables.'

    def parser_setup(self, sps):
        parser = self.init_parser(sps)
        return parser


class LookupUpdate(SubCommandHandler):

    name = 'update'
    description = 'Update an existing lookup table.'

    def parser_setup(self, sps):
        parser = self.init_parser(sps)
        return parser


class LookupDelete(SubCommandHandler):

    name = 'delete'
    description = 'Mark a lookup table as deleted.'

    def parser_setup(self, sps):
        parser = self.init_parser(sps)
        return parser


class LookupRestore(SubCommandHandler):

    name = 'restore'
    description = 'Restore a deleted lookup table.'

    def parser_setup(self, sps):
        parser = self.init_parser(sps)
        return parser


class LookupAttach(SubCommandHandler):

    name = 'attach'
    description = 'Attach a lookup table to an event table'

    def parser_setup(self, sps):
        parser = self.init_parser(sps)
        return parser


class LookupDetach(SubCommandHandler):

    name = 'detach'
    description = 'Detach a lookup table from an event table'

    def parser_setup(self, sps):
        parser = self.init_parser(sps)
        return parser
