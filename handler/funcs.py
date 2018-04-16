import os
import datetime
import zipfile
import settings
import time
import random
import asyncio
from pymongo import MongoClient

languages = {'python': ['py', '', 'python3 MyBot.py'],
 'java': ['java', 'javac MyBot.java', 'java MyBot'],
 'rust': ['rs', 'cargo rustc --release -q -- -Awarnings', 'target/release/MyBot'],
 'javascript': ['js', '', 'node MyBot.js'],
 'c++': ['cpp', 'set -e && cmake . && make MyBot', './MyBot'],
 'dart': ['dart', '', 'dart MyBot.dart'],
 'go': ['go', 'export GOPATH=$(pwd) && go build MyBot.go', './MyBot'],
 'haskell': ['hs', 'ghc --make MyBot.hs -O -v0 -rtsopts -outputdir dist', './MyBot.exe'],
 'ruby': ['rb', '', 'ruby MyBot.rb'],
 'c#': ['cs', 'xbuild Halite2/Halite2.csproj', 'mono Halite2/bin/Debug/Halite2.exe']}

def log(string):

    """
    A simple log function
    """

    string = "Timestamp: - "+getTime()+" "+ string
    with open(settings.path+"/"+settings.logFile, 'a') as (out):
        out.write(string + '\n')
    return '**' + string + '**'

def getTime():

    """
    Function to get and format current time, just to
    speed things up
    """

    return ('{:%Y-%m-%d %H:%M:%S}').format(datetime.datetime.now())

def str_to_bool(s):

    """
    Helper function to handle json settings
    """

    if s == 'True':
        return True
    if s == 'False':
        return False

async def uploadBot(link, username, fileName):

    """
    Function that downloads zip file, unzips it,
    recognize the language used, stores it into the
    player in the database and then runs the
    compiler function
    """

    username = username.replace(' ', '')
    player = settings.db.players.find_one({"username":username})
    save = settings.path + '/../bots/' + username + '/'

    if player is None:
        player = {
            "username":username,
            "path":save,
            "lang":"",
            "commands":[],
            "flagged":False,
            "running":False
        }
        playerId = settings.db.players.insert_one(player).inserted_id

    else:
        playerId = player.get("_id")

    if not player.get('running'):
        try:
            os.system("rm -r "+save+" > /dev/null 2>&1") #clean up folders
            os.mkdir(save) #create folder
            if fileName[-4:] == '.zip': #check file is a zip file
                os.system('wget -q -O ' + save + fileName + ' ' + link)
                z = zipfile.ZipFile(save + fileName, 'r')
                z.extractall(save)
                z.close()

                found = False
                lang, lib = None, None
                for f in os.listdir(save):
                    if f.startswith('MyBot.'):
                        for k, v in languages.items():
                            if f.replace('MyBot.', '') == v[0]:
                                found = True
                                lang = v
                                if f.replace('MyBot.', '') == "py" and os.path.isfile(save+"requirements.txt"):
                                    lib = os.popen("cd "+save+" && pip3 install -r "+save+"requirements.txt").read()

                                elif r.replace('MyBot', '') == "js" and os.path.isfile(save+"package.json"):
                                    lib = os.popen("cd "+save+" && npm install").read()
                                break


                    elif f.startswith("src"):
                        for s in os.listdir(save+"src/"):
                            if s == "MyBot.go":
                                lang = languages.get("go")
                                found = True
                                lib = os.popen("cd "+save+" && go get").read()
                                break
                            elif s == "main.rs":
                                lang = languages.get("rs")
                                found = True
                                break

                    elif f.startswith("Halite2"):
                        for s in os.listdir(save+"Halite2/"):
                            if s == "Halite2.csproj":
                                lang = languages.get("c#")
                                found = True
                                break

                    if found:
                        break

                compileLog = ""
                if lang != None and found:
                    settings.db.players.update_one({"_id":playerId}, {"$set":{"lang":lang[0], "commands":[lang[1], lang[2]]}}, upsert=True)
                    player = settings.db.players.find_one({"_id":playerId})
                    text, compileLog = await compileBot(player)
                    if compileLog != "" :
                        text = "File bot : "+fileName+", "+text

                    if lib != None :
                        text += "\nHere is output of external libraries installation :\n"+lib

                elif lang != None and not found:
                    text = 'File bot : ' + fileName + ' conatins a bot file but the language : '+ext+' isn\'t supported!'

                elif lang == None:
                    text = 'File bot : ' + fileName + ' does not contain a **MyBot** file of any type!'

                log(text)
                return text, compileLog

            return "File wasn't a .zip file, check the rules!", ""

        except Exception as e:
            s = log(str(e))
            return s, ""

    else:
        return "Cannot compile "+fileName+", user is already running a battle/match or compiling other code!", ""


async def compileBot(player):

    """
    Function that starts the compiler.
    player = player object from the database
    Function gets all the info needed to compile
    the code of this player from the object and
    adds it to the queue, then waits for it to
    be done ( or returns a timeout error ).
    It returns the result of the compiler and the
    compiler log.
    """

    #clean up logs
    os.system("rm -r "+settings.path+"/../env/out/"+player["username"]+".txt"" > /dev/null 2>&1")
    compileLog = ""
    data = {
        "type":"compile",
        "players":player,
        "status":"not-running",
        "logfile":"",
        "success":False
    }
    queueId = settings.db.queues.insert_one(data).inserted_id
    settings.db.players.update_one({"_id":player.get("_id")}, {"$set":{"running":True}}, upsert=True)

    secs = 0
    text = "took too much time to compile! Max is "+str(settings.compileOut)+"s"
    while secs <= settings.compileOut:
        q = settings.db.queues.find_one({"_id":queueId})
        if q.get("status") == "finished":
            if q.get("success"):
                compileLog = q.get("logfile")
                if compileLog != "":
                    text = "submitted, compiled and run successfully! Sending log file..."
                else:
                    text = "submitted, compiled and run successfully! Error loading log file..."

            else:
                compileLog = q.get("logfile")
                if compileLog != "":
                    text = "submitted but encountered an error compiling/running! Sending log file..."
                else:
                    text = "submitted but encountered an error compiling/running! Error loading log file as well..."

            break

        else:
            await asyncio.sleep(1)
            secs += 1

    settings.db.queues.delete_one({"_id":queueId})
    settings.db.players.update_one({"_id":player.get("_id")}, {"$set":{"running":False}}, upsert=True)

    return text, compileLog

async def battle(p1, p2, width, height, official):

    """
    Function that takes in these parametes:
    p1 = player one username (string)
    p2 = player two username (string)
    width = width of the map for battle (string)
    height = height for the map for battle (string)
    official = if battle is an official match (bool)
    Function creates a queue in the db, the handler
    stars the battle and here it keeps checking until
    is finished ( or return a timout error ).
    then returns the result of battle, the replay file,
    the player individual logs
    """

    p1Name = p1.replace(' ', '')
    p2Name = p2.replace(' ', '')

    p1 = settings.db.players.find_one({"username":p1Name})
    p2 = settings.db.players.find_one({"username":p2Name})

    p1Ava, p2Ava = False, False
    if p1 != None :
        p1Ava = True
    if p2 != None :
        p2Ava = True

    log1 = ""
    log2 = ""
    result = ""
    replay = ""
    status = ""

    if p1Ava and p2Ava :
        battleName = p1.get("username")+"VS"+p2.get("username")
        if p1.get("running") or p2.get("running"):
            status = "**Error setting up the battle!** "+p1Name+" already running : *"+str(p1.get("running"))+"*, "+p2Name+" already running : *"+str(p2.get("running"))+"*"

        else:
            os.system("rm "+settings.path+"/../env/out/"+battleName+"* > /dev/null 2>&1")
            if not official:
                data = {
                    "type":"battle",
                    "players":[p1, p2],
                    "status":"not-running",
                    "logfile":"",
                    "success":False,
                    "map":[width, height]
                }
                queueId = settings.db.queues.insert_one(data).inserted_id
                settings.db.players.update_one({"_id":p1.get("_id")}, {"$set":{"running":True}}, upsert=True)
                settings.db.players.update_one({"_id":p2.get("_id")}, {"$set":{"running":True}}, upsert=True)

                secs = 0
                status = "**Battle took too much time! Max is "+str(settings.runOut)+"s**"
                while secs <= settings.runOut: #time same as env/handler.py
                    q = settings.db.queues.find_one({"_id":queueId})
                    if q.get("status") == "finished" and os.path.isfile(q.get("logfile")):
                        if os.path.isfile(settings.path+"/../env/out/"+battleName+".hlt"):
                            replay = settings.path+"/../env/out/"+battleName+".hlt"
                            with open(q.get("logfile"), "r") as l:
                                result = "```"+l.read()+"```"
                            for f in os.listdir(p1.get("path")):
                                if f.endswith(".log"):
                                    log1 = p1.get("path")+f
                            for f in os.listdir(p2.get("path")):
                                if f.endswith(".log"):
                                    log2 = p2.get("path")+f
                                status = "**Battle ran successfully, here is the replay and halite output. Sending log files of players in DM...**"
                        else:
                            status = "**Error while running the battle, here is the halite output.**"

                        break

                    else:
                        await asyncio.sleep(1)
                        secs += 1

            else:
                data = {
                    "type":"match",
                    "players":[p1, p2],
                    "status":"not-running",
                    "logfile":"",
                    "success":False
                }
                queueId = settings.db.queues.insert_one(data).inserted_id
                settings.db.players.update_one({"_id":p1.get("_id")}, {"$set":{"running":True}}, upsert=True)
                settings.db.players.update_one({"_id":p2.get("_id")}, {"$set":{"running":True}}, upsert=True)

                secs = 0
                status = "**Match took too much time! Max is "+str(settings.runOut*settings.runs)+"s**"
                while secs <= settings.runOut*settings.runs:
                    q = settings.db.queues.find_one({"_id":queueId})
                    if q.get("status") == "finished":
                        if os.path.exists(settings.path+"/../env/out/"+battleName+"/battle.log"):
                            with open(settings.path+"/../env/out/"+battleName+"/battle.log", "r") as l:
                                result = "```"+l.read()+"```"

                            if os.path.exists(settings.path+"/../env/out/"+battleName+"/"+str(settings.runs)+".hlt"):
                                replay = settings.path+"/../env/out/"+battleName+"/match.zip"
                                status = "**Match ran successfully, here are the results and the replays.**"
                            else:
                                status = "**Error while running the match, here is the halite output.**"

                            break

                    else:
                        await asyncio.sleep(1)
                        secs += 1

            settings.db.queues.delete_one({"_id":queueId})
            settings.db.players.update_one({"_id":p1.get("_id")}, {"$set":{"running":False}}, upsert=True)
            settings.db.players.update_one({"_id":p2.get("_id")}, {"$set":{"running":False}}, upsert=True)

    else:
        status = "**Error setting up the battle! Submissions state :** ***"+p1Name+"="+str(p1Ava)+" "+p2Name+"="+str(p2Ava)+"***"

    return status, result, log1, log2, replay
