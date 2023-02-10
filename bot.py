import discord
from discord import client, app_commands
from discord.ext import commands, tasks

MY_GUILD = discord.Object(id=1073722301805252749)  # replace with your guild id


class Perry(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # A CommandTree is a special type that holds all the application command
        # state required to make it work. This is a separate class because it
        # allows all the extra state to be opt-in.
        # Whenever you want to work with application commands, your tree is used
        # to store and work with them.
        # Note: When using commands.Bot instead of discord.Client, the bot will
        # maintain its own tree instead.
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        # This copies the global commands over to your guild.
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)

        # Website des Gerichts jede Stunde scrapen und eventuelle Änderungen anzeigen
        self.refresh_database.start()

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')


    @tasks.loop(minutes=60)  # task runs every 60 seconds
    async def refresh_database(self):
        channel = self.get_channel(1073722302908346420)  # channel ID goes here
        await channel.send("Die aktuelle Seite des Justizzentrums Aachen wurde abgerufen")

    @refresh_database.before_loop
    async def before_my_task(self):
        await self.wait_until_ready()  # wait until the bot logs in


intents = discord.Intents.default()
intents.message_content = True
intents.typing = True
perry = Perry(intents=intents)


@perry.tree.command()
async def hello(interaction: discord.Interaction):
    """Says hello!"""
    await interaction.response.send_message(f'Hi, {interaction.user.mention}')


@perry.tree.command()
async def az_hinzufuegen(interaction: discord.Interaction, aktenzeichen: str):
    await interaction.response.send_message(f"Das Aktenzeichen {aktenzeichen} wurde auf die Watchlist aufgenommen!")


