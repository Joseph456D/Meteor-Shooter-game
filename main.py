import pygame, sys
import json
from random import randint, uniform


# Update the laser list to remove lasers that go off-screen
def laser_update(laser_list, speed=500):
    for rect in laser_list[:]:
        rect.y -= speed * dt
        if rect.bottom < 0:
            laser_list.remove(rect)


# Function to display the score on the screen with dynamic box positioning
def display_score():
    global border_width, inflation_height, inflation_width
    if not game_over:
        text_surf = font.render(f"Score: {score}", True, (255, 255, 255))

        # Dynamically center the score text at the bottom
        text_rect = text_surf.get_rect(
            center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT - (WINDOW_HEIGHT * 0.1))
        )

        # Calculate dynamic border width based on window size, but keep the border_radius fixed at 5
        border_width = int(
            WINDOW_WIDTH * 0.008
        )  # Scale border width based on window width

        # Inflate the text_rect box for padding (still dynamic)
        inflation_width = int(WINDOW_WIDTH * 0.03)  # Scale horizontal padding
        inflation_height = int(WINDOW_HEIGHT * 0.05)  # Scale vertical padding

        # Draw the score box (white border with a rounded corner and radius 5
        pygame.draw.rect(
            display_surface,
            "white",
            text_rect.inflate(inflation_width, inflation_height),
            width=border_width,
            border_radius=5,
        )

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
        time_text_rect = time_text_surf.get_rect(
            topright=(WINDOW_WIDTH - 10, 10)
        )  # Position in top-right corner
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


# Load the high score from a JSON file
def load_high_score():
    try:
        with open("./Data/high_score.json", "r") as file:
            data = json.load(file)  # Load the JSON data
            return data.get(
                "high_score", 0
            )  # Get the high score or return 0 if not found
    except (
        FileNotFoundError,
        json.JSONDecodeError,
    ):  # Handle file not found or invalid JSON
        return 0  # Return 0 if the file does not exist or there is an error


# Save the high score to a JSON file
def save_high_score():
    data = {"high_score": high_score}  # Create a dictionary to store the high score
    try:
        with open("./Data/high_score.json", "w") as file:
            json.dump(data, file, indent=4)  # Write the JSON data to the file
    except IOError as e:
        print(f"Error saving high score: {e}")  # Print an error if saving fails


# Load the settings from a JSON file
def load_settings():
    try:
        with open("./Data/settings.json", "r") as file:
            data = json.load(file)  # Load all settings as a dictionary
            return data  # Return entire dictionary of settings

    except (FileNotFoundError, json.JSONDecodeError):
        return {}  # Return empty dictionary if file not found or JSON invalid


# Save the settings to a JSON file
def save_settings():
    # Create a dictionary to store the settings
    data = {
        "volume": volume,
        "sfx_volume": sfx_volume,
        "music_volume": music_volume,
        "volume_level": volume_level,
        "sfx_volume_level": sfx_volume_level,
        "music_volume_level": music_volume_level,
    }
    try:
        with open("./Data/settings.json", "w") as file:
            json.dump(data, file, indent=4)  # Write the JSON data to the file
    except IOError as e:
        print(f"Error saving settings: {e}")  # Print an error if saving fails


# Start menu handling
def display_start_menu():
    bg_surf = pygame.image.load("./Resources/background.png").convert()
    bg_surf = pygame.transform.scale(bg_surf, (WINDOW_WIDTH, WINDOW_HEIGHT))
    display_surface.blit(bg_surf, (0, 0))

    # Display Start Button
    start_button_text = "Start Game"
    start_button_surf = font.render(start_button_text, True, (255, 255, 255))
    start_button_rect = start_button_surf.get_rect(
        center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)
    )

    # Display Quit Button
    pygame.draw.rect(display_surface, button_color, quit_button_rect, border_radius=10)
    quit_button_text = font.render("Quit", True, (255, 255, 255))
    quit_button_text_rect = quit_button_text.get_rect(center=quit_button_rect.center)
    display_surface.blit(quit_button_text, quit_button_text_rect)

    # Display Settings Button
    pygame.draw.rect(
        display_surface, button_color, settings_button_rect_start, border_radius=10
    )
    settings_button_text = font.render("Settings", True, (255, 255, 255))
    settings_button_text_rect = settings_button_text.get_rect(
        center=settings_button_rect_start.center
    )
    display_surface.blit(settings_button_text, settings_button_text_rect)

    # Draw the start button
    pygame.draw.rect(
        display_surface,
        (0, 128, 255),
        start_button_rect.inflate(20, 20),
        border_radius=10,
    )
    display_surface.blit(start_button_surf, start_button_rect)

    return start_button_rect


# Settings Menu Handling
def display_settings():
    # Draw a translucent overlay
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    display_surface.blit(overlay, (0, 0))

    # Panel for settings
    panel_w = int(WINDOW_WIDTH * 0.7)
    panel_h = int(WINDOW_HEIGHT * 0.7)
    panel_rect = pygame.Rect(
        (WINDOW_WIDTH - panel_w) // 2, (WINDOW_HEIGHT - panel_h) // 2, panel_w, panel_h
    )
    pygame.draw.rect(display_surface, (40, 40, 40), panel_rect, border_radius=8)

    # Title
    title_surf = font.render("Settings", True, (255, 255, 255))
    title_rect = title_surf.get_rect(midtop=(WINDOW_WIDTH / 2, panel_rect.top + 10))
    display_surface.blit(title_surf, title_rect)

    # Layout positions
    left_x = panel_rect.left + int(panel_w * 0.08)
    label_y = title_rect.bottom + 30
    row_spacing = int(panel_h * 0.12)

    global volume_dragging, sfx_dragging, music_dragging, prev_mouse_pressed, volume, sfx_volume, music_volume, volume_level, sfx_volume_level, music_volume_level

    mouse_x, mouse_y = pygame.mouse.get_pos()
    mouse_pressed = pygame.mouse.get_pressed()[0]

    # Master Volume Toggle (icon)
    vol_label = font.render("Master Volume", True, (255, 255, 255))
    vol_label_rect = vol_label.get_rect(topleft=(left_x, label_y))
    display_surface.blit(vol_label, vol_label_rect)

    volume_toggle_rect = pygame.Rect(
        panel_rect.right - int(panel_w * 0.18),
        vol_label_rect.top,
        int(panel_w * 0.12),
        vol_label_rect.height,
    )
    pygame.draw.rect(
        display_surface, (100, 100, 100), volume_toggle_rect, border_radius=6
    )
    volume_state = font.render("ON" if volume else "OFF", True, (255, 255, 255))
    volume_state_rect = volume_state.get_rect(center=volume_toggle_rect.center)
    display_surface.blit(volume_state, volume_state_rect)

    # SFX Toggle
    sfx_label = font.render("SFX", True, (255, 255, 255))
    sfx_label_rect = sfx_label.get_rect(topleft=(left_x, label_y + row_spacing * 2))
    display_surface.blit(sfx_label, sfx_label_rect)

    sfx_toggle_rect = pygame.Rect(
        panel_rect.right - int(panel_w * 0.18),
        sfx_label_rect.top,
        int(panel_w * 0.12),
        sfx_label_rect.height,
    )
    pygame.draw.rect(display_surface, (100, 100, 100), sfx_toggle_rect, border_radius=6)
    sfx_state = font.render("ON" if sfx_volume else "OFF", True, (255, 255, 255))
    sfx_state_rect = sfx_state.get_rect(center=sfx_toggle_rect.center)
    display_surface.blit(sfx_state, sfx_state_rect)

    # Music Toggle
    music_label = font.render("Music", True, (255, 255, 255))
    music_label_rect = music_label.get_rect(topleft=(left_x, label_y + row_spacing * 4))
    display_surface.blit(music_label, music_label_rect)

    music_toggle_rect = pygame.Rect(
        panel_rect.right - int(panel_w * 0.18),
        music_label_rect.top,
        int(panel_w * 0.12),
        music_label_rect.height,
    )
    pygame.draw.rect(
        display_surface, (100, 100, 100), music_toggle_rect, border_radius=6
    )
    music_state = font.render("ON" if music_volume else "OFF", True, (255, 255, 255))
    music_state_rect = music_state.get_rect(center=music_toggle_rect.center)
    display_surface.blit(music_state, music_state_rect)

    # Sliders (SFX and Music)
    slider_w = int(panel_w * 0.55)
    slider_h = 4
    slider_x = left_x
    volume_slider_y = label_y + row_spacing + 12
    sfx_slider_y = label_y + row_spacing * 3 + 12
    music_slider_y = label_y + row_spacing * 5 + 12
    slider_enabled_color = "green"
    slider_disabled_color = "gray"

    # Draw slider lines
    pygame.draw.rect(
        display_surface,
        (160, 160, 160),
        (slider_x, volume_slider_y, slider_w, slider_h),
    )
    pygame.draw.rect(
        display_surface, (160, 160, 160), (slider_x, sfx_slider_y, slider_w, slider_h)
    )
    pygame.draw.rect(
        display_surface, (160, 160, 160), (slider_x, music_slider_y, slider_w, slider_h)
    )

    # Handle sizes
    handle_w, handle_h = 12, 12

    # Volume handle
    volume_handle_x = int(slider_x + volume_level * slider_w) - handle_w // 2
    volume_handle_rect = pygame.Rect(
        volume_handle_x, (volume_slider_y - handle_h // 2) + 1, handle_w, handle_h
    )
    pygame.draw.rect(
        display_surface,
        (slider_enabled_color if volume else slider_disabled_color),
        volume_handle_rect,
        border_radius=3,
    )

    # Volume level
    volume_label = font.render(f"{int(volume_level * 100)}%", True, (255, 255, 255))
    volume_rect = pygame.Rect(
        panel_rect.right - int(panel_w * 0.18),
        volume_handle_rect.top,
        int(panel_w * 0.12),
        volume_handle_rect.height,
    )
    volume_label_rect = volume_label.get_rect(center=volume_rect.center)
    display_surface.blit(volume_label, volume_label_rect)

    # SFX handle
    sfx_handle_x = int(slider_x + sfx_volume_level * slider_w) - handle_w // 2
    sfx_handle_rect = pygame.Rect(
        sfx_handle_x, (sfx_slider_y - handle_h // 2) + 1, handle_w, handle_h
    )
    pygame.draw.rect(
        display_surface,
        (slider_enabled_color if sfx_volume else slider_disabled_color),
        sfx_handle_rect,
        border_radius=3,
    )

    # SFX volume level
    sfx_volume_label = font.render(
        f"{int(sfx_volume_level * 100)}%", True, (255, 255, 255)
    )
    sfx_volume_rect = pygame.Rect(
        panel_rect.right - int(panel_w * 0.18),
        sfx_handle_rect.top,
        int(panel_w * 0.12),
        sfx_handle_rect.height,
    )
    sfx_vol_label_rect = sfx_volume_label.get_rect(center=sfx_volume_rect.center)
    display_surface.blit(sfx_volume_label, sfx_vol_label_rect)

    # Music handle
    music_handle_x = int(slider_x + music_volume_level * slider_w) - handle_w // 2
    music_handle_rect = pygame.Rect(
        music_handle_x, (music_slider_y - handle_h // 2) + 1, handle_w, handle_h
    )
    pygame.draw.rect(
        display_surface,
        (slider_enabled_color if music_volume else slider_disabled_color),
        music_handle_rect,
        border_radius=3,
    )

    # music volume level
    music_volume_label = font.render(
        f"{int(music_volume_level * 100)}%", True, (255, 255, 255)
    )
    music_volume_rect = pygame.Rect(
        panel_rect.right - int(panel_w * 0.18),
        music_handle_rect.top,
        int(panel_w * 0.12),
        music_handle_rect.height,
    )
    music_vol_label_rect = music_volume_label.get_rect(center=music_volume_rect.center)
    display_surface.blit(music_volume_label, music_vol_label_rect)

    # Back Button
    back_w = int(panel_w * 0.18)
    back_h = int(panel_h * 0.12)
    back_rect = pygame.Rect(
        panel_rect.centerx - back_w // 2,
        panel_rect.bottom - back_h - 20,
        back_w,
        back_h,
    )
    pygame.draw.rect(display_surface, button_color, back_rect, border_radius=8)
    back_text = font.render("Back", True, (255, 255, 255))
    back_text_rect = back_text.get_rect(center=back_rect.center)
    display_surface.blit(back_text, back_text_rect)

    # Interaction handling using mouse pressed state and previous pressed state to detect clicks
    clicked = mouse_pressed and not prev_mouse_pressed

    # Toggle master volume
    if clicked and volume_toggle_rect.collidepoint((mouse_x, mouse_y)):
        volume = not volume
        # Apply immediately
        if volume and music_volume:
            music.play(background_music, loops=-1)
            music.set_volume(music_volume_level * volume_level)
        else:
            music.stop()
        # Update SFX channel
        sfx.set_volume(
            sfx_volume_level * volume_level if (sfx_volume and volume) else 0
        )

    # Toggle SFX
    if clicked and sfx_toggle_rect.collidepoint((mouse_x, mouse_y)):
        sfx_volume = not sfx_volume
        sfx.set_volume(
            sfx_volume_level * volume_level if (sfx_volume and volume) else 0
        )

    # Toggle Music
    if clicked and music_toggle_rect.collidepoint((mouse_x, mouse_y)):
        music_volume = not music_volume
        if music_volume and volume:
            if not music.get_busy():
                music.play(background_music, loops=-1)
            music.set_volume(music_volume_level * volume_level)
        else:
            music.stop()

    # Start dragging handles on click
    if clicked and volume_handle_rect.collidepoint((mouse_x, mouse_y)) and volume:
        volume_dragging = True
    if clicked and sfx_handle_rect.collidepoint((mouse_x, mouse_y)) and sfx_volume:
        sfx_dragging = True
    if clicked and music_handle_rect.collidepoint((mouse_x, mouse_y)) and music_volume:
        music_dragging = True

    # Stop dragging when mouse released
    if not mouse_pressed:
        volume_dragging = False
        sfx_dragging = False
        music_dragging = False

    # Update slider values while dragging
    if volume_dragging and mouse_pressed:
        # Clamp within slider
        mx = max(slider_x, min(mouse_x, slider_x + slider_w))
        volume_level = (mx - slider_x) / slider_w
        sfx.set_volume(
            sfx_volume_level * volume_level if (sfx_volume and volume) else 0
        )
        music.set_volume(
            music_volume_level * volume_level if (music_volume and volume) else 0
        )

    if sfx_dragging and mouse_pressed:
        mx = max(slider_x, min(mouse_x, slider_x + slider_w))
        sfx_volume_level = (mx - slider_x) / slider_w
        sfx.set_volume(
            sfx_volume_level * volume_level if (sfx_volume and volume) else 0
        )

    if music_dragging and mouse_pressed:
        mx = max(slider_x, min(mouse_x, slider_x + slider_w))
        music_volume_level = (mx - slider_x) / slider_w
        music.set_volume(
            music_volume_level * volume_level if (music_volume and volume) else 0
        )

    # Handle Back button click
    if clicked and back_rect.collidepoint((mouse_x, mouse_y)):
        # Save settings and return to previous menu
        save_settings()
        global in_settings_menu, in_start_menu
        in_settings_menu = False
        if previous_menu == "start":
            in_start_menu = True
        else:
            in_start_menu = False

    # update prev_mouse_pressed at end
    prev_mouse_pressed = mouse_pressed


pygame.init()

# Define initial window size
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
display_surface = pygame.display.set_mode(
    (WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE
)

clock = pygame.time.Clock()
pygame.display.set_caption("Meteor Shooter")

ship_surf = pygame.image.load("./Resources/ship.png").convert_alpha()
ship_rect = ship_surf.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))

laser_surf = pygame.image.load("./Resources/laser.png").convert_alpha()
laser_list = []

can_shoot = True
shoot_time = None

meteor_surf = pygame.image.load("./Resources/meteor.png")
meteor_list = []

bg_surf = pygame.image.load("./Resources/background.png").convert()

# Initial background size
bg_surf = pygame.transform.scale(bg_surf, (WINDOW_WIDTH, WINDOW_HEIGHT))


# Function to calculate dynamic font size
def calculate_font_size():
    return int(WINDOW_WIDTH / 35)  # Scaled based on window width


font_size = calculate_font_size()  # Make font size responsive to window width
font = pygame.font.Font("./Resources/subatomic.ttf", font_size)

meteror_timer = pygame.USEREVENT + 1
pygame.time.set_timer(meteror_timer, 500)

laser_sound = pygame.mixer.Sound("./Resources/laser.ogg")
explosion_sound = pygame.mixer.Sound("./Resources/explosion.wav")
background_music = pygame.mixer.Sound("./Resources/music.wav")

sfx = pygame.mixer.Channel(0)
music = pygame.mixer.Channel(1)

game_over = False
button_width, button_height = 270, 60

quit_button_rect = pygame.Rect(
    WINDOW_WIDTH / 2 - button_width / 2,
    WINDOW_HEIGHT / 2 + 60,
    button_width,
    button_height,
)
restart_button_rect = pygame.Rect(
    WINDOW_WIDTH / 2 - button_width / 2,
    WINDOW_HEIGHT / 2 + 150,
    button_width,
    button_height,
)
settings_button_rect_start = pygame.Rect(
    WINDOW_WIDTH / 2 - button_width / 2,
    WINDOW_HEIGHT / 2 + 150,
    button_width,
    button_height,
)
settings_button_rect = pygame.Rect(
    WINDOW_WIDTH / 2 - button_width / 2,
    WINDOW_HEIGHT / 2 + 240,
    button_width,
    button_height,
)
button_color = (255, 0, 0)

# Initialize score, high score, and game start time
score = 0
high_score = load_high_score()  # Load the high score from the file
start_time = pygame.time.get_ticks()  # Set the initial start time for the game

settings = load_settings()

volume = settings["volume"]
volume_level = settings["volume_level"]
sfx_volume = settings["sfx_volume"]
sfx_volume_level = settings["sfx_volume_level"]
music_volume = settings["music_volume"]
music_volume_level = settings["music_volume_level"]


# Initialize the volume state
# Update music channel
if volume and music_volume:
    music.play(background_music, loops=-1)
    music.set_volume(music_volume_level * volume_level)
else:
    music.stop()
# Update SFX channel
sfx.set_volume(sfx_volume_level * volume_level if (sfx_volume and volume) else 0)


# Initialize the volume icons
volume_on_icon = pygame.transform.scale(
    pygame.image.load("./Resources/volume_on.png").convert_alpha(), (70, 70)
)
volume_off_icon = pygame.transform.scale(
    pygame.image.load("./Resources/volume_off.png").convert_alpha(), (70, 70)
)


# Function to scale assets (font size, buttons, and objects) based on window size while preserving the aspect ratio
def scale_assets():
    global font, quit_button_rect, restart_button_rect, settings_button_rect, settings_button_rect_start, font_size, button_width, button_height, volume_on_icon, volume_off_icon, mute_button_rect
    global ship_surf, laser_surf, meteor_surf

    # Scale font size
    font_size = calculate_font_size()
    font = pygame.font.Font("./Resources/subatomic.ttf", font_size)

    # Define a scaling factor for the volume icon
    icon_size = int(WINDOW_WIDTH * 0.055)  # Scale the icon size based on window width

    # Scale the volume icons
    volume_on_icon = pygame.transform.scale(volume_on_icon, (icon_size, icon_size))
    volume_off_icon = pygame.transform.scale(volume_off_icon, (icon_size, icon_size))

    # Scale buttons and reposition them dynamically
    button_width = int(WINDOW_WIDTH * 0.2)
    button_height = int(WINDOW_HEIGHT * 0.07)

    # Recalculate button positions based on window size
    quit_button_rect = pygame.Rect(
        WINDOW_WIDTH / 2 - button_width / 2,
        WINDOW_HEIGHT / 2 + button_height,
        button_width,
        button_height,
    )
    restart_button_rect = pygame.Rect(
        WINDOW_WIDTH / 2 - button_width / 2,
        WINDOW_HEIGHT / 2 + button_height * 2 + 30,
        button_width,
        button_height,
    )

    settings_button_rect_start = pygame.Rect(
        WINDOW_WIDTH / 2 - button_width / 2,
        WINDOW_HEIGHT / 2 + button_height * 2 + 30,
        button_width,
        button_height,
    )
    settings_button_rect = pygame.Rect(
        WINDOW_WIDTH / 2 - button_width / 2,
        WINDOW_HEIGHT / 2 + button_height * 3 + 60,
        button_width,
        button_height,
    )
    mute_button_rect = volume_on_icon.get_rect(bottomleft=(10, WINDOW_HEIGHT - 10))

    # Calculate the scaling factor based on the window width and height, keeping the aspect ratio intact
    scale_factor_width = WINDOW_WIDTH / 1280
    scale_factor_height = WINDOW_HEIGHT / 720
    scale_factor = min(
        scale_factor_width, scale_factor_height
    )  # Use the smaller scale factor to preserve the aspect ratio

    # Resize ship based on its original size (99x75) using the scale factor
    ship_surf = pygame.transform.scale(
        ship_surf, (int(99 * scale_factor), int(75 * scale_factor))
    )

    # Resize laser based on its original size (13x54) using the scale factor
    laser_surf = pygame.transform.scale(
        laser_surf, (int(13 * scale_factor), int(54 * scale_factor))
    )

    # Resize meteor based on its original size (101x84) using the scale factor
    meteor_surf = pygame.transform.scale(
        meteor_surf, (int(101 * scale_factor), int(84 * scale_factor))
    )


# Main game loop
in_start_menu = True  # Variable to track whether we're in the start menu
in_settings_menu = False  # Variable to track whether we're in the settings menu
# Settings menu interaction state
previous_menu = "start"  # track where to return after closing settings
volume_dragging = False
sfx_dragging = False
music_dragging = False
prev_mouse_pressed = False

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_high_score()  # Save the high score when quitting
            save_settings()  # Save the settngs when quitting
            pygame.quit()
            sys.exit()

        # Handle window resizing
        if event.type == pygame.VIDEORESIZE:
            WINDOW_WIDTH, WINDOW_HEIGHT = event.size
            display_surface = pygame.display.set_mode(
                (WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE
            )

            # Call the function to scale fonts and buttons
            scale_assets()

            # Resize the background
            bg_surf = pygame.transform.scale(bg_surf, (WINDOW_WIDTH, WINDOW_HEIGHT))

        if in_start_menu:
            # Handle Start Menu logic
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Start Game button clicked
                start_button_rect = display_start_menu()
                if start_button_rect.collidepoint(event.pos):
                    in_start_menu = False  # Start the game

                if settings_button_rect_start.collidepoint(event.pos):
                    previous_menu = "start"
                    in_start_menu = False
                    in_settings_menu = True
                    display_settings()

                if quit_button_rect.collidepoint(event.pos):
                    save_high_score()  # Save high score before quitting
                    save_settings()  # Save settngs when quitting
                    pygame.quit()
                    sys.exit()

        elif not in_settings_menu and not in_start_menu:
            if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                if can_shoot:
                    laser_rect = laser_surf.get_rect(midbottom=ship_rect.midtop)
                    laser_list.append(laser_rect)

                    can_shoot = False
                    shoot_time = pygame.time.get_ticks()
                    sfx.play(laser_sound)

            if event.type == meteror_timer and not game_over:
                rand_x_pos = randint(-100, WINDOW_WIDTH + 100)
                rand_y_pos = randint(-100, -50)

                meteor_rect = meteor_surf.get_rect(center=(rand_x_pos, rand_y_pos))

                direction = pygame.math.Vector2(uniform(-0.5, 0.5), 1)

                meteor_list.append((meteor_rect, direction))

            if event.type == pygame.MOUSEBUTTONDOWN and game_over:
                if quit_button_rect.collidepoint(event.pos):
                    save_high_score()  # Save high score before quitting
                    save_settings()  # Save the settngs when quitting
                    pygame.quit()
                    sys.exit()

                if restart_button_rect.collidepoint(event.pos):
                    restart_game()

                if settings_button_rect.collidepoint(event.pos):
                    previous_menu = "game"
                    in_settings_menu = True
                    display_settings()

    dt = clock.tick(120) / 1000  # Frame rate control

    display_surface.fill((200, 200, 200))

    if in_start_menu:
        # Show the start menu and wait for user input
        display_start_menu()
    elif in_settings_menu:
        display_settings()
    elif not in_settings_menu and not in_start_menu:
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
                        sfx.play(explosion_sound)
                        score += 1  # Increment score when a meteor is destroyed

        # Display resized background
        display_surface.blit(bg_surf, (0, 0))

        display_score()  # Display the Score in the bottom and middle of the screen
        display_time_played()  # Display the time played in the top-right corner

        # Display the high score
        high_score = max(high_score, score)
        high_score_text = f"High Score: {high_score}"
        high_score_surf = font.render(high_score_text, True, (255, 255, 255))
        high_score_rect = high_score_surf.get_rect(
            topleft=(10, 10)
        )  # Position in top-left corner
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
            game_over_rect = game_over_surf.get_rect(
                center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)
            )
            display_surface.blit(game_over_surf, game_over_rect)

            # Display buttons
            # Display Quit Button
            pygame.draw.rect(
                display_surface, button_color, quit_button_rect, border_radius=5
            )
            quit_button_text = font.render("Quit", True, (255, 255, 255))
            quit_button_text_rect = quit_button_text.get_rect(
                center=quit_button_rect.center
            )
            display_surface.blit(quit_button_text, quit_button_text_rect)

            # Display Restart button
            pygame.draw.rect(
                display_surface, button_color, restart_button_rect, border_radius=5
            )
            restart_button_text = font.render("Restart", True, (255, 255, 255))
            restart_button_text_rect = restart_button_text.get_rect(
                center=restart_button_rect.center
            )
            display_surface.blit(restart_button_text, restart_button_text_rect)

            # Display Settings button
            pygame.draw.rect(
                display_surface, button_color, settings_button_rect, border_radius=5
            )
            settings_button_text = font.render("Settings", True, (255, 255, 255))
            settings_button_text_rect = settings_button_text.get_rect(
                center=settings_button_rect.center
            )
            display_surface.blit(settings_button_text, settings_button_text_rect)

            # Display current score
            text_surf = font.render(f"Score: {score}", True, (255, 255, 255))
            text_rect = text_surf.get_rect(
                center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 - (WINDOW_HEIGHT * 0.2))
            )  # Updated dynamic position
            display_surface.blit(text_surf, text_rect)
            pygame.draw.rect(
                display_surface,
                "white",
                text_rect.inflate(inflation_width, inflation_height),
                width=border_width,
                border_radius=5,
            )

            # Display time survived
            time_played_text = f"{minutes:02}:{seconds:02}"  # Format as MM:SS
            time_text_surf = font.render(time_played_text, True, (255, 255, 255))
            time_text_rect = time_text_surf.get_rect(
                topright=(WINDOW_WIDTH - 10, 10)
            )  # Position in top-right corner
            display_surface.blit(time_text_surf, time_text_rect)

    pygame.display.update()
