import pygame, sys, random
from pygame.math import Vector2

# Initialize Pygame
pygame.init()

# Fonts for title and score
title_font = pygame.font.Font(None, 60)
score_font = pygame.font.Font(None, 40)

# Colors
GREEN = (173, 204, 96)  # Light green background
DARK_GREEN = (43, 51, 24)  # Dark green for snake and other elements

# Game settings
cell_size = 30  # Size of each cell in the grid
number_of_cells = 25  # Number of cells on the grid (both width and height)

# Offset for drawing the grid and the snake inside the window
OFFSET = 75

# Food class handles the food logic
class Food:
    def __init__(self, snake_body) -> None:
        # Initialize food with a random position not on the snake
        self.position = self.generate_random_pos(snake_body)

    def draw(self):
        # Draw the food on the screen
        food_rect = pygame.Rect(OFFSET + self.position.x * cell_size, OFFSET + self.position.y * cell_size, cell_size, cell_size)
        screen.blit(food_surface, food_rect)

    def generate_random_cell(self):
        # Generate a random position on the grid
        x = random.randint(0, number_of_cells - 1)
        y = random.randint(0, number_of_cells - 1)
        return Vector2(x, y)

    def generate_random_pos(self, snake_body):
        # Generate a random position for food, ensuring it doesn't overlap with the snake
        position = self.generate_random_cell()
        while position in snake_body:
            position = self.generate_random_cell()
        return position

# Snake class handles the snake's body and movement
class Snake:
    def __init__(self) -> None:
        # Initialize snake starting position and direction
        self.body = [Vector2(6, 9), Vector2(5, 9), Vector2(4, 9)]
        self.direction = Vector2(1, 0)  # Initially moving right
        self.add_segment = False  # Flag to add a segment when food is eaten
        # Load sound effects for eating food and hitting walls
        self.eat_sound = pygame.mixer.Sound("Sounds/eat.mp3")
        self.wall_hit_sound = pygame.mixer.Sound("Sounds/wall.mp3")

    def draw(self):
        # Draw each segment of the snake's body on the screen
        for segment in self.body:
            segment_rect = (OFFSET + segment.x * cell_size, OFFSET + segment.y * cell_size, cell_size, cell_size)
            pygame.draw.rect(screen, DARK_GREEN, segment_rect, 0, 7)  # Draw with rounded corners

    def update(self):
        # Move the snake forward by adding a new head in the direction of movement
        self.body.insert(0, self.body[0] + self.direction)
        
        if self.add_segment:
            # If we need to add a segment (after eating food), do not remove the tail
            self.add_segment = False
        else:
            # Otherwise, remove the last segment (tail)
            self.body = self.body[:-1]

    def reset(self):
        # Reset the snake's body and direction after a game over
        self.body = [Vector2(6, 9), Vector2(5, 9), Vector2(4, 9)]
        self.direction = Vector2(1, 0)  # Start by moving right

# Game class controls the game logic
class Game:
    def __init__(self) -> None:
        # Initialize the game state
        self.snake = Snake()
        self.food = Food(self.snake.body)
        self.state = "STOPPED"  # Initially the game is stopped
        self.score = 0  # Score is initialized but not reset on game over

    def draw(self):
        # Draw the game elements: food, snake, and score
        if self.state == "STOPPED":
            # Display Game Over message when the game is stopped
            game_over_text = title_font.render("GAME WAITING", True, DARK_GREEN)
            screen.blit(game_over_text, (OFFSET + 10, screen_area // 2 - 40))
            start_message = score_font.render("Press any arrow key to start", True, DARK_GREEN)
            screen.blit(start_message, (OFFSET + 10, screen_area // 2 + 10))
        else:
            # Draw the food and snake when the game is running
            self.food.draw()
            self.snake.draw()

        # Display the score at the bottom of the screen
        score_surface = score_font.render(f"Score: {self.score}", True, DARK_GREEN)
        screen.blit(score_surface, (OFFSET - 5, OFFSET + cell_size * number_of_cells + 10))

    def update(self):
        # Update the game logic (move snake, check collisions)
        if self.state == "RUNNING":
            self.snake.update()
            self.check_collision_with_food()
            self.check_collision_with_edges()
            self.check_collision_with_tail()

    def check_collision_with_food(self):
        # Check if the snake's head collides with the food
        if self.snake.body[0] == self.food.position:
            # Generate a new food position and add a segment to the snake
            self.food.position = self.food.generate_random_pos(self.snake.body)
            self.snake.add_segment = True
            self.score += 1  # Increase the score
            self.snake.eat_sound.play()  # Play sound on food eaten

    def check_collision_with_edges(self):
        # Check if the snake hits the wall (edges of the grid)
        if self.snake.body[0].x == number_of_cells or self.snake.body[0].x == -1:
            self.game_over()
        if self.snake.body[0].y == number_of_cells or self.snake.body[0].y == -1:
            self.game_over()

    def game_over(self):
        # Only reset the snake and food, but not the score
        self.snake.reset()
        self.food.position = self.food.generate_random_pos(self.snake.body)
        self.state = "STOPPED"  # Game is stopped after a collision
        self.snake.wall_hit_sound.play()  # Play sound on wall hit

    def check_collision_with_tail(self):
        # Check if the snake's head collides with its body (self-collision)
        headless_body = self.snake.body[1:]
        if self.snake.body[0] in headless_body:
            self.game_over()

# Set up Pygame window
screen_area = 2 * OFFSET + cell_size * number_of_cells
screen = pygame.display.set_mode((screen_area, screen_area))
pygame.display.set_caption("Retro Snake")
clock = pygame.time.Clock()

# Initialize the game and food image
game = Game()
food_surface = pygame.image.load("Graphics/food.png")

# Event for controlling snake speed
SNAKE_UPDATE = pygame.USEREVENT
pygame.time.set_timer(SNAKE_UPDATE, 200)

# Main Game Loop
while True:
    # Handle events
    for event in pygame.event.get():
        if event.type == SNAKE_UPDATE:
            game.update()

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            # If the game is stopped (after a game over), any key restarts the game
            if game.state == "STOPPED":
                game.state = "RUNNING"
                game.score = 0  # Reset score only when the game is restarted
            
            # Control snake movement with arrow keys
            if event.key == pygame.K_UP and game.snake.direction != Vector2(0, 1):
                game.snake.direction = Vector2(0, -1)
            if event.key == pygame.K_DOWN and game.snake.direction != Vector2(0, -1):
                game.snake.direction = Vector2(0, 1)
            if event.key == pygame.K_LEFT and game.snake.direction != Vector2(1, 0):
                game.snake.direction = Vector2(-1, 0)
            if event.key == pygame.K_RIGHT and game.snake.direction != Vector2(-1, 0):
                game.snake.direction = Vector2(1, 0)

    # Drawing the screen
    screen.fill(GREEN)  # Fill the background with green
    pygame.draw.rect(screen, DARK_GREEN, (OFFSET - 5, OFFSET - 5, cell_size * number_of_cells + 10, cell_size * number_of_cells + 10), 5)  # Draw the grid border
    game.draw()  # Draw the game elements (food, snake, score)

    # Title and score display
    title_surface = title_font.render("Retro Snake", True, DARK_GREEN)
    screen.blit(title_surface, (OFFSET - 5, 20))

    # Update the display
    pygame.display.update()

    # Cap the frame rate to 60 FPS
    clock.tick(60)
