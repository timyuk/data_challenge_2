 Underreporting Project
---

---
## User Instructions

Convert the ``PAS.csv`` to a pickle file.

Combine the street-level crime dataset.

Ensure that you have the following files in the ``/crime_data/`` subdirectory:
-  ``PAS.pkl``
-  the needed crime data files to merge
-  ``PAS_Sharing_EXTERNAL_data dictionary_1517`` up to ``PAS_Sharing_EXTERNAL_data dictionary_2223``

Run the following ``.py`` files to create the necessary datasets
-  ``PAS_cleaning.py``: cleans detailed PAS data and returns ``PAS_detailed2_fixed_borough.pkl``.
-  ``crime_underreporting.ipynb``: uses ``PAS_detailed2_fixed_borough.pkl`` to derive the underreporting metric and creates ``PAS_underreporting.pkl``
-  ``EDA_underreporting.ipynb``: uses ``PAS_underreporting.pkl``, ``PAS.pkl``, and ``london_street_with_city.pkl`` to do EDA and create a dataframe ``result_df.pkl`` for the R analysis.

Run the ``DC2_analysis.R`` file in RStudio using the ``result_df.pkl`` file to run the analysis. Change the file path to where ``result_df.pkl`` is saved on your computer. 
Ctrl + A then Ctrl+ Enter. Click "No" on the pop-up box after running. The last 3 outputs are the 3 respectives model's summaries
