################################################
## Author: I-No Liao                          ##
## Date of update: 2018/08/22                 ##
## Project: NBA Game Prediction               ##
## - NBA Game Pairing                         ##
##   - Clean-up dataset                       ##
##   - Pair games                             ##
##   - Check games' validity                  ##
##   - Generate nbaGamePair.csv               ##
################################################

import time
import os
import argparse
import pandas as pd
import numpy as np



#-----------------------#
#     Main Function     #
#-----------------------#
def main():
    # Argument processing
    inFile, outFile, isAppend = argParse()

    # Load .csv
    df_box = pd.read_csv(inFile)
    
    # Remove NaN
    df_box = cleanDataFrame(df_box)
    df_box = dropNanScore(df_box)

    # Add opponent label
    df_box = addOpponentCol(df_box)

    # Binary encode W/L and Home/Away
    df_box['W/L'] = df_box['W/L'].map({'W':1, 'L':0})
    df_box['Home/Away'] = df_box['Home/Away'].map({'Home':1, 'Away':0})

    # Pair teams and opponents
    df_team, df_oppo, invalid_idx = pairGamePlayers(df_box)

    # Check games' validity
    df_team, df_oppo, invalid_idx = checkGameValidity(df_team, df_oppo)

    # Rename column: Attributes_A and Attributes_B for team and opponent, respectively
    df_team = df_team.rename(columns=lambda x: x + '_A')
    df_oppo = df_oppo.rename(columns=lambda x: x + '_B')

    # Concatenate by column
    df_output = pd.concat([df_team, df_oppo], axis=1)

    # Create/Update nbaGamePair.csv
    if isAppend and os.path.exists(outFile):
        df_old = pd.read_csv(outFile)
        df_new = df_old.append(df_output, ignore_index=True)
        df_new = df_new.drop_duplicates(subset=['Team_A', 'Date_A'], keep='first')
        df_new = df_new.sort_values(by=['Date_A'])
        df_new.to_csv(outFile, encoding='utf-8', header=True, index=False, float_format='%.3f')
    else:
        df_output.to_csv(outFile, encoding='utf-8', header=True, index=False, float_format='%.3f')



#-----------------------#
#     Sub-Functions     #
#-----------------------#
def argParse():
    parser = argparse.ArgumentParser()
    parser.add_argument('--inFile', '-if', type = str)
    parser.add_argument('--outFile', '-of', type = str, default = './nbaGamePair.csv')
    parser.add_argument('--isAppend', '-ia', type = int, default = 1)
    
    args = parser.parse_args()
    inFile = args.inFile
    outFile = args.outFile
    isAppend = args.isAppend
    return inFile, outFile, isAppend

# @param df: pandas.DataFrame
# @return pandas.DataFrame
# NaN cleaner (Numerical)
def cleanDataFrame(df):
    assert isinstance(df, pd.DataFrame), 'df needs to be a pd.DataFrame'
    df.dropna(inplace=True)
    indices_to_keep = ~df.isin([np.nan, np.inf, -np.inf]).any(1)
    return df[indices_to_keep].reset_index(drop=True)

# @param df: pandas.DataFrame
# @return pandas.DataFrame
# Drop objects which are NaN in Score's label (String)
def dropNanScore(df):
    index = []
    for idx, score in enumerate(df['Score']):
        if score[:3] == 'NAN' or score[:3] == 'NaN':
            index.append(idx)
    print('Number of objects dropped =', len(index))
    return df.drop(df.index[index]).reset_index(drop=True)

# @param df: pandas.DataFrame
# @return df: pandas.DataFrame
# Add opponent label to a game
def addOpponentCol(df):
    opponent = [None] * len(df['Score'])
    for idx, score in enumerate(df['Score']):
        opponent[idx] = score[:3]
    df['Opponent'] = opponent
    return df

# @param df: pandas.DataFrame
# @return df_team, df_oppo: pandas.DataFrame
# Pair two teams in a single game by searching 'Date' and 'Opponent' labels.
def pairGamePlayers(df):  
    startTime = time.time()
    invalid_idx = []
    duplicate = 0
    not_found = 0
    # Declare empty dataframe w/ columns from existing dataframe
    df_team = pd.DataFrame(columns = list(df)) # Team attributes
    df_oppo = pd.DataFrame(columns = list(df)) # Opponent attributes
    df_dupl = pd.DataFrame(columns = list(df)) # Duplicated dataframe
    for idx, date, team in zip(df.index.tolist(), df['Date'], df['Team']):
        df_oppo_searched = df.loc[lambda df: df.Date == date, :].loc[lambda df: df.Opponent == team, :]
        if len(df_oppo_searched.index.tolist()) > 1:
            duplicate += 1
            df_dupl = pd.concat([df_dupl, df_oppo_searched], ignore_index=True)
            df_oppo_searched = df_oppo_searched.iloc[0:1, :]
        if not df_oppo_searched.empty:
            df_team = pd.concat([df_team, df.iloc[idx:idx+1, :]], ignore_index=True)
            df_oppo = pd.concat([df_oppo, df_oppo_searched], ignore_index=True)
        else:
            invalid_idx.append(idx)
            not_found += 1
    
    print('Duplicate found =', duplicate)
    print('Opponent not found =', not_found)
    print('Team length = ', len(df_team.index.tolist()))
    print('Oppo length = ', len(df_oppo.index.tolist()))
    print('Execution time =', time.time() - startTime)
    return df_team, df_oppo, invalid_idx

# @param df_team, df_oppo: pandas.DataFrame
# @return df_team, df_oppo: pandas.DataFrame
# Check game validity after pairGamePlayers(df) which pairs two teams in a single game.
def checkGameValidity(df_team, df_oppo):
    startTime = time.time()
    err = 0
    invalid_idx = []
    print('Team length = ', len(df_team.index.tolist()))
    print('Oppo length = ', len(df_oppo.index.tolist()))
    for idx in df_team.index.tolist():
        if df_team.loc[idx]['Date'] != df_oppo.loc[idx]['Date'] or \
        df_team.loc[idx]['Opponent'] != df_oppo.loc[idx]['Team'] or \
        df_team.loc[idx]['W/L'] == df_oppo.loc[idx]['W/L'] or \
        df_team.loc[idx]['Home/Away'] == df_oppo.loc[idx]['Home/Away']:
            err += 1
            invalid_idx.append(idx)
    
    df_team = df_team.drop(df_team.index[invalid_idx]).reset_index(drop=True)
    df_oppo = df_oppo.drop(df_oppo.index[invalid_idx]).reset_index(drop=True)
    
    print('Number of invalid games =', err, '@', [x for x in invalid_idx])
    print('Execution time =', time.time() - startTime)
    return df_team, df_oppo, invalid_idx



#-----------------------#
#       Execution       #
#-----------------------#
if __name__ == '__main__':
    main()
