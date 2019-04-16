######################################
## Author: I-No Liao                ##
## Date of update: 2018/10/16       ##
## Project: NBA Game Prediction     ##
## - Model evaluation               ##
######################################

# General
import time
import os
import argparse
import pandas as pd
import pickle
import warnings
warnings.filterwarnings('ignore')

# Sklearn
from sklearn.metrics import accuracy_score



#-----------------------#
#     Main Function     #
#-----------------------#
def main():
    # Argument processing
    inFile, outPath, mode, dateStart, dateEnd, period, featureSel, team_A, team_B = argParse()
    
    # Create path if necessary
    if not os.path.exists(outPath):
        os.makedirs(outPath)
    
    # Model LUT
    modelsLUT = {}

    # Specify models
    models = []
    models.append('2016-08-01_to_2019-04-10_feature3_period3_LogiRegr')
    models.append('2016-08-01_to_2019-04-10_feature3_period3_SVM')
    models.append('2016-08-01_to_2019-04-10_feature3_period3_XGBoost')
    models.append('2016-08-01_to_2019-04-10_feature3_period3_RandomForest')
    models.append('2016-08-01_to_2019-04-10_feature3_period3_GBDT')
    models.append('2016-08-01_to_2019-04-10_feature3_period3_AdaBoost')
    
    # Import models
    modelsName = {}
    for model in models:
        modelsName[model.split('_')[-1]] = model

    for model in modelsName:
        if mode == 0:
            with open('../model/Z_trainedModel/' + modelsName[model] + '.pkl', 'rb') as f:
                modelsLUT[model] = pickle.load(f)
        elif mode == 1:
            with open('../model/Z_trainedModel/' + modelsName[model] + '_gs.pkl', 'rb') as f:
                modelsLUT[model+'_GS'] = pickle.load(f)
        elif mode == 2:
            with open('../model/Z_trainedModel/' + modelsName[model] + '.pkl', 'rb') as f:
                modelsLUT[model] = pickle.load(f)
            with open('../model/Z_trainedModel/' + modelsName[model] + '_gs.pkl', 'rb') as f:
                modelsLUT[model+'_GS'] = pickle.load(f)
        else:
            print('Error: mode should be only 0, 1, or 2')
            print('mode = 0: Default models')
            print('mode = 1: Grid search models')
            print('mode = 2: Default + Grid Search models')
            return None

    # Evaluation
    accuLUT = gamePrediction(inFile, modelsLUT, dateStart, dateEnd, period, team_A, team_B, featureSel)
    
    # Print results
    print('---------- Accuracy Report ----------')
    print('featureSel =', featureSel)
    print('Predict from', dateStart, 'to', dateEnd)
    print('Model/Train ID =', '_'.join(models[0].split('_')[:-1]))
    if team_A is None:
        print('team_A = All possible teams')
    else:
        print('team_A =', team_A)
    if team_B is None:
        print('team_B = All possible teams')
    else:
        print('team_B =', team_B)
    print('.....................................')
    for x in accuLUT:
        print(x, '= %.3f' %(accuLUT[x]))
    print('-------------------------------------')

    # Save results
    dateOfReport = time.strftime("%Y-%m-%d-h%Hm%Ms%S", time.localtime())
    with open(outPath + dateOfReport + '_report.csv', 'w') as f:
        f.write('Accuracy Report' + '\n')
        f.write('featureSel' + ',' + str(featureSel) + '\n')
        f.write('Predict from' + ',' + dateStart + '\n')
        f.write('Predict to' + ',' + dateEnd + '\n')
        f.write('Model/Train ID' + ',' + '_'.join(models[0].split('_')[:-1]) + '\n')
        if team_A is None:
            f.write('team_A' + ',' + 'None' + '\n')
        else:
            f.write('team_A' + ',' + team_A + '\n')
        if team_B is None:
            f.write('team_B' + ',' + 'None' + '\n')
        else:
            f.write('team_B' + ',' + team_B + '\n')
        f.write('-----' + ',' + '-----' + '\n')
        for x in accuLUT:
            f.write(x + ',' + str(accuLUT[x]) + '\n')
        


#-----------------------#
#     Sub-Functions     #
#-----------------------#
def argParse():
    parser = argparse.ArgumentParser()
    parser.add_argument('--inFile', '-if', type = str, default = '../crawler/nbaGamePair.csv')
    parser.add_argument('--outPath', '-op', type = str, default = './Z_evaluation/')
    parser.add_argument('--mode', '-md', type = int, default = 2)
    parser.add_argument('--dateStart', '-ds', type = str)
    parser.add_argument('--dateEnd', '-de', type = str)
    parser.add_argument('--period', '-pd', type = int, default = 5)
    parser.add_argument('--featureSel', '-fs', type = int, default = 3)
    parser.add_argument('--team_A', '-ta', type = str, default = None)
    parser.add_argument('--team_B', '-tb', type = str, default = None)
    
    args = parser.parse_args()
    inFile = args.inFile
    outPath = args.outPath
    mode = args.mode
    dateStart = args.dateStart
    dateEnd = args.dateEnd
    period = args.period
    featureSel = args.featureSel
    team_A = args.team_A
    team_B = args.team_B
    return inFile, outPath, mode, dateStart, dateEnd, period, featureSel, team_A, team_B

# @param X: pandas.DataFrame
# @param featureSel: int
# @return X: pandas.DataFrame
def featureEng(X, featureSel=None):
    # Feature Engineering
    if not featureSel or featureSel == 0:
        return X
    if featureSel == 1:
        X['PTS_DIFF'] = X['PTS_A'] - X['PTS_B']
    elif featureSel == 2:
        attriToDrop = ['PTS_A', 'PTS_B']
        X = X.drop(columns=attriToDrop)
    elif featureSel == 3:
        X['PTS_DIFF'] = X['PTS_A'] - X['PTS_B']
        attriToDrop = ['PTS_A', 'PTS_B']
        X = X.drop(columns=attriToDrop)
    elif featureSel == 4:
        attriToDrop = [
            'FGM_A', 'FGA_A', '3PM_A', '3PA_A', 'FTM_A', 'FTA_A', 'OREB_A', 'DREB_A', 'PF_A', 
            'FGM_B', 'FGA_B', '3PM_B', '3PA_B', 'FTM_B', 'FTA_B', 'OREB_B', 'DREB_B', 'PF_B'
        ]
        X['PTS_DIFF'] = X['PTS_A'] - X['PTS_B']
        X['STL+BLK_A'] = X['STL_A'] + X['BLK_A']
        X['STL+BLK_B'] = X['STL_B'] + X['BLK_B']
        attriToDrop += ['PTS_A', 'PTS_B', 'STL_A', 'STL_B', 'BLK_A', 'BLK_B']
        X = X.drop(columns=attriToDrop)
    return X

# @param dfFile: pandas.DataFrame (from 'nba_preprocessed.csv')
# @param date: str in the format of 'YYYY-MM-DD'
# @param period: int (Number of previous games to be considered)
# @param Team_A, Team_B: str
# @param homeAway: int (None for played game prediction)
# @param featureSel: int
# @return X: pandas.DataFrame
def attriGen(df, date, period, Team_A, Team_B, homeAway=None, featureSel=None):
    # True Home/Away at the game day
    if homeAway is None:
        df_gameDay = df.loc[(df.Date_A == date) & (df.Team_A == Team_A) & (df.Team_B == Team_B), :].reset_index(drop=True)
        homeAway = int(df_gameDay['Home/Away_A'])
    
    # Date selections
    df = df.loc[df.Date_A < date, :].reset_index(drop=True)
    X_A = df.loc[(df.Team_A == Team_A), :].sort_values(by=['Date_A'], ascending=False).iloc[0:period, 0:24].reset_index(drop=True)
    X_B = df.loc[(df.Team_A == Team_B), :].sort_values(by=['Date_A'], ascending=False).iloc[0:period, 0:24].reset_index(drop=True)
    
    # Drop unnecessary attributes
    colToDrop = ['Home/Away_A'] + ['Team_A', 'Date_A', 'W/L_A', 'Score_A', 'Opponent_A']
    X_A = X_A.drop(columns=colToDrop)
    X_B = X_B.drop(columns=colToDrop)
    
    # Rename X_away's columns
    X_B = X_B.rename(columns=lambda x: x[0:-2] + '_B')
    
    # Get X = [Home/Away_A + X_A + X_B]
    X = pd.DataFrame(data=pd.concat([X_A.mean(), X_B.mean()])).transpose()
    X = pd.concat([pd.DataFrame(data={'Home/Away_A': [homeAway]}), X], axis=1)
    
    # Feature Engineering
    X = featureEng(X, featureSel)
    
    return X

# @param dfFile: pandas.DataFrame (from 'nba_preprocessed.csv')
# @param date: str in the format of 'YYYY-MM-DD'
# @param Team_A, Team_B: str
# @param featureSel: int
# @return X_groundTruth, Y_groundTruth: pandas.DataFrame
def groundTruthGen(df, date, Team_A, Team_B, featureSel=None):
    # Date selections
    df = df.loc[(df.Date_A == date) & (df.Team_A == Team_A) & (df.Team_B == Team_B), :].reset_index(drop=True)

    # Get label Y
    Y_groundTruth = df[['W/L_A']]
    Y_groundTruth = Y_groundTruth.rename(columns={'W/L_A': 'Label'})
    
    # Drop unnecessary attributes
    colToDrop = [
        'Team_A', 'Date_A', 'W/L_A', 'Score_A', 'Opponent_A', 
        'Team_B', 'Date_B', 'W/L_B', 'Home/Away_B', 'Score_B', 'Opponent_B'
    ]
    X_groundTruth = df.drop(columns=colToDrop)
    
    # Feature Engineering
    X_groundTruth = featureEng(X_groundTruth, featureSel)
    
    return X_groundTruth, Y_groundTruth

# @param dfFile: pandas.DataFrame ('nba_preprocessed.csv')
# @param dateStart, dateEnd: str in the format of 'YYYY-MM-DD'
# @param period: int
# @param Team_A, Team_B: str (If both are None, predict all games within the date range)
# @param featureSel: int
# @return X, Y: pandas.DataFrame
# gameAttriGen() outputs X_attri, Y_truth for game prediction.
def gameAttriGen(dfFile, dateStart, dateEnd, period=5, Team_A=None, Team_B=None, featureSel=None):
    df = pd.read_csv(dfFile)
    
    # Date selections
    df_sel = df.loc[(df.Date_A >= dateStart) & (df.Date_A <= dateEnd), :].reset_index(drop=True)
    
    # Generate df_sel which includes [date, Team_A, Team_B] columns
    if Team_A and Team_B:
        df_sel = df_sel.loc[(df_sel.Team_A == Team_A) & (df_sel.Opponent_A == Team_B), :].reset_index(drop=True)[['Date_A', 'Team_A', 'Opponent_A']]
    elif Team_A and not Team_B:
        df_sel = df_sel.loc[df_sel.Team_A == Team_A, :].reset_index(drop=True)[['Date_A', 'Team_A', 'Opponent_A']]
    elif not Team_A and Team_B:
        df_sel = df_sel.loc[df_sel.Opponent_A == Team_B, :].reset_index(drop=True)[['Date_A', 'Team_A', 'Opponent_A']]
    elif not Team_A and not Team_B:
        df_sel = df_sel[['Date_A', 'Team_A', 'Opponent_A']]
        # Delete duplicates: (Team_A vs Team_B) is the same as (Team_B vs Team_A). Remove one to avoid double count.
        df_new = pd.DataFrame(columns=['Date_A', 'Team_A', 'Opponent_A'])
        LUT = {}
        for date, x, y in zip(df_sel['Date_A'], df_sel['Team_A'], df_sel['Opponent_A']):
            if (date + x + y) in LUT:
                df_new = pd.concat([df_new, pd.DataFrame(columns=['Date_A', 'Team_A', 'Opponent_A'], data=[[date, x, y]])], ignore_index=True)
            else:
                LUT[date + x + y] = 1
                LUT[date + y + x] = 1
        df_sel = df_new
    
    # W/L prediction
    X_attri = Y_truth = None
    for date, Team_A, Team_B in zip(df_sel['Date_A'], df_sel['Team_A'], df_sel['Opponent_A']):
        X_toBePredicted = attriGen(df, date, period, Team_A, Team_B, None, featureSel)
        X_groundTruth, Y_groundTruth = groundTruthGen(df, date, Team_A, Team_B, featureSel)
        if X_attri is None and Y_truth is None:
            X_attri = X_toBePredicted
            Y_truth = Y_groundTruth
        else:
            X_attri = pd.concat([X_attri, X_toBePredicted], ignore_index=True)
            Y_truth = pd.concat([Y_truth, Y_groundTruth], ignore_index=True)
        
    return X_attri, Y_truth

# @param dfFile: pandas.DataFrame ('nba_preprocessed.csv')
# @param modelsLUT: dict in the format of {'modelName': model}
# @param dateStart, dateEnd: str in the format of 'YYYY-MM-DD'
# @param period: int (Number of previous games to be considered)
# @param Team_A, Team_B: str (If both are None, predict all games within the date range)
# @param featureSel: int
# @return None
# gamePrediction() prints the predicted game W/L results.
def gamePrediction(dfFile, modelsLUT, dateStart, dateEnd, period=5, Team_A=None, Team_B=None, featureSel=None):
    X_attri, Y_truth = gameAttriGen(dfFile, dateStart, dateEnd, period, Team_A, Team_B, featureSel)
    
    resultLUT, accuLUT = {}, {}
    for model in modelsLUT:
        resultLUT[model] = modelsLUT[model].predict(X_attri)
        accuLUT[model] = accuracy_score(Y_truth, modelsLUT[model].predict(X_attri))
    return accuLUT 



#-----------------------#
#       Execution       #
#-----------------------#
if __name__ == '__main__':
    main()
