import discord
from discord.ext import commands
import requests
import random
import string
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_BOT_TOKEN")  # Ton token de bot ici

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# API publique pour checker les usernames
CHECKER_API = "https://api.pomelo.lixqa.cc/v1/lookups"

def generate_4char(letters_only=False):
    if letters_only:
        chars = string.ascii_lowercase
    else:
        chars = string.ascii_lowercase + string.digits
    return ''.join(random.choices(chars, k=4))

async def check_username_api(username: str):
    try:
        payload = {"username": username}
        r = requests.post(CHECKER_API, json=payload, timeout=10)
        
        if r.status_code == 200:
            data = r.json()
            # Selon la réponse de l'API (adapte si besoin)
            if data.get("available") is True or data.get("status") == "available":
                return True
            else:
                return False
        elif r.status_code == 429:
            print("Rate limit API")
            await asyncio.sleep(5)
            return False
        else:
            print(f"Erreur API {r.status_code}")
            return False
    except Exception as e:
        print(f"Erreur lors du check : {e}")
        return False

@bot.event
async def on_ready():
    print(f"✅ Bot connecté en tant que {bot.user}")
    print("Utilise la commande : !find4 <nombre>")

@bot.command()
async def find4(ctx, nombre: int = 30):
    if nombre > 100:
        nombre = 100  # Limite de sécurité
    
    await ctx.send(f"🔍 Recherche de **{nombre}** pseudos 4 caractères en cours...")

    found = []
    for i in range(nombre):
        username = generate_4char()
        is_available = await check_username_api(username)
        
        if is_available:
            found.append(username)
            try:
                await ctx.send(f"🎉 **DISPONIBLE !** `@{username}`")
            except:
                pass
        
        await asyncio.sleep(1.3)  # Respect des rate limits

    if found:
        await ctx.send(f"✅ **Recherche terminée !** {len(found)} nom(s) disponible(s) :\n" + 
                      "\n".join([f"`@{u}`" for u in found]))
    else:
        await ctx.send("✅ Recherche terminée. Aucun nom disponible trouvé cette fois.")

bot.run(TOKEN)