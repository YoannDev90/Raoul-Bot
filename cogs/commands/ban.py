import discord
from discord import app_commands
from discord.ext import commands

class BanCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command()
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = None):
        """
        Banni un membre du serveur.

        Parameters:
        -----------
        member: discord.Member
            Le membre à bannir
        reason: str, optional
            La raison du bannissement
        """
        try:
            await member.ban(reason=reason)
            await interaction.response.send_message(f"{member.mention} a été banni. Raison : {reason}", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("Je n'ai pas la permission de bannir ce membre.", ephemeral=True)

    @ban.error
    async def ban_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("Vous n'avez pas la permission d'utiliser cette commande.", ephemeral=True)
        else:
            await interaction.response.send_message(f"Une erreur s'est produite : {error}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(BanCommand(bot))
