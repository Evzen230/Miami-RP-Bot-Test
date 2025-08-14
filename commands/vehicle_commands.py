
import discord
from discord import app_commands
from utils import get_or_create_user, save_data, load_data, is_admin
import re

class VehicleRegistrationModal(discord.ui.Modal, title='Registrace vozidla'):
    def __init__(self):
        super().__init__()

    car_type = discord.ui.TextInput(
        label='Typ vozidla',
        placeholder='Např. BMW M3, Audi A4, Mercedes C63...',
        required=True,
        max_length=50
    )

    color = discord.ui.TextInput(
        label='Barva',
        placeholder='Např. Červená, Modrá, Černá...',
        required=True,
        max_length=30
    )

    max_speed = discord.ui.TextInput(
        label='Maximální rychlost (km/h)',
        placeholder='Např. 250',
        required=True,
        max_length=3
    )

    license_plate = discord.ui.TextInput(
        label='Registrační značka (SPZ)',
        placeholder='Např. 1A2 3456 nebo vlastní značka',
        required=True,
        max_length=15
    )

    async def on_submit(self, interaction: discord.Interaction):
        # Validate max speed
        try:
            speed = int(self.max_speed.value)
            if speed <= 0 or speed > 500:
                await interaction.response.send_message("❌ Maximální rychlost musí být mezi 1-500 km/h.", ephemeral=True)
                return
        except ValueError:
            await interaction.response.send_message("❌ Maximální rychlost musí být číslo.", ephemeral=True)
            return

        # Validate license plate format
        plate = self.license_plate.value.upper().strip()
        if not re.match(r'^[A-Z0-9\s]{3,15}$', plate):
            await interaction.response.send_message("❌ Neplatný formát SPZ. Použij pouze písmena, čísla a mezery.", ephemeral=True)
            return

        databaze = load_data()
        
        # Check if license plate already exists
        for user_id, user_data in databaze.items():
            vehicles = user_data.get("registrovana_auta", {})
            for vehicle_id, vehicle_info in vehicles.items():
                if vehicle_info.get("spz") == plate:
                    await interaction.response.send_message(f"❌ SPZ `{plate}` již existuje! Zvolte jinou.", ephemeral=True)
                    return

        user_data = get_or_create_user(interaction.user.id, databaze)
        
        if "registrovana_auta" not in user_data:
            user_data["registrovana_auta"] = {}

        # Generate unique vehicle ID
        vehicle_count = len(user_data["registrovana_auta"]) + 1
        vehicle_id = f"vozidlo_{vehicle_count}"
        
        # Make sure ID is unique
        while vehicle_id in user_data["registrovana_auta"]:
            vehicle_count += 1
            vehicle_id = f"vozidlo_{vehicle_count}"

        vehicle_info = {
            "typ": self.car_type.value,
            "barva": self.color.value,
            "max_rychlost": speed,
            "spz": plate,
            "majitel": interaction.user.display_name,
            "datum_registrace": discord.utils.utcnow().strftime("%d.%m.%Y %H:%M")
        }

        user_data["registrovana_auta"][vehicle_id] = vehicle_info
        save_data(databaze)

        embed = discord.Embed(
            title="✅ Vozidlo úspěšně zaregistrováno",
            color=discord.Color.green()
        )
        embed.add_field(name="🚗 Typ", value=vehicle_info["typ"], inline=True)
        embed.add_field(name="🎨 Barva", value=vehicle_info["barva"], inline=True)
        embed.add_field(name="⚡ Max. rychlost", value=f"{vehicle_info['max_rychlost']} km/h", inline=True)
        embed.add_field(name="🔢 SPZ", value=vehicle_info["spz"], inline=True)
        embed.add_field(name="📅 Datum registrace", value=vehicle_info["datum_registrace"], inline=True)
        embed.add_field(name="👤 Majitel", value=vehicle_info["majitel"], inline=True)

        await interaction.response.send_message(embed=embed)

async def setup_vehicle_commands(tree, bot):

    @tree.command(name="registrovat-vozidlo", description="Zaregistruj své vozidlo do systému")
    async def registrovat_vozidlo(interaction: discord.Interaction):
        modal = VehicleRegistrationModal()
        await interaction.response.send_modal(modal)

    @tree.command(name="moje-vozidla", description="Zobraz svá zaregistrovaná vozidla")
    async def moje_vozidla(interaction: discord.Interaction):
        databaze = load_data()
        user_data = get_or_create_user(interaction.user.id, databaze)
        
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
                f"**Max. rychlost:** {vehicle_info['max_rychlost']} km/h\n"
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
        databaze = load_data()
        
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
        embed.add_field(name="⚡ Max. rychlost", value=f"{found_vehicle['max_rychlost']} km/h", inline=True)
        embed.add_field(name="👤 Majitel", value=owner_name, inline=True)
        embed.add_field(name="📅 Registrováno", value=found_vehicle["datum_registrace"], inline=True)

        await interaction.response.send_message(embed=embed)

    @tree.command(name="smazat-vozidlo", description="Smaž své zaregistrované vozidlo")
    @app_commands.describe(spz="SPZ vozidla, které chceš smazat")
    async def smazat_vozidlo(interaction: discord.Interaction, spz: str):
        spz = spz.upper().strip()
        databaze = load_data()
        user_data = get_or_create_user(interaction.user.id, databaze)
        
        vehicles = user_data.get("registrovana_auta", {})
        vehicle_to_remove = None
        
        for vehicle_id, vehicle_info in vehicles.items():
            if vehicle_info.get("spz") == spz:
                vehicle_to_remove = vehicle_id
                break
        
        if not vehicle_to_remove:
            await interaction.response.send_message(f"❌ Nemáš zaregistrované vozidlo se SPZ `{spz}`.", ephemeral=True)
            return

        del user_data["registrovana_auta"][vehicle_to_remove]
        save_data(databaze)
        
        await interaction.response.send_message(f"✅ Vozidlo se SPZ `{spz}` bylo úspěšně smazáno z registru.")

    @tree.command(name="vsechna-vozidla", description="Zobraz všechna zaregistrovaná vozidla (admin)")
    async def vsechna_vozidla(interaction: discord.Interaction):
        if not is_admin(interaction.user):
            await interaction.response.send_message("❌ Nemáš oprávnění použít tento příkaz.", ephemeral=True)
            return
            
        databaze = load_data()
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

        for vehicle in all_vehicles[:10]:  # Limit to first 10 to avoid embed limits
            vehicle_text = (
                f"**Majitel:** {vehicle['majitel']}\n"
                f"**Typ:** {vehicle['typ']}\n"
                f"**Barva:** {vehicle['barva']}\n"
                f"**Max. rychlost:** {vehicle['max_rychlost']} km/h"
            )
            embed.add_field(
                name=f"🔢 SPZ: {vehicle['spz']}",
                value=vehicle_text,
                inline=True
            )

        if len(all_vehicles) > 10:
            embed.set_footer(text=f"Zobrazeno prvních 10 z {len(all_vehicles)} vozidel")

        await interaction.response.send_message(embed=embed)
