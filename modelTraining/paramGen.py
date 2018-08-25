######################################
## Author: I-No Liao                ##
## Date of update: 2018/08/22       ##
## Project: NBA Game Prediction     ##
## - Sweeping Parameter Generator   ##
##   - Logistic Regression          ##
##   - SVM                          ##
##   - XGBoost                      ##
##   - Random Forest                ##
##   - GBDT                         ##
##   - AdaBoost                     ##
######################################

# General
import pickle

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
    LUT = {}

    # Logistic Regression
    modelName = '_LogiRegr'
    tuned_parameters = {
        'C': [0.001, 0.01, 0.1, 1, 10, 100, 1000],
        'max_iter': [100, 200, 300, 400, 500],
        'n_jobs': [-1]
    }
    LUT['logiRegr'] = [modelName, tuned_parameters, LogisticRegression()]
    
    # Support Vector Machine
    modelName = '_SVM'
    tuned_parameters = {
        'C': [0.1, 1, 10],
        'kernel': ['linear'], 
        'probability': [True]
    }
    LUT['svm'] = [modelName, tuned_parameters, SVC()]

    # XGBoost
    modelName = '_XGBoost'
    tuned_parameters = {
        'max_depth': [3, 5, 7],
        'learning_rate': [x/10 for x in range(1, 5, 2)],
        'n_estimators': [100, 200, 300],
        'min_child_weight': [1, 3],
        'gamma': [x/10 for x in range(0, 5)],
        'n_jobs': [-1]
    }
    LUT['xgBoost'] = [modelName, tuned_parameters, XGBClassifier()]

    # Random Forest
    modelName = '_RandomForest'
    tuned_parameters = {
        'n_estimators': [600, 800, 1000],
        'criterion': ['entropy'],
        'bootstrap': [True],
        'max_depth': [None, 5, 10],
        'max_features': ['auto', 'log2', 'sqrt'],
        'n_jobs': [-1]
    }
    LUT['randForest'] = [modelName, tuned_parameters, RandomForestClassifier()]

    # Gradient Boosting Decision Tree
    modelName = '_GBDT'
    tuned_parameters = {
        'loss': ['exponential'],
        'n_estimators': [600, 800, 1000],
        'learning_rate': [0.1, 0.2, 0.3],
        'max_depth': [3, 5, 10],
        'subsample': [0.5],
        'max_features': ['auto', 'log2', 'sqrt']
    }
    LUT['gbdt'] = [modelName, tuned_parameters, GradientBoostingClassifier()]

    # Adaptive Boosting
    modelName = '_AdaBoost'
    tuned_parameters = {
        'learning_rate': [1, 0.1, 0.2, 0.3],
        'n_estimators': [50, 100, 600, 800, 1000]
    }
    LUT['adaBoost'] = [modelName, tuned_parameters, AdaBoostClassifier()]

    with open('./paramLUT.pkl', 'wb') as f:
        pickle.dump(LUT, f)



#-----------------------#
#       Execution       #
#-----------------------#
if __name__ == '__main__':
    main()
