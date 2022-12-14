import os
import random
import sys
from typing import Any, Callable, Optional

import pygame as pg

import const

pg.init()


roboto50 = pg.font.SysFont('Roboto', 50)
roboto25 = pg.font.SysFont('Roboto', 25)
roboto_cell = pg.font.SysFont('Roboto', const.CELL_SIZE[1])

update: Callable[[], None] = lambda: pg.display.update()

CLICKS: dict[int, str] = {
    1: 'left',
    2: 'middle',
    3: 'right'
}

class Signal:

    def __init__(self, *dtypes):
        self.fn = None
        self.dtypes = dtypes

    def emit(self, *args):
        if self.fn is None:
            return

        for arg, dtype in zip(args, self.dtypes):
            if type(arg) != dtype:
                raise AttributeError(f'argument {arg} should be {dtype}, but is {type(arg)}')

        self.fn(*args)

    def connect(self, fn: Callable[..., Any]) -> None:
        if not isinstance(fn, Callable):
            raise AttributeError(f"Expected fn to be Callable, got {fn.__class__.__name__}")
        self.fn = fn


class Cell:
    def __init__(self, x: int, y: int, width: int, height: int, idx: tuple[int, int]):
        self.i, self.j = idx
        self.cellRect: pg.Rect = pg.Rect(x, y, width, height)
        self.cellArea: pg.surface.Surface = pg.Surface((width, height))
        self.cellArea = self.cellArea.convert()
        self.bomb: bool = True if random.random() < const.BOMB_CHANCE else False

        self.background: const.rgb = const.appearence['hidden']
        self.cellArea.fill(self.background)        

        self.marked: bool = False
        self.discovered: bool = False


        self.__bomb_hint: Optional[int] = 9 if self.bomb else None
        self.fontArea = None
        self.text_position = None

        self.markImage = pg.transform.scale(const.markImage, self.cellRect.size)

        if self.bomb:
            self.bombImage = pg.transform.scale(const.bombImage, self.cellRect.size)

        self.game_over: Signal = Signal()

    def is_in(self, pos: tuple[int, int]) -> bool:
        return self.cellRect.collidepoint(pos)

    @property
    def x(self):
        return self.cellRect.x

    @property
    def y(self):
        return self.cellRect.y

    @property
    def width(self):
        return self.cellArea.get_width()

    @property
    def height(self):
        return self.cellArea.get_height()

    @property
    def bomb_hint(self):
        return self.__bomb_hint

    @bomb_hint.setter
    def bomb_hint(self, value: int) -> None:
        if not (0 <= value < 9):
            raise ValueError('New value must be in interval 0-8')
        self.__bomb_hint = value
        self.fontArea = roboto_cell.render(str(self.bomb_hint) if self.bomb_hint else "", True, const.Colors.BLACK)
        self.text_position = (self.width/2 - self.fontArea.get_width()/2, self.height/2 - self.fontArea.get_height()/2)

    def hover(self):
        if self.discovered:
            self.cellArea.fill(self.background)
            if self.fontArea:
                self.cellArea.blit(self.fontArea, self.text_position)  # type: ignore
        else:
            self.cellArea.fill(const.appearence['hover'])
            if self.marked:
                self.cellArea.blit(self.markImage, (0,0))

    def click(self) -> bool:
        if not self.discovered:
            self.discover()
        if self.bomb:
            # self.cellArea.fill(self.background)  # type: ignore
            # self.cellArea.blit(self.bombImage, self.bombImagePosition)
            self.game_over.emit()
            return False
        return True

    def mark(self):
        if self.discovered:
            return

        self.marked = not self.marked

    def neutral(self):
        self.cellArea.fill(self.background)
        if self.discovered:
            if self.bomb:
                self.cellArea.blit(self.bombImage, (0,0))
            elif self.fontArea:
                self.cellArea.blit(self.fontArea, self.text_position)  # type: ignore
        elif self.marked:
            self.cellArea.blit(self.markImage, (0,0))


    def discover(self):
        self.discovered = True
        self.background = const.appearence['discovered'] if not self.bomb else const.appearence['bomb']
        self.neutral()


class Button:
    def __init__(self, parent: pg.surface.Surface, x, y, width, height, text: str, click_fn: Optional[Callable[..., Any]] = None):
        self.rect = pg.Rect(x, y, width, height)
        self.area = parent.subsurface(self.rect)

        self.fontArea = roboto25.render(text, True, const.Colors.BLACK)

        self.click = Signal()
        if click_fn is not None:
            self.click.connect(click_fn)

        self.handled: bool = False

        self.text_pos = (self.width/2 - self.fontArea.get_width()/2, self.height/2 - self.fontArea.get_height()/2)


    def collide(self, pos: tuple[int, int]) -> bool:
        return self.rect.collidepoint(pos)

    def act(self):
        self.area.fill(const.Colors.GREY_2)
        
        if pg.mouse.get_pressed()[0]:
            self.area.fill(const.Colors.GREEN)

            if not self.handled and self.click.fn:
                self.click.emit()
                self.handled = True
        else:
            self.handled = False
        self.draw_border()
        self.area.blit(self.fontArea, self.text_pos)

    def neutral(self):
        self.area.fill(const.Colors.GREY)
        self.area.blit(self.fontArea, self.text_pos)

        self.draw_border()

    def draw_border(self):
        pg.draw.rect(self.area, const.Colors.BLACK, (0,0, self.width, 1))
        pg.draw.rect(self.area, const.Colors.BLACK, (0,0, 1, self.height))
        pg.draw.rect(self.area, const.Colors.BLACK, (0, self.height - 1, self.width, 1))
        pg.draw.rect(self.area, const.Colors.BLACK, (self.width - 1, 0, 1, self.height))

            
    @property
    def x(self):
        return self.rect.x

    @property
    def y(self):
        return self.rect.y

    @property
    def width(self):
        return self.area.get_width()

    @property
    def height(self):
        return self.area.get_height()

class Board:
    def __init__(self, main_surf: pg.surface.Surface) -> None:
        self._board_rect = pg.Rect(0, 50, *const.BOARD_DIM)#self._board.get_rect()
        self._board = main_surf.subsurface(self._board_rect)#pg.Surface((662,442))
        self._board.fill(const.Colors.GREEN)

        self.active: bool = False
        self.cells: list[Cell] = []

        self.size: tuple[int, int] = const.BOARD_SIZE

        self.lost_surface: pg.surface.Surface = roboto50.render("Game Over!", True, const.Colors.RED)
        self.lost_surface_pos = (const.BOARD_DIM[0]/2 - self.lost_surface.get_width()/2, const.BOARD_DIM[1]/2 - self.lost_surface.get_height()/2)
        self.win_surface = pg.surface.Surface = roboto50.render("You Won!", True, const.Colors.BLUE)
        self.win_surface_pos = (const.BOARD_DIM[0]/2 - self.win_surface.get_width()/2, const.BOARD_DIM[1]/2 - self.win_surface.get_height()/2)

        self.reset()

    @property
    def board(self) -> pg.surface.Surface:
        return self._board

    def reset(self):
        self.active = True
        self.cells.clear()
        self.board.fill(const.Colors.GREEN)
        self.add_cells()
        self.detect_bombs()

    def add_cells(self):
        cell_width, cell_height = const.CELL_SIZE
        for i in range(self.size[0]):
            for j in range(self.size[1]):
                c = Cell(const.PADDING + j*(const.PADDING+cell_width), const.PADDING + i*(const.PADDING+cell_height), cell_width, cell_height, (i, j))
                c.game_over.connect(self.lost)
                self._board.blit(c.cellArea, (c.x, c.y))
                self.cells.append(c)

    def win(self):
        self.active = False
        print("You won")
        self.board.blit(self.win_surface, self.win_surface_pos)


    def lost(self):
        self.active = False
        for c in self.cells:
            if c.bomb:
                c.discover()
            self.board.blit(c.cellArea, (c.x, c.y))
        self.board.blit(self.lost_surface, self.lost_surface_pos)
        update()
        

    def __getitem__(self, index: tuple[int, int]) -> Cell:
        """return cell on index[0]th row and index[1]th column, indexing from zero"""
        row, col = index
        return self.cells[row*(self.size[1]) + col]

    def detect_bombs(self):
        """Pick a number for each cell meaning how many bombs are neighbours"""

        for i in range(self.size[0]):
            for j in range(self.size[1]):
                c = self[i,j]
                if c.bomb:
                    continue
                neighbours: list[tuple[int, int]] = self.find_neighbours(i,j)
                total: int = 0
                for n in neighbours:
                    total += 1 if self[n].bomb else 0
                c.bomb_hint = total


    def find_neighbours(self, i: int, j: int, approach: str = 'square') -> list[tuple[int, int]]:
        out: list[tuple[int, int]] = []
        if approach == 'square':
            for row in range(i-1, i+2):
                if row < 0 or row >= self.size[0] :
                    continue
                for col in range(j-1, j+2):
                    if col < 0 or col >= self.size[1] :
                        continue
                    if row == i and col == j:
                        continue

                    out.append((row, col))
        elif approach == 'cross':
            pass
        else:
            raise AttributeError("Invalid searching approach")

        return out
        

    def is_in(self, mouse_pos: tuple[int, int]) -> bool:
        return self._board_rect.collidepoint(mouse_pos)

    def compute(self, mouse_pos: tuple[int, int], click: Optional[str]):
        offset = self.board.get_offset()
        mouse_pos = mouse_pos[0] - offset[0], mouse_pos[1] - offset[1]

        all_discovered: bool = True

        for c in self.cells:
            if c.is_in(mouse_pos):
                if click == 'left':
                    if not c.click(): # if bomb found
                        all_discovered = False
                        break
                    if c.bomb_hint == 0:
                        self.discover_neighbours(self.find_neighbours(c.i, c.j))
                elif click == 'right':
                    c.mark()
                else:
                    c.hover()
            else:
                c.neutral()

            # FOR TESTING
            # if not c.bomb:
            #     c.discover()

            if not c.bomb and not c.discovered:
                all_discovered = False

            self.board.blit(c.cellArea, (c.x, c.y))

        if all_discovered:
            self.win()

    def discover_neighbours(self, neighbours: list[tuple[int, int]]):
        for n in neighbours:
            cn = self[n]
            if cn.discovered:
                continue
            if cn.bomb is False:
                cn.discover()
            if cn.bomb_hint == 0:
                self.discover_neighbours(self.find_neighbours(cn.i, cn.j))

class App:

    def __init__(self, resolution: tuple[int,int]):
        self.screen: pg.surface.Surface = pg.display.set_mode(resolution)  
        self.screen.fill(const.Colors.BACKGROUND)     

        self.board = Board(self.screen)
        self.clock: pg.time.Clock = pg.time.Clock()

        pg.time.set_timer(pg.USEREVENT, 1000)
        self.seconds_counter: int = 0
        self.timer_surface = roboto25.render(self.secs_repr(self.seconds_counter), True, const.Colors.BLACK)
        self.timer_surface_position = (20, 50/2 - self.timer_surface.get_height()/2) 

        self.buttons: list[Button] = []

        self.buttons.append(Button(self.screen, self.screen.get_width() - 80 - 10, 10, 80, 30, 'Exit', click_fn=self.quit))
        self.buttons.append(Button(self.screen, self.screen.get_width() - 2*(80 + 10), 10, 80, 30, 'Reset', click_fn=self.restart_game))
        
        update()
    
    def restart_game(self):
        self.board.reset()
        self.seconds_counter = 0


    def mainloop(self):

        while True:
            self.clock.tick(const.FPS)


            click: Optional[str] = None

            pos: tuple[int, int] = pg.mouse.get_pos()

            for e in pg.event.get():
                if e.type == pg.QUIT:
                    self.quit()
                if e.type == pg.MOUSEBUTTONDOWN:
                    click = CLICKS.get(e.button, None)
                if e.type == pg.USEREVENT:
                    self.seconds_counter += 1

            if self.board.active:
                self.screen.fill(const.Colors.BACKGROUND)
                self.board.compute(pos, click)
                self.timer_surface = roboto25.render(self.secs_repr(self.seconds_counter), True, const.Colors.BLACK)
                self.screen.blit(self.timer_surface, self.timer_surface_position)
            
            for b in self.buttons:
                if b.collide(pos):
                    b.act()
                else:
                    b.neutral()


            pg.display.flip()

    def quit(self):
        pg.quit()
        sys.exit()

    def secs_repr(self, seconds):
        s = seconds%60
        m = seconds//60

        return f"{m:02d}:{s:02d}"


def main():

    pg.display.set_caption("Minesweeper")

    app = App((const.BOARD_DIM[0], const.BOARD_DIM[1]+50))
    app.mainloop()

if __name__ == "__main__":
    main()
