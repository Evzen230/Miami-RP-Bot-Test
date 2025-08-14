
import json
import discord
from data_config import DATA_FILE, LOG_CHANNEL_ID, ADMIN_ROLE_ID, POLICE_ROLE_ID

# === DATABASE FUNCTIONS ===

def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_data(databaze):
    with open(DATA_FILE, "w") as f:
        json.dump(databaze, f, indent=4)

def get_or_create_user(user_id, databaze):
    user_id = str(user_id)
    if user_id not in databaze:
        databaze[user_id] = {
            "auta": {},
            "zbrane": {},
            "penize": 0,
            "hotovost": 0,
            "bank": 0,
            "last_collect": None,
            "collect_timestamps": {},
            "veci": {}
        }
        save_data(databaze)
        return databaze[user_id]

    # Convert old formats and ensure all fields exist
    data = databaze[user_id]

    # Ensure all money fields exist
    if "penize" not in data:
        data["penize"] = 0
    if "hotovost" not in data:
        data["hotovost"] = 0
    if "bank" not in data:
        data["bank"] = 0
    if "veci" not in data:
        data["veci"] = {}

    # Convert old list format to new dict format
    if isinstance(data.get("auta"), list):
        auta_dict = {}
        for auto in data["auta"]:
            if auto in auta_dict:
                auta_dict[auto] += 1
            else:
                auta_dict[auto] = 1
        data["auta"] = auta_dict

    if isinstance(data.get("zbrane"), list):
        zbrane_dict = {}
        for zbran in data["zbrane"]:
            if zbran in zbrane_dict:
                zbrane_dict[zbran] += 1
            else:
                zbrane_dict[zbran] = 1
        data["zbrane"] = zbrane_dict

    # Update total money
    data["penize"] = data["hotovost"] + data["bank"]

    return data

def get_total_money(data):
    return data.get("hotovost", 0) + data.get("bank", 0)

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
