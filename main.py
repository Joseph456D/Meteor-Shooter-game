import pygame, sys
from random import randint, uniform

# Update the laser list to remove lasers that go off-screen
def laser_update(laser_list, speed=500):
    for rect in laser_list[:]:
        rect.y -= speed * dt
        if rect.bottom < 0:
            laser_list.remove(rect)

# Function to display the score on the screen
def display_score():
    global score_text
    if not game_over:
        score_text = f"Score: {score}"  # Display the number of meteors destroyed
        text_surf = font.render(score_text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT-80))
        display_surface.blit(text_surf, text_rect)
        pygame.draw.rect(display_surface, 'white', text_rect.inflate(30, 40), width=10, border_radius=5)

# Function to display the time played in the top-right corner
def display_time_played():
    global time_played, minutes, seconds
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
    global score, game_over, ship_rect, laser_list, meteor_list, can_shoot, shoot_time, start_time, high_score

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

# Load the top score from a file
def load_high_score():
    try:
        with open('./Data/high_score.txt', 'r') as file:
            return int(file.read())
    except FileNotFoundError:
        return 0  # Return 0 if the file does not exist

# Save the top score to a file
def save_high_score():
    with open('./Data/high_score.txt', 'w') as file:
        file.write(str(high_score))

pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

clock = pygame.time.Clock()
pygame.display.set_caption("Meteor Shooter")

ship_surf = pygame.image.load('./Resources/ship.png').convert_alpha()
ship_rect = ship_surf.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2))

laser_surf = pygame.image.load('./Resources/laser.png').convert_alpha()
laser_list = []

can_shoot = True
shoot_time = None

meteor_surf = pygame.image.load('./Resources/meteor.png')
meteor_list = []

bg_surf = pygame.image.load('./Resources/background.png').convert()

font = pygame.font.Font('./Resources/subatomic.ttf', 50)

meteror_timer = pygame.USEREVENT + 1
pygame.time.set_timer(meteror_timer, 500)

laser_sound = pygame.mixer.Sound('./Resources/laser.ogg')
explosion_sound = pygame.mixer.Sound('./Resources/explosion.wav')
background_music = pygame.mixer.Sound('./Resources/music.wav')
background_music.play(loops=-1)

game_over = False
quit_button_rect = pygame.Rect(WINDOW_WIDTH / 2 - 135, WINDOW_HEIGHT / 2 + 60, 270, 60)
restart_button_rect = pygame.Rect(WINDOW_WIDTH / 2 - 135, WINDOW_HEIGHT / 2 + 155, 270, 60)
button_color = (255, 0, 0)

# Initialize score, top score, and game start time
score = 0
high_score = load_high_score()  # Load the top score from the file
start_time = pygame.time.get_ticks()  # Set the initial start time for the game

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_high_score()  # Save the top score when quitting
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
                save_high_score()  # Save top score before quitting
                pygame.quit()
                sys.exit()

            if restart_button_rect.collidepoint(event.pos):
                restart_game()

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

                    # Increment score when a meteor is destroyed
                    score += 1

    display_surface.fill((200, 200, 200))
    display_surface.blit(bg_surf, (0, 0))

    display_score()
    display_time_played()  # Display the time played in the top-right corner

    # Display the top score
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

        # Save the top score if the current score is greater
        high_score = max(high_score, score)

        game_over_text = "Game Over!"
        game_over_surf = font.render(game_over_text, True, (255, 0, 0))
        game_over_rect = game_over_surf.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
        display_surface.blit(game_over_surf, game_over_rect)

        # Display buttons
        # Display Quit button
        pygame.draw.rect(display_surface, button_color, quit_button_rect)
        quit_button_text = font.render("Quit", True, (255, 255, 255))
        quit_button_text_rect = quit_button_text.get_rect(center=quit_button_rect.center)
        display_surface.blit(quit_button_text, quit_button_text_rect)

        # Display Restart button
        pygame.draw.rect(display_surface, button_color, restart_button_rect)
        restart_button_text = font.render("Restart", True, (255, 255, 255))
        restart_button_text_rect = restart_button_text.get_rect(center=restart_button_rect.center)
        display_surface.blit(restart_button_text, restart_button_text_rect)

        # Display time played
        time_played_text = f"{minutes:02}:{seconds:02}"  # Format as MM:SS
        time_text_surf = font.render(time_played_text, True, (255, 255, 255))
        time_text_rect = time_text_surf.get_rect(topright=(WINDOW_WIDTH - 10, 10))  # Position in top-right corner
        display_surface.blit(time_text_surf, time_text_rect)

        # Display current score
        text_surf = font.render(f"Score: {score}", True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT-80))
        display_surface.blit(text_surf, text_rect)
        pygame.draw.rect(display_surface, 'white', text_rect.inflate(30, 40), width=10, border_radius=5)

        # # Display the top score
        # high_score_text = f"Top Score: {high_score}"
        # high_score_surf = font.render(high_score_text, True, (255, 255, 255))
        # high_score_rect = high_score_surf.get_rect(topleft=(10, 10))  # Position in top-left corner
        # display_surface.blit(high_score_surf, high_score_rect)

    pygame.display.update()