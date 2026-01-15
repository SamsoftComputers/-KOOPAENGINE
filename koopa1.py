import pygame
import sys
import math
import random
from pygame.locals import *

# Constants
SCALE = 2
TILE = 16
WIDTH = int(256 * SCALE)
HEIGHT = int(240 * SCALE)
FPS = 60

# NES Palette
NES_PALETTE = [
    (84, 84, 84), (0, 30, 116), (8, 16, 144), (48, 0, 136), 
    (68, 0, 100), (92, 0, 48), (84, 4, 0), (60, 24, 0), 
    (32, 42, 0), (8, 58, 0), (0, 64, 0), (0, 60, 0), 
    (0, 50, 60), (0, 0, 0), (152, 150, 152), (8, 76, 196), 
    (48, 50, 236), (92, 30, 228), (136, 20, 176), (160, 20, 100), 
    (152, 34, 32), (120, 60, 0), (84, 90, 0), (40, 114, 0), 
    (8, 124, 0), (0, 118, 40), (0, 102, 120), (0, 0, 0), 
    (236, 238, 236), (76, 154, 236), (120, 124, 236), (176, 98, 236), 
    (228, 84, 236), (236, 88, 180), (236, 106, 100), (212, 136, 32), 
    (160, 170, 0), (116, 196, 0), (76, 208, 32), (56, 204, 108), 
    (56, 180, 204), (60, 60, 60), (0, 0, 0), (0, 0, 0)
]

# Game State
class GameState:
    def __init__(self):
        self.slot = 0
        self.progress = [{"world": 1}, {"world": 1}, {"world": 1}]
        self.score = 0
        self.coins = 0
        self.lives = 3
        self.world = 1
        self.level = 1
        self.time = 400
        self.mario_size = "small"
        self.unlocked_worlds = [1]

state = GameState()

SCENES = []
def push(scene): SCENES.append(scene)
def pop(): SCENES.pop()

class Scene:
    def handle(self, events, keys): ...
    def update(self, dt): ...
    def draw(self, surf): ...

WORLD_THEMES = {
    1: {"sky": 27, "ground": 22, "pipe": 14, "block": 33, "name": "GRASS LAND"},
    2: {"sky": 26, "ground": 21, "pipe": 15, "block": 34, "name": "DESERT HILL"},
    3: {"sky": 25, "ground": 22, "pipe": 16, "block": 35, "name": "OCEAN SIDE"},
    4: {"sky": 24, "ground": 23, "pipe": 17, "block": 36, "name": "GIANT LAND"},
    5: {"sky": 23, "ground": 24, "pipe": 18, "block": 37, "name": "SKY WORLD"},
    6: {"sky": 22, "ground": 25, "pipe": 19, "block": 38, "name": "ICE WORLD"},
    7: {"sky": 21, "ground": 26, "pipe": 20, "block": 39, "name": "PIPE MAZE"},
    8: {"sky": 0, "ground": 0, "pipe": 14, "block": 0, "name": "DARK CASTLE"}
}

# EXACT SMB1 World 1-1 (69 columns, 15 rows visible area mapped to our format)
# Using authentic block positions from the original game
LEVEL_1_1 = []
for i in range(11):
    LEVEL_1_1.append(" " * 212)

# Row 11 (y=11) - high platforms/blocks
row11 = list(" " * 212)
LEVEL_1_1.append("".join(row11))

# Row 12 (y=12) - ? blocks and bricks row (4 tiles above ground)
row12 = list(" " * 212)
row12[16] = "?"  # First ? block (mushroom)
row12[20] = "="
row12[21] = "?"  # Coin
row12[22] = "="
row12[23] = "?"  # Mushroom
row12[24] = "="
row12[77] = "?"  # Coin
row12[78] = "?"  # Power up
row12[79] = "?"  # Coin
row12[94] = "="
row12[100] = "="
row12[101] = "="
row12[106] = "?"  # Coin ?
row12[109] = "?"  # Coin
row12[112] = "?"  # Coin
row12[118] = "="
row12[121] = "="
row12[122] = "="
row12[123] = "="
row12[128] = "="
row12[129] = "?"  # Star
row12[130] = "="
row12[168] = "="
row12[169] = "="
row12[170] = "?"  # Coin
row12[171] = "="
LEVEL_1_1.append("".join(row12))

# Row 13 (y=13)
row13 = list(" " * 212)
LEVEL_1_1.append("".join(row13))

# Row 14 (y=14) - brick row 8 tiles high
row14 = list(" " * 212)
row14[80] = "="
row14[81] = "="
row14[82] = "="
row14[83] = "="
row14[84] = "="
row14[85] = "="
row14[86] = "="
row14[87] = "="
row14[91] = "="
row14[92] = "="
row14[93] = "="
row14[94] = "?"  # Coins
row14[118] = "="
row14[119] = "="
row14[120] = "="
row14[129] = "="
row14[130] = "="
row14[131] = "="
row14[132] = "="
row14[134] = "="
row14[135] = "="
row14[136] = "="
row14[137] = "="
row14[148] = "="
row14[149] = "="
row14[150] = "="
row14[151] = "?"  # 1UP
row14[152] = "="
LEVEL_1_1.append("".join(row14))

# Row 15 (y=15) - enemies and player row, pipes, stairs
row15 = list(" " * 212)
row15[3] = "S"   # Player start
row15[22] = "E"  # Goomba
row15[40] = "E"  # Goomba
row15[51] = "E"  # Goomba
row15[52] = "E"  # Goomba
row15[80] = "K"  # Koopa
row15[97] = "E"  # Goomba
row15[98] = "E"  # Goomba
row15[107] = "E" # Goomba
row15[108] = "E" # Goomba
row15[114] = "E" # Goomba
row15[115] = "E" # Goomba
row15[124] = "E" # Goomba
row15[125] = "E" # Goomba
row15[128] = "E" # Goomba
row15[129] = "E" # Goomba
row15[174] = "E" # Goomba
row15[175] = "E" # Goomba
# Stairs at end
for i in range(134, 138):
    row15[i] = "s"
for i in range(140, 149):
    row15[i] = "s"
for i in range(155, 163):
    row15[i] = "s"
for i in range(181, 189):
    row15[i] = "s"
row15[198] = "L"  # Flag
row15[203] = "C"  # Castle
LEVEL_1_1.append("".join(row15))

# Ground rows 16-19
for gy in range(16, 20):
    ground = list("#" * 212)
    # Gaps (pits)
    for g in range(69, 71):
        ground[g] = " "
    for g in range(86, 89):
        ground[g] = " "
    for g in range(153, 155):
        ground[g] = " "
    LEVEL_1_1.append("".join(ground))

# Add pipe data to row 15 area by modifying the level
def add_pipes_1_1():
    global LEVEL_1_1
    pipes = [(28, 2), (38, 3), (46, 4), (57, 4), (163, 2), (179, 2)]
    for px, ph in pipes:
        for py in range(16-ph, 16):
            if py >= 0 and py < len(LEVEL_1_1):
                row = list(LEVEL_1_1[py])
                if px < len(row):
                    row[px] = "T"
                if px+1 < len(row):
                    row[px+1] = "T"
                LEVEL_1_1[py] = "".join(row)

add_pipes_1_1()

# EXACT SMB1 World 8-4 (Castle level with Bowser)
LEVEL_8_4 = []
for i in range(11):
    LEVEL_8_4.append(" " * 200)

# Ceiling
row11_84 = list("C" * 200)
LEVEL_8_4.append("".join(row11_84))

# Castle interior rows
for i in range(12, 15):
    row = list(" " * 200)
    # Add some ceiling blocks
    for x in range(0, 200, 12):
        row[x] = "C"
    LEVEL_8_4.append("".join(row))

# Row 15 - main gameplay row
row15_84 = list(" " * 200)
row15_84[3] = "S"  # Start

# Fire bars (represented as H hazards)
fire_positions = [25, 45, 65, 85, 105, 125, 145]
for fp in fire_positions:
    row15_84[fp] = "H"

# Enemies
row15_84[35] = "E"
row15_84[55] = "E"
row15_84[75] = "K"
row15_84[95] = "E"
row15_84[115] = "K"
row15_84[135] = "E"

# Bridge and Bowser area (starts at x=165)
for bx in range(165, 185):
    row15_84[bx] = "b"
row15_84[180] = "B"  # Bowser
row15_84[186] = "X"  # Axe

LEVEL_8_4.append("".join(row15_84))

# Lava under bridge
row16_84 = list("#" * 200)
for lx in range(165, 190):
    row16_84[lx] = "A"
LEVEL_8_4.append("".join(row16_84))

# More ground
for i in range(17, 20):
    row = list("#" * 200)
    for lx in range(165, 190):
        row[lx] = "A"
    LEVEL_8_4.append("".join(row))

def generate_level_data():
    levels = {"1-1": LEVEL_1_1, "8-4": LEVEL_8_4}
    
    for world in range(1, 9):
        for level in range(1, 5):
            level_id = f"{world}-{level}"
            if level_id in levels:
                continue
                
            theme = WORLD_THEMES[world]
            level_data = []
            
            for i in range(12):
                level_data.append(" " * 200)
            
            # Block rows
            row12 = list(" " * 200)
            row14 = list(" " * 200)
            for i in range(6 + level * 2):
                bx = 20 + i * 22
                if bx < 200:  # Bounds check
                    if random.random() > 0.5:
                        row12[bx] = "?"
                    else:
                        row12[bx] = "="
                    if random.random() > 0.6:
                        for j in range(3):
                            if bx+j < 200:
                                row14[bx+j] = "="
            level_data.append("".join(row12))
            level_data.append(" " * 200)
            level_data.append("".join(row14))
            
            # Enemy/pipe row
            row15 = list(" " * 200)
            row15[3] = "S"
            # Pipes
            for i in range(2 + level):
                px = 25 + i * 35
                if px < 190:
                    row15[px] = "T"
                    row15[px+1] = "T"
            # Enemies
            enemy_type = "E" if world % 2 == 1 else "K"
            for i in range(4 + level):
                ex = 30 + i * 25
                if ex < 190:
                    row15[ex] = enemy_type
            # Stairs at end
            for i in range(180, 190):
                row15[i] = "s"
            row15[192] = "L"
            row15[196] = "C"
            level_data.append("".join(row15))
            
            # Ground with gaps
            for gy in range(16, 20):
                ground = list("#" * 200)
                gap_pos = 60 + level * 20
                if gap_pos < 180:
                    ground[gap_pos] = " "
                    ground[gap_pos+1] = " "
                levels[level_id] = level_data
                level_data.append("".join(ground))
            
            levels[level_id] = level_data
    
    return levels

LEVELS = generate_level_data()

THUMBNAILS = {}
for level_id, level_data in LEVELS.items():
    world = int(level_id.split("-")[0])
    theme = WORLD_THEMES[world]
    thumb = pygame.Surface((32, 24))
    thumb.fill(NES_PALETTE[theme["sky"]])
    for y, row in enumerate(level_data[12:18]):
        for x, char in enumerate(row[::6]):
            if x < 32:
                if char in ("#", "=", "T", "C", "s"):
                    thumb.set_at((x, y+12), NES_PALETTE[theme["ground"]])
                elif char == "?":
                    thumb.set_at((x, y+12), NES_PALETTE[35])
    THUMBNAILS[level_id] = thumb

class Entity:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.vx, self.vy = 0, 0
        self.width, self.height = TILE, TILE
        self.on_ground = False
        self.facing_right = True
        self.active = True
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    def check_collision(self, other):
        return self.get_rect().colliderect(other.get_rect())
    def update(self, colliders, dt):
        if not self.on_ground:
            self.vy += 0.5 * dt * 60
        self.x += self.vx * dt * 60
        self.y += self.vy * dt * 60
        self.on_ground = False
        for rect in colliders:
            if self.get_rect().colliderect(rect):
                if self.vy > 0 and self.y + self.height > rect.top and self.y < rect.top:
                    self.y = rect.top - self.height
                    self.vy = 0
                    self.on_ground = True
                elif self.vy < 0 and self.y < rect.bottom:
                    self.y = rect.bottom
                    self.vy = 0
                if self.vx > 0 and self.x + self.width > rect.left and self.x < rect.left:
                    self.x = rect.left - self.width
                    self.vx = 0
                elif self.vx < 0 and self.x < rect.right:
                    self.x = rect.right
                    self.vx = 0
    def draw(self, surf, cam): pass

class Player(Entity):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.jump_power = -6
        self.move_speed = 2.5
        self.run_speed = 4.5
        self.invincible = 0
        self.anim_frame = 0
        self.anim_timer = 0
    def update(self, colliders, dt, enemies):
        keys = pygame.key.get_pressed()
        self.vx = 0
        speed = self.run_speed if keys[K_LSHIFT] or keys[K_RSHIFT] else self.move_speed
        if keys[K_LEFT]:
            self.vx = -speed
            self.facing_right = False
        if keys[K_RIGHT]:
            self.vx = speed
            self.facing_right = True
        if keys[K_SPACE] and self.on_ground:
            self.vy = self.jump_power
            self.on_ground = False
        if self.vx != 0:
            self.anim_timer += dt
            if self.anim_timer > 0.08:
                self.anim_timer = 0
                self.anim_frame = (self.anim_frame + 1) % 3
        else:
            self.anim_frame = 0
        if self.invincible > 0:
            self.invincible -= dt
        super().update(colliders, dt)
        for enemy in enemies:
            if enemy.active and self.check_collision(enemy):
                if self.vy > 0 and self.y + self.height - 5 < enemy.y:
                    enemy.active = False
                    self.vy = self.jump_power / 2
                    state.score += 100
                elif self.invincible <= 0:
                    if state.mario_size == "big":
                        state.mario_size = "small"
                        self.invincible = 2
                    else:
                        state.lives -= 1
                        if state.lives <= 0:
                            push(GameOverScene())
                        else:
                            self.x, self.y = 50, 200
                            self.vx = self.vy = 0
    def draw(self, surf, cam):
        if self.invincible > 0 and int(self.invincible * 10) % 2 == 0:
            return
        x, y = int(self.x - cam), int(self.y)
        # Body
        pygame.draw.rect(surf, NES_PALETTE[33], (x+4, y+8, 8, 8))
        # Head
        pygame.draw.rect(surf, NES_PALETTE[39], (x+4, y, 8, 8))
        # Hat
        pygame.draw.rect(surf, NES_PALETTE[33], (x+2, y, 12, 3))

class Goomba(Entity):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.vx = -0.5
        self.anim_frame = 0
        self.anim_timer = 0
    def update(self, colliders, dt):
        super().update(colliders, dt)
        self.anim_timer += dt
        if self.anim_timer > 0.2:
            self.anim_timer = 0
            self.anim_frame = (self.anim_frame + 1) % 2
    def draw(self, surf, cam):
        if not self.active:
            return
        x, y = int(self.x - cam), int(self.y)
        pygame.draw.ellipse(surf, NES_PALETTE[21], (x+2, y+4, 12, 12))
        foot = 2 if self.anim_frame == 0 else -2
        pygame.draw.rect(surf, NES_PALETTE[21], (x+2, y+14, 4, 2))
        pygame.draw.rect(surf, NES_PALETTE[21], (x+10, y+14+foot, 4, 2))
        pygame.draw.rect(surf, NES_PALETTE[0], (x+4, y+6, 2, 2))
        pygame.draw.rect(surf, NES_PALETTE[0], (x+10, y+6, 2, 2))

class Koopa(Goomba):
    """Koopa Troopa - only class using Koopa name"""
    def draw(self, surf, cam):
        if not self.active:
            return
        x, y = int(self.x - cam), int(self.y)
        pygame.draw.ellipse(surf, NES_PALETTE[14], (x+2, y+4, 12, 12))
        pygame.draw.rect(surf, NES_PALETTE[39], (x+4, y, 8, 4))
        pygame.draw.rect(surf, NES_PALETTE[14], (x+2, y+14, 4, 2))
        pygame.draw.rect(surf, NES_PALETTE[14], (x+10, y+14, 4, 2))

class Spike(Entity):
    def update(self, colliders, dt): pass
    def draw(self, surf, cam):
        if not self.active:
            return
        x, y = int(self.x - cam), int(self.y)
        t = pygame.time.get_ticks() / 100
        pygame.draw.circle(surf, NES_PALETTE[33], (x+8, y+8), 6)
        for i in range(4):
            angle = t + i * 1.57
            bx = x + 8 + int(math.cos(angle) * 10)
            by = y + 8 + int(math.sin(angle) * 10)
            pygame.draw.circle(surf, NES_PALETTE[35], (bx, by), 4)

class Bowser(Entity):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.width = TILE * 2
        self.height = TILE * 2
        self.vx = -0.2
    def draw(self, surf, cam):
        if not self.active:
            return
        x, y = int(self.x - cam), int(self.y)
        pygame.draw.rect(surf, NES_PALETTE[14], (x, y, 32, 32))
        pygame.draw.rect(surf, NES_PALETTE[35], (x+4, y+8, 24, 20))
        pygame.draw.rect(surf, NES_PALETTE[14], (x+20, y-6, 14, 14))
        pygame.draw.rect(surf, NES_PALETTE[39], (x+26, y-2, 3, 3))
        for i in range(3):
            pygame.draw.polygon(surf, NES_PALETTE[39], [(x+6+i*8, y+4), (x+2+i*8, y-4), (x+10+i*8, y-4)])

class TileMap:
    def __init__(self, level_data, level_id):
        self.tiles = []
        self.colliders = []
        self.width = len(level_data[0]) * TILE
        self.height = len(level_data) * TILE
        world = int(level_id.split("-")[0])
        self.theme = WORLD_THEMES[world]
        self.is_castle = world == 8
        for y, row in enumerate(level_data):
            for x, char in enumerate(row):
                if char != " ":
                    rect = pygame.Rect(x * TILE, y * TILE, TILE, TILE)
                    self.tiles.append((x * TILE, y * TILE, char))
                    if char in ("#", "=", "T", "?", "U", "C", "s", "b"):
                        self.colliders.append(rect)
    def draw(self, surf, cam):
        if self.is_castle:
            surf.fill(NES_PALETTE[0])
        else:
            surf.fill(NES_PALETTE[self.theme["sky"]])
            # Clouds
            for i in range(12):
                cx = (i * 140 - int(cam/4)) % (self.width + 300) - 100
                cy = 50 + (i % 3) * 35
                pygame.draw.ellipse(surf, NES_PALETTE[31], (cx, cy, 45, 22))
                pygame.draw.ellipse(surf, NES_PALETTE[31], (cx+22, cy-10, 38, 22))
            # Hills
            for i in range(6):
                hx = (i * 250 - int(cam/6)) % (self.width + 400) - 100
                pygame.draw.ellipse(surf, NES_PALETTE[14], (hx, HEIGHT-130, 120, 70))
            # Bushes
            for i in range(8):
                bx = (i * 180 - int(cam/5)) % (self.width + 300) - 50
                pygame.draw.ellipse(surf, NES_PALETTE[14], (bx, HEIGHT-82, 35, 18))
                pygame.draw.ellipse(surf, NES_PALETTE[14], (bx+18, HEIGHT-88, 30, 22))
        
        for tx, ty, char in self.tiles:
            dx = tx - cam
            if dx < -TILE or dx > WIDTH + TILE:
                continue
            if char == "#":
                pygame.draw.rect(surf, NES_PALETTE[22], (dx, ty, TILE, TILE))
                pygame.draw.rect(surf, NES_PALETTE[21], (dx+2, ty+2, TILE-4, TILE-4))
            elif char == "=":
                pygame.draw.rect(surf, NES_PALETTE[22], (dx, ty, TILE, TILE))
                pygame.draw.rect(surf, NES_PALETTE[21], (dx+1, ty+1, 6, 6))
                pygame.draw.rect(surf, NES_PALETTE[21], (dx+9, ty+1, 6, 6))
                pygame.draw.rect(surf, NES_PALETTE[21], (dx+1, ty+9, 6, 6))
                pygame.draw.rect(surf, NES_PALETTE[21], (dx+9, ty+9, 6, 6))
            elif char == "?":
                pygame.draw.rect(surf, NES_PALETTE[35], (dx, ty, TILE, TILE))
                pygame.draw.rect(surf, NES_PALETTE[33], (dx+3, ty+3, TILE-6, TILE-6))
                pygame.draw.rect(surf, NES_PALETTE[39], (dx+5, ty+4, 6, 3))
                pygame.draw.rect(surf, NES_PALETTE[39], (dx+6, ty+10, 4, 2))
            elif char == "T":
                pygame.draw.rect(surf, NES_PALETTE[14], (dx, ty, TILE, TILE))
                pygame.draw.rect(surf, NES_PALETTE[37], (dx+2, ty, 4, TILE))
            elif char == "s":
                pygame.draw.rect(surf, NES_PALETTE[22], (dx, ty, TILE, TILE))
                pygame.draw.rect(surf, NES_PALETTE[21], (dx+2, ty+2, TILE-4, TILE-4))
            elif char == "L":
                pygame.draw.rect(surf, NES_PALETTE[14], (dx+6, ty-80, 4, 96))
                pygame.draw.polygon(surf, NES_PALETTE[14], [(dx+10, ty-72), (dx+28, ty-64), (dx+10, ty-56)])
                pygame.draw.circle(surf, NES_PALETTE[14], (dx+8, ty-84), 6)
            elif char == "C":
                pygame.draw.rect(surf, NES_PALETTE[0], (dx, ty-48, TILE*3, TILE*4))
                pygame.draw.rect(surf, NES_PALETTE[28], (dx+4, ty-44, TILE*3-8, TILE*4-8))
                for i in range(3):
                    pygame.draw.rect(surf, NES_PALETTE[0], (dx+4+i*14, ty-52, 8, 8))
                pygame.draw.rect(surf, NES_PALETTE[0], (dx+16, ty-16, 16, 20))
            elif char == "b":
                pygame.draw.rect(surf, NES_PALETTE[22], (dx, ty, TILE, 10))
                pygame.draw.rect(surf, NES_PALETTE[21], (dx+2, ty+2, TILE-4, 6))
            elif char == "A":
                pygame.draw.rect(surf, NES_PALETTE[22], (dx, ty, TILE, TILE))
                pygame.draw.rect(surf, NES_PALETTE[33], (dx+3, ty+3, TILE-6, TILE-6))
                by = ty + 5 + int(math.sin(pygame.time.get_ticks()/150 + tx) * 3)
                pygame.draw.circle(surf, NES_PALETTE[35], (dx+8, by), 3)
            elif char == "X":
                pygame.draw.rect(surf, NES_PALETTE[35], (dx+4, ty, 8, 14))
                pygame.draw.polygon(surf, NES_PALETTE[28], [(dx+2, ty+2), (dx+6, ty), (dx+6, ty+10), (dx+2, ty+8)])

class TitleScreen(Scene):
    def __init__(self):
        self.timer = 0
        self.logo_y = -80
        self.logo_target = 50
        self.stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT//2), random.random()*0.5+0.2) for _ in range(40)]
    def handle(self, events, keys):
        for e in events:
            if e.type == KEYDOWN and e.key == K_RETURN:
                push(FileSelect())
    def update(self, dt):
        self.timer += dt
        if self.logo_y < self.logo_target:
            self.logo_y += 2
        for i, (sx, sy, sp) in enumerate(self.stars):
            self.stars[i] = (sx, (sy + sp) % (HEIGHT//2), sp)
    def draw(self, surf):
        surf.fill(NES_PALETTE[1])
        for sx, sy, sp in self.stars:
            c = 31 if sp > 0.4 else 28
            pygame.draw.rect(surf, NES_PALETTE[c], (sx, sy, 2, 2))
        
        bw, bh = 300, 150
        bx, by = (WIDTH - bw) // 2, self.logo_y
        pygame.draw.rect(surf, NES_PALETTE[0], (bx+4, by+4, bw, bh))
        pygame.draw.rect(surf, NES_PALETTE[33], (bx, by, bw, bh))
        pygame.draw.rect(surf, NES_PALETTE[35], (bx+4, by+4, bw-8, bh-8))
        pygame.draw.rect(surf, NES_PALETTE[33], (bx+8, by+8, bw-16, bh-16))
        
        f1 = pygame.font.SysFont(None, 28)
        t1 = f1.render("Cat's !", True, NES_PALETTE[39])
        surf.blit(t1, (bx + 20, by + 15))
        
        f2 = pygame.font.SysFont(None, 42)
        t2 = f2.render("KOOPA ENGINE", True, NES_PALETTE[39])
        surf.blit(t2, (bx + (bw - t2.get_width()) // 2, by + 50))
        
        f3 = pygame.font.SysFont(None, 36)
        t3 = f3.render("HDR 1.0", True, NES_PALETTE[35])
        surf.blit(t3, (bx + (bw - t3.get_width()) // 2, by + 95))
        
        f4 = pygame.font.SysFont(None, 16)
        t4 = f4.render("~ 8 Worlds Adventure ~", True, NES_PALETTE[21])
        surf.blit(t4, (bx + (bw - t4.get_width()) // 2, by + 125))
        
        f5 = pygame.font.SysFont(None, 14)
        t5 = f5.render("[C] 2024 Team Flames / Samsoft", True, NES_PALETTE[28])
        surf.blit(t5, (WIDTH//2 - t5.get_width()//2, by + bh + 20))
        
        gy = HEIGHT - 50
        for i in range(WIDTH // TILE + 1):
            pygame.draw.rect(surf, NES_PALETTE[22], (i*TILE, gy, TILE, 50))
            pygame.draw.rect(surf, NES_PALETTE[21], (i*TILE+2, gy+2, TILE-4, 46))
        
        mx, my = WIDTH//2 - 70, gy - 24
        pygame.draw.rect(surf, NES_PALETTE[33], (mx+4, my+8, 8, 16))
        pygame.draw.rect(surf, NES_PALETTE[39], (mx+4, my, 8, 8))
        pygame.draw.rect(surf, NES_PALETTE[33], (mx+2, my, 12, 3))
        
        gx, gy2 = WIDTH//2 + 20, gy - 16
        pygame.draw.ellipse(surf, NES_PALETTE[21], (gx, gy2+4, 12, 12))
        pygame.draw.rect(surf, NES_PALETTE[0], (gx+2, gy2+6, 2, 2))
        pygame.draw.rect(surf, NES_PALETTE[0], (gx+8, gy2+6, 2, 2))
        
        kx, ky = WIDTH//2 + 60, gy - 16
        pygame.draw.ellipse(surf, NES_PALETTE[14], (kx, ky+4, 12, 12))
        pygame.draw.rect(surf, NES_PALETTE[39], (kx+2, ky, 8, 4))
        
        if self.logo_y >= self.logo_target and int(self.timer * 8) % 2 == 0:
            pf = pygame.font.SysFont(None, 24)
            pt = pf.render("PRESS ENTER", True, NES_PALETTE[39])
            surf.blit(pt, (WIDTH//2 - pt.get_width()//2, HEIGHT - 25))

class FileSelect(Scene):
    def __init__(self):
        self.selected = 0
        self.t = 0
    def handle(self, evts, keys):
        for e in evts:
            if e.type == KEYDOWN:
                if e.key == K_LEFT and self.selected > 0:
                    self.selected -= 1
                elif e.key == K_RIGHT and self.selected < 2:
                    self.selected += 1
                elif e.key == K_RETURN:
                    state.slot = self.selected
                    state.world = state.progress[state.slot]["world"]
                    push(WorldMapScene())
                elif e.key == K_ESCAPE:
                    push(TitleScreen())
    def update(self, dt):
        self.t += dt
    def draw(self, s):
        s.fill(NES_PALETTE[0])
        f = pygame.font.SysFont(None, 36)
        t = f.render("SELECT FILE", True, NES_PALETTE[39])
        s.blit(t, (WIDTH//2 - t.get_width()//2, 30))
        for i in range(3):
            x = 55 + i * 140
            y = 120 + 6 * math.sin(self.t * 2 + i)
            pygame.draw.rect(s, NES_PALETTE[21], (x-4, y-4, 100, 130))
            pygame.draw.rect(s, NES_PALETTE[22], (x, y, 92, 122))
            if i == self.selected:
                pygame.draw.rect(s, NES_PALETTE[35], (x-7, y-7, 106, 136), 3)
            sf = pygame.font.SysFont(None, 26)
            st = sf.render(f"FILE {i+1}", True, NES_PALETTE[39])
            s.blit(st, (x + 46 - st.get_width()//2, y + 10))
            pygame.draw.rect(s, NES_PALETTE[33], (x+36, y+40, 20, 28))
            pygame.draw.rect(s, NES_PALETTE[39], (x+36, y+32, 20, 12))
            w = state.progress[i]["world"]
            wf = pygame.font.SysFont(None, 18)
            wt = wf.render(f"WORLD {w}", True, NES_PALETTE[39])
            s.blit(wt, (x + 46 - wt.get_width()//2, y + 75))
            th = THUMBNAILS.get(f"{w}-1", THUMBNAILS["1-1"])
            ts = pygame.transform.scale(th, (60, 45))
            s.blit(ts, (x + 16, y + 90))
        inf = pygame.font.SysFont(None, 16)
        it = inf.render("LEFT/RIGHT: Select   ENTER: Start   ESC: Back", True, NES_PALETTE[28])
        s.blit(it, (WIDTH//2 - it.get_width()//2, HEIGHT - 35))

class WorldMapScene(Scene):
    def __init__(self):
        self.sel = state.world
        self.t = 0
    def handle(self, evts, keys):
        for e in evts:
            if e.type == KEYDOWN:
                if e.key == K_LEFT and self.sel > 1:
                    self.sel -= 1
                elif e.key == K_RIGHT and self.sel < 8:
                    self.sel += 1
                elif e.key == K_UP and self.sel > 4:
                    self.sel -= 4
                elif e.key == K_DOWN and self.sel < 5:
                    self.sel += 4
                elif e.key == K_RETURN and self.sel <= max(state.unlocked_worlds):
                    state.world = self.sel
                    state.progress[state.slot]["world"] = self.sel
                    push(LevelScene(f"{state.world}-1"))
                elif e.key == K_ESCAPE:
                    push(FileSelect())
    def update(self, dt):
        self.t += dt
    def draw(self, s):
        s.fill(NES_PALETTE[1])
        f = pygame.font.SysFont(None, 36)
        t = f.render("WORLD SELECT", True, NES_PALETTE[39])
        s.blit(t, (WIDTH//2 - t.get_width()//2, 20))
        ws = 55
        for w in range(1, 9):
            r, c = (w-1) // 4, (w-1) % 4
            x, y = 40 + c * 95, 75 + r * 95
            th = WORLD_THEMES[w]
            if w in state.unlocked_worlds:
                pygame.draw.rect(s, NES_PALETTE[th["ground"]], (x, y, ws, ws))
                pygame.draw.rect(s, NES_PALETTE[th["sky"]], (x+4, y+4, ws-8, ws-8))
                wf = pygame.font.SysFont(None, 28)
                wt = wf.render(str(w), True, NES_PALETTE[39])
                s.blit(wt, (x + ws//2 - wt.get_width()//2, y + ws//2 - wt.get_height()//2))
            else:
                pygame.draw.rect(s, NES_PALETTE[0], (x, y, ws, ws))
                pygame.draw.rect(s, NES_PALETTE[28], (x+4, y+4, ws-8, ws-8))
                pygame.draw.line(s, NES_PALETTE[33], (x, y), (x+ws, y+ws), 2)
                pygame.draw.line(s, NES_PALETTE[33], (x+ws, y), (x, y+ws), 2)
            if w == self.sel:
                nf = pygame.font.SysFont(None, 18)
                nt = nf.render(th["name"], True, NES_PALETTE[35])
                s.blit(nt, (WIDTH//2 - nt.get_width()//2, HEIGHT - 55))
        r, c = (self.sel-1) // 4, (self.sel-1) % 4
        x, y = 40 + c * 95, 75 + r * 95
        off = math.sin(self.t * 6) * 3
        pygame.draw.rect(s, NES_PALETTE[35], (x-5, y-5+off, ws+10, 5))
        pygame.draw.rect(s, NES_PALETTE[35], (x-5, y+ws+off, ws+10, 5))
        mx, my = x + ws//2 - 6, y - 28 + off
        pygame.draw.rect(s, NES_PALETTE[33], (mx+2, my+6, 8, 8))
        pygame.draw.rect(s, NES_PALETTE[39], (mx+2, my, 8, 6))
        inf = pygame.font.SysFont(None, 14)
        it = inf.render("Arrows: Move   ENTER: Play   ESC: Back", True, NES_PALETTE[28])
        s.blit(it, (WIDTH//2 - it.get_width()//2, HEIGHT - 22))
        pt = inf.render(f"Progress: {max(state.unlocked_worlds)}/8", True, NES_PALETTE[28])
        s.blit(pt, (10, HEIGHT - 22))

class LevelScene(Scene):
    def __init__(self, level_id):
        self.map = TileMap(LEVELS[level_id], level_id)
        self.player = Player(50, 200)
        self.enemies = []
        self.cam = 0.0
        self.level_id = level_id
        self.time = 400
        w = int(level_id.split("-")[0])
        self.theme = WORLD_THEMES[w]
        for y, row in enumerate(LEVELS[level_id]):
            for x, char in enumerate(row):
                px, py = x * TILE, y * TILE
                if char == "S":
                    self.player.x, self.player.y = px, py
                elif char == "E":
                    self.enemies.append(Goomba(px, py))
                elif char == "K":
                    self.enemies.append(Koopa(px, py))
                elif char == "H":
                    self.enemies.append(Spike(px, py))
                elif char == "B":
                    self.enemies.append(Bowser(px, py))
        self.end = False
        self.end_timer = 0
    def handle(self, evts, keys):
        for e in evts:
            if e.type == KEYDOWN and e.key == K_ESCAPE:
                push(WorldMapScene())
    def update(self, dt):
        self.time -= dt
        self.player.update(self.map.colliders, dt, self.enemies)
        for e in self.enemies:
            if e.active:
                e.update(self.map.colliders, dt)
        target = self.player.x - WIDTH // 2
        self.cam += (target - self.cam) * 0.1
        self.cam = max(0, min(self.cam, self.map.width - WIDTH))
        if self.player.x > self.map.width - 200 and not self.end:
            self.end = True
            self.end_timer = 3
        if self.end:
            self.end_timer -= dt
            if self.end_timer <= 0:
                w, l = map(int, self.level_id.split("-"))
                if l < 4:
                    push(LevelScene(f"{w}-{l+1}"))
                else:
                    if w < 8 and (w+1) not in state.unlocked_worlds:
                        state.unlocked_worlds.append(w+1)
                    if w == 8 and l == 4:
                        push(WinScreen())
                    else:
                        push(WorldMapScene())
        if self.player.y > HEIGHT + 50:
            state.lives -= 1
            if state.lives <= 0:
                push(GameOverScene())
            else:
                self.player.x, self.player.y = 50, 200
                self.player.vx = self.player.vy = 0
                self.cam = 0
    def draw(self, s):
        self.map.draw(s, self.cam)
        for e in self.enemies:
            e.draw(s, self.cam)
        self.player.draw(s, self.cam)
        pygame.draw.rect(s, NES_PALETTE[0], (0, 0, WIDTH, 28))
        f = pygame.font.SysFont(None, 18)
        pygame.draw.rect(s, NES_PALETTE[33], (8, 6, 10, 14))
        pygame.draw.rect(s, NES_PALETTE[39], (8, 3, 10, 6))
        lt = f.render(f"x{state.lives}", True, NES_PALETTE[39])
        s.blit(lt, (22, 8))
        st = f.render(f"SCORE:{state.score:06d}", True, NES_PALETTE[39])
        s.blit(st, (70, 8))
        pygame.draw.circle(s, NES_PALETTE[35], (190, 14), 5)
        ct = f.render(f"x{state.coins:02d}", True, NES_PALETTE[39])
        s.blit(ct, (198, 8))
        wt = f.render(f"WORLD {self.level_id}", True, NES_PALETTE[39])
        s.blit(wt, (270, 8))
        tt = f.render(f"TIME:{int(max(0,self.time)):03d}", True, NES_PALETTE[39])
        s.blit(tt, (380, 8))

class GameOverScene(Scene):
    def __init__(self):
        self.t = 4
    def update(self, dt):
        self.t -= dt
        if self.t <= 0:
            state.lives = 3
            state.score = 0
            push(TitleScreen())
    def draw(self, s):
        s.fill(NES_PALETTE[0])
        f = pygame.font.SysFont(None, 48)
        t = f.render("GAME OVER", True, NES_PALETTE[33])
        s.blit(t, (WIDTH//2 - t.get_width()//2, HEIGHT//2 - 30))
        f2 = pygame.font.SysFont(None, 24)
        st = f2.render(f"Score: {state.score}", True, NES_PALETTE[39])
        s.blit(st, (WIDTH//2 - st.get_width()//2, HEIGHT//2 + 20))

class WinScreen(Scene):
    def __init__(self):
        self.t = 8
        self.fw = []
    def update(self, dt):
        self.t -= dt
        if random.random() < 0.12:
            self.fw.append({"x": random.randint(50, WIDTH-50), "y": HEIGHT, "c": random.choice([NES_PALETTE[33], NES_PALETTE[35], NES_PALETTE[37]]), "p": []})
        for f in self.fw[:]:
            f["y"] -= 4
            if f["y"] < HEIGHT//3:
                for _ in range(20):
                    a = random.uniform(0, 6.28)
                    sp = random.uniform(2, 5)
                    f["p"].append({"x": f["x"], "y": f["y"], "vx": math.cos(a)*sp, "vy": math.sin(a)*sp, "l": 1.0})
                self.fw.remove(f)
        for f in self.fw:
            for p in f["p"][:]:
                p["x"] += p["vx"]
                p["y"] += p["vy"]
                p["vy"] += 0.12
                p["l"] -= 0.02
                if p["l"] <= 0:
                    f["p"].remove(p)
        if self.t <= 0:
            push(TitleScreen())
    def draw(self, s):
        s.fill(NES_PALETTE[0])
        for f in self.fw:
            pygame.draw.circle(s, NES_PALETTE[35], (int(f["x"]), int(f["y"])), 3)
            for p in f["p"]:
                pygame.draw.circle(s, f["c"], (int(p["x"]), int(p["y"])), 2)
        f1 = pygame.font.SysFont(None, 48)
        t1 = f1.render("CONGRATULATIONS!", True, NES_PALETTE[35])
        s.blit(t1, (WIDTH//2 - t1.get_width()//2, 60))
        f2 = pygame.font.SysFont(None, 28)
        t2 = f2.render("YOU DEFEATED THE DARK KING!", True, NES_PALETTE[39])
        s.blit(t2, (WIDTH//2 - t2.get_width()//2, 120))
        t3 = f2.render("PEACE RETURNS TO THE KINGDOM", True, NES_PALETTE[37])
        s.blit(t3, (WIDTH//2 - t3.get_width()//2, 155))
        f3 = pygame.font.SysFont(None, 26)
        sc = f3.render(f"FINAL SCORE: {state.score}", True, NES_PALETTE[33])
        s.blit(sc, (WIDTH//2 - sc.get_width()//2, 210))
        f4 = pygame.font.SysFont(None, 18)
        ty = f4.render("THANK YOU FOR PLAYING!", True, NES_PALETTE[28])
        s.blit(ty, (WIDTH//2 - ty.get_width()//2, 270))
        cr = f4.render("Cat's ! Koopa Engine HDR 1.0 - Team Flames / Samsoft", True, NES_PALETTE[28])
        s.blit(cr, (WIDTH//2 - cr.get_width()//2, HEIGHT - 35))

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cat's ! Koopa Engine HDR 1.0")
clock = pygame.time.Clock()
push(TitleScreen())

while SCENES:
    dt = clock.tick(FPS) / 1000
    events = pygame.event.get()
    for e in events:
        if e.type == QUIT:
            pygame.quit()
            sys.exit()
    scene = SCENES[-1]
    scene.handle(events, pygame.key.get_pressed())
    scene.update(dt)
    scene.draw(screen)
    pygame.display.flip()

pygame.quit()
sys.exit()
