import pandas as pd
import sys
import matplotlib.pyplot as plt

def main():
    print("Hello World!\n")

    EEGMeasurments = pd.DataFrame
    EEGMeasurments = GetDataFrame("C:\Repos\EEG_applications\Python_analyzer\Kontrolny_Mruganie_3_raw.csv")
    
    PlotDataFrame(EEGMeasurments)
    
    print("yay")


def GetDataFrame (FilePath):
    df = ReadFromCsv(FilePath)
    df = SliceDataFrame(df)
    #WriteToCsv(FilePath, df)
    #df = ReadFromCsv(FilePath)
    return df
    
def SliceDataFrame(df= pd.DataFrame):
    df = df[15: df.shape[0]]   
    df.columns = df.iloc[0]
    df = df[1:df.shape[0]]
    df.drop(df.iloc[:1,25:],inplace = True, axis=1)
    MeasureArray = df.to_numpy()
    return df

def ReadFromCsv(FilePath):
    df = pd.DataFrame 
    df = pd.read_csv(FilePath, on_bad_lines='skip')
    return df

def WriteToCsv(FilePath, df= pd.DataFrame):
    df.to_csv(FilePath)

def PlotDataFrame(df):
    df=df.astype(float)
    df.plot()
    plt.show()

    

main()