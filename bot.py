import discord
from discord.ext import commands
import requests
import random
import string
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# API pour checker les pseudos
CHECKER_API = "https://api.pomelo.lixqa.cc/v1/lookups"

def generate_4char(letters_only=False):
    if letters_only:
        chars = string.ascii_lowercase
    else:
        chars = string.ascii_lowercase + string.digits
    return ''.join(random.choices(chars, k=4))

async def send_webhook(username: str):
    """Envoie une alerte via webhook"""
    if not WEBHOOK_URL:
        return
    
    embed = {
        "title": "🎉 Pseudo 4 caractères disponible !",
        "description": f"`@{username}`",
        "color": 0x00ff00,
        "timestamp": "now"
    }
    
    try:
        requests.post(WEBHOOK_URL, json={"embeds": [embed]}, timeout=10)
    except:
        pass

async def check_username_api(username: str):
    try:
        payload = {"username": username}
        r = requests.post(CHECKER_API, json=payload, timeout=10)
        
        if r.status_code == 200:
            data = r.json()
            if data.get("available") is True or data.get("status") == "available":
                return True
        elif r.status_code == 429:
            await asyncio.sleep(5)
        return False
    except:
        return False

@bot.event
async def on_ready():
    print(f"✅ Bot connecté : {bot.user}")
    print("Commande : !find4 <nombre>")

@bot.command()
async def find4(ctx, nombre: int = 30):
    if nombre > 100:
        nombre = 100
    
    await ctx.send(f"🔍 Recherche de **{nombre}** pseudos 4 caractères en cours...\nLes disponibilités seront envoyées ici + via webhook.")

    found = []
    for i in range(nombre):
        username = generate_4char()
        is_available = await check_username_api(username)
        
        if is_available:
            found.append(username)
            
            # Message dans le salon
            try:
                await ctx.send(f"🎉 **DISPONIBLE !** `@{username}`")
            except:
                pass
            
            # Envoi via webhook
            await send_webhook(username)
        
        await asyncio.sleep(1.3)

    if found:
        await ctx.send(f"✅ **Recherche terminée !** {len(found)} pseudo(s) trouvé(s).")
    else:
        await ctx.send("✅ Recherche terminée. Aucun pseudo disponible cette fois.")

bot.run(TOKEN)