import discord
from discord import app_commands
from discord.ext import commands

class SetUsernameCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command()
    @app_commands.checks.has_permissions(manage_nicknames=True)
    async def setusername(self, interaction: discord.Interaction, member: discord.Member, nickname: str):
        """
        Change le surnom d'un membre sur le serveur.

        Parameters:
        -----------
        member: discord.Member
            Le membre dont le surnom doit être changé
        nickname: str
            Le nouveau surnom à attribuer
        """
        try:
            await
