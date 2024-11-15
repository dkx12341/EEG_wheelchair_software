import pandas as pd
import numpy as np

class Transformer():
    
    def fourier_transform(df):
        fft_results = {}

        for col in df.columns:
            fft_results[col] = np.fft.fft(df[col], n= 1000)

        # Convert results to a DataFrame for easier plotting
        fft_df = pd.DataFrame(fft_results)
        
        
        return fft_df
