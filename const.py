
rgb = tuple[int, int, int]

FPS: int = 120
BOMB_CHANCE: float = 0.15
BOARD_SIZE: tuple[int, int] = 14,20 # cells
CELL_SIZE: tuple[int, int] = 20, 20 # pixels
PADDING: int = 1
BOARD_DIM: tuple[int, int] = (PADDING + BOARD_SIZE[1]*(PADDING+CELL_SIZE[1])), (PADDING + BOARD_SIZE[0]*(PADDING+CELL_SIZE[0]))

print(BOARD_DIM)

class Colors:
    BACKGROUND: rgb = (221, 255, 153)
    GREEN: rgb = (71, 209, 71)
    WHITE: rgb = (255,255,255)
    BLACK: rgb = (0,0,0)
    GREY: rgb = (217, 217, 217)
    BLUE: rgb = (51, 153, 255)
    RED: rgb = (255,0,0)
    GREY_2: rgb = (179, 179, 179)

    

appearence = {
    'hidden': Colors.WHITE ,
    'hover' : Colors.GREY,
    'discovered': Colors.BLUE,
    'bomb': Colors.BLACK,
    'marked': Colors.RED
}
