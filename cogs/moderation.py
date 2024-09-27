# cogs/moderation.py
import discord
from discord.ext import commands
from discord import app_commands
from utils.logger import setup_logger
import asyncio

logger = setup_logger('moderation', 'logs/moderation.log')

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Vérifier la latence du bot")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"Pong! Latence: {round(self.bot.latency * 1000)}ms")
        logger.info(f"Commande ping utilisée par {interaction.user}")

    @app_commands.command(name="kick", description="Expulser un membre")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = "Aucune raison fournie"):
        await member.kick(reason=reason)
        await interaction.response.send_message(f"{member.mention} a été expulsé. Raison: {reason}")
        logger.info(f"{member} a été expulsé par {interaction.user}. Raison: {reason}")

    @app_commands.command(name="tempban", description="Bannir temporairement un membre")
    @app_commands.checks.has_permissions(ban_members=True)
    async def tempban(self, interaction: discord.Interaction, member: discord.Member, duration: int, reason: str = "Aucune raison fournie"):
        await member.ban(reason=reason)
        await interaction.response.send_message(f"{member.mention} a été banni pour {duration} secondes. Raison: {reason}")
        logger.info(f"{member} a été banni temporairement par {interaction.user} pour {duration} secondes. Raison: {reason}")
        await asyncio.sleep(duration)
        await interaction.guild.unban(member)
        logger.info(f"{member} a été débanni automatiquement après {duration} secondes")

async def setup(bot):
    await bot.add_cog(Moderation(bot))
