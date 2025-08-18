import discord
from discord import app_commands
from utils import get_or_create_user, is_admin
import re
import random
import string

# Assume 'hraci' is your MongoDB collection object, and 'databaze' is not used.
# You would typically initialize this client and database in your main bot file.
# For demonstration purposes, let's assume 'hraci' is available.

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
        # Assume 'hraci' is accessible here. It should be initialized in your main bot file.
        # Example: from main_bot import hraci

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
        # Update bank balance in MongoDB
        # Assuming hraci is the collection object
        # hraci.update_one({"user_id": str(interaction.user.id)}, {"$inc": {"bank": -REGISTRATION_COST}})
        # For this example, we'll update the user_data dictionary temporarily
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

        # Check for existing SPZ in MongoDB
        existing_vehicle = hraci.find_one({"registrovana_auta.spz": plate})
        if existing_vehicle:
            await interaction.response.send_message(f"❌ SPZ `{plate}` již existuje! Zvolte jinou.", ephemeral=True)
            return

        # Determine the next vehicle ID
        user_profile = hraci.find_one({"user_id": str(interaction.user.id)})
        if not user_profile:
            user_profile = {"user_id": str(interaction.user.id), "registrovana_auta": {}}
            hraci.insert_one(user_profile)

        registrovana_auta = user_profile.get("registrovana_auta", {})
        vehicle_count = len(registrovana_auta) + 1
        next_id = f"vozidlo_{vehicle_count}"
        while f"registrovana_auta.{next_id}" in user_profile: # Check if this key already exists
            vehicle_count += 1
            next_id = f"vozidlo_{vehicle_count}"

        vehicle_data = {
            "typ": self.selected_car,
            "barva": self.color.value,
            "max_rychlost": speed,
            "spz": plate,
            "majitel": interaction.user.display_name,
            "datum_registrace": discord.utils.utcnow().strftime("%d.%m.%Y %H:%M")
        }

        # Update MongoDB with the new vehicle
        hraci.update_one(
            {"user_id": str(interaction.user.id)},
            {"$set": {f"registrovana_auta.{next_id}": vehicle_data}, "$inc": {"bank": -REGISTRATION_COST}} # Also decrease bank balance
        )


        embed = discord.Embed(
            title="✅ Vozidlo úspěšně zaregistrováno",
            description=f"💰 Cena registrace: {REGISTRATION_COST} ({cost_usd:.2f}$ USD)",
            color=discord.Color.green()
        )
        embed.add_field(name="🚗 Typ", value=vehicle_data["typ"], inline=True)
        embed.add_field(name="🎨 Barva", value=vehicle_data["barva"], inline=True)
        embed.add_field(name="⚡ Max. rychlost", value=f"{vehicle_data['max_rychlost']} mp/h", inline=True)
        embed.add_field(name="🔢 SPZ", value=vehicle_data["spz"], inline=True)
        embed.add_field(name="📅 Datum registrace", value=vehicle_data["datum_registrace"], inline=True)
        embed.add_field(name="👤 Majitel", value=vehicle_data["majitel"], inline=True)
        # Display updated bank balance
        updated_user_data = hraci.find_one({"user_id": str(interaction.user.id)})
        embed.add_field(name="💵 Zůstatek po registraci", value=f"{updated_user_data.get('bank', 0)}💰", inline=True)

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
        # Fetch user data from MongoDB
        user_profile = hraci.find_one({"user_id": str(interaction.user.id)})

        if not user_profile:
            await interaction.response.send_message("❌ Nemáš žádná zaregistrovaná vozidla.", ephemeral=True)
            return

        vehicles = user_profile.get("registrovana_auta", {})

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

        # Fetch user data from MongoDB
        user_profile = hraci.find_one({"user_id": str(user.id)})

        if not user_profile:
            await interaction.response.send_message(f"❌ Uživatel **{user.display_name}** nemá žádná registrovaná vozidla.", ephemeral=True)
            return

        vehicles = user_profile.get("registrovana_auta", {})

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

        # Find vehicle by SPZ in MongoDB
        found_vehicle = hraci.find_one({"registrovana_auta.spz": spz})

        if not found_vehicle:
            await interaction.response.send_message(f"❌ Vozidlo se SPZ `{spz}` nebylo nalezeno.", ephemeral=True)
            return

        # Extract the specific vehicle data and owner name
        owner_name = found_vehicle.get("majitel", "Neznámý") # If majitel is not directly in the vehicle dict, it needs to be fetched.
                                                            # Assuming 'majitel' is stored within the vehicle dict for simplicity here.
                                                            # If 'majitel' is the display name of the user who registered it, you might need to retrieve it differently.

        # To get the exact vehicle_info and owner name correctly, we need to iterate through the found_vehicle's registered_cars
        vehicle_info = None
        for v_id, v_data in found_vehicle.get("registrovana_auta", {}).items():
            if v_data.get("spz") == spz:
                vehicle_info = v_data
                # If 'majitel' is not stored in the vehicle data, you'd need to look up the user_id associated with 'found_vehicle'
                # For now, assume 'majitel' is in vehicle_info as per original code.
                owner_name = vehicle_info.get("majitel", "Neznámý")
                break


        if not vehicle_info: # Should not happen if found_vehicle is not None, but as a safeguard
            await interaction.response.send_message(f"❌ Vozidlo se SPZ `{spz}` nebylo nalezeno.", ephemeral=True)
            return

        embed = discord.Embed(
            title=f"🔍 Informace o vozidle - {spz}",
            color=discord.Color.gold()
        )
        embed.add_field(name="🚗 Typ", value=vehicle_info["typ"], inline=True)
        embed.add_field(name="🎨 Barva", value=vehicle_info["barva"], inline=True)
        embed.add_field(name="⚡ Max. rychlost", value=f"{vehicle_info['max_rychlost']} mp/h", inline=True)
        embed.add_field(name="👤 Majitel", value=owner_name, inline=True)
        embed.add_field(name="📅 Registrováno", value=vehicle_info["datum_registrace"], inline=True)

        await interaction.response.send_message(embed=embed)

    @tree.command(name="smazat-vozidlo", description="Smaž své zaregistrované vozidlo")
    @app_commands.describe(spz="SPZ vozidla, které chceš smazat")
    async def smazat_vozidlo(interaction: discord.Interaction, spz: str):
        spz = spz.upper().strip()

        # Find the vehicle by SPZ and get its key (vehicle_id)
        user_profile = hraci.find_one({"user_id": str(interaction.user.id), "registrovana_auta.spz": spz})

        if not user_profile:
            await interaction.response.send_message(f"❌ Nemáš zaregistrované vozidlo s registrační značkou `{spz}`.", ephemeral=True)
            return

        vehicle_key_to_remove = None
        for key, value in user_profile.get("registrovana_auta", {}).items():
            if value.get("spz") == spz:
                vehicle_key_to_remove = key
                break

        if not vehicle_key_to_remove:
             await interaction.response.send_message(f"❌ Chyba při hledání vozidla s SPZ `{spz}`. Prosím, zkuste to znovu.", ephemeral=True)
             return

        # Remove vehicle from MongoDB
        hraci.update_one(
            {"user_id": str(interaction.user.id)},
            {"$unset": {f"registrovana_auta.{vehicle_key_to_remove}": ""}}
        )

        await interaction.response.send_message(f"✅ Vozidlo s registrační značkou `{spz}` bylo úspěšně smazáno z registru.")

    @tree.command(name="vsechny-registrace", description="Zobraz všechna zaregistrovaná vozidla (admin)")
    async def vsechna_vozidla(interaction: discord.Interaction):
        if not is_admin(interaction.user):
            await interaction.response.send_message("❌ Nemáš oprávnění použít tento příkaz.", ephemeral=True)
            return

        # Fetch all vehicles from MongoDB
        all_vehicles_data = hraci.aggregate([
            {"$match": {"registrovana_auta": {"$exists": True, "$ne": {}}}},
            {"$project": {"_id": 0, "registrovana_auta": 1}}
        ])

        all_vehicles = []
        for user_doc in all_vehicles_data:
            for vehicle_key, vehicle_info in user_doc.get("registrovana_auta", {}).items():
                # Add the owner's name to the vehicle info if not already present
                # This assumes the user_id is available in the user_doc from which we are iterating
                # If not, you would need to fetch the user document for each iteration or modify the aggregation
                # For now, let's assume we can get the user_id from the context of the iteration
                # A better approach might be to get the user_id from the _id field of the user_doc if it's the user_id itself
                # or by projecting it in the aggregation.

                # For simplicity in this example, let's assume we can get user_id from user_doc._id if user_id is the _id
                # If user_id is a field, you'd need to include it in the projection.
                # Let's add a placeholder for owner_name and assume it's handled or fetched separately if needed.

                # Example: Fetching owner name if user_id is available in user_doc._id
                # user_id_str = str(user_doc.get('_id')) # Assuming _id is the user_id string
                # owner_name = "Neznámý"
                # if user_id_str:
                #     user_profile_for_name = hraci.find_one({"user_id": user_id_str})
                #     if user_profile_for_name:
                #         owner_name = user_profile_for_name.get("display_name", "Neznámý") # Assuming display_name is stored

                # As per original code, 'majitel' is in vehicle_info. If it's not, this needs adjustment.
                # If 'majitel' is not stored, we'd need to fetch the user document using the user_id associated with the current user_doc.
                # Let's assume 'majitel' is correctly populated in the vehicle_info from previous operations.
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
                f"**Majitel:** {vehicle.get('majitel', 'Neznámý')}\n" # Use .get for safety
                f"**Typ:** {vehicle.get('typ', 'Neznámý')}\n"
                f"**Barva:** {vehicle.get('barva', 'Neznámý')}\n"
                f"**Max. rychlost:** {vehicle.get('max_rychlost', 'Neznámý')} mp/h"
            )
            embed.add_field(
                name=f"🔢 SPZ: {vehicle.get('spz', 'Neznámá')}",
                value=vehicle_text,
                inline=True
            )

        if len(all_vehicles) > 10:
            embed.set_footer(text=f"Zobrazeno prvních 10 z {len(all_vehicles)} vozidel")

        await interaction.response.send_message(embed=embed)