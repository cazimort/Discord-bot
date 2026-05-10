import discord
from discord.ext import commands
import random
import string
import asyncio
import os
from flask import Flask
import threading
import aiohttp

print(‘Demarrage du bot…’)

TOKEN = os.getenv(‘DISCORD_BOT_TOKEN’)
WEBHOOK_URL = os.getenv(‘WEBHOOK_URL’)

if not TOKEN:
print(‘ERREUR : DISCORD_BOT_TOKEN manquant !’)
exit(1)

# ====================== FLASK KEEP ALIVE ======================

app = Flask(**name**)

@app.route(’/’)
def home():
return ‘Bot Discord 4 lettres - Mode Infini en ligne !’

def run_flask():
port = int(os.environ.get(‘PORT’, 8080))
app.run(host=‘0.0.0.0’, port=port)

# ====================== BOT ======================

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=’!’, intents=intents)

is_searching = False
CHECKER_API = ‘https://api.pomelo.lixqa.cc/v1/lookups’

# Mode equilibre (~200 tests/min)

CONCURRENT_TASKS = 5
DELAY_BETWEEN_BATCHES = 1.5
RATE_LIMIT_PAUSE = 10

def generate_4char_letters():
return ‘’.join(random.choices(string.ascii_lowercase, k=4))

async def send_webhook(session, username):
if not WEBHOOK_URL:
return
embed = {
‘title’: ‘Pseudo 4 lettres disponible !’,
‘description’: f’@{username}’,
‘color’: 0x00ff00
}
try:
await session.post(WEBHOOK_URL, json={‘embeds’: [embed]})
except:
pass

async def check_username_api(session, username):
try:
async with session.post(
CHECKER_API,
json={‘username’: username},
timeout=aiohttp.ClientTimeout(total=10)
) as r:
if r.status == 429:
return False, True
if r.status == 200:
data = await r.json()
available = data.get(‘available’) is True or data.get(‘status’) == ‘available’
return available, False
return False, False
except:
return False, False

@bot.event
async def on_ready():
print(f’Bot connecte : {bot.user}’)
print(‘Commandes : !find4inf | !stop’)

@bot.command()
async def find4inf(ctx):
global is_searching
if is_searching:
await ctx.send(‘Une recherche est deja en cours !’)
return

```
is_searching = True
await ctx.send(
    f'Recherche infinie lancee (4 lettres a-z)\n'
    f'Mode equilibre : {CONCURRENT_TASKS} tests en parallele\n'
    f'Tape !stop pour arreter.'
)

found = 0
tested = 0
last_report = 0

async with aiohttp.ClientSession() as session:
    try:
        while is_searching:
            usernames = [generate_4char_letters() for _ in range(CONCURRENT_TASKS)]

            results = await asyncio.gather(
                *[check_username_api(session, u) for u in usernames]
            )

            rate_limited = any(rl for _, rl in results)

            if rate_limited:
                await ctx.send(
                    f'Rate limit detecte ! Pause de {RATE_LIMIT_PAUSE} secondes...'
                )
                await asyncio.sleep(RATE_LIMIT_PAUSE)
                continue

            tested += CONCURRENT_TASKS

            for username, (available, _) in zip(usernames, results):
                if available:
                    found += 1
                    await ctx.send(f'DISPONIBLE ! @{username}')
                    await send_webhook(session, username)

            if tested // 100 > last_report // 100:
                last_report = tested
                await ctx.send(
                    f'Rapport - {tested} tentatives\n'
                    f'Disponibles trouves : {found}\n'
                    f'Indisponibles : {tested - found}'
                )

            await asyncio.sleep(DELAY_BETWEEN_BATCHES)

    except asyncio.CancelledError:
        pass
    finally:
        is_searching = False
        await ctx.send(
            f'Recherche arretee.\n'
            f'Tentatives : {tested}\n'
            f'Disponibles : {found}'
        )
```

@bot.command()
async def stop(ctx):
global is_searching
if is_searching:
is_searching = False
await ctx.send(‘Arret de la recherche demande…’)
else:
await ctx.send(‘Aucune recherche en cours.’)

# ====================== LANCEMENT ======================

if **name** == ‘**main**’:
threading.Thread(target=run_flask, daemon=True).start()
print(‘Bot lance - Mode equilibre actif’)
bot.run(TOKEN)