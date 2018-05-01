import discord
import asyncio
import os
import json
import funcs
import settings
import subprocess

client = discord.Client()

commands = {"!help":"Show this message",
            "!submit":"Select your file and write this as a comment to submit your bot, you this in the season-"+settings.season+" to submit for the tournament",
            "!rules":"Display the rules of the current tournament",
            "!brackets":"Check current brackets",
            "!matches":"Print upcoming matches, tag a user after to check his upcoming matches",
            "!submissions":"Check if submissions are opened/closed and when they close/open",
            "!languages":"Check supported languages for submissions, add a language name to know how it's compiled/run e.g. !language python",
            "!battle":"Run a match between two players, \n\t!battle [p1] [p2] [height map] [width map] [bet]\n\tYou can write \"bet\" at the end of the command to automatically create a bet on the game with Vegas\n",
            "!donations":"Get infos about donations",
            "!specs":"Check tournament specs",
            "!engine":"Know how to get the engine of the current tournament",
            "!result":"Result [n of the battle], to show the results of battle with bet on",
            "!results":"Show all the battles with bets that are still hidden"}

adminCommands = {"!subs":"!subs True/False opens or closes submissions",
                 "!brk":"To add as a comment with the brackets image to update it",
                 "!clear":"!clear [n of message to delete] [channel, use * to select current]",
                 "!type":"!type [message to make the HTBot type]",
                 "!post":"!post [path to file in the server] [channel, se * to Select current] to post a file from the server",
                 "!ontour":"!ontour True/False to change the current tournament status",
                 "!admin":"Print this message",
                 "!time":"Change time of submissions"}

results = {}
global res
res = 0
global haliteVegas
haliteVegas = None

@client.event
async def on_ready(): #startup
    print("\nBot "+client.user.name+" ready to operate!")
    print("-------\n")
    global haliteVegas
    try:
        haliteVegas = discord.utils.get(client.get_all_channels(), server__name=settings.serverName, name='halite-vegas')
        print("\nInteraction with Vegas enabled")
    except:
        print("\nInteraction with Vegas not avaible")

@client.event
async def on_message(message):
    try :
        if message.content.startswith("!submit"):

            """
            This command submits a player's bot when submissions
            are opened. This command can be run in `battles`, `season-*`
            and via PMs to the bot.
            This command adds a queue to the handler, the handler then picks
            up the queue from the database and :
                - Checks if it's a valid submission
                - If the user isn't already running something
                - Installs external libraries (if required)
                - Compiles the code (if required)
                - Runs a test game against itself to make sure it works
                - Sends logs and compiler outputs via DM to the player
            """

            if not settings.submit : #if the submissions are closed
                await client.delete_message(message)
                await client.send_message(message.channel, "**Submissions are closed at the moment!** "+message.author.mention)
            else:
                if str(message.channel) != "season-"+settings.season and str(message.channel) != "battles": #if message is in the wrong channel
                    await client.delete_message(message)
                    await client.send_message(message.channel, "**Cannot use this command in this channel!** "+message.author.mention)
                else:
                    try:
                        await client.send_message(message.channel, "`Submitting, compiling and testing your bot...` "+message.author.mention)
                        response, compileLog = await funcs.uploadBot(message.attachments[0].get('url'), str(message.author), message.attachments[0].get('filename'))
                        await client.delete_message(message)
                        await client.send_message(message.channel, "`"+response+"` "+message.author.mention)
                        if compileLog != "": #if compiled and run successfully
                            await client.send_message(message.author, "**Here your compile and run log for yout bot submission!**")
                            await client.send_file(message.author, compileLog)

                    except IndexError : #no attachments present
                        await client.send_message(message.channel, "`No attachment present!` "+message.author.mention)


        elif message.content.startswith("!submissions"): #check submissions

            """
            This command shows the current status of submissions.
            Depending on the status the message changes, this command
            also shows when the submissions will close/open
            """

            if settings.submit:
                s, s2 = "opened", "close"
            else :
                s, s2 = "closed", "open"
            await client.send_message(message.channel, "**Current status of submissions : "+s+", the submissions will "+s2+" : "+settings.timeSub+"**")

        elif message.content.startswith("!help"): #help function

            """
            This command simply prints the name of all
            other commands with a brief explaination
            """

            text = "```\n"
            for k,c in sorted(commands.items()):
                text += k + " : " + c + "\n"
            text += "```"
            await client.send_message(message.channel, text)

        elif message.content.startswith("!rules"): #print info about the tournament

            """
            This command prints all the information about the
            tournament such as : dates, rules and prizes
            """

            if settings.onTour:
                try :
                    with open(settings.infos, "r") as f:
                        infos = f.read()
                        infos = infos.replace("\\n","\n")
                        await client.send_message(message.channel, infos)

                except FileNotFoundError:
                    await client.send_message(message.channel, "**Rules for current tournament are not ultimated!**")
            else:
                await client.send_message(message.channel, "**No tournament currently ongoing!**")


        elif message.content.startswith("!matches"): #check upcoming matches

            """
            This command allows everyone to check the upcoming
            matches. A player can also run :
                !matches @Splinter
            And this will return all the games that Splinter is in
            """

            if settings.onTour: #if we are running in a tournament
                m = str(message.content).split()
                if len(m) == 1: #check all matches
                    text = "**Here are the upcoming matches!**\n\n"
                    for k,v in sorted(settings.matches.items()):
                        text += "**" + k + "** : \n"
                        for p in v:
                            text += "\t" + p + "\n"

                else: #check specific matches for player
                    t = ""
                    player = ""
                    try :
                        player = str(message.mentions[0])

                    except IndexError:
                        text = "**Wrong formatting! Check `!help` for more info**"

                    if player != "":
                        for k,v in sorted(settings.matches.items()):
                            for p in v:
                                if player in p:
                                    t += "**" + k + "** : \n"
                                    t += "\t" + p + "\n"

                    if t != "":
                        text = "**Here are all the matches of : "+m[1]+"**\n"+t

                    elif player != "" and t == "" :
                        text = "**No matches scheduled for : "+m[1]+" !**"

            else :
                text = "**No scheduled matches!**"

            await client.send_message(message.channel, text)

        elif message.content.startswith("!battle"):

            """
            This command allows the players to battle against
            themselves whenever they want when there's an ongoing
            tournament. This feature is to allow the players to
            try out the game environment and debug their bots
            properly.
            It also has an integration with our bot Vegas which
            allows the player to hide the results and then
            close the bets for a certain game.
            Example of a command :
                !battle @Splinter @FrankWhoee 292 180 bet
            This command starts a game between FrankWhoee and Splinter
            with a map size of 292x180, also setting up a bet.
            """

            #if we are in a tournament and in the right channel
            if settings.onTour and str(message.channel) == "battles" :
                try:
                    #get the two players from mentions
                    p1 = str(message.mentions[0])
                    try:
                        p2 = str(message.mentions[1])
                    except :
                        p2 = str(message.mentions[0])

                    bet = False
                    try :
                        #get the map sizes
                        width = message.content.split()[3]
                        height = message.content.split()[4]
                        try:
                            if message.content.split()[5] == "bet":
                                bet = True

                        except:
                            pass

                    except : #if there is a problem set default size
                        await client.send_message(message.channel, "*Using default size map : 240x160*")
                        width = "240"
                        height = "160"

                    await client.send_message(message.channel, "*Running battle...* <:logo:416779058924355596>")
                    status, result, log1, log2, replay = await funcs.battle(p1, p2, width, height, False)
                    global haliteVegas
                    if haliteVegas != None and bet:
                        await client.send_message(haliteVegas, "!create "+message.mentions[0].mention+" "+message.mentions[1].mention)

                    await client.send_message(message.channel, status)

                    if result != "": #if we have an output
                        if haliteVegas != None and bet and status.startswith("**Battle ran successfully"):
                            global res
                            results.update({str(res):{"author":str(message.author), "result":result, "battle":p1+"VS"+p2}})
                            result = "**Hiding results until bet isn't closed, check output and close with !result "+str(res)+"**"
                            res += 1

                        await client.send_message(message.channel, result)

                        if replay != "" and not bet:
                            await client.send_file(message.channel, replay)

                        #check if logs are present and send them
                        if log1 != "":
                            await client.send_message(message.mentions[0], "**Here is the logfile of your bot : (timstamp battle : "+funcs.getTime()+")**")
                            await client.send_file(message.mentions[0], log1)
                            os.remove(log1)

                        if log2 != "":
                            await client.send_message(message.mentions[1], "**Here is the logfile of your bot : (timstamp battle : "+funcs.getTime()+")**")
                            await client.send_file(message.mentions[1], log2)
                            os.remove(log2)

                except IndexError : #formatting error
                    await client.send_message(message.channel, "**Bad formatting! Run !help for info about commands**")

            elif str(message.channel) != "battles": #wrong channel!
                battles = discord.utils.get(client.get_all_channels(), server__name=settings.serverName, name='battles')
                await client.send_message(message.channel, "**Run this in the "+battles.mention+" channel!**")

            else: #tournament is closed
                await client.send_message(message.channel, "**Feature not avaible at the moment!**")

        elif message.content.startswith("!results"):

            """
            Command to show all the battles that are
            opened to bets.
            """

            if len(results.items()) > 0:
                text = "**Here are all battles open to bets!**\n```\n"
                for num, r in results.items():
                    text += "- Number : "+num+", battle is "+r.get("battle")+"\n"
                text += "```"
            else:
                text = "**No battle with active bet at the moment!**"

            await client.send_message(message.channel, text)

        elif message.content.startswith("!result"):

            """
            Command to show the result of a battle
            opened to bets, and close the bets
            """
            #TODO Add vegas interaction

            try:
                n = message.content.split()[1]

                text = ""
                for num, r in results.items():
                    if r.get("author") == str(message.author) :
                        if num == n:
                            text = "**Here are the results of the battle n."+str(n)+":** \n"+r.get("result")
                            del results[num]
                            break
                        else:
                            text = "**No battle with bet for number "+str(n)+"**"

                    else:
                        text = "**No battle with bet created by you!**"

                await client.send_message(message.channel, text)

            except IndexError : #formatting error
                await client.send_message(message.channel, "**Bad formatting! Run !help for info about commands**")

        elif message.content.startswith("!players"):

            """
            This command allows to see all the players
            partecipating in this season and their submission
            status. (submitted/not)
            """

            pass

        elif message.content.startswith("!brackets"): #get current brackets

            """
            Sends the current brackets for the season
            """

            if settings.onTour:
                try:
                    await client.send_file(message.channel, settings.brackets)

                except:
                    await client.send_message(message.channel, "**Brackets are not up yet!**")

            else : #if no tournament is running
                await client.send_message(message.channel, "**No tournament currently ongoing!**")

        elif message.content.startswith("!languages"): #send all supported languages

            """
            This command outputs all the languages that are
            currently supported. To check in specific a language :
                !languages python
            This will output the command used to compile the player's code,
            the command used to install the external libraries and
            the command used to run a test game
            """

            m = message.content.split()
            if len(m) == 1:
                t = "**Here are the languages supported for your bot:**\n\n"
                for l in sorted(funcs.languages.keys()):
                    t += l+", "
                t += "\n\nIf your language is **not supported** compile it in a `MyBot` file, or dm Splinter if you have problems"

            else:
                t = ""
                for k,v in funcs.languages.items():
                    if m[1] == k:
                        if v[1] == "" :
                            v[1] = "Not necessary"

                        t += "**File extension : **`"+v[0]+"`, **Compile command : **`"+v[1]+"`, **Run command : **`"+v[2]+"`"

                        if m[1] == "python":
                            t+= "\n\n**External libraries installation command : **`pip3 install -r requirements.txt`"

                        elif m[1] == "go":
                            t += "\n\n**External libraries have to be included in your zip file properly**"

                        elif m[1] == "javascript":
                            t+= "\n\n**External libraries installation command : **`npm install`, which requires a **package.json** file!"

                        break

                if t == "":
                    t = "**Language not supported!**"

            await client.send_message(message.channel, t)

        elif message.content.startswith("!donations"):

            """
            This command prints information on how to
            donate to this project
            """

            text = "Donations are used to help support Halite Tournaments. We use your contributions to run our servers and give cash prizes. Donate here: https://www.paypal.me/HaliteTournaments. Donating will give you the **Contributor** role which has access to the Contributors voice channel. More privileges for Contributors will be coming!"
            await client.send_message(message.channel, text)

        elif message.content.startswith("!specs"):

            """
            This command prints the specs for the current
            season like : constants, map sizes and environment
            changes.
            """

            try :
                with open(settings.specs, "r") as s:
                    text = s.read()

            except FileNotFoundError:
                text = "**Specs for season-"+settings.season+" are still not out**"

            await client.send_message(message.channel, text)

        elif message.content.startswith("!engine"):

            """
            This will give the players access to the code
            of the Halite environment used in the ongoing
            tournament. It will also give away a percompiled
            version of it.
            """
            #TODO Add precompiled options

            if settings.engineLink != "" and settings.onTour:
                await client.send_message(message.channel, "**Here is the link containing the info for the engine : "+settings.engineLink+"**")
            else:
                await client.send_message(message.channel, "**Link still not avaible!**")

        #admin commands
        elif str(message.author) in settings.admins:

            """
            This commands are only avaible for the members
            in the `admins` group
            """

            if message.content.startswith("!type"): #make bot type in current channel

                """
                This will send a message from HTBot
                """

                await client.delete_message(message)
                await client.send_message(message.channel, str(message.content).replace("!type", ""))

            elif message.content.startswith("!match"):

                """
                This command starts an official tournament match,
                if Vegas interaction is enabled it will also create
                a bet between the two players.
                This command will output the outcome of the games and
                a zip file containing all replays of the games run in the match
                """

                if settings.onTour :
                    try:
                        #get the two players from mentions
                        p1 = str(message.mentions[0])
                        p2 = str(message.mentions[1])

                        await client.send_message(message.channel, "*Running match...*")
                        if haliteVegas != None:
                            await client.send_message(haliteVegas, "!create "+message.mentions[0].mention+" "+message.mentions[1].mention)
                        status, result, _, _, replay = await funcs.battle(p1, p2, "", "", True)
                        await client.send_message(message.channel, status)

                        if result != "": #if we have an output
                            await client.send_message(message.channel, result)
                            if replay != "":
                                await client.send_file(message.channel, replay)

                    except IndexError : #formatting error
                        await client.send_message(message.channel, "**Bad formatting! Run !help for info about commands**")

                else :
                    await client.send_message(message.channel, "**Feature not avaible at the moment!**")

            elif message.content.startswith("!admin"): #print admin commands

                """
                A help command for admins
                """

                text = "```\n"
                for k,c in sorted(adminCommands.items()):
                    text += k + " : " + c + "\n"
                text += "```"
                await client.send_message(message.channel, text)

            elif message.content.startswith("!clear"): #delete n messages in a channel

                """
                This command allows to delete x messages in a y channel
                E.g :
                    !clear 20 battles
                Will delete 20 messages in the battles channel
                """

                try :
                    n = int(message.content.split()[1]) #number of messages
                    ch = message.content.split()[2] #channel
                    if ch != "*": #current channel
                        channel = discord.utils.get(client.get_all_channels(), server__name=settings.serverName, name=ch)
                    else :
                        channel = message.channel
                    await client.purge_from(channel, limit=n)

                except IndexError:
                    await client.send_message(discord.utils.get(client.get_all_channels(), server__name=settings.serverName, name='halite'), "**Wrong command formatting**")

            elif message.content.startswith("!post"): #upload a file from server to channel

                """
                This will upload a file from the server to the channel
                wanted.
                """

                try :
                    await client.delete_message(message)
                    c = message.content.replace("!post", "")
                    f, ch = c.split()[0], c.split()[1]
                    if ch != "*":
                        channel = discord.utils.get(client.get_all_channels(), server__name=settings.serverName, name=ch)
                    else :
                        channel = message.channel
                    await client.send_file(channel, f, content=c.replace(f+" "+ch, ""))

                except FileNotFoundError:
                    s = funcs.log("File "+f+" not found!")
                    await client.send_message(discord.utils.get(client.get_all_channels(), server__name=settings.serverName, name='halite'), s)

                except IndexError :
                    await client.send_message(discord.utils.get(client.get_all_channels(), server__name=settings.serverName, name='halite'), "**Wrong command formatting**")

            elif message.content.startswith("!subs"): #change submissions status

                """
                This command will change the submissions status
                E.g. :
                    !subs False
                Will close the submissions
                """

                s = message.content.replace("!subs", "").split()
                if s != "":
                    try:
                        boo = funcs.str_to_bool(s[0])
                        settings.db.settings.update_one({}, {"$set":{"submit":boo}})

                        settings.submit = boo
                        await client.send_message(message.channel, "**Setting : "+s[0]+" in submissions**")

                    except IndexError :
                        await client.send_message(message.channel, "!submissions")

                else :
                    await client.send_message(message.channel, "!submissions")

            elif message.content.startswith("!ontour"): #chane onTour status

                """
                This command will change the onTour status,
                same as !subs
                """

                s = message.content.replace("!ontour", "").split()
                if s != "":
                    boo = funcs.str_to_bool(s[0])

                    settings.db.settings.update_one({}, {"$set":{"onTour":boo}})
                    settings.onTour = boo
                    await client.send_message(message.channel, "**Setting : "+s[0]+" in onTour**")

                else :
                    await client.send_message(message.channel, "**Invalid command**")

            elif message.content.startswith("!brk"): #upload new file to brackets

                """
                This command will update the brackets, like !submit
                this command has to be run as a comment on the file
                """

                try :
                    os.system('wget -q -O '+settings.brackets+' ' + message.attachments[0].get('url'))
                    await client.send_message(message.channel, "**Brackets updated**")
                except:
                    await client.send_message(message.channel, "**Error while uploading the brackets**")

            elif message.content.startswith("!time"):

                """
                This command will change the submissions time
                """

                t = message.content.replace("!time", "")
                if t != "":
                    settings.db.settings.update_one({}, {"$set":{"timeSub":t}})
                    settings.timeSub = t
                    await client.send_message(message.channel, "**Setting : "+t+" in timeSub**")

                else:
                    await client.send_message(message.channel, "**Invalid command**")

    except Exception as e:
        s = funcs.log(str(e))
        await client.send_message(discord.utils.get(client.get_all_channels(), server__name=settings.serverName, name='halite'), s)

@client.event
async def on_member_join(member):
    channel = discord.utils.get(client.get_all_channels(), server__name=settings.serverName, name='announcements')
    role = discord.utils.get(member.server.roles, name="Member")
    await client.add_roles(member, role)
    funcs.log("Member joined : "+str(member))
    await client.send_message(discord.utils.get(client.get_all_channels(), server__name=settings.serverName, name='general'),
        "Welcome "+member.mention+" to Halite Tournaments! Check out the section "+channel.mention+" for information about the upcoming tournaments! <:logo:416779058924355596>")


if __name__ == '__main__':
    try :
        #Custom settings if you want to run handler on different user
        handler = subprocess.Popen("python3 "+settings.path+"/handler.py", shell=True)
        client.run(settings.token)

    except KeyboardInterrupt:
        print("\nExiting...")
        handler.terminate()
        os._exit(1)

    except discord.errors.LoginFailure:
        if settings.token is None or settings.token == "":
            print("\nYou need to register a token in the database!")
        else:
            print("\nToken insered is not valid!")
        handler.terminate()
        os._exit(1)
