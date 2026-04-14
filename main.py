import pygame as pg
import random as rd
import math
import gradient as gd
import numpy as np

# --------------- initialize pygame -------------------
pg.init()

# --------------- setting up pygame display ------------------
FPS = 60

WIDTH = 600
HEIGHT = 600
BORDER = 18

RECT_WIDTH  = (WIDTH  - BORDER * 2) // 3   # = 188
RECT_HEIGHT = (HEIGHT - BORDER * 2) // 3   # = 188

OUTER_PAD = 10
BORDER_RADIUS = 12
OUTLINE_THICKNESS = 5

COLORS = gd.GRADIENTS["rose_petal"]
GRID_COLOR = (255, 255, 255, 80)

FONT = pg.font.SysFont("bookantiqua", 120, bold=True)
FONT_COLOR = (100, 0, 60)  # deep berry

# ── Pick any gradient from your module ──
PALETTE = gd.GRADIENTS["rose_petal"]  # change this key to any gradient

# Precompute pixel grids (normalized 0→1)
xs = np.linspace(0, 1, WIDTH)
ys = np.linspace(0, 1, HEIGHT)
gx, gy = np.meshgrid(xs, ys)

WINDOW = pg.display.set_mode((WIDTH,HEIGHT))
pg.display.set_caption("TIC TAC TOE")

#-------------------- drawing gradient background ---------------
offset = 0.0

def radial_weight(cx, cy, radius):
    dx = gx - cx
    dy = gy - cy
    return np.clip(1.0 - np.sqrt(dx*dx + dy*dy) / radius, 0, 1)[..., np.newaxis]

def hex_to_np(color):
    """Accepts (R,G,B) tuple from gradient dict → numpy float32 array."""
    return np.array(color, dtype=np.float32)

def draw_gradient(window):
    global offset
    offset += 0.003

    n = len(PALETTE)

    # Animate blob positions using sine/cosine so they drift smoothly
    blobs = []
    for i, color in enumerate(PALETTE):
        angle_x = offset * (0.4 + i * 0.15)
        angle_y = offset * (0.3 + i * 0.18)
        cx = 0.5 + math.sin(angle_x + i * 1.2) * 0.3
        cy = 0.5 + math.cos(angle_y + i * 0.9) * 0.3
        radius = 0.55 + math.sin(offset * 0.5 + i) * 0.1
        blobs.append((cx, cy, radius, hex_to_np(color)))

    # Start with first color as base
    canvas = np.full((HEIGHT, WIDTH, 3), blobs[0][3], dtype=np.float32)

    # Blend each blob on top using its radial weight
    for cx, cy, radius, color in blobs[1:]:
        w = radial_weight(cx, cy, radius)
        canvas = canvas * (1 - w) + color * w

    canvas = np.clip(canvas, 0, 255).astype(np.uint8)
    surf = pg.surfarray.make_surface(np.transpose(canvas, (1, 0, 2)))
    window.blit(surf, (0, 0))

# -------------- Drawing X O -----------------
class Grid:
    def __init__(self):
        self.used = {}
        self.touch = 0 #it defines whose turn X or O depending one value even -> X or odd -> O

    def check_used(self,r,c):
        if f"{r}{c}" not in self.used : 
            return True
        
        return False
    
    def store_XO(self,r,c):
        move = None
        if self.touch%2 == 0:
            move = "X"
        else:
            move = "O"

        self.used[f"{r}{c}"] = move
        self.touch+=1

global grid
grid = Grid()
# -------------- Drawing grid ----------------- 
def draw_grid(window):
    surf = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)

    for col in range(1, 3):
        x = BORDER + RECT_WIDTH * col          # ← add BORDER offset here too
        pg.draw.line(surf, GRID_COLOR, (x, BORDER), (x, HEIGHT - BORDER), OUTLINE_THICKNESS)

    for row in range(1, 3):
        y = BORDER + RECT_HEIGHT * row         # ← add BORDER offset here too
        pg.draw.line(surf, GRID_COLOR, (BORDER, y), (WIDTH - BORDER, y), OUTLINE_THICKNESS)

    window.blit(surf, (0, 0))


# -------------- Drawing Moves -----------------
def draw_moves(window):
    for key, symbol in grid.used.items():
        row = int(key[0])
        col = int(key[1])

        text = FONT.render(symbol, True, FONT_COLOR)

        # each cell starts at BORDER + index * cell_size
        cell_x = BORDER + col * RECT_WIDTH
        cell_y = BORDER + row * RECT_HEIGHT

        # center text inside the cell
        x = cell_x + (RECT_WIDTH  - text.get_width())  // 2
        y = cell_y + (RECT_HEIGHT - text.get_height()) // 2

        window.blit(text, (x, y))

# -------------- Checking Win Condition --------------
def check_win():
  
# checking for rows

    for i in range(0,3): 
        count = 1
        for j in range(1,3):
            if f"{i}{j}" in grid.used and f"{i}{j-1}" in grid.used and grid.used[f"{i}{j}"] == grid.used[f"{i}{j-1}"]:
                count+=1
            else: break

        if count == 3:
            return [(i, 0), (i, 1), (i, 2)],True

    # checking for cols

    for j in range(0,3): 
            count = 1
            for i in range(1,3):
                if f"{i}{j}" in grid.used and f"{i-1}{j}" in grid.used and grid.used[f"{i}{j}"] == grid.used[f"{i-1}{j}"]:
                    count+=1
                else: break

            if count == 3:
                return [(0, j), (1, j), (2, j)],True

    # check for both diagonals

    i = 0
    j = 0
    count = 1
    while i<2 :
        if f"{i}{j}" in grid.used and f"{i+1}{j+1}" in grid.used and grid.used[f"{i}{j}"] == grid.used[f"{i+1}{j+1}"]:
            count+=1
        else: break

        i+=1
        j+=1

    if count == 3:
        return [(0, 0), (1, 1), (2, 2)],True

    i = 0
    j = 2
    count = 1
    while i<2 :
        if f"{i}{j}" in grid.used and f"{i+1}{j-1}" in grid.used and grid.used[f"{i}{j}"] == grid.used[f"{i+1}{j-1}"]:
            count+=1
        else: break
        
        i+=1
        j-=1

    if count == 3:
        return [(0, 2), (1, 1), (2, 0)],True
    
    return (None,False)

# -------------- Drawing Win Line --------------
def draw_win_lines(window, winning_cells):
    r1, c1 = winning_cells[0]
    r2, c2 = winning_cells[2]

    x1 = BORDER + c1 * RECT_WIDTH  + RECT_WIDTH  // 2
    y1 = BORDER + r1 * RECT_HEIGHT + RECT_HEIGHT // 2
    x2 = BORDER + c2 * RECT_WIDTH  + RECT_WIDTH  // 2
    y2 = BORDER + r2 * RECT_HEIGHT + RECT_HEIGHT // 2

    # Extend the line beyond the first and last cell centers
    PAD = 60

    dx = x2 - x1
    dy = y2 - y1
    length = math.sqrt(dx*dx + dy*dy)

    if length != 0:
        ux = dx / length  # unit vector
        uy = dy / length

        x1 = int(x1 - ux * PAD)
        y1 = int(y1 - uy * PAD)
        x2 = int(x2 + ux * PAD)
        y2 = int(y2 + uy * PAD)

    # Draw with alpha so it blends with gradient background
    surf = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
    pg.draw.line(surf, (255, 215, 0, 220), (x1, y1), (x2, y2), 8)
    window.blit(surf, (0, 0))

    pg.display.update()
    pg.time.delay(1500)

def draw_game_over(window, winner):
    # semi-transparent dark overlay
    overlay = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
    pg.draw.rect(overlay, (0, 0, 0, 120), (0, 0, WIDTH, HEIGHT))
    window.blit(overlay, (0, 0))

    # "X Wins!" or "O Wins!" text
    msg_font   = pg.font.SysFont("bookantiqua", 70, bold=True)
    retry_font = pg.font.SysFont("bookantiqua", 32, bold=True)

    msg_text   = msg_font.render(f"{winner} Wins!", True, (255, 215, 0))
    retry_text = retry_font.render("Tap or Press R to Retry ", True, (255, 255, 255, 200))

    # center both texts
    window.blit(msg_text,   (WIDTH // 2 - msg_text.get_width()   // 2, HEIGHT // 2 - 70))
    window.blit(retry_text, (WIDTH // 2 - retry_text.get_width() // 2, HEIGHT // 2 + 20))

    pg.display.update()

# -------------- Drawing Window ----------------
def draw(window):
     
     draw_gradient(window)
     draw_grid(window)
     draw_moves(window)

     pg.display.update()

# -------------- main loop function ------------
def main(window):
    clock = pg.time.Clock()
    run = True
    

    while run:
        clock.tick(FPS)
        game_over = False

        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False
                break
            x,y = None,None
            touched = False
            if event.type == pg.MOUSEBUTTONDOWN:
                x, y = event.pos
                touched = True
                

            if event.type == pg.FINGERDOWN:
                x = int(event.x * WIDTH)
                y = int(event.y * HEIGHT)
                touched = True
                
            
            if x is not None and y is not None:
                # subtract BORDER so clicks outside the grid are ignored
                col = (x - BORDER) // RECT_WIDTH
                row = (y - BORDER) // RECT_HEIGHT

                if 0 <= row < 3 and 0 <= col < 3:
                    if grid.check_used(row, col):
                        grid.store_XO(row, col)
                        win_cells,game_over = check_win()

                        if game_over:
                            winner = "X" if grid.touch % 2 == 1 else "O"

                            draw(window)
                            draw_win_lines(window, win_cells)
                            draw_game_over(window, winner)

                            waiting = True
                            while waiting:
                                for event in pg.event.get():
                                    if event.type == pg.QUIT:
                                        pg.quit()
                                        return

                                    # keyboard retry
                                    if event.type == pg.KEYDOWN:
                                        if event.key == pg.K_r:
                                            grid.__init__()
                                            waiting = False

                                    # mouse click retry
                                    if event.type == pg.MOUSEBUTTONDOWN:
                                        grid.__init__()
                                        waiting = False

                                    # touch/finger retry (mobile)
                                    if event.type == pg.FINGERUP:   # FINGERUP is more reliable than FINGERDOWN
                                        grid.__init__()
                                        waiting = False

                            break

                        if not game_over and len(grid.used) == 9:
                            winner = "No One"
                            draw(window)
                            draw_game_over(window, winner)

                            waiting = True
                            while waiting:
                                for event in pg.event.get():
                                    if event.type == pg.QUIT:
                                        pg.quit()
                                        return

                                    # keyboard retry
                                    if event.type == pg.KEYDOWN:
                                        if event.key == pg.K_r:
                                            grid.__init__()
                                            waiting = False

                                    # mouse click retry
                                    if event.type == pg.MOUSEBUTTONDOWN:
                                        grid.__init__()
                                        waiting = False

                                    # touch/finger retry (mobile)
                                    if event.type == pg.FINGERUP:   # FINGERUP is more reliable than FINGERDOWN
                                        grid.__init__()
                                        waiting = False
                            break


        draw(window)

    pg.quit()


if __name__ == "__main__":
    main(WINDOW)


