import pandas as pd
import numpy as np
from scipy.signal import stft

import matplotlib.pyplot as plt

class Transformer():

  
    def fourier_transform(df):
       
        # Getting rid of "Time" column
        df = df.drop('Time', axis=1)

        fft_results = {}

        for col in df.columns:
            fft_results[col] = np.fft.fft(df[col], n= 2000)


        # Convert results to a DataFrame for easier plotting
        fft_df = pd.DataFrame(fft_results)
       
        
        #adding "Frequency" column in place of "Time"
        N = len(fft_df)
        freqs = np.fft.fftfreq(N, d=1/300) #for 300 records per sec of DSI

        fft_df["Frequency"] = freqs

        return fft_df
    

    def short_time_f_t(df, seg_size, column_name):

        df = df.drop('Time', axis=1)

        results = {}

        for column in df.columns:
            f, t, Zxx = stft(df[column], fs = 300, nperseg = seg_size)
            results[column] = (f, t, Zxx)

        stft_df = pd.DataFrame(results)

        print(stft_df)

        f, t, Zxx = results[column_name]
        plt.pcolormesh(t, f, np.abs(Zxx), shading='gouraud')
        plt.title(f'STFT of'+ column_name)
        plt.ylabel('Frequency [Hz]')
        plt.xlabel('Time [sec]')
        plt.colorbar(label='Amplitude')
        plt.show()


        ft_df= Transformer.fourier_transform(df)
        
        fft_results = {}
        for col in df.columns:
            fft_results[col] = np.fft.fft(df[col], n= 2000)
        
        df = pd.DataFrame(fft_results)
        
        df.index = df.index
        df['Time'] = (df.index + 1) / 300
        return df
