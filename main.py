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

# Set up the display - true fullscreen
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
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
        self.image = load_image(f'rocket_{rocket_type}.png', 0.5)
        self.rect = self.image.get_rect()
        self.rect.centerx = WINDOW_WIDTH // 2
        self.rect.bottom = WINDOW_HEIGHT - 10
        
        # Get rocket stats
        rocket_data = ROCKET_TYPES[rocket_type]
        self.speed = rocket_data['speed']
        self.shoot_delay = rocket_data['shoot_delay']
        
        self.last_shot = pygame.time.get_ticks()
        self.lives = 3
        self.shield = False
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

    def draw(self, surface):
        if self.visible:
            # Draw shield if active
            if self.shield:
                self.shield_alpha = (self.shield_alpha + self.shield_alpha_change) % 255
                shield_color = (0, 255, 0, self.shield_alpha)  # Green shield
                self.shield_surface.fill((0, 0, 0, 0))
                pygame.draw.ellipse(self.shield_surface, shield_color, self.shield_surface.get_rect(), 2)
                shield_rect = self.shield_surface.get_rect(center=self.rect.center)
                surface.blit(self.shield_surface, shield_rect)
            
            # Draw player
            surface.blit(self.image, self.rect)
            
            # Draw active laser if any
            if self.active_laser:
                self.active_laser.draw(surface)

    def update(self):
        # Handle invulnerability flashing
        if self.invulnerable:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_flash > self.flash_delay:
                self.visible = not self.visible
                self.last_flash = current_time
                self.flash_count += 1
                if self.flash_count >= 6:  # Flash 3 times (6 toggles)
                    self.invulnerable = False
                    self.visible = True
                    self.flash_count = 0

        # Handle power-up timers
        current_time = pygame.time.get_ticks()
        if self.power_up_time > 0 and current_time > self.power_up_time:
            self.shield = False
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
            current_time = pygame.time.get_ticks()
            if current_time - self.last_shot > self.shoot_delay:
                self.shoot()
                self.last_shot = current_time

        # Update laser if active
        if self.laser_active and self.active_laser:
            self.active_laser.update()

    def shoot(self):
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
        self.power_up_time = pygame.time.get_ticks() + 10000  # 10 seconds
        if type == 'shield':
            self.shield = True
        elif type == 'speed':
            self.speed_boost = True
            self.speed = self.original_speed * 1.5
        elif type == 'triple_shot':
            self.triple_shot = True
        elif type == 'laser':
            self.laser_active = True
            self.active_laser = Laser(self.rect.centerx, self.rect.top)
            all_sprites.add(self.active_laser)
        powerup_sound.play()

    def respawn(self):
        self.rect.centerx = WINDOW_WIDTH // 2
        self.rect.bottom = WINDOW_HEIGHT - 10
        self.invulnerable = True
        self.invulnerable_time = pygame.time.get_ticks()
        self.flash_count = 0
        self.visible = True

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
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = random.randint(2, 4)
        # More varied colors for particles
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

def create_boss():
    # Calculate size based on screen dimensions
    size = int(WINDOW_WIDTH * 0.7)  # 70% of screen width
    surface = pygame.Surface((size, size), pygame.SRCALPHA)
    
    # Main body (hexagonal shape)
    points = []
    for i in range(6):
        angle = i * (360 / 6)
        radius = size/2 * 0.8
        x = size/2 + radius * math.cos(math.radians(angle))
        y = size/2 + radius * math.sin(math.radians(angle))
        points.append((x, y))
    
    # Draw main body with gradient
    for r in range(size//2, 0, -1):
        alpha = int(255 * (r / (size/2)))
        color = (200, 0, 0, alpha)  # Red gradient
        pygame.draw.circle(surface, color, (size//2, size//2), r)
    
    # Draw hexagonal shape
    pygame.draw.polygon(surface, (220, 0, 0), points)
    
    # Add details
    # Cockpit
    pygame.draw.ellipse(surface, (0, 191, 255), (size//4, size//4, size//2, size//3))
    pygame.draw.ellipse(surface, (0, 0, 0), (size//4 + 5, size//4 + 5, size//2 - 10, size//3 - 10))
    
    # Wings
    wing_points = [
        (size//2, size//2),  # Center
        (size//2 - size//2.5, size//2 + size//5),  # Left wing
        (size//2 - size//3.3, size//2 + size//2.5),  # Left wing tip
        (size//2 + size//3.3, size//2 + size//2.5),  # Right wing tip
        (size//2 + size//2.5, size//2 + size//5),  # Right wing
    ]
    pygame.draw.polygon(surface, (180, 0, 0), wing_points)
    
    # Engines
    for x in [size//3, 2*size//3]:
        pygame.draw.ellipse(surface, (255, 100, 0), (x - size//10, size//2 + size//3.3, size//5, size//3.3))
        pygame.draw.ellipse(surface, (255, 200, 0), (x - size//20, size//2 + size//2.8, size//10, size//5))
    
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
    pygame.draw.polygon(surface, (255, 255, 255), highlight_points, 1)
    
    return surface

class AlienBoss(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.original_image = create_boss()
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.rect.centerx = WINDOW_WIDTH // 2
        self.rect.top = -self.rect.height  # Start above the screen
        self.speedy = 2
        self.health = 50
        self.last_shot = pygame.time.get_ticks()
        self.shoot_delay = random.randint(300, 800)  # Random delay between shots
        self.last_powerup_drop = self.health
        self.powerup_threshold = 10  # Drop powerup every 10 health points
        self.rotation = 0
        self.rotation_speed = 1
        # Stop at 40% of screen height (10% above halfway)
        self.target_y = WINDOW_HEIGHT * 0.4
        self.descending = True

    def update(self):
        # Rotate the boss
        self.rotation = (self.rotation + self.rotation_speed) % 360
        self.image = pygame.transform.rotate(self.original_image, self.rotation)
        self.rect = self.image.get_rect(center=self.rect.center)
        
        # Descend until reaching target position
        if self.descending:
            if self.rect.top < self.target_y:
                self.rect.y += self.speedy
            else:
                self.descending = False

        # Shooting
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay and not self.descending:
            self.shoot()
            self.last_shot = now
            # Set new random delay for next shot
            self.shoot_delay = random.randint(300, 800)

    def shoot(self):
        # Random number of bullets (1-4)
        num_shots = random.randint(1, 4)
        
        for _ in range(num_shots):
            # Random position along the bottom of the boss
            x = random.randint(self.rect.left + 20, self.rect.right - 20)
            # Random angle between -45 and 45 degrees
            angle = random.randint(-45, 45)
            # Random speed between 5 and 10
            speed = random.randint(5, 10)
            bullet = EnemyBullet(x, self.rect.bottom, angle, speed)
            all_sprites.add(bullet)
            enemy_bullets.add(bullet)

class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle=0, speed=5):
        super().__init__()
        self.image = pygame.Surface((5, 10))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.top = y
        self.angle = angle
        # Calculate speed based on angle
        rad_angle = math.radians(angle)
        self.speedx = math.sin(rad_angle) * speed
        self.speedy = math.cos(rad_angle) * speed
        # Rotate the bullet image
        self.image = pygame.transform.rotate(self.image, -angle)

    def update(self):
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if self.rect.top > WINDOW_HEIGHT or self.rect.left < 0 or self.rect.right > WINDOW_WIDTH:
            self.kill()

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
        self.rect.top = y
        self.damage = 1
        self.last_damage = pygame.time.get_ticks()
        self.damage_delay = 100  # Damage every 100ms

    def update(self):
        # Update position to follow player
        self.rect.centerx = player.rect.centerx

    def draw(self, surface):
        surface.blit(self.image, self.rect)

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
        if not boss_spawned and not buffer_period and elapsed_time >= 30:
            buffer_period = True
            buffer_start_time = current_time
            # Create explosions for all existing enemies
            for enemy in enemies:
                explosion = Explosion(enemy.rect.centerx, enemy.rect.centery, enemy.rect.width * 2)
                all_sprites.add(explosion)
                enemy.kill()
            enemies.empty()
        
        # Check buffer period (5 seconds)
        if buffer_period and current_time - buffer_start_time >= 5000:  # 5 seconds
            buffer_period = False
            boss_spawned = True
            boss = AlienBoss()
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
        hits = pygame.sprite.groupcollide(enemies, bullets, False, True)
        for enemy, bullet_list in hits.items():
            enemy.health -= len(bullet_list)
            if enemy.health <= 0:
                score += enemy.points
                explosion_sound.play()
                enemy.kill()

        # Check for laser-enemy collisions
        if player.active_laser:
            hits = pygame.sprite.spritecollide(player.active_laser, enemies, False)
            for enemy in hits:
                enemy.health -= 1
                if enemy.health <= 0:
                    score += enemy.points
                    explosion_sound.play()
                    enemy.kill()

        # Check for laser-boss collisions
        if player.active_laser and boss_spawned:
            if pygame.sprite.collide_rect(player.active_laser, boss):
                boss.health -= 1
                # Check if we should drop a powerup
                if boss.health <= boss.last_powerup_drop - boss.powerup_threshold:
                    boss.last_powerup_drop = boss.health
                    # Create shield powerup at boss position
                    powerup = PowerUp(type='shield')
                    powerup.rect.centerx = boss.rect.centerx
                    powerup.rect.top = boss.rect.bottom
                    all_sprites.add(powerup)
                    powerups.add(powerup)
                    powerup_sound.play()
                if boss.health <= 0:
                    score += 1000
                    explosion_sound.play()
                    boss.kill()
                    boss_spawned = False
                    game_start_time = current_time

        # Check for bullet-boss collisions
        if boss_spawned:
            hits = pygame.sprite.spritecollide(boss, bullets, True)
            for bullet in hits:
                boss.health -= 1
                # Check if we should drop a powerup
                if boss.health <= boss.last_powerup_drop - boss.powerup_threshold:
                    boss.last_powerup_drop = boss.health
                    # Create shield powerup at boss position
                    powerup = PowerUp(type='shield')
                    powerup.rect.centerx = boss.rect.centerx
                    powerup.rect.top = boss.rect.bottom
                    all_sprites.add(powerup)
                    powerups.add(powerup)
                    powerup_sound.play()
                if boss.health <= 0:
                    score += 1000
                    explosion_sound.play()
                    boss.kill()
                    boss_spawned = False
                    game_start_time = current_time

        # Check for enemy bullet-player collisions
        hits = pygame.sprite.spritecollide(player, enemy_bullets, True)
        if hits and not player.shield and not player.invulnerable:
            player.lives -= 1
            if player.lives <= 0:
                game_over = True
                if score > high_score:
                    high_score = score
                    save_high_score(high_score)
            else:
                player.respawn()

        # Check for asteroid-player collisions
        asteroid_hits = pygame.sprite.spritecollide(player, enemies, True)
        if asteroid_hits and not player.shield and not player.invulnerable:
            player.lives -= 1
            # Create explosion for each asteroid that hit
            for enemy in asteroid_hits:
                explosion = Explosion(enemy.rect.centerx, enemy.rect.centery, enemy.rect.width * 2)
                all_sprites.add(explosion)
                explosion_sound.play()
            if player.lives <= 0:
                game_over = True
                if score > high_score:
                    high_score = score
                    save_high_score(high_score)
            else:
                player.respawn()

        # Check for power-up collisions
        hits = pygame.sprite.spritecollide(player, powerups, True)
        for powerup in hits:
            player.power_up(powerup.type)

        # Draw
        screen.blit(space_background, (0, 0))
        
        # Draw all sprites except player
        for sprite in all_sprites:
            if sprite != player:
                screen.blit(sprite.image, sprite.rect)
        
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
        
        if boss_spawned:
            boss_health_text = font.render(f'Boss Health: {boss.health}', True, RED)
            screen.blit(boss_health_text, (WINDOW_WIDTH//2 - 100, 90))

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