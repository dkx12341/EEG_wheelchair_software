import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mne

data = mne.io.read_raw_edf("C:\Repos\EEG_applications\Python_analyzer\Flash_10hz_WS_raw.edf")
print(data)