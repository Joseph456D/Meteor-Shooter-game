import pygame, sys
from random import randint, uniform

# Update the laser list to remove lasers that go off-screen
def laser_update(laser_list, speed=500):
    for rect in laser_list[:]:
        rect.y -= speed * dt
        if rect.bottom < 0:
            laser_list.remove(rect)


# Function to display the score on the screen with dynamic box positioning
def display_score():
    global score_text
    if not game_over:
        score_text = f"Score: {score}"  # Display the number of meteors destroyed
        text_surf = font.render(score_text, True, (255, 255, 255))

        # Dynamically center the score text at the bottom
        text_rect = text_surf.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT - (WINDOW_HEIGHT * 0.1)))

        # Draw the score box (white border with a rounded corner)
        pygame.draw.rect(display_surface, 'white', text_rect.inflate(30, 40), width=10, border_radius=5)
        
        # Display the score text inside the box
        display_surface.blit(text_surf, text_rect)


# Function to display the time played in the top-right corner
def display_time_played():
    global minutes, seconds
    if not game_over:
        # Calculate time played in seconds
        time_played = (pygame.time.get_ticks() - start_time) // 1000  # Time in seconds
        minutes = time_played // 60
        seconds = time_played % 60
        time_played_text = f"{minutes:02}:{seconds:02}"  # Format as MM:SS
        time_text_surf = font.render(time_played_text, True, (255, 255, 255))
        time_text_rect = time_text_surf.get_rect(topright=(WINDOW_WIDTH - 10, 10))  # Position in top-right corner
        display_surface.blit(time_text_surf, time_text_rect)

# Function for managing the shooting delay
def laser_timer(can_shoot, duration=500):
    if not can_shoot:
        current_time = pygame.time.get_ticks()
        if current_time - shoot_time > duration:
            can_shoot = True
    return can_shoot

# Function to update meteors' positions
def meteor_update(meteor_list, speed=500):
    for meteor_tuple in meteor_list[:]:
        direction = meteor_tuple[1]
        meteor_rect = meteor_tuple[0]
        meteor_rect.move_ip(direction * speed * dt)
        if meteor_rect.top > WINDOW_HEIGHT:
            meteor_list.remove(meteor_tuple)

# Restart the game by resetting variables
def restart_game():
    global score, game_over, ship_rect, laser_list, meteor_list, can_shoot, shoot_time, start_time

    score = 0
    game_over = False
    ship_rect.center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)
    laser_list.clear()
    meteor_list.clear()
    can_shoot = True
    shoot_time = None
    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)
    start_time = pygame.time.get_ticks()  # Reset the game start time

# Load the high score from a file
def load_high_score():
    try:
        with open('./Data/high_score.txt', 'r') as file:
            return int(file.read())
    except FileNotFoundError:
        return 0  # Return 0 if the file does not exist

# Save the high score to a file
def save_high_score():
    with open('./Data/high_score.txt', 'w') as file:
        file.write(str(high_score))

pygame.init()

# Define initial window size
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)

clock = pygame.time.Clock()
pygame.display.set_caption("Meteor Shooter")

ship_surf = pygame.image.load('./Resources/ship.png').convert_alpha()
ship_rect = ship_surf.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))

laser_surf = pygame.image.load('./Resources/laser.png').convert_alpha()
laser_list = []

can_shoot = True
shoot_time = None

meteor_surf = pygame.image.load('./Resources/meteor.png')
meteor_list = []

bg_surf = pygame.image.load('./Resources/background.png').convert()


# Initial background size
bg_surf = pygame.transform.scale(bg_surf, (WINDOW_WIDTH, WINDOW_HEIGHT))

# Function to calculate dynamic font size
def calculate_font_size():
    return int(WINDOW_WIDTH / 35)  # Scaled based on window width

font_size = calculate_font_size()  # Make font size responsive to window width
font = pygame.font.Font('./Resources/subatomic.ttf', font_size)

meteror_timer = pygame.USEREVENT + 1
pygame.time.set_timer(meteror_timer, 500)

laser_sound = pygame.mixer.Sound('./Resources/laser.ogg')
explosion_sound = pygame.mixer.Sound('./Resources/explosion.wav')
background_music = pygame.mixer.Sound('./Resources/music.wav')
background_music.play(loops=-1)

game_over = False
button_width, button_height = 270, 60

quit_button_rect = pygame.Rect(WINDOW_WIDTH / 2 - button_width / 2, WINDOW_HEIGHT / 2 + 60, button_width, button_height)
restart_button_rect = pygame.Rect(WINDOW_WIDTH / 2 - button_width / 2, WINDOW_HEIGHT / 2 + 150, button_width, button_height)
button_color = (255, 0, 0)

# Initialize score, high score, and game start time
score = 0
high_score = load_high_score()  # Load the high score from the file
start_time = pygame.time.get_ticks()  # Set the initial start time for the game

# Initialize the mute state and volume icons
is_muted = False

volume_on_icon = pygame.transform.scale(pygame.image.load('./Resources/volume_on.png').convert_alpha(), (70,70))
volume_off_icon = pygame.transform.scale(pygame.image.load('./Resources/volume_off.png').convert_alpha(), (70,70))

# Position the mute button in the bottom-left corner
mute_button_rect = volume_on_icon.get_rect(bottomleft=(10, WINDOW_HEIGHT - 10))


# Function to scale font size, buttons, and objects dynamically based on window size
# Function to scale assets based on window size while preserving the aspect ratio
def scale_assets():
    global font, quit_button_rect, restart_button_rect, font_size, button_width, button_height, volume_on_icon, volume_off_icon, mute_button_rect
    global ship_surf, laser_surf, meteor_surf
    
    # Scale font size
    font_size = calculate_font_size()
    font = pygame.font.Font('./Resources/subatomic.ttf', font_size)

    # Define a scaling factor for the volume icon
    icon_size = int(WINDOW_WIDTH * 0.055)  # Scale the icon size based on window width

    # Scale the volume icons
    volume_on_icon = pygame.transform.scale(volume_on_icon, (icon_size, icon_size))
    volume_off_icon = pygame.transform.scale(volume_off_icon, (icon_size, icon_size))
    
    # Scale buttons and reposition them dynamically
    button_width = int(WINDOW_WIDTH * 0.2)
    button_height = int(WINDOW_HEIGHT * 0.07)

    # Recalculate button positions based on window size
    quit_button_rect = pygame.Rect(WINDOW_WIDTH / 2 - button_width / 2, WINDOW_HEIGHT / 2 + button_height, button_width, button_height)
    restart_button_rect = pygame.Rect(WINDOW_WIDTH / 2 - button_width / 2, WINDOW_HEIGHT / 2 + button_height * 2 + 30, button_width, button_height)
    mute_button_rect = volume_on_icon.get_rect(bottomleft=(10, WINDOW_HEIGHT - 10))

    # Calculate the scaling factor based on the window width and height, keeping the aspect ratio intact
    scale_factor_width = WINDOW_WIDTH / 1280
    scale_factor_height = WINDOW_HEIGHT / 720
    scale_factor = min(scale_factor_width, scale_factor_height)  # Use the smaller scale factor to preserve the aspect ratio

    # Resize ship based on its original size (99x75) using the scale factor
    ship_surf = pygame.transform.scale(ship_surf, (int(99 * scale_factor), int(75 * scale_factor)))

    # Resize laser based on its original size (13x54) using the scale factor
    laser_surf = pygame.transform.scale(laser_surf, (int(13 * scale_factor), int(54 * scale_factor)))

    # Resize meteor based on its original size (101x84) using the scale factor
    meteor_surf = pygame.transform.scale(meteor_surf, (int(101 * scale_factor), int(84 * scale_factor)))



# Main game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_high_score()  # Save the high score when quitting
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
            if can_shoot:
                laser_rect = laser_surf.get_rect(midbottom=ship_rect.midtop)
                laser_list.append(laser_rect)

                can_shoot = False
                shoot_time = pygame.time.get_ticks()
                laser_sound.play()

        if event.type == meteror_timer and not game_over:
            rand_x_pos = randint(-100, WINDOW_WIDTH + 100)
            rand_y_pos = randint(-100, -50)

            meteor_rect = meteor_surf.get_rect(center=(rand_x_pos, rand_y_pos))

            direction = pygame.math.Vector2(uniform(-0.5, 0.5), 1)

            meteor_list.append((meteor_rect, direction))

        if event.type == pygame.MOUSEBUTTONDOWN and game_over:
            if quit_button_rect.collidepoint(event.pos):
                save_high_score()  # Save high score before quitting
                pygame.quit()
                sys.exit()

            if restart_button_rect.collidepoint(event.pos):
                restart_game()

            # Toggle mute when clicking the mute button
            if mute_button_rect.collidepoint(event.pos):
                is_muted = not is_muted  # Toggle mute state
                if is_muted:
                    # Mute all sounds
                    background_music.stop()
                    explosion_sound.set_volume(0)
                    laser_sound.set_volume(0)

                else:
                    # Unmute 
                    background_music.play()
                    explosion_sound.set_volume(1)
                    laser_sound.set_volume(1)

        # Handle window resizing
        if event.type == pygame.VIDEORESIZE:
            WINDOW_WIDTH, WINDOW_HEIGHT = event.size
            display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)

            # Call the function to scale fonts and buttons
            scale_assets()

            # Resize the background
            bg_surf = pygame.transform.scale(bg_surf, (WINDOW_WIDTH, WINDOW_HEIGHT))


    dt = clock.tick(120) / 1000  # Frame rate control

    if not game_over:
        ship_rect.center = pygame.mouse.get_pos()

        laser_update(laser_list)
        can_shoot = laser_timer(can_shoot, 400)
        meteor_update(meteor_list)

        for meteor_tuple in meteor_list[:]:
            meteor_rect = meteor_tuple[0]
            if ship_rect.colliderect(meteor_rect):
                game_over = True
                pygame.mouse.set_visible(True)
                pygame.event.set_grab(False)

        for laser_rect in laser_list[:]:
            for meteor_tuple in meteor_list[:]:
                if laser_rect.colliderect(meteor_tuple[0]):
                    meteor_list.remove(meteor_tuple)
                    laser_list.remove(laser_rect)
                    explosion_sound.play()
                    score += 1  # Increment score when a meteor is destroyed

    display_surface.fill((200, 200, 200))

    # Display resized background
    display_surface.blit(bg_surf, (0, 0))

    display_score()  # Display the Score in the bottom and middle of the screen
    display_time_played()  # Display the time played in the top-right corner
    
    # Display the high score
    high_score = max(high_score,score)
    high_score_text = f"High Score: {high_score}"
    high_score_surf = font.render(high_score_text, True, (255, 255, 255))
    high_score_rect = high_score_surf.get_rect(topleft=(10, 10))  # Position in top-left corner
    display_surface.blit(high_score_surf, high_score_rect)

    # Display meteors and lasers
    for meteor_tuple in meteor_list:
        display_surface.blit(meteor_surf, meteor_tuple[0])
    for rect in laser_list:
        display_surface.blit(laser_surf, rect)

    display_surface.blit(ship_surf, ship_rect)

    if game_over:
        # Save the high score if the current score is greater
        high_score = max(high_score, score)

        game_over_text = "Game Over!"
        game_over_surf = font.render(game_over_text, True, (255, 0, 0))
        game_over_rect = game_over_surf.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
        display_surface.blit(game_over_surf, game_over_rect)

        # Display buttons
        # Display Quit Button
        pygame.draw.rect(display_surface, button_color, quit_button_rect)
        quit_button_text = font.render("Quit", True, (255, 255, 255))
        quit_button_text_rect = quit_button_text.get_rect(center=quit_button_rect.center)
        display_surface.blit(quit_button_text, quit_button_text_rect)

        # Display Restart button
        pygame.draw.rect(display_surface, button_color, restart_button_rect)
        restart_button_text = font.render("Restart", True, (255, 255, 255))
        restart_button_text_rect = restart_button_text.get_rect(center=restart_button_rect.center)
        display_surface.blit(restart_button_text, restart_button_text_rect)

        # Display volume icon (mute button)
        volume_icon = volume_off_icon if is_muted else volume_on_icon
        display_surface.blit(volume_icon, mute_button_rect)

        # Display current score
        text_surf = font.render(f"Score: {score}", True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT - (WINDOW_HEIGHT * 0.1)))  # Updated dynamic position
        display_surface.blit(text_surf, text_rect)
        pygame.draw.rect(display_surface, 'white', text_rect.inflate(30, 40), width=10, border_radius=5)

        # Display time survived
        time_played_text = f"{minutes:02}:{seconds:02}"  # Format as MM:SS
        time_text_surf = font.render(time_played_text, True, (255, 255, 255))
        time_text_rect = time_text_surf.get_rect(topright=(WINDOW_WIDTH - 10, 10))  # Position in top-right corner
        display_surface.blit(time_text_surf, time_text_rect)

    pygame.display.update()
