import datetime
import discord
from discord import app_commands
import json
import os
from discord.ext import commands
import asyncio 
import random
from operator import itemgetter
from discord.ui import View, Button

# Import our modules
from utils import get_or_create_user, is_admin
from commands.inventory_commands import setup_inventory_commands
from commands.money_commands import setup_money_commands
from commands.trading_commands import setup_trading_commands
from commands.drug_commands import setup_drug_commands
from commands.vehicle_commands import setup_vehicle_commands
# from commands.casino_commands import casino_setup


TOKEN = os.getenv("DISCORD_BOT_TOKEN")
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="/", intents=intents)
tree = bot.tree

@bot.event
async def on_ready():
    # Setup all command modules
    await setup_inventory_commands(tree, bot)
    await setup_money_commands(tree, bot)
    await setup_trading_commands(tree, bot)
    await setup_drug_commands(tree, bot)
    await setup_vehicle_commands(tree, bot)
    # await casino_setup(tree, bot, load_data, save_data, get_or_create_user)

    # Add the help command
    @tree.command(name="prikazy", description="Zobrazí seznam všech dostupných příkazů a jejich popis")
    async def prikazy(interaction: discord.Interaction):
        embed = discord.Embed(title="📜 Seznam příkazů", color=discord.Color.green())

        embed.add_field(name="/inventory [uživatel]", value="Zobrazí inventář hráče (auta, zbraně, věci, drogy).", inline=False)
        embed.add_field(name="/koupit-zbran [zbraň] [počet]", value="Koupíš zbraň z nabídky, pokud máš oprávnění a peníze.", inline=False)
        embed.add_field(name="/prodej-zbran [uživatel] [zbraň] [počet]", value="Prodáš zbraň jinému hráči, s potvrzením od kupujícího.", inline=False)
        embed.add_field(name="/koupit-auto [auto]", value="Koupíš auto z nabídky.", inline=False)
        embed.add_field(name="/prodej-auto [uživatel] [auto]", value="Prodáš auto jinému hráči, s potvrzením od kupujícího.", inline=False)
        embed.add_field(name="/kup-veci [věc] [počet]", value="Koupíš věci potřebné pro výrobu nelegálních látek.", inline=False)
        embed.add_field(name="/prodej-veci [uživatel] [věc] [počet] [cena]", value="Prodáš věci jinému hráči za určenou cenu.", inline=False)
        embed.add_field(name="/vytvor [droga] [gramy]", value="Vyrobíš nelegální látku (vyžaduje nástroje a suroviny).", inline=False)
        embed.add_field(name="/vyrob [droga] [gramy]", value="Začne výrobu drogy, trvá určitou dobu, může selhat.", inline=False)
        embed.add_field(name="/pouzit-drogu [droga] [gramy]", value="Použiješ drogu ze svého inventáře, aktivují se efekty.", inline=False)
        embed.add_field(name="/balance", value="Zobrazí stav peněženky a bankovního účtu.", inline=False)
        embed.add_field(name="/vyber [částka]", value="Vybereš peníze z banky do peněženky.", inline=False)
        embed.add_field(name="/vloz [částka]", value="Vložíš peníze z peněženky na bankovní účet.", inline=False)
        embed.add_field(name="/collect", value="Vybereš týdenní odměnu podle rolí.", inline=False)
        embed.add_field(name="/leaderboard", value="Zobrazí žebříček hráčů podle jejich peněz.", inline=False)
        embed.add_field(name="/odeber-veci [uživatel] [věc] [počet]", value="Odebere věci z inventáře hráče (pouze policie/admin).", inline=False)
        embed.add_field(name="/odeber-drogy [uživatel] [droga] [gramy]", value="Odebere drogy z inventáře hráče (pouze policie/admin).", inline=False)
        embed.add_field(name="/reset-inventory [uživatel]", value="Resetuje celý inventář hráče (pouze policie/admin).", inline=False)
        embed.add_field(name="/registrovat-vozidlo", value="Zaregistruj vozidlo pomocí formuláře (typ, barva, rychlost, SPZ).", inline=False)
        embed.add_field(name="/moje-vozidla", value="Zobrazí tvá zaregistrovaná vozidla.", inline=False)
        embed.add_field(name="/vyhledat-vozidlo [spz]", value="Vyhledá vozidlo podle registrační značky.", inline=False)
        embed.add_field(name="/smazat-vozidlo [spz]", value="Smaže tvé zaregistrované vozidlo.", inline=False)
        embed.add_field(name="/vsechna-vozidla", value="Zobrazí všechna zaregistrovaná vozidla (admin).", inline=False)
        embed.add_field(name="/prikazy", value="Zobrazí tento seznam příkazů.", inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    await tree.sync()
    print(f"✅ Bot je online jako {bot.user}")

bot.run(TOKEN)