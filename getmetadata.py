from lxml import html
import requests
import pandas as pd
import numpy as np
import re
import os

#change directory
os.chdir(r'C:\Users\mike.lanza\Documents\Python\GitHub\VideoGameAnalytics')

#import gameslist csv
gameslist = pd.read_csv('GamesList.csv', index_col=0, encoding= 'ISO-8859-1')

#regex pattern for time
pattern = '(?:([0-9]+)h ?)?(?:([0-9]+)m ?)?(?:([0-9]+)s ?)?'

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
        
        mainlength = 'invalidURL'
    
    else:
    
        #gets the resulting groups from the pattern and the time string
        result = re.match(pattern, lengthlist[2])
        
        #replaces None values with 0 if particular group isn't found in regex
        groupresult = ['0' if x == None else x for x in list(result.group(1,2,3))]
        
        #sets the mainlength variable to a consistent string
        mainlength = groupresult[0] + 'h ' + groupresult[1] + 'm ' + groupresult[2] + 's'
    
    #updates the value in the gameslist
    gameslist.loc[i.Index,'mainlength'] = mainlength
    
    print(i.hltbTitle, ' ', mainlength)


#create metacritic platformURL
gameslist.loc[:,'platformURL'] = gameslist.loc[:,'Platform'].str.split('/').str[0].str.lower()

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
gameslist.platformURL.replace(platformdict, inplace = True)

#generate metacriticURL
gameslist.loc[:,'metacriticURL'] = 'http://www.metacritic.com/game/' + gameslist.loc[:,'platformURL'] + '/' + gameslist.loc[:,'hltbTitle'].str.replace(' ', '-').str.replace(':','').str.replace("'",'').str.lower()

#sets the headers required for the get request
headers = {'User-Agent' : "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36"}

for i in gameslist.itertuples():
    
    #sets the url
    url = i.metacriticURL
    
    print(url)
    
    #resets metacriticscore, developer, and genre
    metacriticscore = None
    developer = None
    genre = None
    
    #creates the metacritic html page and tree
    metacriticpage = requests.get(url, headers = headers)
    
    #if page get request fails
    if metacriticpage.status_code != 200:
        
        #sets the metacriticscore, developer, and genre to invalidURLs until a valid URL is found
        metacriticscore = 'invalidURLs'
        developer = 'invalidURLs'
        genre = 'invalidURLs'
        
        
        #loop through dictionary to modify url for different platforms
        for k, v in platformdict.items():
            
            #creates the new URL to test
            url = 'http://www.metacritic.com/game/' + v + '/' + i.hltbTitle.replace(' ', '-').replace('.','').replace(',','').replace(':','').replace("'",'').lower()
            print(url)
            #creates the metacritic html page and tree
            metacriticpage = requests.get(url, headers = headers)
            
            #check if page valid
            if metacriticpage.status_code == 200:
                
                #update url to working url
                gameslist.loc[i.Index, 'metacriticURL'] = url
                
                #sets metacriticscore, developer, and genre back to None
                metacriticscore = None
                developer = None
                genre = None
                
                break
    
    #if metacriticscore skip to next item
    if metacriticscore == None:
        
        #creates html tree
        tree = html.fromstring(metacriticpage.content)
        
        #path to extract the metacritic score
        scorepath = '//a[@class="metascore_anchor"]/div/span[@itemprop="ratingValue"]/text()'
        developerpath = '//li[@class="summary_detail developer"]/span[@class="data"]/text()'
        genrepath = '//li[@class="summary_detail product_genre"]/span[@itemprop="genre"]/text()' 

        try:
            
            #sets metacriticscore
            metacriticscore = float(tree.xpath(scorepath)[0])
        
        except IndexError:
            
            #sets metacriticscore
            metacriticscore = 'NoScoreFound'
        
        try:
            
            #sets developer
            developer = str.strip(tree.xpath(developerpath)[0])
            
        except IndexError:
            
            developer = 'NoDeveloperFound'
        
        try:
            
            #sets genre
            genre = ', '.join(set(tree.xpath(genrepath)))
            
        except IndexError:
            
            #sets metacriticscore
            genre = 'NoGenreFound'
    
    #set score value    
    gameslist.loc[i.Index, 'metacriticScore'] = metacriticscore
    gameslist.loc[i.Index, 'developer'] = developer
    gameslist.loc[i.Index, 'genre'] = genre

#convert playtimes to a timedelta
gameslist['formatmainlength'] = pd.to_timedelta(gameslist.mainlength)

##sorting
#gameslist.sort_values(by = ['formatmainlength'], axis = 0, ascending = False)

#find all the unique genres of the gameslist
genres = pd.DataFrame(', '.join(gameslist.genre.str.strip()).split(sep = ', '),columns=['genre']).drop_duplicates()

#reset the index for the genre dataframe
genres.reset_index(drop = True, inplace = True)

#finds count, avg playtime, avg score
for i in genres.itertuples():
    
    #filter dataframe specific to genre
    genredf = gameslist.loc[(~gameslist.metacriticScore.isin(['NoScoreFound','invalidURLs'])) & (gameslist.genre.str.contains(i.genre))]
    
    #set values for columns in genredf
    genres.loc[i.Index,'count'] = len(genredf)    
    genres.loc[i.Index,'meanplaytime'] = genredf.formatmainlength.mean()
    genres.loc[i.Index,'meanscore'] = genredf.metacriticScore.mean()
    print(genres.loc[i.Index])




genrepath = '//li[@class="summary_detail product_genre"]/span[@itemprop="genre"]/text()'

genre = list(set(tree.xpath(genrepath)))

genre[2]

type(genre)

genre = ', '.join(set(tree.xpath(genrepath)))


gameslist.dtypes

gameslist.genre = gameslist.genre.astype('object')

testlist = ['a','b','c']

gameslist['genre'][0] = genre

gameslist['genre'][0][0]

gameslist['Playing Status'].str.contains('Not Played')

gameslist['genre'].str.contains('a')

gameslist.loc['a' in gameslist.genre]

gameslist['genre'].str.contains('Arcade|test')

gameslist['Playing Status'].isin(['Not Played'])


#add code to remove special characters from title for URL

#working on using search functions for using the correct url when it doesn't quite work
#try to get headers section working correctly for below solutions

#sets the url
url = gameslist.loc[1:1,'metacriticURL'].values[0]

#creates the metacritic html page and tree
metacriticpage = requests.get(url, headers = headers)
tree = html.fromstring(metacriticpage.content)

#path to extract the metacritic score
scorepath = '//a[@class="metascore_anchor"]/div/span[@itemprop="ratingValue"]/text()'
scorelist = tree.xpath(titlepath)[0]

gameslist.loc[i.Index, 'metacriticScore'] = scorelist


'http://www.metacritic.com/game/pc/dead-space'

print(url.values[0])




tree.reponse

#sets the searchURL
searchURL = r'http://www.metacritic.com/autosearch'

#sets the title variable
title = 'Dead Space'
    
#search request using POST
r = requests.post(searchURL, data = {'search_term' : title,'User-Agent': "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36"})

#get html from page
tree = html.fromstring(r.content)

#titlelist
titlepath = '//p/text()'
titlelist = tree.xpath(titlepath)

print(titlelist)






#loop through all titles to post requests
for i in gameslist.loc[0:1].itertuples():
    
    #sets the title variable
    title = i.hltbTitle
        
    #search request using POST
    r = requests.post(searchURL, data = {'queryString' : title})

    #get html from page
    tree = html.fromstring(r.content)
    
    #titlelist
    titlepath = '//td[@class="list r30 inset_right"]/div[@class="colright"]/div[@class="title"]'
    titlelist = tree.xpath(titlepath)
    
    print(titlelist)
    
    
