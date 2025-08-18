import discord
from discord import app_commands
from data_config import AUTA, CENY_ZBRANI, CENY_VECI, VECI_SEZNAM, DROGY_SEZNAM
from utils import get_or_create_user, get_total_money, log_action

# Placeholder for MongoDB collection, assuming it's initialized elsewhere
# For example: hraci = db["users"]

class ConfirmationView(discord.ui.View):
    def __init__(self, prodavajici, kupec, item, item_type, cena):
        super().__init__(timeout=60.0)
        self.prodavajici = prodavajici
        self.kupec = kupec
        self.item = item
        self.item_type = item_type
        self.cena = cena
        self.result = None

    @discord.ui.button(label='✅ Potvrdit nákup', style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.kupec.id:
            await interaction.response.send_message("❌ Pouze kupující může potvrdit nákup.", ephemeral=True)
            return

        self.result = True
        self.stop()
        await interaction.response.edit_message(content=f"✅ {self.kupec.display_name} potvrdil nákup!", view=None)

    @discord.ui.button(label='❌ Zrušit', style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id not in [self.kupec.id, self.prodavajici.id]:
            await interaction.response.send_message("❌ Pouze kupující nebo prodávající může zrušit obchod.", ephemeral=True)
            return

        self.result = False
        self.stop()
        await interaction.response.edit_message(content=f"❌ Obchod byl zrušen.", view=None)

    async def on_timeout(self):
        self.result = False

async def setup_trading_commands(tree, bot):

    # Autocomplete functions
    async def autocomplete_veci(interaction: discord.Interaction, current: str):
        return [
            app_commands.Choice(name=vec, value=vec)
            for vec in VECI_SEZNAM if current.lower() in vec.lower()
        ][:25]

    async def autocomplete_drogy(interaction: discord.Interaction, current: str):
        return [
            app_commands.Choice(name=drug, value=drug)
            for drug in DROGY_SEZNAM if current.lower() in drug.lower()
        ][:25]

    async def autocomplete_veci_drogy(interaction: discord.Interaction, current: str):

        user_data = get_or_create_user(interaction.user.id)
        veci = user_data.get("veci", {})
        drogy = user_data.get("drogy", {})

        dostupne_polozky = list(veci.keys()) + list(drogy.keys())

        return [
            app_commands.Choice(name=item, value=item)
            for item in dostupne_polozky if current.lower() in item.lower()
        ][:25]

    @tree.command(name="koupit-auto", description="Koupí auto, pokud máš dost peněz a případnou roli")
    @app_commands.describe(auto="Auto, které chceš koupit")
    async def koupit_auto(interaction: discord.Interaction, auto: str):
        user = interaction.user
        uzivatel = interaction.user # Alias for consistency with MongoDB update

        data = get_or_create_user(user.id)

        if auto not in AUTA:
            await interaction.response.send_message("❌ Takové auto neexistuje.", ephemeral=True)
            return

        info = AUTA[auto]
        cena = info["cena"]
        pozadovana_role = info["role"]

        if pozadovana_role:
            required_role_ids = [int(role_id.strip()) for role_id in pozadovana_role.split("||")]
            user_role_ids = [role.id for role in user.roles]

            if not any(role_id in user_role_ids for role_id in required_role_ids):
                await interaction.response.send_message(
                    f"❌ Toto auto vyžaduje specifickou roli.", ephemeral=True)
                return

        total_money = get_total_money(data)
        if total_money < cena:
            await interaction.response.send_message("❌ Nemáš dostatek peněz.", ephemeral=True)
            return

        # Odebrání peněz
        if data["hotovost"] >= cena:
            new_hotovost = data["hotovost"] - cena
            new_bank = data["bank"]
        else:
            rozdil = cena - data["hotovost"]
            new_hotovost = 0
            new_bank = data["bank"] - rozdil

        new_penize = new_hotovost + new_bank
        new_auto_count = data["auta"].get(auto, 0) + 1

        # Update in MongoDB
        hraci.update_one(
            {"user_id": str(uzivatel.id)},
            {"$set": {
                "hotovost": new_hotovost,
                "bank": new_bank,
                "penize": new_penize,
                f"auta.{auto}": new_auto_count
            }}
        )


        await interaction.response.send_message(
            f"✅ Úspěšně jsi koupil **{auto}** za **{cena:,} $**."
        )

    @koupit_auto.autocomplete("auto")
    async def autocomplete_kup_auto(interaction: discord.Interaction, current: str):
        return [
            app_commands.Choice(name=a, value=a)
            for a in AUTA.keys() if current.lower() in a.lower()
        ][:25]

    @tree.command(name="koupit-zbran", description="Koupit zbraň z nabídky")
    @app_commands.describe(zbran="Zbraň, kterou chceš koupit", pocet="Počet kusů")
    async def koupit_zbran(interaction: discord.Interaction, zbran: str, pocet: int = 1):
        role_id = 1293617188988784667
        if not any(role.id == role_id for role in interaction.user.roles):
            await interaction.response.send_message("❌ Nemáš oprávnění koupit zbraně.", ephemeral=True)
            return

        uzivatel = interaction.user

        data = get_or_create_user(uzivatel.id)

        if zbran not in CENY_ZBRANI:
            await interaction.response.send_message(f"❌ Zbraň `{zbran}` není v nabídce k prodeji.", ephemeral=True)
            return

        cena_za_kus = CENY_ZBRANI[zbran]
        celkova_cena = cena_za_kus * pocet

        total_money = get_total_money(data)
        if total_money < celkova_cena:
            await interaction.response.send_message(
                f"❌ Nemáš dostatek peněz ({total_money:,}$) na koupi {pocet}x `{zbran}` (potřebuješ {celkova_cena:,}$).",
                ephemeral=True
            )
            return

        # Odebrání peněz
        if data["hotovost"] >= celkova_cena:
            new_hotovost = data["hotovost"] - celkova_cena
            new_bank = data["bank"]
        else:
            rozdil = celkova_cena - data["hotovost"]
            new_hotovost = 0
            new_bank = data["bank"] - rozdil

        new_penize = new_hotovost + new_bank
        new_zbran_count = data["zbrane"].get(zbran, 0) + pocet

        # Update in MongoDB
        hraci.update_one(
            {"user_id": str(uzivatel.id)},
            {"$set": {
                "hotovost": new_hotovost,
                "bank": new_bank,
                "penize": new_penize,
                f"zbrane.{zbran}": new_zbran_count
            }}
        )


        await interaction.response.send_message(
            f"✅ Úspěšně jsi koupil {pocet}x `{zbran}` za {celkova_cena:,}$.",
            ephemeral=False
        )

    @koupit_zbran.autocomplete("zbran")
    async def autocomplete_koupit_zbran(interaction: discord.Interaction, current: str):
        return [app_commands.Choice(name=z, value=z) for z in CENY_ZBRANI if current.lower() in z.lower()][:25]

    @tree.command(name="kup-veci", description="Kup si suroviny nebo nástroje")
    @app_commands.describe(veci="Název věci, kterou chceš koupit", pocet="Počet kusů")
    @app_commands.autocomplete(veci=autocomplete_veci)
    async def kup_veci(interaction: discord.Interaction, veci: str, pocet: int = 1):
        user = interaction.user

        data = get_or_create_user(user.id)

        if veci not in CENY_VECI:
            await interaction.response.send_message("❌ Tato věc není dostupná k prodeji.", ephemeral=True)
            return

        celkova_cena = CENY_VECI[veci] * pocet
        if data["hotovost"] < celkova_cena:
            await interaction.response.send_message(f"❌ Nemáš dostatek peněz (potřebuješ {celkova_cena:,}$).", ephemeral=True)
            return

        # Odebrání peněz
        if data["hotovost"] >= celkova_cena:
            new_hotovost = data["hotovost"] - celkova_cena
            new_bank = data["bank"]
        else:
            rozdil = celkova_cena - data["hotovost"]
            new_hotovost = 0
            new_bank = data["bank"] - rozdil

        new_penize = new_hotovost + new_bank
        new_vec_count = data["veci"].get(veci, 0) + pocet

        # Update in MongoDB
        hraci.update_one(
            {"user_id": str(user.id)},
            {"$set": {
                "hotovost": new_hotovost,
                "bank": new_bank,
                "penize": new_penize,
                f"veci.{veci}": new_vec_count
            }}
        )


        await interaction.response.send_message(f"✅ Koupil jsi {pocet}x `{veci}` za {celkova_cena:,}$.")

        await log_action(bot, interaction.guild, f"{user.mention} koupil {pocet}x {veci} za {celkova_cena:,}$")

    # Add similar trading commands for selling items, cars, weapons, etc.
    @tree.command(name="prodej-auto", description="Prodá auto jinému hráči")
    @app_commands.describe(kupec="Komu prodáváš auto", auto="Jaké auto prodáváš", cena="Cena za auto")
    async def prodej_auto(interaction: discord.Interaction, kupec: discord.Member, auto: str, cena: int):

        prodavajici_data = get_or_create_user(interaction.user.id)
        kupec_data = get_or_create_user(kupec.id)

        if auto not in prodavajici_data["auta"]:
            await interaction.response.send_message("❌ Nemáš toto auto v inventáři.", ephemeral=True)
            return
        if prodavajici_data["auta"][auto] <= 0:
            await interaction.response.send_message("❌ Nemáš žádné kusy tohoto auta.", ephemeral=True)
            return
        total_money_kupec = get_total_money(kupec_data)
        if total_money_kupec < cena:
            await interaction.response.send_message("❌ Kupující nemá dostatek peněz.", ephemeral=True)
            return

        view = ConfirmationView(interaction.user, kupec, auto, "auto", cena)

        embed = discord.Embed(
            title="🚗 Potvrzení nákupu auta",
            description=f"**Prodávající:** {interaction.user.display_name}\n**Kupující:** {kupec.display_name}\n**Auto:** {auto}\n**Cena:** {cena:,}$",
            color=discord.Color.orange()
        )
        embed.add_field(name="⏰ Čekám na potvrzení", value=f"{kupec.mention}, potvrď prosím nákup kliknutím na tlačítko níže.", inline=False)

        await interaction.response.send_message(embed=embed, view=view)

        await view.wait()

        if view.result is True:
            # Prepare updates for seller
            seller_updates = {
                "hotovost": prodavajici_data["hotovost"] + cena,
                "penize": prodavajici_data["hotovost"] + cena + prodavajici_data["bank"]
            }
            seller_unsets = {}

            if prodavajici_data["auta"][auto] == 1:
                seller_unsets[f"auta.{auto}"] = ""
            else:
                seller_updates[f"auta.{auto}"] = prodavajici_data["auta"][auto] - 1

            # Prepare updates for buyer
            buyer_updates = {
                "hotovost": kupec_data["hotovost"] - cena,
                "penize": kupec_data["hotovost"] - cena + kupec_data["bank"],
                f"auta.{auto}": kupec_data["auta"].get(auto, 0) + 1
            }

            # Update MongoDB
            seller_operations = {"$set": seller_updates}
            if seller_unsets:
                seller_operations["$unset"] = seller_unsets

            hraci.update_one({"user_id": str(interaction.user.id)}, seller_operations)
            hraci.update_one({"user_id": str(kupec.id)}, {"$set": buyer_updates})


            success_embed = discord.Embed(
                title="✅ Obchod dokončen!",
                description=f"Auto `{auto}` bylo úspěšně prodáno {kupec.display_name} za {cena:,}$.",
                color=discord.Color.green()
            )
            await interaction.followup.send(embed=success_embed)
        elif view.result is False:
            fail_embed = discord.Embed(
                title="❌ Obchod zrušen",
                description="Obchod byl zrušen nebo vypršel čas na potvrzení.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=fail_embed)

    @prodej_auto.autocomplete("auto")
    async def autocomplete_prodej_auto(interaction: discord.Interaction, current: str):

        data = get_or_create_user(interaction.user.id)
        auta = data.get("auta", {})
        return [app_commands.Choice(name=a, value=a) for a in auta if current.lower() in a.lower()][:25]

    @tree.command(name="prodej-veci", description="Prodej věc nebo drogu jinému hráči")
    @app_commands.describe(
        cil="Komu chceš věc nebo drogu prodat",
        vec="Název věci nebo drogy",
        mnozstvi="Kolik kusů/gramů chceš prodat",
        cena="Cena za vše v $"
    )
    @app_commands.autocomplete(vec=autocomplete_veci_drogy)
    async def prodej_veci(interaction: discord.Interaction, cil: discord.Member, vec: str, mnozstvi: int, cena: int):
        prodavajici = interaction.user
        if prodavajici.id == cil.id:
            await interaction.response.send_message("❌ Nemůžeš prodávat sám sobě.", ephemeral=True)
            return


        data_prodejce = get_or_create_user(prodavajici.id)
        data_kupce = get_or_create_user(cil.id)

        inventar = data_prodejce.get("veci", {}) | data_prodejce.get("drogy", {})
        if vec not in inventar or inventar[vec] < mnozstvi:
            await interaction.response.send_message("❌ Nemáš dostatek tohoto předmětu nebo drogy.", ephemeral=True)
            return

        embed = discord.Embed(
            title="💸 Nabídka k prodeji",
            description=f"{prodavajici.mention} nabízí `{mnozstvi}x {vec}` za `{cena:,}$` {cil.mention}.",
            color=discord.Color.green()
        )

        class Potvrzeni(discord.ui.View):
            def __init__(self, timeout=60):
                super().__init__(timeout=timeout)
                self.prodej_potvrzen = None

            @discord.ui.button(label="✅ Přijmout", style=discord.ButtonStyle.success)
            async def prijmout(self, interaction_button: discord.Interaction, button: discord.ui.Button):
                if interaction_button.user.id != cil.id:
                    await interaction_button.response.send_message("❌ Tohle není tvoje nabídka.", ephemeral=True)
                    return
                self.prodej_potvrzen = True
                self.stop()
                await interaction_button.response.defer()

            @discord.ui.button(label="❌ Odmítnout", style=discord.ButtonStyle.danger)
            async def odmitnout(self, interaction_button: discord.Interaction, button: discord.ui.Button):
                if interaction_button.user.id != cil.id:
                    await interaction_button.response.send_message("❌ Tohle není tvoje nabídka.", ephemeral=True)
                    return
                self.prodej_potvrzen = False
                self.stop()
                await interaction_button.response.defer()

        view = Potvrzeni()
        await interaction.response.send_message(embed=embed, view=view)

        await view.wait()

        if view.prodej_potvrzen is None:
            await interaction.edit_original_response(content="⏳ Čas na odpověď vypršel.", embed=None, view=None)
            return

        if not view.prodej_potvrzen:
            await interaction.edit_original_response(content="❌ Kupující odmítl nabídku.", embed=None, view=None)
            return

        total_money_kupce = get_total_money(data_kupce)
        if total_money_kupce < cena:
            await interaction.edit_original_response(content="❌ Kupující nemá dost peněz.", embed=None, view=None)
            return

        # Check if the item is a drug or a regular item
        je_droga = vec in data_prodejce.get("drogy", {})

        # Prepare updates for seller
        seller_updates = {"hotovost": data_prodejce["hotovost"] + cena}
        seller_updates["penize"] = seller_updates["hotovost"] + data_prodejce["bank"]
        seller_unsets = {}

        if je_droga:
            if data_prodejce["drogy"][vec] == mnozstvi:
                seller_unsets[f"drogy.{vec}"] = ""
            else:
                seller_updates[f"drogy.{vec}"] = data_prodejce["drogy"][vec] - mnozstvi
        else:
            if data_prodejce["veci"][vec] == mnozstvi:
                seller_unsets[f"veci.{vec}"] = ""
            else:
                seller_updates[f"veci.{vec}"] = data_prodejce["veci"][vec] - mnozstvi

        # Prepare updates for buyer
        buyer_updates = {
            "hotovost": data_kupce["hotovost"] - cena,
            "penize": data_kupce["hotovost"] - cena + data_kupce["bank"]
        }

        if je_droga:
            buyer_updates[f"drogy.{vec}"] = data_kupce["drogy"].get(vec, 0) + mnozstvi
        else:
            buyer_updates[f"veci.{vec}"] = data_kupce["veci"].get(vec, 0) + mnozstvi

        # Update MongoDB
        seller_operations = {"$set": seller_updates}
        if seller_unsets:
            seller_operations["$unset"] = seller_unsets

        hraci.update_one({"user_id": str(prodavajici.id)}, seller_operations)
        hraci.update_one({"user_id": str(cil.id)}, {"$set": buyer_updates})


        await interaction.edit_original_response(
            content=f"✅ {cil.mention} koupil {mnozstvi}x `{vec}` za {cena:,}$ od {prodavajici.mention}.",
            embed=None,
            view=None
        )