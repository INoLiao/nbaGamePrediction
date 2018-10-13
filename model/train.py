######################################
## Author: I-No Liao                ##
## Date of update: 2018/10/13       ##
## Project: NBA Game Prediction     ##
## - Model training                 ##
##   - Logistic Regression          ##
##   - SVM                          ##
##   - XGBoost                      ##
##   - Random Forest                ##
##   - GBDT                         ##
##   - AdaBoost                     ##
######################################

# General
import time
import os
import argparse
import pandas as pd
import csv
import pickle
import warnings
warnings.filterwarnings('ignore')

# CVGS
from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import GridSearchCV

# Estimators
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import GradientBoostingClassifier
from xgboost import XGBClassifier
from sklearn.ensemble import AdaBoostClassifier



#-----------------------#
#     Main Function     #
#-----------------------#
def main():
    # Argument processing
    inFile, outPath, mode, dateStart, dateEnd, period, featureSel = argParse()
    
    # Create path if necessary
    if not os.path.exists(outPath):
        os.makedirs(outPath)

    # trainID
    trainID = dateStart + '_to_' + dateEnd + '_feature' + str(featureSel) + '_period' + str(period)

    # Load paramLUT.pkl
    with open('./paramLUT.pkl', 'rb') as f:
        LUT = pickle.load(f)

    # Feature Extraction
    print('>> Feature extraction ...')
    X, Y = featureExtraction(inFile, dateStart, dateEnd, period, featureSel)
    
    # Train model with default parameters
    if mode == 0:
        # Default training for all models
        for model in LUT:
            startTime = time.time()
            print('>>', model, '...')
            estimator = LUT[model][2].fit(X, Y)
            # Save model as .pkl
            with open(outPath + trainID + LUT[model][0] + '.pkl', 'wb') as f:
                pickle.dump(estimator, f)
            print('   Execution time =', time.time() - startTime)

    # Train model with grid search
    elif mode == 1:
        for model in LUT:
            startTime = time.time()
            print('>>', model, '...')
            NUM_TRIALS = 1
            max_score, best_estimator = CrossValidationGridSearchNested(X, Y, NUM_TRIALS, 10, LUT[model][2], LUT[model][1], 'roc_auc')
            # Save coefficient as .csv
            with open(outPath + trainID + LUT[model][0] + '_gs.csv', 'w') as f:
                for key, value in zip(best_estimator.get_params().keys(), best_estimator.get_params().values()):
                    f.write(key + ',' + str(value) + '\n')
                f.write('max_score' + ',' + str(max_score) + '\n')
                f.write('Execution time =' + ',' + str(time.time() - startTime) + '\n')
            # Save model as .pkl
            with open(outPath + trainID + LUT[model][0] + '_gs.pkl', 'wb') as f:
                pickle.dump(best_estimator, f)
            print('   Execution time =', time.time() - startTime)
    else:
        print('Err: mode should be either 0 or 1')
        print('mode = 0: grid search disabled')
        print('mode = 1: grid search enabled')



#-----------------------#
#     Sub-Functions     #
#-----------------------#
def argParse():
    parser = argparse.ArgumentParser()
    parser.add_argument('--inFile', '-if', type = str, default = '../crawler/nbaGamePair.csv')
    parser.add_argument('--outPath', '-op', type = str, default = './Z_trainedModel/')
    parser.add_argument('--mode', '-md', type = int, default = 0)
    parser.add_argument('--dateStart', '-ds', type = str)
    parser.add_argument('--dateEnd', '-de', type = str)
    parser.add_argument('--period', '-pd', type = int, default = 5)
    parser.add_argument('--featureSel', '-fs', type = int, default = 3)
    
    args = parser.parse_args()
    inFile = args.inFile
    outPath = args.outPath
    mode = args.mode
    dateStart = args.dateStart
    dateEnd = args.dateEnd
    period = args.period
    featureSel = args.featureSel
    return inFile, outPath, mode, dateStart, dateEnd, period, featureSel

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

# @param inFile: pandas.DataFrame ('nba_preprocessed.csv')
# @param dateStart, dateEnd: str in the format of 'YYYY-MM-DD'
# @param period: int
# @param featureSel: int (0, 1, 2, and 3 corresponds to feature0, 1, 2, and 3, respectively)
# @return X, Y: pandas.DataFrame
# featureExtraction() outputs X, Y for model training.
# Game date can be assigned
# Attribute to be dropped can be assigned
def featureExtraction(inFile, dateStart='1000-01-01', dateEnd='2999-12-31', period=5, featureSel=None):
    df = pd.read_csv(inFile)
    
    # Date selection
    df = df.loc[(df.Date_A >= dateStart) & (df.Date_A <= dateEnd), :].reset_index(drop=True)
    
    # Get label Y
    Y = df[['W/L_A']]
    Y = Y.rename(columns={'W/L_A': 'Label'})
    
    # Get averaged attributes X
    for idx, row in df.iterrows():
        df_sel = df.loc[df.Date_A <= row['Date_A'], :].reset_index(drop=True)
        
        # Process of Team_A
        gamePlayed_A = df_sel.loc[df_sel.Team_A == row['Team_A'], :]
        if len(gamePlayed_A) == 1:
            X_A = gamePlayed_A.loc[(gamePlayed_A.Team_A == row['Team_A']), :].sort_values(by=['Date_A'], ascending=False).iloc[0:1, 0:24].reset_index(drop=True)
        elif len(gamePlayed_A) < period:
            X_A = gamePlayed_A.loc[(gamePlayed_A.Team_A == row['Team_A']), :].sort_values(by=['Date_A'], ascending=False).iloc[1:len(gamePlayed_A), 0:24].reset_index(drop=True)
        else:
            X_A = gamePlayed_A.loc[(gamePlayed_A.Team_A == row['Team_A']), :].sort_values(by=['Date_A'], ascending=False).iloc[1:period+1, 0:24].reset_index(drop=True)
        
        # Process of Team_B
        gamePlayed_B = df_sel.loc[df_sel.Team_A == row['Team_B'], :]
        if len(gamePlayed_B) == 1:
            X_B = gamePlayed_B.loc[(gamePlayed_B.Team_A == row['Team_B']), :].sort_values(by=['Date_A'], ascending=False).iloc[0:1, 0:24].reset_index(drop=True)
        elif len(gamePlayed_B) < period:
            X_B = gamePlayed_B.loc[(gamePlayed_B.Team_A == row['Team_B']), :].sort_values(by=['Date_A'], ascending=False).iloc[1:len(gamePlayed_B), 0:24].reset_index(drop=True)
        else:
            X_B = gamePlayed_B.loc[(gamePlayed_B.Team_A == row['Team_B']), :].sort_values(by=['Date_A'], ascending=False).iloc[1:period+1, 0:24].reset_index(drop=True)
        
        # Drop unnecessary attributes
        colToDrop = ['Home/Away_A'] + ['Team_A', 'Date_A', 'W/L_A', 'Score_A', 'Opponent_A']
        X_A = X_A.drop(columns=colToDrop)
        X_B = X_B.drop(columns=colToDrop)
        
        # Rename X_B's columns
        X_B = X_B.rename(columns=lambda x: x[0:-2] + '_B')
        
        # Get X_single = [Home/Away_A + X_A + X_B]
        X_single = pd.DataFrame(data=pd.concat([X_A.mean(), X_B.mean()])).transpose()
        X_single = pd.concat([pd.DataFrame(data={'Home/Away_A': [row['Home/Away_A']]}), X_single], axis=1)
        
        # Concatenation dataFrames by row
        if idx == 0:
            X = X_single
        else:
            X = pd.concat([X, X_single], ignore_index=True)
        
    # Feature Engineering
    X = featureEng(X, featureSel)
        
    return X, Y

def CrossValidationGridSearchNested(X_data, Y_data, num_trials, fold_num, est_classifcation, tuned_param, scoring):
    max_score = -1
    best_estimator = est_classifcation
    is_tuned_param_empty = (tuned_param == []) | (tuned_param == None)
    
    for i in range(num_trials):
        inner_cv = StratifiedKFold(n_splits=fold_num, random_state=i, shuffle=True)
        outer_cv = StratifiedKFold(n_splits=fold_num, random_state=i+1, shuffle=True)
        
        if(is_tuned_param_empty):
            param_score = cross_val_score(est_classifcation, X=X_data, y=Y_data, cv=outer_cv, scoring=scoring).mean()
        else:
            # Non_nested parameter search and scoring
            clf = GridSearchCV(estimator=est_classifcation, param_grid=tuned_param, cv=inner_cv, scoring=scoring)
            clf.fit(X_data, Y_data)
        
            # CV with parameter optimization
            param_score = cross_val_score(clf.best_estimator_, X=X_data, y=Y_data, cv=outer_cv, scoring=scoring).mean()
            
        if(param_score > max_score):
            max_score = param_score
            if(is_tuned_param_empty):
                best_estimator = est_classifcation
            else:
                best_estimator = clf.best_estimator_
            
        progress = (i+1)/num_trials*100
        print('   Progress = %.0f/100' %(progress))
    
    return (max_score, best_estimator)



#-----------------------#
#       Execution       #
#-----------------------#
if __name__ == '__main__':
    main()
