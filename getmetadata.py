from lxml import html
import requests
import pandas as pd
import os

#change directory
os.chdir(r'C:\Users\mike.lanza\Documents\Python\GitHub\VideoGameAnalytics')

#import gameslist csv
gameslist = pd.read_csv('GamesList.csv', index_col=0, encoding= 'ISO-8859-1')


#loop through all titles to post requests
for i in gameslist.loc[(gameslist.hltbURL != 'URL missing') & gameslist.mainlength.isnull()].itertuples():
    
    #sets the searchURL
    searchURL = i.hltbURL
    
    #initiates gamepage requests
    gamepage = requests.get(searchURL)
       
    #get html from page
    tree = html.fromstring(gamepage.content)
        
    #tablepath
    tablepath = '//table[@class="game_main_table"]/tbody[@class="spreadsheet"][1]/tr/td/text()'
    lengthlist = tree.xpath(tablepath)
    
    #if nothing returned, skip to next title
    if len(lengthlist) == 0:
        
        continue
    
    #sets the mainlength variable
    mainlength = lengthlist[2]
    
    #updates the value in the gameslist
    gameslist.loc[i.Index,'mainlength'] = mainlength
    
    print(i.hltbTitle, ' ', mainlength)
