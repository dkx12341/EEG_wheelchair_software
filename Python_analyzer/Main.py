import pandas as pd
import mne
import pyedflib
from Plots import Plotter
from Transforms import Transformer
from Filters import Filterer


def main():
    data = pd.DataFrame
    data = get_data_frame("C:\Repos\EEG_applications\Python_analyzer\Kontrolny_Mruganie_3_raw.csv")
    Plotter.plot_linear_column(data, "C3")
    data = filter_data(data)
    Plotter.plot_linear_column(data, "C3")
    #f_data = Transformer.time_view_filtered(data)
    #Plotter.plot_linear_column(data, "C3")
  

    #ft_data = Transformer.fourier_transform(data)
    #stft_data = Transformer.short_time_f_t(data, 16, "C3")

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
<<<<<<< HEAD
    df.index = df.index + 1  # This will shift the index by 1, so index starts from 1
    df["Time"] = df.index/300
    print(df["Time"])
=======
    df.index = df.index
    df['Time'] = (df.index + 1) / 300
>>>>>>> 53742c8b8f006dd650a7b7de82f43ba628d25017
    return df

def filter_data(df):
    fs = 300
    cutoff_low = 100  # Low-pass filter cutoff frequency (100 Hz)
    cutoff_high = 1  # High-pass filter cutoff frequency (1 Hz)

    for column in df.columns[1:]:
        df[column] = Filterer.low_pass_filter(df[column],cutoff=cutoff_low, fs=fs)
        df[column] = Filterer.high_pass_filter(df[column],cutoff=cutoff_high, fs=fs)

    return df

if __name__ == "__main__":
    main()
