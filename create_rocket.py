from PIL import Image, ImageDraw

# Create a new image with a transparent background
img = Image.new('RGBA', (100, 200), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# Draw rocket body (white)
draw.rectangle([40, 50, 60, 180], fill=(255, 255, 255))

# Draw rocket nose (red)
draw.polygon([(50, 20), (30, 50), (70, 50)], fill=(255, 0, 0))

# Draw rocket fins (gray)
draw.polygon([(40, 180), (20, 220), (40, 180)], fill=(128, 128, 128))
draw.polygon([(60, 180), (80, 220), (60, 180)], fill=(128, 128, 128))

# Draw rocket window (blue)
draw.ellipse([45, 80, 55, 90], fill=(0, 0, 255))

# Save the image
img.save('assets/rocket.png') 