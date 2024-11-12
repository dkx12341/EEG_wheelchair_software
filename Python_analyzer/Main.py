import pandas as pd
import seaborn as sns

import numpy as np
import csv
from Plots import Plotter


def main():
    
    data = pd.DataFrame
    data = get_data_frame("C:\Repos\EEG_applications\Python_analyzer\Kontrolny_Mruganie_3_raw.csv")

    #Plotter.plot_linear_column(data, "C3")

    ft_data = fourier_transform(data)
    #print(ft_data["C3"])
    Plotter.plot_fourier_column(ft_data,"C3",300)

    print("yay")

def get_data_frame(file_path):
    df = read_from_csv(file_path)
    df = create_time_index(df)
    return df  

def read_from_csv(file_path):
    df = pd.read_csv(file_path,header=1, skiprows=range(15))
    df = df.iloc[:, :25]
    return df

def create_time_index(df):
    df.index = df.index + 1  # This will shift the index by 1, so index starts from 1
    df.iloc[:, 0] = df.index / 300
    df = df.set_index(df.columns[0])
    return df

def fourier_transform(df):
    fft_results = {}

    for col in df.columns:
        fft_results[col] = np.fft.fft(df[col], n= 3000)

    # Convert results to a DataFrame for easier plotting
    fft_df = pd.DataFrame(fft_results)
    #filtering
    #fft_df = fft_df.iloc[1000:]
    return fft_df

if __name__ == "__main__":
    main()
