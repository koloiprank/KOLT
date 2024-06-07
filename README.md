# KOLT
Base discord App(Bot) KOLT

### COMPLETED FEATURES
1. Administrator / Moderator zone:
 - Welcomer
  * Set welcome message type, channel and message/image/message and image
  * Capability to test the welcome message
 - Autorole
  * Roles on-join
  * Roles on-react
 - Automod and Moderation
  * Configurable Warn / Mute / Kick / Ban system with custom maximums
  * Configurable banned words with cabailities to detect automod avoidance (i.e: Banned word Banana, B/ä-*nán==A is detected as Banana)
  * Automatic warning / muting / kicking / banning system on banned word usage
  * Capabilities to clear one / all punishments from a user
  * Capabilities to clear all users from punishments
  * Chat logging on console and command logging on file discord.log
 - Capabilities to reset all configurations (Welcomer, automod, autorole)
2. Regular user zone:
 - Music playing
  * For all users:
    * Connect / disconnect command (Needed to play music)
    * move command to move the bot from one channel to another
    * Play to play/queue a song
    * Playlist command to show the current playlist (User doesn't need to be connected to use)
  * For administrators / DJ role:
   * Toggleable playlist Repeat / Shuffle
   * Pause command to pause the music
   * stop command to stop the music
   * rmsong to remove a specific song
   * forcedisconnect to force the bot to disconnect and clear the playlist configuration


 
### TODO 
- Work on README.md
- Prepare /help command
- Work on setting the play command into a new thread so bot doesnt get stuck while loading song

## Requirements
For your python modules, you will need to install all the requirements in requirements.txt with  
``` pip install -r requirements.txt ```  

For the play command to work, you will need to install into the host machine FFmpeg.  

If you are running linux use ``` sudo apt-get install ffmpeg ``` or any installation method variant (depending on your distribution).  
If you are running windows, [enter this link](https://ffmpeg.org/download.html) and download the latest version.