
def get_eeg_data(file_path):
     
    eeg_broken_data = ""
    orginal_file_data= ""
    phrase = "Time,P3,C3,F3,Fz,F4,C4,P4,Cz,CM,A1,Fp1,Fp2,T3,T5,O1,O2,X3,X2,F7,F8,X1,A2,T6,T4,Trigger,Time_Offset,ADC_Status,ADC_Sequence,Event,Comments"
    found_phrase = False
    with open(file_path, 'r') as file:
            for line in file:
                if found_phrase:
                    eeg_broken_data += line
                elif phrase in line:
                    orginal_file_data += line
                    found_phrase = True
                else:
                    orginal_file_data += line
    return (orginal_file_data, eeg_broken_data)

def fix_eeg_data(data_string):
    eeg_fixed_data_table = []
    rep_comma = True
    for char in data_string:
            if char == ',' or char == '\n':
                if char == '\n':
                     rep_comma = True
                     eeg_fixed_data_table.append('\n')

                elif  rep_comma:
                    eeg_fixed_data_table.append('.')  # Replace the second comma
                    rep_comma = False

                else:
                    eeg_fixed_data_table.append(',')  # Keep the first comma
                    rep_comma = True
            else:
                eeg_fixed_data_table.append(char)  

    return ''.join(eeg_fixed_data_table)

def overwrite_csv_file(file_path,csv_contents):
       with open(file_path, 'w') as file:
                file.writelines(csv_contents[0])
                file.writelines(csv_contents[1])
          
    
def fix_DSI_cvs_temp(file_path):
    
    csv_contents = get_eeg_data(file_path)
    fixed_csv_contents= (csv_contents[0],fix_eeg_data(csv_contents[1]))
    overwrite_csv_file(file_path, fixed_csv_contents)

    





fix_DSI_cvs_temp("C:\Repos\EEG_applications\Python_analyzer\skupienie2_WS_raw.csv")