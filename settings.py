import os
import json

path = os.path.dirname(os.path.realpath(__file__))

s = json.load(open("settings.json"))

serverName = s.get('server') #Name of server : str
infos = s.get('infos') #File that contains infos of tournament : str
brackets = s.get('brackets') #File that contains the image of brackets : str
matches = s.get('matches') #Scheduled matches : dict with str keys and values of lists of str
logFile = s.get('log') #File used for the logging : str
season = s.get('season') #Number of season : str
token = s.get('token') #Token for the discord bot : str
submit = s.get('submit') #Submissions opened or closed : bool
onTour = s.get('onTour') #If a tournament is ongoing : bool
timeSub = s.get('timeSub') #Time when submissions open
runOut = s.get('runOut') #Timeout for battle
compileOut = s.get('compileOut') #Timeout for compiler
admins = s.get('admins') #The usernames of the admins
specs = s.get('specs')  #Tournament specs
engineLink = s.get('engineLink') #Link with info about engine

#Emojis
#<:logo:416779058924355596>
#<:aspiringcoder:419920520901951508>
#<:HTDollar:419938437831983144>
