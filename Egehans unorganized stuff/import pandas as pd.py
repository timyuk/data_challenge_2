import pandas as pd

# Load the CSV files
homicides_df = pd.read_csv('/Users/egehankabacaoglu/Desktop/Data Challenge Files For Review (1)/Code/data_challenge_2/Homicide_Related_Crimes.csv')
trust_police_df = pd.read_csv('/Users/egehankabacaoglu/Desktop/Data Challenge Files For Review (1)/Code/data_challenge_2/PAS.csv')


# Convert dates to datetime objects for easier manipulation
homicides_df['Date'] = pd.to_datetime(homicides_df['Date'])
trust_police_df['Date'] = pd.to_datetime(trust_police_df['Date'])

# Define the overlapping date range
overlap_start = pd.Timestamp('2014-12-31')
overlap_end = pd.Timestamp('2022-01-01')

# Filter the dataframes to include only the overlapping date range
filtered_homicides_df = homicides_df[(homicides_df['Date'] >= overlap_start) & (homicides_df['Date'] <= overlap_end)]
filtered_trust_police_df = trust_police_df[(trust_police_df['Date'] >= overlap_start) & (trust_police_df['Date'] <= overlap_end)]

# Aggregate homicide counts by borough
homicide_aggregated = filtered_homicides_df.groupby('LookUp_BoroughName')['Homicide_Counts'].sum().reset_index()

# For trust data, take the average of Proportion per borough
trust_aggregated = filtered_trust_police_df.groupby('Borough')['Proportion'].mean().reset_index()

# Merge the two datasets for correlation analysis
merged_data = pd.merge(homicide_aggregated, trust_aggregated, left_on='LookUp_BoroughName', right_on='Borough', how='inner')

# Calculate total and average for the merged data separately
total_homicides = merged_data['Homicide_Counts'].sum()
average_proportion = merged_data['Proportion'].mean()

# Add a total row at the end of the dataframe for display purposes
total_row = pd.DataFrame([['Total', total_homicides, 'All Boroughs', average_proportion]], columns=merged_data.columns)
display_data = pd.concat([merged_data, total_row], ignore_index=True)

# Ensure only numeric columns are considered for correlation calculation excluding the total row
print(display_data)  # This includes the total row for display
print(merged_data[['Homicide_Counts', 'Proportion']].corr())  # This excludes the total row for accurate correlation


