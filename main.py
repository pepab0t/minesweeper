import sys
from typing import Callable

import pygame as pg

import const

update: Callable[[], None] = lambda: pg.display.update()

def blitter(fn):
    def wrapper(self, *args, **kwargs):
        res = fn(self, *args, **kwargs)
        self.parent.blit(self.cellArea, (self.x, self.y))
        return res

    return wrapper

class Cell:
    def __init__(self, x: int, y: int, width: int, height: int, parent: pg.Surface):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.parent = parent

        self.cellRect: pg.Rect = pg.Rect(self.x, self.y, self.width, self.height)
        self.cellArea: pg.Surface = pg.Surface((self.width, self.height))

        self.discovered: bool = False
        self.clicked =False

        self.appearence = {
            'normal': const.Colors.WHITE,
            'hover' : const.Colors.GREY,
            'pressed': const.Colors.BLACK,
            'discovered': const.Colors.BLUE
        }

    def process(self, mouse_pos: tuple[int, int]):
        print(self.clicked)
        if self.discovered:
            self.cellArea.fill(self.appearence['discovered'])
            return
        else:
            mouse_pos = (mouse_pos[0] - 50 , mouse_pos[1] -50)
            self.cellArea.fill(self.appearence['normal'])

            if self.cellRect.collidepoint(mouse_pos):
                self.cellArea.fill(self.appearence['hover'])

                if not self.clicked and pg.mouse.get_pressed(num_buttons=3)[0]:
                    self.clicked = True

                if self.clicked is True and not pg.mouse.get_pressed()[0]:
                    self.cellArea.fill(self.appearence['pressed'])
                    self.discovered = True
            else:
                self.clicked = False


        self.parent.blit(self.cellArea, (self.x,self.y))


class Board:
    def __init__(self) -> None:
        self.board = pg.Surface((662,442))
        self.board.fill(const.Colors.GREEN)

        self.cells: list[Cell] = []
        self.create()

    def create(self):
        pad = 2
        cell_width, cell_height = const.CELL_SIZE
        for i in range(const.BOARD_SIZE[0]):
            for j in range(const.BOARD_SIZE[1]):
                c = Cell(pad + j*(pad+cell_width), pad + i*(pad+cell_height), cell_width, cell_height, self.board)
                self.board.blit(c.cellArea, (c.x, c.y))
                self.cells.append(c)               
        

class App:

    def __init__(self, resolution: tuple[int,int]):
        self.screen: pg.surface.Surface = pg.display.set_mode(resolution)
        self.screen.fill(const.Colors.BACKGROUND)     
        self.board = Board()
        self.screen.blit(self.board.board, (50,50))
        update()
        self.clock: pg.time.Clock = pg.time.Clock()

        # pg.draw.rect(self.screen, const.Colors.GREEN, (100,100,100,100))
        # pg.display.update()

    def mainloop(self):

        while True:
            self.clock.tick(const.FPS)

            for e in pg.event.get():
                if e.type == pg.QUIT:
                    pg.quit()
                    sys.exit()

                # if e.type == pg.MOUSEBUTTONDOWN:
            pos: tuple[int, int] = pg.mouse.get_pos()
            # print(pos)
            for c in self.board.cells:
                c.process(pos)

            self.screen.blit(self.board.board, (50,50))
            update()

def main():
    pg.init()

    app = App((762,542))
    app.mainloop()

if __name__ == "__main__":
    main()
