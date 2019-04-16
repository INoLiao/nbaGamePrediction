# NBA Game Prediction Readme
### 0. Prerequisites: Use virtualenv or install the following packages
- pip3 install numpy
- pip3 install pandas
- pip3 install scipy
- pip3 install selenium
- pip3 install beautifulsoup4
- pip3 install scikit-learn
- pip3 install xgboost


### 1. Scraping box scores from NBA official site: https://stats.nba.com/teams/boxscores/
- Directory: ./crawler/
- Run nbaStatsCrawler.py
    > python3 nbaStatsCrawler.py -sy='2018-19' -st='RegularSeason' -ds='2018-10-16' -pn=10


- Argument explanation
    - '--webDriPath' = '-wdp': Path of chromedriver
        - default = './webDriver/chromedriver'
    - '--outPathRaw' = '-opr': Raw box output path
        - default = './Z_raw/'
    - '--outPathArranged' = '-opa': Arranged box output path
        - default = './Z_arranged/'
    - '--seasonYear' = '-sy': Specify the season to be scraped
        - No default
    - '--seasonType' = -st': Specify the season type ('Preseason', 'RegularSeason', 'Playoffs', 'All-Star')
        - No default
    - '--dateStart' = '-ds': Scrape box from date of 'dateStart' to present
        - No default
    - '--pageNum' = '-pn': Specify number of pages to be scraped
        - default = 5
    - '--loadTime' = '-lt': Waiting time for web loading
        - default = 2


### 2. Create/Update nbaGamePair.csv
- Directory: ./crawler/
- Run nbaGamePair.py
    > python3 nbaGamePair.py -if='./Z_arranged/2018-08-22-h19m50s28_2017-18_RegularSeason.csv' -ia=1


- Argument explanation
    - '--inFile' = '-if': Input file
        - No default, one must specify the input file
    - '--outFile' = '-of': Output file
        - default = './nbaGamePair.csv'
    - '--isAppend' = '-ia': Append to the existing file or replace it
        - default = 1


### 3. Model Training
- Directory: ./model/
- Set grid search settings by editing paramGen.py and run paramGen.py. It will generate a LUT named as paramLUT.pkl.
    > python3 paramGen.py
    
    
- Run train.py
    > python3 train.py -md=1 -ds='2016-08-01' -de='2019-04-10' -pd=5 -fs=3


- Argument explanation
    - '--inFile' = '-if': Input file
        - default = '../crawler/nbaGamePair.csv'
    - '--outPath' = '-op': Output path
        - default = './Z_trainedModel/'
    - '--mode' = '-md': 0 for default model and 1 for grid search
        - default = 0
    - '--dataStart' = '-ds': Specify starting date for training
        - No default
    - '--dataEnd' = '-de': Specify ending date for training
        - No default
    - '--period' = '-pd': Specify number of games being averaged as an attribute
        - Default = 5
    - '--featureSel' = '-fs': Specify 'featureSel'
        - Default = 3


### 4. Model Evaluation
- Directory: ./model/
- Edit model path in evaluate.py
    - At '# Specify model', please specify the model name according to the existing models within ./model/Z_trainedModel/
    - Be sure the parameters used for training and evaluating are the same
        - period
        - featureSel
        
        
- Run evaluate.py
    > python3 evaluate.py -md=1 -ds='2018-04-14' -de='2018-06-08' -pd=5 -fs=3
    
    - An evaluation report will be generated: ./Z_evaluation/date_report.csv
    
    
- Argument explanation
    - '--inFile' = '-if': Input file
        - default = '../crawler/nbaGamePair.csv'
    - '--outPath' = '-op': Output path
        - default = './Z_evaluation/'
    - '--mode' = '-md': 0 for default model, 1 for grid search model, and 2 for default + grid search models
        - default = 2
    - '--dataStart' = '-ds': Specify starting date for evaluating
        - No default
    - '--dataEnd' = '-de': Specify ending date for evaluating
        - No default
    - '--period' = '-pd': Specify number of games being averaged as an attribute
        - Default = 5
    - '--featureSel' = '-fs': Specify 'featureSel'
        - Default = 3
    - '--team_A' = '-ta': Specify the interested team A
        - Default = None (All games in the specified period)
        - Others = 'ATL', 'BOS', 'BKN', 'CHA', 'CHI', 'CLE', 'DAL', 'DEN', 'DET', 'GSW' 'HOU', 'IND', 'LAC', 'LAL', 'MEM', 'MIA', 'MIL', 'MIN', 'NOP', 'NYK', 'OKC', 'ORL', 'PHI', 'PHX', 'POR', 'SAC', 'SAS', 'TOR', 'UTA', 'WAS'
    - '--team_B' = '-tb': Specify the interested team B
        - Default = None (All games in the specified period)
        - Others = 'ATL', 'BOS', 'BKN', 'CHA', 'CHI', 'CLE', 'DAL', 'DEN', 'DET', 'GSW' 'HOU', 'IND', 'LAC', 'LAL', 'MEM', 'MIA', 'MIL', 'MIN', 'NOP', 'NYK', 'OKC', 'ORL', 'PHI', 'PHX', 'POR', 'SAC', 'SAS', 'TOR', 'UTA', 'WAS'
