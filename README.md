# Halite Tournaments        

![logo](https://s14.postimg.org/fy1jl5imp/HTLogo.png)

Halite Tournaments is a project created by @FrankWhoee and @Splinter0
to allow fans of the @twosigma's AI challenge Halite-II to participate
in exciting tournaments!

This is the code that we run on our server to interact with our discord
community, which is where we organize and run all our tournaments.

Join our discord server : https://discord.gg/Q2nDHnn

## Setup

The server used for our tournaments is a Google Cloud instance running Debian 9.
All the packages needed to run this are in `./install.sh`.

## Game environment

For security reasons we compile and run the code submitted by the
participants of the tournaments in a Vagrant machine.

Before setting up your Vagrant environment you need to follow the steps
at : https://cloud.google.com/compute/docs/instances/enable-nested-virtualization-vm-instances
in order to enable virtualization on your instance.

When you have installed all packages needed, head over to `env/README.md`
for the overview of the game environment

Check out `season-2/` for more infos on our current battle system

## Files

`bot.py` - Main of the discord bot
`funcs.py` - Helper functions and functions interacting with game environment
`install.sh` - Bash script to install all packages needed
`settings.json` - JSON file containing all environment variables
`setting.py` - Script that loads the environment variables
`bot.log` - Logfile for discord bot

## Disclaimer

This is v1.0, don't expect the code to be nice and clean  :stuck_out_tongue_winking_eye:
It gets the job done, but we would love external help and we want our
community to grow so feel free to create issues and join our discord
server! :smile:

## Future

- A webapp to interact with the game environment
- Fairly big cash prizes
- Include Halite-I tournaments for the vintage fans :laughing:

## TODO

- Add more languages support

## Contribute!

Join our discord server and help our community grow !

https://discord.gg/Q2nDHnn

Donate to help us increase the cash prizes, get a more powerful instance, and support new features!

https://www.paypal.me/HaliteTournaments
