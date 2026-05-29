import pygame
import sys
import random
from pygame.locals import *
import os
import math  # Add this import at the top of your file
import json  # Added for key bindings

# Resource loading system for PyInstaller compatibility
def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

# Debug information - print this first
print("=== Debug Information ===")
print(f"Current working directory: {os.getcwd()}")
print("========================")

# Initialize Pygame and its mixer
pygame.init()
pygame.mixer.init()

# Add font definition here
font = pygame.font.Font(None, 36)  # Default system font, size 36
tutorial_font = pygame.font.Font(None, 48)  # Larger font for tutorial

# Add key bindings dictionary
DEFAULT_KEY_BINDINGS = {
    'jump': pygame.K_w,
    'left': pygame.K_a,
    'right': pygame.K_d,
    'crouch': pygame.K_s,
    'double_jump': pygame.K_SPACE,
    'shoot': pygame.K_f
}

key_bindings = DEFAULT_KEY_BINDINGS.copy()

# Add function to set default key bindings
def set_default_key_bindings():
    global key_bindings
    key_bindings = DEFAULT_KEY_BINDINGS.copy()
    save_key_bindings()  # Save the default bindings

# Add function to save key bindings
def save_key_bindings():
    try:
        with open('key_bindings.json', 'w') as f:
            json.dump({k: v for k, v in key_bindings.items()}, f)
    except Exception as e:
        print(f"Could not save key bindings: {str(e)}")

# Add function to load key bindings
def load_key_bindings():
    # Always use default bindings
    set_default_key_bindings()

# Set up the display
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Sawnick: Out of Love")

# Colors
PINK = (255, 192, 203)
RED_HEART = (255, 0, 0)
BROKEN_HEART_PURPLE = (147, 112, 219)
CUPID_PINK = (255, 182, 193)
WHITE = (255, 255, 255)
ARROW_GOLD = (139, 0, 0)

# Add these global variables at the start of the file, after the other imports and constants
selected_lover_image = None  # Will store which lover image to use
music_muted = False  # Initialize music mute state
music_volume = 0.5  # Music volume 0.0-1.0, used when not muted
is_title_screen = True  # Track if we're on title screen

# Add these new global variables near other game variables
lover_glide_active = False  # True when lover is gliding down
lover_glide_y = -80        # Y position of the gliding lover
lover_glide_x = WINDOW_WIDTH // 2  # X position (center)
lover_landed = False       # True when lover has landed and is waiting for player
lover_contacted = False    # True when player has touched the lover

# Add to global variables:
waiting_for_lover_contact = False

# Game objects
class Heart:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.collected = False
        self.size = 20
        try:
            self.image = pygame.image.load(resource_path('collectHeart.png'))
            self.image = pygame.transform.scale(self.image, (self.size * 2, self.size * 2))
        except Exception as e:
            print(f"Could not load heart sprite: {str(e)}")
            self.image = None

class CupidArrow:
    def __init__(self):
        self.x = WINDOW_WIDTH
        self.y = random.randint(100, 400)
        self.speed = 5

class Platform:
    def __init__(self, x, y, width):
        self.x = x
        self.y = y
        self.width = width
        self.height = 30

class BrokenHeartEnemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.direction = 1
        self.speed = 2
        try:
            self.image = pygame.image.load(resource_path('brokenHeartEnemy.png'))
            self.image = pygame.transform.scale(self.image, (40, 40))
        except Exception as e:
            print(f"Could not load enemy sprite: {str(e)}")
            self.image = None

class ChiliDogBoss:
    def __init__(self):
        self.x = WINDOW_WIDTH - 100
        self.y = 300
        self.health = 3
        self.speed = 3
        self.direction = -1
        try:
            self.image = pygame.image.load(resource_path('chiliDog.png'))  # Add this sprite if you have it
            self.image = pygame.transform.scale(self.image, (80, 80))
        except Exception as e:
            print(f"Could not load boss sprite: {str(e)}")
            self.image = None

class JoyfulLover:
    def __init__(self):
        self.x = WINDOW_WIDTH  # Start off-screen
        self.y = 300
        self.image = pygame.image.load(resource_path('joyful_lover.png'))  # Load joyful lover sprite
        self.image = pygame.transform.scale(self.image, (60, 60))
        self.speed = 5  # Speed for sliding into the center

class Projectile:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.speed = 10
        self.direction = direction  # 1 for right, -1 for left
        try:
            self.image = pygame.image.load(resource_path('coinNoBG.png'))
            self.image = pygame.transform.scale(self.image, (30, 30))
            # Flip the image based on direction
            if direction < 0:
                self.image = pygame.transform.flip(self.image, True, False)
        except Exception as e:
            print(f"Could not load projectile sprite: {str(e)}")
            self.image = None
        self.rect = pygame.Rect(x, y, 30, 30)

    def update(self):
        self.x += self.speed * self.direction
        self.rect.x = self.x
        return self.x < 0 or self.x > WINDOW_WIDTH  # Return True if projectile is off screen

# Game objects lists
hearts = [Heart(random.randint(0, WINDOW_WIDTH), random.randint(100, 300)) for _ in range(5)]
arrows = [CupidArrow()]
platforms = [Platform(300, 300, 100), Platform(500, 200, 100)]
enemies = [BrokenHeartEnemy(400, 350)]

# Player properties
player_x = 100
player_y = 400
player_speed = 5
player_jump_power = -15
player_velocity = 0
gravity = 0.8
is_jumping = False
can_double_jump = True  # New variable for double jump
hearts_collected = 0
player_health = 3

# Particle system
particles = []

# Load and play the theme song
try:
    # Load and play the title screen music
    pygame.mixer.music.load(resource_path("SawnickTitleScreen.mp3"))  # Title screen music
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(music_volume)
except Exception as e:
    print(f"Could not load theme song. Error: {str(e)}")

# Game music tracks (will be used when game starts)
game_soundtracks = [
    'Sawnick Out of Love.mp3',
    'Sawnick_ Out of LoveEmoVersion.mp3',
    'Sawnick_ Out of Love Theme 3.0.mp3',
    "The Valentine's Day Game of Love.mp3",
    "Heartbeats in the Loop.mp3",
    "Speed of Love.mp3",
    "Speed of Love (needs work)DONE.mp3"
]

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        try:
            sprite_path = resource_path('sawnick.png')
            print(f"Attempting to load sprite from: {sprite_path}")
            self.image = pygame.image.load(sprite_path)  # Use resource_path
            self.image = pygame.transform.scale(self.image, (40, 40))
        except Exception as e:
            print(f"Could not load player sprite. Error: {str(e)}")
            self.image = pygame.Surface((40, 40))
            self.image.fill(BROKEN_HEART_PURPLE)
        
        self.facing_right = True
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self, keys):
        # Flip the sprite based on direction
        if keys[K_RIGHT]:
            self.facing_right = True
            self.image = pygame.transform.flip(self.image, False, False)
        elif keys[K_LEFT]:
            self.facing_right = False
            self.image = pygame.transform.flip(self.image, True, False)

# Create player sprite
player = Player(100, 400)

# Game variables
current_level = 1
boss_fight = False
final_victory = False
boss = None
lover = None
victory_timer = 0
victory_duration = 2000  # Show victory screen for 2 seconds
can_take_damage = True  # New flag to control damage
level_transitioning = False  # New flag to control level transition
victory_screen_active = False  # New flag for victory screen
ending_sequence_started = False  # Prevents post-boss cutscene loop

# First, update the game variables section to include the second companion
companion1 = None
companion2 = None
has_companion1 = False
has_companion2 = False

# Add this new function for the second companion cutscene
def play_companion2_cutscene():
    global companion2, has_companion2
    
    try:
        cutscene_image = pygame.image.load(resource_path('companion2cutscene.png'))
        # Make the image wider by using an 18:9 aspect ratio
        cutscene_image = pygame.transform.scale(cutscene_image, (800, 350))  # 800 width, height calculated for 18:9
    except Exception as e:
        print(f"Could not load cutscene image: {str(e)}")
        return
    
    # Create larger font for the announcement text
    announcement_font = pygame.font.Font(None, 48)
    announcement_text = announcement_font.render("Knuckles has joined the party!", True, RED_HEART)
    text_rect = announcement_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT - 100))
    
    start_time = pygame.time.get_ticks()
    duration = 5000  # 5 seconds in milliseconds
    
    while pygame.time.get_ticks() - start_time < duration:
        screen.fill(PINK)
        
        # Center the cutscene image
        screen.blit(cutscene_image, 
                   (WINDOW_WIDTH//2 - cutscene_image.get_width()//2,
                    WINDOW_HEIGHT//2 - cutscene_image.get_height()//2))
        
        # Draw the announcement text below the image
        screen.blit(announcement_text, text_rect)
        
        pygame.display.flip()
        clock.tick(60)
        
        # Handle quit events during cutscene
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
    
    # Create second companion after cutscene
    companion2 = Companion(player_x - 80, player_y, 'knuckles.png')  # Pass the knuckles image name
    has_companion2 = True

# Modify the original companion cutscene function name to be more specific
def play_companion1_cutscene():
    global companion1, has_companion1
    
    try:
        cutscene_image = pygame.image.load(resource_path('companion1cutscene.png'))
        # Make the image wider by using an 18:9 aspect ratio
        cutscene_image = pygame.transform.scale(cutscene_image, (700, 350))  # 700 width, height calculated for 18:9
    except Exception as e:
        print(f"Could not load cutscene image: {str(e)}")
        return
    
    # Create larger font for the announcement text
    announcement_font = pygame.font.Font(None, 48)
    announcement_text = announcement_font.render("Tails has joined the party!", True, RED_HEART)
    text_rect = announcement_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT - 100))
    
    start_time = pygame.time.get_ticks()
    duration = 5000  # 5 seconds in milliseconds
    
    while pygame.time.get_ticks() - start_time < duration:
        screen.fill(PINK)
        
        # Center the cutscene image
        screen.blit(cutscene_image, 
                   (WINDOW_WIDTH//2 - cutscene_image.get_width()//2,
                    WINDOW_HEIGHT//2 - cutscene_image.get_height()//2))
        
        # Draw the announcement text below the image
        screen.blit(announcement_text, text_rect)
        
        pygame.display.flip()
        clock.tick(60)
        
        # Handle quit events during cutscene
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
    
    # Create first companion after cutscene
    companion1 = Companion(player_x - 40, player_y)
    has_companion1 = True

# Modify the Companion class to accept an image parameter
class Companion:
    def __init__(self, x, y, image_name='tails.png'):
        try:
            self.image = pygame.image.load(resource_path(image_name))
            self.image = pygame.transform.scale(self.image, (40, 40))
        except Exception as e:
            print(f"Could not load companion sprite: {str(e)}")
            self.image = pygame.Surface((40, 40))
            self.image.fill(CUPID_PINK)
        
        self.x = x
        self.y = y
        self.target_x = x
        self.target_y = y
        self.speed = 4  # Slightly slower than player

    def update(self, target_x, target_y):
        # Move towards player with a slight delay
        dx = target_x - self.x - 40  # Stay 40 pixels behind player
        dy = target_y - self.y
        
        # Calculate distance
        distance = math.sqrt(dx * dx + dy * dy)
        
        # Only move if we're more than 5 pixels away from target
        if distance > 5:
            # Normalize direction and multiply by speed
            self.x += (dx / distance) * self.speed
            self.y += (dy / distance) * self.speed

# Add this new function for the companion cutscene
def play_companion_cutscene():
    global companion, has_companion
    
    try:
        cutscene_image = pygame.image.load(resource_path('companion1cutscene.png'))
        cutscene_image = pygame.transform.scale(cutscene_image, (400, 300))
    except Exception as e:
        print(f"Could not load cutscene image: {str(e)}")
        return
    
    # Create larger font for the announcement text
    announcement_font = pygame.font.Font(None, 48)
    announcement_text = announcement_font.render("Tails has joined the party!", True, RED_HEART)
    text_rect = announcement_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT - 100))
    
    start_time = pygame.time.get_ticks()
    duration = 5000  # 5 seconds in milliseconds
    
    while pygame.time.get_ticks() - start_time < duration:
        screen.fill(PINK)
        
        # Center the cutscene image
        screen.blit(cutscene_image, 
                   (WINDOW_WIDTH//2 - cutscene_image.get_width()//2,
                    WINDOW_HEIGHT//2 - cutscene_image.get_height()//2))
        
        # Draw the announcement text below the image
        screen.blit(announcement_text, text_rect)
        
        pygame.display.flip()
        clock.tick(60)
        
        # Handle quit events during cutscene
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
    
    # Create companion after cutscene
    companion = Companion(player_x - 40, player_y)
    has_companion = True

def generate_new_level(level_number):
    global hearts, platforms, enemies, victory_screen_active
    
    # Set victory_screen_active to False when generating a new level
    victory_screen_active = False
    
    # First generate platforms
    platforms = [Platform(random.randint(200, WINDOW_WIDTH-200), random.randint(200, 400), 100) for _ in range(3)]
    
    # Generate hearts near platforms or at reachable heights
    hearts = []
    for _ in range(5):
        # 70% chance to place heart near a platform
        if random.random() < 0.7 and platforms:
            platform = random.choice(platforms)
            heart_x = random.randint(int(platform.x), int(platform.x + platform.width))
            heart_y = platform.y - 50  # Place heart above platform
        else:
            # Place heart at a jumpable height
            heart_x = random.randint(0, WINDOW_WIDTH)
            heart_y = random.randint(200, 350)  # Adjusted height range to be reachable
        
        hearts.append(Heart(heart_x, heart_y))
    
    # Generate enemies
    if level_number <= 3:  # Regular levels
        enemies = [BrokenHeartEnemy(random.randint(300, WINDOW_WIDTH-100), 350) for _ in range(level_number)]

def reset_game():
    global player_x, player_y, player_health, hearts_collected
    global current_level, boss_fight, final_victory, boss, lover
    global hearts, platforms, enemies, victory_timer
    global companion1, companion2, has_companion1, has_companion2
    global projectiles, is_title_screen
    global ending_sequence_started  # Add this line
    global arrows  # Add this line to ensure arrows are reset
    
    # Reset player
    player_x = 100
    player_y = 400
    player_health = 3
    hearts_collected = 0
    
    # Reset companions
    companion1 = None
    companion2 = None
    has_companion1 = False
    has_companion2 = False
    
    # Reset game state
    current_level = 1
    boss_fight = False
    final_victory = False
    boss = None
    lover = None
    victory_timer = 0
    ending_sequence_started = False  # Reset ending sequence state
    
    # Generate first level
    generate_new_level(current_level)
    
    projectiles = []  # Clear all projectiles

    arrows = [CupidArrow()]  # Reset arrows so they show up after restart
    
    # Restart music with a random game track
    try:
        selected_track = random.choice(game_soundtracks)
        pygame.mixer.music.load(resource_path(selected_track))
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0 if music_muted else music_volume)
    except Exception as e:
        print(f"Could not restart music: {str(e)}")

# Add this line to create a clock instance
clock = pygame.time.Clock()

# Load Back2Menu button (shown during gameplay only)
try:
    back2menu_image = pygame.image.load(resource_path('Back2Menu.png'))
    back2menu_image = pygame.transform.scale(back2menu_image, (120, 40))
except Exception as e:
    print(f"Could not load Back2Menu.png: {str(e)}")
    back2menu_image = None
    
print(f"back2menu_image value after loading: {back2menu_image}")

# Load settings button (underneath Back2Menu during gameplay)
try:
    settings_btn_image = pygame.image.load(resource_path('settings.png'))
    settings_btn_image = pygame.transform.scale(settings_btn_image, (40, 40))
except Exception as e:
    print(f"Could not load settings.png: {str(e)}")
    settings_btn_image = None

# Game loop
running = True
game_over = False
death_count = 0  # Easter egg: 3 game overs in a row (no level complete in between) = pride song
PRIDE_EGG_DEATHS = 3  # Number of consecutive deaths before pride song plays

# Add these variables near the other game variables
invulnerability_timer = 0
invulnerability_duration = 1000  # 1 second of invulnerability after getting hit

# Add this to the game variables section
projectiles = []
last_movement_direction = 1  # Track last movement direction (1 for right, -1 for left)

# Add this class definition before the game loop
class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velocity_x = random.uniform(-2, 2)
        self.velocity_y = random.uniform(-2, 0)
        self.lifetime = random.randint(20, 40)  # Frames the particle will live

def display_end_screen():
    font = pygame.font.Font(None, 74)  # Create a font for the end screen
    end_text = font.render("Sawnick Found Love!", True, RED_HEART)
    restart_text = font.render("Press R to Restart", True, RED_HEART)
    
    while True:  # Loop until the user decides to restart or quit
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:  # Restart the game
                    reset_game()  # Call the reset function to restart the game
                    return  # Exit the end screen loop

        # Draw the end screen
        screen.fill(PINK)  # Fill the screen with the background color
        screen.blit(end_text, (WINDOW_WIDTH // 2 - end_text.get_width() // 2, WINDOW_HEIGHT // 2 - 50))
        screen.blit(restart_text, (WINDOW_WIDTH // 2 - restart_text.get_width()//2, WINDOW_HEIGHT // 2 + 50))
        pygame.display.flip()  # Update the display
        clock.tick(60)  # Control the frame rate

def trigger_cutscene(skip_glide=False):
    global final_victory, lover, player_x, boss_fight, selected_lover_image
    
    # Fade out gameplay music smoothly
    try:
        pygame.mixer.music.fadeout(1000)  # Fade out over 1 second
        pygame.time.delay(1000)  # Wait for fadeout to finish
    except Exception as e:
        print(f"Could not fade out gameplay music: {str(e)}")
    
    # Play the victory music with fade-in
    try:
        pygame.mixer.music.load(resource_path("Finally Together no intro.wav"))
        pygame.mixer.music.play(-1, fade_ms=1000)  # Fade in over 1 second
        pygame.mixer.music.set_volume(0 if music_muted else music_volume)
    except Exception as e:
        print(f"Could not load victory music: {str(e)}")
    
    # Create both lover instances
    chosen_lover = TheLover()  # This uses the selected_lover_image from the start
    joyful_lover = JoyfulLover()  # This uses the joyful_lover.png
    
    # --- New: Lover glides from the sky animation ---
    if not skip_glide:
        lover_glide_x = WINDOW_WIDTH // 2
        lover_glide_y = -80  # Start well above the screen
        lover_land_y = WINDOW_HEIGHT // 2 - 30  # Land near center
        glide_speed = 3  # Slow, gentle descent
        
        while lover_glide_y < lover_land_y:
            lover_glide_y += glide_speed
            if lover_glide_y > lover_land_y:
                lover_glide_y = lover_land_y
            screen.fill(PINK)
            # Draw the gliding lover
            if chosen_lover.image:
                screen.blit(chosen_lover.image, (lover_glide_x - 30, lover_glide_y))
            pygame.display.flip()
            clock.tick(60)
        # --- End of gliding animation ---
        # Position both lovers at opposite sides for the next animation
        chosen_lover.x = 0  # Start from left
        chosen_lover.y = lover_land_y
        joyful_lover.x = WINDOW_WIDTH  # Start from right
        joyful_lover.y = lover_land_y
    else:
        # If skipping glide, start both lovers at the correct y position
        lover_land_y = WINDOW_HEIGHT // 2 - 30
        chosen_lover.x = 0
        chosen_lover.y = lover_land_y
        joyful_lover.x = WINDOW_WIDTH
        joyful_lover.y = lover_land_y
    
    # Slide both lovers to the center
    while joyful_lover.x > WINDOW_WIDTH // 2 + 30 and chosen_lover.x < WINDOW_WIDTH // 2 - 30:
        chosen_lover.x += 5  # Move right
        joyful_lover.x -= 5  # Move left
        # Update display
        screen.fill(PINK)
        screen.blit(chosen_lover.image, (chosen_lover.x, chosen_lover.y))
        screen.blit(joyful_lover.image, (joyful_lover.x, joyful_lover.y))
        pygame.display.flip()
        clock.tick(60)

    # Spiral effect with oscillating size and burst into hearts
    for _ in range(30):
        particles.append(Particle(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))

    # Reset positions for spiraling effect
    for angle in range(360):
        # Calculate oscillating sizes
        size_factor = 1 + 0.5 * math.sin(math.radians(angle * 2))
        chosen_size = 60 * size_factor
        joyful_size = 60 * size_factor

        # Update positions for spiraling effect
        chosen_lover.x = WINDOW_WIDTH // 2 + 50 * math.cos(math.radians(angle))
        joyful_lover.x = WINDOW_WIDTH // 2 + 50 * math.sin(math.radians(angle))
        
        # Update display
        screen.fill(PINK)
        chosen_image_scaled = pygame.transform.scale(chosen_lover.image, (int(chosen_size), int(chosen_size)))
        joyful_image_scaled = pygame.transform.scale(joyful_lover.image, (int(joyful_size), int(joyful_size)))
        screen.blit(chosen_image_scaled, (chosen_lover.x - chosen_size // 2, WINDOW_HEIGHT // 2 - chosen_size // 2))
        screen.blit(joyful_image_scaled, (joyful_lover.x - joyful_size // 2, WINDOW_HEIGHT // 2 - joyful_size // 2))
        pygame.display.flip()
        clock.tick(60)

    # Final burst of hearts
    for _ in range(100):
        particles.append(Particle(random.randint(0, WINDOW_WIDTH), random.randint(0, WINDOW_HEIGHT)))

    # Display hearts for a few more seconds
    for _ in range(120):
        screen.fill(PINK)
        for particle in particles:
            pygame.draw.circle(screen, RED_HEART, (int(particle.x), int(particle.y)), 2)
        pygame.display.flip()
        clock.tick(60)

    # Clear the screen after the cutscene
    screen.fill(PINK)
    pygame.display.flip()

    # Load and display the appropriate lovey-dovey image based on the selected lover
    try:
        if selected_lover_image == 'lover.png':
            lovey_dovey_image = pygame.image.load(resource_path('loveyDoveyAmy.png'))
        else:  # selected_lover_image == 'lover2.png'
            lovey_dovey_image = pygame.image.load(resource_path('loveyDoveyShadow.png'))
        
        # Scale the image to a reasonable size while maintaining aspect ratio
        image_width = 400  # Adjust this value as needed
        aspect_ratio = lovey_dovey_image.get_height() / lovey_dovey_image.get_width()
        image_height = int(image_width * aspect_ratio)
        lovey_dovey_image = pygame.transform.scale(lovey_dovey_image, (image_width, image_height))
        
        # Create fonts for the end screen
        end_font = pygame.font.Font(None, 74)
        end_text = end_font.render("Sawnick Found Love!", True, RED_HEART)
        restart_text = end_font.render("Press R to Restart", True, RED_HEART)
        
        # Display loop
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:  # Restart the game
                        # Stop the victory music before resetting
                        pygame.mixer.music.stop()
                        reset_game()
                        return
            
            # Draw everything on the screen
            screen.fill(PINK)
            
            # Draw the lovey-dovey image in the upper portion of the screen
            screen.blit(lovey_dovey_image, (WINDOW_WIDTH//2 - image_width//2, 50))
            
            # Draw the text below the image
            screen.blit(end_text, (WINDOW_WIDTH//2 - end_text.get_width()//2, image_height + 100))
            screen.blit(restart_text, (WINDOW_WIDTH//2 - restart_text.get_width()//2, image_height + 180))
            
            pygame.display.flip()
            clock.tick(60)
        
    except Exception as e:
        print(f"Could not load lovey-dovey image: {str(e)}")
        # Fallback to regular end screen if image loading fails
        display_end_screen()

    final_victory = False
    boss_fight = False

def show_lover_selection():
    global selected_lover_image
    
    # Load both selection screen images
    try:
        lover1_selection = pygame.image.load(resource_path('loverSelectionScreen.jpg'))
        lover1_selection = pygame.transform.scale(lover1_selection, (200, 200))
        lover2_selection = pygame.image.load(resource_path('lover2SelectionScreen.jpg'))
        lover2_selection = pygame.transform.scale(lover2_selection, (200, 200))
    except Exception as e:
        print(f"Could not load lover selection sprites: {str(e)}")
        return 'lover.png'
    
    # Create a surface for the lover selection screen
    selection_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    selection_surface.fill(PINK)
    
    # Draw all content to the selection surface
    # Draw the selection images side by side
    selection_surface.blit(lover1_selection, (WINDOW_WIDTH//4 - 100, WINDOW_HEIGHT//2 - 100))
    selection_surface.blit(lover2_selection, (3*WINDOW_WIDTH//4 - 100, WINDOW_HEIGHT//2 - 100))
    
    # Draw selection text
    title_text = font.render("Choose Your Love Interest!", True, RED_HEART)
    option1_text = font.render("Press 1 for this lover", True, RED_HEART)
    option2_text = font.render("Press 2 for this lover", True, RED_HEART)
    
    selection_surface.blit(title_text, (WINDOW_WIDTH//2 - title_text.get_width()//2, 50))
    selection_surface.blit(option1_text, (WINDOW_WIDTH//4 - option1_text.get_width()//2, WINDOW_HEIGHT//2 + 120))
    selection_surface.blit(option2_text, (3*WINDOW_WIDTH//4 - option2_text.get_width()//2, WINDOW_HEIGHT//2 + 120))
    
    # Start with a white screen
    screen.fill(WHITE)
    pygame.display.flip()
    
    # Fade in the selection screen
    for alpha in range(0, 256, 5):  # Fade from 0 to 255 (transparent to opaque)
        screen.fill(WHITE)  # Start with white background
        selection_surface.set_alpha(alpha)
        screen.blit(selection_surface, (0, 0))
        pygame.display.flip()
        clock.tick(60)
    
    selection_made = False
    while not selection_made:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    selected_lover_image = 'lover.png'
                    selection_made = True
                elif event.key == pygame.K_2:
                    selected_lover_image = 'lover2.png'
                    selection_made = True
    
    return selected_lover_image

# Modify the TheLover class to use the selected image
class TheLover:
    def __init__(self):
        self.x = WINDOW_WIDTH - 100
        self.y = 300
        try:
            self.image = pygame.image.load(resource_path(selected_lover_image))  # Use selected image
            self.image = pygame.transform.scale(self.image, (60, 60))
        except Exception as e:
            print(f"Could not load lover sprite: {str(e)}")
            self.image = None

def show_game_over_screen():
    global death_count
    death_count += 1
    print(f"[Pride egg] Game over #{death_count} (need {PRIDE_EGG_DEATHS} in a row for pride song)")
    try:
        # Easter egg: after PRIDE_EGG_DEATHS game overs in a row, play happy pride song
        if death_count >= PRIDE_EGG_DEATHS:
            pride_loaded = False
            for name in ("happy pride (this is the only lyrics).mp3",):  # comma = tuple of 1, so name is the full filename
                try:
                    pygame.mixer.music.load(resource_path(name))
                    pride_loaded = True
                    print(f"[Pride egg] Playing pride song: {name}")
                    break
                except Exception:
                    pass
            if not pride_loaded:
                print(f"[Pride egg] Pride song file not found (tried happy pride (this is the only lyrics).mp3), playing normal jingle")
                pygame.mixer.music.load(resource_path("gameoverjinglecustom.mp3"))
        else:
            pygame.mixer.music.load(resource_path("gameoverjinglecustom.mp3"))
        pygame.mixer.music.play()
    except Exception as e:
        print(f"Could not play game over music: {str(e)}")
    
    try:
        # Load the game over background and retry button images
        # When pride egg triggers, show happyPride.jpg instead of gameOver.png
        pride_egg_active = (death_count >= PRIDE_EGG_DEATHS)
        if pride_egg_active:
            try:
                game_over_img = pygame.image.load(resource_path('happyPride.jpg'))
                game_over_img = pygame.transform.scale(game_over_img, (int(WINDOW_WIDTH * 0.7), int(WINDOW_HEIGHT * 0.6)))
            except Exception:
                pride_egg_active = False
        if not pride_egg_active:
            game_over_img = pygame.image.load(resource_path('gameOver.png'))
            game_over_img = pygame.transform.scale(game_over_img, (int(WINDOW_WIDTH * 0.6), int(WINDOW_WIDTH * 0.6)))
        retry_button = pygame.image.load(resource_path('anotherTry.png'))
        # Make retry button less tall
        retry_button = pygame.transform.scale(retry_button, (200, 70))
        
        # Create a surface for the fade effect
        fade_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        fade_surface.fill((0, 0, 0))  # Black color
        
        # Fade to black while the jingle plays
        for alpha in range(0, 255, 5):  # Gradually increase alpha
            fade_surface.set_alpha(alpha)
            screen.blit(fade_surface, (0, 0))
            pygame.display.flip()
            pygame.time.delay(20)  # Small delay for smooth fade
        
        # Position the retry button in the center bottom of the screen
        button_x = WINDOW_WIDTH//2 - retry_button.get_width()//2
        button_y = WINDOW_HEIGHT - retry_button.get_height() - 20
        
        # Create a rect for the button
        button_rect = retry_button.get_rect(topleft=(button_x, button_y))
        
        # Fade in the game over images
        for alpha in range(0, 255, 5):  # Gradually increase alpha from 0 to 255
            screen.fill((0, 0, 0))  # Black background
            
            # Create temporary surfaces with current alpha for fade-in effect
            temp_game_over = game_over_img.copy()
            temp_retry_button = retry_button.copy()
            
            # Set alpha for fade-in effect
            temp_game_over.set_alpha(alpha)
            temp_retry_button.set_alpha(alpha)
            
            # Position game over image centered horizontally and vertically with padding
            image_x = WINDOW_WIDTH//2 - game_over_img.get_width()//2
            top_padding = 50  # 50 pixels padding from top
            available_height = button_y - top_padding - game_over_img.get_height()
            image_y = top_padding + (available_height // 2)
            
            # Draw the fading images
            screen.blit(temp_game_over, (image_x, image_y))
            screen.blit(temp_retry_button, (button_x, button_y))
            
            pygame.display.flip()
            clock.tick(60)
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Allow clicking the retry button at any time
                    if button_rect.collidepoint(event.pos):
                        # Stop the music immediately when restarting
                        pygame.mixer.music.stop()
                        reset_game()
                        return
            
            # Draw the game over screen
            screen.fill((0, 0, 0))  # Black background
            
            # Position game over image centered horizontally and vertically with padding
            image_x = WINDOW_WIDTH//2 - game_over_img.get_width()//2
            # Calculate vertical position to be centered between top padding and retry button
            top_padding = 50  # 50 pixels padding from top
            available_height = button_y - top_padding - game_over_img.get_height()
            image_y = top_padding + (available_height // 2)
            
            screen.blit(game_over_img, (image_x, image_y))
            screen.blit(retry_button, (button_x, button_y))
            

            
            pygame.display.flip()
            clock.tick(60)
            
    except Exception as e:
        print(f"Could not load game over images: {str(e)}")
        # If images fail to load, just return to restart the game
        reset_game()
        return

# Add these new functions after the other cutscene functions
def play_kidnapping_cutscene():
    global companion1, companion2, has_companion1, has_companion2
    
    if not (has_companion1 or has_companion2):
        return  # Skip if no companions
    
    # Now proceed with the original kidnapping animation
    try:
        boss = pygame.image.load(resource_path('chiliDog.png'))
        boss = pygame.transform.scale(boss, (100, 100))
    except Exception as e:
        print(f"Could not load boss sprite: {str(e)}")
        boss = pygame.Surface((100, 100))
        boss.fill((139, 69, 19))  # Brown color for placeholder
    
    # Boss enters from right
    boss_x = WINDOW_WIDTH
    while boss_x > WINDOW_WIDTH - 200:
        screen.fill(PINK)
        screen.blit(boss.image if hasattr(boss, 'image') else boss, (boss_x, WINDOW_HEIGHT//2 - 50))
        if has_companion1 and companion1:
            screen.blit(companion1.image, (companion1.x, companion1.y))
        if has_companion2 and companion2:
            screen.blit(companion2.image, (companion2.x, companion2.y))
        pygame.display.flip()
        boss_x -= 5
        clock.tick(60)
    
    # Boss "captures" companions
    if has_companion1:
        while companion1.x < WINDOW_WIDTH:
            companion1.x += 10
            screen.fill(PINK)
            screen.blit(boss.image if hasattr(boss, 'image') else boss, (boss_x, WINDOW_HEIGHT//2 - 50))
            screen.blit(companion1.image, (companion1.x, companion1.y))
            if has_companion2:
                screen.blit(companion2.image, (companion2.x, companion2.y))
            pygame.display.flip()
            clock.tick(60)
    
    if has_companion2:
        while companion2.x < WINDOW_WIDTH:
            companion2.x += 10
            screen.fill(PINK)
            screen.blit(boss.image if hasattr(boss, 'image') else boss, (boss_x, WINDOW_HEIGHT//2 - 50))
            screen.blit(companion2.image, (companion2.x, companion2.y))
            pygame.display.flip()
            clock.tick(60)
    
    # Boss exits with companions
    while boss_x < WINDOW_WIDTH + 100:
        screen.fill(PINK)
        screen.blit(boss.image if hasattr(boss, 'image') else boss, (boss_x, WINDOW_HEIGHT//2 - 50))
        pygame.display.flip()
        boss_x += 5
        clock.tick(60)
    
    # Show the "uh oh" image for 5 seconds after the kidnapping
    try:
        uhoh_image = pygame.image.load(resource_path('uhOh.png'))
        uhoh_image = pygame.transform.scale(uhoh_image, (400, 300))
    except Exception as e:
        print(f"Could not load uh oh image: {str(e)}")
        uhoh_image = pygame.Surface((400, 300))
        uhoh_image.fill((139, 69, 19))  # Brown color for placeholder
    
    # Display uh oh image for 5 seconds
    start_time = pygame.time.get_ticks()
    while pygame.time.get_ticks() - start_time < 5000:  # 5000ms = 5 seconds
        screen.fill(PINK)
        screen.blit(uhoh_image, (WINDOW_WIDTH//2 - 200, WINDOW_HEIGHT//2 - 150))
        pygame.display.flip()
        clock.tick(60)
        
        # Handle quit events during uh oh display
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

def show_choice_screen():
    try:
        # Load the single image for the choice screen
        choice_image = pygame.image.load(resource_path('chiliOrLove.png'))
        choice_image = pygame.transform.scale(choice_image, (400, 300))  # Adjust size as needed
    except Exception as e:
        print(f"Could not load choice image: {str(e)}")
        choice_image = pygame.Surface((400, 300))
        choice_image.fill(PINK)  # Fallback color if image fails to load
    
    choice_made = False
    while not choice_made:
        screen.fill(PINK)
        
        # Draw the choice image slightly higher to avoid overlapping with text
        image_y_position = WINDOW_HEIGHT//2 - choice_image.get_height()//2 - 50  # Move up by 50 pixels
        screen.blit(choice_image, (WINDOW_WIDTH//2 - choice_image.get_width()//2, image_y_position))
        
        # Draw text
        title_text = font.render("What do you really want?", True, RED_HEART)
        love_text = font.render("Press L for Love", True, RED_HEART)
        chili_text = font.render("Press C for Chili Dog", True, RED_HEART)
        instruction_text = font.render("Choose wisely...", True, RED_HEART)
        
        # Position all text elements
        screen.blit(title_text, (WINDOW_WIDTH//2 - title_text.get_width()//2, 50))
        screen.blit(love_text, (WINDOW_WIDTH//4 - love_text.get_width()//2, WINDOW_HEIGHT//2 + 120))
        screen.blit(chili_text, (3*WINDOW_WIDTH//4 - chili_text.get_width()//2, WINDOW_HEIGHT//2 + 120))
        screen.blit(instruction_text, (WINDOW_WIDTH//2 - instruction_text.get_width()//2, WINDOW_HEIGHT - 100))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_l:  # Press L for Love
                    return True
                elif event.key == pygame.K_c:  # Press C for Chili Dog
                    return False

def show_chili_ending():
    try:
        # Fade out gameplay music smoothly
        try:
            pygame.mixer.music.fadeout(1000)  # Fade out over 1 second
            pygame.time.delay(1000)  # Wait for fadeout to finish
        except Exception as e:
            print(f"Could not fade out gameplay music: {str(e)}")
        # Play the chili dog ending music with fade-in
        try:
            pygame.mixer.music.load(resource_path("Chili Dog Delight.mp3"))
            pygame.mixer.music.play(-1, fade_ms=1000)  # Fade in over 1 second
            pygame.mixer.music.set_volume(0 if music_muted else music_volume)
        except Exception as e:
            print(f"Could not load chili dog ending music: {str(e)}")

        ending_image = pygame.image.load(resource_path('hungryEnding.png'))
        ending_image = pygame.transform.scale(ending_image, (400, 300))
    except Exception as e:
        print(f"Could not load ending image: {str(e)}")
        ending_image = pygame.Surface((400, 300))
        ending_image.fill((139, 69, 19))
    
    font = pygame.font.Font(None, 74)
    end_text = font.render("Sawnick Found Love?", True, RED_HEART)
    restart_text = font.render("Press R to Restart", True, RED_HEART)
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    # Stop the chili dog ending music before resetting
                    pygame.mixer.music.stop()
                    reset_game()
                    return
        
        screen.fill(PINK)
        # Move the image up by adjusting its y position
        screen.blit(ending_image, (WINDOW_WIDTH//2 - 200, WINDOW_HEIGHT//2 - 250))  # Changed from -150 to -250
        screen.blit(end_text, (WINDOW_WIDTH//2 - end_text.get_width()//2, WINDOW_HEIGHT//2 + 100))
        screen.blit(restart_text, (WINDOW_WIDTH//2 - restart_text.get_width()//2, WINDOW_HEIGHT//2 + 170))
        pygame.display.flip()
        clock.tick(60)

# Modify the toggle_music function
def toggle_music():
    global music_muted, music_volume, is_title_screen
    music_muted = not music_muted
    
    # Only affect music if we're not on the title screen
    if not is_title_screen:
        pygame.mixer.music.set_volume(0 if music_muted else music_volume)

def show_settings_popup():
    """Small in-game settings popup: volume slider and key rebinding for left, right, jump."""
    global music_volume, key_bindings
    
    popup_w, popup_h = 320, 240
    popup_x = (WINDOW_WIDTH - popup_w) // 2
    popup_y = (WINDOW_HEIGHT - popup_h) // 2
    popup_rect = pygame.Rect(popup_x, popup_y, popup_w, popup_h)
    
    # Slider dimensions
    slider_w, slider_h = 180, 12
    slider_x = popup_x + (popup_w - slider_w) // 2
    slider_y = popup_y + 55
    slider_rect = pygame.Rect(slider_x, slider_y, slider_w, slider_h)
    thumb_w = 16
    
    selected_key = None  # 'left', 'right', or 'jump' when waiting for key press
    slider_dragging = False
    
    small_font = pygame.font.Font(None, 28)
    
    popup_active = True
    while popup_active:
        # Draw dimmed background
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(128)
        screen.blit(overlay, (0, 0))
        
        # Draw popup box
        pygame.draw.rect(screen, (240, 230, 240), popup_rect)
        pygame.draw.rect(screen, RED_HEART, popup_rect, 3)
        
        # Title
        title = small_font.render("Settings", True, RED_HEART)
        screen.blit(title, (popup_x + (popup_w - title.get_width()) // 2, popup_y + 12))
        
        # Volume label and slider
        vol_label = small_font.render("Volume", True, RED_HEART)
        screen.blit(vol_label, (popup_x + (popup_w - vol_label.get_width()) // 2, popup_y + 35))
        pygame.draw.rect(screen, (180, 180, 180), slider_rect)
        thumb_x = slider_x + int((music_volume) * (slider_w - thumb_w))
        pygame.draw.rect(screen, RED_HEART, (thumb_x, slider_y - 2, thumb_w, slider_h + 4))
        
        # Key bindings: left, right, jump
        key_actions = [('left', 'Move Left'), ('right', 'Move Right'), ('jump', 'Jump')]
        key_y = popup_y + 85
        key_rects = {}
        for i, (action, label) in enumerate(key_actions):
            y = key_y + i * 38
            key_name = pygame.key.name(key_bindings[action]).upper()
            text = small_font.render(f"{label}: {key_name}", True, RED_HEART)
            r = pygame.Rect(popup_x + 20, y - 2, popup_w - 40, 28)
            key_rects[action] = r
            if selected_key == action:
                pygame.draw.rect(screen, (255, 200, 200), r)
            pygame.draw.rect(screen, RED_HEART, r, 1)
            screen.blit(text, (popup_x + 25, y))
        
        # Done hint
        done_text = small_font.render("Click outside to close", True, (120, 120, 120))
        screen.blit(done_text, (popup_x + (popup_w - done_text.get_width()) // 2, popup_y + popup_h - 28))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not popup_rect.collidepoint(event.pos):
                    popup_active = False
                elif slider_rect.collidepoint(event.pos):
                    slider_dragging = True
                    # Update volume based on click position
                    rel = (event.pos[0] - slider_x) / max(1, slider_w - thumb_w)
                    music_volume = max(0, min(1, rel))
                    pygame.mixer.music.set_volume(0 if music_muted else music_volume)
                else:
                    for action, _ in key_actions:
                        if key_rects[action].collidepoint(event.pos):
                            selected_key = action
                            break
            elif event.type == pygame.MOUSEBUTTONUP:
                slider_dragging = False
            elif event.type == pygame.MOUSEMOTION:
                if slider_dragging:
                    rel = (event.pos[0] - slider_x) / max(1, slider_w - thumb_w)
                    music_volume = max(0, min(1, rel))
                    pygame.mixer.music.set_volume(0 if music_muted else music_volume)
            elif event.type == pygame.KEYDOWN:
                if selected_key:
                    key_bindings[selected_key] = event.key
                    save_key_bindings()
                    selected_key = None
                elif event.key == pygame.K_ESCAPE:
                    popup_active = False
        
        clock.tick(60)

def show_tutorial_screen():
    tutorial_active = True
    selected_action = None  # Track which action is being changed
    key_pressed = None  # Track the last key pressed
    key_press_timer = 0  # Timer for key press display

    # Load settings image
    try:
        settings_image = pygame.image.load(resource_path('settingsImageNoBG.png'))
        # Scale the image to a reasonable size while maintaining aspect ratio
        # Make it wider but not as tall
        settings_image = pygame.transform.scale(settings_image, (300, 150))
    except Exception as e:
        print(f"Could not load settings image: {str(e)}")
        settings_image = None

    while tutorial_active:
        screen.fill(PINK)
        
        # Movement controls
        move_text = font.render("Movement:", True, RED_HEART)
        
        # Action controls
        action_text = font.render("Actions:", True, RED_HEART)
        
        # Music controls
        music_text = font.render("Music Controls:", True, RED_HEART)
        mute_text = font.render(f"Press M to toggle music: {'Off' if music_muted else 'On'}", True, RED_HEART)
        
        # Return instruction - using smaller font
        return_font = pygame.font.Font(None, 32)  # Smaller font size
        return_text = return_font.render("Press ENTER to return to menu", True, RED_HEART)
        
        # Calculate total height needed for all elements
        total_height = 0
        total_height += 50  # Title space
        total_height += 35  # Movement header
        total_height += 30 * 4  # Movement controls (4 items)
        total_height += 35  # Action header
        total_height += 30 * 2  # Action controls (2 items)
        total_height += 35  # Music header
        total_height += 30  # Music control
        total_height += 60  # Extra padding for key press feedback
        total_height += 60  # Space for return text
        
        # Calculate starting y position to center everything above the image
        image_height = settings_image.get_height() if settings_image else 0
        image_padding = 40  # Increased padding between content and image
        start_y = (WINDOW_HEIGHT - total_height - image_height - image_padding) // 2
        
        # Position all text elements with adjusted spacing
        y_pos = start_y
        
        # Draw title - This is now the only place we draw the title
        title = tutorial_font.render("Settings", True, RED_HEART)
        screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, y_pos))
        y_pos += 50
        
        # Draw movement controls
        screen.blit(move_text, (WINDOW_WIDTH//2 - move_text.get_width()//2, y_pos))
        y_pos += 35
        
        for action in ['jump', 'left', 'crouch', 'right']:
            text_content = f"{pygame.key.name(key_bindings[action]).upper()} - {action.title()} (Press {action[0].upper()} to change)"
            
            if selected_action == action:
                text = font.render(text_content, True, (255, 0, 0))
                highlight = pygame.Surface((text.get_width() + 20, text.get_height() + 10))
                highlight.fill((255, 255, 255, 128))
                screen.blit(highlight, (WINDOW_WIDTH//2 - text.get_width()//2 - 10, y_pos - 5))
            else:
                text = font.render(text_content, True, RED_HEART)
            
            screen.blit(text, (WINDOW_WIDTH//2 - text.get_width()//2, y_pos))
            y_pos += 30
        
        # Draw action controls
        y_pos += 5
        screen.blit(action_text, (WINDOW_WIDTH//2 - action_text.get_width()//2, y_pos))
        y_pos += 35
        
        for action in ['double_jump', 'shoot']:
            text_content = f"{pygame.key.name(key_bindings[action]).upper()} - {action.replace('_', ' ').title()} (Press {action[0].upper()} to change)"
            
            if selected_action == action:
                text = font.render(text_content, True, (255, 0, 0))
                highlight = pygame.Surface((text.get_width() + 20, text.get_height() + 10))
                highlight.fill((255, 255, 255, 128))
                screen.blit(highlight, (WINDOW_WIDTH//2 - text.get_width()//2 - 10, y_pos - 5))
            else:
                text = font.render(text_content, True, RED_HEART)
            
            screen.blit(text, (WINDOW_WIDTH//2 - text.get_width()//2, y_pos))
            y_pos += 30
        
        # Draw music controls
        y_pos += 20
        screen.blit(music_text, (WINDOW_WIDTH//2 - music_text.get_width()//2, y_pos))
        y_pos += 35
        screen.blit(mute_text, (WINDOW_WIDTH//2 - mute_text.get_width()//2, y_pos))
        y_pos += 40  # Add extra space after music controls
        
        # Draw key press feedback if a key was pressed
        if key_pressed and pygame.time.get_ticks() - key_press_timer < 1000:
            # Create a semi-transparent background for the key press message
            key_text = font.render(f"Key pressed: {pygame.key.name(key_pressed).upper()}", True, RED_HEART)
            text_width = key_text.get_width()
            text_height = key_text.get_height()
            
            # Create a background surface for the text
            bg_surface = pygame.Surface((text_width + 40, text_height + 20))
            bg_surface.fill(PINK)  # Match the background color
            bg_surface.set_alpha(200)  # Make it semi-transparent
            
            # Draw the background and text
            screen.blit(bg_surface, (WINDOW_WIDTH//2 - text_width//2 - 20, y_pos))
            screen.blit(key_text, (WINDOW_WIDTH//2 - text_width//2, y_pos + 10))
        
        # Draw settings image at the bottom with padding
        if settings_image:
            image_y = WINDOW_HEIGHT - settings_image.get_height() - 40
            screen.blit(settings_image, (WINDOW_WIDTH//2 - settings_image.get_width()//2, image_y))
            
            # Position return text above the image with more space
            return_y = image_y - 60
            screen.blit(return_text, (WINDOW_WIDTH//2 - return_text.get_width()//2, return_y))
        else:
            screen.blit(return_text, (WINDOW_WIDTH//2 - return_text.get_width()//2, WINDOW_HEIGHT - 50))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    tutorial_active = False
                elif event.key == pygame.K_j:
                    selected_action = 'jump'
                elif event.key == pygame.K_l:
                    selected_action = 'left'
                elif event.key == pygame.K_c:
                    selected_action = 'crouch'
                elif event.key == pygame.K_r:
                    selected_action = 'right'
                elif event.key == pygame.K_d:
                    selected_action = 'double_jump'
                elif event.key == pygame.K_s:
                    selected_action = 'shoot'
                elif event.key == pygame.K_m:
                    toggle_music()
                elif selected_action:
                    # Update the key binding for the selected action
                    key_bindings[selected_action] = event.key
                    save_key_bindings()  # Save the updated key bindings
                    key_pressed = event.key  # Store the pressed key
                    key_press_timer = pygame.time.get_ticks()  # Update timer
                    selected_action = None  # Reset the selected action
        
        clock.tick(60)

def show_credits():
    credits_active = True
    
    # Load Knuckles image
    try:
        knuckles_image = pygame.image.load(resource_path('knucklesCreditsNoGB.png'))
        # Scale the image to a reasonable size while maintaining aspect ratio
        # Make it wider but shorter to prevent stretching
        knuckles_image = pygame.transform.scale(knuckles_image, (300, 120))
    except Exception as e:
        print(f"Could not load Knuckles image: {str(e)}")
        knuckles_image = None
    
    while credits_active:
        screen.fill(PINK)
        
        # Title
        title = tutorial_font.render("Credits", True, RED_HEART)
        screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 50))
        
        # Credits text
        credits = [
            "Coding:",
            "Carson Koenig & Zoey Tepman w/ Cursor AI",
            "",
            "Sprites:",
            "Zoey Tepman",
            "",
            "Music:",
            "Carson & Zoey with Suno AI",
            "",
            "Executive Director:",
            "Zoey Tepman"
        ]
        
        # Calculate spacing for better composition
        # Reserve space for image and back button at bottom
        bottom_space = knuckles_image.get_height() + 80 if knuckles_image else 80
        # Reserve space for title at top
        top_space = 100
        # Calculate available space for credits
        available_height = WINDOW_HEIGHT - top_space - bottom_space
        # Calculate number of non-empty lines
        non_empty_lines = len([line for line in credits if line != ""])
        # Calculate even spacing between lines
        line_spacing = available_height // (non_empty_lines + 1)  # +1 for extra padding
        
        y_pos = top_space  # Start after title space
        
        for line in credits:
            if line == "":  # Skip empty lines in rendering
                continue
                
            # Make role titles (lines that end with ':') bold by using a larger font
            if line.endswith(':'):
                text = tutorial_font.render(line, True, RED_HEART)
            else:
                text = font.render(line, True, RED_HEART)
            
            screen.blit(text, (WINDOW_WIDTH//2 - text.get_width()//2, y_pos))
            y_pos += line_spacing
        
        # Draw Knuckles image at the bottom
        if knuckles_image:
            # Position image at the bottom with some padding
            image_y = WINDOW_HEIGHT - knuckles_image.get_height() - 20  # 20 pixels from bottom
            screen.blit(knuckles_image, (WINDOW_WIDTH//2 - knuckles_image.get_width()//2, image_y))
        
        # Back button - ensure it's always at the bottom with some padding
        back_text = font.render("Press ESC to go back", True, RED_HEART)
        # Position back text above the image
        back_y = WINDOW_HEIGHT - knuckles_image.get_height() - 60 if knuckles_image else WINDOW_HEIGHT - 50
        screen.blit(back_text, (WINDOW_WIDTH//2 - back_text.get_width()//2, back_y))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    credits_active = False

def show_background():
    background_active = True
    
    # Load the background image and scale it proportionally
    try:
        bg_image = pygame.image.load(resource_path('bgInfoTails.png'))
        # Get the original dimensions
        original_width = bg_image.get_width()
        original_height = bg_image.get_height()
        
        # Calculate the scaling factor to fit the height while maintaining aspect ratio
        target_height = WINDOW_HEIGHT * 0.4  # 40% of screen height
        scale_factor = target_height / original_height
        target_width = original_width * scale_factor
        
        # Scale the image proportionally
        bg_image = pygame.transform.scale(bg_image, (int(target_width), int(target_height)))
        image_width = bg_image.get_width()
        image_height = bg_image.get_height()
    except Exception as e:
        print(f"Could not load background image: {str(e)}")
        bg_image = None
        image_width = 0
        image_height = 0
    
    while background_active:
        screen.fill(PINK)
        
        # Title - using regular font instead of tutorial_font for smaller size
        title = font.render("Game Background", True, RED_HEART)
        screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 20))  # Moved up to 20px from top
        
        # Position image in top left, closer to top
        if bg_image:
            image_x = 50  # 50 pixels from left edge
            image_y = 70  # Moved up to 70px from top
            screen.blit(bg_image, (image_x, image_y))
            
            # Start text below the image
            text_y = image_y + image_height + 20  # Reduced padding to 20px
        else:
            text_y = 100
        
        # Create a smaller font for the story text
        story_font = pygame.font.Font(None, 28)  # Smaller font size
        
        # Background story with line breaks to prevent text from running off screen
        story = [
            "Sawnick: Out of Love",
            "",
            "A Valentine's Day themed game featuring everyone's favorite",
            "blue hedgehog in his quest to find true love...",
            "or maybe just a chili dog.",
            "",
            "Will you help Sawnick make the right choice?"
        ]
        
        # Draw text below the image, centered on screen
        y_pos = text_y
        for line in story:
            if line == "":
                y_pos += 15  # Reduced empty line spacing
                continue
            
            text_surface = story_font.render(line, True, RED_HEART)
            # Center the text horizontally on screen
            text_x = WINDOW_WIDTH//2 - text_surface.get_width()//2
            screen.blit(text_surface, (text_x, y_pos))
            y_pos += 25  # Reduced line spacing
        
        # Back button at the bottom
        back_text = font.render("Press ESC to go back", True, RED_HEART)
        screen.blit(back_text, (WINDOW_WIDTH//2 - back_text.get_width()//2, WINDOW_HEIGHT - 50))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    background_active = False

def show_title_screen():
    global selected_lover_image, is_title_screen
    is_title_screen = True
    
    print("=== Debug Information ===")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Looking for sonicMainMenu.png: {os.path.abspath('sonicMainMenu.png')}")
    print("========================")
    
    try:
        # Load title image and scale it to fill the entire screen
        title_image = pygame.image.load(resource_path('sonicMainMenu.png'))
        title_image = pygame.transform.scale(title_image, (WINDOW_WIDTH, WINDOW_HEIGHT))
        print("Successfully loaded title image")
    except Exception as e:
        print(f"Could not load images: {str(e)}")
        title_image = None
    
    # Create buttons - moved left by adding an offset
    button_width = 200
    button_height = 50
    button_x = WINDOW_WIDTH//2 - button_width//2 - 200  # Changed from -150 to -200 to move buttons more to the left
    
    buttons = {
        'play': pygame.Rect(button_x, 350, button_width, button_height),
        'settings': pygame.Rect(button_x, 410, button_width, button_height),
        'credits': pygame.Rect(button_x, 470, button_width, button_height),
        'background': pygame.Rect(button_x, 530, button_width, button_height)
    }
    
    # Create a white surface for fading
    fade_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    fade_surface.fill(WHITE)
    
    title_active = True
    while title_active:
        # Draw title image to fill the entire screen
        if title_image:
            screen.blit(title_image, (0, 0))  # Draw at (0,0) to fill the screen
        
        # Draw buttons on top of the image
        for button_name, button_rect in buttons.items():
            # Make buttons semi-transparent
            s = pygame.Surface((button_width, button_height), pygame.SRCALPHA)
            s.fill((255, 0, 0, 128))  # Red with 50% opacity
            screen.blit(s, button_rect)
            
            # Add white border
            pygame.draw.rect(screen, WHITE, button_rect, 2)
            
            # Button text
            text = font.render(button_name.title(), True, WHITE)
            text_rect = text.get_rect(center=button_rect.center)
            screen.blit(text, text_rect)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                
                if buttons['play'].collidepoint(mouse_pos):
                    is_title_screen = False
                    
                    # First fade to white
                    for alpha in range(0, 256, 5):  # Fade from 0 to 255 (transparent to opaque)
                        # Draw the current frame
                        if title_image:
                            screen.blit(title_image, (0, 0))
                        
                        # Draw buttons
                        for button_name, button_rect in buttons.items():
                            s = pygame.Surface((button_width, button_height), pygame.SRCALPHA)
                            s.fill((255, 0, 0, 128))
                            screen.blit(s, button_rect)
                            pygame.draw.rect(screen, WHITE, button_rect, 2)
                            text = font.render(button_name.title(), True, WHITE)
                            text_rect = text.get_rect(center=button_rect.center)
                            screen.blit(text, text_rect)
                        
                        # Draw the fade surface with current alpha
                        fade_surface.set_alpha(alpha)
                        screen.blit(fade_surface, (0, 0))
                        pygame.display.flip()
                        clock.tick(60)
                    
                    # Start game music when play is pressed
                    try:
                        selected_track = random.choice(game_soundtracks)
                        pygame.mixer.music.load(resource_path(selected_track))
                        pygame.mixer.music.play(-1)
                        pygame.mixer.music.set_volume(0 if music_muted else music_volume)
                    except Exception as e:
                        print(f"Could not load game music: {str(e)}")
                    
                    # Keep the screen white while transitioning
                    screen.fill(WHITE)
                    pygame.display.flip()
                    
                    # Create a temporary surface to hold the lover selection screen
                    temp_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
                    temp_surface.fill(PINK)  # Fill with background color
                    
                    # Draw the lover selection screen to the temporary surface
                    selected_lover_image = show_lover_selection()
                    
                    # Now fade from white to the lover selection screen
                    for alpha in range(255, -1, -5):  # Fade from 255 to 0 (opaque to transparent)
                        screen.fill(WHITE)  # Start with white background
                        temp_surface.set_alpha(255 - alpha)  # Inverse of the fade alpha
                        screen.blit(temp_surface, (0, 0))
                        pygame.display.flip()
                        clock.tick(60)
                    
                    title_active = False
                elif buttons['settings'].collidepoint(mouse_pos):
                    show_tutorial_screen()
                elif buttons['credits'].collidepoint(mouse_pos):
                    show_credits()
                elif buttons['background'].collidepoint(mouse_pos):
                    show_background()

# Load key bindings at start
load_key_bindings()

# Show title screen before starting the game
show_title_screen()

# Modify the game loop to use key bindings
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Back to menu button (upper right) - only during gameplay
            if back2menu_image and not game_over:
                back_btn_rect = pygame.Rect(WINDOW_WIDTH - 130, 10, 120, 40)
                settings_btn_rect = pygame.Rect(WINDOW_WIDTH - 55, 55, 40, 40)  # Underneath Back2Menu, closer to edge
                if back_btn_rect.collidepoint(event.pos):
                    death_count = 0  # Reset death count when returning to menu
                    reset_game()
                    try:
                        pygame.mixer.music.load(resource_path("SawnickTitleScreen.mp3"))
                        pygame.mixer.music.play(-1)
                        pygame.mixer.music.set_volume(0 if music_muted else music_volume)
                    except Exception as e:
                        print(f"Could not load title music: {str(e)}")
                    show_title_screen()
                elif settings_btn_image and settings_btn_rect.collidepoint(event.pos):
                    show_settings_popup()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                show_tutorial_screen()  # Show tutorial when ESC is pressed
            elif game_over and event.key == pygame.K_r:
                game_over = False
                reset_game()
            elif not game_over and not level_transitioning:
                if event.key == key_bindings['double_jump']:
                    if not is_jumping:
                        player_velocity = player_jump_power
                        is_jumping = True
                        can_double_jump = True
                        for _ in range(5):
                            particles.append(Particle(player_x + 20, player_y + 40))
                    elif can_double_jump:
                        player_velocity = player_jump_power * 0.8
                        can_double_jump = False
                        is_jumping = True
                        for _ in range(8):
                            particles.append(Particle(player_x + 20, player_y + 40))
                elif event.key == key_bindings['shoot']:
                    # Use last movement direction if not currently moving
                    keys = pygame.key.get_pressed()
                    if keys[key_bindings['left']]:
                        direction = -1
                    elif keys[key_bindings['right']]:
                        direction = 1
                    else:
                        direction = last_movement_direction
                    
                    # Adjust spawn position based on direction
                    spawn_x = player_x + 20 if direction > 0 else player_x - 20
                    new_projectile = Projectile(spawn_x, player_y + 20, direction)
                    projectiles.append(new_projectile)
                elif event.key == pygame.K_m:  # Press M to mute/unmute
                    toggle_music()

    if game_over:
        show_game_over_screen()
        game_over = False
        continue

    # Player movement using key bindings
    keys = pygame.key.get_pressed()
    if keys[key_bindings['left']]:
        player_x -= player_speed
        last_movement_direction = -1  # Update last movement direction
    if keys[key_bindings['right']]:
        player_x += player_speed
        last_movement_direction = 1  # Update last movement direction
    if keys[key_bindings['jump']] and not is_jumping:
        player_velocity = player_jump_power
        is_jumping = True
        can_double_jump = True
        for _ in range(5):
            particles.append(Particle(player_x + 20, player_y + 40))

    # Screen wrapping (Pac-Man style)
    if player_x < -40:  # If player goes off left side
        player_x = WINDOW_WIDTH  # Wrap to right side
    elif player_x > WINDOW_WIDTH:  # If player goes off right side
        player_x = -40  # Wrap to left side

    # Apply gravity
    player_velocity += gravity
    player_y += player_velocity

    # Ground collision
    if player_y > 400:
        player_y = 400
        player_velocity = 0
        is_jumping = False
        can_double_jump = True  # Reset double jump when landing

    # Platform collision
    for platform in platforms:
        if (player_y + 40 >= platform.y and player_y < platform.y + platform.height and
            player_x + 40 > platform.x and player_x < platform.x + platform.width):
            if player_velocity > 0:  # Only if falling
                player_y = platform.y - 40
                player_velocity = 0
                is_jumping = False
                can_double_jump = True  # Reset double jump when landing on platform

    # Heart collection and level progression
    all_hearts_collected = True
    for heart in hearts:
        if not heart.collected:
            all_hearts_collected = False
            if (abs(player_x - heart.x) < 30 and abs(player_y - heart.y) < 30):
                heart.collected = True
                hearts_collected += 1
                for _ in range(10):
                    particles.append(Particle(heart.x, heart.y))

    # Victory check and level progression
    if all_hearts_collected and not boss_fight and not final_victory and not ending_sequence_started:
        current_time = pygame.time.get_ticks()
        if victory_timer == 0:
            victory_timer = current_time
        
        # Show victory screen
        if not victory_screen_active:  # Only show the victory screen once
            victory_screen_active = True
            screen.fill(PINK)
            victory_text = font.render("Level Complete!", True, RED_HEART)
            text_rect = victory_text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2))
            screen.blit(victory_text, text_rect)
            pygame.display.flip()
        
        # After delay, progress to next level or choice/boss
        if current_time - victory_timer >= victory_duration:
            level_transitioning = True
            if current_level < 3:
                current_level += 1
                if current_level == 2:
                    play_companion1_cutscene()
                elif current_level == 3:
                    play_companion2_cutscene()
                generate_new_level(current_level)
            else:
                # Add kidnapping cutscene and choice
                play_kidnapping_cutscene()
                choose_love = show_choice_screen()
                if choose_love:
                    boss_fight = True
                    boss = ChiliDogBoss()
                else:
                    show_chili_ending()
                    reset_game()
            victory_timer = 0
            player_x = 100
            player_y = 400
            can_take_damage = False
            level_transitioning = False
            continue

    # Boss fight logic
    if boss_fight and boss:
        current_time = pygame.time.get_ticks()
        
        # Move boss back and forth
        boss.x += boss.speed * boss.direction
        if boss.x > WINDOW_WIDTH - 80 or boss.x < 0:
            boss.direction *= -1
        
        # Boss collision
        boss_rect = pygame.Rect(boss.x, boss.y, 80, 80)
        player_rect = pygame.Rect(player_x, player_y, 40, 40)
        
        if boss_rect.colliderect(player_rect):
            # Check if player is above the boss and falling
            is_above_boss = player_y + 40 <= boss.y + 10 and player_velocity > 0
            
            if is_above_boss:  # Only damage boss if falling from above
                boss.health -= 1
                player_velocity = player_jump_power  # Bounce off boss
                if boss.health <= 0:
                    ending_sequence_started = True  # Mark ending sequence as started
                    print('DEBUG: Ending sequence started (player collision)')
                    # Show defeatedDog.png for 2 seconds
                    try:
                        defeated_dog_img = pygame.image.load(resource_path('defeatedDog.png'))
                        defeated_dog_img = pygame.transform.scale(defeated_dog_img, (415, 360))
                    except Exception as e:
                        print(f'Could not load defeatedDog.png: {str(e)}')
                        defeated_dog_img = None
                    show_time = pygame.time.get_ticks()
                    while pygame.time.get_ticks() - show_time < 3000:
                        screen.fill(PINK)
                        if defeated_dog_img:
                            screen.blit(defeated_dog_img, (WINDOW_WIDTH//2 - 207, WINDOW_HEIGHT//2 - 180))
                        pygame.display.flip()
                        clock.tick(60)
                    boss_fight = False
                    death_count = 0  # Beating the boss cancels the pride-song death streak
                    # Instead of triggering cutscene, start lover glide
                    lover = TheLover()
                    lover_glide_active = True
                    lover_glide_y = -80
                    lover_glide_x = WINDOW_WIDTH // 2
                    lover_landed = False
                    lover_contacted = False
                    arrows.clear()
                    enemies.clear()
            else:
                # Take damage if touching any other part of the boss
                if current_time - invulnerability_timer >= invulnerability_duration:
                    player_health -= 1
                    invulnerability_timer = current_time  # Reset invulnerability timer
                    
                    # Knock player back in the opposite direction they're touching the boss
                    if player_x < boss.x:
                        player_x -= 100  # Knock left further
                    else:
                        player_x += 100  # Knock right further
                    
                    # Also knock player upward slightly
                    player_velocity = player_jump_power * 0.5
                    
                    if player_health <= 0:
                        game_over = True

    # New condition to skip updating arrows and enemies if the boss is defeated
    if not boss_fight:
        # Arrow movement and collision
        for arrow in arrows:
            arrow.x -= arrow.speed
            if arrow.x < -20:
                arrow.x = WINDOW_WIDTH
                arrow.y = random.randint(100, 400)
            # Arrow collision
            if (abs(player_x - arrow.x) < 30 and abs(player_y - arrow.y) < 30):
                player_health -= 1
                arrow.x = WINDOW_WIDTH
                if player_health <= 0:
                    game_over = True

        # Enemy movement
        for enemy in enemies:
            enemy.x += enemy.speed * enemy.direction
            if enemy.x > WINDOW_WIDTH - 40 or enemy.x < 0:
                enemy.direction *= -1
            # Enemy collision
            if (abs(player_x - enemy.x) < 30 and abs(player_y - enemy.y) < 30):
                player_health -= 1
                player_x -= 50 * enemy.direction
                if player_health <= 0:
                    game_over = True

    # Update particles
    for particle in particles[:]:
        particle.x += particle.velocity_x
        particle.y += particle.velocity_y
        particle.lifetime -= 1
        if particle.lifetime <= 0:
            particles.remove(particle)

    # Update player sprite
    player.update(pygame.key.get_pressed())
    player.rect.x = player_x
    player.rect.y = player_y

    # Update companion positions if we have them
    if has_companion1 and companion1:
        companion1.update(player_x, player_y)
    if has_companion2 and companion2:
        companion2.update(player_x - 40, player_y)  # Follow slightly behind the first companion

    # Update and check projectiles
    for projectile in projectiles[:]:  # Use slice copy to safely remove while iterating
        if projectile.update():  # If projectile is off screen
            projectiles.remove(projectile)
            continue
        
        # Check collision with enemies
        for enemy in enemies[:]:  # Use slice copy to safely remove while iterating
            if abs(projectile.x - enemy.x) < 30 and abs(projectile.y - enemy.y) < 30:
                enemies.remove(enemy)  # Remove the enemy
                projectiles.remove(projectile)  # Remove the projectile
                break
        
        # Check collision with boss
        if boss_fight and boss and projectile in projectiles:
            if (abs(projectile.x - boss.x) < 60 and abs(projectile.y - boss.y) < 60):
                boss.health -= 1
                projectiles.remove(projectile)
                if boss.health <= 0:
                    ending_sequence_started = True  # Mark ending sequence as started
                    print('DEBUG: Ending sequence started (projectile collision)')
                    # Show defeatedDog.png for 2 seconds
                    try:
                        defeated_dog_img = pygame.image.load(resource_path('defeatedDog.png'))
                        defeated_dog_img = pygame.transform.scale(defeated_dog_img, (415, 360))
                    except Exception as e:
                        print(f'Could not load defeatedDog.png: {str(e)}')
                        defeated_dog_img = None
                    show_time = pygame.time.get_ticks()
                    while pygame.time.get_ticks() - show_time < 3000:
                        screen.fill(PINK)
                        if defeated_dog_img:
                            screen.blit(defeated_dog_img, (WINDOW_WIDTH//2 - 207, WINDOW_HEIGHT//2 - 180))
                        pygame.display.flip()
                        clock.tick(60)
                    boss_fight = False
                    death_count = 0  # Beating the boss cancels the pride-song death streak
                    lover = TheLover()
                    lover_glide_active = True
                    lover_glide_y = -80
                    lover_glide_x = WINDOW_WIDTH // 2
                    lover_landed = False
                    lover_contacted = False
                    arrows.clear()
                    enemies.clear()

    # Drawing
    screen.fill(PINK)
    
    # Draw platforms (love letters)
    for platform in platforms:
        pygame.draw.rect(screen, WHITE, (platform.x, platform.y, platform.width, platform.height))
        pygame.draw.rect(screen, RED_HEART, (platform.x + 2, platform.y + 2, platform.width - 4, platform.height - 4))

    # Draw hearts
    for heart in hearts:
        if not heart.collected:
            if heart.image:
                screen.blit(heart.image, (int(heart.x - heart.size), int(heart.y - heart.size)))
            else:
                pygame.draw.circle(screen, RED_HEART, (int(heart.x), int(heart.y)), heart.size)

    # Draw arrows
    for arrow in arrows:
        # Draw arrow shaft (thicker and gold)
        pygame.draw.line(screen, ARROW_GOLD, (arrow.x, arrow.y), (arrow.x - 40, arrow.y), 5)
        # Draw arrow head (larger and gold)
        pygame.draw.polygon(screen, ARROW_GOLD, [
            (arrow.x - 40, arrow.y - 8),
            (arrow.x - 55, arrow.y),
            (arrow.x - 40, arrow.y + 8)
        ])

    # Draw enemies
    for enemy in enemies:
        if enemy.image:
            # Flip the enemy sprite based on direction
            if enemy.direction < 0:
                flipped_image = pygame.transform.flip(enemy.image, True, False)
                screen.blit(flipped_image, (enemy.x, enemy.y))
            else:
                screen.blit(enemy.image, (enemy.x, enemy.y))
        else:
            pygame.draw.rect(screen, BROKEN_HEART_PURPLE, (enemy.x, enemy.y, 40, 40))

    # Draw particles
    for particle in particles:
        pygame.draw.circle(screen, RED_HEART, (int(particle.x), int(particle.y)), 2)

    # Draw projectiles
    for projectile in projectiles:
        if projectile.image:
            screen.blit(projectile.image, (projectile.x, projectile.y))
        else:
            pygame.draw.circle(screen, RED_HEART, (int(projectile.x), int(projectile.y)), 5)

    # Draw player sprite instead of rectangle
    screen.blit(player.image, (player_x, player_y))

    # Draw ground
    pygame.draw.rect(screen, RED_HEART, (0, 440, WINDOW_WIDTH, 160))

    # Draw HUD
    hearts_text = font.render(f'Hearts: {hearts_collected}', True, RED_HEART)
    health_text = font.render(f'Health: {player_health}', True, RED_HEART)
    screen.blit(hearts_text, (10, 10))
    screen.blit(health_text, (10, 50))

    # Draw boss or lover
    if boss_fight and boss:
        if boss.image:
            screen.blit(boss.image, (boss.x, boss.y))
        else:
            pygame.draw.rect(screen, (139, 69, 19), (boss.x, boss.y, 80, 80))  # Brown rectangle for boss
        # Draw boss health
        boss_health_text = font.render(f'Boss HP: {boss.health}', True, RED_HEART)
        screen.blit(boss_health_text, (WINDOW_WIDTH - 200, 10))

    # Draw level counter
    level_text = font.render(f'Level: {current_level}/3', True, RED_HEART)
    screen.blit(level_text, (WINDOW_WIDTH - 200, 50))

    # Draw companions if we have them (draw after player)
    if has_companion1 and companion1:
        screen.blit(companion1.image, (companion1.x, companion1.y))
    if has_companion2 and companion2:
        screen.blit(companion2.image, (companion2.x, companion2.y))

    # After boss_fight logic, add lover glide logic
    if lover_glide_active and lover:
        # Glide lover down
        glide_speed = 3
        lover_land_y = 440 - 60  # Floor y minus lover height
        lover_glide_y += glide_speed
        if lover_glide_y >= lover_land_y:
            lover_glide_y = lover_land_y
            lover_landed = True
        # Check for player contact if landed
        if lover_landed:
            lover_rect = pygame.Rect(lover_glide_x - 30, lover_glide_y, 60, 60)
            player_rect = pygame.Rect(player_x, player_y, 40, 40)
            if lover_rect.colliderect(player_rect):
                lover_contacted = True
        # If player has contacted lover, trigger cutscene
        if lover_contacted:
            lover_glide_active = False
            trigger_cutscene(skip_glide=True)

    # In the drawing section, after drawing the boss, draw the lover if gliding/landed
    if lover_glide_active and lover:
        if lover.image:
            screen.blit(lover.image, (lover_glide_x - 30, lover_glide_y))

    # Draw Back2Menu button in upper right (during gameplay only, on top of everything)
    if back2menu_image:
        back_btn_rect = pygame.Rect(WINDOW_WIDTH - 130, 10, 120, 40)
        screen.blit(back2menu_image, (back_btn_rect.x, back_btn_rect.y))
    # Draw settings button underneath Back2Menu
    if settings_btn_image:
        settings_btn_rect = pygame.Rect(WINDOW_WIDTH - 55, 55, 40, 40)
        screen.blit(settings_btn_image, (settings_btn_rect.x, settings_btn_rect.y))

    # Update display
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
