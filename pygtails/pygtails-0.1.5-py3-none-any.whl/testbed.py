import pygame

from pygtails import Game, Circle, Rectangle
from colors import *

class Test(Game):
    def __init__(self):

#class Test(Game):
#    def __init__(self):
#        super().__init__((400, 300), 'Test')
#        self.screen.fill(WHITE)
#        c = MyCircle(self)
#        c.draw()
#        #r = MyRectangle(self)
#        pygame.display.flip()
#
#class MyCircle(Circle):
#    def __init__(self, game):
#        super().__init__(game, (5, 5), 20)
#        self.color = BLUE
#        self.just_clicked = False
#
#    def on_mouse_enter(self, event):
#        self.color = HIGHLIGHT[BLUE]
#        self.draw()
#
#    def on_mouse_exit(self, event):
#        self.color = BLUE
#        self.draw()
#
#    def on_mouse_down(self, event):
#        self.just_clicked = True
#        pygame.mouse.set_pos(self.center)
#
#    def on_mouse_up(self, event):
#        if self.just_clicked:
#            self.just_clicked = False
#
#    def on_mouse_drag(self, event):
#        if self.just_clicked:
#            self.just_clicked = False
#            return
#
#        color = self.color
#        self.color = WHITE
#        self.draw()
#
#        self.color = color
#        self.corner = tuple(i+di for i, di in zip(self.corner, event.rel))
#        self.draw()
#
#    def draw(self):
#        pygame.draw.circle(self.game.screen, self.color,
#                           self.center, self.radius)
#
#class MyRectangle(Rectangle):
#    def __init__(self, game):
#        super().__init__(game, (50, 50), 70, 40)
#        pygame.draw.polygon(self.game.screen, GREEN, self.corners)
#
#    def on_mouse_enter(self, event):
#        print("mouse entered rectangle")
#    
#    def on_mouse_exit(self, event):
#        print("mouse exited rectangle")
#
#if __name__ == '__main__':
#    game = Test()
#    game.main()
