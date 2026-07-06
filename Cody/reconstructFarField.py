# Reconstruct Far Field
# Cody Pedersen
# July 6, 2026
#
# Given a phase map, propagates either a Gaussian beam
# or a plane wave through it and reconstructs the far-field intensity.

import tkinter as tk
from tkinter import filedialog, messagebox

from PIL import Image
import numpy as np


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


def gaussian_profile(shape, w):
    """
    Creates a centered Gaussian amplitude profile.
    """
    rows, cols = shape
    y, x = np.indices((rows, cols))
    x = x - cols // 2
    y = y - rows // 2

    return np.exp(-(x**2 + y**2) / w**2)


# ----------------------------------------------------
# Select phase map
# ----------------------------------------------------

phase_path = get_file_path("Select Phase Map")

phase = np.asarray(
    Image.open(phase_path).convert("L"),
    dtype=np.float64
)

# ----------------------------------------------------
# Convert grayscale image to phase
# ----------------------------------------------------

while True:
    phase_range = input("Is this phase map encoded from 0-128 or 0-255? (128/255): ").strip()

    if phase_range in ["128", "255"]:
        break

    print("Please enter 128 or 255.")

if phase_range == "255":
    # 0 -> -π, 255 -> π
    phase = (phase / 255.0) * (2 * np.pi) - np.pi

else:
    # 0 -> -π, 128 -> π
    phase = (phase / 128.0) * (2 * np.pi) - np.pi


# ----------------------------------------------------
# Choose source amplitude
# ----------------------------------------------------

while True:
    beam = input("Use a Gaussian beam or plane wave? (gaussian/plane): ").strip().lower()

    if beam in ["gaussian", "plane"]:
        break

    print("Please enter 'gaussian' or 'plane'.")

if beam == "gaussian":
    w = float(input("Enter the Gaussian beam radius w (pixels) [DEFAULT = 300]: "))
    source_amplitude = gaussian_profile(phase.shape, w)

else:
    source_amplitude = np.ones_like(phase)


# ----------------------------------------------------
# Reconstruct far field
# ----------------------------------------------------

reconstructed_field = source_amplitude * np.exp(1j * phase)

far_field = np.fft.fftshift(
    np.fft.fft2(
        np.fft.ifftshift(reconstructed_field)
    )
)

intensity = np.abs(far_field) ** 2

# Show raw intensity
# Image.fromarray(intensity).show()

# Show normalized intensity
normalized_intensity = (
    intensity / np.max(intensity) * 255
).astype(np.uint8)

Image.fromarray(normalized_intensity).show()