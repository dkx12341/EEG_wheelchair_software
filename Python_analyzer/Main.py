import pandas as pd
import mne
import string
from Plots import Plotter
from Transforms import Transformer
from Filters import Filterer


def main():
    
    data = pd.DataFrame
    data = get_data_frame("C:\Repos\EEG_applications\Python_analyzer\skupienie2_WS_raw.csv")
    data.info()
    #data.plot()
    Plotter.plot_linear_column(data, "P3")
    
    #Plotter.plot_linear_column(data, "C3")


    print("yay")



def get_data_frame(file_path):
    df = read_from_csv(file_path)
    
    return df  

def read_from_csv(file_path):
    df = pd.read_csv(file_path,header=1, skiprows=range(15))
    df = df.iloc[:, :25]
    return df



if __name__ == "__main__":
    main()
