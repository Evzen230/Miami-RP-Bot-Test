import discord
from discord import app_commands
from discord.ext import commands
import sqlite3
import datetime

GUILD_ID = 1378711315119607808
POLICE_ROLE_NAME = "Policie"

conn = sqlite3.connect("police.db")
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS police_cases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    suspect_name TEXT NOT NULL,
    offense TEXT NOT NULL,
    officer TEXT NOT NULL,
    date TEXT NOT NULL,
    notes TEXT
)
""")
conn.commit()

def has_police_role(interaction: discord.Interaction):
    role = discord.utils.get(interaction.user.roles, name=POLICE_ROLE_NAME)
    return role is not None

class Police(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="addcase", description="Přidá nový policejní záznam")
    async def addcase(self, interaction: discord.Interaction, suspect_name: str, offense: str, notes: str = None):
        if not has_police_role(interaction):
            await interaction.response.send_message("❌ Nemáš oprávnění použít tento příkaz.", ephemeral=True)
            return
        
        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        officer = interaction.user.name
        c.execute("INSERT INTO police_cases (suspect_name, offense, officer, date, notes) VALUES (?, ?, ?, ?, ?)",
                  (suspect_name, offense, officer, date, notes))
        conn.commit()
        await interaction.response.send_message(f"✅ Případ pro **{suspect_name}** byl přidán.")

    @app_commands.command(name="searchcase", description="Vyhledá policejní záznam podle jména")
    async def searchcase(self, interaction: discord.Interaction, suspect_name: str):
        c.execute("SELECT * FROM police_cases WHERE suspect_name LIKE ?", (f"%{suspect_name}%",))
        results = c.fetchall()
        
        if results:
            embed =discord.Embed(title=f"Výsledky pro '{suspect_name}'", color=discord.Color.blue())
            for case in results:
                embed.add_field(
                    name=f"ID: {case[0]} | {case[1]}",
                    value=f"**Trestný čin:** {case[2]}\n👮 {case[3]}\n📅 {case[4]}\n📝 {case[5] or 'Žádné poznámky'}",
                    inline=False
                )
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("❌ Žádný záznam nenalezen.")

    @app_commands.command(name="deletecase", description="Smaže policejní záznam podle ID")
    async def deletecase(self, interaction: discord.Interaction, case_id: int):
        if not has_police_role(interaction):
            await interaction.response.send_message("❌ Nemáš oprávnění použít tento příkaz.", ephemeral=True)
            return
        
        c.execute("DELETE FROM police_cases WHERE id = ?", (case_id,))
        conn.commit()
        await interaction.response.send_message(f"🗑️ Případ s ID **{case_id}** byl smazán.")

async def setup(bot):
    await bot.add_cog(Police(bot), guild=discord.Object(id=GUILD_ID))