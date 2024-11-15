import pandas as pd
import seaborn as sns

import numpy as np
import csv
from Plots import Plotter
from Transforms import Transformer


def main():
    
    data = pd.DataFrame
    data = get_data_frame("C:\Repos\EEG_applications\Python_analyzer\Kontrolny_Mruganie_3_raw.csv")

    Plotter.plot_linear_column(data, "C3")

    ft_data = Transformer.fourier_transform(data)
 
    Plotter.plot_fourier_column(ft_data,"C3",300)
    #Plotter.plot_short_time_fourier_all(ft_data, 300)
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



if __name__ == "__main__":
    main()
