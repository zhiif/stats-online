import discord
import json
import asyncio
import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
INTERVAL = int(os.getenv("UPDATE_INTERVAL_MINUTES", 5))

intents = discord.Intents.default()
client = discord.Client(intents=intents)

async def get_roblox_presence(user_ids):
    url = "https://presence.roblox.com/v1/presence/users"
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json={"userIds": user_ids}) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("userPresences", [])
            return []

async def update_channel_name():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)

    while not client.is_closed():
        try:
            with open("users.json") as f:
                users = json.load(f)

            roblox_ids = [u["roblox_id"] for u in users.values()]
            presences = await get_roblox_presence(roblox_ids)

            online_count = sum(1 for p in presences if p.get("userPresenceType") in [1, 2, 3])
            new_name = f"🟢 Roblox Online: {online_count}"

            if channel and channel.name != new_name:
                await channel.edit(name=new_name)
                print(f"[UPDATE] {new_name}")
        except Exception as e:
            print("⚠️ Error:", e)

        await asyncio.sleep(INTERVAL * 60)

@client.event
async def on_ready():
    print(f"✅ Bot aktif sebagai {client.user}")
    client.loop.create_task(update_channel_name())

client.run(TOKEN)
