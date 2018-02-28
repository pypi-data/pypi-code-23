import unittest

from common import get_context
import moderngl


class TestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.ctx = get_context()

    def test_program(self):
        program = self.ctx.program(
            vertex_shader='''
                #version 330

                uniform vec2 pos;
                uniform float scale;

                in vec2 vert;
                out vec2 v_vert;

                void main() {
                    gl_Position = vec4(pos + vert * scale, 0.0, 1.0);
                    v_vert = vert;
                }
            ''',
            fragment_shader='''
                #version 330

                in vec2 v_vert;
                out vec4 color;

                void main() {
                    color = vec4(v_vert, 0.0, 1.0);
                }
            ''',
        )

        self.assertIn('vert', program)
        self.assertIn('pos', program)
        self.assertIn('scale', program)

        self.assertIsInstance(program['vert'], moderngl.Attribute)
        self.assertIsInstance(program['pos'], moderngl.Uniform)
        self.assertIsInstance(program['scale'], moderngl.Uniform)


if __name__ == '__main__':
    unittest.main()
