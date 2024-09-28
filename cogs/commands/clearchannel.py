import discord
from discord import app_commands
from discord.ext import commands

class ClearChannelCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command()
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clearchannel(self, interaction: discord.Interaction, amount: int = 100):
        """
        Supprime un certain nombre de messages dans le canal actuel.

        Parameters:
        -----------
        amount: int, optional
            Le nombre de messages à supprimer (par défaut 100)
        """
        try:
            await interaction.response.defer(ephemeral=True)
            deleted = await interaction.channel.purge(limit=amount)
            await interaction.followup.send(f"{len(deleted)} messages ont été supprimés.", ephemeral=True)
        except discord.Forbidden:
            await interaction.followup.send("Je n'ai pas la permission de supprimer des messages dans ce canal.", ephemeral=True)

    @clearchannel.error
    async def clearchannel_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("Vous n'avez pas la permission d'utiliser cette commande.", ephemeral=True)
        else:
            await interaction.response.send_message(f"Une erreur s'est produite : {error}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(ClearChannelCommand(bot))
