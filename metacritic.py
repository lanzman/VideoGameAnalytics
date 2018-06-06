from lxml import html
import requests
import pandas as pd

def getmetadata(gamesdf):
    
    #sets up df for searching
    metacriticdf = gamesdf.loc[(gamesdf.metacriticMetaScore.isnull()) | (gamesdf.metacriticMetaScore == 'invalidURL')].copy()
    
    metacriticdf = gamesdf
    
    #create metacritic platformURL
    metacriticdf['platformURL'] = metacriticdf['Platform'].str.split('/').str[0].str.lower()
    
    #create subsitution dictionary
    platformdict = {'ps4':'playstation-4', \
                   'ps3':'playstation-3', \
                   'pc': 'pc', \
                   'ps vita':'playstation-vita', \
                   '3ds': '3ds', \
                   'psp': 'psp', \
                   'ps2': 'playstation-2', \
                   'ps1': 'playstation', \
                   'ds': 'ds'}
    
    #replaces the extracted platform with the correct format for the URL
    metacriticdf.platformURL.replace(platformdict, inplace = True)
    
#    metacriticdf.loc[:,'metacriticTitle'] = metacriticdf.loc[:,'hltbTitle'].str.replace('\.| - | & | ', '-').str.replace('&|\'|,|:', '').str.lower()
    
#    metacriticdf.loc[:,'metacriticTitle'] = metacriticdf.loc[:,'hltbTitle'].str.replace('&|\'|,|:', '').str.replace('\W', '-').str.replace('-+','-').str.lower()
    
    #creates the metacriticTitle from hltbTitle or Titles where applicable
    metacriticdf['metacriticTitle'] = metacriticdf.loc[:,'hltbTitle'].str.replace('&|\'|,|:', '').str.replace('\W', '-').str.replace('-+','-').str.lower()
    metacriticdf.loc[metacriticdf.hltbTitle.isnull(),'metacriticTitle'] = metacriticdf.loc[:,'Titles'].str.replace('&|\'|,|:', '').str.replace('\W', '-').str.replace('-+','-').str.lower()
    
    #generate metacriticURL
    metacriticdf['metacriticURL'] = 'http://www.metacritic.com/game/' + metacriticdf['platformURL'] + '/' + metacriticdf['metacriticTitle']
    
    #sets the headers required for the get request
    headers = {'User-Agent' : "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36"}
    
    #loops through titles for metacritic scores
    for i in metacriticdf.itertuples():
        
        #sets the url
        orgurl = i.metacriticURL
        
        print(orgurl)
        
        url, orgmetascore, orguserscore = getscores(orgurl,headers)
        
        #if a list was returned, need to run getscores again
        if type(url) == list:
            
            #sets the new url and scores values
            url, metascore, userscore = getscores(url,headers)
        
            #if a list was still returned, full scores were not found and original url and scores will be returned
            if type(url) == list:
                
                url = orgurl
                metascore = orgmetascore
                userscore = orguserscore
        
        #if not a list url and scores should be accepted
        else:
            
            url = orgurl
            metascore = orgmetascore
            userscore = orguserscore
        
        #sets the metacriticdf URL value
        metacriticdf.loc[i.Index,'metacriticURL'] = url
        
        #set score value    
        metacriticdf.loc[i.Index, 'metacriticMetaScore'] = metascore
        metacriticdf.loc[i.Index, 'metacriticUserScore'] = userscore
    
#    gamesdf.drop(['platformURL','metacriticURL','metacriticScore','metacriticTitle'],axis = 1, inplace =True)
#    
#    gamesdf['platformURL'] = None    
#    gamesdf['metacriticTitle'] = None
#    gamesdf['metacriticURL'] = None
#    gamesdf['metacriticMetaScore'] = None
#    gamesdf['metacriticUserScore'] = None
#    
#    #updates gamesdf
#    gamesdf.update(metacriticdf)
#    
#    return gamesdf
     
    return metacriticdf

def getscores(url, headers):
    
    #path to extract the metacritic score, userscore, and other platform links
    metascorepath = '//a[@class="metascore_anchor"]/div/span[@itemprop="ratingValue"]/text()'
    userscorepath = '//a[@class="metascore_anchor"]/div/text()'
    linkpath = '//li[@class="summary_detail product_platforms"]/span[@class="data"]/a/@href'
    
    #initializes metascore values
    metascore = None
    userscore = None
    
    #if it's a single url, it will come in as a string and needs to be converted to list
    if type(url) == str:
        #converts to list
        url = [url]
    
    #loops through urls for testing    
    for i in url:
            
        #creates the metacritic html page and tree
        metacriticpage = requests.get(i, headers = headers)
        
        #creates the html tree for parsing the xpath
        tree = html.fromstring(metacriticpage.content)
        
        #checks if a single link was passed
        if len(url) == 1:
            #gets the other platform links
            linklist = tree.xpath(linkpath)
            
            #checks if other platforms were available and sets it to the url
            if len(linklist) != 0:
                linklist = ['http://www.metacritic.com' + link for link in linklist]
                url = linklist
        
        #checks if URL worked
        if metacriticpage.status_code == 404:
            
            #sets to invalidURL
            metascore = 'invalidURL'
            userscore = 'invalidURL'
            
            #ends function and returns values
            return i, metascore, userscore

        #checks for a metascore and if none, checks for one
        if metascore == 'No Score Recorded' or metascore == None:
            #attempts to get the metascore
            try:
                #gets the scorelist
                metascore = tree.xpath(metascorepath)[0]
            except IndexError:
                metascore = 'No Score Recorded'
        
        #checks for a userscore and if none, checks for one
        if userscore == 'No Score Recorded' or userscore == None:    
            #attempts to get the userscore
            try:
                #gets the userscore
                userscore = tree.xpath(userscorepath)[0]
            except IndexError:
                userscore = 'No Score Recorded'
        
        #if both the metascore and userscore have been recorded, end the loop
        if metascore != 'No Score Recorded' and userscore != 'No Score Recorded':
            
            return i, metascore, userscore
    
    #if all links ran through, return values and end function
    return url, metascore, userscore
    

#url = 'http://www.metacritic.com/game/playstation-3/soul-sacrifice'
#      
#url, metascore, userscore = getscores(url,headers)
#
#getscores(url,headers)

# if url doesn't work, 
# if url works, it will return a string and invalid urls
# if platform not giving right values, it'll return a list of urls
# if list passed through, will return the best url as a string
    
    
    ###ADD section to drop unecessary columns before merging
    #metacriticdf.drop(labels =['])
    
    #get something for posting searches

def manualsearch(metacriticdf):
    
    #URL for searching and sending POST request
    searchURL = 'http://www.metacritic.com/autosearch'
    
    #headers need to be sent in order for the post requests to work
    headers = {'User-Agent' : "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36"}
    
    #path to get list of titles and links
    titlelinkpath = '//h3/a/text()'
    
    #path to get list of some of the metadata
    metadatapath = '//li/div/div/div/p'
    
    #init yes/no choice    
    yes = ['yes','y', 'ye', '']
    no = ['no','n']
    topten =  ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
    
    for i in metacriticdf.loc[(metacriticdf.metacriticMetaScore == 'invalidURL') | (metacriticdf.metacriticUserScore == 'invalidURL')].itertuples():
        
        #input to enter a title to search for
        searchtitle = input('Please enter new title for ' + i.Titles + ' (' + i.Platform + ').\n')
        
        #exits loop
        if searchtitle == 'exit':
            
            print('Ending search loop.')
            break
        elif searchtitle in no:
            print('Skipping to next title.\n')
            continue
        
        #while loop to run for continuous searching, will exit on exit
        while searchtitle != None:
        
            #creates the post request
            #all three form values need to be sent in order for the search to work.  Once search_filter is absent, it will not run
            r = requests.post(url = searchURL, 
                              data = {'search_term' : searchtitle, 'image_size' : "98", 'search_filter' : "game"},
                              headers=headers, timeout = 15)
            
            #creates the html tree
            tree = html.fromstring(r.text)
            
            #path to get list of titles and links
            titlelinkpath = '//h3/a'
            
            #creates the lists from the xpath of the html tree
            titlelinklist = tree.xpath(titlelinkpath)
            metadatalist = tree.xpath(metadatapath)
            
            #checks if there are results
            if len(titlelinklist) == 0:
                
                print('No results found!')
                searchresult = 'no'
            
            else:
        
                #initiates metalist if needed
                metalist = []
                
                #initiates k for display numbering
                k = 1
                
                #iterates through both lists using zip to display results
                for title, meta in zip(titlelinklist, metadatalist):
                    
                    #appends metadata to metalist
                    metalist.append("".join(meta.itertext()).split())
                    
                    #prints out the results
                    print(k, ' ', title.text.strip(), ' ', metalist[k-1][0], ' ', metalist[k-1][2])
                    
                    #iterates k
                    k+=1
                
                #returns the hltbTitle from the search
                searchresult = input('Enter corresponding number for title you wish to use or n to enter a new search\n').lower()
                
            #if user accepts search result, the gamesdf will be updated
            if (searchresult in yes) or (searchresult in topten):
                
                #if first result accepted
                if searchresult in yes:
                    searchindex = 0
                #otherwise set search index down one
                else:
                    searchindex = int(searchresult) - 1
            
                #sets the url to pull data from
                orgurl = 'http://www.metacritic.com' + titlelinklist[searchindex].items()[0][1]
                
                #runs getscores function
                url, orgmetascore, orguserscore = getscores(orgurl,headers)
                
                #if a list was returned, need to run getscores again
                if type(url) == list:
                    
                    #sets the new url and scores values
                    url, metascore, userscore = getscores(url,headers)
                
                    #if a list was still returned, full scores were not found and original url and scores will be returned
                    if type(url) == list:
                        
                        url = orgurl
                        metascore = orgmetascore
                        userscore = orguserscore
                
                #if not a list url and scores should be accepted
                else:
                    
                    url = orgurl
                    metascore = orgmetascore
                    userscore = orguserscore
                
                #splits up url into components for metadata
                urlsplit = url.split('/')
                
                #sets the metacriticdf URL value
                metacriticdf.loc[i.Index,'metacriticURL'] = url
                
                
                metacriticdf.loc[i.Index,'metacriticTitle'] = urlsplit[-1]
                metacriticdf.loc[i.Index,'platformURL'] = urlsplit[-2]
                
                #set score value    
                metacriticdf.loc[i.Index, 'metacriticMetaScore'] = metascore
                metacriticdf.loc[i.Index, 'metacriticUserScore'] = userscore
                
                #for breaking out of searchtitle loop
                searchtitle = None
            
            #if user doesn't accept search result, allows them to search again
            elif searchresult in no:
                
                #user can search again
                searchtitle = input('Search returned nothing, please enter new titlesearch for '  + i.Titles + ' (' + i.Platform + ').\n')
    
                #if anything else, moves onto next title
                if searchtitle.lower() in no:
                    
                    print('Moving on to next title.')
                    
                    #for breaking out of searchtitle loop
                    searchtitle = None
    
            #handles any other answer
            else:
                
                print('Please enter valid answer.')
    