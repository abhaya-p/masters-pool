import requests
import json
import pandas as pd
import numpy as np
import glob
url = "https://live-golf-data.p.rapidapi.com/leaderboard"
querystring = {"tournId":"014","year":"2023"}
headers = {
    "X-RapidAPI-Host": "live-golf-data.p.rapidapi.com",
    "X-RapidAPI-Key": "5f629a65d7msh1010ca075b711c3p1ace3cjsndaf17672e132"
}

response = requests.get(url, headers=headers, params=querystring).json()


# Create an empty list to store row data
rows_data = []

# Loop through the data and check for "CUT" position
for data in response['leaderboardRows']:
    first_name = data['firstName']
    last_name = data['lastName']
    is_amateur = data['isAmateur']
    position = data['position']
    player_id = int(data['playerId'])
    current_hole = int(data['currentHole']['$numberInt'])
    current_round_score = data['currentRoundScore'] if data['currentRoundScore'] != 'E' else '0'
    status = data['status']
    total = int(data['total']) if data['total'] != 'E' else 0
    full_name = first_name + ' ' + last_name
   

        
     # Check if the player has rounds data
   # Create an empty list to store row data

# Loop through the data and check for "CUT" position
for data in response['leaderboardRows']:
    first_name = data['firstName']
    last_name = data['lastName']
    is_amateur = data['isAmateur']
    position = data['position']
    player_id = int(data['playerId'])
    current_hole = int(data['currentHole']['$numberInt'])
    current_round_score = data['currentRoundScore'] if data['currentRoundScore'] != 'E' else '0'
    status = data['status']
    total = int(data['total']) if data['total'] != 'E' else 0
    full_name = first_name + ' ' + last_name

    # Check if the player has rounds data
# Loop through the data and check for "CUT" position
for data in response['leaderboardRows']:
    first_name = data['firstName']
    last_name = data['lastName']
    is_amateur = data['isAmateur']
    position = data['position']
    player_id = int(data['playerId'])
    current_hole = int(data['currentHole']['$numberInt'])
    current_round_score = data['currentRoundScore'] if data['currentRoundScore'] != 'E' else '0'
    status = data['status']
    total = int(data['total']) if data['total'] != 'E' else 0
    full_name = first_name + ' ' + last_name

    # Check if the player has rounds data
    rounds_data = data.get('rounds', [])
    
    if rounds_data:
        # Process each round data
        for round_data in rounds_data:
            round_Id = int(round_data.get('roundId', {}).get('$numberInt', -1))
            strokes = int(round_data.get('strokes', {}).get('$numberInt', -1))
            round_score = round_data.get('scoreToPar', None)
            if round_score == "E":
                round_score = 0
            elif round_score == "":
                round_score = None
            else:
                try:
                    round_score = int(round_score)
                except ValueError:
                    round_score = None

            # Append row data to the list
            rows_data.append({'position': position, 'isAmateur': is_amateur, 'status': status,
                              'full_name': full_name, 'currentRoundScore': current_round_score,
                              'currentHole': current_hole, 'round_Id': round_Id, 'player_id': player_id,
                              'strokes': strokes, 'round_score': round_score, 'total': total})

        # Check if the player is "cut" or "wd" and add missing round entries
        if (status == "wd") and (round_Id < 2):
            for additional_round_Id in range(2, 5):
                rows_data.append({'position': position, 'isAmateur': is_amateur, 'status': status,
                                    'full_name': full_name, 'currentRoundScore': current_round_score,
                                    'currentHole': current_hole, 'round_Id': additional_round_Id,
                                    'player_id': player_id, 'strokes': None, 'round_score': None,
                                    'total': total})
        if (status == "cut") and (round_Id < 3):
            for additional_round_Id in range(3, 5):
                rows_data.append({'position': position, 'isAmateur': is_amateur, 'status': status,
                                    'full_name': full_name, 'currentRoundScore': current_round_score,
                                    'currentHole': current_hole, 'round_Id': additional_round_Id,
                                    'player_id': player_id, 'strokes': None, 'round_score': None,
                                    'total': total})
    else:
        # Add rows for each round if no rounds data is available
        for round_Id in range(1, 5):
            rows_data.append({'position': position, 'isAmateur': is_amateur, 'status': status,
                              'full_name': full_name, 'currentRoundScore': current_round_score,
                              'currentHole': current_hole, 'round_Id': round_Id, 'player_id': player_id,
                              'strokes': None, 'round_score': None, 'total': total})

# Create DataFrame
df = pd.DataFrame(rows_data, columns=['position', 'isAmateur', 'status', 'full_name', 'currentRoundScore',
                                      'currentHole', 'round_Id', 'player_id', 'strokes', 'round_score', 'total'])

# Sort the DataFrame by player_id and round_Id
df = df.sort_values(by=['player_id', 'round_Id']).reset_index(drop=True)

df['round_score'] = pd.to_numeric(df['round_score'], errors='coerce')
df['round_Id']=df['round_Id'].astype(int)
df['position'] = pd.to_numeric(df['position'].str.replace('T', ''), errors ='coerce')

#round scores
# for round 1 and 2, players that have COMPLETED the round will have that round appear in their round_id; therefore if they have not completed
# the round, it does not show up

# Round 1 Score
active_mask1 = (df['round_Id']==1) 
#create a mask for the cut and wd players
non_active_mask1 = (df['round_Id'].isin([0, 1])) & (df['status']=='wd')
max_round_1_score = df.loc[(df['round_Id']==1) & (df['isAmateur']!=True), 'round_score'].max()
if pd.isna(max_round_1_score):
    max_round_1_score=np.nan

#df['round3_score']= np.nan #initialize with NaNs
df.loc[active_mask1, 'round1_score'] = df.loc[active_mask1, 'round_score'] #assign round score if active
df.loc[non_active_mask1, 'round1_score'] = max_round_1_score # assign max round 1 score if wd or cut

# Round 2 Score
active_mask2 = (df['round_Id']==2) 
#create a mask for the cut and wd players
non_active_mask2 = (df['round_Id'].isin([0, 1,2])) & (df['status']=='wd')
max_round_2_score = df.loc[(df['round_Id']==2) & (df['isAmateur']!=True), 'round_score'].max()
if pd.isna(max_round_2_score):
    max_round_2_score=np.nan

#df['round3_score']= np.nan #initialize with NaNs
df.loc[active_mask2, 'round2_score'] = df.loc[active_mask2, 'round_score'] #assign round score if active
df.loc[non_active_mask2, 'round2_score'] = max_round_2_score # assign max round 1 score if wd or cut


active_mask3 = (df['round_Id']==3) & (df['status']=='active')
#create a mask for the cut and wd players
non_active_mask3 = (df['round_Id'].isin([0, 1,2,3])) & (df['status']=='wd')| (df['status']=='cut')
max_round_3_score = df.loc[(df['round_Id']==3) & (df['status']=='active') & (df['isAmateur']!=True), 'round_score'].max()
if pd.isna(max_round_3_score):
    max_round_3_score=np.nan
    
#df['round3_score']= np.nan #initialize with NaNs
df.loc[active_mask3, 'round3_score'] = df.loc[active_mask3, 'round_score'] #assign round score if active
df.loc[non_active_mask3, 'round3_score'] = max_round_3_score # assign max round 3 score if wd or cut


active_mask4 = (df['round_Id']==4) & (df['status']=='active')
non_active_mask4 = (df['round_Id'].isin([0, 1,2,3,4])) & (df['status']=='wd')|(df['status']=='cut')
max_round_4_score = df.loc[(df['round_Id']==4) & (df['status'] =='active') & (df['isAmateur']!=True), 'round_score'].max()
if pd.isna(max_round_4_score):
    max_round_4_score=np.nan

#df['round4_score'] = np.nan
df.loc[active_mask4, 'round4_score'] = df.loc[active_mask4, 'round_score']
df.loc[non_active_mask4, 'round4_score'] = max_round_4_score 

df= df.sort_values(by=['position', 'full_name'], ascending=True)


df.to_csv('C:/Users/apras/Desktop/Masters pool/masters_test2.csv', encoding='utf-8', index=False)



# Initialize a new DataFrame to store the results
new_columns = ['full_name', 'position', 'isAmateur', 'status', 'currentRoundScore', 'currentHole', 'total', 'R1', 'R2', 'R3', 'R4']
new_df = pd.DataFrame(columns=new_columns)

# Group the DataFrame by player_id
grouped = df.groupby('player_id')

# Iterate over each player group
for player_id, group in grouped:
    # Extract relevant information
    player_info = group.iloc[0][new_columns[:7]].copy()  # Assuming player information is the same for all rounds

    # Extract round scores based on round_Id
    R1 = group.loc[group['round_Id'] == 1, 'round1_score'].iloc[0] if 1 in group['round_Id'].values else None
    R2 = group.loc[group['round_Id'] == 2, 'round2_score'].iloc[0] if 2 in group['round_Id'].values else None
    R3 = group.loc[group['round_Id'] == 3, 'round3_score'].iloc[0] if 3 in group['round_Id'].values else None
    R4 = group.loc[group['round_Id'] == 4, 'round4_score'].iloc[0] if 4 in group['round_Id'].values else None

    # Add the player's information and round scores to the new DataFrame
    new_df = new_df.append({**player_info, 'R1': R1, 'R2': R2, 'R3': R3, 'R4': R4}, ignore_index=True)

columns_to_sum=['R1', 'R2', 'R3', 'R4']
new_df['T'] =new_df[columns_to_sum].sum(axis=1)
# Print the new DataFrame
new_df.to_csv('C:/Users/apras/Desktop/Masters pool/newmaster.csv', encoding='utf-8', index=False)
#print(new_df)

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

merged_df= pd.merge(combined_df, new_df, left_on='Players', right_on='full_name', how='left').drop('Players', axis=1)
merged_df.to_csv('C:/Users/apras/Desktop/Masters pool/merged.csv', encoding='utf-8', index=False)