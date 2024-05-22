
import dash
from dash import Dash, dcc, html, Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
# Load the dataset
file_path = '/Users/egehankabacaoglu/Desktop/MPS Borough Level Crime (Historical).csv'  # Ensure this path matches where you've saved the file
try:
    # Try reading the CSV with comma as delimiter
    data = pd.read_csv(file_path, delimiter=',')
except Exception as e:
    print(f"An error occurred: {e}")
    # If the first attempt fails, it might be due to incorrect delimiter handling
    # You can try different delimiters here, e.g., `;`, `|`, etc., or handle a more complex situation
    data = pd.read_csv(file_path, delimiter=';')  # Adjust as necessary based on the actual file

# Check the structure of the DataFrame
print("Data loaded with the following structure:")
print(data.info())

# If the data is still not in a proper format, you may need to manually split the 'bad' column
if data.shape[1] == 1:
    # Split the single column data into multiple columns if everything ended up in one column
    data = data[data.columns[0]].str.split(',', expand=True)
    # Optionally set the first row as header if it looks like it contains header information
    data.columns = data.iloc[0]  # Setting the first row as the column names
    data = data[1:]  # Removing the first row after setting it as header

# Print the first few rows to verify the format
print("\nPreview of formatted data:")
print(data.head())

# Define the path for the new cleaned CSV file
new_file_path = 'Cleaned_MPS_Borough_Level_Crime.csv'

# Save the cleaned DataFrame to a new CSV file
data.to_csv(new_file_path, index=False)
print(f"\nData successfully saved to {new_file_path}")

