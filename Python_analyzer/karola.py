import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Sample DataFrame
data = {
    'Column1': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    'Column2': [7, 8, 9, 10, 11, 12, 13, 14, 15, 16],
    'Column3': [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
}
df = pd.DataFrame(data)

# Function to compute and plot Fourier Transform of a specified column with frequency in Hz
def plot_column_stft(column_name, Fs):
    """
    Plots the Fourier Transform magnitude of a specified column with frequency on the x-axis in Hz.

    Parameters:
    - column_name (str): Name of the column to plot.
    - Fs (float): Sampling rate in Hz.
    """
    # Check if the column exists in the DataFrame
    if column_name in df.columns:
        # Compute the Fourier Transform for the selected column
        fft_result = np.fft.fft(df[column_name])
        
        # Calculate the magnitude of the Fourier Transform
        magnitude = np.abs(fft_result)
        
        # Generate frequency bins in Hz
        N = len(df[column_name])  # Number of samples
        freqs = np.fft.fftfreq(N, d=1/Fs)
        
        # Only take the positive half of the spectrum
        half_N = N // 2
        freqs = freqs[:half_N]
        magnitude = magnitude[:half_N]
        
        # Plot the magnitude of the Fourier Transform
        plt.figure(figsize=(8, 4))
        plt.plot(freqs, magnitude)
        plt.title(f'Fourier Transform Magnitude of {column_name}')
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Magnitude')
        plt.show()
    else:
        print(f"Column '{column_name}' not found in DataFrame.")

# Example usage
# Replace 'Column1' with the name of the column you want to plot, and set the sampling rate (e.g., 10 Hz)
plot_column_stft('Column1', Fs=10)  # Adjust Fs as per your data's sampling rate