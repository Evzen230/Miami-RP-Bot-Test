import discord
from discord import app_commands
import json
import os
from discord.ext import commands

TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="/", intents=intents)
tree = bot.tree

# === Seznamy dostupných aut a zbraní ===
DOSTUPNA_AUTA = [
    "Falcon Stallion 350 1969", "Bullhorn Prancer 1969",
    "Falcon Advance 100 Holiday Edition 1956", "Chevlon Corbeta C2 1967",
    "Sentinel Platinum 1968", "Bullhorn Foreman 1988",
    "Arrow Phoenix Nationals 1977", "Vellfire Runabout 1984",
    "Chevlon L/35 Extended 1981", "Chevlon Inferno 1981", "Chevlon L/15 1981",
    "Falcon Traveller 2003", "Chevlon Camion 2002", "Falcon Prime Eques 2003",
    "Vellfire Evertt 1995", "Overland Apache 1995", "Vellfire Prima 2009",
    "Overland Apache 2011", "Overland Buckaroo 2018", "Falcon Scavenger 2016",
    "Falcon Fission 2015", "Chevlon Captain 2009", "Vellfire Riptide 2020",
    "Bullhorn BH15 2009", "Elysion Slick 2014", "Chevlon Commuter Van 2006",
    "Chevlon Amigo LZR 2016", "Chevlon Landslide 2007",
    "Falcon Traveller 2022", "Navara Boundary 2022",
    "Bullhorn Determinator 2008", "Chevlon Camion 2021", "Chevlon Camion 2008",
    "Chevlon Revver 2005", "Falcon Rampage Bigfoot 2-Door 2021",
    "Bullhorn Prancer 2011", "Navara Imperium 2020", "Falcon Advance 2018",
    "Falcon Advance Beast 2017", "Falcon Rampage Beast 2021",
    "Falcon Advance 2022", "Bullhorn Prancer Widebody 2020",
    "Bullhorn Determinator SFP Fury 2022", "Vellfire Prairie 2022",
    "Bullhorn Pueblo 2018", "Navara Horizon 2013", "Chevlon Antilope 1994",
    "Leland LTS 2010", "Overland Apache SFP 2020", "Stuttgart Landschaft 2022",
    "Vellfire Pioneer 2019", "Falcon Stalion 350", "Chevlon Amigo S 2011",
    "Chevlon Amigo S 2016", "Amigo LZR 2011", "Averon S5 2010",
    "Leland Vault 2020", "Averon RS3 2020", "Stuttgart Executive 2021",
    "Terrain Traveller 2022", "Averon Q8 2022", "BKM Munich 2020",
    "Stuttgart Vierturig 2021", "Takeo Experience 2021", "Averon R8 2017",
    "Strugatti Ettore 2020", "Surrey 650S 2016", "LTS5-V Blackwing 2023",
    "Falcon Heritage 2021", "Ferdinand Jalapeno Turbo 2022",
    "Falcon Traveller 2022", "Chevlon Corbeta TZ 2014",
    "Chevlon Corbeta 8 2023", "Falcon Advance Bolt 2024", "Averon Anodic 2024",
    "Celestial Truckatron 2024", "BKM Risen Roadster 2020"
]
CENY_AUT = {
    # Classic
    "Falcon Stallion 350 1969": 260000,
    "Bullhorn Prancer 1969": 245000,
    "Falcon Advance 100 Holiday Edition 1956": 95000,
    "Chevlon Corbeta C2 1967": 185000,
    "Sentinel Platinum 1968": 115000,
    "Bullhorn Foreman 1988": 105000,
    "Arrow Phoenix Nationals 1977": 240000,
    "Vellfire Runabout 1984": 95000,
    "Chevlon L/35 Extended 1981": 105000,
    "Chevlon Inferno 1981": 97500,
    "Chevlon L/15 1981": 92000,

    # Regular
    "Falcon Traveller 2003": 15000,
    "Chevlon Camion 2002": 10000,
    "Falcon Prime Eques 2003": 9000,
    "Vellfire Evertt 1995": 20000,
    "Overland Apache 1995": 12000,
    "Vellfire Prima 2009": 10000,
    "Overland Apache 2011": 40000,
    "Overland Buckaroo 2018": 45000,
    "Falcon Scavenger 2016": 40000,
    "Falcon Fission 2015": 35000,
    "Chevlon Captain 2009": 20000,
    "Vellfire Riptide 2020": 55000,
    "Bullhorn BH15 2009": 30000,
    "Elysion Slick 2014": 20000,
    "Chevlon Commuter Van 2006": 30000,
    "Chevlon Amigo LZR 2016": 100000,
    "Chevlon Landslide 2007": 26000,
    "Falcon Traveller 2022": 90000,
    "Navara Boundary 2022": 65000,
    "Bullhorn Determinator 2008": 70000,
    "Chevlon Camion 2021": 75000,
    "Chevlon Camion 2008": 30000,
    "Chevlon Revver 2005": 50000,
    "Falcon Rampage Bigfoot 2-Door 2021": 70000,
    "Bullhorn Prancer 2011": 50000,
    "Navara Imperium 2020": 30000,
    "Falcon Advance 2018": 70000,
    "Falcon Advance Beast 2017": 100000,
    "Falcon Rampage Beast 2021": 130000,
    "Falcon Advance 2022": 140000,
    "Bullhorn Prancer Widebody 2020": 170000,
    "Bullhorn Determinator SFP Fury 2022": 185000,
    "Vellfire Prairie 2022": 80000,
    "Bullhorn Pueblo 2018": 100000,
    "Navara Horizon 2013": 250000,
    "Chevlon Antilope 1994": 7000,
    "Leland LTS 2010": 42000,
    "Overland Apache SFP 2020": 150000,
    "Stuttgart Landschaft 2022": 200000,
    "Vellfire Pioneer 2019": 125000,
    "Falcon Stalion 350": 100000,
    "Chevlon Amigo S 2011": 85000,
    "Chevlon Amigo S 2016": 96000,
    "Chevlon Amigo LZR 2011": 90000,

    # Prestige
    "Averon S5 2010": 140000,
    "Leland Vault 2020": 130000,
    "Averon RS3 2020": 180000,
    "Stuttgart Executive: 2021": 240000,
    "Terrain Traveller 2022": 180000,
    "Averon Q8 2022": 220000,
    "BKM Munich 2020": 185000,
    "Stuttgart Vierturig: 2021": 100000,  # Neurčena cena
    "Takeo Experience 2021": 550000,
    "Averon R8 2017": 800000,
    "Strugatti Ettore 2020": 1200000,
    "Surrey 650S 2016": 900000,
    "Leland LTS5-V Blackwing 2023": 280000,
    "Falcon Heritage 2021": 720000,
    "Ferdinand Jalapeno Turbo: 2022": 200000,
    "Falcon Traveller 2022": 100000,
    "Chevlon Corbeta TZ 2014": 450000,
    "Chevlon Corbeta 8 2023": 600000,

    # Electric
    "Falcon Advance Bolt 2024": 350000,
    "Averon Anodic 2024": 500000,
    "Celestial Truckatron 2024": 800000,
    "BKM Risen Roadster 2020": 650000
}

DOSTUPNE_ZBRANE = [
    "Beretta M9", "M249", "Remington MSR", "M14", "AK47", "PPSH 41",
    "Desert Eagle", "Colt M1911", "Kriss Vector", "LMT L129A1", "Skorpion",
    "Colt Python", "TEC-9", "Remington 870", "Lemat Revolver"
]
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
        databaze[user_id] = {"auta": {}, "zbrane": {},"penize": 0}
    else:
        # Convert old list format to new dict format
        data = databaze[user_id]
        if isinstance(data.get("auta"), list):
            # Convert list to dict with counts
            auta_dict = {}
            for auto in data["auta"]:
                if auto in auta_dict:
                    auta_dict[auto] += 1
                else:
                    auta_dict[auto] = 1
            data["auta"] = auta_dict
        
        if isinstance(data.get("zbrane"), list):
            # Convert list to dict with counts
            zbrane_dict = {}
            for zbran in data["zbrane"]:
                if zbran in zbrane_dict:
                    zbrane_dict[zbran] += 1
                else:
                    zbrane_dict[zbran] = 1
            data["zbrane"] = zbrane_dict
            
    return databaze[user_id]


# === PŘIPOJENÍ ===


@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅ Bot je online jako {bot.user}")

# ===INVENTORY PŘÍKAZY ===

#pridej zbran command
@tree.command(name="pridej-zbran", description="Přidá zbraň hráči (admin)")
@app_commands.describe(uzivatel="Uživatel, kterému přidáš zbraň",
                           zbran="Zbraň, kterou chceš přidat",
                           pocet="Počet kusů")
async def pridej_zbran(interaction: discord.Interaction,
                           uzivatel: discord.Member,
                           zbran: str,
                           pocet: int = 1):
        role_id = 1378111107780313209  # Změň na skutečné ID role
        if not any(role.id == role_id for role in interaction.user.roles):
            await interaction.response.send_message(
                "❌ Nemáš oprávnění použít tento příkaz.", ephemeral=True)
            return
        if zbran not in DOSTUPNE_ZBRANE:
            await interaction.response.send_message(
                f"❌ Zbraň `{zbran}` není v seznamu dostupných zbraní.",
                ephemeral=True)
            return
        data = get_or_create_user(uzivatel.id)
        if zbran in data["zbrane"]:
            data["zbrane"][zbran] += pocet
        else:
            data["zbrane"][zbran] = pocet
        save_data()
        await interaction.response.send_message(
            f"✅ Přidáno {pocet}x `{zbran}` hráči {uzivatel.display_name}.")

@pridej_zbran.autocomplete("zbran")
async def autocomplete_zbran_pridat(interaction: discord.Interaction,
                                        current: str):
        return [
            app_commands.Choice(name=z, value=z) for z in DOSTUPNE_ZBRANE
            if current.lower() in z.lower()
        ][:25]
#odeber zbran command
@tree.command(name="odeber-zbran", description="Odebere zbraň hráči (admin)")
@app_commands.describe(uzivatel="Uživatel, kterému odebereš zbraň",
                           zbran="Zbraň, kterou chceš odebrat",
                           pocet="Počet kusů")
async def odeber_zbran(interaction: discord.Interaction,
                           uzivatel: discord.Member,
                           zbran: str,
                           pocet: int = 1):
        role_id = 1378111107780313209  # Změň na skutečné ID role
        if not any(role.id == role_id for role in interaction.user.roles):
            await interaction.response.send_message(
                "❌ Nemáš oprávnění použít tento příkaz.", ephemeral=True)
            return
        data = get_or_create_user(uzivatel.id)
        if zbran in data["zbrane"]:
            data["zbrane"][zbran] -= pocet
            if data["zbrane"][zbran] <= 0:
                del data["zbrane"][zbran]
            save_data()
            await interaction.response.send_message(
                f"✅ Odebráno {pocet}x `{zbran}` hráči {uzivatel.display_name}."
            )
        else:
            await interaction.response.send_message(
                f"❌ Zbraň `{zbran}` nebyla nalezena u {uzivatel.display_name}."
            )

@odeber_zbran.autocomplete("zbran")
async def autocomplete_zbran_odebrat(interaction: discord.Interaction,
                                         current: str):
        uzivatel = interaction.namespace.uzivatel
        if not uzivatel:
            return []
        data = get_or_create_user(uzivatel.id)
        return [
            app_commands.Choice(name=z, value=z) for z in data["zbrane"]
            if current.lower() in z.lower()
        ][:25]

    # Pridej auto command
@tree.command(name="pridej-auto", description="Přidá auto hráči (admin)")
@app_commands.describe(uzivatel="Uživatel, kterému přidáš auto",
                           auto="Auto, které chceš přidat",
                           pocet="Počet kusů")
async def pridej_auto(interaction: discord.Interaction,
                          uzivatel: discord.Member,
                          auto: str,
                          pocet: int = 1):
        role_id = 1378111107780313209  # Změň na skutečné ID role
        if not any(role.id == role_id for role in interaction.user.roles):
            await interaction.response.send_message(
                "❌ Nemáš oprávnění použít tento příkaz.", ephemeral=True)
            return
        if auto not in DOSTUPNA_AUTA:
            await interaction.response.send_message(
                f"❌ Auto `{auto}` není v seznamu dostupných aut.", ephemeral=True)
            return
        data = get_or_create_user(uzivatel.id)
        if auto in data["auta"]:
            data["auta"][auto] += pocet
        else:
            data["auta"][auto] = pocet
        save_data()
        await interaction.response.send_message(
            f"✅ Přidáno {pocet}x `{auto}` hráči {uzivatel.display_name}.")

@pridej_auto.autocomplete("auto")
async def autocomplete_auto_pridat(interaction: discord.Interaction,
                                       current: str):
        return [
            app_commands.Choice(name=a, value=a) for a in DOSTUPNA_AUTA
            if current.lower() in a.lower()
        ][:25]

    # Odeber auto command
@tree.command(name="odeber-auto", description="Odebere auto hráči (admin)")
@app_commands.describe(uzivatel="Uživatel, kterému odebereš auto",
                           auto="Auto, které chceš odebrat",
                           pocet="Počet kusů")
async def odeber_auto(interaction: discord.Interaction,
                          uzivatel: discord.Member,
                          auto: str,
                          pocet: int = 1):
        role_id = 1378111107780313209  # Změň na skutečné ID role
        if not any(role.id == role_id for role in interaction.user.roles):
            await interaction.response.send_message(
                "❌ Nemáš oprávnění použít tento příkaz.", ephemeral=True)
            return
        data = get_or_create_user(uzivatel.id)
        if auto in data["auta"]:
            data["auta"][auto] -= pocet
            if data["auta"][auto] <= 0:
                del data["auta"][auto]
            save_data()
            await interaction.response.send_message(
                f"✅ Odebráno {pocet}x `{auto}` hráči {uzivatel.display_name}.")
        else:
            await interaction.response.send_message(
                f"❌ Auto `{auto}` nebylo nalezeno u {uzivatel.display_name}.")

@odeber_auto.autocomplete("auto")
async def autocomplete_auto_odebrat(interaction: discord.Interaction,
                                        current: str):
        uzivatel = interaction.namespace.uzivatel
        if not uzivatel:
            return []
        data = get_or_create_user(uzivatel.id)
        return [
            app_commands.Choice(name=a, value=a) for a in data["auta"]
            if current.lower() in a.lower()
        ][:25]

    # Inventory command
@tree.command(name="inventory", description="Zobrazí inventář hráče")
@app_commands.describe(uzivatel="Uživatel, jehož inventář chceš zobrazit")
async def inventory(interaction: discord.Interaction,
                        uzivatel: discord.Member = None):
        uzivatel = uzivatel or interaction.user
        data = get_or_create_user(uzivatel.id)

        auta = data.get("auta", {})
        zbrane = data.get("zbrane", {})

        auta_text = "\n".join(f"🚗 {auto} ×{pocet}"
                              for auto, pocet in auta.items()) or "Žádná"
        zbrane_text = "\n".join(f"🔫 {zbran} ×{pocet}"
                                for zbran, pocet in zbrane.items()) or "Žádné"

        embed = discord.Embed(
            title=f"📋 Inventář uživatele {uzivatel.display_name}",
            color=discord.Color.blue())
        embed.add_field(name="Auta", value=auta_text, inline=False)
        embed.add_field(name="Zbraně", value=zbrane_text, inline=False)

        await interaction.response.send_message(embed=embed)

# Reset inventory command
@tree.command(name="reset-inventory", description="Resetuje celý inventář hráče (admin)")
@app_commands.describe(uzivatel="Uživatel, jehož inventář chceš vymazat")
async def reset_inventory(interaction: discord.Interaction, uzivatel: discord.Member):
    role_id = 123456789012345678  # Změň na skutečné ID role
    if not any(role.id == role_id for role in interaction.user.roles):
        await interaction.response.send_message("❌ Nemáš oprávnění použít tento příkaz.", ephemeral=True)
        return
    data = get_or_create_user(uzivatel.id)
    data["auta"] = {}
    data["zbrane"] = {}
    save_data()
    await interaction.response.send_message(f"♻️ Inventář hráče {uzivatel.display_name} byl úspěšně resetován.")

# === PŘÍKAZY NA PENÍZE ===


# Balance command

@tree.command(name="balance", description="Zobrazí zůstatek peněz")
@app_commands.describe(uzivatel="Uživatel, jehož zůstatek chceš zjistit (nepovinné)")
async def balance(interaction: discord.Interaction, uzivatel: discord.Member = None):
    if uzivatel is None:
        uzivatel = interaction.user
    data = get_or_create_user(uzivatel.id)
    await interaction.response.send_message(f"💵 {uzivatel.display_name} má {data['penize']}$.")

# Pridej penize command
@tree.command(name="pridej-penize", description="Přidá peníze hráči (admin)")
@app_commands.describe(uzivatel="Uživatel, kterému chceš přidat peníze", castka="Kolik peněz chceš přidat")
async def pridej_penize(interaction: discord.Interaction, uzivatel: discord.Member, castka: int):
    role_id = 123456789012345678  # Změň na ID role s oprávněním
    if not any(role.id == role_id for role in interaction.user.roles):
        await interaction.response.send_message("❌ Nemáš oprávnění použít tento příkaz.", ephemeral=True)
        return
    data = get_or_create_user(uzivatel.id)
    data["penize"] += castka
    save_data()
    await interaction.response.send_message(f"✅ Přidáno {castka}$ hráči {uzivatel.display_name}.")

# Odeber penize command
@tree.command(name="odeber-penize", description="Odebere peníze hráči (admin)")
@app_commands.describe(uzivatel="Uživatel, kterému chceš odebrat peníze", castka="Kolik peněz chceš odebrat")
async def odeber_penize(interaction: discord.Interaction, uzivatel: discord.Member, castka: int):
    role_id = 123456789012345678  # Změň na ID role s oprávněním
    if not any(role.id == role_id for role in interaction.user.roles):
        await interaction.response.send_message("❌ Nemáš oprávnění použít tento příkaz.", ephemeral=True)
        return
    data = get_or_create_user(uzivatel.id)
    data["penize"] -= castka
    if data["penize"] < 0:
        data["penize"] = 0
    save_data()
    await interaction.response.send_message(f"✅ Odebráno {castka}$ hráči {uzivatel.display_name}.")

# Reset penize command

@tree.command(name="reset-penize", description="Resetuje peníze hráče (admin)")
@app_commands.describe(uzivatel="Uživatel, jehož peníze chceš vynulovat")
async def reset_penize(interaction: discord.Interaction, uzivatel: discord.Member):
    role_id = 123456789012345678  # Změň na ID role s oprávněním
    if not any(role.id == role_id for role in interaction.user.roles):
        await interaction.response.send_message("❌ Nemáš oprávnění použít tento příkaz.", ephemeral=True)
        return
    data = get_or_create_user(uzivatel.id)
    data["penize"] = 0
    save_data()
    await interaction.response.send_message(f"♻️ Peníze hráče {uzivatel.display_name} byly vynulovány.")

# Pay command

@tree.command(name="pay", description="Pošle peníze jinému hráči")
@app_commands.describe(cil="Komu chceš poslat peníze", castka="Kolik peněz chceš poslat")
async def posli_penize(interaction: discord.Interaction, cil: discord.Member, castka: int):
    if castka <= 0:
        await interaction.response.send_message("❌ Částka musí být větší než 0.", ephemeral=True)
        return
    odesilatel_data = get_or_create_user(interaction.user.id)
    prijemce_data = get_or_create_user(cil.id)
    if odesilatel_data["penize"] < castka:
        await interaction.response.send_message("❌ Nemáš dostatek peněz.", ephemeral=True)
        return
    odesilatel_data["penize"] -= castka
    prijemce_data["penize"] += castka
    save_data()
    await interaction.response.send_message(f"💸 Poslal jsi {castka}$ hráči {cil.display_name}.")
# Kup auto command

@tree.command(name="kup-auto", description="Koupí auto za peníze")
@app_commands.describe(auto="Auto, které chceš koupit", pocet="Kolik kusů chceš koupit")
async def kup_auto(interaction: discord.Interaction, auto: str, pocet: int = 1):
        user = interaction.user
        data = get_or_create_user(user.id)

        if auto not in CENY_AUT:
            await interaction.response.send_message(f"❌ Auto `{auto}` není dostupné k nákupu.", ephemeral=True)
            return

        cena = CENY_AUT[auto] * pocet
        if data["penize"] < cena:
            await interaction.response.send_message(f"❌ Nemáš dostatek peněz. Potřebuješ {cena}$.", ephemeral=True)
            return

        # odečtení peněz a přidání auta
        data["penize"] -= cena
        if auto in data["auta"]:
            data["auta"][auto] += pocet
        else:
            data["auta"][auto] = pocet

        save_data()
        await interaction.response.send_message(f"✅ Koupil jsi {pocet}x `{auto}` za {cena}$.")

@kup_auto.autocomplete("auto")
async def autocomplete_kup_auto(interaction: discord.Interaction, current: str):
    return [
        app_commands.Choice(name=a, value=a)
        for a in CENY_AUT.keys() if current.lower() in a.lower()
    ][:25]

bot.run(TOKEN)