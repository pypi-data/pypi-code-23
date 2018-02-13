from typing import Union


class Quaternion:
    def __init__(self, x: Union[float, list] = 0, y: float = 0, z: float = 0, w: float = 0):
        if isinstance(x, list) and len(x) == 4:
            y = x[1]
            z = x[2]
            w = x[3]
            x = x[0]

        self.x = x
        self.y = y
        self.z = z
        self.w = w

    def multiply(self, other: 'Quaternion', out: 'Quaternion'):
        out.x = other.x * self.w + other.w * self.x + other.z * self.y - other.y * self.z
        out.y = other.y * self.w + other.w * self.y + other.x * self.z - other.z * self.x
        out.z = other.z * self.w + other.w * self.z + other.y * self.x - other.x * self.y
        out.w = other.w * self.w - other.x * self.x - other.y * self.y - other.z * self.z

    def copy_to_list(self, out: list):
        if isinstance(out, list) and len(out) == 4:
            out[0] = self.x
            out[1] = self.y
            out[2] = self.z
            out[3] = self.w
