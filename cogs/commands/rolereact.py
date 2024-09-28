import discord
from discord import app_commands
from discord.ext import commands

class RoleReactCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command()
    @app_commands.checks.has_permissions(manage_roles=True)
    async def rolereact(self, interaction: discord.Interaction, message: str, roles: str):
        """
        Crée un message de réaction pour l'attribution de rôles.

        Parameters:
        -----------
        message: str
            Le message à afficher pour la réaction de rôle
        roles: str
            Les rôles à attribuer, séparés par des virgules
        """
        role_list = [role.strip() for role in roles.split(',')]
        emoji_list = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']

        embed = discord.Embed(title="Réaction de Rôle", description=message, color=discord.Color.blue())
        for i, role_name in enumerate(role_list):
            if i < len(emoji_list):
                embed.add_field(name=f"{emoji_list[i]} {role_name}", value="\u200b", inline=False)

        sent_message = await interaction.channel.send(embed=embed)
        for i in range(len(role_list)):
            if i < len(emoji_list):
                await sent_message.add_reaction(emoji_list[i])

        await interaction.response.send_message("Message de réaction de rôle créé.", ephemeral=True)

    @rolereact.error
    async def rolereact_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("Vous n'avez pas la permission d'utiliser cette commande.", ephemeral=True)
        else:
            await interaction.response.send_message(f"Une erreur s'est produite : {error}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(RoleReactCommand(bot))
