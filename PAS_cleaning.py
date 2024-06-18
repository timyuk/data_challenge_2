import json

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
import pickle
import re
import requests
import sys

PAS_detailed_names = ['PAS_ward_level_FY_15_17.csv', 'PAS_ward_level_FY_17_18.csv', 'PAS_ward_level_FY_18_19.csv', 'PAS_ward_level_FY_19_20.csv', 'PAS_ward_level_FY_20_21.csv']
# CREATE merged_PAS file of detailed
def create_merged_PAS():
    """Creates merged PAS file of detailed PAS data"""
    directory = r'crime_data/'  # Replace with your directory path
    dfs = []
    check_which_missing = PAS_detailed_names.copy()
    for filename in os.listdir(directory):
        if filename in PAS_detailed_names:
            check_which_missing.remove(filename)
            filepath = os.path.join(directory, filename)
            df = pd.read_csv(filepath)
            dfs.append(df)
    if check_which_missing:
        print(f'Missing PAS ward level files: {", ".join(check_which_missing)}')
    # Concatenate all dataframes in the list
    merged_df = pd.concat(dfs, ignore_index=True)

    # Save the merged DataFrame to a PKL file
    output_file = r'crime_data/merged_PAS.pkl'
    merged_df.to_pickle(output_file)
    print(f"Merged DataFrame saved to {output_file}")


create_merged_PAS()  # <-- uncomment to create file


# PREPROCESSING
# Function to preprocess the datetime object
def extract_datetime(text):
    """Extract the month and year of each entry."""
    match = re.search(r'\((\w{3}) (\d{4})\)', text)
    if match:
        month_str = match.group(1)
        year = match.group(2)
        dt = pd.to_datetime(f"{month_str} {year}", format="%b %Y")
        return dt
    return None


# Dropping and cleaning columns
def pre_process(df_og, df_stats):
    """Preliminary preprocessing of the merged files"""

    # Create Year-Month column like in other/crime files
    df_og["MONTH"] = df_og["MONTH"].apply(extract_datetime)
    df = df_og.copy()
    df['Year-Month'] = pd.to_datetime(df["MONTH"]).dt.date

    # Dropping unnecessary or duplicate columns
    df.drop(['Unnamed: 0', 'interview_date', 'FinancialYear', 'BOROUGHNEIGHBOURHOODCODED', 'C2', 'Quarter', 'quarter',
             'Quarter1.1', 'MONTH', 'ward_unique', 'WARD_1', 'WARD_0', 'BOROU1'], inplace=True, axis=1)
    df.drop(list(df.filter(regex='WT')), axis=1, inplace=True)  # removing unknown WT questions (just weights)

    # Dropping columns with too little variety in answers
    df = df.replace({'-': np.nan, 'Not Asked': np.nan, 'Not asked': np.nan, 'Don\'t know': np.nan})
    # for col in df.columns:
    #     if len(df[col].unique()) == 1 or len(df[col].unique()) == 2:
    #         df.drop(col, inplace=True, axis=1)

    # Adding ISO week numbers
    df["Week"] = pd.to_datetime(df["Week"].str.split("-", expand=True)[0], format="%d/%m/%Y").dt.isocalendar().week

    # Copy DF to stop performance issues due to fragmentation
    df2 = df.copy()

    # Getting Borough and removing Neighbourhood (too much cleaning, too few values)
    df2["Borough"] = df2["BOROUGHNEIGHBOURHOOD"].str.split("-", expand=True, n=1)[0]
    df2.drop(['BOROUGHNEIGHBOURHOOD'], inplace=True, axis=1)

    # Removing unnecessary white space in string columns
    df_str = df2[['Borough', 'ward_n', 'ward', 'SOA1', 'SOA2']]  # SOA1 and 2?? not in 2015_17 data
    df2[df_str.columns] = df_str.apply(lambda x: x.str.strip())

    # Quick stats on the dataframe
    if df_stats:
        print(df2.info())
        print(df2.describe())
        print(df2.head(40))
        print(df2.columns)
        print(df2.shape)

        for col in df2.columns:
            print(col)
            print("Number nans:", df2[col].isna().sum())
            print("Percentage nans:", df2[col].isna().sum() / df2.shape[0])
            print(df2[col].unique())
            print(len(df2[col].unique()))
            print("---------------------------------------------------------------")

    return df2


# PICKING QUESTIONS
# Function to handle different column types
def get_unique_values(column):
    # Check if the first element is list-like
    if isinstance(column.iloc[0], list):
        return column.apply(str).unique()  # Convert lists to strings
    # Check if the first element is a dictionary
    elif isinstance(column.iloc[0], dict):
        return column.apply(str).unique()  # Convert dictionaries to strings
    else:
        return column.unique()


def get_questions(df_new, df_stats):
    df_list = df_new.columns.tolist()

    # List with open answer questions (or loop questions)
    multi_q = ["Q143", "PQ135", "Q147", "Q145", "Q155", "Q154", "Q147", "Q136", "Q150", "Q139", "Q135", "Q61", "Q149",
               "Q109", "Q190", "Q98" "Q79", "Q191", "Q192", "Q119", "NQ1", "Q90"]
    multi_qs = []

    for q in multi_q:
        result = [item for item in df_list if q in item]
        multi_qs += result

    # Cherry-picked list of questions to keep based on effectiveness, demographics and possible underreporting
    questions = [
        "NQ146", "Q144", "Q141", "Q62A", "Q62E", "Q62TG", "Q62C", "NQ135BD", "Q60", "NQ133A", "Q131",
        "Q79B", "Q79D", "Q79E", "Q79J", "Q79I", "Q79G", "Q65", "Q79C", "NQ21", "RQ80E", "NQ143", "NNQ27C", "Q13",
        "NNQ27E", "Q37", "Q39A_2", "NQ43", "NQ44A", "NQ45A", "Q15", "Q62F", "Q62H", "Q62TJ", "XQ145", "Q201H"
    ]

    # Extra df info questions
    extra_q = ["Year-Month", "ward", "ward_n", "Borough"]

    # Create the final questions dataframe
    all_columns = list(set(extra_q + questions + multi_qs))
    df = df_new[all_columns]
    df = df.dropna(axis=1, how='all')

    # Define columns2 to inspect
    columns2 = ['NQ135BD', 'NQ143', 'NPQ135A', 'NPQ135B', 'NPQ135C', 'NQ147r']

    # Quick stats on the dataframe (fixed from error of some column types)
    df_stats = False
    if df_stats:
        print(df.info())
        print(df.describe())
        print(df.head())
        print(df.columns)
        print(df.shape)

        filtered_list = [item for item in df.columns.tolist() if item not in columns2]

        for col in filtered_list:
            print(col)
            print("Number nans:", df[col].isna().sum())
            print("Percentage nans:", df[col].isna().sum() / df.shape[0])
            print(df[col].unique())
            print(len(df[col].unique()))
            print("---------------------------------------------------------------")

        for col in columns2:
            print("---------------------------------------------------------------")
            try:
                unique_values = get_unique_values(df[col])
                print(f"Unique values in column {col}: {unique_values}")
            except Exception as e:
                print(f"Error processing column {col}: {e}")
                print(f"Number of unique values in {col}: {len(unique_values)}")

    return df


# Save cleaned file as a pickle file
try:
    og_data = pd.read_pickle(r'crime_data\merged_PAS.pkl')
except FileNotFoundError:
    print('File "merged_PAS.pkl" was not found, uncomment line 32 to create this file')
    sys.exit(1)
df_og = pre_process(og_data, False)
df_og['Year-Month'] = pd.to_datetime(df_og['Year-Month'], format='%Y-%m-%d')

# Combining question (who did you report a crime to) answers
under_q = ['SQ109CAA', 'SQ109CAB', 'SQ109CAC', 'SQ109CAD', 'SQ109CAE', 'SQ109CAF']
result = df_og[under_q[0]].combine_first(df_og[under_q[1]])
result1 = result.combine_first(df_og[under_q[2]])
result2 = result1.combine_first(df_og[under_q[3]])
result3 = result2.combine_first(df_og[under_q[4]])
result4 = result3.combine_first(df_og[under_q[5]])

df_og["SQ109CAA"] = result4
df_og.drop(['SQ109CAB', 'SQ109CAC', 'SQ109CAD', 'SQ109CAE', 'SQ109CAF'], inplace=True, axis=1)


# Fix missing boroughs in final dataset
def fix_boroughs(PAS_detailed):
    """Fix missing boroughs"""

    ward_borough_old = {}
    for i, ward in enumerate(PAS_detailed['ward'].unique().tolist()):
        print(i)  # print to check each ward
        borough = requests.get(f'https://findthatpostcode.uk/areas/{ward}.json').json()['data']['attributes']['parent']
        ward_borough_old[ward] = borough
    PAS_detailed['Borough'] = PAS_detailed['ward'].apply(lambda x: ward_borough_old[x])
    PAS_detailed.to_pickle('PAS_detailed2_fixed_borough.pkl')

    borough_name_dict = {}
    for i, borough in enumerate(PAS_detailed['Borough'].unique().tolist()):
        print(i)  # print to check each borough
        borough_name = requests.get(f'https://findthatpostcode.uk/areas/{borough}.json').json()['data']['attributes'][
            'name']
        borough_name_dict[borough] = borough_name
    PAS_detailed['Borough name'] = PAS_detailed['Borough'].apply(lambda x: borough_name_dict[x])
    PAS_detailed.to_pickle('PAS_detailed2_fixed_borough.pkl')

# Fix missing boroughs in final dataset without api
def fix_boroughs_without_api(PAS_detailed):
    """Fix missing boroughs"""

    with open("instead_of_api/ward_borough_old.json", "r") as file:
        ward_borough_old = json.load(file)
    PAS_detailed['Borough'] = PAS_detailed['ward'].apply(lambda x: ward_borough_old[x])
    PAS_detailed.to_pickle('PAS_detailed2_fixed_borough.pkl')

    with open("instead_of_api/borough_name.json", "r") as file:
        borough_name_dict = json.load(file)
    PAS_detailed['Borough name'] = PAS_detailed['Borough'].apply(lambda x: borough_name_dict[x])
    PAS_detailed.to_pickle('PAS_detailed2_fixed_borough.pkl')


# Save cleaned file as a pickle file
# df_fin = fix_boroughs(df_og)
df_fin = fix_boroughs_without_api(df_og)
df_og.to_pickle(r"crime_data\PAS_detailed2_fixed_borough.pkl")

# # MEASURES DATAFRAME
# # Load and create dataframes with preprocessing
# df = pd.read_pickle(r'crime_data\PAS_detailed2.pkl')
#
# # Ward-level PAS data
# df_measures = df[["Year-Month", "Borough", "ward_n", "Q62A", "Q62E", "Q62TG", "Q62C", "Q60", "Q131", "NQ135BD",
#                   "NQ133A"]].copy()
# df_measures = df_measures.replace({'#N/A': np.nan, '': np.nan, 'Westminster': "City of Westminster"})
# df_measures = df_measures[~df_measures["Borough"].isna()]
#
# # Mappings for calculations
# mappings = {
#     'Tend to agree': 1,
#     'Strongly agree': 1,
#     'Neither agree nor disagree': 0,
#     'Tend to disagree': 0,
#     'Strongly disagree': 0
# }
#
# mappings2 = {
#     'Excellent': 1,
#     'Good': 1,
#     'Fair': 0,
#     'Poor': 0,
#     'Very poor': 0
# }
#
# mappings3 = {
#     'Yes': 1,
#     'No': 0
# }
#
# mappings4 = {
#     'Very well informed': 1,
#     'Fairly well informed': 1,
#     'Not at all informed': 0
# }
#
# # Converting measure columns for calculations
# df_measures["Q62A"] = df_measures["Q62A"].map(mappings)
# df_measures["Q62E"] = df_measures["Q62E"].map(mappings)
# df_measures["Q62TG"] = df_measures["Q62TG"].map(mappings)
# df_measures["Q62C"] = df_measures["Q62C"].map(mappings)
# df_measures["NQ135BD"] = df_measures["NQ135BD"].map(mappings)
# df_measures["Q60"] = df_measures["Q60"].map(mappings2)
# df_measures["NQ133A"] = df_measures["NQ133A"].map(mappings3)
# df_measures["Q131"] = df_measures["Q131"].map(mappings4)
#
#
# def calc_wards(df3, questions):
#     results = []
#     for q in questions:
#         for b in df3["Borough"].unique():
#             borough_df = df3[["Year-Month", "Borough", "ward_n", q]][df3["Borough"] == b]
#
#             for w in borough_df["ward_n"].unique():
#                 ward_df = borough_df[borough_df["ward_n"] == w]
#                 perc = ward_df[q].sum() / ward_df.shape[0]
#                 results.append({
#                     "Year-Month": ward_df["Year-Month"].iloc[0],
#                     "Borough": b,
#                     "ward_n": w,
#                     "Measure": q,
#                     "Proportion": perc
#                 })
#
#     # Dataframe to return
#     result_df = pd.DataFrame(results)
#     return result_df
#
#
# # Getting ward level measure values
# questions = ["Q62A", "Q62E", "Q62TG", "Q62C", "NQ135BD", "Q60", "Q131", "NQ133A"]
# result_df = calc_wards(df_measures, questions)
#
# # Renaming questions to their measure names
# result_df["Measure"] = result_df["Measure"].map({
#     "Q62A": "Relied on to be there",
#     "Q62E": "Understand issues",
#     "Q62TG": "Listen to concerns",
#     "Q62C": "Treat everyone fairly",
#     "NQ135BD": "Trust MPS",
#     "Q60": "'Good job' local",
#     "NQ133A": "Contact ward officer",
#     "Q131": "Informed local"
# })
#
# # # Save cleaned file as a pickle file
# # result_df.to_pickle(r"crime_data\PAS_ward.pkl")
