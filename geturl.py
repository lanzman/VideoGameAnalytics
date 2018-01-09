from lxml import html
import requests
import pandas as pd
import os

#change directory
os.chdir(r'C:\Users\mike.lanza\Documents\Python\GitHub\VideoGameAnalytics')

#import gameslist csv
gameslist = pd.read_csv('GamesList.csv', index_col=0, encoding= 'ISO-8859-1')

#set Titles to index for quick updating during loop
gameslist = gameslist.set_index('Titles')

#sets the mainURL and searchURL
mainURL = r'https://howlongtobeat.com/'
searchURL = r'https://howlongtobeat.com/search_main.php?page=1'

#initiates hltb requests
hltb = requests.get(mainURL)

#loop through all titles to post requests
for i in gameslist.loc[gameslist.hltbTitle.isnull()].itertuples():
    
    #checks if hltbTitle and hltbURL are both NOT NaN, if they are anything, they have already been processed and can be skipped
    if (i.hltbTitle == i.hltbTitle) and (i.hltbURL == i.hltbURL):
            
        continue
    
    print(i)
    
    #sets the title variable
    title = i.Index
        
    #search request using POST
    r = requests.post(searchURL, data = {'queryString' : title})

    #get html from page
    tree = html.fromstring(r.content)
    
    #titlelist
    titlepath = '//h3/a/text()'
    titlelist = tree.xpath(titlepath)
    
    #checks if no list was returned and skips to next if that's true
    if len(titlelist) == 0:

        continue
    
    #urllist
    urlpath = '//h3/a/@href'
    urllist = tree.xpath(urlpath)
    
    #return df for searching
    searchdf = pd.DataFrame(data = {'hltbTitle':titlelist, 'hltbURL':urllist}, index= titlelist)

    #using update method and indexing to update gameslist from searchdf for multiple titles if exists
    #map hltbURL to hltbTitle
    try:
        gameslist.update(searchdf)
    
    #Error handling for issues if multiple games exist with the same title    
    except ValueError:

        #updates hltbTitle but not the URL since there are duplicate games with the same name and URL needs to be confirmed
        hltbTitle = titlelist[0]

        #update hltbTitle for current index
        gameslist.loc[i.Index, 'hltbTitle'] = hltbTitle
        
        #move onto next iteration
        continue
    
    try:
        #If update method did not work because Titles did not match so hltbTitle and hltbURL are still NaN
        #Take first value from list and update the Title and URL  
        TitleMatch = not ((gameslist.loc[i.Index, 'hltbTitle'] != gameslist.loc[i.Index, 'hltbTitle']) and (gameslist.loc[i.Index, 'hltbURL'] != gameslist.loc[i.Index, 'hltbURL']))
    
    #exception for when there are multiple indexes for the current title all() needs to be used for logic       
    except ValueError:
        
        TitleMatch = not (all(gameslist.loc[i.Index, 'hltbTitle'] != gameslist.loc[i.Index, 'hltbTitle']) and all(gameslist.loc[i.Index, 'hltbURL'] != gameslist.loc[i.Index, 'hltbURL']))
         
    
    if TitleMatch == False:
        
        #sets the hltb title and url to be the first value
        hltbTitle = titlelist[0]
        hltbURL = urllist[0]
        
        #updates the values in the list
        gameslist.loc[i.Index, 'hltbTitle'] = hltbTitle
        gameslist.loc[i.Index, 'hltbURL'] = hltbURL

#reset index
gameslist = gameslist.reset_index()

#sets titleMatch value
gameslist.loc[gameslist.hltbTitle == gameslist.Titles, 'titleMatch'] = True
gameslist.loc[gameslist.hltbTitle != gameslist.Titles, 'titleMatch'] = False

#sets full URL values
gameslist.loc[~gameslist.hltbURL.str.contains('https://howlongtobeat.com/|URL missing') , 'hltbURL'] = 'https://howlongtobeat.com/' + gameslist.hltbURL 

#writes to csv file
gameslist.to_csv('GamesList.csv')

