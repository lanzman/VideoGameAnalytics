#search request using POST
title = 'Dead Space'

r = requests.post(searchURL, data = {'queryString' : title})

#get html from page
tree = html.fromstring(r.content)

#titlelist
titlepath = '//h3/a/text()'
titlelist = tree.xpath(titlepath)

#urllist
urlpath = '//h3/a/@href'
urllist = tree.xpath(urlpath)

#sets the hltb title and url to be the first value
htlbTitle = titlelist[0]
htlbURL = urllist[0]

#return df for searching
searchdf = pd.DataFrame({'hltbTitle':titlelist, 'hltbURL':urllist})

searchdict = dict(zip(titlelist, urllist))

gameslist.hltbURL = gameslist.Titles.map(searchdict)

searchdf.to_dic

searchdict = searchdf.to_dict(orient = 'list')

print(searchdict)

searchdict['hltbTitle']

gameslist.loc[gameslist.Titles.isin(searchdf.hltbTitle[1:]), ['hltbTitle','hltbURL']] = np.NaN

#looks through searchdf for other games in list and updates hltbTitle and hltbURL
for i in gameslist.loc[gameslist.Titles.isin(searchdf.hltbTitle[1:]),:].itertuples():

    gameslist.loc[i.Index,'hltbTitle'] = searchdf.loc[searchdf.hltbTitle == i.Titles]['hltbTitle'].values[0]
    gameslist.loc[i.Index,'hltbURL'] = searchdf.loc[searchdf.hltbTitle == i.Titles]['hltbURL'].values[0]
    gameslist.loc[i.Index,'titleMatch'] = True

gameslist[gameslist.Titles.isin(searchdf.hltbTitle)]


test = gameslist[gameslist.Titles.isin(searchdf.hltbTitle)]

test

test.hltbURL = searchdf.hltbURL