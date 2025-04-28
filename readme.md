# Overview
Tarot Card Arcade game using python arcade and chatgpt. This directory contains the python game, which compiles to an executable and is available on steam, and a flask server that runs on [render](https://render.com/) and provides the API endpoints.

# Get started instructions 
* As a prerequisite be sure you have python installed with `$ python --version`. The project supports python 3.12.4. You'll also need Postgres installed, you can check the installation of that by using `$ psql --version`.
# Server instructions
1. In a new terminal go to the flask server directory with `$ cd server-engine`
2. Copy the environment files `cp -a .env.example .env` and fill out the applicable variables 
3. Create a virtual environment using `$ python -m venv .venv`
4. Start virtual environment using `$ source .venv/bin/activate`
5. Install the packages using `$ pip install -r requirements.txt`
6. Start the server with by running `$ flask --debug run`
7. See server running on http://localhost:5000/

# Game instructions 
1. In a new terminal, go into the python game directory `$ cd python-game` 
2. Copy the environment files `cp -a .env.example .env` and fill out the applicable variables
3. Create a virtual environment using `$ python -m venv .venv`
4. Start virtual environment using `$ source .venv/bin/activate`
5. Install the packages using `$ pip install -r requirements.txt`
6. Start Tarot game by running `$ python game.py`

# Compile Game 
Follow the below instructions to compile the game: 
1. Ensure you're in the  `python-game` directory 
2. If you're on windows run the command `$pyinstaller --onefile --windowed --clean --noupx --add-data "assets;assets" --icon=icon.ico --name "TarotGame_v1.0.4" game.py`.
If you're on Mac use `$ pyinstaller --onefile  --windowed --clean --noupx --name "TarotGame_v1.0.4" --icon "icon.icns"  --add-data "assets:assets" game.py`
On mac try this, then replace above if it works. `$ pyinstaller --onefile  --windowed --clean --noupx --name "TarotGame_v1.0.4" --icon "icon.icns"  --add-data "assets:assets" game.py`
3. You'll find the resulting executable in the  `/dist/` folder


# Load build to Steam
1. Open build.vdf and edit the version numbers to match the dist files
2. Navigate to your C:\SteamPipe\ directory, Also must be in Command Prompt
3. Check that there are only the two most recent builds and the run.sh file
4. Login to the Steam Console Command using `steamcmd.exe +login <username>`
5. Run the build script: `run_app_build "C:\Users\Dreid\Desktop\Brain\Projects\Tarot_Generate_Arcade\steam-deploy\build.vdf"`
6. Visit (https://partner.steamgames.com/apps/builds/3582900) and change the build to 'default' branch, preview, and set build live
7. Visit (https://partner.steamgames.com/apps/config/3582900) and ensure the file/version matches the .exe build

# Resources
* CardArt base from [chee-seekins](https://chee-seekins.itch.io/tarot) - note, files not in git. commercial use, no distribution 
* Click Sfx from [jarzarr](https://jarzarr.itch.io/ui-button-sounds) - commercial use, distribution
* Music from [alkarab](https://alkakrab.itch.io/free-12-tracks-pixel-rpg-game-music-pack) - commercial use, distribution
* Card SfX from [jdshertbert](https://jdsherbert.itch.io/tabletop-games-sfx-pack) - commercial use, distribution
* Door opening sound from (https://mixkit.co/free-sound-effects/doors/) - commercial use, distribution
* Typerwriter Sfx from (https://mixkit.co/free-sound-effects/click/) - commercial use, Distrubution
* Wind Sfx from https://mixkit.co/free-sound-effects/wind/ - commercial use, distribution

* Original Art made with Aseprite https://www.aseprite.org/
