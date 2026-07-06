# Phase Map Generator 2026
# Cody Pedersen
# July 6th, 2026

"""
Generates a phase-only hologram (phase map) from a target grayscale image
using the Gerchberg-Saxton (GS) algorithm.

Features
--------
- Supports Gaussian or plane-wave illumination.
- Uses interpolation and zero-padding for improved convergence.
- Automatically saves the generated phase map.
- Reconstructs the far-field intensity for verification.

Based on Diffractsim's Fourier phase retrieval implementation (fourier_phase_retrieval.py, file_handling.py, and image_handling.py).
"""

import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import numpy as np
from scipy.interpolate import RectBivariateSpline
from pathlib import Path

# ----------------------------------------------------
# Functions
# ----------------------------------------------------

def get_file_path():
    """
    Opens a file dialog to select a single image file.
    Returns the file path as a string.
    """
    root = tk.Tk()
    root.withdraw()

    while True:
        file_path = filedialog.askopenfilenames(title="Select exactly 1 image")
        if file_path == ():
            raise KeyboardInterrupt  # User canceled
        elif len(file_path) != 1:
            messagebox.showerror("Error", "Select exactly 1 image")
        else:
            return file_path[0]

def gaussian_profile(shape, w):
    """
    Creates a gaussian profile of the given shape and waist radius.
    """
    rows, cols = shape #takes the rows and columns of the img, example: rows = 1152, cols = 1920
    y, x = np.indices((rows, cols)) #creates matrices that record the x and y position of each entry in the matrix
    x = x - cols // 2 #centers the x indices
    y = y - rows // 2 #centers the y indices
    return np.exp(-(x**2 + y**2) / w**2)

def gs(img, max_iter, source_amplitude):
    """
    Performs the Gerchberg-Saxton algorithm.
    Interpolates the target amplitude to "smooth" it out. In other words, reduce discrete jumps from 0-255.
    Pads the source amplitude with zeros.

    Args:
    img: 2D numpy array (grayscale image as amplitude constraint)
    max_iter: number of iterations
    source_amplitude: 2D numpy array representing near field amplitude constraint

    Returns:
    2D complex numpy array representing the final near-field phase result
    """

    # creation of target and source amplitude
    target_amplitude = img / 255
    target_amplitude = np.flip(target_amplitude, axis=0)
    source_amplitude = np.flip(source_amplitude, axis=0)

    # padding and interpolation
    x, y = np.shape(img)
    func = RectBivariateSpline(np.linspace(0, 1, x), np.linspace(0, 1, y), target_amplitude)  # interpolation function
    target_amplitude = func(np.linspace(0, 1, 2 * x), np.linspace(0, 1, 2 * y))  # interpolate target amplitude to be larger
    source_amplitude = np.pad(source_amplitude, ((x // 2, x // 2), (y // 2, y // 2)),'constant')  # pad zeros around source amplitude to make same size as target

    # absolute value to remove any noise from interpolation and ifftshift to put the zero frequency component in the top left of the image
    target_amplitude = np.abs(np.fft.ifftshift(target_amplitude))
    source_amplitude = np.abs(np.fft.ifftshift(source_amplitude))

    near_field = np.fft.ifft2(np.fft.ifftshift(target_amplitude))  # inverse fft to start (there is an extra ifftshift here since diffractsim had it)

    # GS algo loop
    for i in range(max_iter):
        near_field = source_amplitude * np.exp(1j * np.angle(near_field))
        far_field = np.fft.fft2(near_field)
        far_field = target_amplitude * np.exp(1j * np.angle(far_field))
        near_field = np.fft.ifft2(far_field)

        print(f"\rIteration {i + 1}/{max_iter}", end="", flush=True)

    print("\nDone.")

    phase = np.fft.fftshift(np.angle(near_field))  # pull out phase with np.angle and fftshift it to shift the zero frequency component to the center of the spectrum

    return phase[x // 2:-x // 2, y // 2:-y // 2]  # remove padding and return


# ----------------------------------------------------
# Main Execution
# ----------------------------------------------------

# Load grayscale image
image_path = get_file_path()
image = Image.open(image_path).convert("L")
image_array = np.asarray(image)

# Prompt user for initial intensity distribution
while True:
    beam = input('Initial intensity distribution (gaussian/plane): ').strip().lower()
    if beam in ('gaussian','g'):
        source_amplitude = gaussian_profile(image_array.shape, 300)
        break
    elif beam in ('plane','plane wave','p'):
        source_amplitude = np.ones_like(image_array)
        break
    else:
        print('ERROR: Enter "gaussian" or "plane".')

# Prompt user for number of iterations
while True:
    max_iters = input('How many iterations?:')
    try:
        max_iters = int(max_iters)
    except:
        print('ERROR: Enter an integer')
    else:
        break

# Run Gerchberg-Saxton algorithm
phase = gs(image_array, max_iters, source_amplitude)

# Extract and normalize the phase to 0–128 for visualization
phase_normalized_scaled = (((phase + np.pi) / (2 * np.pi)) * 128).astype(np.uint8)  # maps directly to 128
phase_normalized_scaled = np.flip(phase_normalized_scaled, axis=0) # vertical flip of phase map to make hologram right side up

# Save and display the phase map
phase_map = Image.fromarray(phase_normalized_scaled)
input_path = Path(image_path)

beam_name = "gaussian" if beam.startswith("g") else "plane"

output_path = input_path.with_name(
    f"{input_path.stem}_{beam_name}_{max_iters}iterations_phasemap.png"
)

phase_map.save(output_path)

print(f"Phase map saved to:\n{output_path}")

phase_map.show()

# Reconstruct far-field intensity for verification
reconstructed_near_field = source_amplitude * np.exp(1j * phase)  # reconstruct complex field from phase
far_field = np.fft.fftshift(np.fft.fft2(np.fft.ifftshift(reconstructed_near_field)))  # proper FFT with shifts
intensity = np.abs(far_field) ** 2
normalized_intensity = (intensity / np.max(intensity) * 255).astype(np.uint8)
normalized_intensity = np.flip(normalized_intensity, axis=0)
Image.fromarray(normalized_intensity).show()

