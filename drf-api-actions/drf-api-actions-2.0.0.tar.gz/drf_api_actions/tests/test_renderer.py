import base64

from coreapi.codecs import CoreJSONCodec
from django.test import TestCase

from drf_api_actions.renderers import ApiJsRenderer


class ApiJsRendererTest(TestCase):
    def setUp(self):
        codec = CoreJSONCodec()
        self.doc = codec.decode(base64.b64decode(
            'eyJfdHlwZSI6ImRvY3VtZW50IiwiX21ldGEiOnsidXJsIjoiaHR0cDovLzEyNy4wLjAuMTo4Nzg3L3NjaGVtYTIvIiwidGl0bGUiOiJBUEkifSwibG9naW4iOnsiY3JlYXRlIjp7Il90eXBlIjoibGluayIsInVybCI6Ii9hcGkvbG9naW4vIiwiYWN0aW9uIjoicG9zdCIsImVuY29kaW5nIjoiYXBwbGljYXRpb24vanNvbiIsImRlc2NyaXB0aW9uIjoi55So6LSm5Y+35a+G56CB5o2i5Y+WdG9rZW7vvIznmbvlvZXlpLHotKXmmK80MDMiLCJmaWVsZHMiOlt7Im5hbWUiOiJ1c2VybmFtZSIsInJlcXVpcmVkIjp0cnVlLCJsb2NhdGlvbiI6ImZvcm0iLCJzY2hlbWEiOnsiZGVzY3JpcHRpb24iOiIiLCJfdHlwZSI6InN0cmluZyIsInRpdGxlIjoiVXNlcm5hbWUifX0seyJuYW1lIjoicGFzc3dvcmQiLCJyZXF1aXJlZCI6dHJ1ZSwibG9jYXRpb24iOiJmb3JtIiwic2NoZW1hIjp7ImRlc2NyaXB0aW9uIjoiIiwiX3R5cGUiOiJzdHJpbmciLCJ0aXRsZSI6IlBhc3N3b3JkIn19LHsibmFtZSI6InByZXZfdG9rZW4iLCJsb2NhdGlvbiI6ImZvcm0iLCJzY2hlbWEiOnsiZGVzY3JpcHRpb24iOiLkuIrmrKHlvpfliLDnmoR0b2tlbu+8jOWmguaenOWcqOahiOWImeS8mumHjeaWsOWIqeeUqCIsIl90eXBlIjoic3RyaW5nIiwidGl0bGUiOiJQcmV2IHRva2VuIn19XX19LCJwaW5nIjp7InJlYWQiOnsiX3R5cGUiOiJsaW5rIiwidXJsIjoiL2FwaS9waW5nLyIsImFjdGlvbiI6ImdldCIsImRlc2NyaXB0aW9uIjoi5Yi35a2Y5Zyo5oSf77yM6I635Y+W5Yqg5a+G5ZCO55qE5pyN5Yqh5Zmo5Zyw5Z2A77yM5qOA5p+lYXBw54mI5pys5piv5ZCm6L+H5pyfXG5cbmhlYWRlcuS4reimgeW4pjogYFgtQXBwLVZlcjogPOWuouaIt+err+eahOeJiOacrOWPtz5gIO+8iOWFqOWxgOihjOS4uu+8iSJ9fSwicmVnaXN0ZXIiOnsiY3JlYXRlIjp7Il90eXBlIjoibGluayIsInVybCI6Ii9hcGkvcmVnaXN0ZXIvIiwiYWN0aW9uIjoicG9zdCIsImVuY29kaW5nIjoiYXBwbGljYXRpb24vanNvbiIsImRlc2NyaXB0aW9uIjoi5rOo5YaM6LSm5Y+3IiwiZmllbGRzIjpbeyJuYW1lIjoidXNlcm5hbWUiLCJyZXF1aXJlZCI6dHJ1ZSwibG9jYXRpb24iOiJmb3JtIiwic2NoZW1hIjp7ImRlc2NyaXB0aW9uIjoiIiwiX3R5cGUiOiJzdHJpbmciLCJ0aXRsZSI6IlVzZXJuYW1lIn19LHsibmFtZSI6InBhc3N3b3JkIiwicmVxdWlyZWQiOnRydWUsImxvY2F0aW9uIjoiZm9ybSIsInNjaGVtYSI6eyJkZXNjcmlwdGlvbiI6IiIsIl90eXBlIjoic3RyaW5nIiwidGl0bGUiOiJQYXNzd29yZCJ9fV19fSwicnVsZXMiOnsicmVhZCI6eyJfdHlwZSI6ImxpbmsiLCJ1cmwiOiIvYXBpL3J1bGVzLyIsImFjdGlvbiI6ImdldCIsImRlc2NyaXB0aW9uIjoi6I635b6X6KeE5YiZ5YiX6KGo77yMXG5cbui/lOWbnuWAvO+8mlxuXG4tIGAzMDRgIOihqOekuuWuouaIt+err+eahCBtb2RpZmllZF9hdCDkuYvlkI7nmoTml7bpl7TlhoXvvIzmsqHmnInmlrDnmoTlj5jmm7Rcbi0gYDIwMGAgYHtkaXJlY3Q6W3guY29tLCB5LmNvbSwgLi4uXSwgdHVubmVsOiBbYS5jb20sIGIuY29tLCAuLi5dLCBtb2RpZmllZF9hdDpudWxsfGRhdGV0aW1lfWAiLCJmaWVsZHMiOlt7Im5hbWUiOiJtb2RpZmllZF9hdCIsImxvY2F0aW9uIjoicXVlcnkiLCJzY2hlbWEiOnsiZGVzY3JpcHRpb24iOiLlrqLmiLfnq6/mnIDlkI7kv67mlLnml7bpl7QiLCJfdHlwZSI6InN0cmluZyIsInRpdGxlIjoiIn19XX19LCJ1c2VyIjp7InJlbmV3YWxzIjp7Imxpc3QiOnsiX3R5cGUiOiJsaW5rIiwidXJsIjoiL2FwaS91c2VyL3JlbmV3YWxzLyIsImFjdGlvbiI6ImdldCJ9fSwicmVhZCI6eyJfdHlwZSI6ImxpbmsiLCJ1cmwiOiIvYXBpL3VzZXIvIiwiYWN0aW9uIjoiZ2V0IiwiZGVzY3JpcHRpb24iOiLojrflvpfnlKjmiLfnmoRwcm9maWxl5ZKMcHJveGllcyJ9fX0='))

    def test_render_arguments(self):
        self.assertEqual(ApiJsRenderer.render_arguments(self.doc.data['user']['read']),
                         '',
                         '无参数')
        self.assertEqual(ApiJsRenderer.render_arguments(self.doc.data['register']['create']),
                         'username, password',
                         '都是必填参数')
        self.assertEqual(ApiJsRenderer.render_arguments(self.doc.data['login']['create']),
                         'username, password, {prev_token}={}',
                         '带可选参数')

    def test_render_link(self):
        self.assertEqual(ApiJsRenderer.render_link(['user', 'read'], self.doc.data['user']['read']),
                         """() => action(schema, ['user', 'read']),""",
                         '无参数')
        self.assertEqual(ApiJsRenderer.render_link(['register', 'create'], self.doc.data['register']['create']),
                         """(username, password) => action(schema, ['register', 'create'], {username, password}),""",
                         '都是必填参数')
        self.assertEqual(ApiJsRenderer.render_link(['login', 'create'], self.doc.data['login']['create']),
                         """(username, password, {prev_token}={}) => action(schema, ['login', 'create'], {username, password, prev_token}),""",
                         '带可选参数')

    def test_render_tree(self):
        s = ApiJsRenderer.render_tree(self.doc)
        print(s)
