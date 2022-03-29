import discord
from discord.commands import slash_command, Option, OptionChoice
from discord.ext import commands
from discord.ui import Button, View, InputText, Modal, Select
from datetime import datetime
import json
from core.cog import DB, Check, Set
import emojis
import pandas as pd
import os

_db = DB()
_check = Check()
_set = Set()


class claimButton(Button):
    def __init__(self, label, id, disabled, emoji, style):
        super().__init__(label=label, style=eval(f"discord.ButtonStyle.{style}"), custom_id=id, disabled=disabled,
                         emoji=emoji)

    async def callback(self, interaction):
        try:
            res = await _db.get_button_data(mode="id", button_id=interaction.custom_id)
            res = list(res[0])
            check, msg = await _check.check_callback(res, interaction)
            if not check:
                embed = discord.Embed(title="Error", color=discord.Color.red())
                embed.add_field(name="Error message", value=msg, inline=False)
                await interaction.response.send_message(embeds=[embed], ephemeral=True)
                return
        except Exception as e:
            pass
        else:
            title, role_id, length = res[4], res[5], res[6]
            modal = MyModal(title=f"{title}", length=length, custom_id=interaction.custom_id)
            await interaction.response.send_modal(modal)


class setSelect(Select):
    def __int__(self, options):
        super().__init__(placeholder="Select the button name to delete...",
                         min_values=1,
                         max_values=1,
                         options=options, )
        self.set = None
        self.edit = None
        self.max = None
        self.close = False
        self.user = None
        self.export = None
        self.bot = None

    async def callback(self, interaction: discord.Interaction):
        button_id = self.values[0]
        if self.set == "edit":
            await _db.button_edit_update(button_id, self.edit)
            await interaction.response.edit_message(content=f"`Done.`", view=None)
        elif self.set == "max":
            await _db.button_max_update(button_id, self.max)
            await interaction.response.edit_message(content=f"`Done.`", view=None)
        elif self.set == "get":
            res, title = await _db.get_button_user_data(button_id, True)
            user_data = json.loads(res) if res else {}
            if str(self.user.id) in user_data:
                user_data = user_data[str(self.user.id)]
                embed = discord.Embed(title=title, color=discord.Color.blue())
                embed.set_author(name=f"{user_data['name']}#{user_data['discriminator']}", icon_url=user_data['avatar'])
                embed.add_field(name="Wallet address", value=user_data['wallet_address'], inline=False)
                await interaction.response.edit_message(embeds=[embed], view=None)
            else:
                await interaction.response.edit_message(content=f"`No data.`", view=None)
        elif self.set == "export":
            res, title = await _db.get_button_user_data(button_id, True)

            if self.export == "txt":
                user_data = json.loads(res) if res else {}
                file_name = f"{title}.txt"
                file_path = f"./data/{file_name}"

                with open(file_path, 'w', encoding='UTF-8') as f:
                    f.write("Discord ID, Wallet address, Discord User\n")
                    for key, val in user_data.items():
                        f.write(f"{key} {val['wallet_address']} {val['name']}#{val['discriminator']}\n")

            elif self.export == "json":
                user_data = json.loads(res) if res else {}
                for key in user_data.keys():
                    del user_data[key]['avatar']
                    del user_data[key]['display_name']
                file_name = f"{title}.json"
                file_path = f"./data/{file_name}"
                with open(file_path, 'w', encoding='UTF-8') as f:
                    json.dump(user_data, f, indent=4, ensure_ascii=False)

            else:
                user_data = json.loads(res) if res else {}
                res = await _set.set_json(user_data)
                file_data = pd.read_json(res).astype("str")
                if self.export == "csv":
                    file_name = f"{title}.csv"
                    file_path = f"./data/{file_name}"
                    file_data.to_csv(file_path, index=False, encoding="utf_8_sig")

                else:  # Excel
                    file_name = f"{title}.xlsx"
                    file_path = f"./data/{file_name}"
                    file_data.to_excel(file_path, index=False, freeze_panes=(1, 0))

            await interaction.response.send_message(file=discord.File(file_path, filename=file_name))
            os.remove(file_path)
        elif self.set:
            try:
                res = await _db.get_button_data(mode="id", button_id=button_id)
                res = list(res[0])
                channel = await self.bot.fetch_channel(res[9])
                msg = await channel.fetch_message(res[10])
                button = claimButton(label=res[12],
                                     id=button_id,
                                     disabled=self.close,
                                     emoji=res[13] if res[13] else None,
                                     style=res[15])
                view = View()
                view.timeout = None
                view.add_item(button)
                await _db.button_disabled_update(button_id, self.close)
                await msg.edit(view=view)
            except Exception as e:
                await interaction.response.edit_message(content=f"`Error, has the button been removed? Try again.`",
                                                        view=None)
            else:
                await interaction.response.edit_message(content=f"`Done.`", view=None)
        else:
            try:
                res = await _db.del_button(interaction.guild, button_id)
                if not res:
                    await interaction.response.edit_message(content=f"`ERROR try again.`", view=None)
                    return
            except Exception as e:
                print(e)
                await interaction.response.edit_message(content=f"`ERROR try again.`", view=None)

            else:
                await interaction.response.edit_message(
                    content="Data deleted successfully. The original button can be deleted manually.",
                    view=None)


class slelctView(View):
    def __init__(self):
        super().__init__(timeout=30)
        self.msg = None

    async def on_timeout(self):
        try:
            await self.msg.edit_original_message(content="`Time out.`", view=None)
        except Exception as e:
            pass


class MyModal(Modal):
    def __init__(self, length, *args, **kwargs):
        super().__init__(*args, **kwargs, )
        self.add_item(InputText(label="Wallet address",
                                placeholder="Enter your wallet address.",
                                style=discord.InputTextStyle.multiline,
                                min_length=length,
                                max_length=length,
                                required=True))

    async def callback(self, interaction: discord.Interaction):
        res = await _db.get_button_data(mode="id", button_id=interaction.custom_id)
        check, msg = await _check.check_callback(list(res[0]), interaction)
        if not check:
            embed = discord.Embed(title="Error", color=discord.Color.red())
            embed.add_field(name="Error message", value=msg, inline=False)
            await interaction.response.send_message(embeds=[embed], ephemeral=True)
            return

        res = await _db.get_button_user_data(interaction.custom_id)
        wallet_address = self.children[0].value
        user_data = json.loads(res) if res else {}

        user_data[interaction.user.id] = {
            "wallet_address": wallet_address,
            "name": interaction.user.name,
            "display_name": interaction.user.display_name,
            "discriminator": interaction.user.discriminator,
            "avatar": interaction.user.avatar.url
        }
        user_data = json.dumps(user_data, indent=4, ensure_ascii=False)
        await _db.update_button_user_data(interaction.custom_id, user_data)
        embed = discord.Embed(title="Success", color=discord.Color.green())
        embed.add_field(name="Wallet address", value=wallet_address, inline=False)
        await interaction.response.send_message(embeds=[embed], ephemeral=True)


class Main(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("IS OK")
        buttonsData = await _db.get_button_data()
        view = View()
        view.timeout = None
        try:
            for data in buttonsData:
                button = claimButton(label=data[12],
                                     id=data[3],
                                     disabled=True if data[7] else False,
                                     emoji=data[13] if data[13] else None,
                                     style=data[15])
                view.add_item(button)
                self.bot.add_view(view)
        except Exception as e:
            print(e)

    # 添加按鈕
    @slash_command(description="Add a submit button.")
    @commands.has_guild_permissions(manage_messages=True)
    async def add_button(self, ctx,
                         name: Option(str, required=True,
                                      description="The title name, and used as a button option, make sure it is "
                                                  "recognizable."),
                         role: Option(discord.guild.Role, required=True,
                                      description="The role required for the button click, to allow everyone select "
                                                  "@everyone."),
                         channel: Option(discord.TextChannel, required=False, default=None,
                                         description="default is the current channel."),
                         label: Option(str, required=False, default="Claim",
                                       description="The label of the button."),
                         style: Option(str, required=False, default="green",
                                       description="Button style.",
                                       choices=[
                                           OptionChoice("blue", "primary"),
                                           OptionChoice("green", "green"),
                                           OptionChoice("red", "red"),
                                           OptionChoice("grey", "secondary"),
                                       ]),
                         message: Option(str, required=False, default="",
                                         description="Text message to send, default is blank."),
                         emoji: Option(str, required=False, default=None,
                                       description="Set the emoji of the button, the default is none."),
                         allow_editing: Option(bool, required=False, default=True,
                                               description="Whether to allow "
                                                           "users to repeat submissions for editing."),
                         max_submit: Option(int, required=False, default=0,
                                            description="Set the maximum number of submissions."),
                         length: Option(int, required=False, default=42,
                                        description="The default format is Ethereum and the length is 42."),
                         disabled: Option(bool, required=False, default=False,
                                          description="Whether the button is disabled?")):

        guildButtonQuantity = await _db.get_button_quantity(ctx.guild)
        if guildButtonQuantity >= 5:
            await ctx.respond("`Quantity limit reached, please delete a button first.`", ephemeral=True)
            return
        if len(label) > 16:
            await ctx.respond("`Label characters up to 16.`", ephemeral=True)
            return
        if emoji:
            emoji_check = False
            try:
                emoji_check = True if emoji in ctx.guild.emojis else ...
                emoji_check = True if len(emojis.get(emoji)) == 1 else ...
            except Exception as e:
                pass
            await ctx.respond(f"`emoji error.`", ephemeral=True) if not emoji_check else ...

        _id = f"{ctx.guild_id}:{int(datetime.now().timestamp())}:{guildButtonQuantity + 1}"
        button = claimButton(label=label, id=_id, disabled=disabled, emoji=emoji, style=style)
        view = View()
        view.timeout = None
        view.add_item(button)
        send_channel = channel or ctx.channel
        msg = await send_channel.send(message, view=view)
        if channel:
            await ctx.respond(f"Done. Send to <#{channel.id}>", ephemeral=True)
        else:
            await ctx.respond(f"`Done.`", ephemeral=True)

        channel_id = send_channel.id
        await _db.button_add(ctx.guild_id, name, role.id, _id, length, disabled, allow_editing, channel_id, msg.id,
                             max_submit, label, emoji, style)
        await _db.update_guild_button_quantity(ctx.guild)

    # 刪除按鈕
    @slash_command(description="Delete button and data from database.")
    @commands.has_guild_permissions(manage_messages=True)
    async def del_button(self, ctx):
        buttonList = await _db.get_button_data(mode="guild", guild_id=ctx.guild_id)
        if len(buttonList) == 0:
            await ctx.respond("`No data.`", ephemeral=True)
            return
        options = []
        for data in buttonList:
            options.append(discord.SelectOption(label=data[4], value=data[3]))
        select = setSelect(options=options)
        select.set = False
        view = slelctView()
        view.add_item(select)
        view.msg = await ctx.respond("", view=view, ephemeral=True)

    # 開啟按鈕
    @slash_command(description="Enable button to allow interaction.")
    @commands.has_guild_permissions(manage_messages=True)
    async def open_button(self, ctx):
        view = await _db.set_select(ctx, setSelect, slelctView, False)
        view.msg = await ctx.respond("", view=view, ephemeral=True) if view else \
            await ctx.respond("`No closed button to open.`", ephemeral=True)

    # 關閉按鈕
    @slash_command(description="Close button disables interaction.")
    @commands.has_guild_permissions(manage_messages=True)
    async def close_button(self, ctx):
        view = await _db.set_select(ctx, setSelect, slelctView, close=True)
        view.msg = await ctx.respond("", view=view, ephemeral=True) if view else \
            await ctx.respond("`No active button to close.`", ephemeral=True)

    # 開啟編輯
    @slash_command(description="Allow duplicate submissions to edit data.")
    @commands.has_guild_permissions(manage_messages=True)
    async def open_edit(self, ctx):
        view = await _db.set_select(ctx, setSelect, slelctView, edit=True)
        view.msg = await ctx.respond("", view=view, ephemeral=True) if view else \
            await ctx.respond("`No button to close editing.`", ephemeral=True)

    # 關閉編輯close editing
    @slash_command(description="Do not allow duplicate submissions to edit data.")
    @commands.has_guild_permissions(manage_messages=True)
    async def close_edit(self, ctx):
        view = await _db.set_select(ctx, setSelect, slelctView, edit=False)
        view.msg = await ctx.respond("", view=view, ephemeral=True) if view else \
            await ctx.respond("`No button to enable editing.`", ephemeral=True)

    # 修改上限
    @slash_command(description="Modify the maximum commit limit.")
    @commands.has_guild_permissions(manage_messages=True)
    async def edit_max_submit(self, ctx, max_submit: Option(int)):
        view = await _db.set_select(ctx, setSelect, slelctView, max=max_submit)
        view.msg = await ctx.respond("", view=view, ephemeral=True) if view else \
            await ctx.respond("`No buttons to choose from.`", ephemeral=True)

    # 檢查已提交資料
    @slash_command(description="Check the submitted information.")
    async def check_data(self, ctx):
        view = await _db.set_select(ctx, setSelect, slelctView, get=ctx.user)
        view.msg = await ctx.respond("", view=view, ephemeral=True) if view else \
            await ctx.respond("`No data.`", ephemeral=True)

    # 獲取使用者提交資料
    @slash_command(description="Check the commit message for the specified user.")
    @commands.has_guild_permissions(manage_messages=True)
    async def check_user_data(self, ctx, user: Option(discord.guild.Member)):
        view = await _db.set_select(ctx, setSelect, slelctView, get=user)
        view.msg = await ctx.respond("", view=view, ephemeral=True) if view else \
            await ctx.respond("`No data.`", ephemeral=True)

    # 匯出檔案
    @slash_command(description="Export the collected data to a specified file.")
    @commands.cooldown(2, 30.0, discord.ext.commands.BucketType.user)
    @commands.has_guild_permissions(manage_messages=True)
    async def export_data(self, ctx,
                          file_type: Option(str, choices=[
                              OptionChoice("Excel", "excel"),
                              OptionChoice("csv", "csv"),
                              OptionChoice("Json", "json"),
                              OptionChoice("txt", "txt"),
                          ], description="Select the file type to export")):
        view = await _db.set_select(ctx, setSelect, slelctView, export=file_type)
        view.msg = await ctx.respond("", view=view, ephemeral=True) if view else \
            await ctx.respond("`No data.`", ephemeral=True)


def setup(bot):
    bot.add_cog(Main(bot))
