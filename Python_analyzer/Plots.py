import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np


class Plotter():
    def plot_linear_all(df):

        df=df.astype(float)
        num_columns = len(df.columns)
        fig, axes = plt.subplots(num_columns, 1, figsize=(6, num_columns * 4))
        for i, col in enumerate(df.columns):
            sns.lineplot(data=df[col], ax=axes[i])
            axes[i].set_title(f'Line Plot of {col}')
            axes[i].set_xlabel('Time')
            axes[i].set_ylabel(col)
        plt.tight_layout()
        plt.show()

    def plot_linear_column(df,column_name):
        if column_name in df.columns:
            sns.lineplot(data=df[column_name])
            plt.title('Line Plot of'+ column_name)
            plt.xlabel('Time')
            plt.ylabel('Voltage')
            plt.show()
        else:
            print(f"Column '{column_name}' not found in DataFrame.")


  
    def plot_fourier_all(df):
        num_columns = len(df.columns)
        fig, axes = plt.subplots(num_columns, 1, figsize=(8, num_columns * 4))

        for i, col in enumerate(df.columns):
            # Compute the magnitude of the FFT (absolute value)
            magnitude = np.abs(df[col])
        
        # Plot the magnitude of the Fourier Transform
            axes[i].plot(magnitude)
            axes[i].set_title(f'Fourier Transform Magnitude of {col}')
            axes[i].set_xlabel('Frequency')
            axes[i].set_ylabel('Magnitude')
        plt.tight_layout()
        plt.show()


    def plot_fourier_column(df,column_name, Fs): 
        """
        Plots the Fourier Transform magnitude of a specified column with frequency on the x-axis in Hz.

        Parameters:
        - column_name (str): Name of the column to plot.
        - Fs (float): Sampling rate in Hz, in DSI 24 it is 300.
        """
        # Check if the column exists in the DataFrame
        if column_name in df.columns:
            # Number of samples
            N = len(df[column_name])

            # Calculate the magnitude of the Fourier Transform and scale by the number of samples
            magnitude = np.abs(df[column_name]) / N  # Scaling to retain µV
            
            # Generate frequency bins in Hz
            freqs = np.fft.fftfreq(N)#, d=1/Fs)
            
            # Only take the positive half of the spectrum
            half_N = N // 2
            freqs = freqs[:half_N]
            magnitude = magnitude[:half_N]
            
            # Plot the magnitude of the Fourier Transform
            plt.figure(figsize=(8, 4))
            plt.plot(freqs[50:], magnitude[50:])
            plt.title(f'Fourier Transform Magnitude of {column_name}')
            plt.xlabel('Frequency (Hz)')
            plt.ylabel('Magnitude (µV)')
            plt.show()
        else:
            print(f"Column '{column_name}' not found in DataFrame.")

        
    

