from PIL import Image, ImageDraw
import numpy as np
from scipy.io import wavfile
import os

# Create assets directory if it doesn't exist
if not os.path.exists('assets'):
    os.makedirs('assets')

# Create rocket image
def create_rocket():
    img = Image.new('RGBA', (60, 100), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Rocket body (main cone)
    draw.polygon([(30, 0), (10, 70), (50, 70)], fill=(200, 200, 200))
    
    # Rocket nose cone
    draw.polygon([(30, 0), (20, 15), (40, 15)], fill=(255, 0, 0))
    
    # Rocket body details
    draw.rectangle([(25, 15), (35, 70)], fill=(100, 100, 100))
    
    # Rocket fins
    draw.polygon([(10, 70), (5, 90), (15, 70)], fill=(150, 150, 150))  # Left fin
    draw.polygon([(50, 70), (45, 70), (55, 90)], fill=(150, 150, 150))  # Right fin
    
    # Rocket engine
    draw.rectangle([(20, 70), (40, 90)], fill=(50, 50, 50))
    
    # Engine flame
    draw.polygon([(20, 90), (30, 100), (40, 90)], fill=(255, 165, 0))
    draw.polygon([(25, 90), (30, 95), (35, 90)], fill=(255, 0, 0))
    
    # Windows
    draw.ellipse([(25, 30), (35, 40)], fill=(0, 191, 255))
    draw.ellipse([(25, 45), (35, 55)], fill=(0, 191, 255))
    
    img.save('assets/rocket.png')

# Create sound effects
def create_sounds():
    # Shoot sound
    sample_rate = 44100
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

if __name__ == '__main__':
    create_rocket()
    create_sounds() 