import discord
from discord import app_commands
from discord.ext import commands
import datetime

TOKEN = "TON_TOKEN_ICI"

intents = discord.Intents.default()
intents.guilds = True
intents.members = True

class MonBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.warns = {}

    async def setup_hook(self):
        await self.tree.sync()

bot = MonBot()

@bot.event
async def on_ready():
    print(f"✅ Connecté en tant que {bot.user}")

async def send_log(guild: discord.Guild, message: str):
    log_channel = discord.utils.get(guild.text_channels, name="logs")
    if log_channel:
        await log_channel.send(message)

@bot.tree.command(name="ban", description="Bannir un membre")
async def ban(interaction: discord.Interaction, user: discord.Member, reason: str = "Aucune raison"):
    if not interaction.user.guild_permissions.ban_members:
        await interaction.response.send_message("Tu n'as pas la permission de bannir.", ephemeral=True)
        return
    await user.ban(reason=reason)
    await interaction.response.send_message(f"{user} a été banni. Raison: {reason}")
    await send_log(interaction.guild, f"🔨 {user} a été **banni** par {interaction.user} | Raison: {reason}")

@bot.tree.command(name="kick", description="Expulser un membre")
async def kick(interaction: discord.Interaction, user: discord.Member, reason: str = "Aucune raison"):
    if not interaction.user.guild_permissions.kick_members:
        await interaction.response.send_message("Tu n'as pas la permission d'expulser.", ephemeral=True)
        return
    await user.kick(reason=reason)
    await interaction.response.send_message(f"{user} a été expulsé. Raison: {reason}")
    await send_log(interaction.guild, f"👢 {user} a été **expulsé** par {interaction.user} | Raison: {reason}")

@bot.tree.command(name="clear", description="Supprime des messages")
async def clear(interaction: discord.Interaction, amount: int):
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message("Tu n'as pas la permission.", ephemeral=True)
        return
    deleted = await interaction.channel.purge(limit=amount)
    await interaction.response.send_message(f"{len(deleted)} messages supprimés.", ephemeral=True)
    await send_log(interaction.guild, f"🧹 {interaction.user} a supprimé {len(deleted)} messages dans #{interaction.channel.name}")

@bot.tree.command(name="mute", description="Rend un membre muet")
async def mute(interaction: discord.Interaction, user: discord.Member, reason: str = "Aucune raison"):
    if not interaction.user.guild_permissions.mute_members:
        await interaction.response.send_message("Tu n'as pas la permission.", ephemeral=True)
        return

    muted_role = discord.utils.get(interaction.guild.roles, name="Muted")
    if not muted_role:
        muted_role = await interaction.guild.create_role(name="Muted")
        for channel in interaction.guild.channels:
            await channel.set_permissions(muted_role, speak=False, send_messages=False)

    await user.add_roles(muted_role, reason=reason)
    await interaction.response.send_message(f"{user} a été rendu muet. Raison: {reason}")
    await send_log(interaction.guild, f"🔇 {user} a été **muté** par {interaction.user} | Raison: {reason}")

@bot.tree.command(name="warn", description="Avertir un membre")
async def warn(interaction: discord.Interaction, user: discord.Member, reason: str = "Aucune raison"):
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message("Tu n'as pas la permission.", ephemeral=True)
        return
    if user.id not in bot.warns:
        bot.warns[user.id] = []
    bot.warns[user.id].append((reason, datetime.datetime.now()))
    await interaction.response.send_message(f"{user} a été averti. Raison: {reason}")
    await send_log(interaction.guild, f"⚠️ {user} a été **averti** par {interaction.user} | Raison: {reason}")

@bot.tree.command(name="help", description="Affiche les commandes")
async def help_cmd(interaction: discord.Interaction):
    msg = (
        "**📘 Commandes disponibles :**\n"
        "/ban [membre] [raison] - Bannir un membre\n"
        "/kick [membre] [raison] - Expulser un membre\n"
        "/clear [nombre] - Supprimer des messages\n"
        "/mute [membre] [raison] - Rendre muet\n"
        "/warn [membre] [raison] - Avertir\n"
        "/help - Cette aide\n"
    )
    await interaction.response.send_message(msg, ephemeral=True)

bot.run(TOKEN)