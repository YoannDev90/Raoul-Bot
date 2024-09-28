import discord
from discord import app_commands
from discord.ext import commands

class WarnCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.warnings = {}

    @app_commands.command()
    @app_commands.checks.has_permissions(kick_members=True)
    async def warn(self, interaction: discord.Interaction, member: discord.Member, reason: str):
        """
        Avertit un membre du serveur.

        Parameters:
        -----------
        member: discord.Member
            Le membre à avertir
        reason: str
            La raison de l'avertissement
        """
        if member.id not in self.warnings:
            self.warnings[member.id] = []
        
        self.warnings[member.id].append(reason)
        
        await interaction.response.send_message(f"{member.mention} a été averti. Raison : {reason}", ephemeral=True)
        await member.send(f"Vous avez reçu un avertissement sur le serveur {interaction.guild.name}. Raison : {reason}")

    @warn.error
    async def warn_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("Vous n'avez pas la permission d'utiliser cette commande.", ephemeral=True)
        else:
            await interaction.response.send_message(f"Une erreur s'est produite : {error}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(WarnCommand(bot))
