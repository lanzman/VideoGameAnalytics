from lxml import html
import requests
import pandas as pd

#change directory
os.chdir(r'C:\Users\mike.lanza\Documents\Python\GitHub\VideoGameAnalytics')

#import gameslist csv
gameslist = pd.read_csv('GamesList.csv', index_col=0)

#sets the mainURL and searchURL
mainURL = r'https://howlongtobeat.com/'
searchURL = r'https://howlongtobeat.com/search_main.php?page=1'

#initiates hltb requests
hltb = requests.get(mainURL)

for i in gameslist.loc[(pd.isnull(gameslist.hltbTitle))].itertuples():
    
    print(i)
    
    #sets the title variable
    title = i.Titles
        
    #search request using POST
    r = requests.post(searchURL, data = {'queryString' : title})

    #get html from page
    tree = html.fromstring(r.content)
    
    #titlelist
    titlepath = '//h3/a/text()'
    titlelist = tree.xpath(titlepath)
    
    #checks if no list was returned
    if len(titlelist) == 0:
        
        continue
    
    #urllist
    urlpath = '//h3/a/@href'
    urllist = tree.xpath(urlpath)
    
    #sets the hltb title and url to be the first value
    htlbTitle = titlelist[0]
    htlbURL = urllist[0]
    
    #updates the values in the list
    gameslist.loc[i.Index, 'hltbTitle'] = hltbTitle
    gameslist.loc[i.Index, 'hltbURL'] = hltbURL
    
    #return df for searching
    searchdf = pd.DataFrame({'hltbTitle':titlelist, 'hltbURL':urllist})
    
    #looks through searchdf for other games in list and updates hltbTitle and hltbURL
    for i in gameslist.loc[gameslist.Titles.isin(searchdf.hltbTitle[1:]),:].itertuples():
    
        gameslist.loc[i.Index,'hltbTitle'] = searchdf.loc[searchdf.hltbTitle == i.Titles]['hltbTitle'].values[0]
        gameslist.loc[i.Index,'hltbURL'] = searchdf.loc[searchdf.hltbTitle == i.Titles]['hltbURL'].values[0]
        gameslist.loc[i.Index,'titleMatch'] = True
    
    #checks if more than 1 match returned
    if len(titlelist) > 1:
        
        for i in titlelist:
        
            print(i)
        
    print(titlelist)
    print(urllist)

#sets titleMatch value
gameslist.loc[gameslist.hltbTitle == gameslist.Titles, 'titleMatch'] = True

#writes to csv file
gameslist.to_csv('GamesList.csv')

