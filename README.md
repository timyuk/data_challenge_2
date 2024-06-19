 Underreporting Project
---

---
## User Instructions



Create ``/data/`` subdirectory, to keep data files

Download combined street-level crime dataset ``london_street_with_city.pkl`` from the dropbox link

Dropbox link: https://www.dropbox.com/scl/fi/bl7omot3qr6mx9q2p6phy/london_street_with_city.pkl?rlkey=3p2hut7v0k25qhtijkwkol93c&st=13hupa6u&dl=0

Ensure that you have the following files in the ``/data/`` subdirectory:
- ``london_street_with_city.pkl`` 
- ``PAS_T&Cdashboard_to Q3 23-24.xlsx`` or same file but renamed to ``PAS.xlsx``
-  the needed ward level PAS files to merge:
    - ``PAS_ward_level_FY_15_17.csv`` 
    - ``PAS_ward_level_FY_17_18.csv``
    - ``PAS_ward_level_FY_18_19.csv``
    - ``PAS_ward_level_FY_19_20.csv``
    - ``PAS_ward_level_FY_20_21.csv``

Run the following ``.py`` files to create the necessary datasets
-  ``convert_to_PAS_pkl.py``: converts and cleans the original xlsx file into ``PAS.pkl`` which is used further
-  ``PAS_cleaning.py``: cleans detailed PAS data and returns ``PAS_detailed2_fixed_borough.pkl``.
-  ``crime_underreporting.ipynb``: uses ``PAS_detailed2_fixed_borough.pkl`` to derive the underreporting metric and creates ``PAS_underreporting.pkl``
-  ``EDA_underreporting.ipynb``: uses ``PAS_underreporting.pkl``, ``PAS.pkl``, and ``london_street_with_city.pkl`` to do EDA and create a dataframe ``result_df.pkl`` for the R analysis.

Run the ``DC2_analysis.R`` file in RStudio using the ``result_df.pkl`` file to run the analysis. Change the file path to where ``result_df.pkl`` is saved on your computer. 
Ctrl + A then Ctrl+ Enter. Click "No" on the pop-up box after running. The last 3 outputs are the 3 respectives model's summaries
