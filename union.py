# importing the required modules
import glob
import pandas as pd
 
# specifying the path to csv files


 
# csv files in the path
file_paths = glob.glob("C:/Users/apras/Desktop/Masters pool/Entry/New Folder/*.xlsx")
# list of excel files we want to merge.
#pd.read_excel(file_path) reads the excel
# data into pandas dataframe.

dfs = []

for file_path in file_paths:
    df2=pd.read_excel(file_path, sheet_name=2, engine='openpyxl')
    dfs.append(df2)
 
# Concatenate all the sheet 3 DataFrames into a single DataFrame
combined_df = pd.concat(dfs)

# Define the path and file name for your output Excel file
output_path = 'C:/Users/apras/Desktop/Masters pool/Entry.xlsx'

# Write the combined DataFrame to a new Excel file
combined_df.to_excel(output_path, index=False)
