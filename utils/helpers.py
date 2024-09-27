# utils/helpers.py
import discord
from discord.ext import commands
import asyncio

async def send_to_modlogs(bot, modlogs_channel_id, embed):
    modlogs_channel = bot.get_channel(modlogs_channel_id)
    if modlogs_channel:
        await modlogs_channel.send(embed=embed)
    else:
        print(f"Canal modlogs avec l'ID {modlogs_channel_id} non trouvé.")

def create_mod_embed(action, moderator, user, reason=None):
    embed = discord.Embed(title=f"Action de modération : {action}", color=discord.Color.red())
    embed.add_field(name="Modérateur", value=moderator.mention, inline=False)
    embed.add_field(name="Utilisateur", value=user.mention, inline=False)
    if reason:
        embed.add_field(name="Raison", value=reason, inline=False)
    embed.set_footer(text=f"ID de l'utilisateur: {user.id}")
    return embed
