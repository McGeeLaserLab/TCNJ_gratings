# Flat Top Generator
# Cody Pedersen
# July 6, 2026
#
# Creates a 1920 x 1152 binary flat-top image.
# User chooses either a square or circular flat top.
# The image is automatically saved.

import numpy as np
from PIL import Image

# Image dimensions
height = 1152
width = 1920

# Create black image
array = np.zeros((height, width), dtype=np.uint8)

# Image center
center_y = height // 2
center_x = width // 2

# -----------------------------
# User Input
# -----------------------------
while True:
    shape = input("Do you want a square or circular flat top? (square/circle): ").strip().lower()

    if shape in ["square", "circle"]:
        break

    print("Please enter 'square' or 'circle'.")

# -----------------------------
# Generate Shape
# -----------------------------
if shape == "circle":

    radius = int(input("Enter the radius (pixels): "))

    rowindex, colindex = np.indices((height, width))
    mask = (rowindex - center_y) ** 2 + (colindex - center_x) ** 2 <= radius ** 2
    array[mask] = 255

    filename = f"circle_flatTop_r{radius}.png"

else:

    side_length = int(input("Enter the side length (pixels): "))

    start_y = center_y - side_length // 2
    end_y = start_y + side_length

    start_x = center_x - side_length // 2
    end_x = start_x + side_length

    array[start_y:end_y, start_x:end_x] = 255

    filename = f"square_flatTop_{side_length}.png"

# -----------------------------
# Save and Display
# -----------------------------
image = Image.fromarray(array)

image.save(filename)
print(f"Saved as: {filename}")

image.show()