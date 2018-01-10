for i in checklist.itertuples():
    
    print(i)
    
    #sets the title variable
    title = i.hltbTitle
        
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
    
    #sets the hltb title and url to be the first value
    hltbURL = urllist[0]
    
    #updates the values in the list
    checklist.loc[i.Index, 'hltbURL'] = 'https://howlongtobeat.com/' + hltbURL