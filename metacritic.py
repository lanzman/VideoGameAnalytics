from lxml import html
import requests
import pandas as pd
import os

def getmetadata(gamesdf):
    
    #loop through all titles to post requests
    for i in gamesdf.loc[(gamesdf.hltbURL != 'URL missing') & gamesdf.mainlength.isnull()].itertuples():
        
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
        
        #updates the value in the gamesdf
        gamesdf.loc[i.Index,'mainlength'] = mainlength
        
        print(i.hltbTitle, ' ', mainlength)
    
    
    #create metacritic platformURL
    gamesdf.loc[:,'platformURL'] = gamesdf.loc[:,'Platform'].str.split('/').str[0].str.lower()
    
    #create subsitution dictionary
    platformdict = {'ps4':'playstation-4', \
                   'ps3':'playstation-3', \
                   'pc': 'pc', \
                   'PS Vita':'playstation-vita', \
                   '3ds': '3ds', \
                   'psp': 'psp', \
                   'ps2': 'playstation-2', \
                   'ps1': 'playstation', \
                   'ds': 'ds'}
    
    #replaces the extracted platform with the correct format for the URL
    gamesdf.platformURL.replace(platformdict, inplace = True)
    
    #generate metacriticURL
    gamesdf.loc[:,'metacriticURL'] = 'http://www.metacritic.com/game/' + gamesdf.loc[:,'platformURL'] + '/' + gamesdf.loc[:,'hltbTitle'].str.replace(' ', '-').str.lower()
    
    #sets the headers required for the get request
    headers = {'User-Agent' : "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36"}
    
    for i in gamesdf.itertuples():
        
        #sets the url
        url = i.metacriticURL
        
        print(url)
        
        #creates the metacritic html page and tree
        metacriticpage = requests.get(url, headers = headers)
        tree = html.fromstring(metacriticpage.content)
        
        #path to extract the metacritic score
        scorepath = '//a[@class="metascore_anchor"]/div/span[@itemprop="ratingValue"]/text()'
        
        try:
            scorelist = tree.xpath(titlepath)[0]
        except IndexError:
            
            gamesdf.loc[i.Index,'metacriticScore'] = 'invalidURL'
            continue
        
        #set score value    
        gamesdf.loc[i.Index, 'metacriticScore'] = scorelist
    
