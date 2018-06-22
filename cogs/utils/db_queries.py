import asyncpg
import asyncio

from Cryptodome.Cipher import AES
from Cryptodome.Util import Padding

async def create_user_account(bot, uid, gid):
    await bot.db.execute("""
            INSERT INTO users
            (id, guild_id, level, money, pet_id, twitch_name)
            VALUES($1, $2, $3, $4, $5, $6)
            ON CONFLICT(id, guild_id)
            DO NOTHING""",
        uid, gid, 1, 0, 0, "None"
    )

async def dump_log(bot):
    logs = bot.msg_log
    query = """
        INSERT INTO messages
        (msg_id, author_id, channel_id, guild_id, content, date)
        VALUES($1, $2, $3, $4, $5, $6)
        ON CONFLICT(msg_id, author_id)
        DO NOTHING
            """
    args = []

    for log in reversed(logs):
        msg = log["msg"]
        if not msg:
            msg = "<Media transmitted>"
        args.append((log["id"], log["author"], log["channel"], 
                        log["guild"], msg, log["date"]))

    async with bot.db.acquire() as connection:
        async with connection.transaction():
            await bot.db.executemany(query, args)
    bot.msg_log = []

async def get_messages(bot, ctx, query, *args):
    rows = await bot.db.fetch(query, *args)

    new_rows = []
    for row in reversed(rows):
        msgid, authorid, channelid, _, content, date = row

        # Prevent bot logs
        if authorid == bot.user.id:
            continue

        guild = ctx.guild
        channel = None
        msg = None
        author = None
        
        try:
            channel = guild.get_channel(channelid)
            msg = await channel.get_message(msgid)
            author = guild.get_member(authorid)
        except Exception as e:
            bot.logger.exception(e)

        form_date = date.strftime("%d/%m/%y %H:%M")

        # If we dont find the message, decrypt content from query
        if msg:
            content = msg.content
        else:
            aes = AES.new(bot.secrets.ENCRYPT_KEY, AES.MODE_ECB)
            content = aes.decrypt(content)
            content = Padding.unpad(content, 16).decode("utf-8")

        new_rows.append((msg, author, channel, guild, content, form_date))

    return new_rows


async def give_money(bot, amount, uid, gid):
    if amount < 0:
        return False
    elif amount > 2_000_000_000:
        return False
    
    try:
        await bot.db.execute("""
            UPDATE users
                SET money = money + $1
            WHERE id = $2 AND guild_id = $3;""",
            amount, uid, gid)
    except Exception:
        print("Couldn't update users money")
        try:
            await create_user_account(bot, uid, gid)
        except Exception:
            print("Failed to create account")
        return False
    return True

async def take_money(bot, amount, uid, gid):
    if amount < 0:
        return False
    elif amount > 2_000_000_000:
        return False
    money = await bot.db.fetchrow("""
        SELECT money FROM users
        WHERE id = $1 AND guild_id = $2;""",
        uid, gid)

    if not money:
        await create_user_account(bot, uid, gid)

    if money["money"] < amount:
        await bot.db.execute("""
        UPDATE users
            SET money = 0
        WHERE id = $1 AND guild_id = $2;""",
        uid, gid)
        return False
    else:
        await bot.db.execute("""
            UPDATE users
                SET money = money - $1
            WHERE id = $2 AND guild_id = $3;""",
            amount, uid, gid)
    
    return True

async def set_money(bot, amount, uid, gid):
    if amount < 0:
        return False
    elif amount > 2_000_000_000:
        return False

    await bot.db.execute("""
        UPDATE users
            SET money = $1
        WHERE id = $2 AND guild_id = $3;""",
        amount, uid, gid)

    return True

async def transfer_money(bot, amount, fid, tid, gid):
    if amount < 0:
        return False
    elif amount > 2_000_000_000:
        return False

    await bot.db.execute("""
        UPDATE users
            SET money = CASE id
                WHEN $2 THEN money - $1
                WHEN $3 THEN money + $1
            END
        WHERE guild_id = $4
            AND (id = $2 OR id = $3)
        """,
        amount, fid, tid, gid)

    return True

