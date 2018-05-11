# -*- coding: utf-8 -*-
"""
Created on Wed May  2 13:48:37 2018

@author: mike.lanza
"""

#import sys
#
##focus on the files directory
#sys.argv[0]
#

from GoogleDrive import GDrive
import hltb


#
#
#GamesList file ID from GoogleDrive
GamesListFileID = '1OewpCqeugcbNEZQmsYaB9ItOnV9Kkfvuk83BRJaUHFY'

#downloads gameslist and converts to a dataframe
gamesdf = GDrive.DataFrameDownload(GamesListFileID)

#runs through the hltb geturl function and updates dataframe
gamesdf, checklist = hltb.geturl(gamesdf)



# need to work through this to figure out the proper folder structure to be used all over