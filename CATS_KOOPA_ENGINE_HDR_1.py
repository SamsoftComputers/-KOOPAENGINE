import pygame
import sys
import math
import random
from pygame.locals import *

# Constants
SCALE = 2
TILE = 16
WIDTH = int(300 * SCALE)
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

def palette_nearest(color):
    return color

N = palette_nearest

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

# Scene management
SCENES = []
def push(scene): SCENES.append(scene)
def pop(): SCENES.pop()

class Scene:
    def handle(self, events, keys): ...
    def update(self, dt): ...
    def draw(self, surf): ...

# World themes
WORLD_THEMES = {
    1: {"sky": 27, "ground": 20, "pipe": 14, "block": 33, "water": None, "enemy": "E", "name": "GRASS LAND"},
    2: {"sky": 26, "ground": 21, "pipe": 15, "block": 34, "water": None, "enemy": "K", "name": "DESERT HILL"},
    3: {"sky": 25, "ground": 22, "pipe": 16, "block": 35, "water": 45, "enemy": "F", "name": "AQUA SEA"},
    4: {"sky": 24, "ground": 23, "pipe": 17, "block": 36, "water": None, "enemy": "E", "name": "GIANT FOREST"},
    5: {"sky": 23, "ground": 24, "pipe": 18, "block": 37, "water": None, "enemy": "H", "name": "SKY HEIGHTS"},
    6: {"sky": 22, "ground": 25, "pipe": 19, "block": 38, "water": None, "enemy": "E", "name": "ICE CAVERN"},
    7: {"sky": 21, "ground": 26, "pipe": 20, "block": 39, "water": None, "enemy": "H", "name": "LAVA CASTLE"},
    8: {"sky": 13, "ground": 0, "pipe": 14, "block": 0, "water": None, "enemy": "K", "name": "BOWSER'S CASTLE"}
}

# Tile Characters:
# '#' = Ground top
# '=' = Brick
# 'P' = Platform
# 'T' = Pipe top
# 't' = Pipe body
# '?' = Question block
# 'U' = Used block
# 'S' = Player start
# 'L' = Flag pole
# 'C' = Castle
# 'E' = Goomba enemy
# 'K' = Koopa enemy
# 'F' = Fish enemy
# 'H' = Spike hazard
# 'B' = Bowser
# 'X' = Axe
# 'b' = Bridge
# 'A' = Lava

# ACCURATE SMB1 World 1-1 Layout
LEVEL_1_1 = [
    "                                                                                                                                                                                                        ",
    "                                                                                                                                                                                                        ",
    "                                                                                                                                                                                                        ",
    "                                                                                                                                                                                                        ",
    "                                                                                                                                                                                                        ",
    "                                                                                                                                                                                                        ",
    "                                                                                                                                                                                                        ",
    "                                                                                                                                                                                                        ",
    "                    ?                                                      ?=?                                                                                                                          ",
    "                                                                                                                                      ==                                                                ",
    "                                                                                                                                     ===                                                                ",
    "                            =?=?=                                                                       ??                          ====                                                         C      ",
    "                                                                                                                                   =====                                                         C      ",
    "                                                                                                                                  ======                                                        CCC     ",
    "   S                                      TT              TT      TT              TT  TT                          TT  TT         =======                                                       CCCCC   L",
    "                    E          E         TttT     E      TttT    TttT     E      TttTTttT    E       E       E    TttTTttT  E    ========  E                                                   CCCCCCC   ",
    "####################################  ###TttT#########  #TttT####TttT###########TttTTttT#####################################  #########################################                    #############",
    "####################################  ###TttT#########  #TttT####TttT###########TttTTttT#####################################  #########################################                    #############",
    "####################################  ###TttT#########  #TttT####TttT###########TttTTttT#####################################  #########################################                    #############",
    "####################################  ###TttT#########  #TttT####TttT###########TttTTttT#####################################  #########################################                    #############",
]

# ACCURATE SMB1 World 8-4 Layout (Bowser's Castle)
LEVEL_8_4 = [
    "                                                                                                                                                                                                        ",
    "                                                                                                                                                                                                        ",
    "                                                                                                                                                                                                        ",
    "                                                                                                                                                                                                        ",
    "                                                                                                                                                                                                        ",
    "                                                                                                                                                                                                        ",
    "                                                                                                                                                                                                        ",
    "                                                                                                                                                                                                        ",
    "                                                                                                                                                                                                        ",
    "                                                                                                                                                                                                        ",
    "                                                                                                                                                                              bbbbbbbbbbbbbbbbbX        ",
    "                                                                                                                                                                              b              Bb        ",
    "                                                                                                                                                                              b              Bb        ",
    "   S                                                                                                                                                                          b               b        ",
    "                              H   H   H                                    H   H   H                                              H   H   H                                   b               b        ",
    "                    E    E              E    E                   E    E              E    E                             E    E              E                                  b               b        ",
    "####################################################################################################################################################                          bAAAAAAAAAAAAAAAAb        ",
    "####################################################################################################################################################                          bAAAAAAAAAAAAAAAAb        ",
    "####################################################################################################################################################                          bAAAAAAAAAAAAAAAAb        ",
    "####################################################################################################################################################                          bAAAAAAAAAAAAAAAAb        ",
]

def generate_level_data():
    levels = {}
    
    # World 1-1 is accurate
    levels["1-1"] = LEVEL_1_1
    
    # Generate other levels procedurally
    for world in range(1, 9):
        for level in range(1, 5):
            level_id = f"{world}-{level}"
            
            # Skip 1-1 (already set) and 8-4 (set below)
            if level_id == "1-1":
                continue
            if level_id == "8-4":
                levels["8-4"] = LEVEL_8_4
                continue
                
            theme = WORLD_THEMES[world]
            level_data = []
            
            # Sky rows
            for i in range(10):
                level_data.append(" " * 200)
            
            # Platform area
            for i in range(10, 16):
                level_data.append(" " * 200)
            
            # Ground
            for i in range(16, 20):
                if i == 16:
                    row = "#" * 200
                else:
                    row = "#" * 200
                level_data.append(row)
            
            # Add platforms
            for i in range(5 + level):
                platform_y = random.randint(8, 13)
                platform_x = random.randint(10 + i*20, 15 + i*20)
                length = random.randint(3, 6)
                for j in range(length):
                    if platform_x + j < 200:
                        level_data[platform_y] = level_data[platform_y][:platform_x+j] + "=" + level_data[platform_y][platform_x+j+1:]
            
            # Add pipes
            for i in range(2 + level//2):
                pipe_x = random.randint(20 + i*35, 30 + i*35)
                if pipe_x < 195:
                    pipe_height = random.randint(2, 4)
                    # Pipe top
                    level_data[15-pipe_height] = level_data[15-pipe_height][:pipe_x] + "TT" + level_data[15-pipe_height][pipe_x+2:]
                    # Pipe body
                    for j in range(pipe_height):
                        level_data[16-pipe_height+j] = level_data[16-pipe_height+j][:pipe_x] + "tt" + level_data[16-pipe_height+j][pipe_x+2:]
            
            # Add ? blocks and bricks
            for i in range(6 + level):
                block_y = random.randint(8, 12)
                block_x = random.randint(10 + i*15, 15 + i*15)
                if block_x < 200:
                    block_type = "?" if random.random() > 0.4 else "="
                    level_data[block_y] = level_data[block_y][:block_x] + block_type + level_data[block_y][block_x+1:]
            
            # Add player start
            level_data[15] = level_data[15][:3] + "S" + level_data[15][4:]
            
            # Add flag and castle at end
            level_data[15] = level_data[15][:190] + "L" + level_data[15][191:]
            level_data[11] = level_data[11][:194] + "C" + level_data[11][195:]
            level_data[12] = level_data[12][:194] + "C" + level_data[12][195:]
            level_data[13] = level_data[13][:193] + "CCC" + level_data[13][196:]
            level_data[14] = level_data[14][:192] + "CCCCC" + level_data[14][197:]
            level_data[15] = level_data[15][:191] + "CCCCCCC" + level_data[15][198:]
            
            # Add enemies
            for i in range(4 + level):
                enemy_y = 15
                enemy_x = random.randint(25 + i*18, 35 + i*18)
                if enemy_x < 185:
                    enemy_type = theme["enemy"]
                    level_data[enemy_y] = level_data[enemy_y][:enemy_x] + enemy_type + level_data[enemy_y][enemy_x+1:]
            
            levels[level_id] = level_data
    
    return levels

LEVELS = generate_level_data()

# Create thumbnails
THUMBNAILS = {}
for level_id, level_data in LEVELS.items():
    world = int(level_id.split("-")[0])
    theme = WORLD_THEMES[world]
    thumb = pygame.Surface((32, 24))
    thumb.fill(NES_PALETTE[theme["sky"]])
    for y, row in enumerate(level_data[10:18]):
        for x, char in enumerate(row[::6]):
            if char in ("#", "=", "P", "T", "t", "C"):
                thumb.set_at((x, y+8), NES_PALETTE[theme["ground"]])
            elif char == "?":
                thumb.set_at((x, y+8), NES_PALETTE[35])
    THUMBNAILS[level_id] = thumb

class Entity:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.width = TILE
        self.height = TILE
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
                elif self.vy < 0 and self.y < rect.bottom and self.y + self.height > rect.bottom:
                    self.y = rect.bottom
                    self.vy = 0
                if self.vx > 0 and self.x + self.width > rect.left and self.x < rect.left:
                    self.x = rect.left - self.width
                    self.vx = 0
                elif self.vx < 0 and self.x < rect.right and self.x + self.width > rect.right:
                    self.x = rect.right
                    self.vx = 0
    def draw(self, surf, cam):
        pass

class Player(Entity):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.jump_power = -6
        self.move_speed = 2.5
        self.run_speed = 4
        self.invincible = 0
        self.animation_frame = 0
        self.walk_timer = 0
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
            self.walk_timer += dt
            if self.walk_timer > 0.08:
                self.walk_timer = 0
                self.animation_frame = (self.animation_frame + 1) % 3
        else:
            self.animation_frame = 0
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
                            self.x = 50
                            self.y = 100
                            self.vx = 0
                            self.vy = 0
    def draw(self, surf, cam):
        if self.invincible > 0 and int(self.invincible * 10) % 2 == 0:
            return
        x = int(self.x - cam)
        y = int(self.y)
        if state.mario_size == "big":
            pygame.draw.rect(surf, NES_PALETTE[33], (x+4, y+8, 8, 16))
            pygame.draw.rect(surf, NES_PALETTE[39], (x+4, y+4, 8, 4))
            pygame.draw.rect(surf, NES_PALETTE[33], (x+2, y, 12, 4))
            arm_offset = 0
            if self.animation_frame == 1 and self.vx != 0:
                arm_offset = 2 if self.facing_right else -2
            pygame.draw.rect(surf, NES_PALETTE[39], (x+arm_offset, y+10, 4, 6))
            pygame.draw.rect(surf, NES_PALETTE[39], (x+12-arm_offset, y+10, 4, 6))
            leg_offset = 0
            if self.animation_frame == 2 and self.vx != 0:
                leg_offset = 2 if self.facing_right else -2
            pygame.draw.rect(surf, NES_PALETTE[21], (x+2, y+24, 4, 8))
            pygame.draw.rect(surf, NES_PALETTE[21], (x+10, y+24-leg_offset, 4, 8+leg_offset))
        else:
            pygame.draw.rect(surf, NES_PALETTE[33], (x+4, y+8, 8, 8))
            pygame.draw.rect(surf, NES_PALETTE[39], (x+4, y, 8, 8))
            pygame.draw.rect(surf, NES_PALETTE[33], (x+2, y, 12, 2))

class Goomba(Entity):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.vx = -0.5
        self.animation_frame = 0
        self.walk_timer = 0
    def update(self, colliders, dt):
        if self.on_ground:
            edge_check = pygame.Rect(self.x + (self.width if self.vx > 0 else -1), self.y + self.height, 1, 1)
            edge_found = False
            for rect in colliders:
                if edge_check.colliderect(rect):
                    edge_found = True
                    break
            if not edge_found:
                self.vx *= -1
        super().update(colliders, dt)
        self.walk_timer += dt
        if self.walk_timer > 0.2:
            self.walk_timer = 0
            self.animation_frame = (self.animation_frame + 1) % 2
    def draw(self, surf, cam):
        if not self.active:
            return
        x = int(self.x - cam)
        y = int(self.y)
        pygame.draw.ellipse(surf, NES_PALETTE[21], (x+2, y+4, 12, 12))
        foot_offset = 2 if self.animation_frame == 0 else -2
        pygame.draw.rect(surf, NES_PALETTE[21], (x+2, y+14, 4, 2))
        pygame.draw.rect(surf, NES_PALETTE[21], (x+10, y+14+foot_offset, 4, 2))
        eye_dir = 0 if self.vx > 0 else 2
        pygame.draw.rect(surf, NES_PALETTE[0], (x+4+eye_dir, y+6, 2, 2))
        pygame.draw.rect(surf, NES_PALETTE[0], (x+10-eye_dir, y+6, 2, 2))

class Koopa(Goomba):
    """Koopa Troopa enemy - the ONLY class using 'Koopa' naming"""
    def __init__(self, x, y):
        super().__init__(x, y)
        self.shell_mode = False
    def draw(self, surf, cam):
        if not self.active:
            return
        x = int(self.x - cam)
        y = int(self.y)
        pygame.draw.ellipse(surf, NES_PALETTE[14], (x+2, y+4, 12, 12))
        if not self.shell_mode:
            pygame.draw.rect(surf, NES_PALETTE[39], (x+4, y, 8, 4))
            pygame.draw.rect(surf, NES_PALETTE[14], (x+2, y+14, 4, 2))
            pygame.draw.rect(surf, NES_PALETTE[14], (x+10, y+14, 4, 2))

class Fish(Entity):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.vx = -0.5
        self.swim_timer = 0
    def update(self, colliders, dt):
        self.swim_timer += dt
        self.y += math.sin(self.swim_timer * 5) * 0.5
        super().update(colliders, dt)
    def draw(self, surf, cam):
        if not self.active:
            return
        x = int(self.x - cam)
        y = int(self.y)
        pygame.draw.ellipse(surf, NES_PALETTE[31], (x, y, 16, 8))
        pygame.draw.polygon(surf, NES_PALETTE[31], [(x, y+4), (x-5, y), (x-5, y+8)])
        pygame.draw.circle(surf, NES_PALETTE[0], (x+12, y+4), 2)

class Spike(Entity):
    def __init__(self, x, y):
        super().__init__(x, y)
    def update(self, colliders, dt):
        pass
    def draw(self, surf, cam):
        if not self.active:
            return
        x = int(self.x - cam)
        y = int(self.y)
        # Fire bar style
        pygame.draw.rect(surf, NES_PALETTE[22], (x+2, y+2, 12, 12))
        pygame.draw.rect(surf, NES_PALETTE[33], (x+4, y+4, 8, 8))
        pygame.draw.rect(surf, NES_PALETTE[35], (x+6, y+6, 4, 4))

class Bowser(Entity):
    """Final boss"""
    def __init__(self, x, y):
        super().__init__(x, y)
        self.width = TILE * 2
        self.height = TILE * 2
        self.vx = -0.3
        self.fire_timer = 0
    def update(self, colliders, dt):
        self.fire_timer += dt
        super().update(colliders, dt)
    def draw(self, surf, cam):
        if not self.active:
            return
        x = int(self.x - cam)
        y = int(self.y)
        # Bowser body
        pygame.draw.rect(surf, NES_PALETTE[14], (x, y, 32, 32))
        pygame.draw.rect(surf, NES_PALETTE[35], (x+4, y+4, 24, 20))
        # Head
        pygame.draw.rect(surf, NES_PALETTE[14], (x+20, y-8, 16, 16))
        # Eyes
        pygame.draw.rect(surf, NES_PALETTE[39], (x+24, y-4, 4, 4))
        pygame.draw.rect(surf, NES_PALETTE[33], (x+30, y-4, 4, 4))
        # Spikes
        for i in range(3):
            pygame.draw.polygon(surf, NES_PALETTE[39], [
                (x+8+i*8, y), (x+4+i*8, y-8), (x+12+i*8, y-8)
            ])

class TileMap:
    def __init__(self, level_data, level_id):
        self.tiles = []
        self.colliders = []
        self.width = len(level_data[0]) * TILE
        self.height = len(level_data) * TILE
        self.level_id = level_id
        world = int(level_id.split("-")[0])
        self.theme = WORLD_THEMES[world]
        for y, row in enumerate(level_data):
            for x, char in enumerate(row):
                if char != " ":
                    rect = pygame.Rect(x * TILE, y * TILE, TILE, TILE)
                    self.tiles.append((x * TILE, y * TILE, char))
                    if char in ("#", "=", "P", "T", "t", "?", "U", "C", "b"):
                        self.colliders.append(rect)
    def draw(self, surf, cam):
        surf.fill(NES_PALETTE[self.theme["sky"]])
        # Clouds
        for i in range(15):
            x = (i * 120 - int(cam/4)) % (self.width + 300) - 100
            y = 40 + (i % 3) * 30
            pygame.draw.ellipse(surf, NES_PALETTE[31], (x, y, 40, 20))
            pygame.draw.ellipse(surf, NES_PALETTE[31], (x+20, y-8, 35, 20))
            pygame.draw.ellipse(surf, NES_PALETTE[31], (x+40, y, 30, 18))
        # Hills
        for i in range(8):
            hx = (i * 200 - int(cam/6)) % (self.width + 400) - 100
            pygame.draw.ellipse(surf, NES_PALETTE[14], (hx, HEIGHT-120, 100, 60))
            pygame.draw.ellipse(surf, NES_PALETTE[14], (hx+60, HEIGHT-100, 60, 40))
        # Bushes
        for i in range(10):
            bx = (i * 150 - int(cam/5)) % (self.width + 300) - 50
            pygame.draw.ellipse(surf, NES_PALETTE[14], (bx, HEIGHT-75, 30, 15))
            pygame.draw.ellipse(surf, NES_PALETTE[14], (bx+15, HEIGHT-80, 25, 18))
            pygame.draw.ellipse(surf, NES_PALETTE[14], (bx+30, HEIGHT-75, 28, 14))
        
        for x, y, char in self.tiles:
            draw_x = x - cam
            if draw_x < -TILE or draw_x > WIDTH + TILE:
                continue
            if char == "#":
                # Ground
                pygame.draw.rect(surf, NES_PALETTE[22], (draw_x, y, TILE, TILE))
                pygame.draw.rect(surf, NES_PALETTE[21], (draw_x+2, y+2, TILE-4, TILE-4))
            elif char == "=":
                # Brick
                pygame.draw.rect(surf, NES_PALETTE[22], (draw_x, y, TILE, TILE))
                pygame.draw.rect(surf, NES_PALETTE[21], (draw_x+1, y+1, 6, 6))
                pygame.draw.rect(surf, NES_PALETTE[21], (draw_x+9, y+1, 6, 6))
                pygame.draw.rect(surf, NES_PALETTE[21], (draw_x+1, y+9, 6, 6))
                pygame.draw.rect(surf, NES_PALETTE[21], (draw_x+9, y+9, 6, 6))
            elif char == "?":
                # Question block
                pygame.draw.rect(surf, NES_PALETTE[35], (draw_x, y, TILE, TILE))
                pygame.draw.rect(surf, NES_PALETTE[33], (draw_x+2, y+2, TILE-4, TILE-4))
                pygame.draw.rect(surf, NES_PALETTE[39], (draw_x+5, y+4, 6, 3))
                pygame.draw.rect(surf, NES_PALETTE[39], (draw_x+8, y+7, 3, 3))
                pygame.draw.rect(surf, NES_PALETTE[39], (draw_x+6, y+10, 4, 2))
            elif char == "U":
                # Used block
                pygame.draw.rect(surf, NES_PALETTE[21], (draw_x, y, TILE, TILE))
                pygame.draw.rect(surf, NES_PALETTE[0], (draw_x+2, y+2, TILE-4, TILE-4))
            elif char == "T":
                # Pipe top
                pygame.draw.rect(surf, NES_PALETTE[14], (draw_x-2, y, TILE+4, TILE))
                pygame.draw.rect(surf, NES_PALETTE[37], (draw_x, y+2, 4, TILE-2))
                pygame.draw.rect(surf, NES_PALETTE[0], (draw_x+TILE-2, y+2, 2, TILE-2))
            elif char == "t":
                # Pipe body
                pygame.draw.rect(surf, NES_PALETTE[14], (draw_x, y, TILE, TILE))
                pygame.draw.rect(surf, NES_PALETTE[37], (draw_x+2, y, 4, TILE))
                pygame.draw.rect(surf, NES_PALETTE[0], (draw_x+TILE-2, y, 2, TILE))
            elif char == "L":
                # Flag pole
                pygame.draw.rect(surf, NES_PALETTE[14], (draw_x+6, y, 4, TILE*6))
                pygame.draw.rect(surf, NES_PALETTE[37], (draw_x+7, y, 2, TILE*6))
                # Flag
                pygame.draw.polygon(surf, NES_PALETTE[14], [
                    (draw_x+10, y+8), (draw_x+26, y+16), (draw_x+10, y+24)
                ])
                # Ball on top
                pygame.draw.circle(surf, NES_PALETTE[14], (draw_x+8, y-4), 6)
            elif char == "C":
                # Castle
                pygame.draw.rect(surf, NES_PALETTE[0], (draw_x, y, TILE, TILE))
                pygame.draw.rect(surf, NES_PALETTE[28], (draw_x+2, y+2, TILE-4, TILE-4))
            elif char == "b":
                # Bridge
                pygame.draw.rect(surf, NES_PALETTE[22], (draw_x, y, TILE, 8))
                pygame.draw.rect(surf, NES_PALETTE[21], (draw_x+2, y+2, TILE-4, 4))
            elif char == "A":
                # Lava
                pygame.draw.rect(surf, NES_PALETTE[22], (draw_x, y, TILE, TILE))
                pygame.draw.rect(surf, NES_PALETTE[33], (draw_x+2, y+2, TILE-4, TILE-4))
                # Animated bubbles
                bubble_y = y + 4 + int(math.sin(pygame.time.get_ticks()/200 + x) * 3)
                pygame.draw.circle(surf, NES_PALETTE[35], (draw_x+8, bubble_y), 3)
            elif char == "X":
                # Axe
                pygame.draw.rect(surf, NES_PALETTE[35], (draw_x+4, y+2, 8, 12))
                pygame.draw.rect(surf, NES_PALETTE[33], (draw_x+6, y+4, 4, 8))
                pygame.draw.polygon(surf, NES_PALETTE[28], [
                    (draw_x+2, y+4), (draw_x+6, y+2), (draw_x+6, y+10), (draw_x+2, y+8)
                ])

class TitleScreen(Scene):
    def __init__(self):
        self.timer = 0
        self.animation_frame = 0
        self.logo_y = -80
        self.logo_target_y = 40
        self.stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT//2), random.random()) for _ in range(50)]
    def handle(self, events, keys):
        for e in events:
            if e.type == KEYDOWN and e.key == K_RETURN:
                push(FileSelect())
    def update(self, dt):
        self.timer += dt
        if self.timer > 0.1:
            self.timer = 0
            self.animation_frame = (self.animation_frame + 1) % 4
        if self.logo_y < self.logo_target_y:
            self.logo_y += 2
        # Animate stars
        for i, (sx, sy, sp) in enumerate(self.stars):
            self.stars[i] = (sx, (sy + sp) % (HEIGHT//2), sp)
    def draw(self, surf):
        # Dark blue gradient background
        surf.fill(NES_PALETTE[1])
        
        # Stars
        for sx, sy, sp in self.stars:
            brightness = 31 if sp > 0.5 else 28
            pygame.draw.rect(surf, NES_PALETTE[brightness], (sx, sy, 2, 2))
        
        # Main logo box
        box_width, box_height = 280, 140
        box_x = (WIDTH - box_width) // 2
        box_y = self.logo_y
        
        # Shadow
        pygame.draw.rect(surf, NES_PALETTE[0], (box_x+4, box_y+4, box_width, box_height))
        # Main box
        pygame.draw.rect(surf, NES_PALETTE[33], (box_x, box_y, box_width, box_height))
        pygame.draw.rect(surf, NES_PALETTE[35], (box_x+4, box_y+4, box_width-8, box_height-8))
        pygame.draw.rect(surf, NES_PALETTE[33], (box_x+8, box_y+8, box_width-16, box_height-16))
        
        # "Cat's !" text
        cat_font = pygame.font.SysFont(None, 28)
        cat_text = cat_font.render("Cat's !", True, NES_PALETTE[39])
        surf.blit(cat_text, (box_x + 20, box_y + 15))
        
        # Main title
        title_font = pygame.font.SysFont(None, 36)
        title = title_font.render("KOOPA ENGINE", True, NES_PALETTE[39])
        surf.blit(title, (box_x + (box_width - title.get_width()) // 2, box_y + 45))
        
        # HDR 1.0
        hdr_font = pygame.font.SysFont(None, 32)
        hdr = hdr_font.render("HDR 1.0", True, NES_PALETTE[35])
        surf.blit(hdr, (box_x + (box_width - hdr.get_width()) // 2, box_y + 80))
        
        # Subtitle
        sub_font = pygame.font.SysFont(None, 16)
        sub = sub_font.render("~ 8 Worlds Adventure ~", True, NES_PALETTE[21])
        surf.blit(sub, (box_x + (box_width - sub.get_width()) // 2, box_y + 110))
        
        # Copyright
        copy_font = pygame.font.SysFont(None, 14)
        copy1 = copy_font.render("[C] 2024 Team Flames / Samsoft", True, NES_PALETTE[28])
        surf.blit(copy1, (WIDTH//2 - copy1.get_width()//2, box_y + box_height + 15))
        copy2 = copy_font.render("Licensed by Nintendo", True, NES_PALETTE[28])
        surf.blit(copy2, (WIDTH//2 - copy2.get_width()//2, box_y + box_height + 30))
        
        # Characters at bottom
        ground_y = HEIGHT - 60
        
        # Ground
        for i in range(WIDTH // TILE + 1):
            pygame.draw.rect(surf, NES_PALETTE[22], (i*TILE, ground_y, TILE, 60))
            pygame.draw.rect(surf, NES_PALETTE[21], (i*TILE+2, ground_y+2, TILE-4, 56))
        
        # Mario
        mario_x = WIDTH//2 - 80
        mario_y = ground_y - 24
        pygame.draw.rect(surf, NES_PALETTE[33], (mario_x+4, mario_y+8, 8, 16))
        pygame.draw.rect(surf, NES_PALETTE[39], (mario_x+4, mario_y+4, 8, 4))
        pygame.draw.rect(surf, NES_PALETTE[33], (mario_x+2, mario_y, 12, 4))
        pygame.draw.rect(surf, NES_PALETTE[39], (mario_x, mario_y+10, 4, 6))
        pygame.draw.rect(surf, NES_PALETTE[39], (mario_x+12, mario_y+10, 4, 6))
        pygame.draw.rect(surf, NES_PALETTE[21], (mario_x+2, mario_y+24, 4, 8))
        pygame.draw.rect(surf, NES_PALETTE[21], (mario_x+10, mario_y+24, 4, 8))
        
        # Goomba
        goomba_x = WIDTH//2 + 20
        goomba_y = ground_y - 16
        pygame.draw.ellipse(surf, NES_PALETTE[21], (goomba_x+2, goomba_y+4, 12, 12))
        pygame.draw.rect(surf, NES_PALETTE[21], (goomba_x+2, goomba_y+14, 4, 2))
        pygame.draw.rect(surf, NES_PALETTE[21], (goomba_x+10, goomba_y+14, 4, 2))
        pygame.draw.rect(surf, NES_PALETTE[0], (goomba_x+4, goomba_y+6, 2, 2))
        pygame.draw.rect(surf, NES_PALETTE[0], (goomba_x+10, goomba_y+6, 2, 2))
        
        # Koopa (the actual Koopa enemy)
        turtle_x = WIDTH//2 + 60
        turtle_y = ground_y - 16
        pygame.draw.ellipse(surf, NES_PALETTE[14], (turtle_x+2, turtle_y+4, 12, 12))
        pygame.draw.rect(surf, NES_PALETTE[39], (turtle_x+4, turtle_y, 8, 4))
        pygame.draw.rect(surf, NES_PALETTE[14], (turtle_x+2, turtle_y+14, 4, 2))
        pygame.draw.rect(surf, NES_PALETTE[14], (turtle_x+10, turtle_y+14, 4, 2))
        
        # Press Enter
        if self.logo_y >= self.logo_target_y:
            if int(self.timer * 10) % 2 == 0:
                font = pygame.font.SysFont(None, 24)
                text = font.render("PRESS ENTER TO START", True, NES_PALETTE[39])
                surf.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT - 30))

class FileSelect(Scene):
    def __init__(self):
        self.offset = 0
        self.selected = 0
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
        self.offset += dt
    def draw(self, s):
        s.fill(NES_PALETTE[0])
        font = pygame.font.SysFont(None, 36)
        title = font.render("SELECT FILE", True, NES_PALETTE[39])
        s.blit(title, (WIDTH//2 - title.get_width()//2, 30))
        for i in range(3):
            x = 60 + i * 150
            y = 120 + 8 * math.sin(self.offset * 2 + i)
            # File box
            pygame.draw.rect(s, NES_PALETTE[21], (x-5, y-5, 100, 140))
            pygame.draw.rect(s, NES_PALETTE[22], (x, y, 90, 130))
            if i == self.selected:
                pygame.draw.rect(s, NES_PALETTE[35], (x-8, y-8, 106, 146), 3)
            # File number
            slot_font = pygame.font.SysFont(None, 28)
            slot_text = slot_font.render(f"FILE {i+1}", True, NES_PALETTE[39])
            s.blit(slot_text, (x + 45 - slot_text.get_width()//2, y+10))
            # Mario icon
            pygame.draw.rect(s, NES_PALETTE[33], (x+38, y+40, 14, 20))
            pygame.draw.rect(s, NES_PALETTE[39], (x+38, y+35, 14, 8))
            # World progress
            if state.progress[i]:
                world = state.progress[i]["world"]
                world_font = pygame.font.SysFont(None, 20)
                world_text = world_font.render(f"WORLD {world}", True, NES_PALETTE[39])
                s.blit(world_text, (x+45 - world_text.get_width()//2, y+70))
                thumb = THUMBNAILS.get(f"{world}-1", THUMBNAILS["1-1"])
                scaled_thumb = pygame.transform.scale(thumb, (64, 48))
                s.blit(scaled_thumb, (x+13, y+85))
        # Instructions
        inst_font = pygame.font.SysFont(None, 18)
        inst = inst_font.render("LEFT/RIGHT: Select   ENTER: Start   ESC: Back", True, NES_PALETTE[28])
        s.blit(inst, (WIDTH//2 - inst.get_width()//2, HEIGHT - 40))

class WorldMapScene(Scene):
    def __init__(self):
        self.selection = state.world
        self.cursor_timer = 0
    def handle(self, evts, keys):
        for e in evts:
            if e.type == KEYDOWN:
                if e.key == K_LEFT and self.selection > 1:
                    self.selection -= 1
                elif e.key == K_RIGHT and self.selection < 8:
                    self.selection += 1
                elif e.key == K_UP and self.selection > 4:
                    self.selection -= 4
                elif e.key == K_DOWN and self.selection < 5:
                    self.selection += 4
                elif e.key == K_RETURN:
                    if self.selection <= max(state.unlocked_worlds):
                        state.world = self.selection
                        state.progress[state.slot]["world"] = self.selection
                        push(LevelScene(f"{state.world}-1"))
                elif e.key == K_ESCAPE:
                    push(FileSelect())
    def update(self, dt):
        self.cursor_timer += dt
    def draw(self, s):
        s.fill(NES_PALETTE[1])
        font = pygame.font.SysFont(None, 36)
        title = font.render("WORLD SELECT", True, NES_PALETTE[39])
        s.blit(title, (WIDTH//2 - title.get_width()//2, 20))
        world_size = 60
        for world in range(1, 9):
            row = (world - 1) // 4
            col = (world - 1) % 4
            x = 45 + col * 100
            y = 80 + row * 100
            theme = WORLD_THEMES[world]
            if world in state.unlocked_worlds:
                pygame.draw.rect(s, NES_PALETTE[theme["ground"]], (x, y, world_size, world_size))
                pygame.draw.rect(s, NES_PALETTE[theme["sky"]], (x+5, y+5, world_size-10, world_size-10))
                # World number
                w_font = pygame.font.SysFont(None, 32)
                w_text = w_font.render(f"{world}", True, NES_PALETTE[39])
                s.blit(w_text, (x + world_size//2 - w_text.get_width()//2, y + world_size//2 - w_text.get_height()//2))
            else:
                pygame.draw.rect(s, NES_PALETTE[0], (x, y, world_size, world_size))
                pygame.draw.rect(s, NES_PALETTE[28], (x+5, y+5, world_size-10, world_size-10))
                pygame.draw.line(s, NES_PALETTE[33], (x, y), (x+world_size, y+world_size), 3)
                pygame.draw.line(s, NES_PALETTE[33], (x+world_size, y), (x, y+world_size), 3)
            if world == self.selection:
                name_font = pygame.font.SysFont(None, 20)
                name_text = name_font.render(theme["name"], True, NES_PALETTE[35])
                s.blit(name_text, (WIDTH//2 - name_text.get_width()//2, HEIGHT - 60))
        # Cursor
        row = (self.selection - 1) // 4
        col = (self.selection - 1) % 4
        x = 45 + col * 100
        y = 80 + row * 100
        cursor_offset = math.sin(self.cursor_timer * 6) * 4
        pygame.draw.rect(s, NES_PALETTE[35], (x-6, y-6+cursor_offset, world_size+12, 6))
        pygame.draw.rect(s, NES_PALETTE[35], (x-6, y+world_size+cursor_offset, world_size+12, 6))
        # Mario on cursor
        mario_x = x + world_size//2 - 8
        mario_y = y - 35 + cursor_offset
        pygame.draw.rect(s, NES_PALETTE[33], (mario_x+4, mario_y+8, 8, 8))
        pygame.draw.rect(s, NES_PALETTE[39], (mario_x+4, mario_y, 8, 8))
        # Instructions
        font = pygame.font.SysFont(None, 16)
        text = font.render("Arrows: Move   ENTER: Play   ESC: Back", True, NES_PALETTE[28])
        s.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT - 25))
        unlocked = font.render(f"Progress: World {max(state.unlocked_worlds)}/8", True, NES_PALETTE[28])
        s.blit(unlocked, (10, HEIGHT - 25))

class LevelScene(Scene):
    def __init__(self, level_id):
        self.map = TileMap(LEVELS[level_id], level_id)
        self.player = Player(50, 200)
        self.enemies = []
        self.cam = 0.0
        self.level_id = level_id
        self.time = 400
        self.coins = 0
        self.end_level = False
        self.end_timer = 0
        world = int(level_id.split("-")[0])
        self.theme = WORLD_THEMES[world]
        for y, row in enumerate(LEVELS[level_id]):
            for x, char in enumerate(row):
                if char == "S":
                    self.player.x = x * TILE
                    self.player.y = y * TILE
                elif char == "E":
                    self.enemies.append(Goomba(x * TILE, y * TILE))
                elif char == "K":
                    self.enemies.append(Koopa(x * TILE, y * TILE))
                elif char == "F":
                    self.enemies.append(Fish(x * TILE, y * TILE))
                elif char == "H":
                    self.enemies.append(Spike(x * TILE, y * TILE))
                elif char == "B":
                    self.enemies.append(Bowser(x * TILE, y * TILE))
    def handle(self, evts, keys):
        for e in evts:
            if e.type == KEYDOWN and e.key == K_ESCAPE:
                push(WorldMapScene())
    def update(self, dt):
        self.time -= dt
        self.player.update(self.map.colliders, dt, self.enemies)
        for enemy in self.enemies:
            if enemy.active:
                enemy.update(self.map.colliders, dt)
        target = self.player.x - WIDTH // 2
        self.cam += (target - self.cam) * 0.1
        self.cam = max(0, min(self.cam, self.map.width - WIDTH))
        if self.player.x > self.map.width - 150 and not self.end_level:
            self.end_level = True
            self.end_timer = 3
        if self.end_level:
            self.end_timer -= dt
            if self.end_timer <= 0:
                world, level = self.level_id.split("-")
                world = int(world)
                level = int(level)
                if level < 4:
                    next_level = f"{world}-{level+1}"
                    push(LevelScene(next_level))
                else:
                    if world < 8 and (world + 1) not in state.unlocked_worlds:
                        state.unlocked_worlds.append(world + 1)
                    if world == 8 and level == 4:
                        push(WinScreen())
                    else:
                        push(WorldMapScene())
        # Fall death
        if self.player.y > HEIGHT + 50:
            state.lives -= 1
            if state.lives <= 0:
                push(GameOverScene())
            else:
                self.player.x = 50
                self.player.y = 200
                self.player.vx = 0
                self.player.vy = 0
                self.cam = 0
    def draw(self, s):
        self.map.draw(s, self.cam)
        for enemy in self.enemies:
            enemy.draw(s, self.cam)
        self.player.draw(s, self.cam)
        # HUD
        pygame.draw.rect(s, NES_PALETTE[0], (0, 0, WIDTH, 32))
        font = pygame.font.SysFont(None, 20)
        # Mario
        pygame.draw.rect(s, NES_PALETTE[33], (10, 8, 10, 14))
        pygame.draw.rect(s, NES_PALETTE[39], (10, 4, 10, 6))
        lives_text = font.render(f"x {state.lives}", True, NES_PALETTE[39])
        s.blit(lives_text, (25, 10))
        # Score
        score_text = font.render(f"SCORE: {state.score:06d}", True, NES_PALETTE[39])
        s.blit(score_text, (80, 10))
        # Coins
        pygame.draw.circle(s, NES_PALETTE[35], (210, 16), 6)
        coin_text = font.render(f"x {state.coins:02d}", True, NES_PALETTE[39])
        s.blit(coin_text, (220, 10))
        # World
        world_text = font.render(f"WORLD {self.level_id}", True, NES_PALETTE[39])
        s.blit(world_text, (300, 10))
        # Time
        time_text = font.render(f"TIME: {int(max(0, self.time)):03d}", True, NES_PALETTE[39])
        s.blit(time_text, (420, 10))
        # Level name
        name_font = pygame.font.SysFont(None, 16)
        name_text = name_font.render(self.theme["name"], True, NES_PALETTE[28])
        s.blit(name_text, (WIDTH - name_text.get_width() - 10, 10))

class GameOverScene(Scene):
    def __init__(self):
        self.timer = 4
    def update(self, dt):
        self.timer -= dt
        if self.timer <= 0:
            state.lives = 3
            state.score = 0
            push(TitleScreen())
    def draw(self, s):
        s.fill(NES_PALETTE[0])
        font = pygame.font.SysFont(None, 48)
        text = font.render("GAME OVER", True, NES_PALETTE[33])
        s.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 40))
        font2 = pygame.font.SysFont(None, 24)
        score_text = font2.render(f"Final Score: {state.score}", True, NES_PALETTE[39])
        s.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2 + 20))

class WinScreen(Scene):
    def __init__(self):
        self.timer = 8
        self.fireworks = []
    def update(self, dt):
        self.timer -= dt
        if random.random() < 0.15:
            self.fireworks.append({
                "x": random.randint(50, WIDTH-50),
                "y": HEIGHT,
                "color": random.choice([NES_PALETTE[33], NES_PALETTE[35], NES_PALETTE[31], NES_PALETTE[37]]),
                "particles": []
            })
        for fw in self.fireworks[:]:
            fw["y"] -= 4
            if fw["y"] < HEIGHT//3:
                for i in range(25):
                    angle = random.uniform(0, math.pi*2)
                    speed = random.uniform(2, 6)
                    fw["particles"].append({
                        "x": fw["x"], "y": fw["y"],
                        "vx": math.cos(angle) * speed,
                        "vy": math.sin(angle) * speed,
                        "life": 1.0
                    })
                self.fireworks.remove(fw)
        for fw in self.fireworks:
            for p in fw["particles"][:]:
                p["x"] += p["vx"]
                p["y"] += p["vy"]
                p["vy"] += 0.15
                p["life"] -= 0.02
                if p["life"] <= 0:
                    fw["particles"].remove(p)
        if self.timer <= 0:
            push(TitleScreen())
    def draw(self, s):
        s.fill(NES_PALETTE[0])
        for fw in self.fireworks:
            pygame.draw.circle(s, NES_PALETTE[35], (int(fw["x"]), int(fw["y"])), 4)
            for p in fw["particles"]:
                pygame.draw.circle(s, fw["color"], (int(p["x"]), int(p["y"])), 3)
        font = pygame.font.SysFont(None, 48)
        text = font.render("CONGRATULATIONS!", True, NES_PALETTE[35])
        s.blit(text, (WIDTH//2 - text.get_width()//2, 60))
        font2 = pygame.font.SysFont(None, 32)
        text2 = font2.render("YOU DEFEATED BOWSER!", True, NES_PALETTE[39])
        s.blit(text2, (WIDTH//2 - text2.get_width()//2, 120))
        text3 = font2.render("PEACE RETURNS TO THE MUSHROOM KINGDOM", True, NES_PALETTE[37])
        s.blit(text3, (WIDTH//2 - text3.get_width()//2, 160))
        font3 = pygame.font.SysFont(None, 28)
        score = font3.render(f"FINAL SCORE: {state.score}", True, NES_PALETTE[33])
        s.blit(score, (WIDTH//2 - score.get_width()//2, 220))
        # Thank you message
        thanks = pygame.font.SysFont(None, 20)
        ty = thanks.render("THANK YOU FOR PLAYING!", True, NES_PALETTE[28])
        s.blit(ty, (WIDTH//2 - ty.get_width()//2, 280))
        # Credits
        cred = thanks.render("Cat's ! Koopa Engine HDR 1.0 - Team Flames / Samsoft", True, NES_PALETTE[28])
        s.blit(cred, (WIDTH//2 - cred.get_width()//2, HEIGHT - 40))

# Main
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
