import datetime
import discord
from discord import app_commands
import asyncio
import random
from data_config import RECEPTY, VYROBA_COOLDOWN, DROGY_SEZNAM, UCINKY_DROG, VECI_SEZNAM
from utils import get_or_create_user, is_admin, has_permission, hraci

async def setup_drug_commands(tree, bot):

    async def autocomplete_drogy(interaction: discord.Interaction, current: str):
        return [
            app_commands.Choice(name=drug, value=drug)
            for drug in DROGY_SEZNAM if current.lower() in drug.lower()
        ][:25]

    async def autocomplete_veci(interaction: discord.Interaction, current: str):
        return [
            app_commands.Choice(name=vec, value=vec)
            for vec in VECI_SEZNAM if current.lower() in vec.lower()
        ][:25]

    async def autocomplete_drogy_ve_inventari(interaction: discord.Interaction, current: str):
        data = get_or_create_user(interaction.user.id)
        drogy = data.get("drogy", {})
        options = [
            app_commands.Choice(name=droga, value=droga)
            for droga in drogy.keys()
            if current.lower() in droga.lower()
        ][:25]
        return options

    @tree.command(name="vyrob", description="Vyrob nelegální látku")
    @app_commands.describe(droga="Druh drogy", mnozstvi="Kolik gramů chceš vyrobit")
    @app_commands.autocomplete(droga=autocomplete_drogy)
    async def vyrob(interaction: discord.Interaction, droga: str, mnozstvi: int = 10):
        uzivatel = interaction.user

        data = get_or_create_user(uzivatel.id)

        if mnozstvi % 10 != 0 or mnozstvi <= 0:
            return await interaction.response.send_message("❌ Výroba je možná pouze po 10g dávkách (např. 10, 20, 30...).", ephemeral=True)

        recept = RECEPTY.get(droga)
        if not recept:
            return await interaction.response.send_message("❌ Tato droga neexistuje.", ephemeral=True)
        nyni = datetime.datetime.utcnow()
        posledni = data.get("last_vyroba")
        if posledni:
            rozdil = (nyni - datetime.datetime.fromisoformat(posledni)).total_seconds()
            if rozdil < VYROBA_COOLDOWN * 60:
                zbyva = int((VYROBA_COOLDOWN * 60 - rozdil) / 60)
                return await interaction.response.send_message(f"⏳ Musíš počkat {zbyva} minut před další výrobou.", ephemeral=True)

        veci = data.get("veci", {})
        drogy = data.get("drogy", {})
        davky = mnozstvi // 10
        for surovina, pocet in recept["suroviny"].items():
            if veci.get(surovina, 0) < pocet * davky:
                return await interaction.response.send_message(f"❌ Nemáš dostatek `{surovina}`.", ephemeral=True)

        for nastroj, pocet in recept["nastroje"].items():
            if veci.get(nastroj, 0) < pocet:
                return await interaction.response.send_message(f"❌ Chybí ti nástroj `{nastroj}`.", ephemeral=True)

        # Prepare updates for MongoDB
        update_dict = {}

        # Spotřeba surovin
        for surovina, mnozstvi_potreba in recept.get("suroviny", {}).items():
            new_amount = veci.get(surovina, 0) - (mnozstvi_potreba * davky)
            if new_amount <= 0:
                update_dict[f"veci.{surovina}"] = {"$unset": ""}
            else:
                update_dict[f"veci.{surovina}"] = new_amount

        # Přidání dokončené drogy
        new_drug_amount = drogy.get(droga, 0) + mnozstvi
        update_dict[f"drogy.{droga}"] = new_drug_amount

        # Update in MongoDB
        set_updates = {k: v for k, v in update_dict.items() if not isinstance(v, dict)}
        unset_updates = {k: "" for k, v in update_dict.items() if isinstance(v, dict) and "$unset" in v}

        update_operations = {}
        if set_updates:
            update_operations["$set"] = set_updates
        if unset_updates:
            update_operations["$unset"] = unset_updates

        if update_operations:
            hraci.update_one({"user_id": str(uzivatel.id)}, update_operations)

        data["last_vyroba"] = nyni.isoformat()
        celkovy_cas = recept["cas"] * davky
        await interaction.response.send_message(
            f"🧪 Začal jsi vyrábět {mnozstvi}g `{droga}`.\n⏳ Dokončení za {celkovy_cas} minut...", ephemeral=True)

        async def dokonci_vyrobu():
            await asyncio.sleep(celkovy_cas * 60)

            if random.random() < recept["selhani"]:
                for nastroj, pocet in recept["nastroje"].items():
                    if nastroj in veci:
                        veci[nastroj] -= pocet
                        if veci[nastroj] <= 0:
                            veci.pop(nastroj)

                try:
                    await uzivatel.send(f"❌ Výroba {mnozstvi}g `{droga}` selhala. Přišel jsi o suroviny i nástroje.")
                except:
                    pass
                return

            try:
                await uzivatel.send(f"✅ Výroba dokončena: {mnozstvi}g `{droga}` bylo přidáno do inventáře.")
            except:
                pass

        asyncio.create_task(dokonci_vyrobu())

    @tree.command(name="pozij-drogu", description="Požij drogu z inventáře a získej dočasné účinky")
    @app_commands.describe(
        droga="Droga, kterou chceš použít",
        mnozstvi="Kolik chceš požít (např. 0.5g, 500mg, all)"
    )
    @app_commands.autocomplete(droga=autocomplete_drogy_ve_inventari)
    async def pozij_drogu(interaction: discord.Interaction, droga: str, mnozstvi: str):
        uzivatel = interaction.user

        data = get_or_create_user(uzivatel.id)
        drogy = data.get("drogy", {})

        if droga not in drogy:
            await interaction.response.send_message("❌ Tuto drogu nemáš v inventáři.", ephemeral=True)
            return

        inventar_mnozstvi = drogy[droga]

        mnozstvi = mnozstvi.strip().lower()
        try:
            if mnozstvi == "all":
                mnozstvi_g = inventar_mnozstvi
            elif mnozstvi.endswith("mg"):
                mnozstvi_g = float(mnozstvi[:-2].strip()) / 1000
            elif mnozstvi.endswith("g"):
                mnozstvi_g = float(mnozstvi[:-1].strip())
            else:
                mnozstvi_g = float(mnozstvi)
        except ValueError:
            await interaction.response.send_message("❌ Neplatný formát. Zadej třeba `0.5g`, `500mg`, nebo `all`.", ephemeral=True)
            return

        if mnozstvi_g <= 0:
            await interaction.response.send_message("❌ Množství musí být větší než 0.", ephemeral=True)
            return

        if mnozstvi_g > inventar_mnozstvi:
            await interaction.response.send_message(f"❌ Máš pouze {inventar_mnozstvi:.2f}g `{droga}`.", ephemeral=True)
            return

        ucinky = UCINKY_DROG.get(droga, None)
        if not ucinky:
            ucinek_text = "❓ Neznámé účinky"
            priznaky = []
            trvani = 5
        else:
            ucinek_text = ucinky["base"]
            priznaky = ucinky["priznaky"]
            trvani = ucinky["trvani"]

        if mnozstvi_g >= 2.5:
            extra = "🚨 **Silná dávka! Možné záchvaty, halucinace, nebo smrtelné riziko.**"
            priznaky += ["💀 Dezorientace", "🤢 Nevolnost", "💤 Kolaps"]
        elif mnozstvi_g >= 1.0:
            extra = "⚠️ **Silnější účinky. Výrazné změny chování.**"
            priznaky += ["😵 Ztráta rovnováhy", "💬 Zmatečný projev"]
        else:
            extra = ""

        # Odebrání drogy z inventáře
        if data["drogy"][droga] == mnozstvi_g:
            hraci.update_one(
                {"user_id": str(uzivatel.id)},
                {"$unset": {f"drogy.{droga}": ""}}
            )
        else:
            hraci.update_one(
                {"user_id": str(uzivatel.id)},
                {"$set": {f"drogy.{droga}": data["drogy"][droga] - mnozstvi_g}}
            )


        embed = discord.Embed(
            title=f"💊 {droga} použita",
            description=(
                f"**{interaction.user.display_name}** právě požil {mnozstvi_g:.2f}g `{droga}`.\n\n"
                f"🧠 **Účinek:** {ucinek_text}\n"
                f"⏳ **Doba trvání:** {trvani * mnozstvi_g:.1f} minut (OOC)\n"
                f"{extra}\n\n"
                f"🩺 **Příznaky:**\n" + "\n".join(f"- {p}" for p in priznaky)
            ),
            color=discord.Color.purple()
        )
        await interaction.response.send_message(embed=embed)

    @tree.command(name="recepty", description="Zobrazí seznam receptů pro výrobu drog")
    async def recepty(interaction: discord.Interaction):
        embed = discord.Embed(
            title="🧪 Recepty na výrobu drog",
            description="Zde je seznam všech dostupných drog, jejich požadavků a šancí na selhání.",
            color=discord.Color.dark_red()
        )

        for droga, info in RECEPTY.items():
            suroviny = "\n".join(f"- {nazev} ×{pocet}" for nazev, pocet in info["suroviny"].items())
            nastroje = "\n".join(f"- {nazev} ×{pocet}" for nazev, pocet in info["nastroje"].items())
            cas = info["cas"]
            selhani = int(info["selhani"] * 100)

            embed.add_field(
                name=f"💊 {droga}",
                value=(
                    f"**🧂 Suroviny:**\n{suroviny}\n"
                    f"**🛠️ Nástroje:**\n{nastroje}\n"
                    f"⏳ **Čas výroby:** {cas} minut / 10g\n"
                    f"⚠️ **Šance na selhání:** {selhani}%"
                ),
                inline=False
            )

        await interaction.response.send_message(embed=embed)

    @tree.command(name="pridej-veci", description="Přidej věci do inventáře uživatele (admin)")
    @app_commands.describe(uzivatel="Uživatel, kterému přidáš věci", vec="Název věci", mnozstvi="Počet kusů")
    @app_commands.autocomplete(vec=autocomplete_veci)
    async def pridej_veci(interaction: discord.Interaction, uzivatel: discord.Member, vec: str, mnozstvi: int):
        if not is_admin(interaction.user):
            await interaction.response.send_message("❌ Nemáš oprávnění použít tento příkaz.", ephemeral=True)
            return


        data = get_or_create_user(uzivatel.id)
        veci = data.get("veci", {})
        veci[vec] = veci.get(vec, 0) + mnozstvi
        data["veci"] = veci

        hraci.update_one(
            {"user_id": str(uzivatel.id)},
            {"$set": {f"veci.{vec}": veci[vec]}}
        )

        await interaction.response.send_message(f"✅ Přidáno {mnozstvi}× `{vec}` uživateli {uzivatel.display_name}.", ephemeral=True)

    @tree.command(name="pridej-drogy", description="Přidej drogy do inventáře uživatele (admin)")
    @app_commands.describe(uzivatel="Uživatel, kterému přidáš drogy", droga="Název drogy", mnozstvi="Počet gramů")
    @app_commands.autocomplete(droga=autocomplete_drogy)
    async def pridej_drogy(interaction: discord.Interaction, uzivatel: discord.Member, droga: str, mnozstvi: int):
        if not is_admin(interaction.user):
            await interaction.response.send_message("❌ Nemáš oprávnění použít tento příkaz.", ephemeral=True)
            return


        data = get_or_create_user(uzivatel.id)
        drogy = data.get("drogy", {})
        drogy[droga] = drogy.get(droga, 0) + mnozstvi
        data["drogy"] = drogy

        hraci.update_one(
            {"user_id": str(uzivatel.id)},
            {"$set": {f"drogy.{droga}": drogy[droga]}}
        )

        await interaction.response.send_message(f"✅ Přidáno {mnozstvi}g `{droga}` uživateli {uzivatel.display_name}.", ephemeral=True)

    async def autocomplete_odeber_veci(interaction: discord.Interaction, current: str):
        uzivatel = None
        for option in interaction.data.get("options", []):
            if option["name"] == "uzivatel":
                try:
                    uzivatel = await interaction.guild.fetch_member(option["value"])
                except:
                    pass
                break
        if not uzivatel:
            return []


        data = get_or_create_user(uzivatel.id)
        veci = data.get("veci", {})
        return [
            app_commands.Choice(name=vec, value=vec)
            for vec in veci.keys() if current.lower() in vec.lower()
        ][:25]

    async def autocomplete_odeber_drogy(interaction: discord.Interaction, current: str):
        uzivatel = None
        for option in interaction.data.get("options", []):
            if option["name"] == "uzivatel":
                try:
                    uzivatel = await interaction.guild.fetch_member(option["value"])
                except:
                    pass
                break
        if not uzivatel:
            return []


        data = get_or_create_user(uzivatel.id)
        drogy = data.get("drogy", {})
        return [
            app_commands.Choice(name=droga, value=droga)
            for droga in drogy.keys() if current.lower() in droga.lower()
        ][:25]

    @tree.command(name="odeber-veci", description="Odeber věci z inventáře uživatele (admin/policie)")
    @app_commands.describe(uzivatel="Uživatel, kterému odebereš věci", vec="Název věci", mnozstvi="Počet kusů")
    @app_commands.autocomplete(vec=autocomplete_odeber_veci)
    async def odeber_veci(interaction: discord.Interaction, uzivatel: discord.Member, vec: str, mnozstvi: int):
        if not has_permission(interaction.user):
            await interaction.response.send_message("❌ Nemáš oprávnění použít tento příkaz.", ephemeral=True)
            return


        data = get_or_create_user(uzivatel.id)
        veci = data.get("veci", {})
        if vec not in veci or veci[vec] < mnozstvi:
            await interaction.response.send_message(f"❌ Uživateli {uzivatel.display_name} chybí {mnozstvi}× `{vec}`.", ephemeral=True)
            return

        if veci[vec] <= mnozstvi:
            hraci.update_one(
                {"user_id": str(uzivatel.id)},
                {"$unset": {f"veci.{vec}": ""}}
            )
        else:
            hraci.update_one(
                {"user_id": str(uzivatel.id)},
                {"$set": {f"veci.{vec}": veci[vec] - mnozstvi}}
            )

        await interaction.response.send_message(f"✅ Odebráno {mnozstvi}× `{vec}` uživateli {uzivatel.display_name}.", ephemeral=True)

    @tree.command(name="odeber-drogy", description="Odeber drogy z inventáře uživatele (admin/policie)")
    @app_commands.describe(uzivatel="Uživatel, kterému odebereš drogy", droga="Název drogy", mnozstvi="Počet gramů")
    @app_commands.autocomplete(droga=autocomplete_odeber_drogy)
    async def odeber_drogy(interaction: discord.Interaction, uzivatel: discord.Member, droga: str, mnozstvi: int):
        if not has_permission(interaction.user):
            await interaction.response.send_message("❌ Nemáš oprávnění použít tento příkaz.", ephemeral=True)
            return


        data = get_or_create_user(uzivatel.id)
        drogy = data.get("drogy", {})
        if droga not in drogy or drogy[droga] < mnozstvi:
            await interaction.response.send_message(f"❌ Uživateli {uzivatel.display_name} chybí {mnozstvi}g `{droga}`.", ephemeral=True)
            return

        if drogy[droga] <= mnozstvi:
            hraci.update_one(
                {"user_id": str(uzivatel.id)},
                {"$unset": {f"drogy.{droga}": ""}}
            )
        else:
            hraci.update_one(
                {"user_id": str(uzivatel.id)},
                {"$set": {f"drogy.{droga}": drogy[droga] - mnozstvi}}
            )

        await interaction.response.send_message(f"✅ Odebráno {mnozstvi}g `{droga}` uživateli {uzivatel.display_name}.", ephemeral=True)