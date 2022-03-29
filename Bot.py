import os
import discord
from discord.ext import commands
from core.cog import DB

_db = DB()

##############################

token = ''
bot = discord.Bot()

for filename in os.listdir('./cmds'):
    if filename.endswith('.py'):
        bot.load_extension(f'cmds.{filename[:-3]}')


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(name=f"👀 {len(bot.guilds)} Servers.",
                                                        type=discord.ActivityType.watching))
    print(f"機器人已上線 ID : {bot.user}")


@bot.event
async def shutdown():
    print("正在關閉與 Discord 的連結...")
    await bot.close()


@bot.event
async def close():
    print("使用鍵盤中斷連結...")
    await shutdown()


@bot.event
async def on_guild_join(guild):
    await bot.change_presence(activity=discord.Activity(name=f"👀 {len(bot.guilds)} Servers.",
                                                        type=discord.ActivityType.watching))
    await _db.guild_update(guild, True)


@bot.event
async def on_guild_remove(guild):
    await bot.change_presence(activity=discord.Activity(name=f"👀 {len(bot.guilds)} Servers.",
                                                        type=discord.ActivityType.watching))
    await _db.guild_update(guild, False)


@bot.event
async def on_error(event, *args, **kwargs):
    raise event


@bot.event
async def on_application_command_error(ctx, event):
    interaction = ctx.interaction
    try:
        if isinstance(event, discord.ext.commands.CommandOnCooldown):
            await interaction.response.send_message(f"{event}", ephemeral=True)
            return
        if isinstance(event, discord.ext.commands.MissingPermissions):
            await interaction.response.send_message(f"{event}", ephemeral=True)
            return
        if isinstance(event, discord.ext.commands.MissingRole):
            await interaction.response.send_message(f"{event}", ephemeral=True)
            return
        if isinstance(event, AttributeError):
            return
        if isinstance(event, TypeError):
            return

        await interaction.response.send_message(f"An error occurred, please try again.", ephemeral=True)

    except Exception as e:
        pass

    raise event


@bot.event
async def on_resumed():
    print("機器人已恢復.")


@bot.event
async def on_disconnect():
    print("機器人斷開連結.")


@bot.slash_command(guild_ids=[])
@commands.has_role()
async def reload(ctx, extension):
    bot.reload_extension(f"cmds.{extension}")
    await ctx.response.send_message(f"已重新載入 {extension}", ephemeral=True)


@bot.slash_command(guild_ids=[])
@commands.has_role()
async def load(self, ctx, extension):
    self.bot.load_extension(f"cmds.{extension}")
    await ctx.response.send_message(f"已載入 {extension} 模組.", ephemeral=True)


@bot.slash_command(guild_ids=[])
@commands.has_role()
async def unload(self, ctx, extension):
    self.bot.unload_extension(f"cmds.{extension}")
    await ctx.response.send_message(f"已卸載 {extension} 模組.", ephemeral=True)


bot.run(token)
