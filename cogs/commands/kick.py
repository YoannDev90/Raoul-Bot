import discord
from discord import app_commands
from discord.ext import commands

class KickCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command()
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = None):
        """
        Expulse un membre du serveur.

        Parameters:
        -----------
        member: discord.Member
            Le membre à expulser
        reason: str, optional
            La raison de l'expulsion
        """
        try:
            await member.kick(reason=reason)
            await interaction.response.send_message(f"{member.mention} a été expulsé. Raison : {reason}", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("Je n'ai pas la permission d'expulser ce membre.", ephemeral=True)

    @kick.error
    async def kick_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("Vous n'avez pas la permission d'utiliser cette commande.", ephemeral=True)
        else:
            await interaction.response.send_message(f"Une erreur s'est produite : {error}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(KickCommand(bot))
