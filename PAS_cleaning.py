import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
import pickle
import re


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


# # Save cleaned file as a pickle file
# og_data = pd.read_pickle(r'crime_data\merged_PAS.pkl')
# df2 = pre_process(og_data, False)
# df2.to_pickle(r"crime_data\PAS_detailed.pkl")

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
    multi_q = ["Q143", "PQ135", "NQ147", "Q145", "Q155", "Q154", "Q147", "Q136", "Q150", "Q139", "Q135", "Q61", "Q149",
               "Q109", "Q190", "Q98" "Q79"]
    multi_qs = []

    for q in multi_q:
        result = [item for item in df_list if q in item]
        multi_qs += result

    # Cherry-picked list of questions to keep based on effectiveness, demographics and possible underreporting
    questions = [
        "NQ146", "Q144", "Q141", "Q62A", "Q62E", "Q62TG", "Q62C", "NQ135BD", "Q60", "NQ133A", "Q131",
        "Q79B", "Q79D", "Q79E", "Q79J", "Q79I", "Q79G", "Q65", "Q79C", "NQ21", "RQ80E", "NQ143", "NNQ27C", "Q13",
        "NNQ27E", "Q37", "Q39A_2", "NQ43", "NQ44A", "NQ45A", "Q15", "Q62F", "Q62H", "Q62TJ", "BQ90D", "BQ90DA", "XQ145",
        "NQ1I"
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


# # Load data
df_og = pd.read_pickle(r'crime_data\PAS_detailed.pkl')
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


# # Save cleaned file as a pickle file
# df_og.to_pickle(r"crime_data\PAS_detailed2.pkl")

# MEASURES DATAFRAME
# Load and create dataframes with preprocessing
df = pd.read_pickle(r'crime_data\PAS_detailed2.pkl')

# Ward-level PAS data
df_measures = df[["Year-Month", "Borough", "ward_n", "Q62A", "Q62E", "Q62TG", "Q62C", "Q60", "Q131", "NQ135BD",
                  "NQ133A"]].copy()
df_measures = df_measures.replace({'#N/A': np.nan, '': np.nan, 'Westminster': "City of Westminster"})
df_measures = df_measures[~df_measures["Borough"].isna()]

# Mappings for calculations
mappings = {
    'Tend to agree': 1,
    'Strongly agree': 1,
    'Neither agree nor disagree': 0,
    'Tend to disagree': 0,
    'Strongly disagree': 0
}

mappings2 = {
    'Excellent': 1,
    'Good': 1,
    'Fair': 0,
    'Poor': 0,
    'Very poor': 0
}

mappings3 = {
    'Yes': 1,
    'No': 0
}

mappings4 = {
    'Very well informed': 1,
    'Fairly well informed': 1,
    'Not at all informed': 0
}

# Converting measure columns for calculations
df_measures["Q62A"] = df_measures["Q62A"].map(mappings)
df_measures["Q62E"] = df_measures["Q62E"].map(mappings)
df_measures["Q62TG"] = df_measures["Q62TG"].map(mappings)
df_measures["Q62C"] = df_measures["Q62C"].map(mappings)
df_measures["NQ135BD"] = df_measures["NQ135BD"].map(mappings)
df_measures["Q60"] = df_measures["Q60"].map(mappings2)
df_measures["NQ133A"] = df_measures["NQ133A"].map(mappings3)
df_measures["Q131"] = df_measures["Q131"].map(mappings4)


def calc_wards(df3, questions):
    results = []
    for q in questions:
        for b in df3["Borough"].unique():
            borough_df = df3[["Year-Month", "Borough", "ward_n", q]][df3["Borough"] == b]

            for w in borough_df["ward_n"].unique():
                ward_df = borough_df[borough_df["ward_n"] == w]
                perc = ward_df[q].sum() / ward_df.shape[0]
                results.append({
                    "Year-Month": ward_df["Year-Month"].iloc[0],
                    "Borough": b,
                    "ward_n": w,
                    "Measure": q,
                    "Proportion": perc
                })

    # Dataframe to return
    result_df = pd.DataFrame(results)
    return result_df


# Getting ward level measure values
questions = ["Q62A", "Q62E", "Q62TG", "Q62C", "NQ135BD", "Q60", "Q131", "NQ133A"]
result_df = calc_wards(df_measures, questions)

# Renaming questions to their measure names
result_df["Measure"] = result_df["Measure"].map({
    "Q62A": "Relied on to be there",
    "Q62E": "Understand issues",
    "Q62TG": "Listen to concerns",
    "Q62C": "Treat everyone fairly",
    "NQ135BD": "Trust MPS",
    "Q60": "'Good job' local",
    "NQ133A": "Contact ward officer",
    "Q131": "Informed local"
})

# # Save cleaned file as a pickle file
# result_df.to_pickle(r"crime_data\PAS_ward.pkl")


# LINEAR ALGEBRA ATTEMPTS
# # b
# df_b = pd.read_pickle(r'crime_data\PAS.pkl')
# df_b = df_b.loc[0:9311, ['Date', 'Borough', 'Measure', 'Proportion']]
# df_b['Date'] = pd.to_datetime(df_b['Date'], format="%b %Y")
# df_b = df_b.loc[(df_b['Date'] <= '2020-01-01') & (df_b['Date'] >= '2015-03-31')]
#
#
# def solve_eq(df_b):
#     for borough in df_b["Borough"].unique():
#         df_use = df_b[df_b["Borough"] == borough]
#
#
#         for n in df_use["Date"].unique():
#             b = df_use.loc[(df_use["Date"] == n) & (df_use["Measure"] == "\"Good Job\" local"), "Proportion"].iloc[0]
#             print(n, b)


# q60 = df_measures[(df_measures["Borough"] == "Sutton") & (df_measures["Year-Month"] < '2015-06-30')
#                   & (df_measures["Year-Month"] >= '2015-03-31')]
# q60 = q60[["Year-Month", "Borough", "ward_n", "Q60"]][~q60["Q60"].isna()]
# # print(q60)
#
# dct = {}
# # print(q60.shape[0])
# for option in q60["Q60"].unique().tolist():  # Good job local
#     prop = (q60[q60["Q60"] == option].shape[0] / q60.shape[0])
#     # print(q60[q60["Q60"] == option].shape[0])
#     print(option, prop)
#     dct[option] = prop
#
# score = 1.5 * dct["Excellent"] + 1 * dct["Good"] + 0.25 * dct["Fair"] - 1 * dct["Poor"] - 2 * dct["Very poor"]
# print(score)

# RENAMING EACH QUESTION
# questions_dict = {
#     "Q62A": "Relied on to be there",
#     "Q62E": "Understand issues",
#     "Q62TG": "Listen to concerns",
#     "Q62C": "Treat everyone fairly",
#     "NQ135BD": "Trust MPS",
#     "Q60": "'Good job' local",
#     "NQ133A": "Contact ward officer",
#     "Q131": "Informed local",
#     "NQ146": "Highest level of qualification",
#     "Q144": "Renting, mortgage, own your home",
#     "Q141": "Number adults in household",
#     "Q136r": "Age band",
#     "Q139r": "Current Employment status",
#     "Q150r": "Sexual orientation",
#     "XQ135r": "Gender",
#     "Q79B": "Responding to emergencies promptly",
#     "Q79D": "Tackling gun crime",
#     "Q79E": "Supporting victims and witnesses",
#     "Q79J": "Tackling VAWG",
#     "Q79I": "Tackling hate crime",
#     "Q79G": "Tackling drug dealing and use",
#     "Q65": "Local patrols on bike or by foot",
#     "Q79C": "Good patrolling presence?",
#     "NQ21": "Safeness around patrolling officer?",
#     "RQ80E": "Heard about your local Policing Team?",
#     "NQ143": "Considered a career in the Met?",
#     "NNQ27E": "violence problem?",
#     "Q37": "gun crime problem",
#     "Q39A_2": "gangs problem",
#     "NQ43": "knife crime problem",
#     "NQ44A": "hate crime problem",
#     "NQ45A": "cyber crime problem",
#     "Q15": "ABS problem",
#     "Q62F": "Deal with things that matter to community",
#     "Q62H": "Police are helpful",
#     "Q62TJ": "Police are easy to contact"
# }

# list1 = list(questions_dict.keys())
# list1 = df.columns.tolist()
# # print(list(list1))
# list2 = [
#     "Q62A", "Q62E", "Q62TG", "Q62C", "Q60",
#     "Q62A", "Q62E", "Q62TG", "Q62C", "NQ135BD", "Q60", "NQ133A", "Q131",
#     "Q62A", "Q62E", "Q62TG", "Q62C", "NQ135BD", "Q60", "NQ133A", "Q131",
#     "XQ145", "NQ147", "Q155", "Q154", "NQ146", "UQ147", "Q136r", "Q139r", "Q144", "Q150r",
#     "NQ149", "Q141", "XQ135r", "Q79B", "Q79D", "Q79E", "Q79J", "Q79I", "Q79G", "Q65",
#     "Q79C", "NQ21", "RQ80E", "Q143", "NQ143", "NNQ27C", "Q13", "NNQ27E", "Q37", "Q39A_2",
#     "NQ43", "NQ44A", "NQ45A", "Q15", "PQ135", "Q62F", "Q62H", "Q62TJ"
# ]
#
#
# # Convert the lists to sets
# set1 = set(list1)
# set2 = set(list2)
#
# # Find elements in list1 but not in list2
# difference1 = set1 - set2
# # Find elements in list2 but not in list1
# difference2 = set2 - set1
#
# # Convert the sets back to lists if needed
# difference1_list = list(difference1)
# difference2_list = list(difference2)
#
# # Output the results
# print("Elements in list1 but not in list2:", difference1_list)
# print("Elements in list2 but not in list1:", difference2_list)

# ============================================================
