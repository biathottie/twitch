#WIP DOES NOTHING RN

import pandas as pd

# Load your original dataframe
original_df = pd.read_csv('gameInfoCopy.csv')

# Load the CSV file with champion stats
champ_stats_df = pd.read_csv('season1414.23.csv')

# Function to find the WinPercent for a given champion and role
def get_win_percent(champ_name, role):
    match = champ_stats_df[(champ_stats_df['Name'] == champ_name) & (champ_stats_df['Role'] == role)]
    if not match.empty:
        return match['WinPercent'].values[0]  # Return the WinPercent value
    return None  # Return None if no match is found

# Update the Winrate columns in the original DataFrame
roles = ['Top', 'Jungle', 'Mid', 'ADC', 'Support']
teams = ['Blue', 'Red']

for team in teams:
    for role in roles:
        champ_col = f'{team}{role}ChampName'
        winrate_col = f'{team}{role}ChampWinrate'
        role_name = role  # e.g., 'Top', 'Jungle', etc.

        # Populate the Winrate column
        original_df[winrate_col] = original_df.apply(
            lambda row: get_win_percent(row[champ_col], role_name), axis=1
        )

# Save the updated DataFrame to a new CSV
original_df.to_csv('updated_dataframe.csv', index=False)