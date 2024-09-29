import discord
from discord import app_commands
from discord.ext import commands
import json
import os
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('RoleReact')

class RoleReact(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.rolereact_data = {}
        self.load_rolereact_data()

    def load_rolereact_data(self):
        try:
            with open('rolereact_data.json', 'r') as f:
                self.rolereact_data = json.load(f)
            logger.info("Données RoleReact chargées avec succès.")
        except FileNotFoundError:
            logger.warning("Fichier rolereact_data.json non trouvé. Création d'un nouveau fichier.")
            self.rolereact_data = {}
        except json.JSONDecodeError:
            logger.error("Erreur lors du décodage du fichier JSON. Initialisation avec des données vides.")
            self.rolereact_data = {}

    def save_rolereact_data(self):
        with open('rolereact_data.json', 'w') as f:
            json.dump(self.rolereact_data, f)
        logger.info("Données RoleReact sauvegardées.")

    @app_commands.command()
    @app_commands.checks.has_permissions(manage_roles=True)
    async def rolereact(self, interaction: discord.Interaction, titre: str, roles: str, maxroles: int = 0, locked: bool = False):
        """Crée un message de réaction pour l'attribution de rôles avec des boutons."""
        await interaction.response.defer()

        role_list = roles.split()
        guild_roles = interaction.guild.roles
        valid_roles = [discord.utils.get(guild_roles, id=int(role_id.strip('<@&>'))) for role_id in role_list if discord.utils.get(guild_roles, id=int(role_id.strip('<@&>')))]

        embed = discord.Embed(title=titre, description="\n".join([f"• {role.name}" for role in valid_roles]), color=discord.Color.blue())

        view = RoleReactView(self.bot, valid_roles, maxroles, locked)
        sent_message = await interaction.channel.send(embed=embed, view=view)

        self.rolereact_data[str(sent_message.id)] = {
            'roles': [role.id for role in valid_roles],
            'maxroles': maxroles,
            'locked': locked,
            'channel_id': interaction.channel_id
        }
        self.save_rolereact_data()

        logger.info(f"Nouveau RoleReact créé: Message ID {sent_message.id}, Rôles: {[role.name for role in valid_roles]}, MaxRoles: {maxroles}, Locked: {locked}")
        await interaction.followup.send("Message de réaction de rôle créé.", ephemeral=True)

    @rolereact.error
    async def rolereact_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("Vous n'avez pas la permission d'utiliser cette commande.", ephemeral=True)
        else:
            logger.error(f"Erreur lors de l'exécution de la commande rolereact: {error}")
            await interaction.response.send_message(f"Une erreur s'est produite : {error}", ephemeral=True)

    async def cog_load(self):
        logger.info("Chargement du cog RoleReact")
        await self.restore_rolereact_views()

    async def restore_rolereact_views(self):
        for message_id, data in self.rolereact_data.items():
            channel = self.bot.get_channel(data['channel_id'])
            if channel:
                try:
                    message = await channel.fetch_message(int(message_id))
                    roles = [discord.utils.get(channel.guild.roles, id=role_id) for role_id in data['roles']]
                    view = RoleReactView(self.bot, roles, data['maxroles'], data['locked'])
                    await message.edit(view=view)
                    logger.info(f"Vue RoleReact restaurée pour le message ID {message_id}")
                except discord.NotFound:
                    logger.warning(f"Message RoleReact non trouvé: ID {message_id}. Suppression des données.")
                    del self.rolereact_data[message_id]
                except Exception as e:
                    logger.error(f"Erreur lors de la restauration de la vue RoleReact pour le message ID {message_id}: {e}")
        self.save_rolereact_data()

class RoleReactView(discord.ui.View):
    def __init__(self, bot, roles, maxroles, locked):
        super().__init__(timeout=None)
        self.bot = bot
        self.maxroles = maxroles
        self.locked = locked
        self.roles = roles
        self.user_roles = {}

        for i, role in enumerate(roles):
            button_style = discord.ButtonStyle.primary if i % 2 == 0 else discord.ButtonStyle.danger
            self.add_item(RoleButton(role, button_style))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
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
    def __init__(self, role: discord.Role, style: discord.ButtonStyle):
        super().__init__(style=style, label=role.name, custom_id=f"rr:{role.id}")
        self.role = role

    async def callback(self, interaction: discord.Interaction):
        if self.role in interaction.user.roles:
            await interaction.user.remove_roles(self.role)
            action = "retiré"
        else:
            await interaction.user.add_roles(self.role)
            action = "attribué"
        
        logger.info(f"Rôle {action} pour l'utilisateur {interaction.user.name}: {self.role.name}")
        await interaction.response.send_message(f"Le rôle {self.role.name} vous a été {action}.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(RoleReact(bot))
