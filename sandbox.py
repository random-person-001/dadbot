import discord
from discord import app_commands
from discord.ext import commands

import db
import modals


class Sandy(commands.GroupCog, name="trigger"):
    def __init__(self, bot) -> None:
        self.bot = bot
        super().__init__()

    @app_commands.command(name="list", description="View all triggers")
    async def all_triggers(self, interaction: discord.Interaction):
        names = db.get_all_trigger_names(self.bot.con)
        await interaction.response.send_message(f"There are {len(names)} triggers registered:\n\n" + "\n".join(names))

    @app_commands.command(name="delete", description="Delete a trigger")
    @app_commands.describe(name="Which trigger to delete")
    async def delete_trigger(self, interaction: discord.Interaction, name: str):
        await self.view_trigger(interaction, name)
        if db.delete_trigger(self.bot.con, name):  # returns True if deleted; False if nothing to delete
            await interaction.channel.send("Deleted!")

    @app_commands.command(name="create", description="Create new trigger")
    async def new_trigger(self, interaction: discord.Interaction):
        # Send the modal with an instance of our `Feedback` class
        # Since modals require an interaction, they cannot be done as a response to a text command.
        # They can only be done as a response to either an application command or a button press.
        await interaction.response.send_modal(modals.AddTriggerModal(self.bot.con))

    @app_commands.command(name="view", description="See what's up with a trigger yo")
    @app_commands.describe(query="Which trigger to look up")
    async def view_trigger_slash(self, interaction: discord.Interaction, query: str):
        await self.view_trigger(interaction, query)

    async def view_trigger(self, interaction: discord.Interaction, query: str):
        query = query.lower()  # we enforce a naming convention when creating new. Follow that here.
        trigger = db.fetch_from_db(self.bot.con, query)
        if not trigger:
            await interaction.response.send_message(f"No trigger with name `{query}` found. :(")
            return
        e = discord.Embed(color=0x8b785b, title=query)  # title
        e.add_field(name="Times triggered", value=trigger.popularity)
        e.add_field(name='Internal ID', value=trigger.trigger_id)

        for i in trigger.inputs:
            e.add_field(name="Triggered By", value=i.string)
            if i.regex:
                e.add_field(name="Is a regex match", value="Yup!")
            else:
                e.add_field(name="Is case sensitive", value="Yup!" if i.case_sensitive else "Nope!")

        for o in trigger.outputs:
            e.add_field(name="Output", value=o.string)
            if len(trigger.outputs) > 1:
                e.add_field(name="Relative weight", value=o.weight)
        await interaction.response.send_message(embed=e)


async def setup(bot):
    await bot.add_cog(Sandy(bot))
