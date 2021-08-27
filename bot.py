import asyncio
import json
import os
import discord
from discord.ext import commands

bot = commands.Bot(command_prefix="!", help_command=None)


@bot.event
async def on_ready():
    await (await bot.application_info()).owner.send("I Live!")


@bot.command()
@commands.is_owner()
async def emojicode(ctx, emoji):
    await ctx.send(emoji_to_code(emoji))


@bot.command()
@commands.is_owner()
async def testemojicode(ctx, ecode):
    await ctx.send(code_to_emoji(ecode))


@bot.command()
async def embed(ctx):
    buttons = [code_to_emoji(x) for x in bot.help_pages.keys() if x]
    # the emoji for selection are saved as codes, but discord wants the emoji
    msg = await ctx.send(embed=discord.Embed(**bot.help_pages[bot.start_at]))
    for button in buttons:
        await msg.add_reaction(button)
    while True:
        try:
            reaction, user = await bot.wait_for(
                "reaction_add",
                check=lambda _, u: u == ctx.author,
                # only interact with the person calling the command
                timeout=60.0,  # we wait for one minute after last reaction,
                # could also be in the config if needed
            )
        except asyncio.TimeoutError:
            await ctx.message.delete()  # delete the message opening the dialogue
            return await msg.delete()  # delete the embed message
        else:
            codepoint = emoji_to_code(reaction.emoji)  # discord only sends the unicode
            if (
                codepoint in bot.help_pages
            ):  # so we get the codepoint and use that to select
                # the wanted message and change the embed
                await msg.edit(embed=discord.Embed(**bot.help_pages[codepoint]))
            await msg.remove_reaction(reaction.emoji, ctx.author)  # reset the reaction


def emoji_to_code(emoji):
    """takes an emoji and makes it into codepoints, commaseparated string"""
    return ",".join([hex(ord(e))[2:] for e in emoji])


def code_to_emoji(code):
    """takes the output of emoji_to_code and remakes the emoji"""
    return "".join(chr(int(e, base=16)) for e in code.split(","))


if __name__ == "__main__":
    with open(os.path.expanduser("embed_pager.discord"), "r") as tokenfile:
        TOKEN = tokenfile.read().strip() # token file is literally just the token inside a file
    with open("embed_pager.json", "r") as configfile:
        config = json.loads(configfile.read().strip())
    bot.help_pages = config["pages"]
    bot.start_at = config["start"]
    bot.run(TOKEN)
