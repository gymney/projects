# Private Discord Bot

A personal Discord bot, built as a learning project — private use rather than
a public/community bot.

## Concept

- A Discord bot for personal use, likely running in a small/private server.
- Good fit as an early Python project: small surface area, fast feedback loop
  (you can see it working live in Discord), and a natural way to practice
  async Python.

## Suggested tech stack

- **Language:** Python
- **Library:** `discord.py` (or `nextcord`/`py-cord` if `discord.py`'s
  maintenance status is a concern at build time — worth a quick check)
- **Hosting:** can run locally during development; a small VPS or a free-tier
  host works for something that needs to stay online

## Suggested starting scope

Since the specific features weren't nailed down yet, here's a reasonable
default scope to start from and adjust:

- Basic bot skeleton: connects, responds to a `!ping`/slash command, logs to
  console
- A handful of utility commands (reminders, simple polls, or fun/random
  commands)
- Config via environment variables (bot token, server/channel IDs) — never
  commit the token
- Simple persistence (SQLite is enough for a private bot) if commands need to
  remember anything between restarts

## Getting started (once scope is picked)

```bash
pip install discord.py python-dotenv
```

```python
# bot.py (skeleton)
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command()
async def ping(ctx):
    await ctx.send("pong")

bot.run(TOKEN)
```

## Open questions to resolve when picking this back up

- What's the bot actually *for* — utility, moderation, fun commands, or
  something tied into another project (e.g. QuestBound notifications)?
- Which server(s) will it run in?
- Does it need to persist any data, or is it stateless?
