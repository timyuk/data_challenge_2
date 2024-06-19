
# Underreporting Project


## Setup Instructions

### 1. Install Dependencies
Ensure you have all necessary dependencies installed by running:
```sh
pip install -r requirements.txt
```

### 2. Create Data Directory
Create a subdirectory named `/data/` in the current `/data challenge 2/` directory to store the data files:
```sh
mkdir data
```

### 3. Download Data Files
Download the combined street-level crime dataset from Dropbox and place it in the `/data/` subdirectory:
- [Download london_street_with_city.pkl](https://www.dropbox.com/scl/fi/bl7omot3qr6mx9q2p6phy/london_street_with_city.pkl?rlkey=3p2hut7v0k25qhtijkwkol93c&st=13hupa6u&dl=0)

Ensure the following files are in the `/data/` subdirectory:
- `london_street_with_city.pkl`
- `PAS_T&Cdashboard_to Q3 23-24.xlsx` (or renamed to `PAS.xlsx`)
- The ward level PAS files:
  - `PAS_ward_level_FY_15_17.csv`
  - `PAS_ward_level_FY_17_18.csv`
  - `PAS_ward_level_FY_18_19.csv`
  - `PAS_ward_level_FY_19_20.csv`
  - `PAS_ward_level_FY_20_21.csv`

### 4. Process Data Files
Run the following Python scripts and Jupyter notebooks to process the data:

1. **Convert and Clean PAS Data**
    ```sh
    python convert_to_PAS_pkl.py
    ```
    This script converts and cleans the original `.xlsx` file into `PAS.pkl`.

2. **Clean Detailed PAS Data**
    ```sh
    python PAS_cleaning.py
    ```
    This script cleans the detailed PAS data and generates `PAS_detailed2_fixed_borough.pkl`.

3. **Calculate Underreporting Metric**
    Open and run the `crime_underreporting.ipynb` notebook. This notebook uses `PAS_detailed2_fixed_borough.pkl` to derive the underreporting metric and creates `PAS_underreporting.pkl`.

4. **Perform Exploratory Data Analysis (EDA)**
    Open and run the `EDA_underreporting.ipynb` notebook. This notebook uses `PAS_underreporting.pkl`, `PAS.pkl`, and `london_street_with_city.pkl` to perform EDA and create `result_df.pkl` for the R analysis.

### 5. Run R Analysis
Open the `DC2_analysis.R` file in RStudio. Change the file path to where `result_df.pkl` is saved on your computer. Run the script:
1. Select all (Ctrl + A)
2. Run (Ctrl + Enter)
3. Click "No" on the pop-up box after running. 

The last three outputs are the summaries of the three respective models.

### 6. Generate Presentation Graphs
Open and run the `EDA_presentation_graphs.ipynb` notebook to generate the graphs for the presentation.

---

By following these instructions, you will be able to set up the project, process the data, perform analysis, and generate the required visualizations for the underreporting project.
