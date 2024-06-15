import sqlite3
import KTtools
import asyncio

async def reset_all_playlists():
    connexion = sqlite3.connect("configs.db")
    cursor = connexion.cursor()
    
    cursor.execute(""" 
                   SELECT server_id FROM playlist
                   """)
    result = cursor.fetchall()

    serverlist = []
    for server_id in result:
        serverlist.append(server_id[0])

    template = {"playlist": [], "isplaying": False, "repeat": False, "shuffle": False}
    for server_id in serverlist:
        await KTtools.save_playlist(template, server_id)

if __name__ == "__main__":
    asyncio.run(reset_all_playlists())