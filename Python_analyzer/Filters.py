import pandas as pd
import numpy as np
import scipy.signal as sig

import matplotlib.pyplot as plt

class Filterer():
    
    def low_pass_filter(data, cutoff, fs, order=4):
        nyquist = 0.5 * fs  # Nyquist frequency
        normal_cutoff = cutoff / nyquist
        b, a = sig.butter(order, normal_cutoff, btype='low', analog=False)
        return sig.filtfilt(b, a, data.tolist())
    

    def high_pass_filter(data, cutoff, fs, order=4):
        nyquist = 0.5 * fs  # Nyquist frequency
        normal_cutoff = cutoff / nyquist
        b, a = sig.butter(order, normal_cutoff, btype='high', analog=False)
        return sig.filtfilt(b, a, data.tolist())