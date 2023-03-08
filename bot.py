import os
import pickle

import discord
from discord import client, app_commands
from discord.ext import commands, tasks

import utils
from datenbank import Datenbank
from scraper import Scraper

DATA_STORAGE = "data/"

MY_GUILD = discord.Object(id=1073722301805252749)


# Anmerkung: Die Guild ID ist bei Discord
# sowas wie die Server ID, also Server=Guild, warum auch immer das
# nötig ist *hust* BRANDING *hust*


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
        self.watchlist = Datenbank(DATA_STORAGE+"/watch.h5")
        self.datenbank = Datenbank(DATA_STORAGE+"/daten.h5")
        self.scraper = Scraper(datenbank=self.datenbank, watchlist=self.watchlist)

    def website_abrufen(self) -> None:
        """
        Scraped die Website des Gerichts, parst die Termine und wirft sie in die Datenbank

        TODO: Speichern wir alle Termine und filtern lokal nach den relevanten Aktenzeichen oder speichern wir von der
              Seite nur die Aktenzeichen die grade in der Watchlist sind ab?

        Returns
        -------
        None

        """
        self.scraper.update()
        pass

    def speichere_watchlist(self):
        """

        Returns
        -------

        """
        self.watchlist.flush()

    def speichere_datenbank(self):
        """

        Returns
        -------

        """
        self.datenbank.flush()


    ################ BOTCOMMANDS ################

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
        watched = self.scraper.update()

        # TODO ankuendigen

        # write the list back to termine, with all changes
        self.datenbank.append(watched)

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
    cleaned_az = utils.clean_akteneichen(aktenzeichen)

    if cleaned_az is None:
        perry.scraper.watch({"aktenzeichen":cleaned_az})
        await interaction.response.send_message(f"Das Aktenzeichen {cleaned_az} wurde auf die Watchlist aufgenommen!")
    else:
        await interaction.response.send_message(
            f"Das eingegebene Aktenzeichen ist kein gültiges Aktenzeichen des Gerichtszentrums Aachen.")


@perry.tree.command()
async def az_entfernen(interaction: discord.Interaction, aktenzeichen: str):
    cleaned_az = utils.clean_akteneichen(aktenzeichen)

    if cleaned_az is None:
        perry.scraper.unwatch({"aktenzeichen":cleaned_az})
        await interaction.response.send_message(f"Das Aktenzeichen {aktenzeichen} wurde aus der Watchlist entfernt!")
    else:
        await interaction.response.send_message(
            f"Das eingegebene Aktenzeichen ist kein gültiges Aktenzeichen des Gerichtszentrums Aachen.")
