# Image Error Calculator
# Cody Pedersen
# July 6, 2026
#
# Calculates the normalized RMSE between a reconstructed image
# and a target image using the formula from
# "Speckle Reduced Holographic Beam Shaping with Modified Gerchberg-Saxton Algorithm"

import tkinter as tk
from tkinter import filedialog, messagebox
import numpy as np
from PIL import Image


def get_file_path(title):
    """
    Opens a file dialog to select a single image.
    Returns the selected file path.
    """
    root = tk.Tk()
    root.withdraw()

    while True:
        file_path = filedialog.askopenfilenames(title=title)

        if file_path == ():
            raise KeyboardInterrupt("User canceled.")

        elif len(file_path) != 1:
            messagebox.showerror("Error", "Please select exactly one image.")

        else:
            root.destroy()
            return file_path[0]


# -----------------------------
# Select Images
# -----------------------------
print("Select the reconstruction image.")
reconstruction_path = get_file_path("Select Reconstruction Image")

print("Select the target image.")
target_path = get_file_path("Select Target Image")


# -----------------------------
# Load Images
# -----------------------------
reconstruction = np.asarray(
    Image.open(reconstruction_path).convert("L"),
    dtype=np.float64
)

target = np.asarray(
    Image.open(target_path).convert("L"),
    dtype=np.float64
)


# -----------------------------
# Calculate RMSE
# -----------------------------
mask = target > 0

numerator = np.sum((reconstruction[mask] - target[mask]) ** 2)
denominator = np.sum(target[mask] ** 2)

rmse = np.sqrt(numerator / denominator)


# -----------------------------
# Output
# -----------------------------
print(f"\nRMSE = {rmse:.6f}")