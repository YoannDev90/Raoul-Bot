import discord
from discord import app_commands
from discord.ext import commands
import json
import os
import hashlib

class RoleReact(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.rolereact_data = {}
        self.load_rolereact_data()

    def load_rolereact_data(self):
        if os.path.exists('rolereact_data.json'):
            with open('rolereact_data.json', 'r') as f:
                self.rolereact_data = json.load(f)

    def save_rolereact_data(self):
        with open('rolereact_data.json', 'w') as f:
            json.dump(self.rolereact_data, f)

    @app_commands.command()
    @app_commands.checks.has_permissions(manage_roles=True)
    async def rolereact(self, interaction: discord.Interaction, message: str, roles: str, maxroles: int = 0, locked: bool = False):
        """
        Crée un message de réaction pour l'attribution de rôles avec des boutons.
        """
        role_list = [role.strip() for role in roles.split(',')]

        embed = discord.Embed(title="Réaction de Rôle", description=message, color=discord.Color.blue())
        for role_name in role_list:
            embed.add_field(name=role_name, value="\u200b", inline=False)

        view = RoleReactView(self.bot, role_list, maxroles, locked)
        sent_message = await interaction.channel.send(embed=embed, view=view)

        message_id = str(sent_message.id)
        self.rolereact_data[message_id] = {
            'roles': role_list,
            'maxroles': maxroles,
            'locked': locked,
            'channel_id': interaction.channel_id
        }
        self.save_rolereact_data()

        await interaction.response.send_message("Message de réaction de rôle créé.", ephemeral=True)

    @rolereact.error
    async def rolereact_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("Vous n'avez pas la permission d'utiliser cette commande.", ephemeral=True)
        else:
            await interaction.response.send_message(f"Une erreur s'est produite : {error}", ephemeral=True)

    async def cog_load(self):
        self.bot.add_view(RoleReactView(self.bot))

class RoleReactView(discord.ui.View):
    def __init__(self, bot, roles=None, maxroles=0, locked=False):
        super().__init__(timeout=None)
        self.bot = bot
        if roles:
            for role in roles:
                self.add_item(RoleButton(role))
        self.maxroles = maxroles
        self.locked = locked

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        data = self.bot.get_cog('RoleReact').rolereact_data.get(str(interaction.message.id))
        if not data:
            return False

        self.maxroles = data['maxroles']
        self.locked = data['locked']

        if self.locked:
            user_roles = [role.name for role in interaction.user.roles]
            if any(role in user_roles for role in data['roles']):
                await interaction.response.send_message("Vous avez déjà sélectionné un rôle et ne pouvez plus le changer.", ephemeral=True)
                return False

        if self.maxroles > 0:
            user_roles = [role.name for role in interaction.user.roles]
            selected_roles = [role for role in data['roles'] if role in user_roles]
            if len(selected_roles) >= self.maxroles and interaction.data['custom_id'].split(':')[1] not in user_roles:
                await interaction.response.send_message(f"Vous ne pouvez pas sélectionner plus de {self.maxroles} rôles.", ephemeral=True)
                return False

        return True

class RoleButton(discord.ui.Button):
    def __init__(self, role_name: str):
        truncated_name = role_name[:80]  # Tronquer le nom du rôle à 80 caractères
        custom_id = f"rr:{hashlib.md5(role_name.encode()).hexdigest()[:20]}"  # Créer un custom_id unique et court
        super().__init__(style=discord.ButtonStyle.primary, label=truncated_name, custom_id=custom_id)
        self.full_role_name = role_name

    async def callback(self, interaction: discord.Interaction):
        role = discord.utils.get(interaction.guild.roles, name=self.full_role_name)
        if role is None:
            await interaction.response.send_message(f"Le rôle {self.full_role_name} n'existe pas.", ephemeral=True)
            return

        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message(f"Le rôle {self.full_role_name} vous a été retiré.", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(f"Le rôle {self.full_role_name} vous a été attribué.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(RoleReact(bot))
