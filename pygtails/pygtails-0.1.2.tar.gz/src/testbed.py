import pygame

from pygtails import Game, Circle, Rectangle
from colors import *


class Test(Game):
    def __init__(self):
        super().__init__((400, 300), 'Test')
        self.screen.fill(WHITE)
        c = MyCircle(self)
        r = MyRectangle(self)
        pygame.display.flip()

class MyCircle(Circle):
    def __init__(self, game):
        super().__init__(game, (5, 5), 20)
        pygame.draw.circle(game.screen, BLUE, self.center, self.radius)

    def on_mouse_enter(self, event):
        print("mouse entered circle")

    def on_mouse_exit(self, event):
        print("mouse exited circle")

class MyRectangle(Rectangle):
    def __init__(self, game):
        super().__init__(game, (50, 50), 70, 40)
        pygame.draw.polygon(self.game.screen, GREEN, self.corners)

    def on_mouse_enter(self, event):
        print("mouse entered rectangle")
    
    def on_mouse_exit(self, event):
        print("mouse exited rectangle")

if __name__ == '__main__':
    game = Test()
    game.main()
