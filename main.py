# -*- coding: utf-8 -*-
import pygame as pg
import random as rd
import math
import asyncio


# --------------- initialize pygame -------------------
pg.init()

# --------------- setting up pygame display ------------------
FPS = 60

WIDTH = 600
HEIGHT = 600
BORDER = 18

RECT_WIDTH  = (WIDTH  - BORDER * 2) // 3
RECT_HEIGHT = (HEIGHT - BORDER * 2) // 3

OUTER_PAD = 10
BORDER_RADIUS = 12
OUTLINE_THICKNESS = 5

GRID_COLOR = (255, 255, 255, 80)

FONT = pg.font.SysFont("bookantiqua", 120, bold=True)
FONT_COLOR = (100, 0, 60)  # deep berry

PALETTE = [(255,154,158), (250,208,196), (255,236,210), (252,182,159)]

WINDOW = pg.display.set_mode((WIDTH,HEIGHT))
pg.display.set_caption("TIC TAC TOE")

#-------------------- drawing gradient background ---------------
offset = 0.0

def make_base_surface():
    surf = pg.Surface((WIDTH, HEIGHT))
    surf.fill(PALETTE[0])
    blob_surf = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
    blobs_static = [
        (0.15, 0.15, 0.6,  PALETTE[1]),
        (0.85, 0.2,  0.5,  PALETTE[2]),
        (0.2,  0.85, 0.55, PALETTE[3]),
        (0.75, 0.75, 0.45, PALETTE[0]),
    ]
    for cx_n, cy_n, r_n, color in blobs_static:
        cx = int(cx_n * WIDTH)
        cy = int(cy_n * HEIGHT)
        rx = int(r_n * WIDTH)
        ry = int(r_n * HEIGHT)
        steps = 12
        for s in range(steps, 0, -1):
            alpha = int(180 * (s / steps) ** 1.5)
            ex = int(rx * s / steps)
            ey = int(ry * s / steps)
            pg.draw.ellipse(blob_surf, (*color, alpha),
                            (cx - ex, cy - ey, ex * 2, ey * 2))
    surf.blit(blob_surf, (0, 0))
    return surf

BASE_SURF = make_base_surface()

def draw_gradient(window):
    global offset
    offset += 0.012

    window.blit(BASE_SURF, (0, 0))

    anim_blobs = []
    for i, color in enumerate(PALETTE):
        angle_x = offset * (0.4 + i * 0.15)
        angle_y = offset * (0.3 + i * 0.18)
        cx = 0.5 + math.sin(angle_x + i * 1.2) * 0.3
        cy = 0.5 + math.cos(angle_y + i * 0.9) * 0.3
        anim_blobs.append((cx, cy, color))

    overlay = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
    for cx_n, cy_n, color in anim_blobs:
        cx = int(cx_n * WIDTH)
        cy = int(cy_n * HEIGHT)
        rx, ry = 180, 180
        steps = 10
        for i in range(steps, 0, -1):
            alpha = int(90 * (i / steps) ** 2)
            ex = rx * i // steps
            ey = ry * i // steps
            pg.draw.ellipse(overlay, (*color, alpha),
                            (cx - ex, cy - ey, ex * 2, ey * 2))

    window.blit(overlay, (0, 0))

# -------------- Drawing X O -----------------
class Grid:
    def __init__(self):
        self.used = {}
        self.touch = 0

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
        x = BORDER + RECT_WIDTH * col
        pg.draw.line(surf, GRID_COLOR, (x, BORDER), (x, HEIGHT - BORDER), OUTLINE_THICKNESS)

    for row in range(1, 3):
        y = BORDER + RECT_HEIGHT * row
        pg.draw.line(surf, GRID_COLOR, (BORDER, y), (WIDTH - BORDER, y), OUTLINE_THICKNESS)

    window.blit(surf, (0, 0))


# -------------- Drawing Moves -----------------
def draw_moves(window):
    for key, symbol in grid.used.items():
        row = int(key[0])
        col = int(key[1])

        text = FONT.render(symbol, True, FONT_COLOR)

        cell_x = BORDER + col * RECT_WIDTH
        cell_y = BORDER + row * RECT_HEIGHT

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

    PAD = 60

    dx = x2 - x1
    dy = y2 - y1
    length = math.sqrt(dx*dx + dy*dy)

    if length != 0:
        ux = dx / length
        uy = dy / length

        x1 = int(x1 - ux * PAD)
        y1 = int(y1 - uy * PAD)
        x2 = int(x2 + ux * PAD)
        y2 = int(y2 + uy * PAD)

    surf = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
    pg.draw.line(surf, (255, 215, 0, 220), (x1, y1), (x2, y2), 8)
    window.blit(surf, (0, 0))

    # NO pg.time.delay here -- handled by win_timer in main loop

def draw_game_over(window, winner):
    overlay = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
    pg.draw.rect(overlay, (0, 0, 0, 120), (0, 0, WIDTH, HEIGHT))
    window.blit(overlay, (0, 0))

    msg_font   = pg.font.SysFont("bookantiqua", 70, bold=True)
    retry_font = pg.font.SysFont("bookantiqua", 32, bold=True)

    msg_text   = msg_font.render(f"{winner} Wins!", True, (255, 215, 0))
    retry_text = retry_font.render("Tap or Press R to Retry ", True, (255, 255, 255, 200))

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
async def main(window):
    clock = pg.time.Clock()
    run = True

    # State machine instead of blocking inner loops
    state = "playing"   # "playing" | "win_pause" | "game_over"
    winner = None
    win_cells = None
    win_timer = 0       # counts frames instead of pg.time.delay
    frozen_surf = None  # snapshot of screen to prevent blinking in game_over

    while run:
        clock.tick(FPS)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False
                break

            # --- Retry input (win_pause waits for timer, game_over accepts input) ---
            if state == "game_over":
                if event.type == pg.KEYDOWN and event.key == pg.K_r:
                    grid.__init__()
                    frozen_surf = None
                    win_cells = None
                    state = "playing"
                    continue                  # skip rest -- don't let this event reach playing logic
                if event.type == pg.MOUSEBUTTONDOWN:
                    grid.__init__()
                    frozen_surf = None
                    win_cells = None
                    state = "playing"
                    continue                  # skip rest -- don't let this event reach playing logic
                if event.type == pg.FINGERUP:
                    grid.__init__()
                    frozen_surf = None
                    win_cells = None
                    state = "playing"
                    continue                  # skip rest -- don't let this event reach playing logic

            # --- Normal play input ---
            if state == "playing":
                x, y = None, None
                touched = False
                if event.type == pg.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    touched = True
                if event.type == pg.FINGERDOWN:
                    x = int(event.x * WIDTH)
                    y = int(event.y * HEIGHT)
                    touched = True

                if x is not None and y is not None:
                    col = (x - BORDER) // RECT_WIDTH
                    row = (y - BORDER) // RECT_HEIGHT

                    if 0 <= row < 3 and 0 <= col < 3:
                        if grid.check_used(row, col):
                            grid.store_XO(row, col)
                            win_cells, game_over = check_win()

                            if game_over:
                                winner = "X" if grid.touch % 2 == 1 else "O"
                                # Draw once and freeze into snapshot
                                draw(window)
                                draw_win_lines(window, win_cells)
                                frozen_surf = window.copy()
                                state = "win_pause"
                                win_timer = 0

                            elif len(grid.used) == 9:
                                winner = "No One"
                                # Draw once and freeze into snapshot
                                draw(window)
                                frozen_surf = window.copy()
                                state = "game_over"

        # --- Draw based on state ---
        if state == "playing":
            draw(window)

        elif state == "win_pause":
            # Just blit the frozen snapshot -- no gradient redrawn, no flicker
            window.blit(frozen_surf, (0, 0))
            pg.display.update()
            win_timer += 1
            if win_timer >= FPS * 1.5:   # 1.5 seconds at 60fps (same as your delay(1500))
                # Freeze game_over screen as snapshot too
                draw_game_over(window, winner)
                frozen_surf = window.copy()
                state = "game_over"

        elif state == "game_over":
            # Just blit the frozen snapshot -- completely static, no flicker
            window.blit(frozen_surf, (0, 0))
            pg.display.update()

        await asyncio.sleep(0)

    pg.quit()


if __name__ == "__main__":
    asyncio.run(main(WINDOW))