import pandas as pd
import os

PAS_initinal_names = ['PAS_T&Cdashboard_to Q3 23-24.xlsx', 'PAS.xlsx']
def convert_PAS_to_pkl():
    directory = r'crime_data/'
    for filename in os.listdir(directory):
        if filename in PAS_initinal_names:
            print("File found, it will take some time")
            filepath = os.path.join(directory, filename)
            PAS = pd.read_excel(filepath, 'Borough')
            PAS = PAS.dropna(axis=1)
            PAS['Date'] = pd.to_datetime(PAS['Date'])
            new_filepath = os.path.join(directory, 'PAS.pkl')
            PAS.to_pickle(new_filepath)

convert_PAS_to_pkl()