import traceback

import discord

import db


class AddTriggerModal(discord.ui.Modal):
    # Our modal classes MUST subclass `discord.ui.Modal`,
    # but the title can be whatever you want.

    def __init__(self, conn, *, title: str = 'Create New Trigger'):
        super().__init__(title=title)
        self.conn = conn

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
        # we must explicitly cast these to strings to get the responses. Otherwise they're weird more data-y objects.
        db.add_to_db(self.conn, str(self.name), str(self.trigger), str(self.url))
        await interaction.response.send_message(
            f'Added to database! {self.name} | {self.trigger} | <{self.url}>!')

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Uh oh spaghettio! Something went wrong.')

        # Make sure we know what the error actually is
        # traceback.print_tb(error.__traceback__)
        traceback.print_exc()
