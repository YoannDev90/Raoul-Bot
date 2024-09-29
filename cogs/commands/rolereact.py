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
        """
        await interaction.response.defer()

        role_list = [role.strip() for role in roles.split()]
        guild_roles = interaction.guild.roles
        valid_roles = []

        for role_mention in role_list:
            role_id = int(role_mention.strip('<@&>'))
            role = discord.utils.get(guild_roles, id=role_id)
            if role:
                valid_roles.append(role)

        embed = discord.Embed(title=titre, color=discord.Color.blue())
        
        roles_text = "\n".join([f"• {role.name}" for role in valid_roles])
        embed.description = roles_text

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

    async def cog_load(self):
        # Charger les anciens rolereact au démarrage du bot
        for message_id, data in self.rolereact_data.items():
            channel = self.bot.get_channel(data['channel_id'])
            if channel:
                try:
                    message = await channel.fetch_message(int(message_id))
                    roles = [discord.utils.get(channel.guild.roles, id=role_id) for role_id in data['roles']]
                    view = RoleReactView(self.bot, roles, data['maxroles'], data['locked'])
                    await message.edit(view=view)
                except discord.NotFound:
                    # Le message n'existe plus, on le supprime des données
                    del self.rolereact_data[message_id]
                    self.save_rolereact_data()
                except Exception as e:
                    print(f"Erreur lors du chargement du rolereact {message_id}: {e}")

        # Ajouter la vue persistante
        self.bot.add_view(RoleReactView(self.bot))

class RoleReactView(discord.ui.View):
    def __init__(self, bot, roles=None, maxroles=0, locked=False):
        super().__init__(timeout=None)
        self.bot = bot
        self.maxroles = maxroles
        self.locked = locked
        self.user_roles = {}

        if roles:
            max_length = max(len(role.name) for role in roles)
            button_width = min(max_length + 4, 25)  # +4 pour l'espacement, max 25 caractères

            for i, role in enumerate(roles):
                button_style = discord.ButtonStyle.primary if i % 2 == 0 else discord.ButtonStyle.danger
                padded_name = self.pad_role_name(role.name, button_width)
                self.add_item(RoleButton(role, button_style, padded_name))

    def pad_role_name(self, name, width):
        if len(name) >= width:
            return name[:width]
        padding = (width - len(name)) // 2
        return ' ' * padding + name + ' ' * (width - len(name) - padding)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        cog = self.bot.get_cog('RoleReact')
        if not cog:
            return False

        data = cog.rolereact_data.get(str(interaction.message.id))
        if not data:
            return False

        self.maxroles = data['maxroles']
        self.locked = data['locked']

        if interaction.user.id not in self.user_roles:
            self.user_roles[interaction.user.id] = set()

        role_id = int(interaction.data['custom_id'].split(':')[1])
        
        if self.locked and self.user_roles[interaction.user.id]:
            await interaction.response.send_message("Vous avez déjà sélectionné un rôle et ne pouvez plus le changer.", ephemeral=True)
            return False

        if role_id in self.user_roles[interaction.user.id]:
            self.user_roles[interaction.user.id].remove(role_id)
            return True

        if self.maxroles > 0 and len(self.user_roles[interaction.user.id]) >= self.maxroles:
            await interaction.response.send_message(f"Vous ne pouvez pas sélectionner plus de {self.maxroles} rôles.", ephemeral=True)
            return False

        self.user_roles[interaction.user.id].add(role_id)
        return True

class RoleButton(discord.ui.Button):
    def __init__(self, role: discord.Role, style: discord.ButtonStyle, padded_name: str):
        super().__init__(style=style, label=padded_name, custom_id=f"rr:{role.id}")
        self.role = role

    async def callback(self, interaction: discord.Interaction):
        if self.role in interaction.user.roles:
            await interaction.user.remove_roles(self.role)
            await interaction.response.send_message(f"Le rôle {self.role.name} vous a été retiré.", ephemeral=True)
        else:
            await interaction.user.add_roles(self.role)
            await interaction.response.send_message(f"Le rôle {self.role.name} vous a été attribué.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(RoleReact(bot))
