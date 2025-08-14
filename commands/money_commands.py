
import datetime
import discord
from discord import app_commands
import json
from data_config import ROLE_ODMENY
from utils import get_or_create_user, save_data, is_admin, get_total_money, load_data

async def setup_money_commands(tree, bot):

    @tree.command(name="balance", description="Zobrazí finanční stav")
    @app_commands.describe(uzivatel="(Volitelné) Uživatel, jehož stav chceš zobrazit")
    async def balance(interaction: discord.Interaction, uzivatel: discord.Member = None):
        uzivatel = uzivatel or interaction.user
        databaze = load_data()
        data = get_or_create_user(uzivatel.id, databaze)

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

    @tree.command(name="pridej-penize", description="Přidá peníze hráči (admin)")
    @app_commands.describe(uzivatel="Uživatel, kterému chceš přidat peníze", castka="Kolik peněz chceš přidat")
    async def pridej_penize(interaction: discord.Interaction, uzivatel: discord.Member, castka: int):
        if not is_admin(interaction.user):
            await interaction.response.send_message("❌ Nemáš oprávnění použít tento příkaz.", ephemeral=True)
            return
        databaze = load_data()
        data = get_or_create_user(uzivatel.id, databaze)
        data["hotovost"] += castka
        data["penize"] = data["hotovost"] + data["bank"]
        save_data(databaze)
        await interaction.response.send_message(f"✅ Přidáno {castka}$ hráči {uzivatel.display_name}.")

    @tree.command(name="odeber-penize", description="Odebere peníze hráči (admin)")
    @app_commands.describe(uzivatel="Uživatel, kterému chceš odebrat peníze", castka="Kolik peněz chceš odebrat (nebo 'all' pro všechny)")
    async def odeber_penize(interaction: discord.Interaction, uzivatel: discord.Member, castka: str):
        if not is_admin(interaction.user):
            await interaction.response.send_message("❌ Nemáš oprávnění použít tento příkaz.", ephemeral=True)
            return
        databaze = load_data()
        data = get_or_create_user(uzivatel.id, databaze)

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
        save_data(databaze)
        await interaction.response.send_message(f"✅ Odebráno {actual_castka}$ hráči {uzivatel.display_name}.")

    @tree.command(name="reset-penize", description="Resetuje peníze hráče (admin)")
    @app_commands.describe(uzivatel="Uživatel, jehož peníze chceš vynulovat")
    async def reset_penize(interaction: discord.Interaction, uzivatel: discord.Member):
            if not is_admin(interaction.user):
                await interaction.response.send_message("❌ Nemáš oprávnění použít tento příkaz.", ephemeral=True)
                return
            databaze = load_data()
            data = get_or_create_user(uzivatel.id, databaze)
            data["hotovost"] = 0
            data["bank"] = 0
            data["penize"] = 0
            save_data(databaze)
            await interaction.response.send_message(f"♻️ Peníze hráče {uzivatel.display_name} byly vynulovány.")

    @tree.command(name="pay", description="Pošle peníze jinému hráči")
    @app_commands.describe(cil="Komu chceš poslat peníze", castka="Kolik peněz chceš poslat")
    async def posli_penize(interaction: discord.Interaction, cil: discord.Member, castka: int):
        if castka <= 0:
            await interaction.response.send_message("❌ Částka musí být větší než 0.", ephemeral=True)
            return
        databaze = load_data()
        odesilatel_data = get_or_create_user(interaction.user.id, databaze)
        prijemce_data = get_or_create_user(cil.id, databaze)

        total_money_odesilatel = get_total_money(odesilatel_data)
        if total_money_odesilatel < castka:
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

        save_data(databaze)
        await interaction.response.send_message(f"💸 Poslal jsi {castka}$ hráči {cil.display_name}.")

    @tree.command(name="vybrat", description="Vybere peníze z banky do peněženky")
    @app_commands.describe(castka="Částka, kterou chceš vybrat (nebo 'all' pro všechny)")
    async def vybrat(interaction: discord.Interaction, castka: str):
        databaze = load_data()
        data = get_or_create_user(interaction.user.id, databaze)

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
        save_data(databaze)

        await interaction.response.send_message(f"✅ Vybral jsi {actual_castka:,} $ z banky do peněženky.")

    @tree.command(name="vlozit", description="Vloží peníze z peněženky do banky")
    @app_commands.describe(castka="Částka, kterou chceš vložit (nebo 'all' pro všechny)")
    async def vlozit(interaction: discord.Interaction, castka: str):
        databaze = load_data()
        data = get_or_create_user(interaction.user.id, databaze)

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
        save_data(databaze)

        await interaction.response.send_message(f"✅ Vložil jsi {actual_castka:,} $ z peněženky do banky.")

    @tree.command(name="collect", description="Vybereš si týdenní výplatu podle svých rolí (každá má vlastní cooldown).")
    async def collect(interaction: discord.Interaction):
        now = datetime.datetime.utcnow()
        databaze = load_data()
        data = get_or_create_user(interaction.user.id, databaze)

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
        save_data(databaze)

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

    @tree.command(name="leaderboard", description="Zobrazí žebříček nejbohatších hráčů")
    @app_commands.describe(stranka="Číslo stránky leaderboardu")
    async def leaderboard(interaction: discord.Interaction, stranka: int = 1):
        with open("data.json", "r") as f:
            db = json.load(f)

        if not db:
            await interaction.response.send_message("❌ Žádná data k zobrazení.", ephemeral=True)
            return

        leaderboard = []
        for user_id, data in db.items():
            total = data.get("hotovost", 0) + data.get("bank", 0)
            leaderboard.append((int(user_id), total))

        leaderboard.sort(key=lambda x: x[1], reverse=True)

        stranka -= 1
        zaznamu_na_stranku = 10
        zacatek = stranka * zaznamu_na_stranku
        konec = zacatek + zaznamu_na_stranku
        strankovany = leaderboard[zacatek:konec]

        if not strankovany:
            await interaction.response.send_message("❌ Tato stránka neexistuje.", ephemeral=True)
            return

        embed = discord.Embed(
            title="💰 Leaderboard – Nejbohatší hráči",
            description=f"Stránka {stranka + 1}/{(len(leaderboard) + 9) // 10}",
            color=discord.Color.gold()
        )

        for index, (user_id, total) in enumerate(strankovany, start=zacatek + 1):
            user = interaction.guild.get_member(user_id)
            jmeno = user.display_name if user else f"<@{user_id}>"
            embed.add_field(
                name=f"#{index} – {jmeno}",
                value=f"💵 {total:,} $",
                inline=False
            )

        await interaction.response.send_message(embed=embed)
