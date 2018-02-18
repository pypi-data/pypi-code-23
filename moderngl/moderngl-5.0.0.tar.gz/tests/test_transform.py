import unittest

from common import get_context


class TestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.ctx = get_context()

    def test_transform(self):

        program = self.ctx.program(
            vertex_shader='''
                #version 330

                in vec4 vert;
                out float vert_length;

                void main() {
                    vert_length = length(vert);
                }
            ''',
            varyings=['vert_length']
        )

        self.assertIs(program.geometry_input, None)
        self.assertIs(program.geometry_output, None)

        self.assertIn('vert', program)
        self.assertIn('vert_length', program)


if __name__ == '__main__':
    unittest.main()
