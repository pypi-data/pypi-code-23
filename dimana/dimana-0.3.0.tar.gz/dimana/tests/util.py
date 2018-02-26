from dimana.exceptions import BaseParseError


def ParseTestClass(targetclass, target_parse, TargetParseError):
    def clsdeco(testcls):

        def make_title(s):
            return repr(str(s).replace('.', '_'))

        def set_tests(value, text, alts):
            title = make_title(value)

            # This exists merely to work around loop scoping issue.
            setattr(
                testcls,
                'test_str_of {}'.format(title),
                lambda self: self.assertEqual(text, str(value)),
            )

            repexp = '<{} {!r}>'.format(targetclass.__name__, text)
            setattr(
                testcls,
                'test_repr_of {}'.format(title),
                lambda self: self.assertEqual(repexp, repr(value)),
            )

            texts = [text] + alts
            setattr(
                testcls,
                'test_parse_of {}'.format(title),
                lambda self: [
                    self.assertParsedValueMatches(value, target_parse(t))
                    for t
                    in texts
                ],
            )

        for (value, text, alts) in testcls.cases:
            set_tests(value, text, alts)

        for badinput in testcls.errorcases:
            setattr(
                testcls,
                'test_parse_error_of {}'.format(make_title(badinput)),
                lambda self, badinput=badinput: self.assertRaises(
                    BaseParseError,
                    target_parse,
                    badinput,
                )
            )

        def test_ParseError_hierarchy(self):
            self.assertTrue(issubclass(TargetParseError, BaseParseError))

        testcls.test_ParseError_hierarchy = test_ParseError_hierarchy

        return testcls

    return clsdeco
