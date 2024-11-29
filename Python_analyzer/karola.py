import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import pandas as pd
import numpy as np
from scipy.signal import butter, filtfilt

# Generate sample data
np.random.seed(42)
time = np.linspace(0, 10, 1000)  # Simulated time axis
signal = np.sin(2 * np.pi * 1 * time) + 0.5 * np.random.randn(1000)  # A noisy sine wave

# Create a DataFrame
df = pd.DataFrame({'time': time, 'signal': signal})

def low_pass_filter(data, cutoff, fs, order=4):
    nyquist = 0.5 * fs  # Nyquist frequency
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return filtfilt(b, a, data)


def high_pass_filter(data, cutoff, fs, order=4):
    nyquist = 0.5 * fs  # Nyquist frequency
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='high', analog=False)
    return filtfilt(b, a, data)

# Define parameters
fs = 100  # Sampling frequency (100 Hz)
cutoff_low = 2  # Low-pass filter cutoff frequency (2 Hz)
cutoff_high = 0.5  # High-pass filter cutoff frequency (0.5 Hz)

# Apply filters
df['low_pass_filtered'] = low_pass_filter(df['signal'], cutoff=cutoff_low, fs=fs)
df['high_pass_filtered'] = high_pass_filter(df['signal'], cutoff=cutoff_high, fs=fs)

import matplotlib.pyplot as plt

plt.figure(figsize=(12, 6))
plt.plot(df['time'], df['signal'], label='Original Signal', alpha=0.5)
plt.plot(df['time'], df['low_pass_filtered'], label='Low-Pass Filtered', linewidth=2)
plt.plot(df['time'], df['high_pass_filtered'], label='High-Pass Filtered', linewidth=2)
plt.legend()
plt.xlabel('Time (s)')
plt.ylabel('Signal Amplitude')
plt.title('Signal Filtering')
plt.grid()
plt.show()
