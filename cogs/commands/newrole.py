import discord
from discord import app_commands
from discord.ext import commands

class NewRoleCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command()
    @app_commands.checks.has_permissions(manage_roles=True)
    async def newrole(self, interaction: discord.Interaction, name: str, color: discord.Color = discord.Color.default(), reason: str = None):
        """
        Crée un nouveau rôle sur le serveur.

        Parameters:
        -----------
        name: str
            Le nom du nouveau rôle
        color: discord.Color, optional
            La couleur du rôle (par défaut, pas de couleur)
        reason: str, optional
            La raison de la création du rôle
        """
        try:
            role = await interaction.guild.create_role(name=name, color=color, reason=reason)
            await interaction.response.send_message(f"Le rôle {role.mention} a été créé.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("Je n'ai pas la permission de créer des rôles.", ephemeral=True)

    @newrole.error
    async def newrole_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("Vous n'avez pas la permission d'utiliser cette commande.", ephemeral=True)
        else:
            await interaction.response.send_message(f"Une erreur s'est produite : {error}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(NewRoleCommand(bot))
