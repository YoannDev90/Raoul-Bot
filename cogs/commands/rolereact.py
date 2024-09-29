import discord
from discord import app_commands
from discord.ext import commands
import json
import os

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
    async def rolereact(self, interaction: discord.Interaction, titre: str, roles: str, maxroles: int = 0, locked: bool = False):
        """
        Crée un message de réaction pour l'attribution de rôles avec des boutons.

        Parameters:
        -----------
        titre: str
            Le titre de l'embed.
        roles: str
            Les rôles à attribuer, séparés par des mentions.
        maxroles: int, optional
            Le nombre maximum de rôles qu'un utilisateur peut sélectionner (0 pour illimité).
        locked: bool, optional
            Si True, les utilisateurs ne peuvent interagir qu'une seule fois avec les boutons.
        """
        await interaction.response.defer()

        role_list = [role.strip() for role in roles.split()]
        guild_roles = interaction.guild.roles
        valid_roles = []
        role_names = []

        for role_mention in role_list:
            role_id = int(role_mention.strip('<@&>'))
            role = discord.utils.get(guild_roles, id=role_id)
            if role:
                valid_roles.append(role)
                role_names.append(role.name)

        description = "\n".join([f"• {role_name}" for role_name in role_names])
        embed = discord.Embed(title=titre, description=description, color=discord.Color.blue())

        view = RoleReactView(self.bot, valid_roles, maxroles, locked)
        sent_message = await interaction.channel.send(embed=embed, view=view)

        message_id = str(sent_message.id)
        self.rolereact_data[message_id] = {
            'roles': [role.id for role in valid_roles],
            'maxroles': maxroles,
            'locked': locked,
            'channel_id': interaction.channel_id
        }
        self.save_rolereact_data()

        await interaction.followup.send("Message de réaction de rôle créé.", ephemeral=True)

    @rolereact.error
    async def rolereact_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("Vous n'avez pas la permission d'utiliser cette commande.", ephemeral=True)
        else:
            await interaction.response.send_message(f"Une erreur s'est produite : {error}", ephemeral=True)

class RoleReactView(discord.ui.View):
    def __init__(self, bot, roles=None, maxroles=0, locked=False):
        super().__init__(timeout=None)
        self.bot = bot
        self.maxroles = maxroles
        self.locked = locked
        self.user_roles_selected = set()  # Pour suivre les rôles sélectionnés par l'utilisateur

        if roles:
            for i, role in enumerate(roles):
                button_style = discord.ButtonStyle.primary if i % 2 == 0 else discord.ButtonStyle.danger
                self.add_item(RoleButton(role, button_style))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        data = self.bot.get_cog('RoleReact').rolereact_data.get(str(interaction.message.id))
        
        if not data:
            return False

        if self.locked and any(role.id in self.user_roles_selected for role in data['roles']):
            await interaction.response.send_message("Vous avez déjà sélectionné un rôle et ne pouvez plus le changer.", ephemeral=True)
            return False

        if self.maxroles > 0:
            user_roles_count = len(self.user_roles_selected)
            if user_roles_count >= self.maxroles and interaction.data['custom_id'].split(':')[1] not in self.user_roles_selected:
                await interaction.response.send_message(f"Vous ne pouvez pas sélectionner plus de {self.maxroles} rôles.", ephemeral=True)
                return False

        return True

class RoleButton(discord.ui.Button):
    def __init__(self, role: discord.Role, style: discord.ButtonStyle):
        super().__init__(style=style, label=role.name, custom_id=f"rr:{role.id}")
        self.role = role

    async def callback(self, interaction: discord.Interaction):
        view: RoleReactView = self.view  # Récupérer la vue pour accéder aux données

        if self.role in interaction.user.roles:
            await interaction.user.remove_roles(self.role)
            view.user_roles_selected.discard(self.role.id)  # Retirer le rôle de l'ensemble
            await interaction.response.send_message(f"Le rôle {self.role.name} vous a été retiré.", ephemeral=True)
        else:
            await interaction.user.add_roles(self.role)
            view.user_roles_selected.add(self.role.id)  # Ajouter le rôle à l'ensemble
            await interaction.response.send_message(f"Le rôle {self.role.name} vous a été attribué.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(RoleReact(bot))
