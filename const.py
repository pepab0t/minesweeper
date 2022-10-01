import os
from pathlib import Path

import pygame as pg

PATH: Path = Path(__file__).parent.resolve()

rgb = tuple[int, int, int]

FPS: int = 60
BOMB_CHANCE: float = 0.15
BOARD_SIZE: tuple[int, int] = 14, 20 # cells
CELL_SIZE: tuple[int, int] = 30, 30 # pixels
PADDING: int = 1

BOARD_DIM: tuple[int, int] = (PADDING + BOARD_SIZE[1]*(PADDING+CELL_SIZE[1])), (PADDING + BOARD_SIZE[0]*(PADDING+CELL_SIZE[0]))

class Colors:
    BACKGROUND: rgb = (221, 255, 153)
    GREEN: rgb = (71, 209, 71)
    GREEN_DARK: rgb = (0,153,0)
    GREEN_LIGHT: rgb = (179, 255, 179)
    GREEN_LIME: rgb = (0, 255, 0)
    WHITE: rgb = (255,255,255)
    BLACK: rgb = (0,0,0)
    GREY: rgb = (217, 217, 217)
    BLUE: rgb = (0,0,255)
    RED: rgb = (255,0,0)
    RED_DARK: rgb = (153, 0, 0)
    GREY_2: rgb = (179, 179, 179)
    YELLOW: rgb = (255, 255, 0)

markImage: pg.surface.Surface = pg.image.load(os.path.abspath(f'{PATH}/img/flag.png' ))
bombImage: pg.surface.Surface =  pg.image.load(os.path.abspath(f'{PATH}/img/bomb.png' ))

appearence: dict[str, rgb] = {
    'hidden': Colors.GREEN_DARK,
    'discovered': Colors.GREEN_LIGHT,
    'bomb': Colors.BACKGROUND,
    'hover' : Colors.GREEN_LIME,
}
