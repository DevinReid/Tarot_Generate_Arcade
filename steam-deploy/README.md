# Load build to Steam
1. Open build.vdf and edit the version numbers to match the dist files
2. Navigate to your C:\SteamPipe\ directory, Also must be in Command Prompt
3. Check that there are only the two most recent builds and the run.sh file
4. Login to the Steam Console Command using `steamcmd.exe +login <username>`
5. Run the build script: `run_app_build "C:\Users\Dreid\Desktop\Brain\Projects\Tarot_Generate_Arcade\steam-deploy\build.vdf"`
6. Visit (https://partner.steamgames.com/apps/builds/3582900) and change the build to 'default' branch, preview, and set build live
7. Visit (https://partner.steamgames.com/apps/config/3582900) and ensure the file/version matches the .exe build