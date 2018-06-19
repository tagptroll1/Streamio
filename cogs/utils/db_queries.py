import asyncpg
import asyncio

async def create_user_account(bot, uid, gid):
    await bot.db.execute("""
            INSERT INTO users
            (id, guild_id, level, money, pet_id, twitch_name)
            VALUES($1, $2, $3, $4, $5, $6)
            ON CONFLICT(id, guild_id)
            DO NOTHING""",
        uid, gid, 1, 0, 0, "None"
    )

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

