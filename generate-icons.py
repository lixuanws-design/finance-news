"""Generate PWA icons"""
from PIL import Image, ImageDraw, ImageFont

def create_icon(size, path):
    img = Image.new('RGB', (size, size), '#1a1a1a')
    draw = ImageDraw.Draw(img)
    # Circle
    margin = size // 10
    draw.ellipse([margin, margin, size-margin, size-margin], fill='#c41e3a')
    # Text (use default font)
    try:
        font = ImageFont.truetype("simhei.ttf", size // 2)
    except:
        font = ImageFont.load_default()
    text = "老"
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    x = (size - tw) // 2
    y = (size - th) // 2 - size // 20
    draw.text((x, y), text, fill='#ffffff', font=font)
    img.save(path, 'PNG')
    print(f'Created: {path}')

create_icon(512, 'static/icon-512.png')
create_icon(192, 'static/icon-192.png')
print('Done!')
