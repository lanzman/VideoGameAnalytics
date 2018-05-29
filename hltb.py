from lxml import html
import requests
import pandas as pd


#performs a manual search of the dataframe
def manualsearch(gamesdf):
    
    #sets the searchURL
    searchURL = r'https://howlongtobeat.com/search_main.php?page=1'
        
    #init yes/no choice    
    yes = ['yes','y', 'ye', '']
    no = ['no','n']
    
    
    for i in gamesdf.loc[gamesdf.hltbTitle != gamesdf.hltbTitle].itertuples():
        
        #input to enter a title to search for
        searchtitle = input('Please enter new title for ' + i.Titles + '.\n')
        
        #exits loop
        if searchtitle == 'exit':
            
            print('Ending search loop.')
            break
        elif searchtitle in no:
            print('Skipping to next title.\n')
            continue
        
        #while loop to run for continuous searching, will exit on exit
        while searchtitle != None:
            
            #gets the searchdf back from the title search
            searchdf = titlesearch(searchtitle,searchURL)
            
            #checks if there are results
            if len(searchdf) == 0:
                
                print('No results found!')
                searchresult = 'no'
            
            else:
                #returns the hltbTitle from the search
                searchresult = input('Resulting title is ' + searchdf.hltbTitle[0] + ', do you accept?\n').lower()
                
            #if user accepts search result, the gamesdf will be updated
            if searchresult in yes:
    
                #updates the title in the gamesdf
                gamesdf.loc[i.Index, 'Titles'] = searchdf.hltbTitle[0]
                gamesdf.loc[i.Index, 'hltbTitle'] = searchdf.hltbTitle[0]
                gamesdf.loc[i.Index, 'TitleMatch'] = searchdf.TitleMatch[0]
                gamesdf.loc[i.Index, 'hltbURL'] = searchdf.hltbURL[0]
                gamesdf.loc[i.Index, 'mainlength'] = getmainlength(searchdf.hltbURL[0])
                
                #for breaking out of searchtitle loop
                searchtitle = None
            
            #if user doesn't accept search result, allows them to search again
            elif searchresult in no:
                
                #user can search again
                searchtitle = input('Search returned nothing, please enter new titlesearch for ' + i.Titles + '.\n')
    
                #if anything else, moves onto next title
                if searchtitle.lower() in no:
                    
                    print('Moving on to next title.')
                    
                    #for breaking out of searchtitle loop
                    searchtitle = None
    
            #handles any other answer
            else:
                
                print('Please enter valid answer.')

    return gamesdf

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
            
            #perform title search
            searchdf = titlesearch(title, searchURL)
            
            #if titlesearch yields nothing, continue to next item
            if len(searchdf) == 0:
                
                continue
            
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
            hltbTitle = searchdf.hltbTitle[0]
            hltbURL = searchdf.hltbURL[0]
            
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
            
            #sets the mainlength variable
            mainlength = getmainlength(searchURL)
        
        #updates the value in the gamesdf
        gamesdf.loc[i.Index,'mainlength'] = mainlength
        
        print(mainlength)
        
    #reset index
    gamesdf.reset_index(level = 0, inplace = True)
    
    #create dataframe with missing data
    checklist = gamesdf.loc[(gamesdf.mainlength == 'URL missing') | (gamesdf.hltbTitle == 'Title missing')].copy()
    
    return gamesdf, checklist

#performs titlesearch on hltb site from title that is passed through
def titlesearch(title, searchURL):
    
    #search request using POST
    r = requests.post(searchURL, data = {'queryString' : title})
    
    #sets encoding to be utf-8 to handle special characters
    r.encoding = 'utf-8'
    
    #get html from page
    tree = html.fromstring(r.text)
    
    #titlelist
    titlepath = '//h3/a/text()'
    titlelist = tree.xpath(titlepath)
    
    #checks if no list was returned and skips to next if that's true
    if len(titlelist) == 0:
        
        #creates empty dataframe
        searchdf = pd.DataFrame()
        
        return searchdf
    
    #urllist
    urlpath = '//h3/a/@href'
    urllist = tree.xpath(urlpath)
    
    #create df for searching and updating
    searchdf = pd.DataFrame(data = {'hltbTitle':titlelist, 'hltbURL':urllist}, index= titlelist)
    
    #fills out remaining part of url
    searchdf['hltbURL'] = 'https://howlongtobeat.com/' + searchdf['hltbURL']
    
    #Sets TitleMatch value for searchdf
    searchdf['TitleMatch'] = True
    
    #drops the duplicates based on the hltbTitle
    searchdf.drop_duplicates(subset = ['hltbTitle'], inplace = True)
    
    return searchdf
    
#gets the mainlength of a game from the URL
def getmainlength(searchURL):
    
    #initiates gamepage requests
    gamepage = requests.get(searchURL)
       
    #get html from page
    tree = html.fromstring(gamepage.content)
        
    #tablepath
    tablepath = '//table[@class="game_main_table"]/tbody[@class="spreadsheet"][1]/tr/td/text()'
    lengthlist = tree.xpath(tablepath)
    
    #if nothing returned, skip to next title
    if len(lengthlist) == 0:
        
        mainlength = 'URL missing'
    else:
        #sets the mainlength variable
        mainlength = lengthlist[2]

    return mainlength

#checks the collected title vs the entered title and sets the mainlength if accepted
def verifychecklist(gamesdf, checklist):
    
    #init yes/no choice    
    yes = ['yes','y', 'ye', '']
    no = ['no','n']
    
    #loops through the checklist to allow user to accept new title and get mainlength value
    for i in checklist.loc[checklist.mainlength == 'URL missing'].itertuples():
        
        #prints out the Original Title and HLTB Title
        print(i.Titles, ' --> ', i.hltbTitle)
        
        #sets choice to none
        choice = None
        
        #checks the result of the choice to continue running loop
        while choice not in yes and choice not in no:
            
            #creates yes no input to accept the new title
            choice = input('Do you accept the new HLTB Title?\n').lower()
            
            #if user accepts, runs function to get the mainlength value
            if choice in yes:
                
                #gets mainlength value and sets it in the dataframe
                checklist.loc[i.Index, 'mainlength'] = getmainlength(i.hltbURL)
                print('Updated!\n')
                
            #if user declines, does nothing
            elif choice in no:
                print('Not Updated!\n')
            
            #exit allows user to exit the loop
            elif choice == 'exit':
                print('Exiting loop!\n')
                break
            #if selection not accepted, re-runs loop
            else:
                print('Please give a better answer.')
        
        #breaks out of loop when exit is selected
        if choice == 'exit':
            break
    
    #updates the gamesdf
    gamesdf.update(checklist)
    
    #reduces the checklist
    checklist = checklist.loc[checklist.mainlength == 'URL missing']
    
    print('Verification Complete!')
    
    return gamesdf, checklist