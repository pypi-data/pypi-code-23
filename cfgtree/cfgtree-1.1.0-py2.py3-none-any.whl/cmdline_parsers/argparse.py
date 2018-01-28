# coding: utf-8

# Standard Libraries
import argparse
import logging
import sys

# Cfgtree modules
from cfgtree.cmdline_parsers import CmdlineParsersBase
from cfgtree.dictxpath import make_xpath
from cfgtree.types import _UNDEFINED

log = logging.getLogger(__name__)


class ArgparseCmdlineParser(CmdlineParsersBase):
    def parse_cmd_line(self, model, argv=None):
        """
        Inject parameters provider by the user in the command line.
        """
        if argv is None:
            argv = sys.argv

        argv = argv[1:]

        parser = argparse.ArgumentParser()
        self._inject_cfg_in_parser(parser, root=model)
        args = parser.parse_args(args=argv)
        for k, v in vars(args).items():
            cfg = self._find_cfg_for_cmd_line_name(model, k)
            if v is _UNDEFINED:
                continue
            cfg.value = v
            if cfg.ignore_in_cfg or cfg.ignore_in_args:
                log.debug("Ignoring command line parameter %s", cfg.long_param)
            log.debug("Found command line parameter '%s': %s (conf: %s)", cfg.long_param,
                      cfg.safe_value, cfg.xpath)

    def _inject_cfg_in_parser(self, parser, xpath=None, root=None):
        """
        Configure the argument parser according to cfgtree.
        """
        assert root is not None
        # pylint: disable=no-member
        for name, item in root.items():
            if isinstance(item, dict):
                self._inject_cfg_in_parser(parser, xpath=make_xpath(xpath, name), root=item)
            else:
                if item.ignore_in_args:
                    continue
                args = item.get_cmd_line_params()
                kwargs = {
                    "action": item.action,
                    "dest": item.cmd_line_name,
                    "help": item.summary,
                    "default": _UNDEFINED,
                }
                nargs = item.n_args
                dbg_infos = ["arg '{}'".format(item.long_param), "dest '{}'".format(kwargs['dest'])]
                if nargs:
                    kwargs["nargs"] = nargs
                    dbg_infos.append("nargs '{}'".format(str(nargs)))
                metavar = item.metavar
                if metavar:
                    kwargs["metavar"] = metavar
                    dbg_infos.append("metavar '{}'".format(metavar))
                if item.arg_type is not None:
                    kwargs["type"] = item.arg_type
                    dbg_infos.append("type '{}'".format(item.arg_type))
                log.debug("parser %s", ", ".join(dbg_infos))
                parser.add_argument(*args, **kwargs)
        # pylint: enable=no-member
