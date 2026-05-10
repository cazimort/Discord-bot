import discord
from discord.ext import commands
import requests
import random
import string
import asyncio
import os

print("🚀 Démarrage du script...")

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

print(f"Token trouvé : {'Oui' if TOKEN else 'NON'}")

if not TOKEN:
    print("❌ ERREUR CRITIQUE : DISCORD_BOT_TOKEN manquant dans les variables Render !")
    exit(1)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

CHECKER_API = "https://api.pomelo.lixqa.cc/v1/lookups"

def generate_4char():
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choices(chars, k=4))

async def send_webhook(username: str):
    if not WEBHOOK_URL:
        return
    embed = {
        "title": "🎉 Pseudo 4 caractères disponible !",
        "description": f"`@{username}`",
        "color": 0x00ff00
    }
    try:
        requests.post(WEBHOOK_URL, json={"embeds": [embed]})
    except:
        pass

async def check_username_api(username: str):
    try:
        r = requests.post(CHECKER_API, json={"username": username}, timeout=10)
        if r.status_code == 200:
            data = r.json()
            return data.get("available") is True or data.get("status") == "available"
        return False
    except:
        return False

@bot.event
async def on_ready():
    print(f"✅ Bot connecté avec succès : {bot.user}")

@bot.command()
async def find4(ctx, nombre: int = 20):
    await ctx.send(f"🔍 Recherche de {nombre} pseudos 4 caractères...")
    found_count = 0
    for _ in range(nombre):
        username = generate_4char()
        if await check_username_api(username):
            found_count += 1
            await ctx.send(f"🎉 **DISPONIBLE !** `@{username}`")
            await send_webhook(username)
        await asyncio.sleep(1.3)
    await ctx.send(f"✅ Recherche terminée. {found_count} pseudo(s) trouvé(s).")

print("Lancement de bot.run()...")
bot.run(TOKEN)