import discord
from discord import app_commands
from utils import get_or_create_user, is_admin
import re
import random
import string

class VehicleRegistrationModal(discord.ui.Modal, title='Registrace vozidla'):
    def __init__(self, selected_car):
        super().__init__()
        self.selected_car = selected_car

        self.color = discord.ui.TextInput(
            label='Barva',
            placeholder='Např. Červená, Modrá, Černá...',
            required=True,
            max_length=30
        )
        self.add_item(self.color)

        self.max_speed = discord.ui.TextInput(
            label='Maximální rychlost (mp/h)',
            placeholder='Např. 75',
            required=True,
            max_length=3
        )
        self.add_item(self.max_speed)

        self.license_plate = discord.ui.TextInput(
            label='Registrační značka',
            placeholder='Např. ABD456 nebo nech prázdné pro generovanou',
            required=False,
            max_length=15
        )
        self.add_item(self.license_plate)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            speed = int(self.max_speed.value)
            if speed <= 0 or speed > 500:
                await interaction.response.send_message("❌ Maximální rychlost musí být mezi 1-500 mp/h.", ephemeral=True)
                return
        except ValueError:
            await interaction.response.send_message("❌ Maximální rychlost musí být číslo.", ephemeral=True)
            return

        # --- Nastavení ceny ---
        REGISTRATION_COST = 400  # herní měna
        USD_RATE = 0.045  # příklad převodu
        cost_usd = REGISTRATION_COST * USD_RATE

        
        user_data = get_or_create_user(interaction.user.id)

        # Kontrola peněz
        if user_data.get("bank", 0) < REGISTRATION_COST:
            await interaction.response.send_message(
                f"❌ Registrace stojí {REGISTRATION_COST}💰 ({cost_usd:.2f}$ USD), ale máš jen v bance {user_data.get('bank', 0)}💰.",
                ephemeral=True
            )
            return

        # Odečtení peněz
        user_data["bank"] = user_data.get("bank", 0) - REGISTRATION_COST

        # --- Generování SPZ ---
        if not self.license_plate.value.strip():
            letters = ''.join(random.choices(string.ascii_uppercase, k=3))
            numbers = ''.join(random.choices(string.digits, k=3))
            plate = f"{letters}{numbers}"
        else:
            plate = self.license_plate.value.upper().strip()

        if not re.match(r'^[A-Z0-9\-]{3,15}$', plate):
            await interaction.response.send_message("❌ Neplatný formát SPZ. Použij pouze písmena, čísla, pomlčky.", ephemeral=True)
            return

        for user_id, udata in databaze.items():
            for vehicle_info in udata.get("registrovana_auta", {}).values():
                if vehicle_info.get("spz") == plate:
                    await interaction.response.send_message(f"❌ SPZ `{plate}` již existuje! Zvolte jinou.", ephemeral=True)
                    return

        if "registrovana_auta" not in user_data:
            user_data["registrovana_auta"] = {}

        vehicle_count = len(user_data["registrovana_auta"]) + 1
        vehicle_id = f"vozidlo_{vehicle_count}"
        while vehicle_id in user_data["registrovana_auta"]:
            vehicle_count += 1
            vehicle_id = f"vozidlo_{vehicle_count}"

        vehicle_info = {
            "typ": self.selected_car,
            "barva": self.color.value,
            "max_rychlost": speed,
            "spz": plate,
            "majitel": interaction.user.display_name,
            "datum_registrace": discord.utils.utcnow().strftime("%d.%m.%Y %H:%M")
        }

        user_data["registrovana_auta"][vehicle_id] = vehicle_info
        

        embed = discord.Embed(
            title="✅ Vozidlo úspěšně zaregistrováno",
            description=f"💰 Cena registrace: {REGISTRATION_COST} ({cost_usd:.2f}$ USD)",
            color=discord.Color.green()
        )
        embed.add_field(name="🚗 Typ", value=vehicle_info["typ"], inline=True)
        embed.add_field(name="🎨 Barva", value=vehicle_info["barva"], inline=True)
        embed.add_field(name="⚡ Max. rychlost", value=f"{vehicle_info['max_rychlost']} mp/h", inline=True)
        embed.add_field(name="🔢 SPZ", value=vehicle_info["spz"], inline=True)
        embed.add_field(name="📅 Datum registrace", value=vehicle_info["datum_registrace"], inline=True)
        embed.add_field(name="👤 Majitel", value=vehicle_info["majitel"], inline=True)
        embed.add_field(name="💵 Zůstatek po registraci", value=f"{user_data['bank']}💰", inline=True)

        await interaction.response.send_message(embed=embed)


class VehicleSelectView(discord.ui.View):
    def __init__(self, available_cars):
        super().__init__(timeout=60)
        self.add_item(VehicleSelect(available_cars))


class VehicleSelect(discord.ui.Select):
    def __init__(self, available_cars):
        options = [discord.SelectOption(label=car, value=car) for car in available_cars]
        super().__init__(placeholder="Vyber vozidlo k registraci", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        selected_car = self.values[0]
        modal = VehicleRegistrationModal(selected_car)
        await interaction.response.send_modal(modal)


async def setup_vehicle_commands(tree, bot):
    @tree.command(name="registrovat-vozidlo", description="Zaregistruj své vozidlo do systému")
    async def registrovat_vozidlo(interaction: discord.Interaction):
        
        user_data = get_or_create_user(interaction.user.id)
        available_cars = user_data.get("auta", [])

        if not available_cars:
            await interaction.response.send_message("❌ Nemáš žádná vozidla k registraci.", ephemeral=True)
            return

        view = VehicleSelectView(available_cars)
        await interaction.response.send_message("Vyber vozidlo, které chceš registrovat:", view=view, ephemeral=True)

    @tree.command(name="moje-registrace", description="Zobraz svá zaregistrovaná vozidla")
    async def moje_vozidla(interaction: discord.Interaction):
        
        user_data = get_or_create_user(interaction.user.id)
        
        vehicles = user_data.get("registrovana_auta", {})
        
        if not vehicles:
            await interaction.response.send_message("❌ Nemáš žádná zaregistrovaná vozidla.", ephemeral=True)
            return

        embed = discord.Embed(
            title=f"🚗 Registrovaná vozidla - {interaction.user.display_name}",
            color=discord.Color.blue()
        )

        for vehicle_id, vehicle_info in vehicles.items():
            vehicle_text = (
                f"**Typ:** {vehicle_info['typ']}\n"
                f"**Barva:** {vehicle_info['barva']}\n"
                f"**Max. rychlost:** {vehicle_info['max_rychlost']} mp/h\n"
                f"**SPZ:** `{vehicle_info['spz']}`\n"
                f"**Registrováno:** {vehicle_info['datum_registrace']}"
            )
            embed.add_field(
                name=f"🚙 {vehicle_info['typ']} ({vehicle_info['spz']})",
                value=vehicle_text,
                inline=False
            )

        await interaction.response.send_message(embed=embed)
        
    @tree.command(name="registrace-uzivatele", description="Zobraz registrovaná vozidla konkrétního uživatele")
    @app_commands.describe(user="Uživatel, jehož vozidla chceš zobrazit")
    async def registrace_uzivatele(interaction: discord.Interaction, user: discord.User):
        
        user_data = get_or_create_user(user.id)

        vehicles = user_data.get("registrovana_auta", {})

        if not vehicles:
            await interaction.response.send_message(f"❌ Uživatel **{user.display_name}** nemá žádná registrovaná vozidla.", ephemeral=True)
            return

        embed = discord.Embed(
            title=f"🚗 Registrovaná vozidla - {user.display_name}",
            color=discord.Color.blue()
        )

        for vehicle_id, vehicle_info in vehicles.items():
            vehicle_text = (
                f"**Typ:** {vehicle_info['typ']}\n"
                f"**Barva:** {vehicle_info['barva']}\n"
                f"**Max. rychlost:** {vehicle_info['max_rychlost']} mp/h\n"
                f"**SPZ:** `{vehicle_info['spz']}`\n"
                f"**Registrováno:** {vehicle_info['datum_registrace']}"
            )
            embed.add_field(
                name=f"🚙 {vehicle_info['typ']} ({vehicle_info['spz']})",
                value=vehicle_text,
                inline=False
            )

        await interaction.response.send_message(embed=embed)

    @tree.command(name="vyhledat-vozidlo", description="Vyhledej vozidlo podle SPZ")
    @app_commands.describe(spz="Registrační značka vozidla")
    async def vyhledat_vozidlo(interaction: discord.Interaction, spz: str):
        spz = spz.upper().strip()
        
        
        found_vehicle = None
        owner_name = None
        
        for user_id, user_data in databaze.items():
            vehicles = user_data.get("registrovana_auta", {})
            for vehicle_id, vehicle_info in vehicles.items():
                if vehicle_info.get("spz") == spz:
                    found_vehicle = vehicle_info
                    owner_name = vehicle_info.get("majitel", "Neznámý")
                    break
            if found_vehicle:
                break
        
        if not found_vehicle:
            await interaction.response.send_message(f"❌ Vozidlo se SPZ `{spz}` nebylo nalezeno.", ephemeral=True)
            return

        embed = discord.Embed(
            title=f"🔍 Informace o vozidle - {spz}",
            color=discord.Color.gold()
        )
        embed.add_field(name="🚗 Typ", value=found_vehicle["typ"], inline=True)
        embed.add_field(name="🎨 Barva", value=found_vehicle["barva"], inline=True)
        embed.add_field(name="⚡ Max. rychlost", value=f"{found_vehicle['max_rychlost']} mp/h", inline=True)
        embed.add_field(name="👤 Majitel", value=owner_name, inline=True)
        embed.add_field(name="📅 Registrováno", value=found_vehicle["datum_registrace"], inline=True)

        await interaction.response.send_message(embed=embed)

    @tree.command(name="smazat-vozidlo", description="Smaž své zaregistrované vozidlo")
    @app_commands.describe(spz="SPZ vozidla, které chceš smazat")
    async def smazat_vozidlo(interaction: discord.Interaction, spz: str):
        spz = spz.upper().strip()
        
        user_data = get_or_create_user(interaction.user.id)
        
        vehicles = user_data.get("registrovana_auta", {})
        vehicle_to_remove = None
        
        for vehicle_id, vehicle_info in vehicles.items():
            if vehicle_info.get("spz") == spz:
                vehicle_to_remove = vehicle_id
                break
        
        if not vehicle_to_remove:
            await interaction.response.send_message(f"❌ Nemáš zaregistrované vozidlo s registrační značkou `{spz}`.", ephemeral=True)
            return

        del user_data["registrovana_auta"][vehicle_to_remove]
        
        
        await interaction.response.send_message(f"✅ Vozidlo s registrační značkou `{spz}` bylo úspěšně smazáno z registru.")

    @tree.command(name="vsechny-registrace", description="Zobraz všechna zaregistrovaná vozidla (admin)")
    async def vsechna_vozidla(interaction: discord.Interaction):
        if not is_admin(interaction.user):
            await interaction.response.send_message("❌ Nemáš oprávnění použít tento příkaz.", ephemeral=True)
            return
            
        
        all_vehicles = []
        
        for user_id, user_data in databaze.items():
            vehicles = user_data.get("registrovana_auta", {})
            for vehicle_id, vehicle_info in vehicles.items():
                all_vehicles.append(vehicle_info)
        
        if not all_vehicles:
            await interaction.response.send_message("❌ V systému nejsou žádná zaregistrovaná vozidla.", ephemeral=True)
            return

        embed = discord.Embed(
            title="🚗 Všechna zaregistrovaná vozidla",
            description=f"Celkem: {len(all_vehicles)} vozidel",
            color=discord.Color.purple()
        )

        for vehicle in all_vehicles[:10]:
            vehicle_text = (
                f"**Majitel:** {vehicle['majitel']}\n"
                f"**Typ:** {vehicle['typ']}\n"
                f"**Barva:** {vehicle['barva']}\n"
                f"**Max. rychlost:** {vehicle['max_rychlost']} mp/h"
            )
            embed.add_field(
                name=f"🔢 SPZ: {vehicle['spz']}",
                value=vehicle_text,
                inline=True
            )

        if len(all_vehicles) > 10:
            embed.set_footer(text=f"Zobrazeno prvních 10 z {len(all_vehicles)} vozidel")

        await interaction.response.send_message(embed=embed)