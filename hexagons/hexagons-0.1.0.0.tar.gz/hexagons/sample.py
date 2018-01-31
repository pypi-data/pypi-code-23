#! /usr/bin/env python

import pygame
from hexagons.grid import HexagonGrid
from hexagons.coordinate import Axial
import random


def main():
    def random_color():
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        return pygame.Color(r, g, b, 255)

    hex_size = 50
    grid_size = 4
    window_size = 600
    center_hex = Axial(0, 0)
    hex_format = 'flat'

    g = HexagonGrid(window_size, center_hex, hex_format=hex_format,
                    grid_size=grid_size)
    pygame.init()
    display = pygame.display.set_mode((window_size, window_size),
                                      pygame.HWSURFACE)
    running = True

    colors = {}
    for pt in center_hex.to_cube().circle_around(g.size):
        colors[pt] = random_color()

    def get_color(cubecoord):
        if cubecoord not in colors:
            colors[cubecoord] = random_color()
        return colors[cubecoord]

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                clicked = g.clicked_hex(pos)
                if clicked is not None:
                    if clicked == g.center_hex:
                        colors[clicked.to_cube()] = random_color()
                    else:
                        g.move_center(clicked)
        for ax, c, cn in g.hexagon_list():
            pygame.draw.polygon(display, get_color(ax.to_cube()), cn)
        pygame.display.flip()

    pygame.quit()


if __name__ == '__main__':
    main()
