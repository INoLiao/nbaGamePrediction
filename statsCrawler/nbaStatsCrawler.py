################################################
## Author: I-No Liao                          ##
## Date of update: 2018/08/22                 ##
## Project: NBA Game Prediction               ##
## - NBA Stats Crawler                        ##
##   - https://stats.nba.com/teams/boxscores/ ##
##   - Scrape team box scores                 ##
################################################

import time
import os
import argparse
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import Select



#-----------------------#
#     Main Function     #
#-----------------------#
def main():
    # Argument processing
    webDriPath, outPathRaw, outPathArranged, seasonYear, seasonType, dateStart, pageNum, loadTime = argParse()
    
    # Create path if necessary
    if not os.path.exists(outPathRaw):
        os.makedirs(outPathRaw)
    if not os.path.exists(outPathArranged):
        os.makedirs(outPathArranged)
    
    # Date of crawling
    dateOfCrawl = time.strftime("%Y-%m-%d-h%Hm%Ms%S", time.localtime())

    # URL selection
    prefix = 'https://stats.nba.com/teams/boxscores/' + '?Season='
    url = {
        'Preseason': prefix + seasonYear + '&SeasonType=Pre%20Season',
        'RegularSeason': prefix + seasonYear + '&SeasonType=Regular%20Season',
        'Playoffs': prefix + seasonYear + '&SeasonType=Playoffs',
        'All-Star': prefix + seasonYear + '&SeasonType=All%20Star'
    }

    # Open browser
    driver = webdriver.Chrome(executable_path=webDriPath)
    driver.get(url[seasonType])
    time.sleep(loadTime)

    # Scrape the maximum page informtion
    content = []
    curSoup = BeautifulSoup(driver.page_source, 'html.parser')
    info = curSoup.findAll('select', {'class':'stats-table-pagination__select'})
    for x in info[-1]:
        content.append(x.get_text())
    maxPage = int(content[-1])

    # Load pages 
    pages = []
    pageNum = min(pageNum, maxPage)
    pageSel = Select(driver.find_element_by_class_name('stats-table-pagination__select'))
    for i in range(1, pageNum+1):
        # Pagination (Mimic a browser that clicks "next page".)
        pageSel.select_by_value('number:'+str(i))
        # Wait for loading the web
        time.sleep(loadTime)
        # Capture current page
        pages.append(driver.page_source)
        print('----- Note: Page %d scraping completed. -----' %(i))
    driver.quit()
    print('----- Note: %d of %d page(s) scraped. -----' %(pageNum, maxPage))

    # >> Raw Box Acquisition
    # Scrape box from each page and create DataFrame
    soups = [BeautifulSoup(page, 'html.parser') for page in pages]
    df_box = None
    for soup in soups:
        boxTitle = []
        for item in soup.findAll('thead'):
            boxTitle.append(item.get_text())
        title = [x for x in boxTitle[0].split('\n') if x != '' and x != 'Season']
        
        boxes = []
        for item in soup.findAll('tr', {'data-ng-repeat':'(i, row) in page track by row.$hash'}):
            boxes.append(item.get_text())
        boxData = []
        for i in range(len(boxes)//2):
            boxData.append([x for x in boxes[i].split('\n') if x != ''])
        for i in range(len(boxData)):
            for j in range(4, len(boxData[i])):
                if j == 8 or j == 11 or j == 14:
                    boxData[i][j] = round(float(boxData[i][j])*0.01, 3)
                else:
                    boxData[i][j] = int(boxData[i][j])
        
        # Create/Append data frame
        if df_box is None:
            df_box = pd.DataFrame(boxData, columns=title)
        else:
            df_box = df_box.append(pd.DataFrame(boxData, columns=title), ignore_index=True)

    # Date reformation and selection
    date = []
    df_box.rename(columns = {'Game\xa0Date':'Date'}, inplace=True)
    for x in df_box['Date']:
        date.append(x[-4:] + '-' + x[0:2] + '-' + x[3:5])
    df_box['Date'] = date
    df_box = df_box.loc[(df_box.Date >= dateStart), :].reset_index(drop=True)

    # Save raw box as .csv
    df_box.to_csv(outPathRaw + dateOfCrawl + '_' + seasonYear + '_' + seasonType + '.csv', encoding='utf-8', index=False, float_format='%.3f')

    # >> Arranged Box Acquisition
    # Drop'MIN'
    df_box = df_box.drop(columns=['MIN'])

    # Create 'Score' and 'Home/Away' columns
    score = []
    homeAway = []
    for team, match, pts, pm in zip(df_box['Team'], df_box['Match\xa0Up'], df_box['PTS'], df_box['+/-']):
        # 'Score'
        oppo = match[-3:]
        score.append(oppo + str(pts-pm) + '-' + str(pts) + team)
        # 'Home/Away'
        if '@' in match:
            homeAway.append('Away')
        else:
            homeAway.append('Home')
    df_box['Score'] = score
    df_box['Home/Away'] = homeAway
    df_box = df_box.drop(columns=['Match\xa0Up', '+/-'])

    # Re-arrange orders
    df_box = df_box[['Team', 'Date', 'W/L', 'Home/Away', 'Score', 'FG%', 'FGM', 
                     'FGA', '3P%', '3PM', '3PA', 'FT%', 'FTM', 'FTA', 'REB', 'OREB', 
                     'DREB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS']]

    # Sort by 'Date'
    df_box = df_box.sort_values(by=['Date'])

    # Save arranged box as .csv
    df_box.to_csv(outPathArranged + dateOfCrawl + '_' + seasonYear + '_' + seasonType + '.csv', encoding='utf-8', index=False, float_format='%.3f')



#-----------------------#
#     Sub-Functions     #
#-----------------------#
def argParse():
    parser = argparse.ArgumentParser()
    parser.add_argument('--webDriPath', '-wdp', type = str , default = '/Users/ltc/Projects/webDriver/chromedriver')
    parser.add_argument('--outPathRaw', '-opr', type = str , default = './Z_raw/')
    parser.add_argument('--outPathArranged', '-opa', type = str, default = './Z_arranged/')
    parser.add_argument('--seasonYear', '-sy', type = str, default = '2017-18')
    parser.add_argument('--seasonType', '-st', type = str, default = 'RegularSeason')
    parser.add_argument('--dateStart', '-ds', type = str, default = '2018-04-01')
    parser.add_argument('--pageNum', '-pn', type = int, default = 5)
    parser.add_argument('--loadTime', '-lt', type = int, default = 2)
    
    args = parser.parse_args()
    webDriPath = args.webDriPath
    outPathRaw = args.outPathRaw
    outPathArranged = args.outPathArranged
    seasonYear = args.seasonYear
    seasonType = args.seasonType
    dateStart = args.dateStart
    pageNum = args.pageNum
    loadTime = args.loadTime
    return webDriPath, outPathRaw, outPathArranged, seasonYear, seasonType, dateStart, pageNum, loadTime 



#-----------------------#
#       Execution       #
#-----------------------#
if __name__ == '__main__':
    main()
