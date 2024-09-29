# main.py
import discord
from discord.ext import commands
import asyncio
import logging
from config import TOKEN, MODLOGS_CHANNEL_ID, ADMIN_ROLE_ID, OWNER_ID
from utils.logger import setup_logger

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Configuration du logging principal
logger = setup_logger('main', 'logs/main.log')

@bot.event
async def on_ready():
    logger.info(f'{bot.user} est connecté et prêt!')
    try:
        synced = await bot.tree.sync()
        logger.info(f"Synced {len(synced)} command(s)")
    except Exception as e:
        logger.error(f"Erreur lors de la synchronisation des commandes: {e}")

async def load_cogs():
    for extension in ['moderation', 'rolereact', 'newrole', 'setusername', 'clearchannel', 'automod']:
        try:
            await bot.load_extension(f'cogs/commands/{extension}.py')
            logger.info(f'Loaded extension: {extension}')
        except Exception as e:
            logger.error(f'Failed to load extension {extension}: {e}')

async def main():
    await load_cogs()
    try:
        await bot.start(TOKEN)
    except Exception as e:
        logger.critical(f"Erreur fatale lors du lancement du bot: {str(e)}")
    finally:
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())
