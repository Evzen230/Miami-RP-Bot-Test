
import json
import discord
from data_config import DATA_FILE, LOG_CHANNEL_ID, ADMIN_ROLE_ID, POLICE_ROLE_ID
from pymongo import MongoClient
from datetime import datetime

# MongoDB připojení
MONGO_URI = "mongodb+srv://Miami_RP_BOT:txHJ7gp9aAe8urpm@miamirp.y7b8j.mongodb.net/?retryWrites=true&w=majority&appName=MiamiRP"
client = MongoClient(MONGO_URI)
db = client["miamirpbot"]
hraci = db["hraci"]


def get_or_create_user(user_id: int):
    user_id = str(user_id)

    user = hraci.find_one({"_id": user_id})
    if not user:
        user = {
            "_id": user_id,
            "auta": {},
            "zbrane": {},
            "penize": 0,
            "hotovost": 4000,
            "bank": 0,
            "last_collect": None,
            "collect_timestamps": {},
            "veci": {},
            "registrovana_auta": {}
        }
        hraci.insert_one(user)
        return user

    # --- Migrace starých dat ---
    changed = False

    if "penize" not in user:
        user["penize"] = 0
        changed = True
    if "hotovost" not in user:
        user["hotovost"] = 0
        changed = True
    if "bank" not in user:
        user["bank"] = 0
        changed = True
    if "veci" not in user:
        user["veci"] = {}
        changed = True

    # převod listů na dict
    if isinstance(user.get("auta"), list):
        auta_dict = {}
        for auto in user["auta"]:
            auta_dict[auto] = auta_dict.get(auto, 0) + 1
        user["auta"] = auta_dict
        changed = True

    if isinstance(user.get("zbrane"), list):
        zbrane_dict = {}
        for zbran in user["zbrane"]:
            zbrane_dict[zbran] = zbrane_dict.get(zbran, 0) + 1
        user["zbrane"] = zbrane_dict
        changed = True

    # aktualizace celkových peněz
    user["penize"] = user.get("hotovost", 0) + user.get("bank", 0)

    if changed:
        hraci.update_one({"user_id": user_id}, {"$set": user})

    return user


def get_total_money(user):
    return user.get("hotovost", 0) + user.get("bank", 0)

# === PERMISSION FUNCTIONS ===

def is_admin(user: discord.User):
    return any(role.id == ADMIN_ROLE_ID for role in user.roles)

def has_permission(user: discord.User):
    return any(role.id in (ADMIN_ROLE_ID, POLICE_ROLE_ID) for role in user.roles)

# === LOGGING FUNCTIONS ===

async def log_action(bot, guild: discord.Guild, message: str):
    log_channel = guild.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        await log_channel.send(f"📘 **Log:** {message}")
