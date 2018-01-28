# coding: utf-8


class CmdlineParsersBase(object):
    def parse_cmd_line(self, model, argv=None):
        pass

    def _find_cfg_for_cmd_line_name(self, root, cmd_line_name):
        assert root is not None
        for v in root.values():
            if isinstance(v, dict):
                f = self._find_cfg_for_cmd_line_name(v, cmd_line_name)
                if f:
                    return f
            else:
                if v.cmd_line_name == cmd_line_name:
                    return v
