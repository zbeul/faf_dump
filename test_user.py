import discord
import pymongo
import os
import json
from datetime import datetime, timezone, timedelta

DISCORD_TOKEN_AUTH = os.environ.get("DISCORD_TOKEN_AUTH") # Retrieved from browser local storage
# xxxxxxxxxxxxxxxxxxxxxxx.xxxxxxx.xxxxxxxxxxxxxxxxxxxxxxxxxxx <- mine looked like this

# We assume this client has access to one DB per discord server
# each DB has a collection named "faf_posts"
# Said collection has an attribute "date" written using datetime.datetime
#MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")

discord_client = discord.Client()
#mongo_client = pymongo.MongoClient(MONGO_URI)

@discord_client.event
async def on_connect():
    """
    Performs a retrieval of every message posted 24h ago in every text channel 
    of every guilds the client is connected in.
    """
    now = datetime.utcnow()
    print("Connected on ", ','.join([g.name for g in discord_client.guilds]), "at", now)
    save_dump = { 
        "meta" : { 
            "users" : {},
            "userindex" : [],
            "servers" : [],
            "channels" : {}
        },
        "data": {
        }
    }
    temp = {
        "userlookup": {}
    }
    for guild in discord_client.guilds:
#        db = mongo_client[guild.name]
        save_dump["meta"]["servers"].append({ 
            "name":guild.name, "type":"SERVER" })
#        messages = db.messages
        for text_channel in guild.text_channels:
            save_dump["meta"]["channels"][text_channel.id] = { 
                    "server": len(save_dump["meta"]["servers"]) - 1,
                    "name": text_channel.name }
            save_dump["data"][text_channel.id] = {}
            try :
                after = now - timedelta(days=1)
                hist_messages = [ 0 ]
                while len(hist_messages) > 0 :
                    hist_messages = await text_channel.history(limit=100, after=after).flatten()
                    for message in hist_messages:
                        if message.author.id not in save_dump["meta"]["userindex"]:
                            save_dump["meta"]["userindex"].append(message.author.id)
                            save_dump["meta"]["users"][message.author.id] = { 
                                    "name" : message.author.name}
                            temp["userlookup"][message.author.id] = len(save_dump["meta"]["userindex"]) - 1
                        mess = {
                                "u" : temp["userlookup"][message.author.id],
                                "t" : message.created_at.timestamp(),
                                "m" : message.content
                        }
                        if message.edited_at != None:
                            mess["te"] = message.edited_at.timestamp()

                        for embed in message.embeds:
                            if "e" not in mess:
                                mess["e"] = []
                            e = { "url" : embed.url, "type" : embed.type }
                            if embed.type == "rich":
                                if embed.title is not discord.Embed.Empty:
                                    e["t"] = embed.title
                                if embed.description is not discord.Embed.Empty :
                                    e["d"] = embed.description
    
                            mess["e"].append(e)
    
                        for attachment in message.attachments:
                            if "a" not in mess:
                                mess["a"] = []
                            
                            mess["a"].append({
                                "url" : attachment.url })
 #                   processed_message = { "date" : message.created_at }
 #                   messages.insert_one(processed_message)
                        
                        save_dump["data"][text_channel.id][message.id] = mess
                        if message.created_at > after:
                            after = message.created_at
            except discord.Forbidden:
                print(guild.name,"] ... cannot access", text_channel.name)
            print(guild.name,"] Processed ", text_channel.name, "...")
        f_name = os.getcwd()+"/"+guild.name+"_"+str(now).replace(" ","T")+".json"
        with open(f_name, "w") as fp:
            json.dump(save_dump, fp)
            print("\tSaved in file ", f_name)
    print("It took ", datetime.utcnow() - now)
    await discord_client.logout()

@discord_client.event
async def on_message(message):
    print("Message received", message.guild.name)
    if "zbeul" in message.content:
        pass 

print("Running...")
discord_client.run(DISCORD_TOKEN_AUTH, bot=False)
