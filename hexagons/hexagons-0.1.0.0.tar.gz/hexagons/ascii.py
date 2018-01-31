#! /usr/bin/env python

from collections import defaultdict
import random
import pygame
from hexagons.grid import HexagonGrid
from hexagons.coordinate import Axial


def main():
    pygame.init()
    letters = 'abcdefghijklmnopqrstuvxwyz '
    white = pygame.Color(255, 255, 255, 255)
    black = pygame.Color(0, 0, 0, 255)
    font = pygame.font.SysFont('Arial', 30)
    hex_size = 50
    grid_size = 4
    window_size = 600
    center_hex = Axial(0, 0)
    hex_format = 'pointy'

    def next_letter(letter):
        idx = letters.index(letter)
        nextidx = (idx + 1) % len(letters)
        return letters[nextidx]

    letter_mapping = defaultdict(lambda: ' ')

    g = HexagonGrid(window_size, center_hex, hex_format=hex_format,
                    grid_size=grid_size)
    display = pygame.display.set_mode((window_size, window_size),
                                      pygame.HWSURFACE)
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                clicked = g.clicked_hex(pos)
                if clicked is not None:
                    #if clicked == g.center_hex:
                    letter_mapping[clicked] = next_letter(letter_mapping[clicked])

        for ax, c, cn in g.hexagon_list():
            pygame.draw.polygon(display, white, cn)
            pygame.draw.polygon(display, black, cn, 1)
            letter = letter_mapping[ax]
            if letter != ' ':
                letterdisplay = font.render(letter, True, black)
                textwidth, textheight = font.size(letter)
                x = c[0] - (textwidth / 2)
                y = c[1] - (textheight / 2)
                display.blit(letterdisplay, (x, y))

        pygame.display.flip()

    pygame.quit()


if __name__ == '__main__':
    main()
