import pandas as pd
import seaborn as sns

import numpy as np
import csv
from Plots import Plotter


def main():
    print("Hello World!\n")
    data = pd.DataFrame
    data = get_data_frame("C:\Repos\EEG_applications\Python_analyzer\Kontrolny_Mruganie_3_raw.csv")
    #plot_linear(data)
    ft_data = fourier_transform(data)
    print(ft_data["C3"])
    Plotter.plot_fourier_colmn(ft_data,"C3",300)
    print("yay")

def get_data_frame(file_path):
    dataList = read_from_csv(file_path)
    dataList = slice_array(dataList)
    dataList = create_time_index(dataList)
    df = pd.DataFrame(dataList[1:], columns=dataList[0])  # Use the first row as columns
    df.set_index("Time", inplace=True)  
    return df  

def read_from_csv(file_path):
    with open(file_path, newline='') as csvfile:
        data = list(csv.reader(csvfile))
    return data

def slice_array(list):
    list = list[16:]
    list = [row[:25] for row in list]
    return list

def create_time_index(list):
    i = 0
    TimeDelay = 333
    for i in range(1, len(list)):
        row = list[i]
        row[0] = i* TimeDelay
        i = i+1
        
    return list

def fourier_transform(df):
    fft_results = {}

    for col in df.columns:
        fft_results[col] = np.fft.fft(df[col])

    # Convert results to a DataFrame for easier plotting
    fft_df = pd.DataFrame(fft_results)
    #filtering
    fft_df.drop([0,50])
    return fft_df

if __name__ == "__main__":
    main()
