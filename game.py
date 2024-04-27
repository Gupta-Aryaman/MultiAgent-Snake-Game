import pygame
import random
from enum import Enum
from collections import namedtuple
import numpy as np

pygame.init()
font = pygame.font.Font('arial.ttf', 25)
#font = pygame.font.SysFont('arial', 25)

class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

Point = namedtuple('Point', 'x, y')

# rgb colors
WHITE = (255, 255, 255)
RED = (200,0,0)
BLUE1 = (0, 0, 255)
BLUE2 = (0, 100, 255)
BLACK = (0,0,0)

BLOCK_SIZE = 20
SPEED = 10

class SnakeGameAI:

    def __init__(self, w=640, h=480):
        self.w = w
        self.h = h
        # init display
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Snake')
        self.clock = pygame.time.Clock()
        
        
        # init game state
        self.direction = Direction.RIGHT

        self.head = Point(self.w/2, self.h/2)
        self.snake = [self.head,
                      Point(self.head.x-BLOCK_SIZE, self.head.y),
                      Point(self.head.x-(4*BLOCK_SIZE), self.head.y)]

        self.score = 0
        self.food = None
        self._place_food()
        self.frame_iteration = 0


        # init game state for player
        self.direction_player = Direction.RIGHT

        self.head_player = Point(self.w/2 - 5*BLOCK_SIZE, self.h/2 - 3*BLOCK_SIZE)
        self.snake_player = [self.head_player,
                        Point(self.head_player.x-BLOCK_SIZE, self.head_player.y),
                        Point(self.head_player.x-(2*BLOCK_SIZE), self.head_player.y)]
        
        self.score_player = 0
        


    def _place_food(self):
        x = random.randint(0, (self.w-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE
        y = random.randint(0, (self.h-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE
        self.food = Point(x, y)
        if self.food in self.snake:
            self._place_food()


    def play_step(self, action):
        self.frame_iteration += 1
        # 1. collect user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        
        # 2. move
        self._move(action) # update the head
        self.snake.insert(0, self.head)
        
        # 3. check if game over
        reward = 0
        game_over = False
        if self.is_collision() or self.frame_iteration > 100*len(self.snake):
            game_over = True
            reward = -10
            return reward, game_over, self.score

        # 4. place new food or just move
        if self.head == self.food:
            self.score += 1
            reward = 10
            self._place_food()
        else:
            self.snake.pop()
        
        # 5. update ui and clock
        self._update_ui()
        self.clock.tick(SPEED)
        # 6. return game over and score
        return reward, game_over, self.score
    
    def play_step_player(self):
        # 1. collect user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.direction_player = Direction.LEFT
                elif event.key == pygame.K_RIGHT:
                    self.direction_player = Direction.RIGHT
                elif event.key == pygame.K_UP:
                    self.direction_player = Direction.UP
                elif event.key == pygame.K_DOWN:
                    self.direction_player = Direction.DOWN
        
        # 2. move
        self._move_player(self.direction_player) # update the head
        self.snake_player.insert(0, self.head_player)
        
        # 3. check if game over
        game_over = False
        if self._is_collision_player():
            game_over = True
            return game_over, self.score
            
        # 4. place new food or just move
        if self.head_player == self.food:
            self.score_player += 1
            self._place_food()
        else:
            self.snake_player.pop()
        
        # 5. update ui and clock
        self._update_ui()
        self.clock.tick(SPEED)
        # 6. return game over and score
        return game_over, self.score_player


    def is_collision(self, pt=None):
        if pt is None:
            pt = self.head

        # hits boundary
        if pt.x > self.w - BLOCK_SIZE or pt.x < 0 or pt.y > self.h - BLOCK_SIZE or pt.y < 0:
            return True
        
        # hits itself
        if pt in self.snake[1:]:
            return True

        # if pt in self.snake_player : print(True)

        # hits player
        if pt in self.snake_player:
            return True

        return False
    
    def _is_collision_player(self):
        # hits boundary
        if self.head_player.x > self.w - BLOCK_SIZE or self.head_player.x < 0 or self.head_player.y > self.h - BLOCK_SIZE or self.head_player.y < 0:
            return True
        
        # hits itself
        if self.head_player in self.snake_player[1:]:
            return True
        
        # hits AI snake
        if self.head_player in self.snake:
            return True
        
        return False


    def _update_ui(self):
        self.display.fill(BLACK)

        for pt in self.snake:
            pygame.draw.rect(self.display, BLUE1, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(self.display, BLUE2, pygame.Rect(pt.x+4, pt.y+4, 12, 12))

        for player_pt in self.snake_player:
            pygame.draw.rect(self.display, WHITE, pygame.Rect(player_pt.x, player_pt.y, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(self.display, RED, pygame.Rect(player_pt.x+4, player_pt.y+4, 12, 12))

        pygame.draw.rect(self.display, RED, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))

        text = font.render("AI Score: " + str(self.score), True, WHITE)
        self.display.blit(text, [0, 0])

        text = font.render("Player Score: " + str(self.score_player), True, WHITE)
        self.display.blit(text, [450, 0])

        pygame.display.flip()


    def _move(self, action):
        # [straight, right, left]

        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        idx = clock_wise.index(self.direction)

        if np.array_equal(action, [1, 0, 0]):
            new_dir = clock_wise[idx] # no change
        elif np.array_equal(action, [0, 1, 0]):
            next_idx = (idx + 1) % 4
            new_dir = clock_wise[next_idx] # right turn r -> d -> l -> u
        else: # [0, 0, 1]
            next_idx = (idx - 1) % 4
            new_dir = clock_wise[next_idx] # left turn r -> u -> l -> d

        self.direction = new_dir

        x = self.head.x
        y = self.head.y
        if self.direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif self.direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif self.direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif self.direction == Direction.UP:
            y -= BLOCK_SIZE

        self.head = Point(x, y)

    
    def _move_player(self, direction):
        x = self.head_player.x
        y = self.head_player.y
        if direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif direction == Direction.UP:
            y -= BLOCK_SIZE
            
        self.head_player = Point(x, y)

    