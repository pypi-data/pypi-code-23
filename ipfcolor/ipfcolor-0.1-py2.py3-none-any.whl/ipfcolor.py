import numpy as np
from typing import Union
from math import pi, acos, atan2, sqrt

from .quaternion import Quaternion
from .orientation import eu2qu, qu2om, om2gmatrix

# GLOBAL CONSTANTS
get_has_inversion = True

k_pi_over_180 = pi / 180
k_180_over_pi = 180 / pi
hex_quat_sym = [Quaternion(0, 0, 0, 1), Quaternion(0, 0, 0.5, 0.8660254), Quaternion(0, 0, 0.8660254, 0.5),
                Quaternion(0, 0, 1, 0), Quaternion(0, 0, 0.8660254, -0.5), Quaternion(0, 0, 0.5, -0.8660254),
                Quaternion(1, 0, 0, 0), Quaternion(0.8660254, 0.5, 0, 0), Quaternion(0.5, 0.8660254, 0, 0),
                Quaternion(0, 1, 0, 0), Quaternion(-0.5, 0.8660254, 0, 0), Quaternion(-0.8660254, 0.5, 0, 0)]


class Generator:
    def __init__(self):
        pass

    @staticmethod
    def in_unit_triangle(eta: float = 0, chi: float = 0) -> bool:
        if eta < 0 or eta > 30.0 * k_pi_over_180 or chi < 0 or chi > 90.0 * k_pi_over_180:
            return False

        return True

    @staticmethod
    def drgb(a: int = 0, r: Union[int, list] = 0, g: int = 0, b: int = 0) -> int:
        if isinstance(r, list) and len(r) == 3:
            g = int(round(r[1]))
            b = int(round(r[2]))
            r = int(round(r[0]))

        return ((a & 0xff) << 24) | ((r & 0xff) << 16) | ((g & 0xff) << 8) | (b & 0xff)

    def generate_ipf_color(self, phi1: Union[float, list], ref_dir_0: Union[float, list], deg_to_rad: bool,
                           phi: float = 0, phi2: float = 0, ref_dir_1: float = 0, ref_dir_2: float = 0) -> list:
        if isinstance(phi1, list) and len(phi1) == 3:
            phi = phi1[1]
            phi2 = phi1[2]
            phi1 = phi1[0]

        if isinstance(ref_dir_0, list) and len(ref_dir_0) == 3:
            ref_dir_1 = ref_dir_0[1]
            ref_dir_2 = ref_dir_0[2]
            ref_dir_0 = ref_dir_0[0]

        if deg_to_rad:
            phi1 *= k_pi_over_180
            phi *= k_pi_over_180
            phi2 *= k_pi_over_180

        eu = [phi1, phi, phi2]
        ref_direction = [ref_dir_0, ref_dir_1, ref_dir_2]
        qu = [0, 0, 0, 0]
        eu2qu(eu, qu)

        q1 = Quaternion(qu)
        qc = Quaternion(0)
        om = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        g = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        chi = 0
        eta = 0

        for j in range(12):
            q2 = hex_quat_sym[j]
            q2.multiply(q1, out=qc)

            qc.copy_to_list(qu)
            qu2om(qu, om)
            om2gmatrix(om, g)

            p = np.matmul(g, ref_direction)
            p = p / np.linalg.norm(p)

            if p[2] < 0:
                if get_has_inversion:
                    for i, element in enumerate(p):
                        p[i] = -element
                else:
                    continue

            chi = acos(p[2])
            eta = atan2(p[1], p[0])

            if Generator.in_unit_triangle(eta, chi):
                break

        eta_min = 0
        eta_max = 30
        chi_max = 90
        eta_deg = eta * k_180_over_pi
        chi_deg = chi * k_180_over_pi

        rgb = [1 - chi_deg / chi_max, 0, abs(eta_deg - eta_min) / (eta_max - eta_min)]
        rgb[1] = 1 - rgb[2]
        rgb[1] *= chi_deg / chi_max
        rgb[2] *= chi_deg / chi_max
        for i, element in enumerate(rgb):
            rgb[i] = sqrt(element)

        max_val = max(rgb[0], rgb[1], rgb[2])
        for i, element in enumerate(rgb):
            rgb[i] = 255 * element / max_val

        return rgb
        # return Generator.drgb(255, rgb)
