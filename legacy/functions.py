from PIL import Image, ImageOps, ImageDraw

def make_circle(img_path, size=(300,300)):
    img = Image.open(img_path).convert("RGBA")
    img = ImageOps.fit(img, size, centering=(0.5,0.5))

    # Create circular mask
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + size, fill=255)

    # Apply mask
    img.putalpha(mask)
    return img