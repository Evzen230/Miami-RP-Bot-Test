import datetime
import discord
from discord import app_commands
import json
from data_config import ROLE_ODMENY
from utils import get_or_create_user, is_admin, get_total_money, hraci

async def setup_money_commands(tree, bot):

    # --- BALANCE ---
    @tree.command(name="balance", description="Zobrazí finanční stav")
    @app_commands.describe(uzivatel="(Volitelné) Uživatel, jehož stav chceš zobrazit")
    async def balance(interaction: discord.Interaction, uzivatel: discord.Member = None):
        uzivatel = uzivatel or interaction.user
        data = get_or_create_user(uzivatel.id)

        penize = data.get("penize", 0)
        hotovost = data.get("hotovost", 0)
        bank = data.get("bank", 0)

        embed = discord.Embed(
            title=f"💰 Finanční přehled pro {uzivatel.display_name}",
            color=discord.Color.gold()
        )
        embed.add_field(name="💵 Celkem", value=f"{penize:,} $", inline=False)
        embed.add_field(name="💳 Hotovost", value=f"{hotovost:,} $", inline=True)
        embed.add_field(name="🏦 Banka", value=f"{bank:,} $", inline=True)

        await interaction.response.send_message(embed=embed)

    # --- PRIDEJ PENIZE ---
    @tree.command(name="pridej-penize", description="Přidá peníze hráči (admin)")
    @app_commands.describe(uzivatel="Uživatel, kterému chceš přidat peníze", castka="Kolik peněz chceš přidat")
    async def pridej_penize(interaction: discord.Interaction, uzivatel: discord.Member, castka: int):
            if not is_admin(interaction.user):
                await interaction.response.send_message("❌ Nemáš oprávnění použít tento příkaz.", ephemeral=True)
                return

            data = get_or_create_user(uzivatel.id)
            data["hotovost"] += castka
            data["penize"] = data["hotovost"] + data["bank"]

            # aktualizace MongoDB
            hraci.update_one(
                {"user_id": str(uzivatel.id)},
                {"$set": {"hotovost": data["hotovost"], "bank": data["bank"], "penize": data["penize"]}}
            )

            await interaction.response.send_message(f"✅ Přidáno {castka}$ hráči {uzivatel.display_name}.")


    # --- ODEBER PENIZE ---
    @tree.command(name="odeber-penize", description="Odebere peníze hráči (admin)")
    @app_commands.describe(uzivatel="Uživatel, kterému chceš odebrat peníze", castka="Kolik peněz chceš odebrat (nebo 'all' pro všechny)")
    async def odeber_penize(interaction: discord.Interaction, uzivatel: discord.Member, castka: str):
        if not is_admin(interaction.user):
            await interaction.response.send_message("❌ Nemáš oprávnění použít tento příkaz.", ephemeral=True)
            return

        data = get_or_create_user(uzivatel.id)

        if castka.lower() == "all":
            actual_castka = data["hotovost"] + data["bank"]
            data["hotovost"] = 0
            data["bank"] = 0
        else:
            try:
                actual_castka = int(castka)
                if actual_castka <= 0:
                    await interaction.response.send_message("❌ Částka musí být větší než 0.", ephemeral=True)
                    return
            except ValueError:
                await interaction.response.send_message("❌ Neplatná částka. Použij číslo nebo 'all'.", ephemeral=True)
                return

            if data["hotovost"] >= actual_castka:
                data["hotovost"] -= actual_castka
            else:
                remaining = actual_castka - data["hotovost"]
                data["hotovost"] = 0
                data["bank"] -= remaining
                if data["bank"] < 0:
                    data["bank"] = 0

        data["penize"] = data["hotovost"] + data["bank"]
        # Update in MongoDB
        hraci.update_one(
            {"user_id": str(uzivatel.id)},
            {"$set": {
                "hotovost": data["hotovost"],
                "bank": data["bank"],
                "penize": data["penize"]
            }}
        )
        await interaction.response.send_message(f"✅ Odebráno {actual_castka}$ hráči {uzivatel.display_name}.")


    # --- RESET PENIZE ---
    @tree.command(name="reset-penize", description="Resetuje peníze hráče (admin)")
    @app_commands.describe(uzivatel="Uživatel, jehož peníze chceš vynulovat")
    async def reset_penize(interaction: discord.Interaction, uzivatel: discord.Member):
        if not is_admin(interaction.user):
            await interaction.response.send_message("❌ Nemáš oprávnění použít tento příkaz.", ephemeral=True)
            return

        data = get_or_create_user(uzivatel.id)

        # aktualizace v MongoDB
        hraci.update_one(
            {"user_id": str(uzivatel.id)},
            {"$set": {"hotovost": 0, "bank": 0, "penize": 0}}
        )

        await interaction.response.send_message(f"♻️ Peníze hráče {uzivatel.display_name} byly vynulovány.")


    # --- PAY ---
    @tree.command(name="pay", description="Pošle peníze jinému hráči")
    @app_commands.describe(cil="Komu chceš poslat peníze", castka="Kolik peněz chceš poslat")
    async def posli_penize(interaction: discord.Interaction, cil: discord.Member, castka: int):
        if castka <= 0:
            await interaction.response.send_message("❌ Částka musí být větší než 0.", ephemeral=True)
            return

        odesilatel_data = get_or_create_user(interaction.user.id)
        prijemce_data = get_or_create_user(cil.id)

        if get_total_money(odesilatel_data) < castka:
            await interaction.response.send_message("❌ Nemáš dostatek peněz.", ephemeral=True)
            return

        remaining_to_remove = castka
        if odesilatel_data["hotovost"] >= remaining_to_remove:
            odesilatel_data["hotovost"] -= remaining_to_remove
        else:
            remaining_to_remove -= odesilatel_data["hotovost"]
            odesilatel_data["hotovost"] = 0
            odesilatel_data["bank"] -= remaining_to_remove

        prijemce_data["hotovost"] += castka

        odesilatel_data["penize"] = odesilatel_data["hotovost"] + odesilatel_data["bank"]
        prijemce_data["penize"] = prijemce_data["hotovost"] + prijemce_data["bank"]

        # Update in MongoDB for sender
        hraci.update_one(
            {"user_id": str(interaction.user.id)},
            {"$set": {
                "hotovost": odesilatel_data["hotovost"],
                "bank": odesilatel_data["bank"],
                "penize": odesilatel_data["penize"]
            }}
        )
        # Update in MongoDB for receiver
        hraci.update_one(
            {"user_id": str(cil.id)},
            {"$set": {
                "hotovost": prijemce_data["hotovost"],
                "bank": prijemce_data["bank"],
                "penize": prijemce_data["penize"]
            }}
        )

        await interaction.response.send_message(f"💸 Poslal jsi {castka}$ hráči {cil.display_name}.")
    # --- VYBRAT ---
    @tree.command(name="vybrat", description="Vybere peníze z banky do peněženky")
    @app_commands.describe(castka="Částka, kterou chceš vybrat (nebo 'all' pro všechny)")
    async def vybrat(interaction: discord.Interaction, castka: str):
        data = get_or_create_user(interaction.user.id)
        if castka.lower() == "all":
            actual_castka = data.get("bank", 0)
            if actual_castka <= 0:
                await interaction.response.send_message("❌ Nemáš žádné peníze v bance.", ephemeral=True)
                return
            data["bank"] = 0
            data["hotovost"] += actual_castka
        else:
            try:
                actual_castka = int(castka)
                if actual_castka <= 0:
                    await interaction.response.send_message("❌ Částka musí být větší než 0.", ephemeral=True)
                    return
            except ValueError:
                await interaction.response.send_message("❌ Neplatná částka. Použij číslo nebo 'all'.", ephemeral=True)
                return
            if data.get("bank", 0) < actual_castka:
                await interaction.response.send_message("❌ Nemáš dostatek peněz v bance.", ephemeral=True)
                return
            data["bank"] -= actual_castka
            data["hotovost"] += actual_castka
        data["penize"] = data["hotovost"] + data["bank"]
        # Update in MongoDB
        hraci.update_one(
            {"user_id": str(interaction.user.id)},
            {"$set": {
                "bank": data["bank"],
                "hotovost": data["hotovost"],
                "penize": data["penize"]
            }}
        )
        await interaction.response.send_message(f"✅ Vybral jsi {actual_castka:,} $ z banky do peněženky.")

    # --- VLOZIT ---
    @tree.command(name="vlozit", description="Vloží peníze z peněženky do banky")
    @app_commands.describe(castka="Částka, kterou chceš vložit (nebo 'all' pro všechny)")
    async def vlozit(interaction: discord.Interaction, castka: str):
        data = get_or_create_user(interaction.user.id)
        if castka.lower() == "all":
            actual_castka = data.get("hotovost", 0)
            if actual_castka <= 0:
                await interaction.response.send_message("❌ Nemáš žádné peníze v peněžence.", ephemeral=True)
                return
            data["hotovost"] = 0
            data["bank"] += actual_castka
        else:
            try:
                actual_castka = int(castka)
                if actual_castka <= 0:
                    await interaction.response.send_message("❌ Částka musí být větší než 0.", ephemeral=True)
                    return
            except ValueError:
                await interaction.response.send_message("❌ Neplatná částka. Použij číslo nebo 'all'.", ephemeral=True)
                return
            if data.get("hotovost", 0) < actual_castka:
                await interaction.response.send_message("❌ Nemáš dostatek peněz v peněžence.", ephemeral=True)
                return
            data["hotovost"] -= actual_castka
            data["bank"] += actual_castka
        data["penize"] = data["hotovost"] + data["bank"]
        # Update in MongoDB
        hraci.update_one(
            {"user_id": str(interaction.user.id)},
            {"$set": {
                "hotovost": data["hotovost"],
                "bank": data["bank"],
                "penize": data["penize"]
            }}
        )
        await interaction.response.send_message(f"✅ Vložil jsi {actual_castka:,} $ z peněženky do banky.")

    # --- COLLECT ---
    @tree.command(name="collect", description="Vybereš si týdenní výplatu podle svých rolí (každá má vlastní cooldown).")
    async def collect(interaction: discord.Interaction):
        now = datetime.datetime.utcnow()
        data = get_or_create_user(interaction.user.id)
        if "collect_timestamps" not in data:
            data["collect_timestamps"] = {}
        user_role_ids = [role.id for role in interaction.user.roles]
        vyplaceno = 0
        vyplacene_role = []
        cekajici_role = []
        for role_id, castka in ROLE_ODMENY.items():
            if role_id not in user_role_ids:
                continue
            posledni = data["collect_timestamps"].get(str(role_id))
            if posledni:
                posledni_cas = datetime.datetime.fromisoformat(posledni)
                rozdil = now - posledni_cas
                if rozdil < datetime.timedelta(days=7):
                    zbývá = datetime.timedelta(days=7) - rozdil
                    hodiny, zbytek = divmod(zbývá.total_seconds(), 3600)
                    minuty = int((zbytek % 3600) // 60)
                    cekajici_role.append((role_id, hodiny, minuty))
                    continue
            vyplaceno += castka
            vyplacene_role.append((role_id, castka))
            data["collect_timestamps"][str(role_id)] = now.isoformat()
        data["hotovost"] = data.get("hotovost", 0) + vyplaceno
        # Update in MongoDB
        hraci.update_one(
            {"user_id": str(interaction.user.id)},
            {"$set": {
                "hotovost": data["hotovost"],
                "penize": data["hotovost"] + data["bank"],
                f"collect_timestamps.{role_id}": now.isoformat()
            }}
        )
        embed = discord.Embed(
            title="💰 Týdenní výplata",
            color=discord.Color.green()
        )
        if vyplacene_role:
            popis = ""
            for role_id, castka in vyplacene_role:
                role_obj = discord.utils.get(interaction.guild.roles, id=role_id)
                nazev = role_obj.name if role_obj else f"Role ID {role_id}"
                popis += f"✅ **{nazev}**: +{castka:,} $\n"
            embed.add_field(name="💸 Vyplaceno", value=popis, inline=False)
        if cekajici_role:
            cekani = ""
            for role_id, h, m in cekajici_role:
                role_obj = discord.utils.get(interaction.guild.roles, id=role_id)
                nazev = role_obj.name if role_obj else f"Role ID {role_id}"
                cekani += f"⏳ **{nazev}** – za {int(h)}h {int(m)}m\n"
            embed.add_field(name="🕒 Nelze vybrat (ještě cooldown)", value=cekani, inline=False)
        if not vyplacene_role:
            embed.description = "❌ Tento týden už sis vybral odměnu za všechny své role."
        await interaction.response.send_message(embed=embed, ephemeral=True)