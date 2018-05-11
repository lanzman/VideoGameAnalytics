from lxml import html
import requests
import pandas as pd

#gets the hltbURL, hltbTitle, and playtime
def geturl(gamesdf):
    
    #set Titles to index for quick updating during loop
    gamesdf = gamesdf.set_index('Titles')
    
    #loop through all titles to post requests
    for i in gamesdf.loc[(gamesdf.hltbTitle.isnull()) | (gamesdf.hltbURL.isnull())].itertuples():
        
        print(i)
        #sets the searchURL
        searchURL = r'https://howlongtobeat.com/search_main.php?page=1'
        
        try:
            #checks if hltbTitle and hltbURL are both NOT NaN, if they are anything, they have already been processed through the update method and can be skipped
            Processed = (gamesdf.loc[i.Index,'hltbTitle'] == gamesdf.loc[i.Index,'hltbTitle']) and (gamesdf.loc[i.Index,'hltbURL'] == gamesdf.loc[i.Index,'hltbURL'])
            multiindex = False
        except ValueError:
            #checks if hltbTitle and hltbURL are both NOT NaN, if they are anything, they have already been processed through the update method and can be skipped
            Processed = all(gamesdf.loc[i.Index,'hltbTitle'] == gamesdf.loc[i.Index,'hltbTitle']) and all(gamesdf.loc[i.Index,'hltbURL'] == gamesdf.loc[i.Index,'hltbURL'])
            multiindex = True
            
        if Processed == False:
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
            
            #create df for searching and updating
            searchdf = pd.DataFrame(data = {'hltbTitle':titlelist, 'hltbURL':urllist}, index= titlelist)
            
            #fills out remaining part of url
            searchdf['hltbURL'] = 'https://howlongtobeat.com/' + searchdf['hltbURL']
            
            #Sets TitleMatch value for searchdf
            searchdf['TitleMatch'] = True
            
            #using update method and indexing to update gamesdf from searchdf for multiple titles that were returned from search if exists
            #map hltbURL, hltbTitle, and TitleMatch
            gamesdf.update(searchdf)
            
        #look into changing this to utilize the TitleMatch field
        try:
            #If update method did not work because Titles did not match so hltbTitle and hltbURL are still NaN
            #Take first value from list and update the Title and URL  
            TitleMatch = not ((gamesdf.loc[i.Index, 'hltbTitle'] != gamesdf.loc[i.Index, 'hltbTitle']) and (gamesdf.loc[i.Index, 'hltbURL'] != gamesdf.loc[i.Index, 'hltbURL']))
            print('single match')
        #exception for when there are multiple indexes for the current title all() needs to be used for logic       
        except ValueError:
            
            TitleMatch = not (all(gamesdf.loc[i.Index, 'hltbTitle'] != gamesdf.loc[i.Index, 'hltbTitle']) and all(gamesdf.loc[i.Index, 'hltbURL'] != gamesdf.loc[i.Index, 'hltbURL']))
            print('multi match')
        
        #if TitleMatch is False, update the gamesdf with the first Title and URL from the returned list, this will be checked later
        if TitleMatch == False:
            
            #sets the hltb title and url to be the first value
            hltbTitle = titlelist[0]
            hltbURL = 'https://howlongtobeat.com/' + urllist[0]
            
            #updates the values in the list
            gamesdf.loc[i.Index, 'hltbTitle'] = hltbTitle
            gamesdf.loc[i.Index, 'hltbURL'] = hltbURL
            gamesdf.loc[i.Index, 'TitleMatch'] = False
            
            #sets the mainlength value
            mainlength = 'URL missing'
        
        #if TitleMatch is False, go forward and get the timing metrics
        else:
            
            if multiindex == True:
                #sets the searchURL
                searchURL = gamesdf.loc[i.Index, 'hltbURL'][0:1][0]
            else:
                #sets the searchURL
                searchURL = gamesdf.loc[i.Index, 'hltbURL']
            
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
        
    #reset index
    gamesdf.reset_index(level = 0, inplace = True)
    
#    #sets titleMatch value
#    gamesdf.loc[gamesdf.hltbTitle == gamesdf.Titles, 'TitleMatch'] = True
#    gamesdf.loc[gamesdf.hltbTitle != gamesdf.Titles, 'TitleMatch'] = False
    
#    #Remove NaNs and replace with URL missing and Title missing
#    gamesdf.hltbURL = gamesdf.hltbURL.fillna('URL missing')
#    gamesdf.hltbTitle = gamesdf.hltbTitle.fillna('Title missing')
    
#    #sets full URL values
#    gamesdf.loc[~gamesdf.hltbURL.str.contains('https://howlongtobeat.com/|URL missing') , 'hltbURL'] = 'https://howlongtobeat.com/' + gamesdf.hltbURL 
    
    #create dataframe with missing data
    checklist = gamesdf.loc[(gamesdf.mainlength == 'URL missing') | (gamesdf.hltbTitle == 'Title missing')].copy()
    
    ### run last line of code after manually updating Titles
    ### run urlloop after updating Titles
    
#    #update gamesdf with checklist
#    gamesdf.loc[checklist.index, 'hltbTitle'] = checklist.hltbTitle
#    gamesdf.loc[checklist.index, 'hltbURL'] = checklist.hltbURL

    return gamesdf, checklist