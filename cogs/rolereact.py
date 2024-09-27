# cogs/rolereact.py
import discord
from discord.ext import commands
from discord import app_commands
from utils.logger import setup_logger
from utils.helpers import send_to_modlogs, create_mod_embed

logger = setup_logger('rolereact', 'logs/rolereact.log')

class RoleReact(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="rolereact", description="Crée un embed avec des boutons pour ajouter des rôles")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def rolereact(self, interaction: discord.Interaction, titre: str, roles: str, maxroles: int = 0, ischangeable: bool = True):
        # Le code existant pour la commande rolereact
        # ...

        logger.info(f"Embed de réaction de rôle créé par {interaction.user}")
        
        embed = create_mod_embed("Création de RoleReact", interaction.user, interaction.user, f"Titre: {titre}, Rôles: {roles}")
        await send_to_modlogs(self.bot, self.bot.modlogs_channel_id, embed)

async def setup(bot):
    await bot.add_cog(RoleReact(bot))
