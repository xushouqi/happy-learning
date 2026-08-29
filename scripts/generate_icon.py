#!/usr/bin/env python3
"""Generate app launcher icon for Happy Learning."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math, time

t0 = time.time()
SIZE = 1024
BG_TOP = (72, 201, 176)       # teal-green
BG_BOT = (56, 152, 236)       # sky blue
WHITE = (255, 255, 255)
YELLOW = (255, 204, 51)

# --- Fast gradient: draw horizontal lines ---
bg = Image.new('RGBA', (SIZE, SIZE))
for y in range(SIZE):
    t = y / SIZE
    r = int(BG_TOP[0] + (BG_BOT[0] - BG_TOP[0]) * t)
    g = int(BG_TOP[1] + (BG_BOT[1] - BG_TOP[1]) * t)
    b = int(BG_TOP[2] + (BG_BOT[2] - BG_TOP[2]) * t)
    ImageDraw.Draw(bg).line([(0, y), (SIZE, y)], fill=(r, g, b, 255))

# --- Round corners with mask ---
mask = Image.new('L', (SIZE, SIZE), 0)
ImageDraw.Draw(mask).rounded_rectangle([0, 0, SIZE - 1, SIZE - 1], radius=200, fill=255)
bg.putalpha(mask)

img = bg.copy()
draw = ImageDraw.Draw(img)

# --- "ABC" text ---
font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
font = ImageFont.truetype(font_path, 220)
text = 'ABC'
bbox = draw.textbbox((0, 0), text, font=font)
tw = bbox[2] - bbox[0]
th = bbox[3] - bbox[1]
tx = (SIZE - tw) // 2
ty = int(SIZE * 0.22)

# Shadow
shadow = Image.new('RGBA', (SIZE, SIZE), (0, 0, 0, 0))
ImageDraw.Draw(shadow).text((tx + 6, ty + 6), text, font=font, fill=(0, 0, 0, 60))
img = Image.alpha_composite(img, shadow)
draw = ImageDraw.Draw(img)
draw.text((tx, ty), text, font=font, fill=WHITE)

# --- Smile curve ---
smile_y = ty + th + 50
draw.arc(
    [(SIZE // 2 - 150, smile_y - 60), (SIZE // 2 + 150, smile_y + 60)],
    start=10, end=170, fill=WHITE, width=20
)

# --- Stars ---
def draw_star(draw, cx, cy, size, color):
    points = []
    for i in range(5):
        angle = math.radians(-90 + i * 72)
        points.append((cx + size * math.cos(angle), cy + size * math.sin(angle)))
        angle2 = math.radians(-90 + i * 72 + 36)
        points.append((cx + size * 0.4 * math.cos(angle2), cy + size * 0.4 * math.sin(angle2)))
    draw.polygon(points, fill=color)

draw_star(draw, 180, smile_y - 20, 60, YELLOW)
draw_star(draw, SIZE - 180, smile_y - 20, 60, YELLOW)

# --- Subtitle ---
sub_font = ImageFont.truetype(font_path, 72)
sub_text = 'Happy Learning'
sub_bbox = draw.textbbox((0, 0), sub_text, font=sub_font)
stw = sub_bbox[2] - sub_bbox[0]
draw.text(((SIZE - stw) // 2, SIZE - 200), sub_text, font=sub_font, fill=WHITE)

img.save('/tmp/app_icon_1024.png', 'PNG')
print(f'Source icon saved: {img.size} ({time.time()-t0:.1f}s)')

# --- Android mipmap sizes ---
sizes = {'mdpi': 48, 'hdpi': 72, 'xhdpi': 96, 'xxhdpi': 144, 'xxxhdpi': 192}
android_dir = '/home/xsq/happy-learning/frontend/android/app/src/main/res'

for density, px in sizes.items():
    resized = img.resize((px, px), Image.LANCZOS)
    for suffix in ['', '_round']:
        resized.save(f'{android_dir}/mipmap-{density}/ic_launcher{suffix}.png', 'PNG')
    # Foreground
    fg_size = max(1, int(px * 432 / 1024))
    fg = img.resize((fg_size, fg_size), Image.LANCZOS)
    fg.save(f'{android_dir}/mipmap-{density}/ic_launcher_foreground.png', 'PNG')
    print(f'  {density}: {px}x{px}')

print(f'All done! ({time.time()-t0:.1f}s)')
