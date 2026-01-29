"""Convert PNG to ICO - transparent background only, no border."""
from PIL import Image
import os
from collections import deque

SOURCE_PNG = r"C:\Users\Sam\.cursor\projects\c-Users-Sam-Documents-GitHub-dict-to-anki\assets\c__Users_Sam_AppData_Roaming_Cursor_User_workspaceStorage_99807c46623ac45d81f85fe6f3ddf3a5_images_Lexi_Snap_Icon_cropped-6f2cb30b-1f9f-4ea7-8c78-375860603228.png"
OUTPUT_ICO = "assets/icon.ico"
OUTPUT_PNG = "assets/icon.png"


def flood_fill_transparent(img, tolerance=30):
    """Make background transparent using flood fill from edges."""
    img = img.convert("RGBA")
    pixels = img.load()
    width, height = img.size
    
    corner_samples = [
        pixels[0, 0], pixels[width-1, 0],
        pixels[0, height-1], pixels[width-1, height-1],
    ]
    
    avg_r = sum(p[0] for p in corner_samples) // len(corner_samples)
    avg_g = sum(p[1] for p in corner_samples) // len(corner_samples)
    avg_b = sum(p[2] for p in corner_samples) // len(corner_samples)
    
    def is_background(r, g, b):
        return (abs(r - avg_r) < tolerance and 
                abs(g - avg_g) < tolerance and 
                abs(b - avg_b) < tolerance)
    
    visited = set()
    queue = deque()
    
    for x in range(width):
        r, g, b, a = pixels[x, 0]
        if is_background(r, g, b):
            queue.append((x, 0))
        r, g, b, a = pixels[x, height-1]
        if is_background(r, g, b):
            queue.append((x, height-1))
    
    for y in range(height):
        r, g, b, a = pixels[0, y]
        if is_background(r, g, b):
            queue.append((0, y))
        r, g, b, a = pixels[width-1, y]
        if is_background(r, g, b):
            queue.append((width-1, y))
    
    while queue:
        x, y = queue.popleft()
        if (x, y) in visited:
            continue
        if x < 0 or x >= width or y < 0 or y >= height:
            continue
        visited.add((x, y))
        r, g, b, a = pixels[x, y]
        if is_background(r, g, b):
            pixels[x, y] = (r, g, b, 0)
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in visited:
                    queue.append((nx, ny))
    
    return img


def create_ico_with_sizes(img, output_path):
    """Create ICO file with multiple sizes."""
    sizes = [16, 20, 24, 32, 40, 48, 64, 96, 128, 256]
    
    images = []
    for size in sizes:
        resized = img.copy()
        resized = resized.resize((size, size), Image.Resampling.LANCZOS)
        images.append(resized)
    
    images[-1].save(
        output_path,
        format='ICO',
        sizes=[(s, s) for s in sizes]
    )
    print(f"Created {output_path}")


def main():
    img = Image.open(SOURCE_PNG)
    img_transparent = flood_fill_transparent(img)
    img_transparent.save(OUTPUT_PNG, format='PNG')
    create_ico_with_sizes(img_transparent, OUTPUT_ICO)
    print("Done - reverted to no border")


if __name__ == "__main__":
    main()
