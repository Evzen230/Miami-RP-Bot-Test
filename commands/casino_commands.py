import discord
import random
from discord import app_commands
from discord.ui import View, button

# ===============================
# Pomocné funkce pro Blackjack
# ===============================

def hand_value(hand):
    value = 0
    aces = 0
    for card in hand:
        rank = card[:-1]
        if rank in ["J", "Q", "K"]:
            value += 10
        elif rank == "A":
            value += 11
            aces += 1
        else:
            value += int(rank)
    while value > 21 and aces:
        value -= 10
        aces -= 1
    return value

def draw_card():
    ranks = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
    suits = ["♠", "♥", "♦", "♣"]
    return random.choice(ranks) + random.choice(suits)

blackjack_sessions = {}  # user_id -> dict hry

# ===============================
# Blackjack UI
# ===============================

class BlackjackView(View):
    def __init__(self, user_id, bet, load_data_func, save_data_func, get_user_func):
        super().__init__(timeout=120)
        self.user_id = user_id
        self.bet = bet
        self.load_data = load_data_func
        self.save_data = save_data_func
        self.get_user = get_user_func

    async def end_game(self, interaction, result):
        session = blackjack_sessions.pop(self.user_id, None)
        if not session:
            return
        databaze = self.load_data()
        data = self.get_user(self.user_id)

        if result == "win":
            data["hotovost"] += self.bet
            msg = f"🎉 Vyhrál jsi {self.bet}$!"
        elif result == "blackjack":
            win_amount = int(self.bet * 1.5)
            data["hotovost"] += win_amount
            msg = f"🃏 BLACKJACK! Vyhráváš {win_amount}$!"
        elif result == "lose":
            data["hotovost"] -= self.bet
            msg = f"💀 Prohrál jsi {self.bet}$."
        elif result == "push":
            msg = "🤝 Remíza — sázka vrácena."

        self.save_data(databaze)

        dealer_hand_str = f"{' '.join(session['dealer'])} ({hand_value(session['dealer'])})"
        player_hand_str = f"{' '.join(session['player'])} ({hand_value(session['player'])})"

        embed = discord.Embed(title="🃏 Blackjack — Konec hry")
        embed.add_field(name="Tvoje ruka", value=player_hand_str, inline=False)
        embed.add_field(name="Dealer", value=dealer_hand_str, inline=False)

        await interaction.response.edit_message(content=msg, embed=embed, view=None)

    @button(label="Hit", style=discord.ButtonStyle.primary)
    async def hit(self, interaction: discord.Interaction, _button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("Tohle není tvoje hra!", ephemeral=True)

        session = blackjack_sessions[self.user_id]
        session["player"].append(draw_card())

        if hand_value(session["player"]) > 21:
            await self.end_game(interaction, "lose")
            return

        embed = discord.Embed(title="🃏 Blackjack")
        embed.add_field(
            name="Tvoje ruka",
            value=f"{' '.join(session['player'])} ({hand_value(session['player'])})",
            inline=False
        )
        embed.add_field(
            name="Dealer",
            value=f"{session['dealer'][0]} ??",
            inline=False
        )
        await interaction.response.edit_message(embed=embed, view=self)

    @button(label="Stand", style=discord.ButtonStyle.secondary)
    async def stand(self, interaction: discord.Interaction, _button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("Tohle není tvoje hra!", ephemeral=True)

        session = blackjack_sessions[self.user_id]

        while hand_value(session["dealer"]) < 17:
            session["dealer"].append(draw_card())

        player_val = hand_value(session["player"])
        dealer_val = hand_value(session["dealer"])

        if dealer_val > 21 or player_val > dealer_val:
            if player_val == 21 and len(session["player"]) == 2:
                await self.end_game(interaction, "blackjack")
            else:
                await self.end_game(interaction, "win")
        elif player_val < dealer_val:
            await self.end_game(interaction, "lose")
        else:
            await self.end_game(interaction, "push")

    @button(label="Double", style=discord.ButtonStyle.success)
    async def double(self, interaction: discord.Interaction, _button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("Tohle není tvoje hra!", ephemeral=True)

        self.bet *= 2
        session = blackjack_sessions[self.user_id]
        session["player"].append(draw_card())

        if hand_value(session["player"]) > 21:
            await self.end_game(interaction, "lose")
            return

        while hand_value(session["dealer"]) < 17:
            session["dealer"].append(draw_card())

        player_val = hand_value(session["player"])
        dealer_val = hand_value(session["dealer"])

        if dealer_val > 21 or player_val > dealer_val:
            if player_val == 21 and len(session["player"]) == 2:
                await self.end_game(interaction, "blackjack")
            else:
                await self.end_game(interaction, "win")
        elif player_val < dealer_val:
            await self.end_game(interaction, "lose")
        else:
            await self.end_game(interaction, "push")

# ===============================
# Hazardní příkazy
# ===============================

async def casino_setup(tree, bot, load_data_func, save_data_func, get_user_func):

    @tree.command(name="ruleta", description="Zahraj si ruletu.")
    @app_commands.describe(castka="Sázka", tip="Číslo 0–36 nebo 'red', 'black', 'green'")
    async def ruleta(interaction: discord.Interaction, castka: int, tip: str):
        databaze = load_data_func()
        data = get_user_func(interaction.user.id)
        if data["hotovost"] < castka:
            return await interaction.response.send_message("Nemáš dost hotovosti!", ephemeral=True)

        result = random.randint(0, 36)
        colors = {0: "green", **{n: "red" if n % 2 == 0 else "black" for n in range(1, 37)}}
        win = False
        if tip.isdigit() and int(tip) == result:
            win = True
            vyhra = castka * 35
        elif colors[result] == tip.lower():
            win = True
            vyhra = castka * (14 if tip.lower() == "green" else 2)

        if win:
            data["hotovost"] += vyhra
            msg = f"🎉 Padlo {result} ({colors[result]}) — vyhráváš {vyhra}$!"
        else:
            data["hotovost"] -= castka
            msg = f"💀 Padlo {result} ({colors[result]}) — prohráváš {castka}$."

        save_data_func(databaze)
        await interaction.response.send_message(msg)

    @tree.command(name="sloty", description="Zatoč si automatem.")
    @app_commands.describe(castka="Sázka")
    async def sloty(interaction: discord.Interaction, castka: int):
        databaze = load_data_func()
        data = get_user_func(interaction.user.id)
        if data["hotovost"] < castka:
            return await interaction.response.send_message("Nemáš dost hotovosti!", ephemeral=True)

        symbols = ["🍒", "🍋", "🍉", "⭐", "💎"]
        roll = [random.choice(symbols) for _ in range(3)]

        if len(set(roll)) == 1:
            vyhra = castka * 5
            data["hotovost"] += vyhra
            msg = f"{' '.join(roll)} 🎉 JACKPOT! Vyhráváš {vyhra}$!"
        elif len(set(roll)) == 2:
            vyhra = castka * 2
            data["hotovost"] += vyhra
            msg = f"{' '.join(roll)} Výhra {vyhra}$!"
        else:
            data["hotovost"] -= castka
            msg = f"{' '.join(roll)} Smůla, prohráváš {castka}$."

        save_data_func(databaze)
        await interaction.response.send_message(msg)

    @tree.command(name="hilo", description="Hádání vyšší/nižší s kostkou.")
    @app_commands.describe(castka="Sázka", volba="'high' (4-6) nebo 'low' (1-3)")
    async def hilo(interaction: discord.Interaction, castka: int, volba: str):
        databaze = load_data_func()
        data = get_user_func(interaction.user.id)
        if data["hotovost"] < castka:
            return await interaction.response.send_message("Nemáš dost hotovosti!", ephemeral=True)

        roll = random.randint(1, 6)
        if (volba.lower() == "high" and roll >= 4) or (volba.lower() == "low" and roll <= 3):
            data["hotovost"] += castka
            msg = f"🎲 Padlo {roll} — vyhráváš {castka}$!"
        else:
            data["hotovost"] -= castka
            msg = f"🎲 Padlo {roll} — prohráváš {castka}$."

        save_data_func(databaze)
        await interaction.response.send_message(msg)

    @tree.command(name="blackjack", description="Zahraj si blackjack.")
    @app_commands.describe(castka="Sázka")
    async def blackjack(interaction: discord.Interaction, castka: int):
        databaze = load_data_func()
        data = get_user_func(interaction.user.id)
        if data["hotovost"] < castka:
            return await interaction.response.send_message("Nemáš dost hotovosti!", ephemeral=True)

        player = [draw_card(), draw_card()]
        dealer = [draw_card(), draw_card()]
        blackjack_sessions[interaction.user.id] = {"player": player, "dealer": dealer}

        embed = discord.Embed(title="🃏 Blackjack")
        embed.add_field(name="Tvoje ruka", value=f"{' '.join(player)} ({hand_value(player)})", inline=False)
        embed.add_field(name="Dealer", value=f"{dealer[0]} ??", inline=False)

        view = BlackjackView(interaction.user.id, castka, load_data_func, save_data_func, get_user_func)
        await interaction.response.send_message(embed=embed, view=view)