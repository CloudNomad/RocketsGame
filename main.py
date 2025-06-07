import pygame
import sys
import random
import math
import os
import json

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Set up the display
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Rocket Game")
clock = pygame.time.Clock()

# Load sounds
def load_sound(name):
    try:
        return pygame.mixer.Sound(os.path.join('assets', name))
    except:
        return None

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

class PowerUp(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.type = random.choice(['shield', 'speed', 'triple_shot'])
        self.image = pygame.Surface((20, 20))
        self.image.fill(GREEN if self.type == 'shield' else BLUE if self.type == 'speed' else YELLOW)
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(WINDOW_WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = 2

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > WINDOW_HEIGHT:
            self.kill()

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed=-10, angle=0):
        super().__init__()
        self.image = pygame.Surface((5, 10))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = speed
        self.angle = angle

    def update(self):
        self.rect.y += self.speed * math.cos(math.radians(self.angle))
        self.rect.x += self.speed * math.sin(math.radians(self.angle))
        if self.rect.bottom < 0 or self.rect.top > WINDOW_HEIGHT or self.rect.right < 0 or self.rect.left > WINDOW_WIDTH:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, enemy_type='normal'):
        super().__init__()
        self.enemy_type = enemy_type
        if enemy_type == 'normal':
            self.image = pygame.Surface((30, 30))
            self.image.fill(RED)
            self.health = 1
            self.points = 10
        elif enemy_type == 'tank':
            self.image = pygame.Surface((40, 40))
            self.image.fill((150, 0, 0))
            self.health = 3
            self.points = 30
        elif enemy_type == 'fast':
            self.image = pygame.Surface((20, 20))
            self.image.fill((255, 100, 100))
            self.health = 1
            self.points = 20
        
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(WINDOW_WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = random.randrange(1, 4) if enemy_type != 'fast' else random.randrange(3, 6)
        self.speedx = random.randrange(-2, 2)

    def update(self):
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        if self.rect.top > WINDOW_HEIGHT or self.rect.left < -25 or self.rect.right > WINDOW_WIDTH + 25:
            self.rect.x = random.randrange(WINDOW_WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(1, 4) if self.enemy_type != 'fast' else random.randrange(3, 6)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = load_image('rocket.png', 0.5)
        self.rect = self.image.get_rect()
        self.rect.centerx = WINDOW_WIDTH // 2
        self.rect.bottom = WINDOW_HEIGHT - 10
        self.speed = 5
        self.shoot_delay = 250
        self.last_shot = pygame.time.get_ticks()
        self.lives = 3
        self.shield = False
        self.triple_shot = False
        self.power_up_time = 0
        self.original_speed = self.speed

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WINDOW_WIDTH:
            self.rect.x += self.speed
        
        # Shooting
        now = pygame.time.get_ticks()
        if keys[pygame.K_SPACE] and now - self.last_shot > self.shoot_delay:
            self.shoot()
            self.last_shot = now

        # Power-up timer
        if self.power_up_time > 0:
            self.power_up_time -= 1
            if self.power_up_time == 0:
                self.speed = self.original_speed
                self.triple_shot = False

    def shoot(self):
        if self.triple_shot:
            for angle in [-15, 0, 15]:
                bullet = Bullet(self.rect.centerx, self.rect.top, -10, angle)
                all_sprites.add(bullet)
                bullets.add(bullet)
        else:
            bullet = Bullet(self.rect.centerx, self.rect.top)
            all_sprites.add(bullet)
            bullets.add(bullet)

    def power_up(self, power_type):
        if power_type == 'shield':
            self.shield = True
            self.power_up_time = 300
        elif power_type == 'speed':
            self.speed = self.original_speed * 1.5
            self.power_up_time = 300
        elif power_type == 'triple_shot':
            self.triple_shot = True
            self.power_up_time = 300

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

# Create sprite groups
all_sprites = pygame.sprite.Group()
bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()
powerups = pygame.sprite.Group()
player = Player()
all_sprites.add(player)

# Spawn enemies
for i in range(8):
    enemy_type = random.choice(['normal', 'tank', 'fast'])
    enemy = Enemy(enemy_type)
    all_sprites.add(enemy)
    enemies.add(enemy)

# Game variables
score = 0
high_score = load_high_score()
font = pygame.font.Font(None, 36)
game_over = False

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

        # Spawn power-ups
        if random.random() < 0.01:
            powerup = PowerUp()
            all_sprites.add(powerup)
            powerups.add(powerup)

        # Check for bullet-enemy collisions
        hits = pygame.sprite.groupcollide(enemies, bullets, False, True)
        for enemy, bullet_list in hits.items():
            enemy.health -= len(bullet_list)
            if enemy.health <= 0:
                score += enemy.points
                enemy.kill()
                new_enemy = Enemy(random.choice(['normal', 'tank', 'fast']))
                all_sprites.add(new_enemy)
                enemies.add(new_enemy)

        # Check for player-enemy collisions
        hits = pygame.sprite.spritecollide(player, enemies, False)
        if hits and not player.shield:
            player.lives -= 1
            if player.lives <= 0:
                game_over = True
                if score > high_score:
                    high_score = score
                    save_high_score(high_score)
            else:
                player.rect.centerx = WINDOW_WIDTH // 2
                player.rect.bottom = WINDOW_HEIGHT - 10

        # Check for power-up collisions
        hits = pygame.sprite.spritecollide(player, powerups, True)
        for hit in hits:
            player.power_up(hit.type)

        # Draw
        screen.fill(BLACK)
        all_sprites.draw(screen)
        
        # Draw score and lives
        score_text = font.render(f'Score: {score}', True, WHITE)
        screen.blit(score_text, (10, 10))
        
        lives_text = font.render(f'Lives: {player.lives}', True, WHITE)
        screen.blit(lives_text, (10, 50))
        
        if player.shield:
            shield_text = font.render('Shield Active', True, GREEN)
            screen.blit(shield_text, (WINDOW_WIDTH - 150, 10))
        
        pygame.display.flip()

    else:
        show_game_over_screen(score, high_score)
        # Reset game
        all_sprites = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        enemies = pygame.sprite.Group()
        powerups = pygame.sprite.Group()
        player = Player()
        all_sprites.add(player)
        
        for i in range(8):
            enemy_type = random.choice(['normal', 'tank', 'fast'])
            enemy = Enemy(enemy_type)
            all_sprites.add(enemy)
            enemies.add(enemy)
        
        score = 0
        game_over = False

    # Cap the frame rate
    clock.tick(FPS)

pygame.quit()
sys.exit() 