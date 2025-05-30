
import discord
from discord import app_commands
import json
import os

TOKEN = os.getenv("DISCORD_BOT_TOKEN")

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

# === Discord Client ===
class MyClient(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        # Sync commands when bot starts
        await self.tree.sync()
        print(f"Synced {len(self.tree.get_commands())} commands")

    async def on_ready(self):
        print(f"✅ Bot je online jako {self.user}")

client = MyClient()

# === SLASH PŘÍKAZY ===

@client.tree.command(name="mojeinfo", description="Zobrazí tvůj inventář")
async def mojeinfo(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    data = get_or_create_user(user_id)
    embed = discord.Embed(title=f"🗂️ Inventář hráče {interaction.user.name}", color=0x00ffff)
    embed.add_field(name="🚗 Auta", value=", ".join(data["auta"]) or "Žádná", inline=False)
    embed.add_field(name="🔫 Zbraně", value=", ".join(data["zbrane"]) or "Žádné", inline=False)
    await interaction.response.send_message(embed=embed)

@client.tree.command(name="pridej-auto", description="Přidá auto hráči (admin)")
@app_commands.describe(uzivatel="Uživatel, kterému přidáš auto", auto="Auto, které chceš přidat")
async def pridej_auto(interaction: discord.Interaction, uzivatel: discord.Member, auto: str):
    # Check if user has administrator permissions
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Nemáš oprávnění (ADMIN) pro tento příkaz.", ephemeral=True)
        return
    
    data = get_or_create_user(uzivatel.id)
    data["auta"].append(auto)
    save_data()
    await interaction.response.send_message(f"✅ Přidáno auto `{auto}` hráči {uzivatel.display_name}.")

@client.tree.command(name="pridej-zbran", description="Přidá zbraň hráči (admin)")
@app_commands.describe(uzivatel="Uživatel, kterému přidáš zbraň", zbran="Zbraň, kterou chceš přidat")
async def pridej_zbran(interaction: discord.Interaction, uzivatel: discord.Member, zbran: str):
    # Check if user has administrator permissions
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Nemáš oprávnění (ADMIN) pro tento příkaz.", ephemeral=True)
        return
    
    data = get_or_create_user(uzivatel.id)
    data["zbrane"].append(zbran)
    save_data()
    await interaction.response.send_message(f"✅ Přidána zbraň `{zbran}` hráči {uzivatel.display_name}.")

# Run the bot
if TOKEN:
    client.run(TOKEN)
else:
    print("❌ DISCORD_BOT_TOKEN not found in environment variables!")
