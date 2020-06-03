import discord
import pymongo
import os
from datetime import datetime, timezone

DISCORD_TOKEN_AUTH = os.environ.get("DISCORD_TOKEN_AUTH") # Retrieved from browser local storage
# xxxxxxxxxxxxxxxxxxxxxxx.xxxxxxx.xxxxxxxxxxxxxxxxxxxxxxxxxxx <- mine looked like this

# We assume this client has access to one DB per discord server
# each DB has a collection named "faf_posts"
# Said collection has an attribute "date" written using datetime.datetime
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")

discord_client = discord.Client()
mongo_client = pymongo.MongoClient(MONGO_URI)

@discord_client.event
async def on_ready():
    """
    Performs a retrieval of every message posted 24h ago in every text channel 
    of every guilds the client is connected in.
    """
    now = datetime.now(timezone.utc)
    print("Connected in ", client.guids, "at", now)
    for guild in client.guilds:
        db = mongo_client[guild.name]
        messages = db.messages
        for text_channel in guild.text_channels:
            after = now - timedelta(days=1)

            hist_messages = [ 0 ]
            while len(hist_messages) > 0 :
                hist_messages = text_channel.history(limit=100, after=after).flatten()
                for message in hist_messages:
                    print(message)
                    processed_message = { "date" : message.created_at }
                    messages.insert_one(processed_message)
                    if message.created_at > after:
                        after = message.created_at
            print(guild.name,"] Processed ", text_channel.name)


@discord_client.event
async def on_message(message):
    if "zbeul" in message.content:
        pass 

discord_client.run(DISCORD_TOKEN_AUTH, bot=False)
