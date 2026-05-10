import discord
from discord.ext import commands
import requests
import random
import string
import asyncio
import os
from flask import Flask
import threading

print("🚀 Démarrage du bot...")

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

if not TOKEN:
    print("❌ ERREUR : DISCORD_BOT_TOKEN manquant !")
    exit(1)

# ====================== FLASK KEEP ALIVE ======================
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Discord 4 lettres - Mode Infini en ligne ! ✅"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# ====================== BOT ======================
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

is_searching = False
CHECKER_API = "https://api.pomelo.lixqa.cc/v1/lookups"

def generate_4char_letters():
    return ''.join(random.choices(string.ascii_lowercase, k=4))

async def send_webhook(username: str):
    if not WEBHOOK_URL:
        return
    embed = {
        "title": "🎉 Pseudo 4 lettres disponible !",
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
    print(f"✅ Bot connecté : {bot.user}")
    print("Commandes : !find4inf (infini) | !stop")

@bot.command()
async def find4inf(ctx):
    global is_searching
    if is_searching:
        await ctx.send("⚠️ Une recherche est déjà en cours !")
        return

    is_searching = True
    await ctx.send("🔄 **Recherche infinie lancée** (4 lettres a-z)\nLe bot va continuer jusqu'à ce que tu fasses `!stop`.\nLes disponibilités seront envoyées immédiatement.")

    found = 0
    try:
        while is_searching:
            username = generate_4char_letters()
            
            if await check_username_api(username):
                found += 1
                await ctx.send(f"🎉 **DISPONIBLE !** `@{username}`")
                await send_webhook(username)
                await asyncio.sleep(1)
            
            await asyncio.sleep(1.3)  # Important : ne pas trop spammer

    except asyncio.CancelledError:
        pass
    finally:
        is_searching = False
        await ctx.send(f"✅ Recherche infinie arrêtée. **{found}** pseudo(s) trouvé(s) au total.")

@bot.command()
async def stop(ctx):
    global is_searching
    if is_searching:
        is_searching = False
        await ctx.send("⛔ Arrêt de la recherche infinie demandé...")
    else:
        await ctx.send("Aucune recherche en cours.")

# ====================== LANCEMENT ======================
if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    print("🚀 Bot lancé - Mode Infini disponible")
    bot.run(TOKEN)