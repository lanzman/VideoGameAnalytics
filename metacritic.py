from lxml import html
import requests
import pandas as pd
import os

metacriticdf = gamesdf

def getmetadata(gamesdf):
    
    metacriticdf = gamesdf.loc[gamesdf.metacriticScore.isnull()]
    
    #create metacritic platformURL
    metacriticdf.loc[:,'platformURL'] = metacriticdf.loc[:,'Platform'].str.split('/').str[0].str.lower()
    
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
    metacriticdf.platformURL.replace(platformdict, inplace = True)
    
    #creates the metacriticTitle from hltbTitle or Titles where applicable
    metacriticdf.loc[:,'metacriticTitle'] = metacriticdf.loc[:,'hltbTitle'].str.replace('\.| - | & | ', '-').str.replace('&|\'|,|:', '').str.lower()
    metacriticdf.loc[metacriticdf.hltbTitle.isnull(),'metacriticTitle'] = metacriticdf.loc[:,'Titles'].str.replace('\.| - | & | ', '-').str.replace('&|\'|,|:', '').str.lower()
    
    #generate metacriticURL
    metacriticdf.loc[:,'metacriticURL'] = 'http://www.metacritic.com/game/' + metacriticdf.loc[:,'platformURL'] + '/' + metacriticdf.loc[:,'metacriticTitle']
    
    #sets the headers required for the get request
    headers = {'User-Agent' : "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36"}
    
    #loops through titles for metacritic scores
    for i in metacriticdf.itertuples():
        
        #sets the url
        url = i.metacriticURL
        
        print(url)
        
        #creates the metacritic html page and tree
        metacriticpage = requests.get(url, headers = headers)
        
        #checks if URL worked
        if metacriticpage.status_code == 404:
            
            #sets to invalidURL
            metacriticdf.loc[i.Index,'metacriticMetaScore'] = 'invalidURL'
            metacriticdf.loc[i.Index,'metacriticUserScore'] = 'invalidURL'
            continue
        
        #creates the html tree for parsing the xpath
        tree = html.fromstring(metacriticpage.content)
        
        #path to extract the metacritic score
        metascorepath = '//a[@class="metascore_anchor"]/div/span[@itemprop="ratingValue"]/text()'
        userscorepath = '//a[@class="metascore_anchor"]/div/text()'

        try:
            #gets the scorelist
            metascore = tree.xpath(metascorepath)[0]
        except IndexError:
            
            #gets the other platform links if a score isn't logged
            linkpath = '//li[@class="summary_detail product_platforms"]/span[@class="data"]/a/@href'
            linklist = tree.xpath(linkpath)
            
            #loops through the returned links
            for j in linklist:
                
                #recreates url
                url = 'http://www.metacritic.com' + j
                
                #creates the metacritic html page and tree
                metacriticpage = requests.get(url, headers = headers)
                
                #creates the html tree for parsing the xpath
                tree = html.fromstring(metacriticpage.content)
                
                #path to extract the metacritic score
                metascorepath = '//a[@class="metascore_anchor"]/div/span[@itemprop="ratingValue"]/text()'
                
                try:
                    #gets the scorelist    
                    metascore = tree.xpath(metascorepath)[0]
                    
                    #sets the metacriticdf URL value
                    metacriticdf.loc[i.Index,'metacriticURL'] = url
                    
                    #breaks loop
                    break
                
                except IndexError:
                    
                    #continues on through loop
                    pass
                
                #if it didn't break, set the scorelist value for nothing
                metascore = 'No Score Recorded'
    
        try:
            #gets the userscore
            userscore = tree.xpath(userscorepath)[0]
        except IndexError:
            userscore = 'No Score Recorded'
        
        #set score value    
        metacriticdf.loc[i.Index, 'metacriticMetaScore'] = metascore
        metacriticdf.loc[i.Index, 'metacriticUserScore'] = userscore
    
    ###ADD section to drop unecessary columns before merging
    #metacriticdf.drop(labels =['])
    
    #take out section for getting score from url and make it's own function
    
    #get something for posting searches
