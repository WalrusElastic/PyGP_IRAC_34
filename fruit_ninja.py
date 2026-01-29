import sys
import os
import random
import pygame

# ==================== GLOBAL GAME VARIABLES ====================
score = 0 
game_duration = 60
current_time = 0 
fruit_spawn_rate = 0.2  

WHITE = (255, 255, 255)

# ==================== INITIALIZING PYGAME WINDOW ====================

WIDTH = 800
HEIGHT = 500
FPS = 30
pygame.init()
pygame.display.set_caption("Fruit-Ninja Game -- DataFlair")
gameDisplay = pygame.display.set_mode((WIDTH, HEIGHT)) 
clock = pygame.time.Clock()


# ==================== LOAD IMAGES ====================
background = pygame.image.load("summer.jpg")


# DISPLAY FONT ON SCREEN
font_name = pygame.font.match_font("mario.otf")


def draw_text(display, text, size, x, y):

    font = pygame.font.Font(os.path.join(os.getcwd(), "mario.otf"), size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    display.blit(text_surface, text_rect)


# ==================== FRUIT CLASS ====================


class Fruit:
    # Base class for fruits in the game

    def __init__(self, name, game_display):
        self.name = name
        self.game_display = game_display
        self.fruit_path = "images/" + name + ".png"
        self.img = pygame.image.load(self.fruit_path)
        self.x = random.randint(100, 500)
        self.y = 800
        self.speed_x = random.randint(-10, 10)
        self.speed_y = random.randint(-60, -50)
        self.throw = False
        self.t = 0
        self.hit = False
        self.set_throw_status()

    def set_throw_status(self):
        # Randomly decide if fruit should be thrown
        if random.random() >= 0.75:
            self.throw = True
        else:
            self.throw = False

    def update(self):
        # Update fruit position and physics
        if self.throw:
            self.x += self.speed_x
            self.y += self.speed_y
            self.speed_y += 0.3 * self.t
            self.t += 1

    def draw(self):
        # Draw fruit on screen if within bounds
        if self.y <= 800:
            self.game_display.blit(self.img, (self.x, self.y))

    def is_outside_screen(self):
        # Check if fruit has fallen off screen
        return self.y > 800

    def reset(self):
        # Reset fruit for next spawn
        self.x = random.randint(100, 500)
        self.y = 800
        self.speed_x = random.randint(-10, 10)
        self.speed_y = random.randint(-60, -50)
        self.t = 0
        self.hit = False
        self.img = pygame.image.load(self.fruit_path)
        self.set_throw_status()

    def check_collision(self, mouse_x, mouse_y):
        # Check if mouse collides with fruit
        if (
            not self.hit
            and mouse_x > self.x
            and mouse_x < self.x + 60
            and mouse_y > self.y
            and mouse_y < self.y + 60
        ):
            return True
        return False

    def on_hit(self):
        # Handle fruit being hit
        self.hit = True
        half_fruit_path = "images/half_" + self.name + ".png"
        self.img = pygame.image.load(half_fruit_path)
        self.speed_x += 10


class FruitManager:
    # Manager class for handling all fruits

    def __init__(self, game_display, fruit_names=None):
        self.game_display = game_display
        self.fruits = {}
        self.fruit_names = fruit_names or ["melon", "orange", "pomegranate", "guava"]
        self.initialize_fruits()

    def initialize_fruits(self):
        # Create initial fruit instances
        for fruit_name in self.fruit_names:
            self.fruits[fruit_name] = Fruit(fruit_name, self.game_display)

    def update(self):
        # Update all fruits and regenerate those not thrown
        for fruit_name, fruit in self.fruits.items():
            if fruit.throw:
                fruit.update()
            else:
                self.reset_fruit(fruit_name)

    def draw(self):
        # Draw all fruits
        for fruit in self.fruits.values():
            if fruit.throw:
                fruit.draw()

    def reset_fruit(self, fruit_name):
        # Reset a specific fruit
        if fruit_name in self.fruits:
            self.fruits[fruit_name].reset()

    def check_collisions(self, mouse_x, mouse_y):
        # Check collisions for all fruits, returns (fruit_name, fruit_obj) or (None, None)
        for fruit_name, fruit in self.fruits.items():
            if fruit.throw and fruit.check_collision(mouse_x, mouse_y):
                return fruit_name, fruit
        return None, None

    def handle_fruit_hit(self, fruit_name, fruit):
        # Handle a fruit being hit
        fruit.on_hit()

    def remove_offscreen_fruits(self):
        # Reset fruits that have fallen off screen
        for fruit_name, fruit in self.fruits.items():
            if fruit.throw and fruit.is_outside_screen():
                self.reset_fruit(fruit_name)

    def get_fruit(self, fruit_name):
        # Get a specific fruit object
        return self.fruits.get(fruit_name)


def show_gameover_screen():

    gameDisplay.blit(background, (0, 0))
    draw_text(gameDisplay, "FRUIT NINJA!", 70, WIDTH / 2, HEIGHT / 4)
    if not game_over:
        draw_text(gameDisplay, "Score : " + str(score), 35, WIDTH / 2, HEIGHT / 2)
    draw_text(gameDisplay, "Press Enter to begin!", 35, WIDTH / 2, HEIGHT * 3 / 4)
    pygame.display.flip()

    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYUP:
                waiting = False


# MAIN GAME LOOP

first_round = True
game_over = True
game_running = True
game_duration = 60
current_time = 0

while game_running:

    if game_over:

        if first_round:
            show_gameover_screen()
            first_round = False
        game_over = False

        # reset score for new game
        score = 0

        # Initialize fruit manager for new game
        fruit_manager = FruitManager(gameDisplay)

        start_time = pygame.time.get_ticks()

    # ==================== INPUT ====================

    for event in pygame.event.get():
        # checking for closing window
        if event.type == pygame.QUIT:
            game_running = False

    current_position = pygame.mouse.get_pos()
    # ==================== UPDATE ====================

    current_time = (pygame.time.get_ticks() - start_time) // 1000

    # Check if game duration has ended
    if current_time >= game_duration:
        show_gameover_screen()
        game_over = True
        start_time = pygame.time.get_ticks()
        continue

    # Update all fruits
    fruit_manager.update()
    fruit_manager.remove_offscreen_fruits()

    # Check for collisions with mouse
    fruit_name, fruit_obj = fruit_manager.check_collisions(
        current_position[0], current_position[1]
    )

    if fruit_name is not None:
        # A fruit has been hit
        fruit_manager.handle_fruit_hit(fruit_name, fruit_obj)
        score += 1

    # ==================== RENDER ====================

    # Draw background
    gameDisplay.blit(background, (0, 0))

    # Draw timer
    draw_text(gameDisplay, "Time: " + str(game_duration - current_time), 27, 100, 50)

    # Draw score
    draw_text(gameDisplay, "Score: " + str(score), 40, 125, 10)

    # Draw all fruits
    fruit_manager.draw()

    # Update display
    pygame.display.update()
    clock.tick(
        FPS
    )  # keep loop running at the right speed (manages the frame/second. The loop should update afer every 1/12th pf the sec

pygame.quit()
