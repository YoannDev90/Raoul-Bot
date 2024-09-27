# cogs/automod.py
import discord
from discord.ext import commands
from utils.logger import setup_logger
import re

logger = setup_logger('automod', 'logs/automod.log')

class AutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.spam_threshold = 5
        self.spam_interval = 5
        self.user_message_count = {}

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        await self.check_spam(message)
        await self.check_banned_words(message)

    async def check_spam(self, message):
        author_id = message.author.id
        current_time = message.created_at.timestamp()

        if author_id not in self.user_message_count:
            self.user_message_count[author_id] = []

        self.user_message_count[author_id].append(current_time)

        # Supprimer les messages plus anciens que l'intervalle
        self.user_message_count[author_id] = [t for t in self.user_message_count[author_id] if current_time - t <= self.spam_interval]

        if len(self.user_message_count[author_id]) > self.spam_threshold:
            await message.author.timeout(duration=60, reason="Spam détecté")
            await message.channel.send(f"{message.author.mention} a été mis en timeout pour spam.")
            logger.warning(f"Spam détecté: {message.author} a été mis en timeout")

    async def check_banned_words(self, message):
        banned_words = ["mot1", "mot2", "mot3"]  # Ajoutez vos mots bannis ici
        content = message.content.lower()
        
        if any(word in content for word in banned_words):
            await message.delete()
            await message.channel.send(f"{message.author.mention}, votre message a été supprimé car il contenait un mot banni.")
            logger.warning(f"Message supprimé de {message.author} pour utilisation de mot banni")

async def setup(bot):
    await bot.add_cog(AutoMod(bot))
