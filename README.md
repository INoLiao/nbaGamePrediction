# NBA Game Prediction Readme
### 0. Prerequisites: Use virtualenv or install the following packages
- pip3 install numpy
- pip3 install pandas
- pip3 install scipy
- pip3 install selenium
- pip3 install beautifulsoup4
- pip3 install scikit-learn
- pip3 install xgboost


### 1. Scraping box scores from NBA official site: ./statsCrawler/nbaStatsCrawler.py
- Run the following on the terminal 
    > python3 nbaStatsCrawler.py -sy='2017-18' -st='RegularSeason' -ds='2018-04-01' -pn=10

- Argument explanation
    - '--webDriPath' = '-wdp': Path of chromedriver
        - default = './webDriver/chromedriver'
    - '--outPathRaw' = '-opr': Raw box output path
        - default = './Z_raw/'
    - '--outPathArranged' = '-opa': Arranged box output path
        - default = './Z_arranged/'
    - '--seasonYear' = '-sy': Specify the season to be scraped
        - default = '2017-18'
    - '--seasonType' = -st': Specify the season type ('Preseason', 'RegularSeason', 'Playoffs', 'All-Star') 
        - default = 'RegularSeason'
    - '--dateStart' = '-ds': Scrape box from date of 'dateStart' to present
        - default = '2018-04-01'
    - '--pageNum' = '-pn': Specify number of pages to be scraped
        - default = 5
    - '--loadTime' = '-lt': Waiting time for web loading
        - default = 2

### 2. Create/Update nbaGamePair.csv: ./statsCrawler/nbaGamePair.py
- Run the following on the terminal 
    > python3 nbaGamePair.py -if='./Z_arranged/2018-08-22-h19m50s28_2017-18_RegularSeason.csv' -ia=1

- Argument explanation
    - '--inFile' = '-if': Input file
        - No default, one must specify the input file
    - '--outFile' = '-of': Output file
        - default = './nbaGamePair.csv'
    - '--isAppend' = '-ia': Append to the existing file or replace it
        - default = 1
        
### 3. Grid Search: ./modelTraining/gridSearh.py
- Set search parameter settings by editing paramGen.py and run the following on the terminal. It will generate a LUT as .pkl file.
    > python3 paramGen.py
- Run the following on the terminal 
    > python3 gridSearch.py -ds='2017-08-01' -de='2018-04-13' -pd=5 -fs=3

- Argument explanation
    - '--inFile' = '-if': Input file
        - default = '../statsCrawler/nbaGamePair.csv'
    - '--outPath' = '-op': Output path
        - default = './Z_gridSearchedModel/'
    - '--dataStart' = '-ds': Specify starting date for training
        - No default
    - '--dataEnd' = '-de': Specify ending date for training
        - No default
    - '--period' = '-pd': Specify number of games being averaged as an attribute
        - Default = 5
    - '--featureSel' = '-fs': Specify 'featureSel'
        - Default = 3