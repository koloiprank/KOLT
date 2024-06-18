# KOLT
Base discord App(Bot) KOLT

### COMPLETED FEATURES
<ul>
    <li>0. Fixes/Important changes</li>
        <ul>
            <li>Changed from function command tree to cog command tree functionality</li>
            <li>Revamped music functionality to work as intended</li>
        </ul>
    <li>1. Administrator / Moderator zone:</li>
        <ul>
            <li>Welcomer</li>
                <ul>
                    <li>Set welcome message type, channel and message/image/message and image</li>
                    <li>Capability to test the welcome message</li>
                </ul>
            <li>Autorole</li>
                <ul>
                    <li>Roles on-join</li>
                    <li>Roles on-react</li>
                </ul>
            <li>Automod and Moderation</li>
                <ul>
                    <li>Configurable Warn / Mute / Kick / Ban system with custom maximums</li>
                    <li>Configurable banned words with cabailities to detect automod avoidance (i.e: Banned word Banana, B/ä-*nán==A is detected as Banana)</li>
                    <li>Automatic warning / muting / kicking / banning system on banned word usage</li>
                    <li>Capabilities to clear one / all punishments from a user</li>
                    <li>Capabilities to clear all users from punishments</li>
                    <li>Chat logging on console and command logging on file discord.log</li>
                </ul>
            <li>Capabilities to reset all configurations (Welcomer, automod, autorole)</li>
        </ul>
    <li>2. Regular user zone</li>
        <ul>
            <li>Music playing</li>
                <ul>
                    <li>NOTE: YT and SPOTIFY single track / playlist support</li>
                    <li>For all users:</li>
                        <ul>
                            <li>Connect / disconnect command</li>
                            <li>move command to move the bot from one channel to another</li>
                            <li>Play to play/queue a song, connects the bot if it is not connected</li>
                            <li>Playlist command to show the current playlist (User doesn't need to be connected to use)</li>
                            <li>Automatic disconnect after an inactivity period</li>
                        </ul>
                    <li>For administrators / DJ role:</li>
                        <ul>
                            <li>Toggleable playlist Repeat / Shuffle</li>
                            <li>Pause command to pause the music</li>
                            <li>stop command to stop the music</li>
                            <li>rmsong to remove a specific song, replace the song name with a * to clear playlist</li>
                            <li>forcedisconnect to force the bot to disconnect and clear the playlist configuration</li>
                        </ul>
                </ul>
        </ul>
</ul>

### TODO 
- Work on README.md
- Prepare /help command

## Requirements
For your python modules, you will need to install all the requirements in requirements.txt with  
``` pip install -r requirements.txt ```  

For the play command to work, you will need to install into the host machine FFmpeg.  

If you are running linux use ``` sudo apt-get install ffmpeg ``` or any installation method variant (depending on your distribution).  
If you are running windows, [enter this link](https://ffmpeg.org/download.html) and download the latest version.