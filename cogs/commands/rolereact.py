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

        buttons = []
        for i, role in enumerate(valid_roles):
            style = discord.ButtonStyle.primary if i % 2 == 0 else discord.ButtonStyle.danger
            buttons.append({"type": 2, "style": style.value, "label": role.name, "custom_id": f"rolereact:{role.id}"})

        sent_message = await interaction.channel.send(embed=embed, components=[{"type": 1, "components": buttons}])

        self.rolereact_data[str(sent_message.id)] = {
            'roles': [role.id for role in valid_roles],
            'maxroles': maxroles,
            'locked': locked,
            'channel_id': interaction.channel_id
        }
        self.save_rolereact_data()

        logger.info(f"Nouveau RoleReact créé: Message ID {sent_message.id}, Rôles: {[role.name for role in valid_roles]}, MaxRoles: {maxroles}, Locked: {locked}")
        await interaction.followup.send("Message de réaction de rôle créé.", ephemeral=True)

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.type == discord.InteractionType.component:
            custom_id = interaction.data['custom_id']
            if custom_id.startswith("rolereact:"):
                await self.handle_rolereact(interaction)

    async def handle_rolereact(self, interaction: discord.Interaction):
        message_id = str(interaction.message.id)
        if message_id not in self.rolereact_data:
            return

        data = self.rolereact_data[message_id]
        role_id = int(interaction.data['custom_id'].split(':')[1])
        role = interaction.guild.get_role(role_id)

        if not role:
            await interaction.response.send_message("Le rôle sélectionné n'existe plus.", ephemeral=True)
            return

        if data['locked'] and any(r.id in data['roles'] for r in interaction.user.roles):
            await interaction.response.send_message("Vous avez déjà sélectionné un rôle et ne pouvez plus le changer.", ephemeral=True)
            return

        user_roles = set(role.id for role in interaction.user.roles if role.id in data['roles'])

        if role_id in user_roles:
            await interaction.user.remove_roles(role)
            user_roles.remove(role_id)
            action = "retiré"
        else:
            if data['maxroles'] > 0 and len(user_roles) >= data['maxroles']:
                await interaction.response.send_message(f"Vous ne pouvez pas sélectionner plus de {data['maxroles']} rôles.", ephemeral=True)
                return
            await interaction.user.add_roles(role)
            user_roles.add(role_id)
            action = "attribué"

        logger.info(f"Rôle {action} pour l'utilisateur {interaction.user.name}: {role.name}")
        await interaction.response.send_message(f"Le rôle {role.name} vous a été {action}.", ephemeral=True)

    @rolereact.error
    async def rolereact_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("Vous n'avez pas la permission d'utiliser cette commande.", ephemeral=True)
        else:
            logger.error(f"Erreur lors de l'exécution de la commande rolereact: {error}")
            await interaction.response.send_message(f"Une erreur s'est produite : {error}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(RoleReact(bot))
