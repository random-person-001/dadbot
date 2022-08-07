import traceback

import discord
from discord import app_commands
from discord.ext import commands


def add_to_db(db, name: str, trigger: str, url: str):
    db.execute("INSERT INTO MAIN(name) VALUES (?)", (name,))
    trigger_id = db.execute("SELECT trigger_id FROM main WHERE name = ?", (name,)).fetchone()[0]
    db.execute("INSERT INTO OUTPUTS(trigger_id, string) VALUES (?, ?)", (trigger_id, url))
    db.execute("INSERT INTO INPUTS(trigger_id, string) VALUES (?, ?)", (trigger_id, trigger))
    db.commit()


class AddTriggerModal(discord.ui.Modal):
    # Our modal classes MUST subclass `discord.ui.Modal`,
    # but the title can be whatever you want.

    def __init__(self, db, *, title: str = 'Create New Trigger'):
        super().__init__(title=title)
        self.conn = db

    trigger = discord.ui.TextInput(
        label='Trigger Text',
        placeholder='What makes dad say this...',
    )

    name = discord.ui.TextInput(
        label='Human Name',
        placeholder='What should we refer to this as?',
    )

    url = discord.ui.TextInput(
        label='URL',
        placeholder='Paste those goodies here!',
    )

    async def on_submit(self, interaction: discord.Interaction):
        add_to_db(self.conn, str(self.name), str(self.trigger), str(self.url))
        await interaction.response.send_message(
            f'Added to database! {self.name} | {self.trigger} | <{self.url}>!', ephemeral=False)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

        # Make sure we know what the error actually is
        # traceback.print_tb(error.__traceback__)
        traceback.print_exc()


class Sandy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="newtrigger", description="Create new trigger")
    async def new_trigger(self, interaction: discord.Interaction):
        # Send the modal with an instance of our `Feedback` class
        # Since modals require an interaction, they cannot be done as a response to a text command.
        # They can only be done as a response to either an application command or a button press.
        await interaction.response.send_modal(AddTriggerModal(self.bot.con))


async def setup(bot):
    await bot.add_cog(Sandy(bot))
