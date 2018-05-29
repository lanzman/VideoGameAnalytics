# -*- coding: utf-8 -*-
"""
Created on Wed May  2 13:48:37 2018

@author: mike.lanza
"""

from GoogleDrive import GDrive
import hltb

#GamesList file ID from GoogleDrive
GamesListFileID = '1OewpCqeugcbNEZQmsYaB9ItOnV9Kkfvuk83BRJaUHFY'
GamesListFileName = GDrive.getFilename(GamesListFileID)
GamesListFilePath = GamesListFileName + '.csv'

#downloads gameslist and converts to a dataframe
gamesdf = GDrive.DataFrameDownload(GamesListFileID)

#runs through the hltb geturl function and updates dataframe
gamesdf, checklist = hltb.geturl(gamesdf)

#passes gamesdf and checklist to manually accept titles, update URLs, and get mainlengths
gamesdf, checklist = hltb.verifychecklist(gamesdf, checklist)

#passes gamesdf and allows user to manually search for titles
gamesdf = hltb.manualsearch(gamesdf)

#gets metadata from Games List for updating
gamesdfmetadata = GDrive.searchFile(10, query = ("name contains '" + GamesListFileName + "'"))

#Updates the Games List File on the google drive
#will not work with pokemon special characters
GDrive.df_to_GoogleSheetUpdate(gamesdf, GamesListFileName, gamesdfmetadata[0]['id'])

