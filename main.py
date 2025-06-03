import discord
from discord.ext import commands
from discord.utils import get
import asyncio
import datetime
import platform
from keep_alive import keep_alive
import os

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)
warns = {}

@bot.event
async def on_ready():
    print(f"✅ BAF connecté en tant que {bot.user}")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"🧹 {amount} messages supprimés.", delete_after=5)

@bot.command()
@commands.has_permissions(kick_members=True)
async def warn(ctx, member: discord.Member, *, reason="Pas de raison fournie"):
    warns.setdefault(member.id, []).append(reason)
    await ctx.send(f"⚠️ {member.mention} a été averti pour : {reason}")

@bot.command()
async def warnlist(ctx, member: discord.Member):
    reasons = warns.get(member.id, [])
    if reasons:
        await ctx.send(f"📛 Avertissements de {member.name} :\n" + "\n".join([f"- {r}" for r in reasons]))
    else:
        await ctx.send(f"✅ {member.name} n'a aucun avertissement.")

@bot.command()
@commands.has_permissions(kick_members=True)
async def unwarn(ctx, member: discord.Member, index: int = -1):
    if member.id in warns and warns[member.id]:
        try:
            removed = warns[member.id].pop(index)
            await ctx.send(f"✅ Avertissement retiré : {removed}")
        except IndexError:
            await ctx.send("❌ Index invalide.")
    else:
        await ctx.send("❌ Aucun avertissement à retirer.")

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f"🔨 {member.mention} a été banni. Raison : {reason or 'Non spécifiée'}")

@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, *, user):
    banned_users = await ctx.guild.bans()
    name, discriminator = user.split('#')
    for entry in banned_users:
        if (entry.user.name, entry.user.discriminator) == (name, discriminator):
            await ctx.guild.unban(entry.user)
            await ctx.send(f"✅ {user} a été débanni.")
            return
    await ctx.send("❌ Utilisateur non trouvé.")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member, duration: int = 60):
    role = get(ctx.guild.roles, name="Muted")
    if not role:
        role = await ctx.guild.create_role(name="Muted")
        for channel in ctx.guild.channels:
            await channel.set_permissions(role, send_messages=False, speak=False)
    await member.add_roles(role)
    await ctx.send(f"🔇 {member.mention} a été mute pour {duration} secondes.")
    await asyncio.sleep(duration)
    await member.remove_roles(role)
    await ctx.send(f"🔊 {member.mention} a été unmute automatiquement.")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, member: discord.Member):
    role = get(ctx.guild.roles, name="Muted")
    if role in member.roles:
        await member.remove_roles(role)
        await ctx.send(f"🔊 {member.mention} a été unmute.")
    else:
        await ctx.send("❌ Ce membre n'est pas mute.")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def lock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send("🔒 Ce salon est maintenant verrouillé.")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def unlock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
    await ctx.send("🔓 Ce salon est maintenant déverrouillé.")

@bot.command()
async def profil(ctx, member: discord.Member = None):
    member = member or ctx.author
    nb_warns = len(warns.get(member.id, []))
    await ctx.send(f"👤 Profil de {member.name} :\n- Avertissements : {nb_warns}")

@bot.command()
async def help(ctx):
    embed = discord.Embed(title="📚 Commandes de BAF", color=discord.Color.blue())
    embed.add_field(name="Modération", value="`clear`, `warn`, `warnlist`, `unwarn`, `ban`, `unban`, `mute`, `unmute`, `lock`, `unlock`, `profil`", inline=False)
    embed.add_field(name="Utilitaires", value="`help`, `mods`, `botinfo`", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def mods(ctx):
    await ctx.send("🛠️ Commandes de modération :\n`!clear`, `!warn`, `!warnlist`, `!unwarn`, `!ban`, `!unban`, `!mute`, `!unmute`, `!lock`, `!unlock`, `!profil`")

@bot.command()
async def botinfo(ctx):
    embed = discord.Embed(title="ℹ️ Infos sur BAF", color=discord.Color.green())
    embed.add_field(name="Nom", value=bot.user.name)
    embed.add_field(name="ID", value=bot.user.id)
    embed.add_field(name="Serveurs", value=len(bot.guilds))
    embed.add_field(name="Python", value=platform.python_version())
    embed.add_field(name="discord.py", value=discord.__version__)
    embed.set_footer(text="Bot de modération BAF")
    await ctx.send(embed=embed)

keep_alive()
bot.run(os.getenv("DISCORD_TOKEN"))
