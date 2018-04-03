import os
import threading
import time
import subprocess
import random
import zipfile
import datetime

path = os.path.dirname(os.path.realpath(__file__))
compileQueue = path+"/compilerQueue.txt"
runQueue = path+"/runQueue.txt"
runFile = path+"/run.txt"
logFile = path+"/handler.log"

def log(string):

    """
    Log function
    """
    
    string = "Timestamp: - {:%Y-%m-%d %H:%M:%S}".format(datetime.datetime.now())+" "+ string
    with open(logFile, 'a') as (out):
        out.write(string + '\n')
    return '**' + string + '**'

def firewallUp():

    """
    Function to turn the firewall up
    """

    command = "sudo ufw default deny outgoing && \
              sudo ufw allow ssh && \
              sudo ufw disable && sudo ufw enable"

    firewall = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    firewall.communicate("y".encode())

def firewallDown():

    """
    Function to turn the firewall down
    """

    command = "sudo ufw default allow outgoing && \
              sudo ufw disable && sudo ufw enable"

    firewall = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    firewall.communicate("y".encode())

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

    with open(runFile, "r") as r:
        return int(r.read())

class BobTheBuilder(threading.Thread): #reference alert

    """
    Thread class that builds the submission of a player.

    self.bot = Name of the player that owns the bot (string)
    self.log = The output that will be written in logfile (string)
    self.comp = Command to compile the bot (string)
    self.fire = Command to run the bot (string)
    """

    def __init__(self, bot):
        threading.Thread.__init__(self)
        self._stop_event = threading.Event()

        self.bot = bot
        self.log = ""

    def run(self):
        os.system("rm "+self.bot+"/*.log "+self.bot+"/*.hlt > /dev/null 2>&1")

        with open(path+"/"+self.bot+"/lang.txt", "r") as l:
            infos = l.read().splitlines(True)
            self.comp = infos[0].replace("\n", "")
            self.fire = infos[1].replace("\n", "")

        if self.comp != "":
            self.log += "*****COMPILER LOG*****\n"
            try:
                output = subprocess.check_output("cd "+path+"/"+self.bot+" && "+self.comp, timeout=60, shell=True).decode()
                self.log += output+"\n\n"

            except subprocess.TimeoutExpired:
                self.log += "Timeout Error!\n"

            except subprocess.CalledProcessError as e:
                self.log += str(e)

        if self.fire.startswith("python3") and os.path.exists(path+"/"+self.bot+"/requirements.txt"):
            firewallDown()
            self.log += "****PIP LOG****\n"
            try :
                output = subprocess.check_output("cd "+path+"/"+self.bot+" && sudo pip3 install -r requirements.txt", timeout=60, shell=True).decode()
                self.log += output+"\n\n"

            except subprocess.TimeoutExpired:
                self.log += "Timeout Error!\n"

            except subprocess.CalledProcessError as e:
                self.log += str(e)

            firewallUp()

        self.fire = "cd "+path+"/"+self.bot+" && "+self.fire
        command = "./halite -d \"240 160\" \""+self.fire+"\" \""+self.fire+"\" -t -i "+path+"/out/"
        self.log += "*****HALITE LOG*****\n"

        try:
            output = subprocess.check_output(command, timeout=120, shell=True).decode()
            self.log += output

            if output.splitlines(True)[-3].startswith("Opening"):
                replay = output.splitlines(True)[-3].split()[4]
                status = "\n"+"successful"
                os.system("rm "+replay+" > /dev/null 2>&1")
            else:
                status = "\n"+"failed"

        except subprocess.TimeoutExpired:
            self.log += "Timeout Error!\n"
            status = "\n"+"failed"

        except subprocess.CalledProcessError as e:
            self.log += str(e)
            status = "\n"+"failed"

        with open(path+"/out/"+self.bot+".txt", "w") as l :
            l.write(self.log+status)

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

    def __init__(self, p1, p2, official, sizes):
        threading.Thread.__init__(self)
        self._stop_event = threading.Event()
        self.p1 = p1
        self.p2 = p2
        self.official = official
        if self.official:
            self.maps = []
        self.sizes = sizes
        self.log = ""
        self.battles = 5
        self.results = []

    def start(self):
        os.system("rm "+self.p1+"/*.log "+self.p2+"/*.log > /dev/null 2>&1")
        runCmds = []
        with open(path+"/"+self.p1+"/lang.txt", "r") as f:
            runCmds.append(f.read().splitlines(True)[1])

        with open(path+"/"+self.p2+"/lang.txt", "r") as f:
            runCmds.append(f.read().splitlines(True)[1])

        try:
            os.mkdir(path+"/out/"+self.name)
        except:
            pass

        if self.official:
            zipped = zipfile.ZipFile(path+"/out/"+self.name+"/"+"match.zip", mode="w")
            for b in range(self.battles):
                self.sizes = randmizeMap(self.maps)
                self.maps.append(self.sizes)
                self.command = ["./halite", "-d", self.sizes[0]+" "+self.sizes[1],\
                                "cd "+path+"/"+self.p1+"/ && "+runCmds[0], \
                                "cd "+path+"/"+self.p2+"/ && "+runCmds[1], "-t", "-i", \
                                path+"/out/"+self.name+"/", "-s", randomizeSeed()]

                try:
                    output = subprocess.check_output(self.command, timeout=120).decode()

                    if output.splitlines(True)[-3].startswith("Opening"):
                        replay = output.splitlines(True)[-3].split()[4]
                        os.rename(replay, path+"/out/"+self.name+"/"+str(b+1)+".hlt")
                        self.results.append([self.p1+" came in rank "+output.splitlines(True)[-2].split()[6], self.p2+" came in rank "+output.splitlines(True)[-1].split()[6]])
                        zipped.write(path+"/out/"+self.name+"/"+str(b+1)+".hlt", arcname=str(b+1)+".hlt")
                    else :
                        self.log += "ERROR RUNNING BATTLE:\n\n"+output

                except subprocess.TimeoutExpired:
                    self.log += "Timeout Error\n"

                except Exception as e:
                    self.log += str(e)+"\n"

            zipped.close()

        else:
            self.command = ["./halite", "-d", self.sizes[0]+" "+self.sizes[1],\
                            "cd "+path+"/"+self.p1+"/ && "+runCmds[0], \
                            "cd "+path+"/"+self.p2+"/ && "+runCmds[1], "-t", "-i", \
                            path+"/out/"+self.name+"/"]

            try:
                output = subprocess.check_output(self.command, timeout=120).decode()

                if output.splitlines(True)[-3].startswith("Opening"):
                    replay = output.splitlines(True)[-3].split()[4]
                    os.rename(replay, path+"/out/"+self.name+"/battle.hlt")
                    self.results.append([self.p1+" came in rank "+output.splitlines(True)[-2].split()[6], self.p2+" came in rank "+output.splitlines(True)[-1].split()[6]])
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

        with open(path+"/out/"+self.name+"/battle.log", "w") as l:
            l.write(self.log)


        self.stop()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

class Handler(threading.Thread):

    """
    This class is what runs everything.
    In short it reads the two queue files
    where all the instructions are written.
    For every instruction in the runQueue it
    creates a "Arena" thread and for every
    instruction in compileQueue it creates
    a "BobTheBuilder" thread.

    self.queue = List of all the threads loaded
    self.max = Number of max threads running at the same time
    self.compilers = Number of BobTheBuilder threads running
    self.runners = Number of Arena threads running
    self.runners = self.runners + self.compilers OR len(self.queue)
    """

    def __init__(self):
        threading.Thread.__init__(self)
        self._stop_event = threading.Event()
        self.queue = []
        self.max = 4
        self.compilers = 0
        self.runners = 0
        self.running = 0

    def start(self):
        while self.running == 0: #if our queue is empty
            try:
                with open(compileQueue, "r") as q:
                    compLines = q.read().splitlines(True)
                    if len(compLines) > self.max :
                        self.compilers = self.max
                    elif len(compLines) == 1: #if only one line
                        if len(compLines[0]) > 2: #check if it's only a space
                            self.compilers = 1
                    else : #if threads needed are between 2-4
                        self.compilers = len(compLines)

                with open(compileQueue, "w") as q:
                    data = ""
                    #create the threads and remove threads from queue file
                    for l in range(self.compilers):
                        bot = compLines[0].replace("\n", "")
                        compLines = compLines[1:]
                        thread = BobTheBuilder(bot)
                        thread.setName(bot)
                        self.queue.append(thread) #add thread to queue

                    for l in compLines:
                        data += l+"\n"
                    q.write(data)

                if self.compilers < self.max:
                    with open(runQueue, "r") as q:
                        runLines = q.read().splitlines(True)
                        if len(runLines) > self.max-self.compilers :
                            self.runners = self.max-self.compilers
                        elif len(runLines) == 1:
                            if len(runLines[0]) > 5:
                                self.runners += 1
                        else :
                            self.runners = len(runLines)

                    with open(runQueue, "w") as q:
                        data = ""
                        for l in range(self.runners):
                            r = runLines[0].replace("\n", "").split()
                            official = False
                            sizes = ["", ""]
                            if r[0] == "official": #if it's match and not just a battle
                                official = True
                                p1, p2 = r[1], r[2]
                            else:
                                p1, p2 = r[0], r[1]
                                sizes[0], sizes[1] = r[2], r[3] #width and height
                            runLines = runLines[1:]
                            thread = Arena(p1, p2, official, sizes)
                            thread.setName(p1+"VS"+p2)
                            self.queue.append(thread) #add thread to queue

                        for l in runLines:
                            data += l+"\n"
                        q.write(data)

                self.running = self.compilers+self.runners
                #print(self.queue)
                if self.running == 0:
                    time.sleep(1)
                    continue

                for thread in self.queue : #start all the threads
                    log("Running : "+thread.name)
                    thread.start()

                time.sleep(0.2)

                while self.running != 0:
                    for thread in self.queue :
                        if thread.stopped(): #check if thread stopped
                            self.queue.remove(thread) #remove it from the queue
                            self.running -= 1

                    time.sleep(1)

                time.sleep(2)

            except Exception as e:
                log(str(e))



    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

if __name__ == '__main__':
    try:
        if forrest(): #if we are running
            print("Starting up...")
            hands = [Handler(), Handler()]
            hands[0].setName("right-hand")
            hands[1].setName("left-hand")
            while True:
                try:
                    hands[0].start()
                    #if we get more power run a second hand too
                    #while True:
                    #    if len(hands[0].queue) == hands[0].max:
                    #        hands[1].start()

                    #    time.sleep(2)

                    #    if len(hands[1].queue) == 0 and hands[1].isAlive():
                    #        hands[1].join(timeout=1)

                except KeyboardInterrupt:
                    break

                except Exception as e:
                    print(str(e))
                    continue

            raise KeyboardInterrupt

        else :
            print("We are not running... sad.")
    except KeyboardInterrupt:
        print("Closing...")
