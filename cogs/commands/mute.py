import discord
from discord import app_commands
from discord.ext import commands

class MuteCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command()
    @app_commands.checks.has_permissions(manage_roles=True)
    async def mute(self, interaction: discord.Interaction, member: discord.Member, reason: str = None):
        """
        Rend muet un membre du serveur.

        Parameters:
        -----------
        member: discord.Member
            Le membre à rendre muet
        reason: str, optional
            La raison du mute
        """
        mute_role = discord.utils.get(interaction.guild.roles, name="Muted")
        if not mute_role:
            mute_role = await interaction.guild.create_role(name="Muted")
            for channel in interaction.guild.channels:
                await channel.set_permissions(mute_role, speak=False, send_messages=False)

        try:
            await member.add_roles(mute_role, reason=reason)
            await interaction.response.send_message(f"{member.mention} a été rendu muet. Raison : {reason}", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("Je n'ai pas la permission de rendre muet ce membre.", ephemeral=True)

    @mute.error
    async def mute_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("Vous n'avez pas la permission d'utiliser cette commande.", ephemeral=True)
        else:
            await interaction.response.send_message(f"Une erreur s'est produite : {error}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(MuteCommand(bot))
