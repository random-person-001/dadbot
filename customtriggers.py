import asyncio

from discord.ext import commands

"""
DB SCHEMA

The text of every message is checked against the INPUTS table. If any matches are found, 
the trigger_id is dug up. The popularity field is incremented, and an appropriate output
is chosen and sent.

======= TABLE OUTPUTS ========
PRIMARY KEY INT output_id - internal use for this entry
INT trigger_id - which trigger this corresponds to
STRING text - what text to output
INT weight - an int weight to attach to this output. Allows some outputs to be sent more often than others.

======= TABLE INPUTS =========
PRIMARY KEY INT input_id - internal use for this entry
INT trigger_id - which trigger this corresponds to
STRING text - what text input
BOOL regex DEFAULT FALSE - whether to treat the trigger strings as regex
BOOL case_sensitive DEFAULT FALSE - whether to only match same-case with the trigger strings (if not regex)

======= TABLE MAIN =========
PRIMARY KEY INT trigger_id - internal use for this entry
STRING name - human readable reference name for this entry
INT popularity DEFAULT 0 - times this has been triggered

"""

"""Woo"""


class Triggered(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        # db connection should be inherited from the setup_hook in other code.

    """Show info about a trigger"""

    async def info(self, ctx):
        pass

    """Delete a trigger. It should call the info command as it goes out, just in case"""

    async def delete(self, ctx):
        pass

    """Edit a trigger."""

    async def edit(self, ctx):
        # can edit indexed name,
        # the probability of output,
        # add or remove output options
        # add or remove trigger phrases
        pass

    """Helper method to wait for the command invoker to write something else and return it"""

    async def wait_for_reply(self, ctx):
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            msg = await ctx.bot.wait_for('message', timeout=120, check=check)
        except asyncio.TimeoutError:
            await ctx.send("Wow leaving me on read like that. Ig I'll walk away from this too then.")
            return None
        return msg

    """Create a new trigger. Alias to "create" """

    async def add(self, ctx):
        # todo: rehost images and gifs

        # first get the image/gif
        await ctx.send("Please paste some text.")
        output = await self.wait_for_reply(ctx)
        if not output:
            return
        if not len(output.content):
            await ctx.send("try again but u gotta have some text. I am too lazy to recognize attachments rn")
            return

        # now get word to trigger on
        await ctx.send("Aight bro gimme something that should trigger this.")
        msg = await self.wait_for_reply(ctx)
        if not msg:
            return
        trigger = msg.content

        # now get name for index
        name = trigger.lower().replace(" ", "-").replace(".", "-")
        if len(name) > 20:
            name = name[:20]
        await ctx.send(f"Is `{name}` ok to refer to this by? If yes, type y, or else your preferred name instead")
        msg = await self.wait_for_reply(ctx)
        if not msg:
            return
        if msg.content.lower() != "y" and len(msg.content) > 2:
            name = msg.content.lower()

        # Yay!
        print(name)
        print(trigger)
        print(output)

    @commands.command()
    async def uhh(self, ctx):
        await ctx.send("uh yeah this works ig...")


async def setup(bot):
    await bot.add_cog(Triggered(bot))
