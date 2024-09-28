import discord
from discord import app_commands
from discord.ext import commands

class UnmuteCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command()
    @app_commands.checks.has_permissions(manage_roles=True)
    async def unmute(self, interaction: discord.Interaction, member: discord.Member):
        """
        Retire le statut muet d'un membre du serveur.

        Parameters:
        -----------
        member: discord.Member
            Le membre à démuter
        """
        mute_role = discord.utils.get(interaction.guild.roles, name="Muted")
        if not mute_role:
            await interaction.response.send_message("Il n'y a pas de rôle 'Muted' sur ce serveur.", ephemeral=True)
            return

        try:
            await member.remove_roles(mute_role)
            await interaction.response.send_message(f"{member.mention} n'est plus muet.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("Je n'ai pas la permission de démuter ce membre.", ephemeral=True)

    @unmute.error
    async def unmute_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("Vous n'avez pas la permission d'utiliser cette commande.", ephemeral=True)
        else:
            await interaction.response.send_message(f"Une erreur s'est produite : {error}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(UnmuteCommand(bot))
