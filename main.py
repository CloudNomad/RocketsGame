import pygame
import sys
import random
import math
import os
import json
import numpy as np
import scipy.io.wavfile as wavfile
from PIL import Image, ImageDraw

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Get screen info for fullscreen
screen_info = pygame.display.Info()
WINDOW_WIDTH = screen_info.current_w
WINDOW_HEIGHT = screen_info.current_h
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (100, 100, 100)

# Set up the display - true fullscreen with hardware acceleration
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), 
                               pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.SCALED)
pygame.display.set_caption("Rocket Game")
clock = pygame.time.Clock()

# Load sounds
shoot_sound = pygame.mixer.Sound('assets/shoot.wav')
explosion_sound = pygame.mixer.Sound('assets/explosion.wav')
powerup_sound = pygame.mixer.Sound('assets/powerup.wav')
laser_sound = pygame.mixer.Sound('assets/laser.wav')

# Set sound effect volumes (0.0 to 1.0)
shoot_sound.set_volume(0.2)  # 20% volume
explosion_sound.set_volume(0.3)  # 30% volume
powerup_sound.set_volume(0.3)  # 30% volume
laser_sound.set_volume(0.2)  # 20% volume

# Load images
def load_image(name, scale=1):
    try:
        image = pygame.image.load(os.path.join('assets', name))
        if scale != 1:
            new_size = (int(image.get_width() * scale), int(image.get_height() * scale))
            image = pygame.transform.scale(image, new_size)
        return image
    except:
        # Fallback to colored rectangle if image not found
        surf = pygame.Surface((30, 50))
        surf.fill(WHITE)
        return surf

def create_asteroid(size, level):
    surface = pygame.Surface((size, size), pygame.SRCALPHA)
    points = []
    for i in range(12):  # More points for smoother shape
        angle = i * (360 / 12)
        radius = size/2 * (0.8 + random.random() * 0.4)
        x = size/2 + radius * math.cos(math.radians(angle))
        y = size/2 + radius * math.sin(math.radians(angle))
        points.append((x, y))
    
    # Create gradient effect
    for r in range(size//2, 0, -1):
        alpha = int(255 * (r / (size/2)))
        # Color based on level
        if level == 4:
            color = (200, 0, 0, alpha)  # Red for level 4
        elif level == 3:
            color = (180, 0, 0, alpha)  # Dark red for level 3
        elif level == 2:
            color = (200, 200, 0, alpha)  # Yellow for level 2
        else:
            color = (150, 150, 150, alpha)  # Gray for level 1
        pygame.draw.circle(surface, color, (size//2, size//2), r)
    
    # Draw main shape
    if level == 4:
        pygame.draw.polygon(surface, (220, 0, 0), points)  # Red for level 4
    elif level == 3:
        pygame.draw.polygon(surface, (200, 0, 0), points)  # Dark red for level 3
    elif level == 2:
        pygame.draw.polygon(surface, (220, 220, 0), points)  # Yellow for level 2
    else:
        pygame.draw.polygon(surface, (180, 180, 180), points)  # Gray for level 1
    
    # Add highlights
    highlight_points = []
    for x, y in points:
        dx = x - size/2
        dy = y - size/2
        length = math.sqrt(dx*dx + dy*dy)
        if length > 0:
            dx = dx / length * 2
            dy = dy / length * 2
        highlight_points.append((x - dx, y - dy))
    pygame.draw.polygon(surface, (200, 200, 200), highlight_points, 1)
    
    # Add craters
    for _ in range(3):
        x = random.randint(size//4, 3*size//4)
        y = random.randint(size//4, 3*size//4)
        r = random.randint(2, size//8)
        pygame.draw.circle(surface, (80, 80, 80), (x, y), r)
    
    return surface

def create_space_background():
    # Create a surface for the background
    background = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    background.fill(BLACK)
    
    # Add stars
    for _ in range(200):
        x = random.randint(0, WINDOW_WIDTH)
        y = random.randint(0, WINDOW_HEIGHT)
        size = random.randint(1, 3)
        brightness = random.randint(100, 255)
        color = (brightness, brightness, brightness)
        pygame.draw.circle(background, color, (x, y), size)
    
    # Add nebula effect
    for _ in range(5):
        x = random.randint(0, WINDOW_WIDTH)
        y = random.randint(0, WINDOW_HEIGHT)
        size = random.randint(100, 300)
        color = (
            random.randint(50, 100),  # R
            random.randint(50, 100),  # G
            random.randint(100, 150),  # B
            30  # Alpha
        )
        for r in range(size, 0, -1):
            alpha = int(30 * (r / size))
            pygame.draw.circle(background, (*color[:3], alpha), (x, y), r)
    
    return background

# Create space background
space_background = create_space_background()

def create_sound_effects():
    sample_rate = 44100
    
    # Shoot sound
    duration = 0.1
    t = np.linspace(0, duration, int(sample_rate * duration))
    shoot = np.sin(2 * np.pi * 440 * t) * np.exp(-10 * t)
    shoot = (shoot * 32767).astype(np.int16)
    wavfile.write('assets/shoot.wav', sample_rate, shoot)
    
    # Explosion sound
    duration = 0.3
    t = np.linspace(0, duration, int(sample_rate * duration))
    explosion = np.random.normal(0, 1, len(t)) * np.exp(-5 * t)
    explosion = (explosion * 32767).astype(np.int16)
    wavfile.write('assets/explosion.wav', sample_rate, explosion)
    
    # Powerup sound
    duration = 0.2
    t = np.linspace(0, duration, int(sample_rate * duration))
    powerup = np.sin(2 * np.pi * 880 * t) * np.exp(-5 * t)
    powerup = (powerup * 32767).astype(np.int16)
    wavfile.write('assets/powerup.wav', sample_rate, powerup)
    
    # Laser sound
    duration = 0.5
    t = np.linspace(0, duration, int(sample_rate * duration))
    laser = np.sin(2 * np.pi * 880 * t) * np.exp(-2 * t)
    laser = (laser * 32767).astype(np.int16)
    wavfile.write('assets/laser.wav', sample_rate, laser)

def create_background_music():
    sample_rate = 44100
    duration = 5.0  # 5 seconds loop
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # Create a simple space-like background music
    notes = [440, 523.25, 659.25, 783.99]  # A4, C5, E5, G5
    music = np.zeros_like(t)
    
    for i, note in enumerate(notes):
        start = i * duration/4
        end = (i + 1) * duration/4
        mask = (t >= start) & (t < end)
        music[mask] = np.sin(2 * np.pi * note * (t[mask] - start)) * 0.3
    
    # Add some space-like effects
    noise = np.random.normal(0, 0.1, len(t))
    music = music + noise
    
    # Fade in/out
    fade = 0.1
    fade_samples = int(fade * sample_rate)
    music[:fade_samples] *= np.linspace(0, 1, fade_samples)
    music[-fade_samples:] *= np.linspace(1, 0, fade_samples)
    
    music = (music * 32767).astype(np.int16)
    wavfile.write('assets/background.wav', sample_rate, music)

def load_high_score():
    try:
        with open('highscore.json', 'r') as f:
            return json.load(f)['high_score']
    except:
        return 0

def save_high_score(score):
    with open('highscore.json', 'w') as f:
        json.dump({'high_score': score}, f)

def show_game_over_screen(score, high_score):
    screen.fill(BLACK)
    font = pygame.font.Font(None, 74)
    text = font.render('GAME OVER', True, WHITE)
    text_rect = text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/3))
    screen.blit(text, text_rect)
    
    font = pygame.font.Font(None, 36)
    score_text = font.render(f'Score: {score}', True, WHITE)
    score_rect = score_text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2))
    screen.blit(score_text, score_rect)
    
    high_score_text = font.render(f'High Score: {high_score}', True, WHITE)
    high_score_rect = high_score_text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2 + 50))
    screen.blit(high_score_text, high_score_rect)
    
    restart_text = font.render('Press SPACE to restart', True, WHITE)
    restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT*2/3))
    screen.blit(restart_text, restart_rect)
    
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    waiting = False

def create_rocket_variations():
    rockets = {}
    
    # Default Rocket (Balanced)
    img = Image.new('RGBA', (60, 100), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Create gradient for rocket body
    for y in range(100):
        alpha = int(255 * (1 - y/100))
        color = (200, 200, 200, alpha)
        draw.line([(30, y), (30, y+1)], fill=color)
    # Rocket body (main cone)
    draw.polygon([(30, 0), (10, 70), (50, 70)], fill=(200, 200, 200))
    # Add metallic shine
    draw.polygon([(30, 0), (20, 15), (40, 15)], fill=(255, 255, 255))
    draw.polygon([(30, 0), (25, 10), (35, 10)], fill=(180, 180, 180))
    # Rocket fins
    draw.polygon([(10, 70), (5, 90), (15, 70)], fill=(150, 150, 150))
    draw.polygon([(50, 70), (45, 70), (55, 90)], fill=(150, 150, 150))
    # Windows
    draw.ellipse([(25, 30), (35, 40)], fill=(0, 191, 255))
    draw.ellipse([(25, 45), (35, 55)], fill=(0, 191, 255))
    img.save('assets/rocket_default.png')
    rockets['default'] = {'speed': 5, 'shoot_delay': 250, 'description': 'Balanced: Good speed and fire rate'}

    # Speed Rocket (Fast but slower fire rate)
    img = Image.new('RGBA', (60, 100), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Sleeker design
    draw.polygon([(30, 0), (15, 60), (45, 60)], fill=(150, 200, 255))
    # Add metallic shine
    draw.polygon([(30, 0), (25, 10), (35, 10)], fill=(200, 220, 255))
    # Smaller fins
    draw.polygon([(15, 60), (10, 80), (20, 60)], fill=(100, 150, 200))
    draw.polygon([(45, 60), (40, 60), (50, 80)], fill=(100, 150, 200))
    # Single window
    draw.ellipse([(25, 30), (35, 40)], fill=(0, 191, 255))
    img.save('assets/rocket_speed.png')
    rockets['speed'] = {'speed': 7, 'shoot_delay': 300, 'description': 'Speed: Faster movement but slower fire rate'}

    # Heavy Rocket (Slower but faster fire rate)
    img = Image.new('RGBA', (60, 100), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Wider design
    draw.polygon([(30, 0), (5, 80), (55, 80)], fill=(255, 150, 150))
    # Add metallic shine
    draw.polygon([(30, 0), (20, 20), (40, 20)], fill=(255, 180, 180))
    # Larger fins
    draw.polygon([(5, 80), (0, 95), (10, 80)], fill=(200, 100, 100))
    draw.polygon([(55, 80), (50, 80), (60, 95)], fill=(200, 100, 100))
    # Multiple windows
    draw.ellipse([(20, 30), (30, 40)], fill=(0, 191, 255))
    draw.ellipse([(30, 30), (40, 40)], fill=(0, 191, 255))
    draw.ellipse([(25, 45), (35, 55)], fill=(0, 191, 255))
    img.save('assets/rocket_heavy.png')
    rockets['heavy'] = {'speed': 3, 'shoot_delay': 200, 'description': 'Heavy: Slower but faster fire rate'}

    return rockets

# Create rocket variations
ROCKET_TYPES = create_rocket_variations()

def show_start_screen():
    screen.fill(BLACK)
    
    # Draw title
    title_font = pygame.font.Font(None, 100)
    title_text = title_font.render('SPACE FRONTIERS', True, WHITE)
    title_rect = title_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//4))
    screen.blit(title_text, title_rect)
    
    # Draw "Press any key" text with flashing effect
    flash_alpha = int(255 * (0.5 + 0.5 * math.sin(pygame.time.get_ticks() / 200)))
    start_font = pygame.font.Font(None, 50)
    start_text = start_font.render('Press any button to start', True, WHITE)
    start_text.set_alpha(flash_alpha)
    start_rect = start_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
    screen.blit(start_text, start_rect)
    
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYUP:
                waiting = False

def show_rocket_selection(rockets):
    selected_rocket = 'default'
    selection_active = True
    
    while selection_active:
        screen.fill(BLACK)
        
        # Draw title
        title_font = pygame.font.Font(None, 80)
        title_text = title_font.render('Select Your Rocket', True, WHITE)
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH//2, 50))
        screen.blit(title_text, title_rect)
        
        # Draw rocket options
        y_pos = 150
        for rocket_type, data in rockets.items():
            # Draw rocket image
            rocket_img = load_image(f'rocket_{rocket_type}.png', 0.5)
            img_rect = rocket_img.get_rect(center=(WINDOW_WIDTH//2, y_pos))
            screen.blit(rocket_img, img_rect)
            
            # Draw rocket name and description
            font = pygame.font.Font(None, 36)
            name_text = font.render(rocket_type.capitalize(), True, WHITE)
            desc_text = font.render(data['description'], True, GRAY)
            
            name_rect = name_text.get_rect(center=(WINDOW_WIDTH//2, y_pos + 60))
            desc_rect = desc_text.get_rect(center=(WINDOW_WIDTH//2, y_pos + 90))
            
            screen.blit(name_text, name_rect)
            screen.blit(desc_text, desc_rect)
            
            # Draw selection indicator
            if rocket_type == selected_rocket:
                pygame.draw.rect(screen, GREEN, (img_rect.left - 10, img_rect.top - 10, 
                                               img_rect.width + 20, img_rect.height + 20), 2)
            
            y_pos += 200
        
        # Draw selection instructions
        font = pygame.font.Font(None, 36)
        instructions = font.render('Use UP/DOWN to select, ENTER to confirm', True, WHITE)
        screen.blit(instructions, (WINDOW_WIDTH//2 - 200, WINDOW_HEIGHT - 50))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    if selected_rocket == 'speed':
                        selected_rocket = 'default'
                    elif selected_rocket == 'heavy':
                        selected_rocket = 'speed'
                elif event.key == pygame.K_DOWN:
                    if selected_rocket == 'default':
                        selected_rocket = 'speed'
                    elif selected_rocket == 'speed':
                        selected_rocket = 'heavy'
                elif event.key == pygame.K_RETURN:
                    selection_active = False
    
    return selected_rocket

def create_powerup(type):
    size = 40  # Increased from 30 to 40
    surface = pygame.Surface((size, size), pygame.SRCALPHA)
    
    # Create glossy background with brighter colors
    for r in range(size//2, 0, -1):
        alpha = int(255 * (r / (size/2)))
        if type == 'shield':
            color = (0, 255, 0, alpha)  # Bright green
        elif type == 'laser':
            color = (0, 191, 255, alpha)  # Bright blue
        else:  # triple_shot
            color = (255, 255, 0, alpha)  # Bright yellow
        pygame.draw.circle(surface, color, (size//2, size//2), r)
    
    # Add bright highlight
    pygame.draw.ellipse(surface, (255, 255, 255, 150), (2, 2, size//3, size//3))
    
    # Add letter based on power-up type
    font = pygame.font.Font(None, 36)  # Larger font
    if type == 'shield':
        letter = 'S'
        color = (0, 255, 0)  # Green
    elif type == 'laser':
        letter = 'L'  # L for Laser
        color = (0, 191, 255)  # Bright blue
    else:  # triple_shot
        letter = 'T'
        color = (255, 255, 0)  # Yellow
    
    # Draw letter with glow effect
    for i in range(3):
        alpha = 255 - i * 50
        text = font.render(letter, True, (*color, alpha))
        text_rect = text.get_rect(center=(size//2, size//2))
        surface.blit(text, text_rect)
    
    # Add pulsing border
    border_color = (*color, 150)
    pygame.draw.circle(surface, border_color, (size//2, size//2), size//2, 2)
    
    return surface

class Enemy(pygame.sprite.Sprite):
    def __init__(self, level=1):
        super().__init__()
        self.level = level
        if level == 1:
            size = 25
            self.health = 1
            self.points = 10
        elif level == 2:
            size = 35
            self.health = 3
            self.points = 20
        elif level == 3:
            size = 45
            self.health = 5
            self.points = 30
        else:  # level 4
            size = 60
            self.health = 10
            self.points = 50
        
        self.original_image = create_asteroid(size, level)
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(WINDOW_WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = random.randrange(1, 4)
        self.speedx = random.randrange(-2, 2)
        self.rotation = 0
        self.rotation_speed = random.randrange(-3, 4)

    def update(self):
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        self.rotation = (self.rotation + self.rotation_speed) % 360
        self.image = pygame.transform.rotate(self.original_image, self.rotation)
        self.rect = self.image.get_rect(center=self.rect.center)
        
        if self.rect.top > WINDOW_HEIGHT or self.rect.left < -25 or self.rect.right > WINDOW_WIDTH + 25:
            self.rect.x = random.randrange(WINDOW_WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(1, 4)

class Player(pygame.sprite.Sprite):
    def __init__(self, rocket_type='default'):
        super().__init__()
        self.rocket_type = rocket_type
        self.original_image = load_image(f'rocket_{rocket_type}.png', 0.5)
        self.image = self.original_image
        self.rect = self.image.get_rect()
        # Start from off-screen right
        self.rect.centerx = WINDOW_WIDTH + 200  # Start further off-screen to the right
        self.rect.centery = WINDOW_HEIGHT // 2  # Center vertically
        
        # Get rocket stats
        rocket_data = ROCKET_TYPES[rocket_type]
        self.speed = rocket_data['speed']
        self.shoot_delay = rocket_data['shoot_delay']
        
        self.last_shot = pygame.time.get_ticks()
        self.lives = 3
        self.shield = False
        self.shield_time = 0
        self.triple_shot = False
        self.speed_boost = False
        self.laser_active = False
        self.power_up_time = 0
        self.original_speed = self.speed
        self.shoot_sound = pygame.mixer.Sound('assets/shoot.wav')
        self.shoot_sound.set_volume(0.2)
        self.shield_surface = pygame.Surface((self.rect.width + 20, self.rect.height + 20), pygame.SRCALPHA)
        self.shield_alpha = 0
        self.shield_alpha_change = 5
        self.active_laser = None
        self.invulnerable = False
        self.invulnerable_time = 0
        self.flash_count = 0
        self.visible = True
        self.flash_delay = 100
        self.last_flash = 0
        self.respawn_delay = 2000
        self.respawn_time = 0
        self.is_respawning = False
        
        # Warp-in animation properties
        self.warp_start_time = pygame.time.get_ticks()
        self.warp_duration = 1500  # 1.5 seconds for smoother animation
        self.is_warping = True
        self.warp_particles = []
        self.original_y = WINDOW_HEIGHT - 10  # Target position
        self.original_size = self.original_image.get_size()
        self.current_scale = 2.5  # Start at 2.5x size
        self.start_x = self.rect.centerx
        self.target_x = WINDOW_WIDTH // 2  # Center of screen

    def update(self):
        current_time = pygame.time.get_ticks()
        
        # Handle warp-in animation
        if self.is_warping:
            warp_progress = (current_time - self.warp_start_time) / self.warp_duration
            
            if warp_progress >= 1.0:
                self.is_warping = False
                self.rect.centerx = self.target_x
                self.rect.bottom = self.original_y
                self.warp_particles.clear()
                self.image = self.original_image  # Reset to original size
                self.rect = self.image.get_rect(center=self.rect.center)
            else:
                # Use continuous sine wave for smooth curved path
                # Horizontal movement from right to center
                current_x = self.start_x + (self.target_x - self.start_x) * warp_progress
                
                # Vertical movement using sine wave
                # Start at center height, curve up, then down to final position
                vertical_offset = math.sin(warp_progress * math.pi) * 200  # Increased curve height
                current_y = (WINDOW_HEIGHT // 2) - vertical_offset + (self.original_y - (WINDOW_HEIGHT // 2)) * warp_progress
                
                self.rect.centerx = current_x
                self.rect.bottom = current_y
                
                # Calculate scale (from 2.5 to 1.0) with easing
                self.current_scale = 2.5 - (1.5 * warp_progress)
                new_size = (int(self.original_size[0] * self.current_scale), 
                          int(self.original_size[1] * self.current_scale))
                self.image = pygame.transform.scale(self.original_image, new_size)
                self.rect = self.image.get_rect(center=self.rect.center)
                
                # Add warp particles
                if random.random() < 0.3:  # 30% chance each frame
                    particle = {
                        'x': self.rect.centerx + random.randint(-20, 20),
                        'y': self.rect.centery + random.randint(-10, 10),
                        'size': random.randint(2, 5),
                        'alpha': 255,
                        'color': (0, 191, 255)  # Cyan color
                    }
                    self.warp_particles.append(particle)
                
                # Update and remove old particles
                for particle in self.warp_particles[:]:
                    particle['alpha'] -= 10
                    if particle['alpha'] <= 0:
                        self.warp_particles.remove(particle)
                
                return  # Skip other updates during warp
        
        # Handle respawn delay
        if self.is_respawning:
            if current_time - self.respawn_time >= self.respawn_delay:
                self.is_respawning = False
                self.invulnerable = True
                self.visible = True
                self.flash_count = 0
                self.last_flash = current_time

        # Handle invulnerability flashing
        if self.invulnerable and not self.is_respawning:
            if current_time - self.last_flash > self.flash_delay:
                self.visible = not self.visible
                self.last_flash = current_time
                self.flash_count += 1
                if self.flash_count >= 6:
                    self.invulnerable = False
                    self.visible = True
                    self.flash_count = 0

        # Only update movement and shooting if not respawning and not warping
        if not self.is_respawning and not self.is_warping:
            # Handle power-up timers
            if self.shield and current_time > self.shield_time:
                self.shield = False
            
            if self.power_up_time > 0 and current_time > self.power_up_time:
                self.triple_shot = False
                self.speed_boost = False
                self.laser_active = False
                if self.active_laser:
                    self.active_laser.kill()
                    self.active_laser = None
                self.speed = self.original_speed
                self.power_up_time = 0

            # Handle movement
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.rect.x -= self.speed
            if keys[pygame.K_RIGHT]:
                self.rect.x += self.speed
            if keys[pygame.K_UP]:
                self.rect.y -= self.speed
            if keys[pygame.K_DOWN]:
                self.rect.y += self.speed

            # Keep player on screen
            self.rect.clamp_ip(screen.get_rect())

            # Handle shooting
            if keys[pygame.K_SPACE]:
                if current_time - self.last_shot > self.shoot_delay:
                    self.shoot()
                    self.last_shot = current_time
                if self.laser_active and not self.active_laser:
                    self.active_laser = Laser(self.rect.centerx, self.rect.top)
                    all_sprites.add(self.active_laser)
            else:
                if self.active_laser:
                    self.active_laser.kill()
                    self.active_laser = None

            # Update laser if active
            if self.laser_active and self.active_laser:
                self.active_laser.update()

    def draw(self, surface):
        # Draw warp particles
        for particle in self.warp_particles:
            particle_surface = pygame.Surface((particle['size'] * 2, particle['size'] * 2), pygame.SRCALPHA)
            color = (*particle['color'], particle['alpha'])
            pygame.draw.circle(particle_surface, color, (particle['size'], particle['size']), particle['size'])
            surface.blit(particle_surface, (particle['x'] - particle['size'], particle['y'] - particle['size']))
        
        if self.visible:
            # Draw shield if active
            if self.shield:
                self.shield_alpha = int(128 + 127 * math.sin(pygame.time.get_ticks() / 500))
                shield_color = (0, 255, 0, self.shield_alpha)
                self.shield_surface.fill((0, 0, 0, 0))
                
                pygame.draw.ellipse(self.shield_surface, shield_color, self.shield_surface.get_rect(), 4)
                
                inner_glow = pygame.Surface((self.rect.width + 10, self.rect.height + 10), pygame.SRCALPHA)
                pygame.draw.ellipse(inner_glow, (0, 255, 0, 50), inner_glow.get_rect())
                inner_glow_rect = inner_glow.get_rect(center=self.shield_surface.get_rect().center)
                self.shield_surface.blit(inner_glow, inner_glow_rect)
                
                current_time = pygame.time.get_ticks()
                for i in range(8):
                    angle = (current_time / 500 + i * 45) % 360
                    rad_angle = math.radians(angle)
                    distance = self.rect.width * 0.6
                    x = self.shield_surface.get_rect().centerx + math.cos(rad_angle) * distance
                    y = self.shield_surface.get_rect().centery + math.sin(rad_angle) * distance
                    
                    sparkle_size = 3
                    sparkle_color = (255, 255, 255, self.shield_alpha)
                    pygame.draw.circle(self.shield_surface, sparkle_color, (int(x), int(y)), sparkle_size)
                    glow_surface = pygame.Surface((sparkle_size * 4, sparkle_size * 4), pygame.SRCALPHA)
                    pygame.draw.circle(glow_surface, (255, 255, 255, 50), (sparkle_size * 2, sparkle_size * 2), sparkle_size * 2)
                    glow_rect = glow_surface.get_rect(center=(int(x), int(y)))
                    self.shield_surface.blit(glow_surface, glow_rect)
                
                shield_rect = self.shield_surface.get_rect(center=self.rect.center)
                surface.blit(self.shield_surface, shield_rect)
            
            # Draw player
            surface.blit(self.image, self.rect)
            
            # Draw active laser if any
            if self.active_laser:
                self.active_laser.draw(surface)

    def shoot(self):
        if self.laser_active:
            return  # Don't shoot regular bullets when laser is active
            
        self.shoot_sound.play()
        if self.triple_shot:
            # Shoot three bullets in a spread pattern
            for angle in [-15, 0, 15]:
                bullet = Bullet(self.rect.centerx, self.rect.top, angle)
                all_sprites.add(bullet)
                bullets.add(bullet)
        else:
            # Shoot single bullet
            bullet = Bullet(self.rect.centerx, self.rect.top)
            all_sprites.add(bullet)
            bullets.add(bullet)

    def power_up(self, type):
        if type == 'shield':
            self.shield = True
            self.shield_time = pygame.time.get_ticks() + 15000  # 15 seconds
            powerup_sound.play()
            return  # Don't clear other power-ups for shield
        
        # Clear other power-ups
        self.triple_shot = False
        self.speed_boost = False
        self.laser_active = False
        if self.active_laser:
            self.active_laser.kill()
            self.active_laser = None
        self.speed = self.original_speed
        
        # Set new power-up
        self.power_up_time = pygame.time.get_ticks() + 15000  # 15 seconds
        if type == 'speed':
            self.speed_boost = True
            self.speed = self.original_speed * 1.5
            powerup_sound.play()
        elif type == 'triple_shot':
            self.triple_shot = True
            powerup_sound.play()
        elif type == 'laser':
            self.laser_active = True
            self.active_laser = Laser(self.rect.centerx, self.rect.top)
            all_sprites.add(self.active_laser)
            laser_sound.play()  # Play laser sound when activating laser power-up

    def respawn(self):
        self.rect.centerx = WINDOW_WIDTH // 2
        self.rect.bottom = WINDOW_HEIGHT - 10
        self.visible = False  # Hide the ship during respawn delay
        self.is_respawning = True
        self.respawn_time = pygame.time.get_ticks()
        self.invulnerable = False  # Don't start invulnerability until after delay

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle=0):
        super().__init__()
        self.image = pygame.Surface((5, 10))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy = -10
        self.angle = angle
        if angle != 0:
            self.image = pygame.transform.rotate(self.image, angle)
            # Adjust speed based on angle
            rad_angle = math.radians(angle)
            self.speedx = math.sin(rad_angle) * 10
            self.speedy = -math.cos(rad_angle) * 10

    def update(self):
        if self.angle == 0:
            self.rect.y += self.speedy
        else:
            self.rect.x += self.speedx
            self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, size):
        super().__init__()
        self.images = []
        for i in range(8):
            img = pygame.Surface((size, size), pygame.SRCALPHA)
            color = (255, 100, 0, 255 - i * 30)  # Orange to transparent
            pygame.draw.circle(img, color, (size//2, size//2), size//2 - i * 2)
            self.images.append(img)
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50
        
        # Create particles
        self.particles = []
        for _ in range(20):  # Number of particles
            self.particles.append(Particle(x, y, size))

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.index += 1
            if self.index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.index]
        
        # Update particles
        for particle in self.particles[:]:
            particle.update()
            if particle.lifetime <= 0:
                self.particles.remove(particle)

    def draw(self, surface):
        # Draw particles
        for particle in self.particles:
            particle.draw(surface)
        # Draw explosion
        surface.blit(self.image, self.rect)

class Particle:
    def __init__(self, x, y, size, color=None):
        self.x = x
        self.y = y
        self.size = random.uniform(1, 3)  # Smaller particles
        # More varied colors for particles
        if color is None:
            if random.random() < 0.3:  # 30% chance for white/yellow particles
                self.color = (
                    random.randint(200, 255),  # R
                    random.randint(200, 255),  # G
                    random.randint(100, 200),  # B
                    255                        # A
                )
            else:  # 70% chance for orange/red particles
                self.color = (
                    random.randint(200, 255),  # R
                    random.randint(50, 150),   # G
                    random.randint(0, 50),     # B
                    255                        # A
                )
        else:
            self.color = color
        self.speed = random.uniform(3, 8)  # Increased speed range
        self.angle = random.uniform(0, 360)
        self.lifetime = random.randint(30, 60)  # Longer lifetime
        self.original_lifetime = self.lifetime
        self.gravity = 0.15  # Increased gravity effect
        self.velocity_x = math.cos(math.radians(self.angle)) * self.speed
        self.velocity_y = math.sin(math.radians(self.angle)) * self.speed
        self.rotation = random.uniform(-5, 5)  # Random rotation
        self.rotation_speed = random.uniform(-2, 2)  # Random rotation speed
        self.scale = 1.0
        self.scale_speed = random.uniform(0.95, 0.98)  # Particles shrink over time

    def update(self):
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.velocity_y += self.gravity
        self.lifetime -= 1
        self.rotation += self.rotation_speed
        self.scale *= self.scale_speed
        
        # Fade out
        alpha = int(255 * (self.lifetime / self.original_lifetime))
        self.color = (*self.color[:3], alpha)
        
        # Add some random movement
        if random.random() < 0.1:  # 10% chance each frame
            self.velocity_x += random.uniform(-0.2, 0.2)
            self.velocity_y += random.uniform(-0.2, 0.2)

    def draw(self, surface):
        if self.lifetime > 0:
            # Create a surface for the particle
            particle_surface = pygame.Surface((int(self.size * 2 * self.scale), int(self.size * 2 * self.scale)), pygame.SRCALPHA)
            
            # Draw the particle with rotation
            pygame.draw.circle(particle_surface, self.color, 
                             (int(self.size * self.scale), int(self.size * self.scale)), 
                             int(self.size * self.scale))
            
            # Rotate the particle
            rotated_particle = pygame.transform.rotate(particle_surface, self.rotation)
            
            # Draw the rotated particle
            surface.blit(rotated_particle, 
                        (int(self.x - rotated_particle.get_width()/2), 
                         int(self.y - rotated_particle.get_height()/2)))

class AsteroidExplosion(pygame.sprite.Sprite):
    def __init__(self, x, y, size, level=1):
        pygame.sprite.Sprite.__init__(self)
        self.particles = []
        self.x = x
        self.y = y
        self.size = size
        self.level = level
        # Create a transparent surface for the sprite
        self.image = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        self.create_particles()
        
    def create_particles(self):
        # Create particles based on asteroid size and level
        num_particles = int(self.size * 0.8)  # More particles for larger asteroids
        
        # Define colors based on level
        if self.level == 4:
            colors = [(255, 0, 0), (200, 0, 0), (255, 100, 0)]  # Red theme
        elif self.level == 3:
            colors = [(255, 100, 0), (255, 150, 0), (255, 200, 0)]  # Orange theme
        elif self.level == 2:
            colors = [(255, 255, 0), (200, 200, 0), (255, 200, 0)]  # Yellow theme
        else:
            colors = [(200, 200, 200), (150, 150, 150), (100, 100, 100)]  # Gray theme
        
        for _ in range(num_particles):
            # Randomly select a color from the theme
            base_color = random.choice(colors)
            # Add some variation to the color
            color = (
                max(0, min(255, base_color[0] + random.randint(-20, 20))),
                max(0, min(255, base_color[1] + random.randint(-20, 20))),
                max(0, min(255, base_color[2] + random.randint(-20, 20))),
                255
            )
            self.particles.append(Particle(self.x, self.y, self.size, color))
    
    def update(self):
        for particle in self.particles[:]:
            particle.update()
            if particle.lifetime <= 0:
                self.particles.remove(particle)
        if len(self.particles) == 0:
            self.kill()
    
    def draw(self, surface):
        for particle in self.particles:
            particle.draw(surface)

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, type=None):
        super().__init__()
        if type is None:
            self.type = random.choice(['shield', 'laser', 'triple_shot'])
        else:
            self.type = type
        self.image = create_powerup(self.type)
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(WINDOW_WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = 2

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > WINDOW_HEIGHT:
            self.kill()

class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle=0, speed=5):
        super().__init__()
        # Create a small glowing sphere (energy orb)
        orb_radius = 10
        self.image = pygame.Surface((orb_radius*2, orb_radius*2), pygame.SRCALPHA)
        # Outer glow
        for r in range(orb_radius, 2, -2):
            alpha = int(60 * (r / orb_radius))
            pygame.draw.circle(self.image, (0, 200, 255, alpha), (orb_radius, orb_radius), r)
        # Main orb
        pygame.draw.circle(self.image, (0, 255, 255), (orb_radius, orb_radius), orb_radius-2)
        # Core
        pygame.draw.circle(self.image, (255, 255, 255), (orb_radius, orb_radius), 4)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.top = y
        self.angle = angle
        rad_angle = math.radians(angle)
        self.speedx = math.sin(rad_angle) * speed
        self.speedy = math.cos(rad_angle) * speed
        # Trail
        self.trail_positions = []
        self.max_trail_length = 5

    def update(self):
        self.trail_positions.append(self.rect.center)
        if len(self.trail_positions) > self.max_trail_length:
            self.trail_positions.pop(0)
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if self.rect.top > WINDOW_HEIGHT or self.rect.left < 0 or self.rect.right > WINDOW_WIDTH:
            self.kill()

    def draw(self, surface):
        for i, pos in enumerate(self.trail_positions):
            alpha = int(80 * (i / len(self.trail_positions)))
            trail_surf = pygame.Surface((20, 20), pygame.SRCALPHA)
            pygame.draw.circle(trail_surf, (0, 200, 255, alpha), (10, 10), 8)
            trail_rect = trail_surf.get_rect(center=pos)
            surface.blit(trail_surf, trail_rect)
        surface.blit(self.image, self.rect)

def create_boss(size):
    # Create a surface for the boss
    size = int(size)  # Convert size to integer
    surface = pygame.Surface((size, size), pygame.SRCALPHA)
    
    # Draw main body - hexagonal core with energy shield
    shield_radius = size//2
    core_radius = int(size * 0.35)
    
    # Energy shield effect
    for r in range(shield_radius, core_radius, -1):
        alpha = int(100 * (r / shield_radius))
        color = (0, 150, 255, alpha)  # Cyan energy shield
        pygame.draw.circle(surface, color, (size//2, size//2), r)
    
    # Main core - metallic hexagon
    points = []
    for i in range(6):
        angle = math.pi/3 * i
        x = size/2 + math.cos(angle) * core_radius
        y = size/2 + math.sin(angle) * core_radius
        points.append((x, y))
    
    # Core gradient
    for r in range(core_radius, 0, -1):
        alpha = int(255 * (r / core_radius))
        color = (50, 50, 80, alpha)  # Dark metallic blue
        pygame.draw.circle(surface, color, (size//2, size//2), r)
    
    # Core border
    pygame.draw.polygon(surface, (100, 100, 255), points)  # Bright blue edges
    pygame.draw.polygon(surface, (255, 255, 255), points, 3)  # White border
    
    # Energy core
    core_size = int(size * 0.15)
    for r in range(core_size, 0, -1):
        alpha = int(255 * (r / core_size))
        pygame.draw.circle(surface, (0, 200, 255, alpha), (size//2, size//2), r)
    pygame.draw.circle(surface, (255, 255, 255), (size//2, size//2), core_size, 2)
    
    # Energy tendrils
    for i in range(8):
        angle = math.pi/4 * i
        start_x = size/2 + math.cos(angle) * core_radius
        start_y = size/2 + math.sin(angle) * core_radius
        end_x = size/2 + math.cos(angle) * shield_radius
        end_y = size/2 + math.sin(angle) * shield_radius
        
        # Tendril glow
        for r in range(3):
            alpha = int(150 * (1 - r/3))
            pygame.draw.line(surface, (0, 200, 255, alpha), 
                           (start_x, start_y), (end_x, end_y), 3-r)
    
    # Energy rings
    for i in range(3):
        ring_radius = int(core_radius * (1.2 + i * 0.3))
        pygame.draw.circle(surface, (0, 150, 255, 100), (size//2, size//2), ring_radius, 2)
    
    # Energy orbs
    for i in range(4):
        angle = math.pi/2 * i
        orb_x = size/2 + math.cos(angle) * int(size * 0.4)
        orb_y = size/2 + math.sin(angle) * int(size * 0.4)
        orb_size = int(size * 0.08)
        
        # Orb glow
        for r in range(orb_size, 0, -1):
            alpha = int(200 * (r / orb_size))
            pygame.draw.circle(surface, (0, 200, 255, alpha), (int(orb_x), int(orb_y)), r)
        
        # Orb border
        pygame.draw.circle(surface, (255, 255, 255), (int(orb_x), int(orb_y)), orb_size, 2)
    
    return surface

class AlienBoss(pygame.sprite.Sprite):
    def __init__(self, size):
        super().__init__()
        self.image = create_boss(size)
        self.rect = self.image.get_rect()
        self.rect.centerx = WINDOW_WIDTH // 2
        self.rect.top = -size  # Start above screen
        self.speed = 2
        self.rotation = 0
        self.rotation_speed = 1
        self.last_shot = 0
        self.shoot_delay = 1000  # 1 second between shots
        self.max_health = 240  # Changed from 300 to 240
        self.health = self.max_health
        self.health_bar_width = int(WINDOW_WIDTH * 0.6)
        self.health_bar_height = 20
        self.health_bar_padding = 15
        self.target_y = int(WINDOW_HEIGHT * 0.4)
        self.has_reached_position = False
        self.last_powerup_drop = self.max_health  # Initialize to max health
        self.powerup_drop_delay = 5000
        self.original_image = self.image
        self.original_rect = self.rect.copy()
        self.movement_direction = 1  # 1 for right, -1 for left
        self.base_speed = 2
        self.base_shoot_delay = 1000

    def update(self):
        # Rotate the boss
        self.rotation = (self.rotation + self.rotation_speed) % 360
        self.image = pygame.transform.rotate(self.original_image, self.rotation)
        self.rect = self.image.get_rect(center=self.rect.center)
        
        # Descend until reaching target position
        if not self.has_reached_position:
            if self.rect.centery < self.target_y:
                self.rect.y += self.speed
            else:
                self.has_reached_position = True
                self.last_shot = pygame.time.get_ticks()
        
        # Horizontal movement based on health
        if self.has_reached_position:
            health_ratio = self.health / self.max_health
            
            # Update speed and shoot delay based on health
            if health_ratio <= 0.3:  # Red health - fastest
                self.speed = self.base_speed * 3
                self.shoot_delay = self.base_shoot_delay // 3
            elif health_ratio <= 0.6:  # Yellow health - medium speed
                self.speed = self.base_speed * 2
                self.shoot_delay = self.base_shoot_delay // 2
            else:  # Green health - base speed
                self.speed = self.base_speed
                self.shoot_delay = self.base_shoot_delay
            
            # Move horizontally if in yellow or red health
            if health_ratio <= 0.6:
                self.rect.x += self.speed * self.movement_direction
                
                # Bounce off screen edges
                if self.rect.right >= WINDOW_WIDTH:
                    self.rect.right = WINDOW_WIDTH
                    self.movement_direction = -1
                elif self.rect.left <= 0:
                    self.rect.left = 0
                    self.movement_direction = 1
            
            # Shoot if reached target position
            current_time = pygame.time.get_ticks()
            if current_time - self.last_shot > self.shoot_delay:
                self.shoot()
                self.last_shot = current_time

            # Check for shield drops at health thresholds
            if self.health <= self.last_powerup_drop - 100:
                self.last_powerup_drop = self.health
                # Create shield powerup at boss position
                powerup = PowerUp(type='shield')
                powerup.rect.centerx = self.rect.centerx
                powerup.rect.top = self.rect.bottom
                all_sprites.add(powerup)
                powerups.add(powerup)
                powerup_sound.play()

    def shoot(self):
        # Calculate spawn points along the bottom edge of the boss
        spawn_width = self.rect.width * 0.6  # Use 60% of boss width for spawn area
        left_edge = self.rect.centerx - spawn_width/2
        right_edge = self.rect.centerx + spawn_width/2
        
        # Fire multiple bullets in a spread pattern
        num_bullets = 5  # Increased from 1 to 5 bullets
        for i in range(num_bullets):
            # Calculate spawn position
            spawn_x = left_edge + (spawn_width * i / (num_bullets - 1))
            spawn_y = self.rect.bottom - 5  # Spawn slightly inside the boss
            
            # Calculate angle based on spawn position relative to center
            relative_x = spawn_x - self.rect.centerx
            angle = math.degrees(math.atan2(relative_x, 100))  # 100 is arbitrary distance for angle calculation
            
            # Add some random variation to the angle
            angle += random.uniform(-10, 10)  # Add up to 10 degrees of variation
            
            bullet = EnemyBullet(spawn_x, spawn_y, angle)
            all_sprites.add(bullet)
            enemy_bullets.add(bullet)

    def draw(self, surface):
        # Draw the boss
        surface.blit(self.image, self.rect)
        
        # Only draw health bar if we've reached our position
        if self.has_reached_position:
            # Calculate health bar position - fixed at top of screen
            health_bar_x = (WINDOW_WIDTH - self.health_bar_width) // 2
            health_bar_y = 20  # Fixed distance from top
            
            # Draw health bar background
            pygame.draw.rect(surface, (50, 50, 50),
                           (health_bar_x, health_bar_y,
                            self.health_bar_width, self.health_bar_height))
            
            # Calculate health ratio and fill width
            health_ratio = self.health / self.max_health
            fill_width = int(self.health_bar_width * health_ratio)
            
            # Draw health bar fill with color gradient
            if health_ratio > 0.6:
                color = (0, 255, 0)  # Green for high health
            elif health_ratio > 0.3:
                color = (255, 255, 0)  # Yellow for medium health
            else:
                color = (255, 0, 0)  # Red for low health
            
            pygame.draw.rect(surface, color,
                           (health_bar_x, health_bar_y,
                            fill_width, self.health_bar_height))
            
            # Draw health bar border
            pygame.draw.rect(surface, (255, 255, 255),
                           (health_bar_x, health_bar_y,
                            self.health_bar_width, self.health_bar_height), 2)

class Laser(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((10, WINDOW_HEIGHT), pygame.SRCALPHA)
        # Create gradient laser beam
        for i in range(10):
            alpha = 255 - i * 20
            color = (0, 191, 255, alpha)  # Bright blue
            pygame.draw.line(self.image, color, (i, 0), (i, WINDOW_HEIGHT), 1)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y  # Changed from top to bottom
        self.damage = 1
        self.last_damage = pygame.time.get_ticks()
        self.damage_delay = 500  # Changed from 100 to 500 (5 times slower)
        # Start playing laser sound in loop
        laser_sound.play(-1)  # -1 means loop indefinitely

    def update(self):
        # Update position to follow player
        self.rect.centerx = player.rect.centerx
        self.rect.bottom = player.rect.top  # Keep laser at player's top

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def kill(self):
        # Stop laser sound when laser is deactivated
        laser_sound.stop()
        super().kill()

class PlayerExplosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.particles = []
        self.x = x
        self.y = y
        # Create a transparent surface for the sprite
        self.image = pygame.Surface((50, 50), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        self.create_particles()
        
    def create_particles(self):
        # Create more particles for player explosion
        num_particles = 40
        
        # Blue/cyan theme for player explosion
        colors = [
            (0, 200, 255),    # Cyan
            (0, 150, 255),    # Light blue
            (0, 100, 255),    # Blue
            (255, 255, 255),  # White
            (200, 200, 255)   # Light purple
        ]
        
        for _ in range(num_particles):
            # Randomly select a color from the theme
            base_color = random.choice(colors)
            # Add some variation to the color
            color = (
                max(0, min(255, base_color[0] + random.randint(-20, 20))),
                max(0, min(255, base_color[1] + random.randint(-20, 20))),
                max(0, min(255, base_color[2] + random.randint(-20, 20))),
                255
            )
            self.particles.append(Particle(self.x, self.y, 2, color))
    
    def update(self):
        for particle in self.particles[:]:
            particle.update()
            if particle.lifetime <= 0:
                self.particles.remove(particle)
        if len(self.particles) == 0:
            self.kill()
    
    def draw(self, surface):
        for particle in self.particles:
            particle.draw(surface)

# Show start screen
show_start_screen()

# Show rocket selection
selected_rocket = show_rocket_selection(ROCKET_TYPES)

# Create sprite groups
all_sprites = pygame.sprite.Group()
bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()
powerups = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
player = Player(selected_rocket)
all_sprites.add(player)

# Spawn enemies
for i in range(8):
    # Weighted random choice for enemy levels
    level = random.choices(
        [1, 2, 3, 4],
        weights=[0.4, 0.3, 0.2, 0.1]  # 40% level 1, 30% level 2, 20% level 3, 10% level 4
    )[0]
    new_enemy = Enemy(level)
    all_sprites.add(new_enemy)
    enemies.add(new_enemy)

# Game variables
score = 0
high_score = load_high_score()
font = pygame.font.Font(None, 36)
game_over = False
game_start_time = pygame.time.get_ticks()
boss_spawned = False
buffer_period = False
buffer_start_time = 0

# Create assets directory if it doesn't exist
if not os.path.exists('assets'):
    os.makedirs('assets')

# Create sound effects and music only if they don't exist
if not os.path.exists('assets/shoot.wav'):
    create_sound_effects()
if not os.path.exists('assets/background.wav'):
    create_background_music()

# Load and play background music immediately
pygame.mixer.music.load('assets/background.wav')
pygame.mixer.music.play(-1)  # -1 means loop indefinitely
pygame.mixer.music.set_volume(0.3)  # Set volume to 30%

# Game loop
running = True
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    if not game_over:
        # Update
        all_sprites.update()
        current_time = pygame.time.get_ticks()
        elapsed_time = (current_time - game_start_time) / 1000  # Convert to seconds

        # Check for boss battle timing
        if not boss_spawned and not buffer_period and elapsed_time >= 10:
            buffer_period = True
            buffer_start_time = current_time
            # Create explosions for all existing enemies
            for enemy in enemies:
                explosion = AsteroidExplosion(enemy.rect.centerx, enemy.rect.centery, enemy.rect.width, enemy.level)
                all_sprites.add(explosion)
                enemy.kill()
            enemies.empty()
        
        # Check buffer period (5 seconds)
        if buffer_period and current_time - buffer_start_time >= 5000:  # 5 seconds
            buffer_period = False
            boss_spawned = True
            boss = AlienBoss(WINDOW_WIDTH * 0.25)  # Spawn from center
            all_sprites.add(boss)

        # Only spawn enemies if not in buffer period and boss not spawned
        if not buffer_period and not boss_spawned:
            if random.random() < 0.02:  # 2% chance each frame
                level = random.choices(
                    [1, 2, 3, 4],
                    weights=[0.4, 0.3, 0.2, 0.1]
                )[0]
                new_enemy = Enemy(level)
                all_sprites.add(new_enemy)
                enemies.add(new_enemy)
            
            # Add power-up spawning
            if random.random() < 0.005:  # 0.5% chance each frame
                powerup = PowerUp()
                all_sprites.add(powerup)
                powerups.add(powerup)

        # Check for bullet-enemy collisions
        hits = pygame.sprite.groupcollide(enemies, bullets, False, True)  # First parameter False to keep enemies alive
        for enemy, bullet_list in hits.items():
            if enemy is not None:  # Check if enemy exists
                enemy.health -= len(bullet_list)
                if enemy.health <= 0:
                    score += enemy.points
                    explosion_sound.play()
                    # Create particle explosion
                    explosion = AsteroidExplosion(enemy.rect.centerx, enemy.rect.centery, enemy.rect.width, enemy.level)
                    all_sprites.add(explosion)
                    # Chance to drop powerup
                    if random.random() < 0.1:  # 10% chance
                        powerup = PowerUp(type='shield')
                        all_sprites.add(powerup)
                        powerups.add(powerup)
                    enemy.kill()

        # Check for laser-enemy collisions
        if player.active_laser:
            hits = pygame.sprite.spritecollide(player.active_laser, enemies, False)
            for enemy in hits:
                if enemy is not None:  # Check if enemy exists
                    enemy.health -= 1
                    if enemy.health <= 0:
                        score += enemy.points
                        explosion_sound.play()
                        enemy.kill()

        # Check for laser-boss collisions
        if boss_spawned and boss.has_reached_position:  # Only check collisions after descent
            # Check player bullets hitting boss
            hits = pygame.sprite.spritecollide(boss, bullets, True)
            for hit in hits:
                if hit is not None:  # Check if bullet exists
                    boss.health -= 1
                    # Check if we should drop a powerup
                    if boss.health <= boss.last_powerup_drop - 20:
                        boss.last_powerup_drop = boss.health
                        # Create shield powerup at boss position
                        powerup = PowerUp(type='shield')
                        powerup.rect.centerx = boss.rect.centerx
                        powerup.rect.top = boss.rect.bottom
                        all_sprites.add(powerup)
                        powerups.add(powerup)
                        powerup_sound.play()
                    if boss.health <= 0:
                        boss.kill()
                        boss_spawned = False
                        score += 1000
                        game_start_time = current_time
            
            # Check player collision with boss
            if pygame.sprite.collide_mask(player, boss):
                player.health -= 1
                if player.health <= 0:
                    player.kill()
            
            # Check laser hitting boss
            if player.laser_active and player.active_laser and pygame.sprite.collide_mask(player.active_laser, boss):
                current_time = pygame.time.get_ticks()
                if current_time - player.active_laser.last_damage > player.active_laser.damage_delay:
                    boss.health -= player.active_laser.damage
                    player.active_laser.last_damage = current_time
                    if boss.health <= 0:
                        boss.kill()
                        boss_spawned = False
                        score += 1000
                        game_start_time = current_time

        # Check for power-up collisions
        hits = pygame.sprite.spritecollide(player, powerups, True, pygame.sprite.collide_mask)
        for powerup in hits:
            if powerup is not None:
                player.power_up(powerup.type)
                powerup_sound.play()

        # Check for enemy bullet-player collisions
        hits = pygame.sprite.spritecollide(player, enemy_bullets, True)
        if hits and not player.shield and not player.invulnerable:
            # Create player explosion first
            explosion = PlayerExplosion(player.rect.centerx, player.rect.centery)
            all_sprites.add(explosion)
            # Then handle player damage
            player.lives -= 1
            if player.lives <= 0:
                game_over = True
                if score > high_score:
                    high_score = score
                    save_high_score(high_score)
            else:
                player.respawn()

        # Check for enemy-player collisions
        hits = pygame.sprite.spritecollide(player, enemies, False, pygame.sprite.collide_mask)
        if hits and not player.shield and not player.invulnerable:
            # Create player explosion first
            explosion = PlayerExplosion(player.rect.centerx, player.rect.centery)
            all_sprites.add(explosion)
            # Then handle player damage
            player.lives -= 1
            if player.lives <= 0:
                game_over = True
                if score > high_score:
                    high_score = score
                    save_high_score(high_score)
            else:
                player.respawn()
            # Destroy the enemy that hit the player
            for enemy in hits:
                explosion = AsteroidExplosion(enemy.rect.centerx, enemy.rect.centery, enemy.rect.width, enemy.level)
                all_sprites.add(explosion)
                enemy.kill()

        # Check for boss-player collisions
        if boss_spawned and boss.has_reached_position:
            if pygame.sprite.collide_mask(player, boss) and not player.shield and not player.invulnerable:
                # Create player explosion first
                explosion = PlayerExplosion(player.rect.centerx, player.rect.centery)
                all_sprites.add(explosion)
                # Then handle player damage
                player.lives -= 1
                if player.lives <= 0:
                    game_over = True
                    if score > high_score:
                        high_score = score
                        save_high_score(high_score)
                else:
                    player.respawn()

        # Draw
        screen.blit(space_background, (0, 0))
        
        # Draw all sprites except player and boss
        for sprite in all_sprites:
            if sprite != player and not isinstance(sprite, AlienBoss):
                if isinstance(sprite, AsteroidExplosion):
                    sprite.draw(screen)  # Draw particles for AsteroidExplosion
                else:
                    screen.blit(sprite.image, sprite.rect)  # Draw normal sprites
        
        # Draw boss with health bar if spawned
        if boss_spawned:
            boss.draw(screen)
        
        # Draw player with shield if active
        player.draw(screen)
        
        # Draw score and lives
        score_text = font.render(f'Score: {score}', True, WHITE)
        screen.blit(score_text, (10, 10))
        
        lives_text = font.render(f'Lives: {player.lives}', True, WHITE)
        screen.blit(lives_text, (10, 50))
        
        # Draw timer
        timer_text = font.render(f'Time: {int(elapsed_time)}s', True, WHITE)
        screen.blit(timer_text, (WINDOW_WIDTH - 150, 10))
        
        if buffer_period:
            # Create flashing boss warning text
            flash_alpha = int(255 * (0.5 + 0.5 * math.sin(pygame.time.get_ticks() / 200)))  # Slower flash
            warning_font = pygame.font.Font(None, 120)  # Much larger font
            buffer_text = warning_font.render('BOSS INCOMING!', True, (255, 0, 0))
            buffer_text.set_alpha(flash_alpha)
            text_rect = buffer_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
            screen.blit(buffer_text, text_rect)
        
        pygame.display.flip()

    else:
        show_game_over_screen(score, high_score)
        # Reset game
        all_sprites = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        enemies = pygame.sprite.Group()
        powerups = pygame.sprite.Group()
        enemy_bullets = pygame.sprite.Group()
        player = Player(selected_rocket)
        all_sprites.add(player)
        
        # Reset boss-related variables
        boss_spawned = False
        buffer_period = False
        buffer_start_time = 0
        
        # Spawn new enemies
        for i in range(8):
            # Weighted random choice for enemy levels
            level = random.choices(
                [1, 2, 3, 4],
                weights=[0.4, 0.3, 0.2, 0.1]  # 40% level 1, 30% level 2, 20% level 3, 10% level 4
            )[0]
            new_enemy = Enemy(level)
            all_sprites.add(new_enemy)
            enemies.add(new_enemy)
        
        score = 0
        game_over = False

    # Cap the frame rate
    clock.tick(FPS)

pygame.quit()
sys.exit() 