# coding=utf-8


from edlm.convert._preprocessor._markdown._aliases import Context, process_aliases


def test_process_aliases():
    ctx = Context()
    ctx.settings.data = {
        'aliases': {
            'key': 'value'
        }
    }
    ctx.markdown_text = 'this is some key text'
    process_aliases(ctx)
    assert ctx.markdown_text == 'this is some value text'
