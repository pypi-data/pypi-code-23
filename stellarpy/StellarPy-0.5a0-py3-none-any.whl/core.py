#!/usr/bin/python
# -*- coding: utf-8 -*-
import numpy as np
from datetime import datetime


class Star:
    def __init__(self, object_name, m, color=(1, 1, 0, 1)):
        self.name = object_name
        self.m = m  # масса
        self.X = [0]
        self.Y = [0]
        self.Z = [0]
        self.color = color
        # pos = gl.GLScatterPlotItem(pos=array([0, 0, 0]), color=color, size=10)
        # pos.setGLOptions('translucent')
        # plot_wid.addItem(pos)


class Body:
    def __init__(self, object_name, major, m, a, e, i, w, O=0, M=0, at=0, JD=2451545.0, color=(.5, .5, .5, 1)):
        """
        :param str object_name:     name, название
        :param tuple color:         color point, цвет точки
        :param JD:                  julian date, юлианская дата 2451545.0
        :param major:               center of mass, центр масс
        :param float m:             mass, масса
        :param float at:            наклон оси
        :param float a:             большая полуось КМ
        :param float e:             ексцентриситет ε e=c/a
        :param float i:             отклонение°
        :param float w:             аргумент перицентра° ω
        :param float O:             долгота восходящего узла° Ω N
        :param float M:             средняя аномалия° M=E-e*sin(E)
        ∂ φ
        """
        self.name = object_name
        self.color = color
        self.major = major
        self.m = m
        self.at = at
        self.JD = JD
        self.orbit = True
        self.guide = True
        self.size = None
        self.width = None
        k = G * (self.major.m + m)  # µ гравитационный параметр
        n = np.sqrt(k / a ** 3)  # среднее движение
        self.T = 2 * np.pi / n  # период обращения sqrt(((4 * pi**2)/(G * (SUN.M + m))) * a**3) Кеплер 3
        x, y, z = [], [], []
        E = np.radians(M)
        self.age = int(999 / 365 * (datetime.now() - get_g_d(JD)).days)
        for count in range(self.age):
            while abs((M + e * np.sin(E)) - E) > 0.00001:  # последовательные приближения для эксцентрической аномалии
                E = M + e * np.sin(E)
            M += n * 1  # M = n(t−t0)+M0
            r = a * (1 - e * np.cos(E))  # радиус-вектор
            sin_v = (np.sqrt(1 - e ** 2) * np.sin(E)) / (1 - e * np.cos(E))
            cos_v = (np.cos(E) - e) / (1 - e * np.cos(E))
            sin_u = np.sin(np.radians(w)) * cos_v + np.cos(np.radians(w)) * sin_v
            cos_u = np.cos(np.radians(w)) * cos_v - np.sin(np.radians(w)) * sin_v
            x.append(r * (cos_u * np.cos(np.radians(O)) - sin_u * np.sin(np.radians(O)) * np.cos(np.radians(i))))
            y.append(r * (cos_u * np.sin(np.radians(O)) + sin_u * np.cos(np.radians(O)) * np.cos(np.radians(i))))
            z.append(r * (sin_u * np.sin(np.radians(i))))
            # V1 = sqrt(r / p) * e * sinv
            # V2 = sqrt(r / p) * (1 + e * cosv)
        self.X = list(reversed(x)) if self.at > 90 else x
        self.Y = list(reversed(y)) if self.at > 90 else y
        self.Z = list(reversed(z)) if self.at > 90 else z
        # self.X = x
        # self.Y = y
        # self.Z = z
        # F = G * SUN.M * self.m / r ** 2  # сила гравитационного притяжения
        # p = a * (1 - e ** 2)  # фокальный параметр
        # b = sqrt(a * p)  # малая полуось
        # Rper = (1 - e) * a  # радиус перегелия
        # Rafe = (1 + e) * a  # радиус афелия
        # φ = (24 * pi**3 * a**2) / (T**2 * C**2 * (1 - e**2))
        # φ = (6 * pi * G * SUN.M) / (C**2 * a * (1 - e**2))

        if self.m > 1e25:
            self.outer_planets()
        elif self.m > 1e23:
            self.planet()
        elif self.m > 1e20:
            self.dwarf_planet()
        else:
            self.small_body()

    def star(self):
        pass

    def planet(self, orbit=True, guide=True, size=8, width=1):
        return self.paint(orbit=orbit, guide=guide, size=size, width=width)

    def outer_planets(self, orbit=True, guide=True, size=10, width=1):
        return self.paint(orbit=orbit, guide=guide, size=size, width=width)

    def dwarf_planet(self, orbit=True, guide=True, size=6, width=1):
        return self.paint(orbit=orbit, guide=guide, size=size, width=width)

    def small_body(self, orbit=False, guide=False, size=1.5, width=.25):
        return self.paint(orbit=orbit, guide=guide, size=size, width=width)

    def satellite(self, orbit=False, guide=False, size=3, width=1):
        pass

    def paint(self, orbit=True, guide=True, size=4.0, width=1.0):
        self.orbit = orbit
        self.guide = guide
        self.size = size
        self.width = width


def get_g_d(j_d):
    a = int(j_d + 32044)
    b = int((4 * a + 3) / 146097)
    c = a - int((146097 * b) / 4)
    d = int((4 * c + 3) / 1461)
    e = c - int((1461 * d) / 4)
    m = int((5 * e + 2) / 153)
    day = e - int((153 * m + 2) / 5) + 1
    month = m + 3 - 12 * int((m / 10))
    year = 100 * b + d - 4800 + int((m / 10))
    return datetime(year, month, day)


def get_j_d(day, month, year):
    a = int((14 - month) / 12)
    b = year + 4800 - a
    c = month + 12 * a - 3
    return day + int((153 * c + 2) / 5) + 365 * b + int(b / 4) - int(b / 100) + int(b / 400) - 32045


G = 6.67408e-11  # граивтационная постоянная м3·с−2·кг−1 или Н·м2·кг−2
au = 149597870.700  # а.е. астрономическая единица
C = 299792458  # скорость света м/с
