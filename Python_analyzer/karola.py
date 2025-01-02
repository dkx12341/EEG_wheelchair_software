import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mne

data = mne.io.read_raw_edf("C:\Repos\EEG_applications\Python_analyzer\skupienie2_WS_raw.edf", preload=True)


data.plot( title='Raw EDF Data', show=True, block=True, picks=['EEG P3-Pz'])

print("hello")