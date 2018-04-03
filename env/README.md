# Vagrant environment

This is the folder where the Vagrant machine operates,
it's a shared folder between the host and the machine.
Make sure that you first run `../install.sh` in the host.
In this folder is where the bots of all the players are stored.

## Setup

All you need to do, assuming you already installed Vagrant
and VirtualBox (check `../install.sh`), is to run these commands :
(in the current directory of course)

`vagrant up` which will bring up the machine following the instructions
in the `Vagrantfile`.

`vagrant ssh` which will establish an ssh connection with the VM

Once you are connected you have to `cd` into the shared folder,
it's very easy, the shared folder is under `/vagrant/`.

When you are in the shared folder you should see the `install.sh`
file, run it and it will install everything that is necessary to run
the environment on the VM side.

To run the game environment simply execute `python3 handler.py`

## Files

`compilerQueue.txt` - File where a queue for compiling bots is created
`runQueue.txt` - File where a queue for running bots is created
`run.txt` - A file with a boolean value to determine if environment is running
`install.sh` - Install all packages needed to run environment
`handler.py` - Contains all the code of the environment
`halite` - Halite binary with our modifications
`Vagrantfile` - File containing Vagrant VM infos
`handler.log` - Log file for environment handler
`out/` - Directory where all outputs from environment is put
`halite-env/` - Directory with all files to build Halite binary
