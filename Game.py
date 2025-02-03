import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
CAR_WIDTH = 50
CAR_HEIGHT = 80
OBSTACLE_WIDTH = 50
OBSTACLE_HEIGHT = 80
FPS = 60
ROAD_WIDTH = 400
ROAD_COLOR = (50, 50, 50)  # Dark gray for the road
GRASS_COLOR = (0, 128, 0)   # Green for grass
INITIAL_OBSTACLE_SPEED = 6 
CAR_MAX_SPEED = 300  # Maximum speed of the car
MIN_CAR_SPEED = -30  # Minimum speed of the car (in km/h)
BASE_ACCELERATION = 1.0  # Base acceleration rate
DECELERATION = 1.0   # Deceleration rate

# Load car images
car_image = pygame.image.load('playerCar.png')  # Load player car image
car_image = pygame.transform.scale(car_image, (CAR_WIDTH, CAR_HEIGHT))  # Scale it to the desired size

# Load opponent obstacle images
obstacle_images = [
    pygame.image.load('opponentCar.png'),
    pygame.image.load('opponentCar2.png'),
    pygame.image.load('opponentCar3.png')
]

# Scale opponent images
obstacle_images = [pygame.transform.scale(img, (OBSTACLE_WIDTH, OBSTACLE_HEIGHT)) for img in obstacle_images]

# Load the close application logo
close_app_logo = pygame.image.load('closeAppLogo.png')  # Load close app logo
close_app_logo = pygame.transform.scale(close_app_logo, (45, 45))  # Scale to the desired size

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Crazy Car")

# Game clock
clock = pygame.time.Clock()

def draw_buttons():
    # Create button rectangles
    play_again_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2, 200, 50)
    quit_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 60, 200, 50)
    
    # Draw buttons
    pygame.draw.rect(screen, (0, 255, 0), play_again_button)  # Green button
    pygame.draw.rect(screen, (255, 0, 0), quit_button)  # Red button
    
    # Create font and render text
    font = pygame.font.Font(None, 36)
    play_again_text = font.render('Play Again', True, (0, 0, 0))
    quit_text = font.render('Quit', True, (0, 0, 0))
    
    # Center the text on the buttons
    play_again_text_rect = play_again_text.get_rect(center=play_again_button.center)
    quit_text_rect = quit_text.get_rect(center=quit_button.center)
    
    # Blit the text onto the buttons
    screen.blit(play_again_text, play_again_text_rect)
    screen.blit(quit_text, quit_text_rect)
    
    return play_again_button, quit_button

def game_over(distance):
    while True:
        screen.fill((0, 0, 0))  # Black background
        font = pygame.font.Font(None, 70)
        text = font.render('Game Over', True, (255, 255, 255))
        
        # Center the game over text
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
        screen.blit(text, text_rect)

        # Display the latest distance
        distance_font = pygame.font.Font(None, 38)  # Set font size
        distance_text = distance_font.render(f'Your Distance: {int(distance)} metres', True, (255, 255, 255))
        distance_rect = distance_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 32))  # Move up by 32 pixels
        screen.blit(distance_text, distance_rect)

        play_again_button, quit_button = draw_buttons()
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    if play_again_button.collidepoint(event.pos):
                        main()  # Restart the game
                    elif quit_button.collidepoint(event.pos):
                        pygame.quit()
                        sys.exit()

def draw_obstacle(obstacle_rect, obstacle_image):
 # Draw the obstacle using the loaded image
    screen.blit(obstacle_image, obstacle_rect)  # Use the top-left corner of the rectangle for positioning

def draw_road(lane_offset):
    # Draw the road
    road_rect = pygame.Rect((SCREEN_WIDTH - ROAD_WIDTH) // 2, 0, ROAD_WIDTH, SCREEN_HEIGHT)
    pygame.draw.rect(screen, ROAD_COLOR, road_rect)

    # Draw roadside markers
    roadside_color = (255, 255, 255)  # White for roadside markers
    roadside_width = 10
    pygame.draw.rect(screen, roadside_color, (road_rect.x - roadside_width, 0, roadside_width, SCREEN_HEIGHT))  # Left roadside
    pygame.draw.rect(screen, roadside_color, (road_rect.x + road_rect.width, 0, roadside_width, SCREEN_HEIGHT))  # Right roadside

    # Draw lane markings
    lane_marking_color = (255, 255, 255)  # White for lane markings
    lane_marking_width = 10
    for i in range(int(lane_offset), SCREEN_HEIGHT, 40):
        pygame.draw.rect(screen, lane_marking_color, (road_rect.x + road_rect.width // 2 - lane_marking_width // 2, i, lane_marking_width, 20))

def create_gradient_surface(width, height, color1, color2):
    """Create a gradient surface from color1 to color2."""
    gradient_surface = pygame.Surface((width, height))
    for y in range(height):
        # Calculate the color for each row
        r = int(color1[0] * (1 - y / height) + color2[0] * (y / height))
        g = int(color1[1] * (1 - y / height) + color2[1] * (y / height))
        b = int(color1[2] * (1 - y / height) + color2[2] * (y / height))
        pygame.draw.line(gradient_surface, (r, g, b), (0, y), (width, y))
    return gradient_surface

def draw_rainbow_text(surface, text, font, x, y, colors):
    """Draws text with a rainbow effect."""
    total_width = 0
    for i, char in enumerate(text):
        color = colors[i % len(colors)]  # Cycle through the colors
        char_surface = font.render(char, True, color)
        char_rect = char_surface.get_rect(topleft=(x + total_width, y))
        surface.blit(char_surface, char_rect)
        total_width += char_rect.width

def calculate_acceleration(car_speed):
    """Calculate acceleration based on current speed."""
    if car_speed < 100:
        return BASE_ACCELERATION * 0.75
    elif car_speed < 200:
        return BASE_ACCELERATION * 0.50  # Decrease acceleration after 100 km/h
    elif car_speed < 300:
        return BASE_ACCELERATION * 0.25  # Further decrease after 200 km/h
    return BASE_ACCELERATION * 0.10  # Maximum acceleration at 300 km/h

def main_menu():
    # Colors for rainbow text
    rainbow_colors = [
        (255, 0, 0),    # Red
        (255, 127, 0),  # Orange
        (255, 255, 0),  # Yellow
        (0, 255, 0),    # Green
        (0, 0, 255),    # Blue
        (75, 0, 130),   # Indigo
        (148, 0, 211)   # Violet
    ]

    while True:
        screen.fill((0, 0, 0))  # Black background
        
        # Create gradient surface for the title (Gray to Red)
        gradient_surface = create_gradient_surface(400, 70, (128, 128, 128), (255, 0, 0))  # Gray to Red
        
        font = pygame.font.Font(None, 70)
        title_text = font.render('CRAZY CAR', True, (255, 255, 255))
        instruction_font = pygame.font.Font(None, 36)
        instruction_text = instruction_font.render('Press ENTER to Play', True, (0, 0, 255))

        # Adjust the vertical position of the title
        title_y_position = SCREEN_HEIGHT // 2 - 60  # Move it up by pixels
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, title_y_position))
        
        gradient_rect = gradient_surface.get_rect(center=(SCREEN_WIDTH // 2, title_y_position))  # Centering to title

        # Blit the gradient surface first, then the text
        screen.blit(gradient_surface, gradient_rect)
        screen.blit(title_text, title_rect)

        # Position the instruction text below the title
        instruction_rect = instruction_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))  # Adjust as needed
        screen.blit(instruction_text, instruction_rect)

        # Rainbow Publisher Text
        publisher_font = pygame.font.Font(None, 28)
        publisher_text = "Made by notququ"
        publisher_y_position = SCREEN_HEIGHT - 30
        draw_rainbow_text(
            screen,
            publisher_text,
            publisher_font,
            SCREEN_WIDTH // 2 - (publisher_font.size(publisher_text)[0] // 2),
            publisher_y_position,
            rainbow_colors
        )

        # Blit the close application logo
        logo_rect = close_app_logo.get_rect(topleft=(10, 10))  # Get the rect for the logo
        screen.blit(close_app_logo, logo_rect)  # Position the logo at the top left corner

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()  # Close the game when the close button is clicked
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    # Check if the mouse click is within the logo's area
                    logo_rect = close_app_logo.get_rect(topleft=(10, 10))
                    if logo_rect.collidepoint(event.pos):
                        pygame.quit()
                        sys.exit()  # Close the game when the logo is clicked
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  # Start the game when ENTER is pressed
                    main()  # Call the main game function

def main():
    running = True
    paused = False  # Variable to track if the game is paused
    car_x = SCREEN_WIDTH // 2 - CAR_WIDTH // 2
    car_y = SCREEN_HEIGHT - CAR_HEIGHT - 10
    obstacle_x = random.randint((SCREEN_WIDTH - ROAD_WIDTH) // 2, (SCREEN_WIDTH + ROAD_WIDTH) // 2 - OBSTACLE_WIDTH)
    obstacle_y = -OBSTACLE_HEIGHT
    distance = 0  # Initialize distance
    obstacle_speed = INITIAL_OBSTACLE_SPEED
    car_speed = 0  # Initialize car_speed here
    lane_offset = 0  # Offset for lane markings

    # Randomly select an obstacle image at the start
    obstacle_image = random.choice(obstacle_images)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # Check for ESC key
                    paused = not paused  # Toggle pause state

        if paused:
            # Display pause message
            screen.fill((0, 0, 0))  # Black background

            pause_font = pygame.font.Font(None, 60)  # Font size for "Paused" text
            instruction_font = pygame.font.Font(None, 40)  # Font size for instruction text
            
            pause_text = pause_font.render('Paused', True, (255, 255, 255))
            instruction_text = instruction_font.render('Press ESC again to Resume', True, (255, 255, 0))
            
            # Center the pause text
            pause_text_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            instruction_text_rect = instruction_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10))
            
            screen.blit(pause_text, pause_text_rect)  # Blit the pause text
            screen.blit(instruction_text, instruction_text_rect)  # Blit the instruction text
            
            pygame.display.flip()
            continue  # Skip the rest of the loop if paused

        keys = pygame.key.get_pressed()
        
        # Control the car's horizontal movement
        if keys[pygame.K_LEFT] and car_x > (SCREEN_WIDTH - ROAD_WIDTH) // 2:
            car_x -= 5
        if keys[pygame.K_RIGHT] and car_x < (SCREEN_WIDTH + ROAD_WIDTH) // 2 - CAR_WIDTH:
            car_x += 5

        # Calculate acceleration based on current speed
        acceleration = calculate_acceleration(car_speed)

        # Accelerate or decelerate the car
        if keys[pygame.K_UP]:  # Use 'UP' for acceleration
            car_speed += acceleration
            if car_speed > CAR_MAX_SPEED:
                car_speed = CAR_MAX_SPEED
        elif keys[pygame.K_DOWN]:  # Use 'DOWN' for brake
            car_speed -= DECELERATION * 1.5  # Immediate deceleration when pressing down
            if car_speed < MIN_CAR_SPEED:
                car_speed = MIN_CAR_SPEED
        else:
            # Smooth deceleration when not pressing down
            if car_speed > 0:
                car_speed -= DECELERATION
                if car_speed < 0:
                    car_speed = 0  # Don't go below 0
            elif car_speed < 0:
                car_speed += DECELERATION * 0.50
                if car_speed > 0:
                    car_speed = 0  # Don't go above 0

        # Update obstacle speed based on car speed
        obstacle_speed = INITIAL_OBSTACLE_SPEED + (car_speed /  10)  # Adjust the divisor for desired effect
        if car_speed > 50:  # If the car speed is high, increase obstacle speed
            obstacle_speed += 2  # Increase obstacle speed to make it harder

        # Move the obstacle based on the speed of the player's car
        obstacle_y += obstacle_speed

        # Update distance based on car speed, but scale it for realism
        # Only increment distance if the car is moving forward
        if car_speed > 0:
            distance_increment = (car_speed / 360)  # Scale the speed to a more realistic distance increment
            distance += distance_increment  # Increment distance based on the scaled speed

        # Update lane offset based on car speed for realistic movement
        lane_offset += car_speed / 12  # Adjust the divisor for speed of lane movement
        if lane_offset >= 40:  # Reset lane offset to create a looping effect
            lane_offset -= 40

        # Reset obstacle if it goes off screen
        if obstacle_y > SCREEN_HEIGHT:
            obstacle_y = -OBSTACLE_HEIGHT
            obstacle_x = random.randint((SCREEN_WIDTH - ROAD_WIDTH) // 2, (SCREEN_WIDTH + ROAD_WIDTH) // 2 - OBSTACLE_WIDTH)

                        # Randomly select an obstacle image
            obstacle_image = random.choice(obstacle_images)

        # Check for collision with the obstacle
        car_rect = pygame.Rect(car_x, car_y, CAR_WIDTH, CAR_HEIGHT)
        obstacle_rect = pygame.Rect(obstacle_x, obstacle_y, OBSTACLE_WIDTH, OBSTACLE_HEIGHT)

        if car_rect.colliderect(obstacle_rect):
            game_over(distance)  # Call game over function

        # Fill the background with grass
        screen.fill(GRASS_COLOR)

        # Draw the road and the cars
        draw_road(lane_offset)
        screen.blit(car_image, (car_x, car_y))
        draw_obstacle(obstacle_rect, obstacle_image)

        # Display the player's speed
        font = pygame.font.Font(None, 36)
        speed_text = font.render(f'Speed: {int(car_speed)} km/h', True, (0, 255, 255))
        screen.blit(speed_text, (10, 10))

        # Display the distance
        distance_text = font.render(f'Distance: {int(distance)} m', True, (0, 255, 255))
        screen.blit(distance_text, (10, 50))

        # Control instructions
        controls = [
            "Accelerate = Up",
            "Brake = Down",
            "Avoid Cars = Left & Right",
            "Pause = Esc"
        ]
        
        # Render and display control instructions in the top right corner
        for i, control in enumerate(controls):
            control_text = font.render(control, True, (0, 255, 255))  # White color for control text
            control_text_rect = control_text.get_rect(topright=(SCREEN_WIDTH - 10, 10 + i * 30))  # Position in top right
            screen.blit(control_text, control_text_rect)  # Blit the control text

        # Update the display
        pygame.display.flip()

        # Cap the frame rate
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main_menu()  # Start with the main menu