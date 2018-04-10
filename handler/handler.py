import os
import threading
import time
import subprocess
import random
import zipfile
import datetime
import urllib.parse
from pymongo import MongoClient

username = urllib.parse.quote_plus('arena')
password = urllib.parse.quote_plus('')
mongo = MongoClient('mongodb://%s:%s@localhost:27017/halite-tournaments' % (username, password))

db = mongo["halite-tournaments"]
s = db.arena.find_one({})

path = os.path.dirname(os.path.realpath(__file__))
compileQueue = path+"/queues/compilerQueue.txt"
runQueue = path+"/queues/runQueue.txt"
mainQueue = path+"/queues/queue.txt"
#runFile = path+"/run.txt"

def log(string):

    """
    Log function
    """

    string = "Timestamp: - {:%Y-%m-%d %H:%M:%S}".format(datetime.datetime.now())+" "+ string
    with open(path+s.get('log'), 'a') as (out):
        out.write(string + '\n')
    return '**' + string + '**'

def randmizeMap(m):

    """
    Randomize the maps for battle
    """

    default = ["240", "160"]
    maps = {
        "small":[
            ["216", "144"], #-10% from default
            ["204", "136"], #-15% from default
            ["192", "128"]], #-20% from default

        "big":[
            ["264", "176"], #+10% from default
            ["276", "192"], #+15% from default
            ["288", "192"]]  #+20% from default
        }
    if len(m) == 0 or len(m) == 2:
        return maps["small"][random.randint(0, 2)]
    elif len(m) == 1 or len(m) == 3:
        return maps["big"][random.randint(0, 2)]
    else:
        return default

def randomizeSeed():

    """
    Randomize the seed for battle
    """

    return str(random.randint(2350513674, 2350513694))

def forrest(): #reference alert

    """
    Check runFile to see if we should run Handler
    """

    return s.get('running')

class BobTheBuilder(threading.Thread): #reference alert

    """
    Thread class that builds the submission of a player.

    self.bot = Name of the player that owns the bot (string)
    self.log = The output that will be written in logfile (string)
    self.comp = Command to compile the bot (string)
    self.fire = Command to run the bot (string)
    """

    def __init__(self, q):
        threading.Thread.__init__(self)
        self._stop_event = threading.Event()
        self.q = q
        self.player = self.q.get('players')
        self.path = self.player.get('path')
        self.log = ""

    def run(self):
        os.system("rm "+self.path+"*.log "+self.path+"*.hlt > /dev/null 2>&1")

        self.comp = self.player.get('commands')[0]
        self.fire = self.player.get('commands')[1]

        if self.comp != "":
            self.log += "*****COMPILER LOG*****\n"
            try:
                output = subprocess.check_output("cd "+self.path+" && "+self.comp, timeout=60, shell=True).decode()
                self.log += output+"\n\n"

            except subprocess.TimeoutExpired:
                self.log += "Timeout Error!\n"

            except subprocess.CalledProcessError as e:
                self.log += str(e)

        self.fire = "cd "+self.path+" && "+self.fire
        command = "/."+path+s.get('halite')+" -d \"240 160\" \""+self.fire+"\" \""+self.fire+"\" -t -i "+path+s.get('out')
        self.log += "*****HALITE LOG*****\n"

        try:
            output = subprocess.check_output(command, timeout=120, shell=True).decode()
            self.log += output

            if output.splitlines(True)[-3].startswith("Opening"):
                replay = output.splitlines(True)[-3].split()[4]
                success = True
                os.system("rm "+replay+" > /dev/null 2>&1")
            else:
                status = "failed"

        except subprocess.TimeoutExpired:
            self.log += "Timeout Error!\n"
            success = False

        except subprocess.CalledProcessError as e:
            self.log += str(e)
            success = False

        with open(path+s.get('out')+self.name+".txt", "w") as l :
            l.write(self.log)

        db.queues.update_one({"_id":self.q.get("_id")}, {"$set": {"status":"finished", "success":success, "logfile":path+s.get('out')+self.name+".txt"}}, upsert=True)

        self.stop()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

class Arena(threading.Thread):

    """
    Thread class that runs battles and matches.

    self.p1 = Player one (string)
    self.p2 = Player two (string)
    self.official = If it's a match or just a battle (bool)
    self.maps = All maps that we ran in, only if we are running a match (list of lists of string)
    self.sizes = Width and height of current map (list of strings)
    self.log = The output that will be written in logfile (string)
    self.battles = The battles we are running in a match
    self.results = All results of battles (list of lists of strings)
    """

    def __init__(self, q):
        threading.Thread.__init__(self)
        self._stop_event = threading.Event()
        self.q = q
        self.p1 = self.q.get("players")[0]
        self.p2 = self.q.get("players")[1]
        self.name = self.p1.get('username')+"VS"+self.p2.get('username')
        self.official = False
        if self.q.get("type") == "match":
            self.official = True
            self.maps = []
        else:
            self.sizes = q.get("map")
        self.log = ""
        self.battles = 5
        self.results = []
        self.out = path+s.get('out')+self.name
        self.logFile = ""

    def start(self):
        os.system("rm "+self.p1.get("path")+"*.log "+self.p2.get("path")+"*.log > /dev/null 2>&1")

        success = False

        if self.official:
            try:
                os.mkdir(self.out)
            except:
                pass
            self.logFile = self.out+"/battle.log"
            zipped = zipfile.ZipFile(self.out+"/match.zip", mode="w")
            for b in range(self.battles):
                self.sizes = randmizeMap(self.maps)
                self.maps.append(self.sizes)
                self.command = ["/."+path+s.get('halite'), "-d", self.sizes[0]+" "+self.sizes[1],\
                                "cd "+self.p1.get("path")+" && "+self.p1.get("commands")[1], \
                                "cd "+self.p2.get("path")+" && "+self.p2.get("commands")[1], \
                                "-t", "-i", self.out+"/", "-s", randomizeSeed()]

                try:
                    output = subprocess.check_output(self.command, timeout=120).decode()
                    if output.splitlines(True)[-3].startswith("Opening"):
                        replay = output.splitlines(True)[-3].split()[4]
                        os.rename(replay, self.out+"/"+str(b+1)+".hlt")
                        self.results.append([self.p1.get("username")+" came in rank "+output.splitlines(True)[-2].split()[6], self.p2.get("username")+" came in rank "+output.splitlines(True)[-1].split()[6]])
                        zipped.write(self.out+"/"+str(b+1)+".hlt", arcname=str(b+1)+".hlt")
                        success = True
                    else :
                        self.log += "ERROR RUNNING BATTLE:\n\n"+output

                except subprocess.TimeoutExpired:
                    self.log += "Timeout Error\n"

                except Exception as e:
                    self.log += str(e)+"\n"

            zipped.close()

        else:
            self.logFile = self.out+".log"
            self.command = ["/."+path+s.get('halite'), "-d", self.sizes[0]+" "+self.sizes[1],\
                            "cd "+self.p1.get("path")+" && "+self.p1.get("commands")[1], \
                            "cd "+self.p2.get("path")+" && "+self.p2.get("commands")[1], \
                            "-t", "-i", path+s.get('out')]

            try:
                output = subprocess.check_output(self.command, timeout=120).decode()

                if output.splitlines(True)[-3].startswith("Opening"):
                    replay = output.splitlines(True)[-3].split()[4]
                    os.rename(replay, self.out+".hlt")
                    self.results.append([self.p1.get("username")+" came in rank "+output.splitlines(True)[-2].split()[6], self.p2.get("username")+" came in rank "+output.splitlines(True)[-1].split()[6]])
                    success = True
                else :
                    self.log += "ERROR RUNNING BATTLE:\n\n"+output

            except subprocess.TimeoutExpired:
                self.log += "Timeout Error\n"

            except Exception as e:
                self.log += str(e)+"\n"

        num = 1
        for r in self.results:
            if len(r) == 2:
                self.log += "Round number : "+str(num)+"\n"+r[0]+"\n"+r[1]+"\n\n"
            else:
                break
            num += 1

        with open(self.logFile, "w") as l:
            l.write(self.log)

        db.queues.update_one({"_id":self.q.get("_id")}, {"$set": {"status":"finished", "success":success, "logfile":self.logFile}})

        self.stop()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()


class Handler(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self._stop_event = threading.Event()
        self.max = s.get('max')
        self.queue = []

    def start(self):
        while forrest():
            self.space = self.max
            for q in db.queues.find({"type":"compile"}):
                if self.space == 0:
                    break
                if q.get('status') == "not-running":
                    thread = BobTheBuilder(q)
                    thread.setName(q.get('players').get('username'))
                    self.queue.append(thread)
                    self.space -= 1
                    db.queues.update_one({"_id":q.get('_id')}, {"$set":{"status":"running"}}, upsert=True)
                    thread.start()
                else:
                    continue

            if self.space > 0:
                for q in db.queues.find({"type":"match"}):
                    if self.space == 0:
                        break
                    if q.get('status') == "not-running":
                        thread = Arena(q)
                        thread.setName(q.get('players')[0].get('username')+"VS"+q.get('players')[1].get('username'))
                        self.queue.append(thread)
                        self.space -= 1
                        db.queues.update_one({"_id":q.get('_id')}, {"$set":{"status":"running"}}, upsert=True)
                        thread.start()
                    else:
                        continue

            if self.space > 0:
                for q in db.queues.find({"type":"battle"}):
                    if self.space == 0:
                        break
                    if q.get('status') == "not-running":
                        thread = Arena(q)
                        thread.setName(q.get('players')[0].get('username')+"VS"+q.get('players')[1].get('username'))
                        self.queue.append(thread)
                        self.space -= 1
                        db.queues.update_one({"_id":q.get('_id')}, {"$set":{"status":"running"}}, upsert=True)
                        thread.start()
                    else:
                        continue

            while len(self.queue) > 0:
                for thread in self.queue :
                    if thread.stopped():
                        self.queue.remove(thread)

            time.sleep(1)


    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

if __name__ == '__main__':
    try:
        if forrest(): #if we are running
            h = Handler()
            h.setName("hand")
            h.start()
        else :
            print("Handler is not running... sad.")

    except KeyboardInterrupt:
        pass
