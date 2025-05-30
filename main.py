import discord
from discord import app_commands
from discord.ext import commands
import json
import os

TOKEN = "MTMzMTI5OTg2MjE0NjMxODM0Nw.G705oX.x8NU9RdOWnXKFh0gFJoGnhaH6BHYe26nNFc52E"

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="/", intents=intents)
tree = bot.tree

# === Databáze ===

DATA_FILE = "data.json"

# Načti data
try:
    with open(DATA_FILE, "r") as f:
        databaze = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    databaze = {}

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(databaze, f, indent=4)

def get_or_create_user(user_id):
    user_id = str(user_id)
    if user_id not in databaze:
        databaze[user_id] = {
            "auta": [],
            "zbrane": []
        }
    return databaze[user_id]

# === PŘIPOJENÍ ===

@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅ Bot je online jako {bot.user}")

# === SLASH PŘÍKAZY ===

@tree.command(name="mojeinfo", description="Zobrazí tvůj inventář")
async def mojeinfo(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    data = get_or_create_user(user_id)
    embed = discord.Embed(title=f"🗂️ Inventář hráče {interaction.user.name}", color=0x00ffff)
    embed.add_field(name="🚗 Auta", value=", ".join(data["auta"]) or "Žádná", inline=False)
    embed.add_field(name="🔫 Zbraně", value=", ".join(data["zbrane"]) or "Žádné", inline=False)
    await interaction.response.send_message(embed=embed)

@tree.command(name="pridej-auto", description="Přidá auto hráči (admin)")
@app_commands.describe(uzivatel="Uživatel, kterému přidáš auto", auto="Auto, které chceš přidat")
@app_commands.checks.has_permissions(administrator=True)
async def pridej_auto(interaction: discord.Interaction, uzivatel: discord.Member, auto: str):
    data = get_or_create_user(uzivatel.id)
    data["auta"].append(auto)
    save_data()
    await interaction.response.send_message(f"✅ Přidáno auto `{auto}` hráči {uzivatel.display_name}.")

@tree.command(name="pridej-zbran", description="Přidá zbraň hráči (admin)")
@app_commands.describe(uzivatel="Uživatel, kterému přidáš zbraň", zbran="Zbraň, kterou chceš přidat")
@app_commands.checks.has_permissions(administrator=True)
async def pridej_zbran(interaction: discord.Interaction, uzivatel: discord.Member, zbran: str):
    data = get_or_create_user(uzivatel.id)
    data["zbrane"].append(zbran)
    save_data()
    await interaction.response.send_message(f"✅ Přidána zbraň `{zbran}` hráči {uzivatel.display_name}.")

# === Error handling ===
@pridej_auto.error
@pridej_zbran.error
async def missing_perm_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("❌ Nemáš oprávnění (ADMIN) pro tento příkaz.", ephemeral=True)
    else:
        await interaction.response.send_message("⚠️ Došlo k chybě.", ephemeral=True)

bot.run(TOKEN)