
import discord
from discord import app_commands
from data_config import DOSTUPNE_ZBRANE, DOSTUPNA_AUTA
from utils import get_or_create_user, is_admin

async def setup_inventory_commands(tree, bot):
    
    @tree.command(name="pridej-zbran", description="Přidá zbraň hráči (admin)")
    @app_commands.describe(uzivatel="Uživatel, kterému přidáš zbraň",
                               zbran="Zbraň, kterou chceš přidat",
                               pocet="Počet kusů")
    async def pridej_zbran(interaction: discord.Interaction,
                               uzivatel: discord.Member,
                               zbran: str,
                               pocet: int = 1):
            if not is_admin(interaction.user):
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
            
            await interaction.response.send_message(
                f"✅ Přidáno {pocet}x `{zbran}` hráči {uzivatel.display_name}.")

    @pridej_zbran.autocomplete("zbran")
    async def autocomplete_zbran_pridat(interaction: discord.Interaction,
                                            current: str):
            return [
                app_commands.Choice(name=z, value=z) for z in DOSTUPNE_ZBRANE
                if current.lower() in z.lower()
            ][:25]

    @tree.command(name="odeber-zbran", description="Odebere zbraň hráči (admin)")
    @app_commands.describe(uzivatel="Uživatel, kterému odebereš zbraň",
                               zbran="Zbraň, kterou chceš odebrat",
                               pocet="Počet kusů")
    async def odeber_zbran(interaction: discord.Interaction,
                               uzivatel: discord.Member,
                               zbran: str,
                               pocet: int = 1):
            if not is_admin(interaction.user):
                await interaction.response.send_message(
                    "❌ Nemáš oprávnění použít tento příkaz.", ephemeral=True)
                return
            
            data = get_or_create_user(uzivatel.id)
            if zbran in data["zbrane"]:
                data["zbrane"][zbran] -= pocet
                if data["zbrane"][zbran] <= 0:
                    del data["zbrane"][zbran]
                
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

    @tree.command(name="pridej-auto", description="Přidá auto hráči (admin)")
    @app_commands.describe(uzivatel="Uživatel, kterému přidáš auto",
                              auto="Auto, které chceš přidat",
                              pocet="Počet kusů")
    async def pridej_auto(interaction: discord.Interaction,
                              uzivatel: discord.Member,
                              auto: str,
                              pocet: int = 1):
            if not is_admin(interaction.user):
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
            
            await interaction.response.send_message(
                f"✅ Přidáno {pocet}x `{auto}` hráči {uzivatel.display_name}.")

    @pridej_auto.autocomplete("auto")
    async def autocomplete_auto_pridat(interaction: discord.Interaction,
                                           current: str):
            return [
                app_commands.Choice(name=a, value=a) for a in DOSTUPNA_AUTA
                if current.lower() in a.lower()
            ][:25]

    @tree.command(name="odeber-auto", description="Odebere auto hráči (admin)")
    @app_commands.describe(uzivatel="Uživatel, kterému odebereš auto",
                              auto="Auto, které chceš odebrat",
                              pocet="Počet kusů")
    async def odeber_auto(interaction: discord.Interaction,
                              uzivatel: discord.Member,
                              auto: str,
                              pocet: int = 1):
            if not is_admin(interaction.user):
                await interaction.response.send_message(
                    "❌ Nemáš oprávnění použít tento příkaz.", ephemeral=True)
                return
            
            data = get_or_create_user(uzivatel.id)
            if auto in data["auta"]:
                data["auta"][auto] -= pocet
                if data["auta"][auto] <= 0:
                    del data["auta"][auto]
                
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

    @tree.command(name="inventory", description="Zobrazí inventář hráče")
    @app_commands.describe(uzivatel="Uživatel, jehož inventář chceš zobrazit")
    async def inventory(interaction: discord.Interaction, uzivatel: discord.Member = None):
            uzivatel = uzivatel or interaction.user
            
            data = get_or_create_user(uzivatel.id)

            auta = data.get("auta", {})
            zbrane = data.get("zbrane", {})
            veci = data.get("veci", {})
            drogy = data.get("drogy", {})

            auta_text = "\n".join(f"🚗 {auto} ×{pocet}" for auto, pocet in auta.items()) or "Žádná"
            zbrane_text = "\n".join(f"🔫 {zbran} ×{pocet}" for zbran, pocet in zbrane.items()) or "Žádné"
            veci_text = "\n".join(f"📦 {nazev} ×{pocet}" for nazev, pocet in veci.items()) or "Žádné"
            drogy_text = "\n".join(f"💊 {nazev} ×{gramy}g" for nazev, gramy in drogy.items())

            embed = discord.Embed(
                title=f"📋 Inventář uživatele {uzivatel.display_name}",
                color=discord.Color.blue()
            )
            embed.add_field(name="Auta", value=auta_text, inline=False)
            embed.add_field(name="Zbraně", value=zbrane_text, inline=False)
            embed.add_field(name="Věci", value=veci_text, inline=False)

            if drogy:
                embed.add_field(name="Drogy", value=drogy_text, inline=False)

            await interaction.response.send_message(embed=embed)

    @tree.command(name="reset-inventory", description="Resetuje celý inventář hráče (admin)")
    @app_commands.describe(uzivatel="Uživatel, jehož inventář chceš vymazat")
    async def reset_inventory(interaction: discord.Interaction, uzivatel: discord.Member):
            if not is_admin(interaction.user):
                await interaction.response.send_message("❌ Nemáš oprávnění použít tento příkaz.", ephemeral=True)
                return
            
            data = get_or_create_user(uzivatel.id)
            data["auta"] = {}
            data["zbrane"] = {}
            data["veci"] = {}
            data["drogy"] = {}
            
            await interaction.response.send_message(f"♻️ Inventář hráče {uzivatel.display_name} byl úspěšně resetován.")
