import pandas as pd
import os
import sys
PAS_initinal_names = ['PAS_T&Cdashboard_to Q3 23-24.xlsx', 'PAS.xlsx']
def convert_PAS_to_pkl():
    directory = r'data/'
    count =0
    for filename in os.listdir(directory):
        if filename in PAS_initinal_names:
            count+=1
            print("File found, it will take some time")
            filepath = os.path.join(directory, filename)
            PAS = pd.read_excel(filepath, 'Borough')
            PAS = PAS.dropna(axis=1)
            PAS['Date'] = pd.to_datetime(PAS['Date'])
            new_filepath = os.path.join(directory, 'PAS.pkl')
            PAS.to_pickle(new_filepath)
    if not count:
        print(f"PAS file not found. Please add it to /data/ subdirectory. It should have one of the names {', or '.join(PAS_initinal_names)}\n\n"
              f"The directory should look like this: /data challenge 2/data/PAS.xlsx")
        sys.exit(1)
convert_PAS_to_pkl()