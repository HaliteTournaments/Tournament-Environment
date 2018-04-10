# Halite Tournaments        

![logo](https://s14.postimg.org/fy1jl5imp/HTLogo.png)

Halite Tournaments is a project created by @FrankWhoee and @Splinter0
to allow fans of the @twosigma's AI challenge Halite-II to participate
in exciting tournaments!

This is the code that we run on our server to interact with our discord
community, which is where we organize and run all our tournaments.

Join our discord server : https://discord.gg/Q2nDHnn

## Dependencies

- python3
- python3-pip
- mongodb-org
- python3-discord (install through pip3)
- python3-pymongo (install through pip3)

Run `install.sh` to automatically install the dependencies.

## Files

- `ht.sh` - Bash file to start the environment
- `install.sh` - Bash file to install dependencies
- `imgs/` - Folder where we store images
- `season-2/` - Folder with all season-2 related stuff
- `bots/` - Folder where bot submissions are stored in
- `env/` - Folder with the game environment
- `mongo/` - Folder to store database
- `db/` - Containing templates for db setup

## Security

Since we are compiling and executing untrusted code we setted up
security measures to protect our server.
Some of them are mandatory to setup, so if you wanna run this
code on your own server you will have to follow them, others are
optional.

#### Database
As database to store the data about our players, settings and matches
we use MongoDB. The user are setted up to be one `root` which has
complete access to the `halite-tournaments` database, and the other
one called `arena`, which is the user that only has access to matches
and players. You should check the folder `db/` for more info about
the roles and the users.

#### Running the program
The discord bot is run by a user which has to provide his password to
become sudo ( very recommended ). The other user is the user `arena`
which is the one that compiles the code for the bots and runs the
matches.

#### Users
The user `arena` **does not** have internet access, to limit
all the possible damage that could be done if malicious code
is contained in the code for the bots. `arena` also has restricted
access to the project folder ( it is recommended ), you can set the
permissions up as you wish.
The user running the discord bot is allowed internet access of course
and is in charge of installing dependencies for the bots as well.
He has access to all project folders.

## Future

- A webapp to interact with the game environment
- Fairly big cash prizes
- Include Halite-I tournaments for the vintage fans :laughing:

## TODO

- Add more languages support

## Contribute!

Please help us improve this code! We would love to hear your opinion!

Join our discord server and help our community grow !

https://discord.gg/Q2nDHnn

Donate to help us increase the cash prizes, get a more powerful instance, and support new features!

https://www.paypal.me/HaliteTournaments
