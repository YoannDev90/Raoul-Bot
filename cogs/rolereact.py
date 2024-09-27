# cogs/rolereact.py
import discord
from discord.ext import commands
from discord import app_commands
from utils.logger import setup_logger
from utils.helpers import send_to_modlogs, create_mod_embed

logger = setup_logger('rolereact', 'logs/rolereact.log')

class RoleReact(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="rolereact", description="Crée un embed avec des boutons pour ajouter des rôles")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def rolereact(self, interaction: discord.Interaction, titre: str, roles: str, maxroles: int = 0, ischangeable: bool = True):
class PersistentView(discord.ui.View):
    def __init__(self, max_roles: int = 0, is_changeable: bool = True, add_remove: Literal["add", "remove", "both"] = "both"):
        super().__init__(timeout=None)
        self.max_roles = max_roles
        self.is_changeable = is_changeable
        self.add_remove = add_remove

async def setup_rolereact(bot):
    @bot.tree.command(name="rolereact", description="Crée un embed avec des boutons pour ajouter des rôles")
    @discord.app_commands.describe(
        titre="Le titre de l'embed",
        roles="Les rôles à inclure dans les boutons",
        maxroles="Nombre maximum de rôles sélectionnables (0 pour illimité, 1 pour un seul rôle)",
        ischangeable="Les rôles peuvent-ils être changés après sélection",
        add_remove="Mode d'ajout/retrait des rôles"
    )
    async def role_react(
        interaction: discord.Interaction,
        titre: str,
        roles: str,
        maxroles: int = 0,
        ischangeable: bool = True,
        add_remove: Literal["add", "remove", "both"] = "both"
    ):
        try:
            role_ids = [int(role_id.strip('<@&>')) for role_id in roles.split()]
            guild_roles = interaction.guild.roles
            selected_roles = [role for role in guild_roles if role.id in role_ids]

            embed = discord.Embed(title=titre, description="Cliquez sur un bouton pour obtenir le rôle correspondant.", color=discord.Color.green())
            view = PersistentView(max_roles=maxroles, is_changeable=ischangeable, add_remove=add_remove)

            for role in reversed(selected_roles):
                button = discord.ui.Button(label=role.name, style=discord.ButtonStyle.primary, custom_id=f"role_button:{role.id}")
                view.add_item(button)

            await interaction.response.send_message(embed=embed, view=view)
            logger.info(f"Embed de réaction de rôle créé par {interaction.user}")
        except Exception as e:
            logger.error(f"Erreur lors de la création de l'embed avec les rôles: {e}")
            await interaction.response.send_message("Une erreur est survenue lors de la création de l'embed.", ephemeral=True)

    @bot.tree.command(name="updaterolereact", description="Met à jour un embed de réaction de rôle existant")
    @discord.app_commands.describe(
        message_id="L'ID du message de l'embed à mettre à jour",
        titre="Le nouveau titre de l'embed (optionnel)",
        roles_ajouter="Les rôles à ajouter (optionnel)",
        roles_enlever="Les rôles à enlever (optionnel)",
        maxroles="Nouveau nombre maximum de rôles sélectionnables (optionnel)",
        ischangeable="Les rôles peuvent-ils être changés après sélection (optionnel)",
        add_remove="Mode d'ajout/retrait des rôles (optionnel)"
    )
    async def update_role_react(
        interaction: discord.Interaction, 
        message_id: str,
        titre: Optional[str] = None,
        roles_ajouter: Optional[str] = None,
        roles_enlever: Optional[str] = None,
        maxroles: Optional[int] = None,
        ischangeable: Optional[bool] = None,
        add_remove: Optional[Literal["add", "remove", "both"]] = None
    ):
        try:
            if not any([titre, roles_ajouter, roles_enlever, maxroles is not None, ischangeable is not None, add_remove]):
                await interaction.response.send_message("Vous devez spécifier au moins une modification.", ephemeral=True)
                return

            channel = interaction.channel
            message = await channel.fetch_message(int(message_id))

            if not message.embeds:
                await interaction.response.send_message("Le message spécifié ne contient pas d'embed.", ephemeral=True)
                return

            embed = message.embeds[0]
            old_view = discord.ui.View.from_message(message)
            new_max_roles = maxroles if maxroles is not None else getattr(old_view, 'max_roles', 0)
            new_is_changeable = ischangeable if ischangeable is not None else getattr(old_view, 'is_changeable', True)
            new_add_remove = add_remove if add_remove is not None else getattr(old_view, 'add_remove', "both")
            view = PersistentView(max_roles=new_max_roles, is_changeable=new_is_changeable, add_remove=new_add_remove)

            if titre:
                embed.title = titre

            # Récupérer les rôles existants
            existing_role_ids = [int(item.custom_id.split(':')[1]) for item in old_view.children if isinstance(item, discord.ui.Button)]

            # Ajouter les nouveaux rôles
            if roles_ajouter:
                new_role_ids = [int(role_id.strip('<@&>')) for role_id in roles_ajouter.split()]
                existing_role_ids.extend(new_role_ids)

            # Enlever les rôles spécifiés
            if roles_enlever:
                remove_role_ids = [int(role_id.strip('<@&>')) for role_id in roles_enlever.split()]
                existing_role_ids = [role_id for role_id in existing_role_ids if role_id not in remove_role_ids]

            # Créer les boutons pour tous les rôles
            for role_id in existing_role_ids:
                role = interaction.guild.get_role(role_id)
                if role:
                    button = discord.ui.Button(label=role.name, style=discord.ButtonStyle.primary, custom_id=f"role_button:{role.id}")
                    view.add_item(button)

            # Mettre à jour le message
            await message.edit(embed=embed, view=view)
            await interaction.response.send_message("L'embed de réaction de rôle a été mis à jour avec succès.", ephemeral=True)
            logger.info(f"Embed de réaction de rôle mis à jour par {interaction.user}")

        except discord.errors.NotFound:
            await interaction.response.send_message("Le message spécifié n'a pas été trouvé.", ephemeral=True)
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour de l'embed de réaction de rôle: {e}")
            await interaction.response.send_message("Une erreur est survenue lors de la mise à jour de l'embed.", ephemeral=True)

@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type == discord.InteractionType.component:
        custom_id = interaction.data["custom_id"]
        if custom_id.startswith("role_button:"):
            role_id = int(custom_id.split(":")[1])
            role = interaction.guild.get_role(role_id)
            if role is None:
                await interaction.response.send_message("Rôle non trouvé.", ephemeral=True)
                return

            view = discord.ui.View.from_message(interaction.message)
            max_roles = getattr(view, 'max_roles', 0)
            is_changeable = getattr(view, 'is_changeable', True)
            add_remove = getattr(view, 'add_remove', "both")

            try:
                if role in interaction.user.roles:
                    if not is_changeable or add_remove == "add":
                        await interaction.response.send_message(f"Vous ne pouvez pas retirer le rôle {role.name}.", ephemeral=True)
                        return
                    await interaction.user.remove_roles(role)
                    await interaction.response.send_message(f"Le rôle {role.name} a été retiré.", ephemeral=True)
                else:
                    if add_remove == "remove":
                        await interaction.response.send_message(f"Vous ne pouvez pas ajouter le rôle {role.name}.", ephemeral=True)
                        return
                    
                    current_roles = [r for r in interaction.user.roles if r.id in [int(item.custom_id.split(':')[1]) for item in view.children]]
                    
                    if max_roles > 0 and len(current_roles) >= max_roles:
                        if max_roles == 1:
                            # Retirer l'ancien rôle et ajouter le nouveau
                            await interaction.user.remove_roles(*current_roles)
                        else:
                            await interaction.response.send_message(f"Vous avez atteint la limite de {max_roles} rôles.", ephemeral=True)
                            return
                    
                    await interaction.user.add_roles(role)
                    await interaction.response.send_message(f"Le rôle {role.name} a été ajouté.", ephemeral=True)
            except discord.errors.Forbidden:
                await interaction.response.send_message("Je n'ai pas la permission de gérer ce rôle.", ephemeral=True)
            except Exception as e:
                logger.error(f"Erreur lors de l'interaction avec le bouton pour le rôle {role.name}: {e}")
                await interaction.response.send_message(f"Une erreur est survenue lors de la gestion du rôle {role.name}.", ephemeral=True)

    # Assurez-vous d'ajouter cette ligne pour que les boutons persistent après un redémarrage
    bot.add_view(PersistentView())

    logger.info("Module rolereact configuré")

        logger.info(f"Embed de réaction de rôle créé par {interaction.user}")
        
        embed = create_mod_embed("Création de RoleReact", interaction.user, interaction.user, f"Titre: {titre}, Rôles: {roles}")
        await send_to_modlogs(self.bot, self.bot.modlogs_channel_id, embed)

async def setup(bot):
    await bot.add_cog(RoleReact(bot))
