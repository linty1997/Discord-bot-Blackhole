from core.sql import SQL
from datetime import datetime
import json, discord

class DB:

    async def guild_update(self, guild, join: bool):
        nowtime = int(datetime.now().timestamp())
        db = SQL()
        sql = f'SELECT * FROM guilds WHERE id={guild.id};'
        res = db.get_one(sql)
        if res:
            if not join:
                sql = f'UPDATE guilds SET leave_time=%s, users=%s WHERE id={guild.id};'
                val = (nowtime, guild.member_count)
            else:
                sql = f'UPDATE guilds SET join_time=%s, name=%s, users=%s WHERE id={guild.id};'
                val = (nowtime, guild.name, guild.member_count)
            db.update(sql, val)
        else:
            sql = f'INSERT INTO guilds (join_time, leave_time, id, name, users, buttons) VALUES (%s, %s, %s, %s, %s, %s);'
            val = (nowtime, 0, guild.id, guild.name, guild.member_count, 0)
            db.insert(sql, val)


    async def get_button_quantity(self, guild):
        db = SQL()
        sql = f'SELECT buttons FROM guilds WHERE id={guild.id};'
        res = db.get_one(sql)
        if not res:
            await self.guild_update(guild, True)
            res = db.get_one(sql)
        try:
            res = list(res)[0]
            return res
        except:
            return False

    async def button_add(self, guild_id, name, role, id, length, disabled, edit, channel_id, msg_id, max_submit, label, emoji, style):
        disabled = 1 if disabled else 0
        edit = 1 if edit else 0
        label = label if label else None
        emoji = emoji if emoji else None
        nowtime = int(datetime.now().timestamp())
        db = SQL()
        sql = f'INSERT INTO buttons (guild, add_time, id, name, role, length, disabled, edit, channel, msg_id, max_submit, label, emoji, style) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);'
        val = (guild_id, nowtime, id, name, role, length, disabled, edit, channel_id, msg_id, max_submit, label, emoji, style)
        db.insert(sql, val)

    async def update_guild_button_quantity(self, guild, add: bool=True):
        db = SQL()
        buttons = await self.get_button_quantity(guild)
        if add:
            buttons += 1
        else:
            buttons -= 1
        sql = f'UPDATE guilds SET buttons={buttons} WHERE id={guild.id};'
        db.update(sql)


    async def get_button_data(self, mode: str=None, button_id: str=None, guild_id: int=None, disabled: bool=None,
                              edit: bool=None, max: int=None):
        db = SQL()
        if mode == "guild":
            sql = f'SELECT * FROM buttons WHERE guild={guild_id};'
        elif mode == "id":
            sql = f'SELECT * FROM buttons WHERE id="{button_id}";'
        elif mode == "status":
            if disabled != None:
                disabled = 0 if disabled else 1
                sql = f'SELECT * FROM buttons WHERE guild="{guild_id}" AND disabled={disabled};'
            elif edit != None:
                edit = 0 if edit else 1
                sql = f'SELECT * FROM buttons WHERE guild="{guild_id}" AND edit={edit};'
            else:
                sql = f'SELECT * FROM buttons WHERE guild={guild_id};'
        else:
            sql = f'SELECT * FROM buttons;'

        res = db.get_all(sql)
        return res

    async def button_disabled_update(self, button_id: str, disabled: bool):
        db = SQL()
        disabled = 1 if disabled else 0
        sql = f'UPDATE buttons SET disabled={disabled} WHERE id="{button_id}";'
        db.update(sql)

    async def button_edit_update(self, button_id: str, edit: bool):
        db = SQL()
        edit = 1 if edit else 0
        sql = f'UPDATE buttons SET edit={edit} WHERE id="{button_id}";'
        db.update(sql)

    async def button_max_update(self, button_id: str, max: int):
        db = SQL()
        sql = f'UPDATE buttons SET max_submit={max} WHERE id="{button_id}";'
        db.update(sql)

    async def del_button(self, guild, button_id: str):
        db = SQL()
        sql = f'DELETE FROM buttons WHERE id="{button_id}";'
        try:
            db.delete(sql)
            await self.update_guild_button_quantity(guild, False)
        except:
            return False
        else:
            return True

    async def set_select(self, ctx, setSelect, slelctView, close=None, edit=None, max=None, get :discord.Member=None, export=None):
        db = SQL()
        buttonList = await self.get_button_data(mode="status", guild_id=ctx.guild_id, disabled=close, edit=edit)
        if buttonList == ():
            return False
        options = []
        for data in buttonList:
            options.append(discord.SelectOption(label=data[4], value=data[3]))
        select = setSelect(options=options)
        select.bot = ctx.bot
        if edit != None:
            select.set = "edit"
            select.edit = edit
        elif max != None:
            select.set = "max"
            select.max = max
        elif get != None:
            select.set = "get"
            select.user = get
        elif export != None:
            select.set = "export"
            select.export = export
        else:
            select.set = True
            select.close = close
        view = slelctView()
        view.add_item(select)
        return view

    async def get_button_user_data(self, button_id: str, name: bool=False):
        db = SQL()
        sql = f'SELECT data, name FROM buttons WHERE id="{button_id}";'
        res = db.get_one(sql)
        if name:
            return res[0], res[1]
        else:
            return res[0]

    async def update_button_user_data(self, button_id: str, user_data: json):
        db = SQL()
        sql = f"UPDATE buttons SET data=( %s ) WHERE id='{button_id}';"
        val = user_data
        db.update(sql, val)


class Check:
    async def check_callback(self, data, interaction):
        user_data = {} if not data[14] else json.loads(data[14])
        # 最大提交
        if data[11] != 0:
            if len(user_data) >= data[11] and str(interaction.user.id) not in user_data:
                return False, "to reach the maximum commit limit."
        # 是否允許編輯
        if data[8] == 0:
            if str(interaction.user.id) in user_data:
                return False, "Duplicate submissions or editing of content are prohibited."

        # 是否 close
        if data[7] == 1:
            return False, "This form has been closed."

        # 檢查 role
        role = interaction.guild.get_role(data[5])
        userRoles = interaction.user.roles
        if role not in userRoles:
            return False, "You do not have permission."

        return True, "ok"

class Set:
    async def set_json(self, data: dict):
        user_id = []
        user_name = []
        address = []
        for key, val in data.items():
            user_id.append(key)
            user_name.append(f"{val['name']}#{val['discriminator']}")
            address.append(val['wallet_address'])
        user_data = {
            "Discord id": user_id,
            "Discord user": user_name,
            "Wallet address": address
        }
        return json.dumps(user_data, indent=4, ensure_ascii=False)


