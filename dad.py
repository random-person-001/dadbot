import random
import re
import time

import discord
from discord.ext import commands

import db

WORK_EVERY_TIME = True  # If false, will only sometimes respond with Hi, XX, I'm dad!


class Dad(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def oh_no(self, msg):
        if "oh no" in msg.content.lower() and not msg.author.bot:
            max = 294
            n = random.randint(1, max)  # inclusive on both ends
            url = "https://www.raylu.net/f/ohno/ohno{:0>3}.png".format(n)
            e = discord.Embed(title="Oh no.", url="https://webcomicname.com/")
            e.set_image(url=url)
            await msg.channel.send(embed=e)

    async def rt(self, msg):
        if msg.content.lower().startswith('rt') and not msg.author.bot:
            await msg.channel.send('rt ' + msg.content)

    async def ur_mom_is(self, msg):
        if msg.author.bot:
            return
        regex = r'\w+ is (.+)'
        wordy = re.search(regex, msg.content)
        if wordy:
            await msg.channel.send(f'Your mother is {wordy.group(1)}')

    async def hi_im_dad(self, msg):
        content = msg.content.lower()
        if len(content) > 4 and any(punct == content[-1] for punct in ('.', '?', '!', ',')):
            content = content[:-1]
        ims = ('im ', "i'm ", 'i am ')
        for im in ims:
            if content.startswith(im):
                if 'fucked' in content:
                    await msg.channel.send("Oh wow already! Just remember to be using protection!")
                else:
                    await msg.channel.send(f"Hi {content[len(im):]}, I'm dad")

    async def check_specials(self, msg):
        await self.rt(msg)
        await self.oh_no(msg)
        await self.hi_im_dad(msg)
        await self.ur_mom_is(msg)

    @commands.Cog.listener()
    async def on_message(self, msg):
        if WORK_EVERY_TIME:
            await self.check_specials(msg)
        else:
            now_minutes = int(time.time() / 60)
            if now_minutes % 10 >= 5:
                await self.check_specials(msg)
        for trigger_output in db.get_trigger_outputs_for_msg(self.bot.con, msg.content):
            await msg.channel.send(trigger_output)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def say_img(self, ctx, chan_id: int, *, msg=None):
        """upload an image directly"""
        chan = ctx.bot.get_channel(chan_id)
        img = await ctx.message.attachments[0].to_file()
        await chan.send(content=msg, file=img)


async def setup(bot):
    await bot.add_cog(Dad(bot))
