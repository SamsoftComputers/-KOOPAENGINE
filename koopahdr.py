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

# SMB1 Authentic Colors
SKY_BLUE = (92, 148, 252)
BRICK_DARK = (136, 56, 0)
BRICK_LIGHT = (200, 76, 12)
BRICK_LINE = (60, 24, 0)
GROUND_DARK = (136, 56, 0)
GROUND_LIGHT = (252, 152, 56)
BLOCK_DARK = (136, 56, 0)
BLOCK_LIGHT = (252, 152, 56)
BLOCK_SHADOW = (60, 24, 0)
QBLOCK_ORANGE = (252, 152, 56)
QBLOCK_DARK = (136, 56, 0)
PIPE_GREEN = (0, 168, 0)
PIPE_LIGHT = (128, 208, 16)
PIPE_DARK = (0, 88, 0)
MARIO_RED = (200, 76, 12)
MARIO_SKIN = (252, 152, 56)
MARIO_BROWN = (136, 56, 0)
GOOMBA_BROWN = (136, 56, 0)
GOOMBA_TAN = (228, 148, 88)
TURTLE_GREEN = (0, 168, 0)
TURTLE_LIGHT = (128, 208, 16)
WHITE = (252, 252, 252)
BLACK = (0, 0, 0)
FLAGPOLE_GREEN = (0, 168, 0)

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
        self.power = 0  # 0=small, 1=big, 2=fire
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

# World themes - SMB1 style
WORLD_THEMES = {
    1: {"sky": SKY_BLUE, "name": "WORLD 1-1"},
    2: {"sky": SKY_BLUE, "name": "WORLD 1-2"},
    3: {"sky": SKY_BLUE, "name": "WORLD 1-3"},
    4: {"sky": BLACK, "name": "WORLD 1-4"},
    5: {"sky": SKY_BLUE, "name": "WORLD 2-1"},
    6: {"sky": SKY_BLUE, "name": "WORLD 2-2"},
    7: {"sky": SKY_BLUE, "name": "WORLD 2-3"},
    8: {"sky": BLACK, "name": "WORLD 2-4"}
}

# SMB1 1-1 Style Level Generation
def generate_level_data():
    levels = {}
    for world in range(1, 9):
        for level in range(1, 5):
            level_id = f"{world}-{level}"
            
            # 15 rows tall, 212 columns wide (like SMB1 1-1)
            level_data = []
            
            # Sky area (rows 0-12)
            for i in range(13):
                level_data.append(" " * 212)
            
            # Ground (rows 13-14) - 2 tiles tall like SMB1
            level_data.append("G" * 212)  # Ground top
            level_data.append("D" * 212)  # Ground dirt/fill
            
            # Create gaps in ground
            gaps = [(69, 71), (86, 88), (153, 155)]
            for gap_start, gap_end in gaps:
                for row in [13, 14]:
                    level_data[row] = level_data[row][:gap_start] + " " * (gap_end - gap_start) + level_data[row][gap_end:]
            
            # Add pipes (SMB1 style - varying heights)
            pipe_positions = [(28, 2), (38, 3), (46, 4), (57, 4), (163, 2), (179, 2)]
            for pipe_x, pipe_height in pipe_positions:
                for h in range(pipe_height):
                    y = 12 - h
                    if h == pipe_height - 1:
                        # Pipe top
                        level_data[y] = level_data[y][:pipe_x] + "T" + level_data[y][pipe_x+1:]
                        level_data[y] = level_data[y][:pipe_x+1] + "t" + level_data[y][pipe_x+2:]
                    else:
                        # Pipe body
                        level_data[y] = level_data[y][:pipe_x] + "P" + level_data[y][pipe_x+1:]
                        level_data[y] = level_data[y][:pipe_x+1] + "p" + level_data[y][pipe_x+2:]
            
            # Add brick blocks (SMB1 patterns)
            brick_rows = [
                (20, 9, "?B?"),      # First ? block cluster
                (23, 9, "B"),
                (77, 9, "B?B"),
                (80, 5, "B?B?B?B?B"),
                (91, 9, "BBB"),
                (94, 5, "BBB"),
                (100, 9, "?"),
                (106, 9, "BB"),
                (109, 5, "BBB"),
                (118, 9, "B?B"),
                (128, 9, "BB"),
                (129, 5, "BBB"),
                (168, 9, "BB"),
            ]
            for bx, by, pattern in brick_rows:
                for i, char in enumerate(pattern):
                    if bx + i < 212:
                        level_data[by] = level_data[by][:bx+i] + char + level_data[by][bx+i+1:]
            
            # Add stairs (end of level)
            stair_x = 181
            for step in range(8):
                for h in range(step + 1):
                    y = 12 - h
                    x = stair_x + step
                    if x < 212 and y >= 0:
                        level_data[y] = level_data[y][:x] + "S" + level_data[y][x+1:]
            
            # Flagpole
            flag_x = 198
            for h in range(10):
                y = 3 + h
                level_data[y] = level_data[y][:flag_x] + "F" + level_data[y][flag_x+1:]
            
            # Castle
            castle_x = 202
            # Castle base
            for cx in range(6):
                level_data[11] = level_data[11][:castle_x+cx] + "C" + level_data[11][castle_x+cx+1:]
                level_data[12] = level_data[12][:castle_x+cx] + "C" + level_data[12][castle_x+cx+1:]
            # Castle top
            for cx in range(4):
                level_data[9] = level_data[9][:castle_x+1+cx] + "C" + level_data[9][castle_x+1+cx+1:]
                level_data[10] = level_data[10][:castle_x+1+cx] + "C" + level_data[10][castle_x+1+cx+1:]
            # Castle door
            level_data[11] = level_data[11][:castle_x+2] + "c" + level_data[11][castle_x+3:]
            level_data[12] = level_data[12][:castle_x+2] + "c" + level_data[12][castle_x+3:]
            
            # Player start
            level_data[12] = level_data[12][:3] + "M" + level_data[12][4:]
            
            # Add enemies (Goombas and Koopas)
            enemy_positions = [
                (22, 12, "E"),   # Goomba
                (40, 12, "E"),
                (51, 12, "E"),
                (52, 12, "E"),
                (80, 4, "E"),
                (82, 4, "E"),
                (97, 12, "K"),   # Koopa
                (114, 12, "E"),
                (115, 12, "E"),
                (124, 12, "E"),
                (125, 12, "E"),
                (128, 4, "E"),
                (130, 4, "E"),
                (174, 12, "E"),
                (175, 12, "E"),
            ]
            for ex, ey, etype in enemy_positions:
                if ex < 212:
                    level_data[ey] = level_data[ey][:ex] + etype + level_data[ey][ex+1:]
            
            levels[level_id] = level_data
    
    return levels

LEVELS = generate_level_data()

# Create thumbnails
THUMBNAILS = {}
for level_id in LEVELS.keys():
    thumb = pygame.Surface((64, 48))
    thumb.fill(SKY_BLUE)
    pygame.draw.rect(thumb, GROUND_DARK, (0, 40, 64, 8))
    THUMBNAILS[level_id] = thumb

# Entity classes
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
            self.vy += 0.4 * dt * 60
            if self.vy > 8:
                self.vy = 8
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
        self.jump_power = -6.5
        self.move_speed = 2.5
        self.run_speed = 4
        self.invincible = 0
        self.animation_frame = 0
        self.walk_timer = 0
    def update(self, colliders, dt, enemies):
        keys = pygame.key.get_pressed()
        running = keys[K_LSHIFT] or keys[K_RSHIFT]
        speed = self.run_speed if running else self.move_speed
        
        self.vx = 0
        if keys[K_LEFT] or keys[K_a]:
            self.vx = -speed
            self.facing_right = False
        if keys[K_RIGHT] or keys[K_d]:
            self.vx = speed
            self.facing_right = True
        if (keys[K_SPACE] or keys[K_w] or keys[K_UP]) and self.on_ground:
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
                if self.vy > 0 and self.y + self.height - 8 < enemy.y:
                    enemy.stomp()
                    self.vy = self.jump_power / 2
                    state.score += 100
                elif self.invincible <= 0:
                    if state.power > 0:
                        state.power = 0
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
        # Fall death
        if self.y > HEIGHT:
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
        
        # SMB1 Small Mario sprite (16x16)
        # Hat
        pygame.draw.rect(surf, MARIO_RED, (x+3, y, 10, 4))
        pygame.draw.rect(surf, MARIO_RED, (x+2, y+2, 12, 2))
        # Face
        pygame.draw.rect(surf, MARIO_SKIN, (x+2, y+4, 12, 4))
        pygame.draw.rect(surf, MARIO_SKIN, (x+4, y+8, 8, 2))
        # Hair/sideburns
        pygame.draw.rect(surf, MARIO_BROWN, (x+2, y+4, 2, 4))
        pygame.draw.rect(surf, MARIO_BROWN, (x+12, y+4, 2, 4))
        # Eyes
        pygame.draw.rect(surf, BLACK, (x+4, y+5, 2, 2))
        pygame.draw.rect(surf, BLACK, (x+10, y+5, 2, 2))
        # Body/Overalls
        pygame.draw.rect(surf, MARIO_RED, (x+2, y+10, 12, 4))
        pygame.draw.rect(surf, MARIO_BROWN, (x+4, y+10, 8, 2))
        # Feet
        if self.animation_frame == 0 or not self.on_ground:
            pygame.draw.rect(surf, MARIO_BROWN, (x+2, y+14, 4, 2))
            pygame.draw.rect(surf, MARIO_BROWN, (x+10, y+14, 4, 2))
        elif self.animation_frame == 1:
            pygame.draw.rect(surf, MARIO_BROWN, (x+1, y+14, 4, 2))
            pygame.draw.rect(surf, MARIO_BROWN, (x+11, y+14, 4, 2))
        else:
            pygame.draw.rect(surf, MARIO_BROWN, (x+3, y+14, 4, 2))
            pygame.draw.rect(surf, MARIO_BROWN, (x+9, y+14, 4, 2))

class Goomba(Entity):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.vx = -0.5
        self.animation_frame = 0
        self.walk_timer = 0
        self.stomped = False
        self.stomp_timer = 0
    def stomp(self):
        self.stomped = True
        self.stomp_timer = 0.5
        self.vx = 0
    def update(self, colliders, dt):
        if self.stomped:
            self.stomp_timer -= dt
            if self.stomp_timer <= 0:
                self.active = False
            return
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
        if self.walk_timer > 0.15:
            self.walk_timer = 0
            self.animation_frame = (self.animation_frame + 1) % 2
    def draw(self, surf, cam):
        if not self.active:
            return
        x = int(self.x - cam)
        y = int(self.y)
        
        if self.stomped:
            # Flat goomba
            pygame.draw.rect(surf, GOOMBA_BROWN, (x, y+12, 16, 4))
            return
        
        # SMB1 Goomba sprite
        # Body (mushroom shape)
        pygame.draw.ellipse(surf, GOOMBA_BROWN, (x+1, y+2, 14, 10))
        # Face area
        pygame.draw.rect(surf, GOOMBA_TAN, (x+3, y+4, 10, 6))
        # Eyes (angry eyebrows)
        pygame.draw.rect(surf, BLACK, (x+4, y+5, 3, 3))
        pygame.draw.rect(surf, BLACK, (x+9, y+5, 3, 3))
        pygame.draw.rect(surf, WHITE, (x+5, y+6, 2, 2))
        pygame.draw.rect(surf, WHITE, (x+10, y+6, 2, 2))
        # Feet
        foot_offset = 1 if self.animation_frame == 0 else -1
        pygame.draw.ellipse(surf, GOOMBA_BROWN, (x+1+foot_offset, y+11, 6, 5))
        pygame.draw.ellipse(surf, GOOMBA_BROWN, (x+9-foot_offset, y+11, 6, 5))

class Koopa(Entity):
    """Koopa Troopa - green shelled turtle enemy"""
    def __init__(self, x, y):
        super().__init__(x, y)
        self.vx = -0.5
        self.animation_frame = 0
        self.walk_timer = 0
        self.shell_mode = False
        self.shell_speed = 0
    def stomp(self):
        if not self.shell_mode:
            self.shell_mode = True
            self.vx = 0
            self.height = 14
            self.y += 2
        else:
            # Kick shell
            self.shell_speed = 5 if self.x > state.score else -5  # kick direction
            self.vx = self.shell_speed
    def update(self, colliders, dt):
        if self.shell_mode and self.vx == 0:
            return  # Stationary shell
        if self.on_ground and not self.shell_mode:
            edge_check = pygame.Rect(self.x + (self.width if self.vx > 0 else -1), self.y + self.height, 1, 1)
            edge_found = False
            for rect in colliders:
                if edge_check.colliderect(rect):
                    edge_found = True
                    break
            if not edge_found:
                self.vx *= -1
        super().update(colliders, dt)
        if not self.shell_mode:
            self.walk_timer += dt
            if self.walk_timer > 0.15:
                self.walk_timer = 0
                self.animation_frame = (self.animation_frame + 1) % 2
    def draw(self, surf, cam):
        if not self.active:
            return
        x = int(self.x - cam)
        y = int(self.y)
        
        if self.shell_mode:
            # Shell only
            pygame.draw.ellipse(surf, TURTLE_GREEN, (x+2, y+2, 12, 12))
            pygame.draw.ellipse(surf, TURTLE_LIGHT, (x+4, y+4, 8, 8))
            pygame.draw.rect(surf, TURTLE_GREEN, (x+6, y+3, 4, 10))
            return
        
        # SMB1 Koopa Troopa sprite
        # Shell
        pygame.draw.ellipse(surf, TURTLE_GREEN, (x+2, y+6, 12, 10))
        pygame.draw.ellipse(surf, TURTLE_LIGHT, (x+4, y+8, 8, 6))
        # Head
        pygame.draw.ellipse(surf, TURTLE_LIGHT, (x+3, y+1, 8, 7))
        # Eye
        pygame.draw.rect(surf, BLACK, (x+5, y+3, 2, 2))
        # Feet
        foot_offset = 1 if self.animation_frame == 0 else -1
        pygame.draw.rect(surf, TURTLE_LIGHT, (x+3+foot_offset, y+14, 4, 2))
        pygame.draw.rect(surf, TURTLE_LIGHT, (x+9-foot_offset, y+14, 4, 2))

class TileMap:
    def __init__(self, level_data, level_id):
        self.tiles = []
        self.colliders = []
        self.width = len(level_data[0]) * TILE
        self.height = len(level_data) * TILE
        self.level_id = level_id
        world = int(level_id.split("-")[0])
        self.sky_color = WORLD_THEMES.get(world, WORLD_THEMES[1])["sky"]
        
        for y, row in enumerate(level_data):
            for x, char in enumerate(row):
                if char not in (" ", "M", "E", "K"):
                    rect = pygame.Rect(x * TILE, y * TILE, TILE, TILE)
                    self.tiles.append((x * TILE, y * TILE, char))
                    if char in ("G", "D", "B", "?", "S", "C", "P", "p", "T", "t"):
                        self.colliders.append(rect)
    
    def draw(self, surf, cam):
        surf.fill(self.sky_color)
        
        # Draw clouds (SMB1 style)
        cloud_positions = [(36, 20), (100, 36), (150, 20), (220, 44), (300, 28), (380, 36), (450, 20), (530, 44)]
        for cx, cy in cloud_positions:
            draw_x = (cx - cam * 0.3) % (self.width + 200)
            pygame.draw.ellipse(surf, WHITE, (draw_x, cy, 32, 16))
            pygame.draw.ellipse(surf, WHITE, (draw_x+16, cy-8, 32, 20))
            pygame.draw.ellipse(surf, WHITE, (draw_x+32, cy, 32, 16))
        
        # Draw bushes (SMB1 style) - same sprite as clouds but green, on ground
        bush_positions = [(50, 13*TILE), (200, 13*TILE), (360, 13*TILE), (500, 13*TILE)]
        for bx, by in bush_positions:
            draw_x = bx - cam
            if -48 < draw_x < WIDTH + 48:
                pygame.draw.ellipse(surf, PIPE_GREEN, (draw_x, by, 32, 12))
                pygame.draw.ellipse(surf, PIPE_GREEN, (draw_x+16, by-4, 16, 14))
        
        # Draw hills (SMB1 style)
        hill_positions = [(0, 13*TILE), (240, 13*TILE), (480, 13*TILE), (720, 13*TILE)]
        for hx, hy in hill_positions:
            draw_x = hx - cam
            if -80 < draw_x < WIDTH + 80:
                # Big hill
                pygame.draw.polygon(surf, PIPE_GREEN, [
                    (draw_x+40, hy),
                    (draw_x, hy+32),
                    (draw_x+80, hy+32)
                ])
                pygame.draw.ellipse(surf, PIPE_LIGHT, (draw_x+30, hy+4, 20, 8))
        
        for tx, ty, char in self.tiles:
            draw_x = tx - cam
            if draw_x < -TILE or draw_x > WIDTH:
                continue
            
            if char == "G":
                # Ground top tile (SMB1 brick pattern)
                pygame.draw.rect(surf, GROUND_DARK, (draw_x, ty, TILE, TILE))
                # Brick lines
                pygame.draw.line(surf, GROUND_LIGHT, (draw_x, ty), (draw_x+TILE, ty), 1)
                pygame.draw.line(surf, GROUND_LIGHT, (draw_x, ty+8), (draw_x+TILE, ty+8), 1)
                pygame.draw.line(surf, BRICK_LINE, (draw_x+8, ty), (draw_x+8, ty+8), 1)
                pygame.draw.line(surf, BRICK_LINE, (draw_x, ty+8), (draw_x, ty+TILE), 1)
                pygame.draw.line(surf, BRICK_LINE, (draw_x+TILE-1, ty+8), (draw_x+TILE-1, ty+TILE), 1)
                
            elif char == "D":
                # Ground fill/dirt
                pygame.draw.rect(surf, GROUND_DARK, (draw_x, ty, TILE, TILE))
                pygame.draw.line(surf, BRICK_LINE, (draw_x+8, ty), (draw_x+8, ty+8), 1)
                pygame.draw.line(surf, BRICK_LINE, (draw_x, ty+8), (draw_x, ty+TILE), 1)
                pygame.draw.line(surf, BRICK_LINE, (draw_x+TILE-1, ty+8), (draw_x+TILE-1, ty+TILE), 1)
                
            elif char == "B":
                # Brick block (SMB1 style)
                pygame.draw.rect(surf, BRICK_LIGHT, (draw_x, ty, TILE, TILE))
                pygame.draw.rect(surf, BRICK_DARK, (draw_x+1, ty+1, TILE-2, TILE-2))
                pygame.draw.rect(surf, BRICK_LIGHT, (draw_x+2, ty+2, 5, 6))
                pygame.draw.rect(surf, BRICK_LIGHT, (draw_x+9, ty+2, 5, 6))
                pygame.draw.rect(surf, BRICK_LIGHT, (draw_x+2, ty+9, 12, 5))
                pygame.draw.line(surf, BLACK, (draw_x, ty), (draw_x+TILE, ty), 1)
                pygame.draw.line(surf, BLACK, (draw_x, ty+TILE-1), (draw_x+TILE, ty+TILE-1), 1)
                pygame.draw.line(surf, BLACK, (draw_x, ty), (draw_x, ty+TILE), 1)
                pygame.draw.line(surf, BLACK, (draw_x+TILE-1, ty), (draw_x+TILE-1, ty+TILE), 1)
                
            elif char == "?":
                # Question block (SMB1 style)
                pygame.draw.rect(surf, QBLOCK_ORANGE, (draw_x, ty, TILE, TILE))
                pygame.draw.rect(surf, QBLOCK_DARK, (draw_x+1, ty+1, TILE-2, TILE-2))
                pygame.draw.rect(surf, QBLOCK_ORANGE, (draw_x+2, ty+2, TILE-4, TILE-4))
                # Question mark
                pygame.draw.rect(surf, BLACK, (draw_x+5, ty+3, 6, 2))
                pygame.draw.rect(surf, BLACK, (draw_x+9, ty+5, 2, 3))
                pygame.draw.rect(surf, BLACK, (draw_x+5, ty+7, 6, 2))
                pygame.draw.rect(surf, BLACK, (draw_x+5, ty+9, 2, 2))
                pygame.draw.rect(surf, BLACK, (draw_x+5, ty+12, 2, 2))
                # Border
                pygame.draw.line(surf, BLACK, (draw_x, ty), (draw_x+TILE, ty), 1)
                pygame.draw.line(surf, BLACK, (draw_x, ty+TILE-1), (draw_x+TILE, ty+TILE-1), 1)
                pygame.draw.line(surf, BLACK, (draw_x, ty), (draw_x, ty+TILE), 1)
                pygame.draw.line(surf, BLACK, (draw_x+TILE-1, ty), (draw_x+TILE-1, ty+TILE), 1)
                
            elif char == "S":
                # Stair block (solid color like SMB1)
                pygame.draw.rect(surf, GROUND_DARK, (draw_x, ty, TILE, TILE))
                pygame.draw.rect(surf, GROUND_LIGHT, (draw_x+2, ty+2, 4, 4))
                pygame.draw.rect(surf, GROUND_LIGHT, (draw_x+10, ty+2, 4, 4))
                pygame.draw.rect(surf, GROUND_LIGHT, (draw_x+2, ty+10, 4, 4))
                pygame.draw.rect(surf, GROUND_LIGHT, (draw_x+10, ty+10, 4, 4))
                pygame.draw.line(surf, BLACK, (draw_x, ty), (draw_x+TILE, ty), 1)
                pygame.draw.line(surf, BLACK, (draw_x, ty), (draw_x, ty+TILE), 1)
                
            elif char in ("P", "p"):
                # Pipe body
                pygame.draw.rect(surf, PIPE_GREEN, (draw_x, ty, TILE, TILE))
                pygame.draw.rect(surf, PIPE_LIGHT, (draw_x+2, ty, 4, TILE))
                pygame.draw.rect(surf, PIPE_DARK, (draw_x+TILE-4, ty, 4, TILE))
                
            elif char in ("T", "t"):
                # Pipe top
                pygame.draw.rect(surf, PIPE_GREEN, (draw_x-2, ty, TILE+4, TILE))
                pygame.draw.rect(surf, PIPE_LIGHT, (draw_x, ty+2, 4, TILE-4))
                pygame.draw.rect(surf, PIPE_DARK, (draw_x+TILE-2, ty+2, 4, TILE-4))
                pygame.draw.line(surf, PIPE_DARK, (draw_x-2, ty), (draw_x+TILE+2, ty), 2)
                pygame.draw.line(surf, PIPE_LIGHT, (draw_x-2, ty+TILE-2), (draw_x+TILE+2, ty+TILE-2), 2)
                
            elif char == "F":
                # Flagpole
                pygame.draw.rect(surf, FLAGPOLE_GREEN, (draw_x+6, ty, 4, TILE))
                if ty < 5 * TILE:
                    # Flag at top
                    pygame.draw.polygon(surf, MARIO_RED, [
                        (draw_x+6, ty+4),
                        (draw_x-8, ty+10),
                        (draw_x+6, ty+16)
                    ])
                    # Ball on top
                    pygame.draw.circle(surf, FLAGPOLE_GREEN, (draw_x+8, ty+2), 4)
                    
            elif char == "C":
                # Castle brick
                pygame.draw.rect(surf, BLACK, (draw_x, ty, TILE, TILE))
                pygame.draw.rect(surf, (100, 100, 100), (draw_x+1, ty+1, 6, 6))
                pygame.draw.rect(surf, (100, 100, 100), (draw_x+9, ty+1, 6, 6))
                pygame.draw.rect(surf, (100, 100, 100), (draw_x+1, ty+9, 6, 6))
                pygame.draw.rect(surf, (100, 100, 100), (draw_x+9, ty+9, 6, 6))
                
            elif char == "c":
                # Castle door
                pygame.draw.rect(surf, BLACK, (draw_x, ty, TILE, TILE))

class TitleScreen(Scene):
    def __init__(self):
        self.timer = 0
        self.animation_frame = 0
        self.logo_y = -50
        self.logo_target_y = 60
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
            self.logo_y += 3
    def draw(self, surf):
        surf.fill(SKY_BLUE)
        
        # Ground
        pygame.draw.rect(surf, GROUND_DARK, (0, HEIGHT-64, WIDTH, 64))
        
        # Logo box
        box_width, box_height = 300, 120
        box_x = (WIDTH - box_width) // 2
        box_y = int(self.logo_y)
        
        pygame.draw.rect(surf, BLACK, (box_x-4, box_y-4, box_width+8, box_height+8))
        pygame.draw.rect(surf, BRICK_LIGHT, (box_x, box_y, box_width, box_height))
        
        title_font = pygame.font.SysFont(None, 48)
        title = title_font.render("KOOPA ENGINE", True, WHITE)
        surf.blit(title, (box_x + (box_width - title.get_width()) // 2, box_y + 20))
        
        subtitle_font = pygame.font.SysFont(None, 24)
        subtitle = subtitle_font.render("SMB1 Style Edition", True, QBLOCK_ORANGE)
        surf.blit(subtitle, (box_x + (box_width - subtitle.get_width()) // 2, box_y + 65))
        
        copyright_font = pygame.font.SysFont(None, 18)
        copyright_text = copyright_font.render("[C] Team Flames 20XX", True, BLACK)
        surf.blit(copyright_text, (WIDTH//2 - copyright_text.get_width()//2, box_y + box_height + 10))
        
        # Characters on ground
        char_y = HEIGHT - 80
        
        # Mario
        mario_x = WIDTH//2 - 80
        pygame.draw.rect(surf, MARIO_RED, (mario_x+3, char_y, 10, 4))
        pygame.draw.rect(surf, MARIO_SKIN, (mario_x+2, char_y+4, 12, 4))
        pygame.draw.rect(surf, MARIO_RED, (mario_x+2, char_y+8, 12, 4))
        pygame.draw.rect(surf, MARIO_BROWN, (mario_x+2, char_y+12, 4, 4))
        pygame.draw.rect(surf, MARIO_BROWN, (mario_x+10, char_y+12, 4, 4))
        
        # Goomba
        goomba_x = WIDTH//2 + 20
        pygame.draw.ellipse(surf, GOOMBA_BROWN, (goomba_x, char_y+2, 16, 10))
        pygame.draw.ellipse(surf, GOOMBA_BROWN, (goomba_x+2, char_y+10, 5, 6))
        pygame.draw.ellipse(surf, GOOMBA_BROWN, (goomba_x+9, char_y+10, 5, 6))
        
        # Green turtle (Koopa)
        turtle_x = WIDTH//2 + 60
        pygame.draw.ellipse(surf, TURTLE_GREEN, (turtle_x+2, char_y+4, 12, 10))
        pygame.draw.ellipse(surf, TURTLE_LIGHT, (turtle_x+3, char_y+1, 8, 6))
        pygame.draw.rect(surf, TURTLE_LIGHT, (turtle_x+4, char_y+12, 3, 4))
        pygame.draw.rect(surf, TURTLE_LIGHT, (turtle_x+9, char_y+12, 3, 4))
        
        if self.logo_y >= self.logo_target_y and int(self.timer * 10) % 2 == 0:
            font = pygame.font.SysFont(None, 28)
            text = font.render("PRESS ENTER", True, WHITE)
            surf.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT - 40))

class FileSelect(Scene):
    def __init__(self):
        self.offset = 0
        self.selected = 0
    def handle(self, evts, keys):
        for e in evts:
            if e.type == KEYDOWN:
                if e.key in (K_1, K_2, K_3):
                    self.selected = e.key - K_1
                elif e.key == K_RETURN:
                    state.slot = self.selected
                    state.world = state.progress[state.slot]["world"]
                    push(LevelScene(f"{state.world}-1"))
                elif e.key == K_ESCAPE:
                    push(TitleScreen())
    def update(self, dt):
        self.offset += dt
    def draw(self, s):
        s.fill(BLACK)
        font = pygame.font.SysFont(None, 36)
        title = font.render("SELECT FILE", True, WHITE)
        s.blit(title, (WIDTH//2 - title.get_width()//2, 40))
        
        for i in range(3):
            x = 80 + i * 150
            y = 120 + 8 * math.sin(self.offset * 3 + i)
            
            pygame.draw.rect(s, BRICK_DARK, (x-5, y-5, 100, 120))
            pygame.draw.rect(s, BRICK_LIGHT, (x, y, 90, 110))
            
            slot_font = pygame.font.SysFont(None, 32)
            slot_text = slot_font.render(f"FILE {i+1}", True, BLACK)
            s.blit(slot_text, (x + 45 - slot_text.get_width()//2, y+10))
            
            if i == self.selected:
                pygame.draw.rect(s, QBLOCK_ORANGE, (x-8, y-8, 106, 126), 4)
            
            if state.progress[i]:
                world = state.progress[i]["world"]
                world_font = pygame.font.SysFont(None, 24)
                world_text = world_font.render(f"WORLD {world}", True, BLACK)
                s.blit(world_text, (x + 45 - world_text.get_width()//2, y+80))

class LevelScene(Scene):
    def __init__(self, level_id):
        self.map = TileMap(LEVELS[level_id], level_id)
        self.player = Player(50, 180)
        self.enemies = []
        self.cam = 0.0
        self.level_id = level_id
        self.time = 400
        self.end_level = False
        self.end_timer = 0
        world = int(level_id.split("-")[0])
        
        for y, row in enumerate(LEVELS[level_id]):
            for x, char in enumerate(row):
                if char == "M":
                    self.player.x = x * TILE
                    self.player.y = y * TILE
                elif char == "E":
                    self.enemies.append(Goomba(x * TILE, y * TILE))
                elif char == "K":
                    self.enemies.append(Koopa(x * TILE, y * TILE))
    
    def handle(self, evts, keys):
        for e in evts:
            if e.type == KEYDOWN and e.key == K_ESCAPE:
                push(TitleScreen())
                
    def update(self, dt):
        self.time -= dt
        self.player.update(self.map.colliders, dt, self.enemies)
        for enemy in self.enemies:
            if enemy.active:
                enemy.update(self.map.colliders, dt)
        
        # Camera follows player
        target = self.player.x - WIDTH // 3
        self.cam += (target - self.cam) * 0.1
        self.cam = max(0, min(self.cam, self.map.width - WIDTH))
        
        # Level end
        if self.player.x > self.map.width - 200 and not self.end_level:
            self.end_level = True
            self.end_timer = 3
            
        if self.end_level:
            self.end_timer -= dt
            if self.end_timer <= 0:
                world, level = self.level_id.split("-")
                world = int(world)
                level = int(level)
                if level < 4:
                    push(LevelScene(f"{world}-{level+1}"))
                else:
                    if world < 8:
                        state.unlocked_worlds.append(world + 1)
                    push(TitleScreen())
        
    def draw(self, s):
        self.map.draw(s, self.cam)
        for enemy in self.enemies:
            enemy.draw(s, self.cam)
        self.player.draw(s, self.cam)
        
        # HUD (SMB1 style)
        font = pygame.font.SysFont(None, 24)
        
        # MARIO label and score
        mario_label = font.render("MARIO", True, WHITE)
        s.blit(mario_label, (40, 16))
        score_text = font.render(f"{state.score:06d}", True, WHITE)
        s.blit(score_text, (40, 32))
        
        # Coins
        pygame.draw.circle(s, QBLOCK_ORANGE, (180, 38), 8)
        coin_text = font.render(f"x{state.coins:02d}", True, WHITE)
        s.blit(coin_text, (195, 32))
        
        # World
        world_label = font.render("WORLD", True, WHITE)
        s.blit(world_label, (280, 16))
        world_text = font.render(self.level_id, True, WHITE)
        s.blit(world_text, (290, 32))
        
        # Time
        time_label = font.render("TIME", True, WHITE)
        s.blit(time_label, (420, 16))
        time_text = font.render(f"{int(self.time):03d}", True, WHITE)
        s.blit(time_text, (425, 32))

class GameOverScene(Scene):
    def __init__(self):
        self.timer = 3
    def update(self, dt):
        self.timer -= dt
        if self.timer <= 0:
            pop()
            state.lives = 3
            state.score = 0
    def draw(self, s):
        s.fill(BLACK)
        font = pygame.font.SysFont(None, 48)
        text = font.render("GAME OVER", True, WHITE)
        s.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 20))

# Main game loop
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("KOOPA ENGINE - SMB1 Style")
clock = pygame.time.Clock()
push(TitleScreen())

while SCENES:
    dt = clock.tick(FPS) / 1000
    events = pygame.event.get()
    keys = pygame.key.get_pressed()
    for e in events:
        if e.type == QUIT:
            pygame.quit()
            sys.exit()
    scene = SCENES[-1]
    scene.handle(events, keys)
    scene.update(dt)
    scene.draw(screen)
    pygame.display.flip()

pygame.quit()
sys.exit()
