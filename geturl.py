from lxml import html
import requests
import pandas as pd

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
    
    #checks if hltbTitle and hltbURL are both not NaN, if they are anything, they have already been processed and can be skipped
    if ~np.isnan(i.hltbTitle) and ~np.isnan(i.hltbURL):
            
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
    
    #checks if no list was returned
    if len(titlelist) == 0:

        continue
    
    #urllist
    urlpath = '//h3/a/@href'
    urllist = tree.xpath(urlpath)
    
    #return df for searching
    searchdf = pd.DataFrame(data = {'hltbTitle':titlelist, 'hltbURL':urllist}, index= titlelist)
    
    #return dict for mapping hltbURL to hltbTitle
    #searchdict = dict(zip(titlelist, urllist))
    
    #map hltbURL to hltbTitle
    gameslist.update(searchdf)
    
    #set hltbTitle = to Titles for matches
    #gameslist.hltbTitle = gameslist.loc[gameslist.Titles.isin(searchdf.index)].Titles
    
    print(gameslist.loc[i.Index, 'hltbTitle'])
    
    if gameslist.loc[i.Index, 'hltbTitle'] == np.NaN and gameslist.loc[i.Index, 'hltbURL'] == np.NaN:
        
        print('test')
        #sets the hltb title and url to be the first value
        htlbTitle = titlelist[0]
        htlbURL = urllist[0]
        
        #updates the values in the list
        gameslist.loc[i.Index, 'hltbTitle'] = hltbTitle
        gameslist.loc[i.Index, 'hltbURL'] = hltbURL


####Start from here and try to figure out why the print('test') section isn't firing off when a match isn't found
###



#reset index
gameslist = gameslist.reset_index()

#sets titleMatch value
gameslist.loc[gameslist.hltbTitle == gameslist.Titles, 'titleMatch'] = True









print(gameslist)

gameslist.hltbURL = searchdf.where(gameslist.Titles.isin(searchdf.index))

gameslist[gameslist.Titles.isin(searchdf.index)]

###This uses the update method and requires matching indexes ie:Title values
gameslist.update(searchdf)
test.update(searchdf1)

searchdf = pd.DataFrame(data = {'hltbTitle':titlelist, 'hltbURL':urllist}, index= titlelist)

print(searchdict1)
gameslist.loc[gameslist.Titles.isin(searchdf1.index)]

print(searchdict)
gameslist.loc[gameslist.Titles.isin(searchdf.index)]

test = gameslist.set_index('Titles')

test.update(searchdf)
test.update(searchdf1)

test.hltbTitle = test.loc[test.index.isin(searchdf.index)].index

test.loc[test.index.isin(searchdf.index)].hltbTitle = test.index.where(test.index.isin(searchdf.index))


test.loc[test.isin(searchdf)]

test.loc[test.index.isin(searchdf1.index)].hltbTitle

= test.loc[test.index.isin(searchdf.index)].index

gameslist.where(gameslist.Titles.isin(searchdf.index))

searchdf
searchdf1

#map hltbURL to hltbTitle
gameslist.loc[gameslist.Titles.isin(searchdf1.index)].hltbURL = gameslist.Titles.map(searchdict1, na_action=None)
gameslist.loc[gameslist.Titles.isin(searchdf.index)].hltbURL = gameslist.Titles.map(searchdict, na_action=None)

gameslist.hltbURL = gameslist.Titles.map(searchdict1, na_action=None)


gameslist.loc[gameslist.Titles.isin(searchdf1.index)]
gameslist.loc[gameslist.Titles.isin(searchdf.index)]


gameslist.hltbURL = gameslist.Titles.map(searchdict, na_action=None)

#set hltbTitle = to Titles for matches
gameslist.hltbTitle = gameslist.loc[gameslist.Titles.isin(searchdf.hltbTitle)].Titles


searchdf = pd.DataFrame(data = {'hltbURL':urllist}, index= titlelist)

print(searchdf)

gameslist.loc[gameslist.Titles.isin(searchdf.index)].hltbURL = searchdf.hltbURL


gameslist.loc[gameslist.Titles.isin(searchdf.index)].hltbURL


gameslist.hltbURL = gameslist.loc[gameslist.Titles.isin(searchdf.hltbTitle)].Titles



#writes to csv file
gameslist.to_csv('GamesList.csv')


#reset
gameslist.loc[:,['hltbTitle', 'hltbURL', 'titleMatch']] = np.NaN
gameslist.loc[:,['hltbTitle', 'hltbURL', 'titleMatch']]


gameslist[:1]

gameslist.loc[gameslist.hltbTitle.isnull()][:5]

#looks through searchdf for other games in list and updates hltbTitle and hltbURL
for i in gameslist.loc[gameslist.Titles.isin(searchdf.hltbTitle[1:]),:].itertuples():

    gameslist.loc[i.Index,'hltbTitle'] = searchdf.loc[searchdf.hltbTitle == i.Titles]['hltbTitle'].values[0]
    gameslist.loc[i.Index,'hltbURL'] = searchdf.loc[searchdf.hltbTitle == i.Titles]['hltbURL'].values[0]
    gameslist.loc[i.Index,'titleMatch'] = True


print(searchdf.loc[searchdf.hltbTitle == 'Dead Space 3']['hltbURL'].values)

test = searchdf.loc[searchdf.hltbTitle == 'Dead Space 3']['hltbURL']


print(searchdf)

gameslist.loc[gameslist.Titles.isin(searchdf.hltbTitle[1:]),['hltbTitle', 'hltbURL', 'titleMatch']] = ['', '', True]

gameslist.loc[gameslist.Titles == 'Dead Space 3']


gameslist.merge(searchdf, on=['hltbTitle', 'hltbURL'])

gameslist.merge(searchdf, on='hltbTitle')


#return df for searching
searchdf = pd.DataFrame({'hltbTitle':titlelist, 'hltbURL':urllist})

gameslist.update(searchdf)

gameslist.loc[gameslist.Titles == 'Dead Space 3']


gameslist.loc[gameslist.Titles == 'Dead Space 3'].update(searchdf)

gameslist.mer
#setup join instead of isin

for i in titlelist:
        
    print(i)
    
    print(gameslist[gameslist.Titles == i])



gameslist[:2]
#title to search
title = 'Assassin\'s Creed'

#search request using POST
r = requests.post(searchURL, data = {'queryString' : title})

#get html from page
tree = html.fromstring(r.content)

#titlelist
titlepath = '//h3/a/text()'
titlelist = tree.xpath(titlepath)
print(titlelist)

#urllist
urlpath = '//h3/a/@href'
urllist = tree.xpath(urlpath)
print(urllist)

#return df for searching
searchdf = pd.DataFrame({'title':titlelist, 'url':urllist})

#use loop to find match of title in df to get url
titleurl = searchdf.loc[searchdf['title'] == title]['url'][0]

print(titleurl)

print(titleurl)

hltb.raise_for_status()

hltb.text()

path = '//*[@id="global_search_content"]/li[1]/div[2]/h3/a'

