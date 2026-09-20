import os
os.system('pip install telebot')
os.system('pip install dotenv')
os.system('pip install tzdata')
os.system('pip install gtts')
os.system('pip install yt_dlp')
os.system('pip install python-telegram-bot')
os.system('pip install telethon')
os.system('pip install psutil')
os.system('pip install flask')
os.system('pip install requests')
def _split_telegram_text(text, max_chars=4096):
    text = str(text or '')
    return [text[i:i+max_chars] for i in range(0, len(text), max_chars)] or ['']

# -*- coding: utf-8 -*-
import telebot
import subprocess
import os
import zipfile
import tempfile
import shutil
from telebot import types
import time
from datetime import datetime, timedelta
try:
    import psutil
except Exception as _psutil_import_error:
    psutil = None
    _psutil_import_error = str(_psutil_import_error)
import sqlite3
import json
import logging
import signal
import threading
import re
import sys
import atexit
import requests
import gc
from dotenv import load_dotenv  # New import for .env

# --- Small-caps button formatting ---
_SMALLCAPS_MAP = str.maketrans({
    "a":"ᴀ", "b":"ʙ", "c":"ᴄ", "d":"ᴅ", "e":"ᴇ", "f":"ꜰ",
    "g":"ɢ", "h":"ʜ", "i":"ɪ", "j":"ᴊ", "k":"ᴋ", "l":"ʟ",
    "m":"ᴍ", "n":"ɴ", "o":"ᴏ", "p":"ᴘ", "q":"q", "r":"ʀ",
    "s":"s", "t":"ᴛ", "u":"ᴜ", "v":"ᴠ", "w":"ᴡ", "x":"x",
    "y":"ʏ", "z":"z",
    "A":"ᴀ", "B":"ʙ", "C":"ᴄ", "D":"ᴅ", "E":"ᴇ", "F":"ꜰ",
    "G":"ɢ", "H":"ʜ", "I":"ɪ", "J":"ᴊ", "K":"ᴋ", "L":"ʟ",
    "M":"ᴍ", "N":"ɴ", "O":"ᴏ", "P":"ᴘ", "Q":"q", "R":"ʀ",
    "S":"s", "T":"ᴛ", "U":"ᴜ", "V":"ᴠ", "W":"ᴡ", "X":"x",
    "Y":"ʏ", "Z":"z",
})

def _smallcaps(text):
    return text.translate(_SMALLCAPS_MAP) if isinstance(text, str) else text

# --- Royal button styling ---
# Telegram does not support true animated button labels. These wrappers give
# every button a royal animated-look using Unicode crown/shimmer decorations,
# while leaving callback_data/URLs untouched.
def _royal_button_text(value):
    # Keep the existing small-caps styling, but remove the added royal crown/shimmer decorations.
    if not isinstance(value, str):
        return value
    return _smallcaps(value)

def _sc_inline_button(*args, **kwargs):
    if args:
        args = list(args)
        args[0] = _royal_button_text(args[0])
        args = tuple(args)
    elif "text" in kwargs:
        kwargs["text"] = _royal_button_text(kwargs["text"])
    return types.InlineKeyboardButton(*args, **kwargs)

def _sc_keyboard_button(*args, **kwargs):
    if args:
        args = list(args)
        args[0] = _royal_button_text(args[0])
        args = tuple(args)
    elif "text" in kwargs:
        kwargs["text"] = _royal_button_text(kwargs["text"])
    return types.KeyboardButton(*args, **kwargs)

# --- Load environment variables ---
load_dotenv()  # Load .env file

# --- Flask Keep Alive ---
from flask import Flask
from threading import Thread
from functools import wraps

app = Flask('')

@app.route('/')
def home():
    return "I am 👿 /~Gᴏᴅ Fᴀᴛʜᴇʀ𓆩⃟🇰🇬𓆪 👿 HOSTING BOT"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()
    print("Flask Keep-Alive server started.")
# --- End Flask Keep Alive ---

# --- Configuration FROM .env FILE ---
TOKEN = ('8916732492:AAFjTPD0-o4FeL89NBhC0cTIjdY7bWVXMec')
OWNER_ID = int(os.getenv('OWNER_ID', 8748719644))
ADMIN_ID = int(os.getenv('ADMIN_ID',1099148582,))
YOUR_USERNAME = os.getenv('YOUR_USERNAME','whx2t')
UPDATE_CHANNEL = os.getenv('UPDATE_CHANNEL', 'teammonster001')

# Limits from .env or defaults
FREE_USER_LIMIT = int(os.getenv('FREE_USER_LIMIT', 5))
SUBSCRIBED_USER_LIMIT = int(os.getenv('SUBSCRIBED_USER_LIMIT', 20))
ADMIN_LIMIT = int(os.getenv('ADMIN_LIMIT', 99999))
OWNER_LIMIT = float('inf')

# Folder setup
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_BOTS_DIR = os.path.join(BASE_DIR, 'upload_bots')
IROTECH_DIR = os.path.join(BASE_DIR, 'inf')
DATABASE_PATH = os.path.join(IROTECH_DIR, 'bot_data.db')

# Create necessary directories
os.makedirs(UPLOAD_BOTS_DIR, exist_ok=True)
os.makedirs(IROTECH_DIR, exist_ok=True)

# Initialize bot
bot = telebot.TeleBot(TOKEN, num_threads=10)



# --- Premium Progress Animations ---
def _progress_frames(label, icon="⚡"):
    """Return Telegram-friendly 0..100% progress frames."""
    frames = []
    for pct in range(0, 101, 10):
        filled = pct // 10
        bar = "▰" * filled + "▱" * (10 - filled)
        prefix = icon if pct < 100 else "✅"
        title = label if pct < 100 else f"{label} Complete"
        frames.append(f"{prefix} 𝐄𝐱𝐞𝐜𝐮𝐭𝐢𝐧𝐠: {title}\n[{bar}] {pct}%")
    return frames

def _show_progress(chat_id, message_id, label, icon="⚡", delay=0.10):
    """Animate one Telegram message by editing it through progress frames."""
    frames = _progress_frames(label, icon)
    for frame in frames:
        try:
            bot.edit_message_text(frame, chat_id, message_id)
        except Exception as e:
            if "message is not modified" not in str(e).lower():
                logger.debug(f"Progress animation edit failed: {e}")
        time.sleep(delay)
    return frames[-1]

# --- Global boxed-message formatting ---
_BOX_TOP = "╔═══════════════✦═══════════════╗"
_BOX_BOTTOM = "╚═══════════════✦═══════════════╝"

# --- Small-caps UI font ---
# Converts only ordinary A-Z/a-z characters in user-facing bot messages.
# Text inside backticks (commands, filenames, IDs, etc.) is preserved.
_SMALLCAPS = str.maketrans({
    **dict(zip("abcdefghijklmnopqrstuvwxyz", "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ")),
    **dict(zip("ABCDEFGHIJKLMNOPQRSTUVWXYZ", "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ")),
})

def _smallcaps_text(text):
    """Convert ordinary UI text to small-caps while preserving commands/usernames."""
    if text is None:
        return text
    text = str(text)

    # Preserve literal ASCII bot commands and the owner username. This uses
    # split-and-translate instead of placeholder tokens so internal marker
    # strings can never leak into Telegram messages.
    import re as _re
    owner_raw = str(YOUR_USERNAME).strip().lstrip('@') if 'YOUR_USERNAME' in globals() else 'whx2t'
    protected = []
    if owner_raw:
        protected.append(_re.escape('@' + owner_raw))
        protected.append(_re.escape(owner_raw))
    protected.append(_re.escape('/cancel'))
    protected.append(_re.escape('/CANCEL'))

    if protected:
        pattern = _re.compile('(' + '|'.join(protected) + ')', _re.IGNORECASE)
        chunks = pattern.split(text)
    else:
        chunks = [text]

    out = []
    for i, chunk in enumerate(chunks):
        if pattern.fullmatch(chunk) if protected else False:
            # Keep protected commands/usernames exactly as typed, normalizing
            # only the /CANCEL command spelling.
            out.append('/cancel' if chunk.lower() == '/cancel' else chunk)
        else:
            # Preserve code spans while translating ordinary UI text.
            parts = chunk.split('`')
            for j in range(0, len(parts), 2):
                parts[j] = parts[j].translate(_SMALLCAPS)
            out.append('`'.join(parts))
    return ''.join(out)


def _box_outgoing_text(text):
    """Apply the same dark/premium box style to every outgoing text message."""
    if text is None or not isinstance(text, str):
        return text
    raw = text.strip()
    if not raw:
        return text

    # Keep the requested lock/unlock cards exactly in the premium style.
    low = raw.lower()
    if 'bot has been locked' in low or ('bot locked' in low and 'unlocked' not in low):
        return (
            "╔══════════════════════════════╗\n"
            "║   🔒 ʙᴏᴛ ᴄᴏɴᴛʀᴏʟ ʟᴏᴄᴋᴇᴅ   ║\n"
            "╚══════════════════════════════╝\n\n"
            "        ⛔ ʟᴏᴄᴋᴇᴅ sᴛᴀᴛᴜs\n\n"
            "   🔐 ᴀᴅᴍɪɴ ʟᴏᴄᴋ ᴀᴄᴛɪᴠᴇ\n"
            "   ⚠️ ᴜsᴇʀ ᴀᴄᴄᴇss ʀᴇsᴛʀɪᴄᴛᴇᴅ"
        )
    if 'bot has been unlocked' in low or 'bot unlocked' in low:
        return (
            "╔══════════════════════════════╗\n"
            "║  🔓 ʙᴏᴛ ᴄᴏɴᴛʀᴏʟ ᴜɴʟᴏᴄᴋᴇᴅ  ║\n"
            "╚══════════════════════════════╝\n\n"
            "        ✅ ᴜɴʟᴏᴄᴋᴇᴅ sᴛᴀᴛᴜs\n\n"
            "   🟢 ᴀᴅᴍɪɴ ʟᴏᴄᴋ ʀᴇᴍᴏᴠᴇᴅ\n"
            "   🚀 ᴜsᴇʀ ᴀᴄᴄᴇss ʀᴇsᴛᴏʀᴇᴅ"
        )

    # Strip legacy Telegram box frames so old messages are restyled instead of
    # preserving the previous "BOT MESSAGE" wrapper.
    clean_lines=[]
    for line in raw.splitlines():
        stripped=line.strip()
        if stripped and not (set(stripped) <= set('╔═╗╚╝║╠╣╬')):
            clean_lines.append(stripped)
    raw='\n'.join(clean_lines).strip() or text.strip()

    low=raw.lower()
    if any(k in low for k in ('error','failed','invalid','unable','exception')):
        icon,title='❌','ᴇʀʀᴏʀ'
    elif 'cancel' in low:
        icon,title='❌','ᴄᴀɴᴄᴇʟʟᴇᴅ'
    elif any(k in low for k in ('success','successfully','completed','added','started')):
        icon,title='✅','sᴜᴄᴄᴇss'
    elif 'admin' in low:
        icon,title='👑','ᴀᴅᴍɪɴ'
    elif 'subscription' in low:
        icon,title='💳','sᴜʙsᴄʀɪᴘᴛɪᴏɴ'
    elif 'status' in low or 'statistics' in low or 'uptime' in low:
        icon,title='📊','sᴛᴀᴛᴜs'
    else:
        icon,title='🔔','ʙᴏᴛ ᴍᴇssᴀɢᴇ'

    # Uniform premium frame for every message.
    frame='═'*30
    title=title[:24]
    title_line=f"║   {icon} {title:^{23}}║"
    body='\n'.join(f"   {line}" if line else '' for line in raw.splitlines())
    return f"╔{frame}╗\n{title_line}\n╚{frame}╝\n\n{body}"


def _install_box_wrappers(_bot):
    """Box ordinary text sent/edited through common TeleBot methods."""
    original_send_message = _bot.send_message
    original_reply_to = _bot.reply_to
    original_edit_message_text = _bot.edit_message_text

    def _retry_without_parse_mode(call, args, kwargs):
        """Retry Telegram messages as plain text if Markdown entities are malformed."""
        try:
            return call(*args, **kwargs)
        except Exception as exc:
            err = str(exc).lower()
            if "can't parse entities" not in err and "parse entities" not in err and "bad request" not in err:
                raise
            retry_kwargs = dict(kwargs)
            retry_kwargs.pop("parse_mode", None)
            retry_kwargs.pop("entities", None)
            return call(*args, **retry_kwargs)

    def send_message_boxed(*args, **kwargs):
        # Internal raw-message escape hatch used by broadcasts so the original
        # user text is sent exactly as entered (no premium box/small-caps).
        broadcast_raw = kwargs.pop("_broadcast_raw", False)
        if broadcast_raw:
            return original_send_message(*args, **kwargs)
        if len(args) >= 2:
            args = list(args)
            args[1] = _box_outgoing_text(args[1])
            args = tuple(args)
        elif "text" in kwargs:
            kwargs["text"] = _box_outgoing_text(kwargs["text"])
        return _retry_without_parse_mode(original_send_message, args, kwargs)

    def reply_to_boxed(*args, **kwargs):
        if len(args) >= 3:
            args = list(args)
            args[2] = _box_outgoing_text(args[2])
            args = tuple(args)
        elif "text" in kwargs:
            kwargs["text"] = _box_outgoing_text(kwargs["text"])
        return _retry_without_parse_mode(original_reply_to, args, kwargs)

    def edit_message_text_boxed(*args, **kwargs):
        # TeleBot signature places text at positional index 2.
        if len(args) >= 3:
            args = list(args)
            args[2] = _box_outgoing_text(args[2])
            args = tuple(args)
        elif "text" in kwargs:
            kwargs["text"] = _box_outgoing_text(kwargs["text"])
        return _retry_without_parse_mode(original_edit_message_text, args, kwargs)

    _bot.send_message = send_message_boxed
    _bot.reply_to = reply_to_boxed
    _bot.edit_message_text = edit_message_text_boxed


_install_box_wrappers(bot)

# --- Universal UI message boxing ---
# Keeps existing boxed messages unchanged and gives ordinary bot/UI messages
# a consistent boxed appearance. Uses only standard Python features.
def _box_ui_text(text):
    if not isinstance(text, str) or not text.strip():
        return text
    if "╔════════" in text and "╚════════" in text:
        return _smallcaps_text(text)

    lines = _smallcaps_text(text.strip()).splitlines()
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    if not lines:
        return text

    # First line becomes the compact heading; remaining lines stay as body.
    title = lines[0].strip()
    body = lines[1:]
    # Avoid extremely wide boxes while keeping readable text.
    width = max(28, min(48, len(title) + 4))
    if len(title) > width - 4:
        title = title[:width - 7] + "..."

    result = ["╔" + "═" * width + "╗"]
    result.append("║" + title.center(width) + "║")
    result.append("╚" + "═" * width + "╝")
    if body:
        result.append("")
        for line in body:
            result.append("  " + line)
    return "\n".join(result)

# Wrap TeleBot send/edit methods once so ordinary UI responses are boxed.
_original_send_message = bot.send_message
_original_edit_message_text = bot.edit_message_text

def _boxed_send_message(chat_id, text, *args, **kwargs):
    # Broadcasts use _broadcast_raw=True to preserve the exact message text
    # and avoid the global premium UI boxing wrapper.
    broadcast_raw = kwargs.pop("_broadcast_raw", False)
    if broadcast_raw:
        return _original_send_message(chat_id, text, *args, **kwargs, _broadcast_raw=True)
    try:
        return _original_send_message(chat_id, _box_ui_text(text), *args, **kwargs)
    except Exception as exc:
        err = str(exc).lower()
        if "can't parse entities" not in err and "parse entities" not in err and "bad request" not in err:
            raise
        retry_kwargs = dict(kwargs)
        retry_kwargs.pop("parse_mode", None)
        retry_kwargs.pop("entities", None)
        return _original_send_message(chat_id, _box_ui_text(text), *args, **retry_kwargs)

def _boxed_edit_message_text(text, chat_id, message_id, *args, **kwargs):
    try:
        return _original_edit_message_text(_box_ui_text(text), chat_id, message_id, *args, **kwargs)
    except Exception as exc:
        err = str(exc).lower()
        if "can't parse entities" not in err and "parse entities" not in err and "bad request" not in err:
            raise
        retry_kwargs = dict(kwargs)
        retry_kwargs.pop("parse_mode", None)
        retry_kwargs.pop("entities", None)
        return _original_edit_message_text(_box_ui_text(text), chat_id, message_id, *args, **retry_kwargs)

bot.send_message = _boxed_send_message
bot.edit_message_text = _boxed_edit_message_text

# --- Bot start time for uptime tracking ---
import zoneinfo
IST = zoneinfo.ZoneInfo("Asia/Kolkata")
BOT_START_TIME = datetime.now(IST)

# --- Data structures ---
bot_scripts = {}
user_subscriptions = {}
user_files = {}
active_users = set()
admin_ids = {ADMIN_ID, OWNER_ID}
banned_users = set()
user_limits = {}  # Custom limits per user
bot_locked = False
maintenance_mode = False  # When enabled, normal users see maintenance message; admins remain unrestricted.
subscription_mode = True  # When enabled, mandatory channel subscription checks are enforced.

# --- Manual Modules Installation System ---
pending_modules = {}  # {user_id: {module_name: package_name}}
manual_install_requests = {}  # {admin_id: {user_id: {module_name: package_name}}}

# --- Mandatory Channels/Groups ---
mandatory_channels = {}  # {channel_id: {'username': 'channel_username', 'name': 'Channel Name'}}

# Store pending ZIP files for approval
pending_zip_files = {}  # {user_id: {file_name: file_content}}

# --- Security Settings ---
SECURITY_CONFIG = {
    'blocked_modules': ['os.system', 'os', 'zipfile', 'subprocess.Popen', 'subprocess', 'eval', 'exec','compile', '__import__'],
    'max_file_size': 20 * 1024 * 1024,  # 20MB
    'max_script_runtime': 3600,  # 1 hour
    'allowed_extensions': ['.py', '.js'],
    'blocked_imports': ['shutil.rmtree', 'subprocess','os.remove', 'os.unlink']
}

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Command Button Layouts ---
COMMAND_BUTTONS_LAYOUT_USER_SPEC = [
    ['🌟╔━━━ UPDATES ━━━╗🌟'],
    ['🚀 Upload File', '🗂️ Check Files'],
    ['⚡ Bot Speed', '📊 Statistics'],
    ['📈 Status', '💬 Contact Owner'],
    ['🔧 Manual Install', '🆘 Help'],
]

ADMIN_COMMAND_BUTTONS_LAYOUT_USER_SPEC = [
    ['🌟╔━━━ UPDATES ━━━╗🌟'],
    ['🚀 Upload File', '🗂️ Check Files'],
    ['⚡ Bot Speed', '📊 Statistics'],
    ['📈 Status', '💳 Subscriptions'],
    ['📡 Broadcast', '🔒 Lock Bot'],
    ['🟢 Running All Code', '⛔ Stop All Scripts'],
    ['👑 Admin Panel', '💬 Contact Owner'],
    ['📢 Channel Add', '🔧 Manual Install'],
    ['👥 User Management', '⚙️ Settings'],
    ['🛠️ Maintenance Mode'],
]

# --- Database Setup ---
def init_db():
    """Initialize the database with required tables"""
    logger.info(f"Initializing database at: {DATABASE_PATH}")
    try:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS subscriptions
                     (user_id INTEGER PRIMARY KEY, expiry TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS user_files
                     (user_id INTEGER, file_name TEXT, file_type TEXT,
                      PRIMARY KEY (user_id, file_name))''')
        c.execute('''CREATE TABLE IF NOT EXISTS active_users
                     (user_id INTEGER PRIMARY KEY, join_date TEXT, last_seen TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS admins
                     (user_id INTEGER PRIMARY KEY, added_by INTEGER, added_date TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS banned_users
                     (user_id INTEGER PRIMARY KEY, reason TEXT, banned_by INTEGER, ban_date TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS user_limits
                     (user_id INTEGER PRIMARY KEY, file_limit INTEGER, set_by INTEGER, set_date TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS mandatory_channels
                     (channel_id TEXT PRIMARY KEY, 
                      channel_username TEXT,
                      channel_name TEXT,
                      added_by INTEGER,
                      added_date TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS bot_settings
                     (setting_key TEXT PRIMARY KEY, setting_value TEXT NOT NULL)''')
        c.execute('''INSERT OR IGNORE INTO bot_settings (setting_key, setting_value) VALUES ('subscription_mode', '1')''')
        c.execute('''CREATE TABLE IF NOT EXISTS install_logs
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      user_id INTEGER,
                      module_name TEXT,
                      package_name TEXT,
                      status TEXT,
                      log TEXT,
                      install_date TEXT)''')
        
        # --- Safe migrations: add missing columns to existing databases ---
        migrations = [
            ("ALTER TABLE active_users ADD COLUMN join_date TEXT",       "active_users.join_date"),
            ("ALTER TABLE active_users ADD COLUMN last_seen TEXT",        "active_users.last_seen"),
            ("ALTER TABLE admins ADD COLUMN added_by INTEGER",            "admins.added_by"),
            ("ALTER TABLE admins ADD COLUMN added_date TEXT",             "admins.added_date"),
            ("ALTER TABLE banned_users ADD COLUMN reason TEXT",           "banned_users.reason"),
            ("ALTER TABLE banned_users ADD COLUMN banned_by INTEGER",     "banned_users.banned_by"),
            ("ALTER TABLE banned_users ADD COLUMN ban_date TEXT",         "banned_users.ban_date"),
            ("ALTER TABLE user_limits ADD COLUMN set_by INTEGER",         "user_limits.set_by"),
            ("ALTER TABLE user_limits ADD COLUMN set_date TEXT",          "user_limits.set_date"),
            ("ALTER TABLE mandatory_channels ADD COLUMN added_by INTEGER","mandatory_channels.added_by"),
            ("ALTER TABLE mandatory_channels ADD COLUMN added_date TEXT", "mandatory_channels.added_date"),
        ]
        for sql, col_name in migrations:
            try:
                c.execute(sql)
                logger.info(f"Migration applied: added column {col_name}")
            except sqlite3.OperationalError:
                pass  # Column already exists — skip silently

        c.execute('INSERT OR IGNORE INTO admins (user_id, added_by, added_date) VALUES (?, ?, ?)', 
                  (OWNER_ID, OWNER_ID, datetime.now().isoformat()))
        if ADMIN_ID != OWNER_ID:
            c.execute('INSERT OR IGNORE INTO admins (user_id, added_by, added_date) VALUES (?, ?, ?)', 
                      (ADMIN_ID, OWNER_ID, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"❌ Database initialization error: {e}", exc_info=True)

def load_data():
    """Load data from database into memory"""
    logger.info("Loading data from database...")
    try:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()

        # Load subscriptions
        c.execute('SELECT user_id, expiry FROM subscriptions')
        for user_id, expiry in c.fetchall():
            try:
                user_subscriptions[user_id] = {'expiry': datetime.fromisoformat(expiry)}
            except ValueError:
                logger.warning(f"⚠️ Invalid expiry date format for user {user_id}: {expiry}. Skipping.")

        # Load user files
        c.execute('SELECT user_id, file_name, file_type FROM user_files')
        for user_id, file_name, file_type in c.fetchall():
            if user_id not in user_files:
                user_files[user_id] = []
            user_files[user_id].append((file_name, file_type))

        # Load active users
        c.execute('SELECT user_id FROM active_users')
        active_users.update(user_id for (user_id,) in c.fetchall())

        # Load admins
        c.execute('SELECT user_id FROM admins')
        admin_ids.update(user_id for (user_id,) in c.fetchall())

        # Load banned users
        c.execute('SELECT user_id FROM banned_users')
        banned_users.update(user_id for (user_id,) in c.fetchall())

        # Load user limits
        c.execute('SELECT user_id, file_limit FROM user_limits')
        for user_id, file_limit in c.fetchall():
            user_limits[user_id] = file_limit

        # Load mandatory channels
        c.execute('SELECT channel_id, channel_username, channel_name FROM mandatory_channels')
        for channel_id, channel_username, channel_name in c.fetchall():
            mandatory_channels[channel_id] = {
                'username': channel_username,
                'name': channel_name
            }

        # Load global bot settings
        global subscription_mode
        c.execute("SELECT setting_value FROM bot_settings WHERE setting_key = 'subscription_mode' LIMIT 1")
        setting_row = c.fetchone()
        if setting_row is not None:
            subscription_mode = str(setting_row[0]).strip().lower() in ('1', 'true', 'on', 'yes')

        conn.close()
        logger.info(f"Data loaded: {len(active_users)} users, {len(user_subscriptions)} subscriptions, {len(admin_ids)} admins, {len(banned_users)} banned users, {len(user_limits)} custom limits, {len(mandatory_channels)} mandatory channels, subscription_mode={subscription_mode}.")
    except Exception as e:
        logger.error(f"❌ Error loading data: {e}", exc_info=True)

# Initialize DB and Load Data at startup
init_db()
load_data()

# Always keep the configured owner authorized as an admin.
# This prevents stale/missing DB admin records from blocking owner-only admin features.
admin_ids.add(OWNER_ID)

# --- Security Functions ---
def check_code_security(file_path, file_type):
    """Check code for dangerous commands (lightweight version)"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Comprehensive dangerous patterns with regex
        dangerous_patterns = [
    # ======================
    # SYSTEM / OS COMMANDS
    # ======================
    r'\bos\b',
    r'\bos\.system\b',
    r'\bos\.(remove|unlink|walk|listdir|scandir|stat|popen|fork|exec|kill|spawn)\b',
    r'\bshutdown\b',
    r'\breboot\b',
    r'rm\s+-rf',
    r'format\s+c:',
    r'dd\s+if=',
    r'\bmkfs\b',
    r'\bfdisk\b',
    r'chmod\s+777',
    r'chmod\s+\+x',
    r'\bsys\.exit\b',
    r'\bsys\.argv\b',

    # ======================
    # BASIC SHELL COMMANDS
    # ======================
    r'\bls\b',
    r'\bcd\b',
    r'\bvps\b',
    r'\bkill\b',
    r'\bkillall\b',
    r'\bpkill\b',
    r'\bkill\s+-\d+',
    r'\bhalt\b',
    r'\bpoweroff\b',
    r'\binit\s+0',
    r'\binit\s+6',
    r'\btelinit\s+0',
    r'\btelinit\s+6',
    r'\bmv\b.*/dev/null',
    r'\bcat\s+>/dev/null',
    r'>\s*/dev/null',
    r'2>\s*&1',
    r'\b&\s*$',
    r'\bnohup\b',
    r'\bdisown\b',

    # ======================
    # FILE DELETION/DESTRUCTION
    # ======================
    r'rm\s+-rf\s+/',
    r'rm\s+-rf\s+~',
    r'rm\s+-rf\s+\.',
    r'rm\s+-rf\s+\*',
    r'rm\s+-rf\s+.*',
    r'\bdd\s+if=/dev/zero',
    r'\bdd\s+of=/dev/sda',
    r'\bmv\s+/dev/null',
    r'>\s+\.bash_history',
    r'>\s+\.zsh_history',
    r'echo\s+""\s+>',
    r'truncate\s+-s\s+0',
    r':>\s*',

    # ======================
    # REGULAR EXPRESSIONS (re) - Yeh add kiya
    # ======================
    r'\bre\b',
    r'\bre\.(compile|search|match|findall|finditer|sub|split|escape|fullmatch)\b',
    r'\bimport\s+re\b',
    r'\bfrom\s+re\s+import\b',
    r'\bregex\b',
    r'\bpattern\s*=\s*re\.compile',
    r're\.(I|IGNORECASE|M|MULTILINE|S|DOTALL|U|UNICODE|X|VERBOSE)',
    r'\.*\{.*,\}',
    r'\^.*\$',
    r'\[.*\]',
    r'\(.*\)',
    r'\?.*',
    r'\*.*',
    r'\+.*',

    # ======================
    # IMAGE/FILE MANIPULATION - Yeh add kiya
    # ======================
    r'image\.jpeg',
    r'image\.jpg',
    r'image\.png',
    r'image\.gif',
    r'image\.bmp',
    r'\.jpeg\b',
    r'\.jpg\b',
    r'\.png\b',
    r'\.gif\b',
    r'\.bmp\b',
    r'\.ico\b',
    r'\.svg\b',
    r'\.webp\b',
    r'\.tiff\b',
    r'\.tif\b',
    r'\.pdf\b',
    r'\.docx\b',
    r'\.doc\b',
    r'\.xlsx\b',
    r'\.xls\b',
    r'\.pptx\b',
    r'\.ppt\b',
    r'\.zip\b',
    r'\.tar\b',
    r'\.gz\b',
    r'\.7z\b',
    r'\.rar\b',
    r'\bPIL\b',
    r'\bImage\b',
    r'\bImage\.(open|save|new|fromarray|frombytes)\b',
    r'\bcv2\b',
    r'\bopencv\b',
    r'\bskimage\b',
    r'\bscikit-image\b',
    r'\bmatplotlib\.image\b',
    r'\bimread\b',
    r'\bimwrite\b',
    r'\bimshow\b',
    r'\bimsave\b',

    # ======================
    # CTYPES / DLL LOADING
    # ======================
    r'\bctypes\b',
    r'\bctypes\.(CDLL|WinDLL|PyDLL|cdll|windll|oledll|py_object|Structure|Union)\b',
    r'\bCDLL\b',
    r'\bWinDLL\b',
    r'\blibc\b',
    r'\bFILE_p\b',
    r'\blibc\.(system|exec|fork|kill|popen)\b',
    r'\bmemset\b',
    r'\bmemcpy\b',
    r'\bmprotect\b',
    r'\bmmap\b',
    r'\bVirtualAlloc\b',
    r'\bCreateProcess\b',
    r'\bLoadLibrary\b',
    r'\bGetProcAddress\b',

    # ======================
    # EXEC / SUBPROCESS
    # ======================
    r'\bsubprocess\b',
    r'\bsubprocess\.(Popen|call|run|check_output|getoutput|getstatusoutput)\b',
    r'\beval\b',
    r'\bexec\b',
    r'\bcompile\b',
    r'\b__import__\b',

    # ======================
    # FILE SYSTEM / DATA READ
    # ======================
    r'\bopen\s*\(',
    r'\bread\s*\(',
    r'\bpathlib\b',
    r'\bglob\b',
    r'\bshutil\b',
    r'\bshutil\.(rmtree|copytree|move|disk_usage)\b',
    r'\bzipfile\b',
    r'\btempfile\b',
    r'\bcPickle\b',
    r'\bshelve\b',
    r'\bsqlite3\b',
    r'\bpandas\.(read_csv|read_excel|read_json)\b',

    # ======================
    # ENV / SECRETS
    # ======================
    r'\bos\.environ\b',
    r'\bdotenv\b',
    r'\bload_dotenv\b',
    r'\bprintenv\b',
    r'\benv\b',
    r'\bgetpass\b',
    r'\bkeyring\b',
    r'\bconfigparser\b',
    r'\byaml\b',
    r'\bjson\.load\b',

    # ======================
    # NETWORK / DATA EXFIL
    # ======================
    r'\bsocket\b',
    r'\bsocket\.(socket|create_connection|gethostname|gethostbyname)\b',
    r'\brequests\b',
    r'\brequests\.(get|post|put|delete|head|request)\b',
    r'\burllib\b',
    r'\burllib2\b',
    r'\burllib3\b',
    r'\bhttp\.client\b',
    r'\bwebsocket\b',
    r'\basyncio\.open_connection\b',
    r'\bwget\b',
    r'\bcurl\b',
    r'\bdownload\b',
    r'\bftplib\b',
    r'\bsmtplib\b',
    r'\bpoplib\b',
    r'\bimaplib\b',
    r'\btelnetlib\b',

    # ======================
    # SSH / REMOTE ACCESS
    # ======================
    r'\bparamiko\b',
    r'\bscp\b',
    r'\bssh\b',
    r'\bsshlib\b',
    r'\bpexpect\b',
    r'\bfabric\b',

    # ======================
    # SYSTEM INFO LEAK
    # ======================
    r'\bpsutil\b',
    r'\bplatform\b',
    r'\bplatform\.(node|processor|machine|architecture|system|version)\b',
    r'\bcmdline\b',
    r'\bpid\b',
    r'/proc/',
    r'\bmem\b',
    r'\bcpu\b',
    r'\bhostname\b',
    r'\buname\b',
    r'\bwhoami\b',

    # ======================
    # PYTHON INTERNAL ABUSE
    # ======================
    r'\bglobals\b',
    r'\blocals\b',
    r'\bvars\b',
    r'\binspect\b',
    r'\bmarshal\b',
    r'\bpickle\b',
    r'\bimportlib\b',
    r'\b__builtins__\b',
    r'\b__import__\b',
    r'\b__loader__\b',
    r'\b__file__\b',
    r'\b__package__\b',
    r'\b__spec__\b',
    r'\b__code__\b',
    r'\b__dict__\b',
    r'\bgetattr\b',
    r'\bsetattr\b',
    r'\bdelattr\b',
    r'\bhasattr\b',
    r'\bcallable\b',

    # ======================
    # TELEGRAM / BOT CONTROL
    # ======================
    r'\btelebot\b',
    r'\btelebot\.types\b',
    r'\baiogram\b',
    r'\bpyrogram\b',
    r'\btelegram\.ext\b',
    r'\btelegram\.bot\b',

    # ======================
    # LINUX / SHELL / BACKDOOR
    # ======================
    r'/bin/sh',
    r'/bin/bash',
    r'/bin/zsh',
    r'/bin/dash',
    r'nc\s+-e',
    r'netcat',
    r'\bbase64\b',
    r'\becho\b.*\|',
    r'\bawk\b',
    r'\bsed\b',
    r'\bfind\b',
    r'\bxargs\b',
    r'\bcrontab\b',
    r'\bservice\b',
    r'\bsystemctl\b',
    r'\btop\b',
    r'\bps\b',
    r'\bhtop\b',
    r'\bifconfig\b',
    r'\bip\s+a',
    r'\bss\b',
    r'\blsof\b',
    r'\bnetstat\b',

    # ======================
    # SSH KEYS / USER DATA
    # ======================
    r'/etc/passwd',
    r'/etc/shadow',
    r'/etc/hosts',
    r'/etc/resolv.conf',
    r'\.ssh/',
    r'id_rsa',
    r'id_dsa',
    r'authorized_keys',
    r'known_hosts',
    r'\.bashrc',
    r'\.bash_profile',
    r'\.zshrc',
    r'\.profile',

    # ======================
    # DATABASE ACCESS
    # ======================
    r'\bsqlite3\b',
    r'\bmysql\b',
    r'\bmysql\.connector\b',
    r'\bpsycopg2\b',
    r'\bpymongo\b',
    r'\bredis\b',

    # ======================
    # CRYPTO / ENCRYPTION
    # ======================
    r'\bcrypt\b',
    r'\bhashlib\b',
    r'\bhmac\b',
    r'\bssl\b',
    r'\btls\b',
    r'\bCrypto\b',
    r'\bcryptography\b',

    # ======================
    # PROCESS CONTROL
    # ======================
    r'\bsignal\b',
    r'\bmultiprocessing\b',
    r'\bthreading\b',
    r'\bdaemon\b',
    r'\batexit\b',
    r'\bexit\b',
    r'\bquit\b',

    # ======================
    # GUI / SCREEN CAPTURE
    # ======================
    r'\bpyautogui\b',
    r'\bselenium\b',
    r'\bpyscreenshot\b',
    r'\bImageGrab\b',

    # ======================
    # KEYLOGGING / INPUT
    # ======================
    r'\bpynput\b',
    r'\bkeyboard\b',
    r'\bmouse\b',
    r'\bgetch\b',

    # ======================
    # MISC DANGEROUS
    # ======================
    r'\.name\b',
    r'\.__name__\b',
    r'\.__class__\b',
    r'\.__bases__\b',
    r'\.__subclasses__\b',
    r'\.__mro__\b',
    r'\.__dictitems__\b',
    r'\.__reduce__\b',
    r'\.__reduce_ex__\b',
    r'\.__getstate__\b',
    r'\.__setstate__\b',

    # ======================
    # WINDOWS SPECIFIC
    # ======================
    r'\bwin32api\b',
    r'\bwin32com\b',
    r'\bwin32con\b',
    r'\bwin32event\b',
    r'\bwin32file\b',
    r'\bwin32process\b',
    r'\bwin32security\b',
    r'\bwmi\b',
    r'\bregedit\b',
    r'\bregistry\b',
    r'\bGetAsyncKeyState\b',
    r'\bSetWindowsHookEx\b',
    r'\btaskkill\b',
    r'\btasklist\b',
    r'\bschtasks\b',

    # ======================
    # ANTI-DEBUG / ANTI-VM
    # ======================
    r'\bptrace\b',
    r'\bdebugger\b',
    r'\bisatty\b',
    r'\bwindbg\b',
    r'\bollydbg\b',

    # ======================
    # MEMORY MANIPULATION
    # ======================
    r'\bmmap\b',
    r'\bmprotect\b',
    r'\bbrk\b',
    r'\bsbrk\b',
    r'\bmalloc\b',
    r'\bfree\b',
    r'\brealloc\b',
    r'\bVirtualAlloc\b',
    r'\bVirtualProtect\b',
    r'\bVirtualFree\b',
    r'\bHeapAlloc\b',
    r'\bHeapFree\b',

    # ======================
    # CODE INJECTION
    # ======================
    r'\binject\b',
    r'\bpayload\b',
    r'\bshellcode\b',
    r'\bmetasploit\b',
    r'\bbackdoor\b',
    r'\brootkit\b',
    r'\btrojan\b',
    r'\bmalware\b',
    r'\bexploit\b',
    r'\bvirus\b',
    r'\bworm\b',

    # ======================
    # NETWORK SCANNING
    # ======================
    r'\bnmap\b',
    r'\bnping\b',
    r'\bscapy\b',
    r'\barp\b',
    r'\bping\b',
    r'\btraceroute\b',
    r'\broute\b',
    r'\bifconfig\b',
    r'\bipconfig\b',
    r'\bnetstat\b',
    r'\bss\b',

    # ======================
    # PRIVILEGE ESCALATION
    # ======================
    r'\bsudo\b',
    r'\bsu\b',
    r'\brunas\b',
    r'\bprivilege\b',
    r'\bescalation\b',
    r'\buac\b',
    r'\bbypassuac\b',

    # ======================
    # PERSISTENCE
    # ======================
    r'\bregistry\b',
    r'\bstartup\b',
    r'\bautostart\b',
    r'\bscheduled\s*task\b',
    r'\bcron\b',
    r'\bat\b',
    r'\binit\.d\b',
    r'\bsystemd\b',
    r'\blaunchd\b',
    r'\bplist\b',

    # ======================
    # MORE DESTRUCTIVE COMMANDS
    # ======================
    r'\bmv\s+.*\s+/dev/null',
    r'\b>+\s*.*\.log',
    r'\btar\s+.*--exclude',
    r'\bfuser\b',
    r'\bstrace\b',
    r'\bltrace\b',
    r'\bgdb\b',
    r'\bobjdump\b',
    r'\bstrings\b',
    r'\bhexdump\b',
    r'\bxxd\b',
    r'\bod\b',
    r'\bsize\b',
    r'\bnm\b',
    r'\breadelf\b',
    r'\bldd\b',
    r'\bfile\b',
    r'\bwhich\b',
    r'\bwhereis\b',
    r'\blocate\b',
    r'\bupdatedb\b',
    r'\bmake\b',
    r'\bgcc\b',
    r'\bg\+\+\b',
    r'\bclang\b',
    r'\bclang\+\+\b',
    r'\bpython\d*\s+-c',
    r'\bperl\s+-e',
    r'\bruby\s+-e',
    r'\bphp\s+-r',
    r'\blua\s+-e',
    r'\bnode\s+-e',
    r'\bwget\s+.*\|\s*sh',
    r'\bcurl\s+.*\|\s*sh',
    r'\bwget\s+.*\|\s*bash',
    r'\bcurl\s+.*\|\s*bash',
    r'\bchattr\s+\+i',
    r'\bchattr\s+-i',
    r'\bsetfacl\b',
    r'\bgetfacl\b',
    r'\bchown\s+.*:.*',
    r'\bchgrp\b',
    r'\busermod\b',
    r'\bgroupmod\b',
    r'\badduser\b',
    r'\baddgroup\b',
    r'\bdeluser\b',
    r'\bdelgroup\b',
    r'\bpasswd\b',
    r'\bvisudo\b',
    r'\bed\b',
    r'\bex\b',
    r'\bvi\b',
    r'\bvim\b',
    r'\bnano\b',
    r'\bemacs\b',
    r'\bpico\b',
    r'\bmicro\b',
    r'\bne\b',

    # ======================
    # ADDITIONAL SECURITY PATTERNS
    # ======================
    r'\b__import__\s*\(',
    r'\bgetattr\s*\(',
    r'\bsetattr\s*\(',
    r'\bdelattr\s*\(',
    r'\bhasattr\s*\(',
    r'\b__getattr__\b',
    r'\b__setattr__\b',
    r'\b__delattr__\b',
    r'\b__getattribute__\b',
    r'\b__call__\b',
    r'\b__enter__\b',
    r'\b__exit__\b',
    r'\b__new__\b',
    r'\b__init__\b',
    r'\b__del__\b',
    r'\b__repr__\b',
    r'\b__str__\b',
    r'\b__bytes__\b',
    r'\b__format__\b',
    r'\b__lt__\b',
    r'\b__le__\b',
    r'\b__eq__\b',
    r'\b__ne__\b',
    r'\b__gt__\b',
    r'\b__ge__\b',
    r'\b__hash__\b',
    r'\b__bool__\b',
    r'\b__getitem__\b',
    r'\b__setitem__\b',
    r'\b__delitem__\b',
    r'\b__iter__\b',
    r'\b__next__\b',
    r'\b__reversed__\b',
    r'\b__contains__\b',
    r'\b__len__\b',
    r'\b__length_hint__\b',
    r'\b__missing__\b',
    r'\b__copy__\b',
    r'\b__deepcopy__\b'
]
        
        found_patterns = []
        for pattern in dangerous_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                found_patterns.append(pattern)
        
        if found_patterns:
            logger.warning(f"🚨 Dangerous patterns detected in {file_path}: {found_patterns}")
            return False, f"Code contains dangerous commands: {', '.join(found_patterns[:5])}"  # Show first 5 only
        
        return True, "Code is safe"
    except Exception as e:
        logger.error(f"Error in security check: {e}")
        return False, f"Security check error: {str(e)}"

def scan_zip_security(zip_path):
    """Check ZIP contents for security (lightweight version)"""
    try:
        dangerous_patterns = [
    # ======================
    # SYSTEM / OS COMMANDS
    # ======================
    r'\bos\b',
    r'\bos\.system\b',
    r'\bos\.(remove|unlink|walk|listdir|scandir|stat|popen|fork|exec|kill|spawn)\b',
    r'\bshutdown\b',
    r'\breboot\b',
    r'rm\s+-rf',
    r'format\s+c:',
    r'dd\s+if=',
    r'\bmkfs\b',
    r'\bfdisk\b',
    r'chmod\s+777',
    r'chmod\s+\+x',
    r'\bsys\.exit\b',
    r'\bsys\.argv\b',

    # ======================
    # BASIC SHELL COMMANDS
    # ======================
    r'\bls\b',
    r'\bcd\b',
    r'\bvps\b',
    r'\bkill\b',
    r'\bkillall\b',
    r'\bpkill\b',
    r'\bkill\s+-\d+',
    r'\bhalt\b',
    r'\bpoweroff\b',
    r'\binit\s+0',
    r'\binit\s+6',
    r'\btelinit\s+0',
    r'\btelinit\s+6',
    r'\bmv\b.*/dev/null',
    r'\bcat\s+>/dev/null',
    r'>\s*/dev/null',
    r'2>\s*&1',
    r'\b&\s*$',
    r'\bnohup\b',
    r'\bdisown\b',

    # ======================
    # FILE DELETION/DESTRUCTION
    # ======================
    r'rm\s+-rf\s+/',
    r'rm\s+-rf\s+~',
    r'rm\s+-rf\s+\.',
    r'rm\s+-rf\s+\*',
    r'rm\s+-rf\s+.*',
    r'\bdd\s+if=/dev/zero',
    r'\bdd\s+of=/dev/sda',
    r'\bmv\s+/dev/null',
    r'>\s+\.bash_history',
    r'>\s+\.zsh_history',
    r'echo\s+""\s+>',
    r'truncate\s+-s\s+0',
    r':>\s*',

    # ======================
    # REGULAR EXPRESSIONS (re) - Yeh add kiya
    # ======================
    r'\bre\b',
    r'\bre\.(compile|search|match|findall|finditer|sub|split|escape|fullmatch)\b',
    r'\bimport\s+re\b',
    r'\bfrom\s+re\s+import\b',
    r'\bregex\b',
    r'\bpattern\s*=\s*re\.compile',
    r're\.(I|IGNORECASE|M|MULTILINE|S|DOTALL|U|UNICODE|X|VERBOSE)',
    r'\.*\{.*,\}',
    r'\^.*\$',
    r'\[.*\]',
    r'\(.*\)',
    r'\?.*',
    r'\*.*',
    r'\+.*',

    # ======================
    # IMAGE/FILE MANIPULATION - Yeh add kiya
    # ======================
    r'image\.jpeg',
    r'image\.jpg',
    r'image\.png',
    r'image\.gif',
    r'image\.bmp',
    r'\.jpeg\b',
    r'\.jpg\b',
    r'\.png\b',
    r'\.gif\b',
    r'\.bmp\b',
    r'\.ico\b',
    r'\.svg\b',
    r'\.webp\b',
    r'\.tiff\b',
    r'\.tif\b',
    r'\.pdf\b',
    r'\.docx\b',
    r'\.doc\b',
    r'\.xlsx\b',
    r'\.xls\b',
    r'\.pptx\b',
    r'\.ppt\b',
    r'\.zip\b',
    r'\.tar\b',
    r'\.gz\b',
    r'\.7z\b',
    r'\.rar\b',
    r'\bPIL\b',
    r'\bImage\b',
    r'\bImage\.(open|save|new|fromarray|frombytes)\b',
    r'\bcv2\b',
    r'\bopencv\b',
    r'\bskimage\b',
    r'\bscikit-image\b',
    r'\bmatplotlib\.image\b',
    r'\bimread\b',
    r'\bimwrite\b',
    r'\bimshow\b',
    r'\bimsave\b',

    # ======================
    # CTYPES / DLL LOADING
    # ======================
    r'\bctypes\b',
    r'\bctypes\.(CDLL|WinDLL|PyDLL|cdll|windll|oledll|py_object|Structure|Union)\b',
    r'\bCDLL\b',
    r'\bWinDLL\b',
    r'\blibc\b',
    r'\bFILE_p\b',
    r'\blibc\.(system|exec|fork|kill|popen)\b',
    r'\bmemset\b',
    r'\bmemcpy\b',
    r'\bmprotect\b',
    r'\bmmap\b',
    r'\bVirtualAlloc\b',
    r'\bCreateProcess\b',
    r'\bLoadLibrary\b',
    r'\bGetProcAddress\b',

    # ======================
    # EXEC / SUBPROCESS
    # ======================
    r'\bsubprocess\b',
    r'\bsubprocess\.(Popen|call|run|check_output|getoutput|getstatusoutput)\b',
    r'\beval\b',
    r'\bexec\b',
    r'\bcompile\b',
    r'\b__import__\b',

    # ======================
    # FILE SYSTEM / DATA READ
    # ======================
    r'\bopen\s*\(',
    r'\bread\s*\(',
    r'\bpathlib\b',
    r'\bglob\b',
    r'\bshutil\b',
    r'\bshutil\.(rmtree|copytree|move|disk_usage)\b',
    r'\bzipfile\b',
    r'\btempfile\b',
    r'\bcPickle\b',
    r'\bshelve\b',
    r'\bsqlite3\b',
    r'\bpandas\.(read_csv|read_excel|read_json)\b',

    # ======================
    # ENV / SECRETS
    # ======================
    r'\bos\.environ\b',
    r'\bdotenv\b',
    r'\bload_dotenv\b',
    r'\bprintenv\b',
    r'\benv\b',
    r'\bgetpass\b',
    r'\bkeyring\b',
    r'\bconfigparser\b',
    r'\byaml\b',
    r'\bjson\.load\b',

    # ======================
    # NETWORK / DATA EXFIL
    # ======================
    r'\bsocket\b',
    r'\bsocket\.(socket|create_connection|gethostname|gethostbyname)\b',
    r'\brequests\b',
    r'\brequests\.(get|post|put|delete|head|request)\b',
    r'\burllib\b',
    r'\burllib2\b',
    r'\burllib3\b',
    r'\bhttp\.client\b',
    r'\bwebsocket\b',
    r'\basyncio\.open_connection\b',
    r'\bwget\b',
    r'\bcurl\b',
    r'\bdownload\b',
    r'\bftplib\b',
    r'\bsmtplib\b',
    r'\bpoplib\b',
    r'\bimaplib\b',
    r'\btelnetlib\b',

    # ======================
    # SSH / REMOTE ACCESS
    # ======================
    r'\bparamiko\b',
    r'\bscp\b',
    r'\bssh\b',
    r'\bsshlib\b',
    r'\bpexpect\b',
    r'\bfabric\b',

    # ======================
    # SYSTEM INFO LEAK
    # ======================
    r'\bpsutil\b',
    r'\bplatform\b',
    r'\bplatform\.(node|processor|machine|architecture|system|version)\b',
    r'\bcmdline\b',
    r'\bpid\b',
    r'/proc/',
    r'\bmem\b',
    r'\bcpu\b',
    r'\bhostname\b',
    r'\buname\b',
    r'\bwhoami\b',

    # ======================
    # PYTHON INTERNAL ABUSE
    # ======================
    r'\bglobals\b',
    r'\blocals\b',
    r'\bvars\b',
    r'\binspect\b',
    r'\bmarshal\b',
    r'\bpickle\b',
    r'\bimportlib\b',
    r'\b__builtins__\b',
    r'\b__import__\b',
    r'\b__loader__\b',
    r'\b__file__\b',
    r'\b__package__\b',
    r'\b__spec__\b',
    r'\b__code__\b',
    r'\b__dict__\b',
    r'\bgetattr\b',
    r'\bsetattr\b',
    r'\bdelattr\b',
    r'\bhasattr\b',
    r'\bcallable\b',

    # ======================
    # TELEGRAM / BOT CONTROL
    # ======================
    r'\btelebot\b',
    r'\btelebot\.types\b',
    r'\baiogram\b',
    r'\bpyrogram\b',
    r'\btelegram\.ext\b',
    r'\btelegram\.bot\b',

    # ======================
    # LINUX / SHELL / BACKDOOR
    # ======================
    r'/bin/sh',
    r'/bin/bash',
    r'/bin/zsh',
    r'/bin/dash',
    r'nc\s+-e',
    r'netcat',
    r'\bbase64\b',
    r'\becho\b.*\|',
    r'\bawk\b',
    r'\bsed\b',
    r'\bfind\b',
    r'\bxargs\b',
    r'\bcrontab\b',
    r'\bservice\b',
    r'\bsystemctl\b',
    r'\btop\b',
    r'\bps\b',
    r'\bhtop\b',
    r'\bifconfig\b',
    r'\bip\s+a',
    r'\bss\b',
    r'\blsof\b',
    r'\bnetstat\b',

    # ======================
    # SSH KEYS / USER DATA
    # ======================
    r'/etc/passwd',
    r'/etc/shadow',
    r'/etc/hosts',
    r'/etc/resolv.conf',
    r'\.ssh/',
    r'id_rsa',
    r'id_dsa',
    r'authorized_keys',
    r'known_hosts',
    r'\.bashrc',
    r'\.bash_profile',
    r'\.zshrc',
    r'\.profile',

    # ======================
    # DATABASE ACCESS
    # ======================
    r'\bsqlite3\b',
    r'\bmysql\b',
    r'\bmysql\.connector\b',
    r'\bpsycopg2\b',
    r'\bpymongo\b',
    r'\bredis\b',

    # ======================
    # CRYPTO / ENCRYPTION
    # ======================
    r'\bcrypt\b',
    r'\bhashlib\b',
    r'\bhmac\b',
    r'\bssl\b',
    r'\btls\b',
    r'\bCrypto\b',
    r'\bcryptography\b',

    # ======================
    # PROCESS CONTROL
    # ======================
    r'\bsignal\b',
    r'\bmultiprocessing\b',
    r'\bthreading\b',
    r'\bdaemon\b',
    r'\batexit\b',
    r'\bexit\b',
    r'\bquit\b',

    # ======================
    # GUI / SCREEN CAPTURE
    # ======================
    r'\bpyautogui\b',
    r'\bselenium\b',
    r'\bpyscreenshot\b',
    r'\bImageGrab\b',

    # ======================
    # KEYLOGGING / INPUT
    # ======================
    r'\bpynput\b',
    r'\bkeyboard\b',
    r'\bmouse\b',
    r'\bgetch\b',

    # ======================
    # MISC DANGEROUS
    # ======================
    r'\.name\b',
    r'\.__name__\b',
    r'\.__class__\b',
    r'\.__bases__\b',
    r'\.__subclasses__\b',
    r'\.__mro__\b',
    r'\.__dictitems__\b',
    r'\.__reduce__\b',
    r'\.__reduce_ex__\b',
    r'\.__getstate__\b',
    r'\.__setstate__\b',

    # ======================
    # WINDOWS SPECIFIC
    # ======================
    r'\bwin32api\b',
    r'\bwin32com\b',
    r'\bwin32con\b',
    r'\bwin32event\b',
    r'\bwin32file\b',
    r'\bwin32process\b',
    r'\bwin32security\b',
    r'\bwmi\b',
    r'\bregedit\b',
    r'\bregistry\b',
    r'\bGetAsyncKeyState\b',
    r'\bSetWindowsHookEx\b',
    r'\btaskkill\b',
    r'\btasklist\b',
    r'\bschtasks\b',

    # ======================
    # ANTI-DEBUG / ANTI-VM
    # ======================
    r'\bptrace\b',
    r'\bdebugger\b',
    r'\bisatty\b',
    r'\bwindbg\b',
    r'\bollydbg\b',

    # ======================
    # MEMORY MANIPULATION
    # ======================
    r'\bmmap\b',
    r'\bmprotect\b',
    r'\bbrk\b',
    r'\bsbrk\b',
    r'\bmalloc\b',
    r'\bfree\b',
    r'\brealloc\b',
    r'\bVirtualAlloc\b',
    r'\bVirtualProtect\b',
    r'\bVirtualFree\b',
    r'\bHeapAlloc\b',
    r'\bHeapFree\b',

    # ======================
    # CODE INJECTION
    # ======================
    r'\binject\b',
    r'\bpayload\b',
    r'\bshellcode\b',
    r'\bmetasploit\b',
    r'\bbackdoor\b',
    r'\brootkit\b',
    r'\btrojan\b',
    r'\bmalware\b',
    r'\bexploit\b',
    r'\bvirus\b',
    r'\bworm\b',

    # ======================
    # NETWORK SCANNING
    # ======================
    r'\bnmap\b',
    r'\bnping\b',
    r'\bscapy\b',
    r'\barp\b',
    r'\bping\b',
    r'\btraceroute\b',
    r'\broute\b',
    r'\bifconfig\b',
    r'\bipconfig\b',
    r'\bnetstat\b',
    r'\bss\b',

    # ======================
    # PRIVILEGE ESCALATION
    # ======================
    r'\bsudo\b',
    r'\bsu\b',
    r'\brunas\b',
    r'\bprivilege\b',
    r'\bescalation\b',
    r'\buac\b',
    r'\bbypassuac\b',

    # ======================
    # PERSISTENCE
    # ======================
    r'\bregistry\b',
    r'\bstartup\b',
    r'\bautostart\b',
    r'\bscheduled\s*task\b',
    r'\bcron\b',
    r'\bat\b',
    r'\binit\.d\b',
    r'\bsystemd\b',
    r'\blaunchd\b',
    r'\bplist\b',

    # ======================
    # MORE DESTRUCTIVE COMMANDS
    # ======================
    r'\bmv\s+.*\s+/dev/null',
    r'\b>+\s*.*\.log',
    r'\btar\s+.*--exclude',
    r'\bfuser\b',
    r'\bstrace\b',
    r'\bltrace\b',
    r'\bgdb\b',
    r'\bobjdump\b',
    r'\bstrings\b',
    r'\bhexdump\b',
    r'\bxxd\b',
    r'\bod\b',
    r'\bsize\b',
    r'\bnm\b',
    r'\breadelf\b',
    r'\bldd\b',
    r'\bfile\b',
    r'\bwhich\b',
    r'\bwhereis\b',
    r'\blocate\b',
    r'\bupdatedb\b',
    r'\bmake\b',
    r'\bgcc\b',
    r'\bg\+\+\b',
    r'\bclang\b',
    r'\bclang\+\+\b',
    r'\bpython\d*\s+-c',
    r'\bperl\s+-e',
    r'\bruby\s+-e',
    r'\bphp\s+-r',
    r'\blua\s+-e',
    r'\bnode\s+-e',
    r'\bwget\s+.*\|\s*sh',
    r'\bcurl\s+.*\|\s*sh',
    r'\bwget\s+.*\|\s*bash',
    r'\bcurl\s+.*\|\s*bash',
    r'\bchattr\s+\+i',
    r'\bchattr\s+-i',
    r'\bsetfacl\b',
    r'\bgetfacl\b',
    r'\bchown\s+.*:.*',
    r'\bchgrp\b',
    r'\busermod\b',
    r'\bgroupmod\b',
    r'\badduser\b',
    r'\baddgroup\b',
    r'\bdeluser\b',
    r'\bdelgroup\b',
    r'\bpasswd\b',
    r'\bvisudo\b',
    r'\bed\b',
    r'\bex\b',
    r'\bvi\b',
    r'\bvim\b',
    r'\bnano\b',
    r'\bemacs\b',
    r'\bpico\b',
    r'\bmicro\b',
    r'\bne\b',

    # ======================
    # ADDITIONAL SECURITY PATTERNS
    # ======================
    r'\b__import__\s*\(',
    r'\bgetattr\s*\(',
    r'\bsetattr\s*\(',
    r'\bdelattr\s*\(',
    r'\bhasattr\s*\(',
    r'\b__getattr__\b',
    r'\b__setattr__\b',
    r'\b__delattr__\b',
    r'\b__getattribute__\b',
    r'\b__call__\b',
    r'\b__enter__\b',
    r'\b__exit__\b',
    r'\b__new__\b',
    r'\b__init__\b',
    r'\b__del__\b',
    r'\b__repr__\b',
    r'\b__str__\b',
    r'\b__bytes__\b',
    r'\b__format__\b',
    r'\b__lt__\b',
    r'\b__le__\b',
    r'\b__eq__\b',
    r'\b__ne__\b',
    r'\b__gt__\b',
    r'\b__ge__\b',
    r'\b__hash__\b',
    r'\b__bool__\b',
    r'\b__getitem__\b',
    r'\b__setitem__\b',
    r'\b__delitem__\b',
    r'\b__iter__\b',
    r'\b__next__\b',
    r'\b__reversed__\b',
    r'\b__contains__\b',
    r'\b__len__\b',
    r'\b__length_hint__\b',
    r'\b__missing__\b',
    r'\b__copy__\b',
    r'\b__deepcopy__\b'
]
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for file_info in zip_ref.infolist():
                if file_info.filename.endswith(('.py', '.js', '.zip', '.txt', '.sh', '.bat', '.cmd')):
                    with zip_ref.open(file_info.filename) as f:
                        try:
                            content = f.read().decode('utf-8', errors='ignore')
                        except:
                            continue
                        
                        for pattern in dangerous_patterns:
                            if re.search(pattern, content, re.IGNORECASE):
                                return False, f"File {file_info.filename} contains dangerous command: {pattern}"
        return True, "Archive is safe"
    except Exception as e:
        return False, f"Error scanning archive: {str(e)}"

# --- Mandatory Channels Functions ---
def is_user_member(user_id, channel_id):
    """Check if user is member of a channel"""
    try:
        chat_member = bot.get_chat_member(channel_id, user_id)
        return chat_member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        logger.error(f"Error checking channel membership for {user_id} in {channel_id}: {e}")
        return False

def check_mandatory_subscription(user_id):
    """Check mandatory channels, while active paid subscribers bypass the access gate."""
    # When paid Subscription Mode is ON, an active subscription grants bot access.
    # Admins/owners are also always allowed through this gate.
    if subscription_mode:
        try:
            if user_id in admin_ids or _has_active_paid_subscription(user_id):
                return True, []
        except Exception:
            pass
    if not subscription_mode:
        return True, []  # Subscription mode OFF: bypass mandatory channel checks.
    if not mandatory_channels:
        return True, []  # No mandatory channels exist
    
    not_joined = []
    for channel_id, channel_info in mandatory_channels.items():
        if not is_user_member(user_id, channel_id):
            not_joined.append((channel_id, channel_info))
    
    if not_joined:
        return False, not_joined
    return True, []

def save_mandatory_channel(channel_id, channel_username, channel_name, added_by):
    """Save mandatory channel to database"""
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            added_date = datetime.now().isoformat()
            c.execute('INSERT OR REPLACE INTO mandatory_channels (channel_id, channel_username, channel_name, added_by, added_date) VALUES (?, ?, ?, ?, ?)',
                      (channel_id, channel_username, channel_name, added_by, added_date))
            conn.commit()
            mandatory_channels[channel_id] = {
                'username': channel_username,
                'name': channel_name
            }
            logger.info(f"Saved mandatory channel: {channel_name} ({channel_id})")
            return True
        except sqlite3.Error as e:
            logger.error(f"❌ SQLite error saving channel: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error saving channel: {e}", exc_info=True)
            return False
        finally:
            conn.close()

def remove_mandatory_channel_db(channel_id):
    """Remove mandatory channel from database"""
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute('DELETE FROM mandatory_channels WHERE channel_id = ?', (channel_id,))
            conn.commit()
            if channel_id in mandatory_channels:
                del mandatory_channels[channel_id]
            logger.info(f"Removed mandatory channel: {channel_id}")
            return True
        except sqlite3.Error as e:
            logger.error(f"❌ SQLite error removing channel: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error removing channel: {e}", exc_info=True)
            return False
        finally:
            conn.close()

def save_subscription_mode_setting(enabled):
    """Persist the global mandatory-subscription mode."""
    try:
        with DB_LOCK:
            conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
            c = conn.cursor()
            c.execute(
                "INSERT OR REPLACE INTO bot_settings (setting_key, setting_value) VALUES ('subscription_mode', ?)",
                ('1' if enabled else '0',)
            )
            conn.commit()
            conn.close()
        return True
    except Exception as e:
        logger.error(f"❌ Failed to save subscription mode: {e}", exc_info=True)
        return False

def create_mandatory_channels_menu():
    """Create mandatory channels management menu"""
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.row(
        _sc_inline_button('➕ Add Channel', callback_data='add_mandatory_channel'),
        _sc_inline_button('➖ Remove Channel', callback_data='remove_mandatory_channel')
    )
    markup.row(_sc_inline_button('📋 List Channels', callback_data='list_mandatory_channels'))
    markup.row(_sc_inline_button('🔙 Back to Main', callback_data='back_to_main'))
    return markup

def create_subscription_check_message(not_joined_channels):
    """Create subscription verification message"""
    message = "📢 **Important: Join Our Channels First:**\n\n"
    
    markup = types.InlineKeyboardMarkup()
    
    for channel_id, channel_info in not_joined_channels:
        channel_username = channel_info.get('username', '')
        channel_name = channel_info.get('name', 'Channel')
        
        if channel_username:
            channel_link = f"https://t.me/{channel_username.replace('@', '')}"
        else:
            channel_link = f"https://t.me/c/{channel_id.replace('-100', '')}"
        
        message += f"• {channel_name}\n"
        markup.add(_sc_inline_button(f"Join {channel_name}", url=channel_link))
    
    markup.add(_sc_inline_button("✅ Verify Subscription", callback_data='check_subscription_status'))
    
    return message, markup

# --- Database Lock ---
DB_LOCK = threading.Lock()

# --- User Management Functions ---
def is_user_banned(user_id):
    """Check if user is banned"""
    return user_id in banned_users

def ban_user_db(user_id, reason, banned_by):
    """Ban a user"""
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            ban_date = datetime.now().isoformat()
            c.execute('INSERT OR REPLACE INTO banned_users (user_id, reason, banned_by, ban_date) VALUES (?, ?, ?, ?)',
                      (user_id, reason, banned_by, ban_date))
            conn.commit()
            banned_users.add(user_id)
            logger.warning(f"User {user_id} banned by {banned_by}. Reason: {reason}")
            return True
        except sqlite3.Error as e:
            logger.error(f"❌ SQLite error banning user {user_id}: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error banning user {user_id}: {e}", exc_info=True)
            return False
        finally:
            conn.close()

def unban_user_db(user_id):
    """Unban a user"""
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute('DELETE FROM banned_users WHERE user_id = ?', (user_id,))
            conn.commit()
            banned_users.discard(user_id)
            logger.info(f"User {user_id} unbanned")
            return True
        except sqlite3.Error as e:
            logger.error(f"❌ SQLite error unbanning user {user_id}: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error unbanning user {user_id}: {e}", exc_info=True)
            return False
        finally:
            conn.close()

def set_user_limit_db(user_id, limit, set_by):
    """Set custom file limit for a user"""
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            set_date = datetime.now().isoformat()
            c.execute('INSERT OR REPLACE INTO user_limits (user_id, file_limit, set_by, set_date) VALUES (?, ?, ?, ?)',
                      (user_id, limit, set_by, set_date))
            conn.commit()
            user_limits[user_id] = limit
            logger.info(f"Set file limit {limit} for user {user_id} by {set_by}")
            return True
        except sqlite3.Error as e:
            logger.error(f"❌ SQLite error setting limit for user {user_id}: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error setting limit for user {user_id}: {e}", exc_info=True)
            return False
        finally:
            conn.close()

def remove_user_limit_db(user_id):
    """Remove custom file limit for a user"""
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute('DELETE FROM user_limits WHERE user_id = ?', (user_id,))
            conn.commit()
            if user_id in user_limits:
                del user_limits[user_id]
            logger.info(f"Removed custom limit for user {user_id}")
            return True
        except sqlite3.Error as e:
            logger.error(f"❌ SQLite error removing limit for user {user_id}: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error removing limit for user {user_id}: {e}", exc_info=True)
            return False
        finally:
            conn.close()

# --- Modified Helper Functions ---
def get_user_folder(user_id):
    """Get or create user's folder for storing files"""
    user_folder = os.path.join(UPLOAD_BOTS_DIR, str(user_id))
    os.makedirs(user_folder, exist_ok=True)
    return user_folder

def get_user_file_limit(user_id):
    """Get the file upload limit for a user"""
    if user_id == OWNER_ID: return OWNER_LIMIT
    if user_id in admin_ids: return ADMIN_LIMIT
    if user_id in user_limits: return user_limits[user_id]
    if user_id in user_subscriptions and user_subscriptions[user_id]['expiry'] > datetime.now():
        return SUBSCRIBED_USER_LIMIT
    return FREE_USER_LIMIT

def get_user_file_count(user_id):
    """Get the number of files uploaded by a user"""
    return len(user_files.get(user_id, []))

def is_bot_running(script_owner_id, file_name):
    """Check script state without requiring psutil (Termux/Android compatible)."""
    script_key = f"{script_owner_id}_{file_name}"
    script_info = bot_scripts.get(script_key)
    if not script_info:
        return False

    process = script_info.get('process')
    if process is None:
        return False

    try:
        # subprocess.Popen provides poll() on Python/Termux/VPS.
        # None means the child is still running.
        return process.poll() is None
    except Exception as e:
        logger.warning(f"Could not check process state for {script_key}: {e}")
        return False

def kill_process_tree(process_info):
    """Stop a script process. Uses psutil when available, otherwise Popen methods."""
    try:
        if not process_info:
            return
        process = process_info.get('process') if isinstance(process_info, dict) else process_info
        if process is None:
            return

        pid = getattr(process, 'pid', None)
        script_key = process_info.get('script_key', str(pid)) if isinstance(process_info, dict) else str(pid)

        if psutil is not None and pid:
            try:
                parent = psutil.Process(pid)
                children = parent.children(recursive=True)
                for child in children:
                    try:
                        child.terminate()
                    except Exception:
                        pass
                try:
                    psutil.wait_procs(children, timeout=1)
                except Exception:
                    pass
                try:
                    parent.terminate()
                    parent.wait(timeout=1)
                except Exception:
                    try:
                        parent.kill()
                    except Exception:
                        pass
                return
            except Exception as e:
                logger.warning(f"psutil process-tree stop failed for {script_key}: {e}")

        # Fallback: stop the tracked Popen process directly.
        try:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=2)
                except Exception:
                    process.kill()
        except Exception as e:
            logger.warning(f"Fallback process stop failed for {script_key}: {e}")
    except Exception as e:
        logger.error(f"Error stopping process tree: {e}", exc_info=True)

def save_install_log(user_id, module_name, package_name, status, log):
    """Save installation log to database"""
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            install_date = datetime.now().isoformat()
            c.execute('INSERT INTO install_logs (user_id, module_name, package_name, status, log, install_date) VALUES (?, ?, ?, ?, ?, ?)',
                      (user_id, module_name, package_name, status, log, install_date))
            conn.commit()
            logger.info(f"Saved install log for user {user_id}: {module_name} - {status}")
        except sqlite3.Error as e:
            logger.error(f"❌ SQLite error saving install log: {e}")
        except Exception as e:
            logger.error(f"❌ Unexpected error saving install log: {e}", exc_info=True)
        finally:
            conn.close()

# Python module -> pip package mapping used by Manual Install
TELEGRAM_MODULES = {
    "telebot": "pyTelegramBotAPI",
    "telegram": "python-telegram-bot",
    "python_telegram_bot": "python-telegram-bot",
    "aiogram": "aiogram",
    "pyrogram": "pyrogram",
    "telethon": "telethon",
    "telethon.sync": "telethon",
    "requests": "requests",
    "flask": "Flask",
    "dotenv": "python-dotenv",
    "bs4": "beautifulsoup4",
    "beautifulsoup4": "beautifulsoup4",
    "pytz": "pytz",
    "psutil": "psutil",
    "PIL": "Pillow",
    "pillow": "Pillow",
}

def attempt_install_pip(module_name, message, manual_request=False):
    """Install a Python package safely for this bot, including restricted VPS/Pterodactyl.

    Uses a bot-local .python_packages directory first so installation does not
    require root permissions. The directory is added to sys.path immediately.
    """
    raw_name = (module_name or '').strip()
    package_name = TELEGRAM_MODULES.get(raw_name.lower(), raw_name)
    if not package_name:
        return False, "Invalid module/package name."
    if package_name is None:
        return False, "Core module - no installation needed"

    try:
        from pathlib import Path
        bot_package_dir = Path(__file__).resolve().parent / '.python_packages'
        bot_package_dir.mkdir(parents=True, exist_ok=True)
        package_dir_str = str(bot_package_dir)
        if package_dir_str not in sys.path:
            sys.path.insert(0, package_dir_str)

        if manual_request:
            bot.reply_to(message, f"🔄 Manual installation requested for `{raw_name}` → `{package_name}`...", parse_mode='Markdown')
        else:
            bot.reply_to(message, f"🐍 Module `{raw_name}` not found. Installing `{package_name}`...", parse_mode='Markdown')

        # First choice: user-writable local install. This works on Pterodactyl/VPS
        # without sudo and avoids modifying the system Python environment.
        # PEP 668-safe install: always prefer the bot-local directory.
        # --break-system-packages is passed explicitly for Debian/Ubuntu images
        # that mark the interpreter as externally managed. The env variable is
        # also set for pip versions that honor PIP_BREAK_SYSTEM_PACKAGES.
        pip_env = os.environ.copy()
        pip_env['PIP_BREAK_SYSTEM_PACKAGES'] = '1'
        command = [sys.executable, '-m', 'pip', 'install', '--disable-pip-version-check', '--no-input', '--upgrade', '--break-system-packages', '--target', package_dir_str, package_name]
        logger.info(f"Running local install: {' '.join(command)}")
        result = subprocess.run(command, capture_output=True, text=True, check=False,
                                encoding='utf-8', errors='ignore', timeout=300, env=pip_env)

        if result.returncode != 0:
            # Fallback for environments where pip blocks --target/externally managed
            # installs. Still keep --break-system-packages rather than requiring sudo.
            fallback = [sys.executable, '-m', 'pip', 'install', '--disable-pip-version-check', '--no-input', '--upgrade', '--break-system-packages', package_name]
            logger.warning(f"Local target install failed; trying fallback: {' '.join(fallback)}")
            fallback_result = subprocess.run(fallback, capture_output=True, text=True, check=False,
                                             encoding='utf-8', errors='ignore', timeout=300, env=pip_env)
            if fallback_result.returncode == 0:
                result = fallback_result
            else:
                # Last fallback: user-site installation. This is useful on VPS images
                # whose pip rejects a target directory but permits user installs.
                user_fallback = [sys.executable, '-m', 'pip', 'install', '--disable-pip-version-check', '--no-input', '--upgrade', '--break-system-packages', '--user', package_name]
                logger.warning(f'PIP target/system install failed; trying user install: {" ".join(user_fallback)}')
                user_result = subprocess.run(user_fallback, capture_output=True, text=True, check=False,
                                             encoding='utf-8', errors='ignore', timeout=300, env=pip_env)
                if user_result.returncode == 0:
                    result = user_result

        if result.returncode == 0:
            # Make newly installed packages importable in this running process.
            if package_dir_str not in sys.path:
                sys.path.insert(0, package_dir_str)
            log_msg = f"Installed {package_name}. Output:\n{result.stdout}"
            logger.info(log_msg)
            success_msg = f"✅ Package `{package_name}` (for `{raw_name}`) installed successfully."
            bot.reply_to(message, success_msg, parse_mode='Markdown')
            save_install_log(message.from_user.id, raw_name, package_name, "success", log_msg)
            return True, log_msg

        output = (result.stderr or result.stdout or 'No pip output').strip()
        if len(output) > 3000:
            output = output[-3000:]
        error_msg = f"❌ Failed to install `{package_name}` for `{raw_name}`.\nLog:\n```\n{output}\n```"
        logger.error(error_msg)
        bot.reply_to(message, error_msg, parse_mode='Markdown')
        save_install_log(message.from_user.id, raw_name, package_name, "failed", error_msg)
        return False, error_msg
    except subprocess.TimeoutExpired:
        error_msg = f"❌ Installation timed out for `{package_name}` (5 minutes)."
        logger.error(error_msg)
        bot.reply_to(message, error_msg, parse_mode='Markdown')
        save_install_log(message.from_user.id, raw_name, package_name, "timeout", error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"❌ Error installing `{package_name}`: {str(e)}"
        logger.error(error_msg, exc_info=True)
        bot.reply_to(message, error_msg, parse_mode='Markdown')
        save_install_log(message.from_user.id, raw_name, package_name, "error", error_msg)
        return False, error_msg

def attempt_install_npm(module_name, user_folder, message, manual_request=False):
    """Install Node package via npm"""
    try:
        if manual_request:
            bot.reply_to(message, f"🔄 Manual Node package installation requested for `{module_name}`...", parse_mode='Markdown')
        else:
            bot.reply_to(message, f"🟠 Node package `{module_name}` not found. Installing locally...", parse_mode='Markdown')
        
        command = ['npm', 'install', module_name]
        logger.info(f"Running npm install: {' '.join(command)} in {user_folder}")
        result = subprocess.run(command, capture_output=True, text=True, check=False, cwd=user_folder, encoding='utf-8', errors='ignore')
        
        if result.returncode == 0:
            log_msg = f"Installed {module_name}. Output:\n{result.stdout}"
            logger.info(log_msg)
            success_msg = f"✅ Node package `{module_name}` installed locally."
            bot.reply_to(message, success_msg, parse_mode='Markdown')
            save_install_log(message.from_user.id, module_name, module_name, "success", log_msg)
            return True, log_msg
        else:
            error_msg = f"❌ Failed to install Node package `{module_name}`.\nLog:\n```\n{result.stderr or result.stdout}\n```"
            logger.error(error_msg)
            if len(error_msg) > 4000: error_msg = error_msg[:4000] + "\n... (Log truncated)"
            bot.reply_to(message, error_msg, parse_mode='Markdown')
            save_install_log(message.from_user.id, module_name, module_name, "failed", error_msg)
            return False, error_msg
    except FileNotFoundError:
         error_msg = "❌ Error: 'npm' not found. Ensure Node.js/npm are installed and in PATH."
         logger.error(error_msg)
         bot.reply_to(message, error_msg)
         save_install_log(message.from_user.id, module_name, module_name, "error", error_msg)
         return False, error_msg
    except Exception as e:
        error_msg = f"❌ Error installing Node package `{module_name}`: {str(e)}"
        logger.error(error_msg, exc_info=True)
        bot.reply_to(message, error_msg)
        save_install_log(message.from_user.id, module_name, module_name, "error", error_msg)
        return False, error_msg

def manual_install_module_init(message):
    """Initialize manual module installation"""
    user_id = message.from_user.id
    
    if is_user_banned(user_id):
        bot.reply_to(message, "❌ You are banned from using this bot.")
        return
    
    # Check mandatory subscription first
    is_subscribed, not_joined = check_mandatory_subscription(user_id)
    if not is_subscribed and user_id not in admin_ids:
        subscription_message, markup = create_subscription_check_message(not_joined)
        bot.reply_to(message, subscription_message, reply_markup=markup, parse_mode='Markdown')
        return
    
    if bot_locked and user_id not in admin_ids:
        bot.reply_to(message, "╔══════════════════════════════╗\n║   🔒 ʙᴏᴛ ᴄᴏɴᴛʀᴏʟ ʟᴏᴄᴋᴇᴅ   ║\n╚══════════════════════════════╝\n\n⛔ ʟᴏᴄᴋᴇᴅ sᴛᴀᴛᴜs\n\n🔐 ᴀᴅᴍɪɴ ʟᴏᴄᴋ ᴀᴄᴛɪᴠᴇ\n⚠️ ᴜsᴇʀ ᴀᴄᴄᴇss ʀᴇsᴛʀɪᴄᴛᴇᴅ")
        return
    
    msg = bot.reply_to(message,
        "╔══════════════════════════╗\n"
        "║   🔧 MANUAL INSTALL 🔧  ║\n"
        "╚══════════════════════════╝\n\n"
        "📦 Send the module name to install:\n\n"
        "├ 🐍 Python : requests\n"
        "├ 🐍 Python : pillow\n"
        "└ 🟨 Node   : npm:axios\n\n"
        "❌ Send /cancel to abort.")
    bot.register_next_step_handler(msg, process_manual_install_module)

def process_manual_install_module(message):
    """Process manual module installation"""
    user_id = message.from_user.id
    
    if is_user_banned(user_id):
        bot.reply_to(message, "❌ You are banned from using this bot.")
        return
    
    text = (message.text or "").strip()
    
    # If user tapped a (possibly royal/small-caps) menu button instead of
    # typing a module name, re-route it to the correct action.
    button_logic = _get_button_logic(text)
    if button_logic:
        button_logic(message)
        return
    
    # If it's any slash command, let the normal handlers take over
    if text.startswith('/'):
        if text.lower() == '/cancel':
            bot.reply_to(message, "❌ Installation cancelled.")
        return
    
    # Reject obviously invalid names (contain spaces and look like button labels)
    if len(text) > 50 or '\n' in text:
        bot.reply_to(message, "❌ Invalid module name. Installation cancelled.")
        return
    
    module_name = text
    if any(ch in module_name for ch in ('\x00', '\r', '\n')) or len(module_name) > 100:
        bot.reply_to(message, "❌ Invalid module name. Installation cancelled.")
        return

    # Check if it's a Node.js module
    if module_name.lower().startswith('npm:'):
        module_name = module_name[4:].strip()
        user_folder = get_user_folder(user_id)
        success, log = attempt_install_npm(module_name, user_folder, message, manual_request=True)
    else:
        # Python module
        success, log = attempt_install_pip(module_name, message, manual_request=True)
    
    if success:
        logger.info(f"User {user_id} manually installed module: {module_name}")

# --- Database Operations ---
def save_user_file(user_id, file_name, file_type='py'):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute('INSERT OR REPLACE INTO user_files (user_id, file_name, file_type) VALUES (?, ?, ?)',
                      (user_id, file_name, file_type))
            conn.commit()
            if user_id not in user_files: user_files[user_id] = []
            user_files[user_id] = [(fn, ft) for fn, ft in user_files[user_id] if fn != file_name]
            user_files[user_id].append((file_name, file_type))
            logger.info(f"Saved file '{file_name}' ({file_type}) for user {user_id}")
        except sqlite3.Error as e: logger.error(f"❌ SQLite error saving file for user {user_id}, {file_name}: {e}")
        except Exception as e: logger.error(f"❌ Unexpected error saving file for {user_id}, {file_name}: {e}", exc_info=True)
        finally: conn.close()

def remove_user_file_db(user_id, file_name):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute('DELETE FROM user_files WHERE user_id = ? AND file_name = ?', (user_id, file_name))
            conn.commit()
            if user_id in user_files:
                user_files[user_id] = [f for f in user_files[user_id] if f[0] != file_name]
                if not user_files[user_id]: del user_files[user_id]
            logger.info(f"Removed file '{file_name}' for user {user_id} from DB")
        except sqlite3.Error as e: logger.error(f"❌ SQLite error removing file for {user_id}, {file_name}: {e}")
        except Exception as e: logger.error(f"❌ Unexpected error removing file for {user_id}, {file_name}: {e}", exc_info=True)
        finally: conn.close()

def add_active_user(user_id):
    active_users.add(user_id) 
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            join_date = datetime.now().isoformat()
            c.execute('INSERT OR REPLACE INTO active_users (user_id, join_date, last_seen) VALUES (?, ?, ?)', 
                      (user_id, join_date, join_date))
            conn.commit()
            logger.info(f"Added/Updated active user {user_id} in DB")
        except sqlite3.Error as e: logger.error(f"❌ SQLite error adding active user {user_id}: {e}")
        except Exception as e: logger.error(f"❌ Unexpected error adding active user {user_id}: {e}", exc_info=True)
        finally: conn.close()

def save_subscription(user_id, expiry):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            expiry_str = expiry.isoformat()
            c.execute('INSERT OR REPLACE INTO subscriptions (user_id, expiry) VALUES (?, ?)', (user_id, expiry_str))
            conn.commit()
            user_subscriptions[user_id] = {'expiry': expiry}
            logger.info(f"Saved subscription for {user_id}, expiry {expiry_str}")
        except sqlite3.Error as e: logger.error(f"❌ SQLite error saving subscription for {user_id}: {e}")
        except Exception as e: logger.error(f"❌ Unexpected error saving subscription for {user_id}: {e}", exc_info=True)
        finally: conn.close()

def remove_subscription_db(user_id):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute('DELETE FROM subscriptions WHERE user_id = ?', (user_id,))
            conn.commit()
            if user_id in user_subscriptions: del user_subscriptions[user_id]
            logger.info(f"Removed subscription for {user_id} from DB")
        except sqlite3.Error as e: logger.error(f"❌ SQLite error removing subscription for {user_id}: {e}")
        except Exception as e: logger.error(f"❌ Unexpected error removing subscription for {user_id}: {e}", exc_info=True)
        finally: conn.close()

def add_admin_db(admin_id, added_by):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            added_date = datetime.now().isoformat()
            c.execute('INSERT OR IGNORE INTO admins (user_id, added_by, added_date) VALUES (?, ?, ?)', 
                      (admin_id, added_by, added_date))
            conn.commit()
            admin_ids.add(admin_id) 
            logger.info(f"Added admin {admin_id} to DB by {added_by}")
        except sqlite3.Error as e: logger.error(f"❌ SQLite error adding admin {admin_id}: {e}")
        except Exception as e: logger.error(f"❌ Unexpected error adding admin {admin_id}: {e}", exc_info=True)
        finally: conn.close()

def remove_admin_db(admin_id):
    if admin_id == OWNER_ID:
        logger.warning("Attempted to remove OWNER_ID from admins.")
        return False 
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        removed = False
        try:
            c.execute('SELECT 1 FROM admins WHERE user_id = ?', (admin_id,))
            if c.fetchone():
                c.execute('DELETE FROM admins WHERE user_id = ?', (admin_id,))
                conn.commit()
                removed = c.rowcount > 0 
                if removed: admin_ids.discard(admin_id); logger.info(f"Removed admin {admin_id} from DB")
                else: logger.warning(f"Admin {admin_id} found but delete affected 0 rows.")
            else:
                logger.warning(f"Admin {admin_id} not found in DB.")
                admin_ids.discard(admin_id)
            return removed
        except sqlite3.Error as e: logger.error(f"❌ SQLite error removing admin {admin_id}: {e}"); return False
        except Exception as e: logger.error(f"❌ Unexpected error removing admin {admin_id}: {e}", exc_info=True); return False
        finally: conn.close()

# --- Menu creation (Inline and ReplyKeyboards) ---
def create_main_menu_inline(user_id):
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        _sc_inline_button('📢 Updates Channel', url=f'https://t.me/{UPDATE_CHANNEL.replace("@", "")}'),
        _sc_inline_button('📤 Upload File', callback_data='upload', icon_custom_emoji_id='6237517438464826398'),
        _sc_inline_button('📂 Check Files', callback_data='check_files'),
        _sc_inline_button('⚡ Bot Speed', callback_data='speed', icon_custom_emoji_id='6199473713373517474'),
        _sc_inline_button('📦 Manual Install', callback_data='manual_install'),
        _sc_inline_button('📞 Contact Owner', url=f'https://t.me/{YOUR_USERNAME.replace("@", "")}')
    ]

    if user_id in admin_ids:
        admin_buttons = [
            _sc_inline_button('💳 Subscriptions', callback_data='subscription'), #0
            _sc_inline_button('📊 Statistics', callback_data='stats'), #1
            _sc_inline_button('🔒 Lock Bot' if not bot_locked else '🔓 Unlock Bot', #2
                                     callback_data='lock_bot' if not bot_locked else 'unlock_bot'),
            _sc_inline_button('📢 Broadcast', callback_data='broadcast'), #3
            _sc_inline_button('👑 Admin Panel', callback_data='admin_panel'), #4
            _sc_inline_button('🟢 Run All Scripts', callback_data='run_all_scripts'), #5
            _sc_inline_button('⛔ Stop All Scripts', callback_data='stop_all_scripts'), #5b
            _sc_inline_button('📢 Channel Add', callback_data='manage_mandatory_channels'), #6
            _sc_inline_button('👥 User Management', callback_data='user_management'), #7
            _sc_inline_button('🛠️ Admin Install', callback_data='admin_install'), #8
            _sc_inline_button('⚙️ Settings', callback_data='admin_settings') #9
        ]
        markup.add(buttons[0]) # Updates
        markup.add(buttons[1], buttons[2]) # Upload, Check Files
        markup.add(buttons[3], admin_buttons[0]) # Speed, Subscriptions
        markup.add(admin_buttons[1], admin_buttons[3]) # Stats, Broadcast
        markup.add(admin_buttons[2], admin_buttons[5]) # Lock Bot, Run All Scripts
        markup.add(admin_buttons[10]) # Stop All Scripts
        markup.add(admin_buttons[6], admin_buttons[8]) # Channel Management, Admin Install
        markup.add(admin_buttons[7], admin_buttons[9]) # User Management, Settings
        markup.add(admin_buttons[4]) # Admin Panel
        markup.add(buttons[5]) # Contact
    else:
        markup.add(buttons[0])
        markup.add(buttons[1], buttons[2])
        markup.add(buttons[3], buttons[4]) # Speed, Manual Install
        markup.add(_sc_inline_button('📊 Statistics', callback_data='stats')) # Allow non-admins to see stats too
        markup.add(buttons[5])
    return markup

def create_reply_keyboard_main_menu(user_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    layout_to_use = ADMIN_COMMAND_BUTTONS_LAYOUT_USER_SPEC if user_id in admin_ids else COMMAND_BUTTONS_LAYOUT_USER_SPEC
    for row_buttons_text in layout_to_use:
        markup.add(*[_sc_keyboard_button(text) for text in row_buttons_text])
    return markup

def create_control_buttons(script_owner_id, file_name, is_running=True):
    markup = types.InlineKeyboardMarkup(row_width=2)
    if is_running:
        markup.row(
            _sc_inline_button("🔴 Stop", callback_data=f'stop_{script_owner_id}_{file_name}'),
            _sc_inline_button("🔄 Restart", callback_data=f'restart_{script_owner_id}_{file_name}')
        )
        markup.row(
            _sc_inline_button("🗑️ Delete", callback_data=f'delete_{script_owner_id}_{file_name}'),
            _sc_inline_button("📜 Logs", callback_data=f'logs_{script_owner_id}_{file_name}')
        )
    else:
        markup.row(
            _sc_inline_button("🟢 Start", callback_data=f'start_{script_owner_id}_{file_name}'),
            _sc_inline_button("🗑️ Delete", callback_data=f'delete_{script_owner_id}_{file_name}')
        )
        markup.row(
            _sc_inline_button("📜 View Logs", callback_data=f'logs_{script_owner_id}_{file_name}')
        )
    markup.add(_sc_inline_button("🔙 Back to Files", callback_data='check_files'))
    return markup

def create_admin_panel():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.row(
        _sc_inline_button('➕ Add Admin', callback_data='add_admin'),
        _sc_inline_button('➖ Remove Admin', callback_data='remove_admin')
    )
    markup.row(_sc_inline_button('📋 List Admins', callback_data='list_admins'))
    markup.row(_sc_inline_button('🔙 Back to Main', callback_data='back_to_main'))
    return markup

def create_user_management_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.row(
        _sc_inline_button('🚫 Ban User', callback_data='ban_user'),
        _sc_inline_button('✅ Unban User', callback_data='unban_user')
    )
    markup.row(
        _sc_inline_button('📊 User Info', callback_data='user_info'),
        _sc_inline_button('👥 All Users', callback_data='all_users')
    )
    markup.row(
        _sc_inline_button('🔧 Set User Limit', callback_data='set_user_limit'),
        _sc_inline_button('🗑️ Remove User Limit', callback_data='remove_user_limit')
    )
    
    markup.row(
        _sc_inline_button('📂 Browse Users with Files', callback_data='browse_users_files')
    )
    markup.row(_sc_inline_button('🔙 Back to Main', callback_data='back_to_main'))
    return markup
    return markup

def create_subscription_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.row(
        _sc_inline_button('➕ Add Subscription', callback_data='add_subscription'),
        _sc_inline_button('➖ Remove Subscription', callback_data='remove_subscription')
    )
    markup.row(_sc_inline_button('🔍 Check Subscription', callback_data='check_subscription'))
    markup.row(_sc_inline_button('🔙 Back to Main', callback_data='back_to_main'))
    return markup

def create_admin_settings_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.row(
        _sc_inline_button('📊 System Info', callback_data='system_info'),
        _sc_inline_button('📈 Bot Performance', callback_data='bot_performance')
    )
    markup.row(
        _sc_inline_button('🧹 Cleanup Files', callback_data='cleanup_files'),
        _sc_inline_button('📋 Installation Logs', callback_data='install_logs')
    )
    markup.row(
        _sc_inline_button(
            '🟢 Maintenance ON' if maintenance_mode else '🔴 Maintenance OFF',
            callback_data='maintenance_mode'
        )
    )
    markup.row(
        _sc_inline_button(
            '🟢 Subscription Mode ON' if subscription_mode else '🔴 Subscription Mode OFF',
            callback_data='subscription_mode'
        )
    )
    markup.row(_sc_inline_button('🔙 Back to Main', callback_data='back_to_main'))
    return markup

# --- File Handling ---
def handle_zip_file(downloaded_file_content, file_name_zip, message):
    user_id = message.from_user.id
    user_folder = get_user_folder(user_id)
    temp_dir = None 
    try:
        temp_dir = tempfile.mkdtemp(prefix=f"user_{user_id}_zip_")
        logger.info(f"Temp dir for zip: {temp_dir}")
        zip_path = os.path.join(temp_dir, file_name_zip)
        with open(zip_path, 'wb') as new_file: new_file.write(downloaded_file_content)
        
        # Security check for ZIP
        is_safe, security_msg = scan_zip_security(zip_path)
        if not is_safe:
            # Send security warning to admin for approval
            security_warning_msg = f"🚨 File needs approval:\n👤 User: {user_id}\n📁 File: {file_name_zip}\n⚠️ Reason: {security_msg}"
            markup = types.InlineKeyboardMarkup()
            markup.row(
                _sc_inline_button("✅ Approve", callback_data=f"approve_zip_{user_id}_{file_name_zip}"),
                _sc_inline_button("❌ Reject", callback_data=f"reject_zip_{user_id}_{file_name_zip}")
            )
            for admin_id in admin_ids:
                try:
                    bot.send_message(admin_id, security_warning_msg, reply_markup=markup)
                except Exception as e:
                    logger.error(f"Failed to send security warning to admin {admin_id}: {e}")
            
            # Store the file content for later approval
            if user_id not in pending_zip_files:
                pending_zip_files[user_id] = {}
            pending_zip_files[user_id][file_name_zip] = downloaded_file_content
            
            bot.reply_to(message, f"⏳ File under security review.\n\nYou will be notified after file approval.")
            return

        # Process ZIP file if safe
        process_zip_file(zip_path, user_id, user_folder, file_name_zip, message, temp_dir)
        
    except zipfile.BadZipFile as e:
        logger.error(f"Bad zip file from {user_id}: {e}")
        bot.reply_to(message, f"❌ Error: Invalid/corrupted ZIP. {e}")
    except Exception as e:
        logger.error(f"❌ Error processing zip for {user_id}: {e}", exc_info=True)
        bot.reply_to(message, f"❌ Error processing zip: {str(e)}")
    finally:
        if temp_dir and os.path.exists(temp_dir):
            try: shutil.rmtree(temp_dir); logger.info(f"Cleaned temp dir: {temp_dir}")
            except Exception as e: logger.error(f"Failed to clean temp dir {temp_dir}: {e}", exc_info=True)

def process_zip_file(zip_path, user_id, user_folder, file_name_zip, message, temp_dir=None):
    """Process ZIP file extraction and setup"""
    cleanup_temp = False
    if temp_dir is None:
        temp_dir = tempfile.mkdtemp(prefix=f"user_{user_id}_zip_")
        cleanup_temp = True
        
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Check for safe paths
            for member in zip_ref.infolist():
                member_path = os.path.abspath(os.path.join(temp_dir, member.filename))
                if not member_path.startswith(os.path.abspath(temp_dir)):
                    raise zipfile.BadZipFile(f"Zip has unsafe path: {member.filename}")
            zip_ref.extractall(temp_dir)
            logger.info(f"Extracted zip to {temp_dir}")

        extracted_items = os.listdir(temp_dir)
        py_files = [f for f in extracted_items if f.endswith('.py')]
        js_files = [f for f in extracted_items if f.endswith('.js')]
        req_file = 'requirements.txt' if 'requirements.txt' in extracted_items else None
        pkg_json = 'package.json' if 'package.json' in extracted_items else None

        if req_file:
            req_path = os.path.join(temp_dir, req_file)
            logger.info(f"requirements.txt found, installing: {req_path}")
            bot.reply_to(message, f"🔄 Installing Python deps from `{req_file}`...")
            try:
                # Install ZIP requirements into the bot-local package directory.
                # This avoids Debian/Ubuntu PEP 668 externally-managed errors.
                local_req_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.python_packages')
                os.makedirs(local_req_dir, exist_ok=True)
                req_env = os.environ.copy()
                req_env['PIP_BREAK_SYSTEM_PACKAGES'] = '1'
                req_env['PYTHONPATH'] = os.pathsep.join([local_req_dir, req_env.get('PYTHONPATH', '')]).rstrip(os.pathsep)
                command = [sys.executable, '-m', 'pip', 'install', '--disable-pip-version-check', '--no-input', '--upgrade', '--break-system-packages', '--target', local_req_dir, '-r', req_path]
                result = subprocess.run(command, capture_output=True, text=True, check=True, encoding='utf-8', errors='ignore', env=req_env)
                logger.info(f"pip install from requirements.txt OK. Output:\n{result.stdout}")
                bot.reply_to(message, f"✅ Python deps from `{req_file}` installed.")
            except subprocess.CalledProcessError as e:
                error_msg = f"❌ Failed to install Python deps from `{req_file}`.\nLog:\n```\n{e.stderr or e.stdout}\n```"
                logger.error(error_msg)
                if len(error_msg) > 4000: error_msg = error_msg[:4000] + "\n... (Log truncated)"
                bot.reply_to(message, error_msg, parse_mode='Markdown'); return
            except Exception as e:
                 error_msg = f"❌ Unexpected error installing Python deps: {e}"
                 logger.error(error_msg, exc_info=True); bot.reply_to(message, error_msg); return

        if pkg_json:
            logger.info(f"package.json found, npm install in: {temp_dir}")
            bot.reply_to(message, f"🔄 Installing Node deps from `{pkg_json}`...")
            try:
                command = ['npm', 'install']
                result = subprocess.run(command, capture_output=True, text=True, check=True, cwd=temp_dir, encoding='utf-8', errors='ignore')
                logger.info(f"npm install OK. Output:\n{result.stdout}")
                bot.reply_to(message, f"✅ Node deps from `{pkg_json}` installed.")
            except FileNotFoundError:
                bot.reply_to(message, "❌ 'npm' not found. Cannot install Node deps."); return 
            except subprocess.CalledProcessError as e:
                error_msg = f"❌ Failed to install Node deps from `{pkg_json}`.\nLog:\n```\n{e.stderr or e.stdout}\n```"
                logger.error(error_msg)
                if len(error_msg) > 4000: error_msg = error_msg[:4000] + "\n... (Log truncated)"
                bot.reply_to(message, error_msg, parse_mode='Markdown'); return
            except Exception as e:
                 error_msg = f"❌ Unexpected error installing Node deps: {e}"
                 logger.error(error_msg, exc_info=True); bot.reply_to(message, error_msg); return

        main_script_name = None; file_type = None
        preferred_py = ['main.py', 'bot.py', 'app.py']; preferred_js = ['index.js', 'main.js', 'bot.js', 'app.js']
        for p in preferred_py:
            if p in py_files: main_script_name = p; file_type = 'py'; break
        if not main_script_name:
             for p in preferred_js:
                 if p in js_files: main_script_name = p; file_type = 'js'; break
        if not main_script_name:
            if py_files: main_script_name = py_files[0]; file_type = 'py'
            elif js_files: main_script_name = js_files[0]; file_type = 'js'
        if not main_script_name:
            bot.reply_to(message, "❌ No `.py` or `.js` script found in archive!"); return

        logger.info(f"Moving extracted files from {temp_dir} to {user_folder}")
        moved_count = 0
        for item_name in os.listdir(temp_dir):
            src_path = os.path.join(temp_dir, item_name)
            dest_path = os.path.join(user_folder, item_name)
            if os.path.isdir(dest_path): shutil.rmtree(dest_path)
            elif os.path.exists(dest_path): os.remove(dest_path)
            shutil.move(src_path, dest_path); moved_count +=1
        logger.info(f"Moved {moved_count} items to {user_folder}")

        save_user_file(user_id, main_script_name, file_type)
        logger.info(f"Saved main script '{main_script_name}' ({file_type}) for {user_id} from zip.")
        main_script_path = os.path.join(user_folder, main_script_name)
        bot.reply_to(message, f"✅ Files extracted. Starting main script: `{main_script_name}`...", parse_mode='Markdown')

        # Use user_id as script_owner_id for script key context
        if file_type == 'py':
             threading.Thread(target=run_script, args=(main_script_path, user_id, user_folder, main_script_name, message)).start()
        elif file_type == 'js':
             threading.Thread(target=run_js_script, args=(main_script_path, user_id, user_folder, main_script_name, message)).start()
             
    except Exception as e:
        logger.error(f"Error processing zip file: {e}", exc_info=True)
        bot.reply_to(message, f"❌ Error processing zip: {str(e)}")
    finally:
        if cleanup_temp and temp_dir and os.path.exists(temp_dir):
            try: shutil.rmtree(temp_dir); logger.info(f"Cleaned temp dir: {temp_dir}")
            except Exception as e: logger.error(f"Failed to clean temp dir {temp_dir}: {e}", exc_info=True)

def handle_js_file(file_path, script_owner_id, user_folder, file_name, message):
    try:
        save_user_file(script_owner_id, file_name, 'js')
        threading.Thread(target=run_js_script, args=(file_path, script_owner_id, user_folder, file_name, message)).start()
    except Exception as e:
        logger.error(f"❌ Error processing JS file {file_name} for {script_owner_id}: {e}", exc_info=True)
        bot.reply_to(message, f"❌ Error processing JS file: {str(e)}")

def handle_py_file(file_path, script_owner_id, user_folder, file_name, message):
    try:
        save_user_file(script_owner_id, file_name, 'py')
        threading.Thread(target=run_script, args=(file_path, script_owner_id, user_folder, file_name, message)).start()
    except Exception as e:
        logger.error(f"❌ Error processing Python file {file_name} for {script_owner_id}: {e}", exc_info=True)
        bot.reply_to(message, f"❌ Error processing Python file: {str(e)}")

# --- Automatic Package Installation & Script Running ---
def run_script(script_path, script_owner_id, user_folder, file_name, message_obj_for_reply, attempt=1):
    """Run Python script. script_owner_id is used for the script_key. message_obj_for_reply is for sending feedback."""
    max_attempts = 2 
    if attempt > max_attempts:
        bot.reply_to(message_obj_for_reply, f"❌ Failed to run '{file_name}' after {max_attempts} attempts. Check logs.")
        return

    script_key = f"{script_owner_id}_{file_name}"
    logger.info(f"Attempt {attempt} to run Python script: {script_path} (Key: {script_key}) for user {script_owner_id}")

    try:
        if not os.path.exists(script_path):
             bot.reply_to(message_obj_for_reply, f"❌ Error: Script '{file_name}' not found at '{script_path}'!")
             logger.error(f"Script not found: {script_path} for user {script_owner_id}")
             if script_owner_id in user_files:
                 user_files[script_owner_id] = [f for f in user_files.get(script_owner_id, []) if f[0] != file_name]
             remove_user_file_db(script_owner_id, file_name)
             return

        if attempt == 1:
            check_command = [sys.executable, script_path]
            logger.info(f"Running Python pre-check: {' '.join(check_command)}")
            check_proc = None
            try:
                check_env = os.environ.copy()
                local_pkg_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.python_packages')
                check_env['PIP_BREAK_SYSTEM_PACKAGES'] = '1'
                check_env['PYTHONPATH'] = os.pathsep.join([local_pkg_dir, check_env.get('PYTHONPATH', '')]).rstrip(os.pathsep)
                check_proc = subprocess.Popen(check_command, cwd=user_folder, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8', errors='ignore', env=check_env)
                stdout, stderr = check_proc.communicate(timeout=5)
                return_code = check_proc.returncode
                logger.info(f"Python Pre-check early. RC: {return_code}. Stderr: {stderr[:200]}...")
                if return_code != 0 and stderr:
                    match_py = re.search(r"ModuleNotFoundError: No module named '(.+?)'", stderr)
                    if match_py:
                        module_name = match_py.group(1).strip().strip("'\"")
                        logger.info(f"Detected missing Python module: {module_name}")
                        success, _ = attempt_install_pip(module_name, message_obj_for_reply)
                        if success:
                            logger.info(f"Install OK for {module_name}. Retrying run_script...")
                            bot.reply_to(message_obj_for_reply, f"🔄 Install successful. Retrying '{file_name}'...")
                            time.sleep(2)
                            threading.Thread(target=run_script, args=(script_path, script_owner_id, user_folder, file_name, message_obj_for_reply, attempt + 1)).start()
                            return
                        else:
                            bot.reply_to(message_obj_for_reply, f"❌ Install failed. Cannot run '{file_name}'.")
                            return
                    else:
                         error_summary = stderr[:500]
                         bot.reply_to(message_obj_for_reply, f"❌ Error in script pre-check for '{file_name}':\n```\n{error_summary}\n```\nFix the script.", parse_mode='Markdown')
                         return
            except subprocess.TimeoutExpired:
                logger.info("Python Pre-check timed out (>5s), imports likely OK. Killing check process.")
                if check_proc and check_proc.poll() is None: check_proc.kill(); check_proc.communicate()
                logger.info("Python Check process killed. Proceeding to long run.")
            except FileNotFoundError:
                 logger.error(f"Python interpreter not found: {sys.executable}")
                 bot.reply_to(message_obj_for_reply, f"❌ Error: Python interpreter '{sys.executable}' not found.")
                 return
            except Exception as e:
                 logger.error(f"Error in Python pre-check for {script_key}: {e}", exc_info=True)
                 bot.reply_to(message_obj_for_reply, f"❌ Unexpected error in script pre-check for '{file_name}': {e}")
                 return
            finally:
                 if check_proc and check_proc.poll() is None:
                     logger.warning(f"Python Check process {check_proc.pid} still running. Killing.")
                     check_proc.kill(); check_proc.communicate()

        logger.info(f"Starting long-running Python process for {script_key}")
        log_file_path = os.path.join(user_folder, f"{os.path.splitext(file_name)[0]}.log")
        log_file = None; process = None
        try: log_file = open(log_file_path, 'w', encoding='utf-8', errors='ignore', buffering=1)
        except Exception as e:
             logger.error(f"Failed to open log file '{log_file_path}' for {script_key}: {e}", exc_info=True)
             bot.reply_to(message_obj_for_reply, f"❌ Failed to open log file '{log_file_path}': {e}")
             return
        try:
            startupinfo = None; creationflags = 0
            if os.name == 'nt':
                 startupinfo = subprocess.STARTUPINFO(); startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                 startupinfo.wShowWindow = subprocess.SW_HIDE
            proc_env = os.environ.copy(); proc_env['PYTHONUNBUFFERED'] = '1'
            proc_env['PIP_BREAK_SYSTEM_PACKAGES'] = '1'
            local_pkg_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.python_packages')
            proc_env['PYTHONPATH'] = os.pathsep.join([local_pkg_dir, proc_env.get('PYTHONPATH', '')]).rstrip(os.pathsep)
            process = subprocess.Popen(
                [sys.executable, '-u', script_path], cwd=user_folder, stdout=log_file, stderr=log_file,
                stdin=subprocess.PIPE, startupinfo=startupinfo, creationflags=creationflags,
                encoding='utf-8', errors='ignore', env=proc_env
            )
            logger.info(f"Started Python process {process.pid} for {script_key}")
            bot_scripts[script_key] = {
                'process': process, 'log_file': log_file, 'file_name': file_name,
                'chat_id': message_obj_for_reply.chat.id, # Chat ID for potential future direct replies from script, defaults to admin/triggering user
                'script_owner_id': script_owner_id, # Actual owner of the script
                'start_time': datetime.now(), 'user_folder': user_folder, 'type': 'py', 'script_key': script_key
            }
            now_ist = datetime.now(IST).strftime("%d %b %Y • %I:%M:%S %p")
            bot.reply_to(message_obj_for_reply,
                "╔══════════════════════════╗\n"
                "║   🟢 SCRIPT STARTED 🟢   ║\n"
                "╚══════════════════════════╝\n\n"
                f"🐍 *File*    : `{file_name}`\n"
                f"🔢 *PID*     : `{process.pid}`\n"
                f"👤 *User*    : `{script_owner_id}`\n"
                f"🕐 *Started* : `{now_ist} IST`\n\n"
                "✅ *Python script is now running!*",
                parse_mode='Markdown')
            try:
                bot.edit_message_text(
                    "╔══════════════════════════╗\n"
                    "║   🎛️ FILE  CONTROL 🎛️    ║\n"
                    "╚══════════════════════════╝\n\n"
                    f"📄 *File*    : `{file_name}`\n"
                    f"🐍 *Type*    : `PY`\n"
                    f"👤 *Owner*   : `{script_owner_id}`\n"
                    f"📡 *Status*  : 🟢 Running\n"
                    f"🔢 *PID*     : `{process.pid}`\n"
                    f"🕐 *Updated* : `{now_ist} IST`\n\n"
                    "👇 *Select an action:*",
                    message_obj_for_reply.chat.id, message_obj_for_reply.message_id,
                    reply_markup=create_control_buttons(script_owner_id, file_name, True),
                    parse_mode='Markdown')
            except Exception: pass
        except FileNotFoundError:
             logger.error(f"Python interpreter {sys.executable} not found for long run {script_key}")
             bot.reply_to(message_obj_for_reply, f"❌ Error: Python interpreter '{sys.executable}' not found.")
             if log_file and not log_file.closed: log_file.close()
             if script_key in bot_scripts: del bot_scripts[script_key]
        except Exception as e:
            if log_file and not log_file.closed: log_file.close()
            error_msg = f"❌ Error starting Python script '{file_name}': {str(e)}"
            logger.error(error_msg, exc_info=True)
            bot.reply_to(message_obj_for_reply, error_msg)
            if process and process.poll() is None:
                 logger.warning(f"Killing potentially started Python process {process.pid} for {script_key}")
                 kill_process_tree({'process': process, 'log_file': log_file, 'script_key': script_key})
            if script_key in bot_scripts: del bot_scripts[script_key]
    except Exception as e:
        error_msg = f"❌ Unexpected error running Python script '{file_name}': {str(e)}"
        logger.error(error_msg, exc_info=True)
        bot.reply_to(message_obj_for_reply, error_msg)
        if script_key in bot_scripts:
             logger.warning(f"Cleaning up {script_key} due to error in run_script.")
             kill_process_tree(bot_scripts[script_key])
             del bot_scripts[script_key]

def run_js_script(script_path, script_owner_id, user_folder, file_name, message_obj_for_reply, attempt=1):
    """Run JS script. script_owner_id is used for the script_key. message_obj_for_reply is for sending feedback."""
    max_attempts = 2
    if attempt > max_attempts:
        bot.reply_to(message_obj_for_reply, f"❌ Failed to run '{file_name}' after {max_attempts} attempts. Check logs.")
        return

    script_key = f"{script_owner_id}_{file_name}"
    logger.info(f"Attempt {attempt} to run JS script: {script_path} (Key: {script_key}) for user {script_owner_id}")

    try:
        if not os.path.exists(script_path):
             bot.reply_to(message_obj_for_reply, f"❌ Error: Script '{file_name}' not found at '{script_path}'!")
             logger.error(f"JS Script not found: {script_path} for user {script_owner_id}")
             if script_owner_id in user_files:
                 user_files[script_owner_id] = [f for f in user_files.get(script_owner_id, []) if f[0] != file_name]
             remove_user_file_db(script_owner_id, file_name)
             return

        if attempt == 1:
            check_command = ['node', script_path]
            logger.info(f"Running JS pre-check: {' '.join(check_command)}")
            check_proc = None
            try:
                check_proc = subprocess.Popen(check_command, cwd=user_folder, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8', errors='ignore')
                stdout, stderr = check_proc.communicate(timeout=5)
                return_code = check_proc.returncode
                logger.info(f"JS Pre-check early. RC: {return_code}. Stderr: {stderr[:200]}...")
                if return_code != 0 and stderr:
                    match_js = re.search(r"Cannot find module '(.+?)'", stderr)
                    if match_js:
                        module_name = match_js.group(1).strip().strip("'\"")
                        if not module_name.startswith('.') and not module_name.startswith('/'):
                             logger.info(f"Detected missing Node module: {module_name}")
                             success, _ = attempt_install_npm(module_name, user_folder, message_obj_for_reply)
                             if success:
                                 logger.info(f"NPM Install OK for {module_name}. Retrying run_js_script...")
                                 bot.reply_to(message_obj_for_reply, f"🔄 NPM Install successful. Retrying '{file_name}'...")
                                 time.sleep(2)
                                 threading.Thread(target=run_js_script, args=(script_path, script_owner_id, user_folder, file_name, message_obj_for_reply, attempt + 1)).start()
                                 return
                             else:
                                 bot.reply_to(message_obj_for_reply, f"❌ NPM Install failed. Cannot run '{file_name}'.")
                                 return
                        else: logger.info(f"Skipping npm install for relative/core: {module_name}")
                    error_summary = stderr[:500]
                    bot.reply_to(message_obj_for_reply, f"❌ Error in JS script pre-check for '{file_name}':\n```\n{error_summary}\n```\nFix script or install manually.", parse_mode='Markdown')
                    return
            except subprocess.TimeoutExpired:
                logger.info("JS Pre-check timed out (>5s), imports likely OK. Killing check process.")
                if check_proc and check_proc.poll() is None: check_proc.kill(); check_proc.communicate()
                logger.info("JS Check process killed. Proceeding to long run.")
            except FileNotFoundError:
                 error_msg = "❌ Error: 'node' not found. Ensure Node.js is installed for JS files."
                 logger.error(error_msg)
                 bot.reply_to(message_obj_for_reply, error_msg)
                 return
            except Exception as e:
                 logger.error(f"Error in JS pre-check for {script_key}: {e}", exc_info=True)
                 bot.reply_to(message_obj_for_reply, f"❌ Unexpected error in JS pre-check for '{file_name}': {e}")
                 return
            finally:
                 if check_proc and check_proc.poll() is None:
                     logger.warning(f"JS Check process {check_proc.pid} still running. Killing.")
                     check_proc.kill(); check_proc.communicate()

        logger.info(f"Starting long-running JS process for {script_key}")
        log_file_path = os.path.join(user_folder, f"{os.path.splitext(file_name)[0]}.log")
        log_file = None; process = None
        try: log_file = open(log_file_path, 'w', encoding='utf-8', errors='ignore', buffering=1)
        except Exception as e:
            logger.error(f"Failed to open log file '{log_file_path}' for JS script {script_key}: {e}", exc_info=True)
            bot.reply_to(message_obj_for_reply, f"❌ Failed to open log file '{log_file_path}': {e}")
            return
        try:
            startupinfo = None; creationflags = 0
            if os.name == 'nt':
                 startupinfo = subprocess.STARTUPINFO(); startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                 startupinfo.wShowWindow = subprocess.SW_HIDE
            process = subprocess.Popen(
                ['node', '--max-old-space-size=256', script_path], cwd=user_folder, stdout=log_file, stderr=log_file,
                stdin=subprocess.PIPE, startupinfo=startupinfo, creationflags=creationflags,
                encoding='utf-8', errors='ignore'
            )
            logger.info(f"Started JS process {process.pid} for {script_key}")
            bot_scripts[script_key] = {
                'process': process, 'log_file': log_file, 'file_name': file_name,
                'chat_id': message_obj_for_reply.chat.id, # Chat ID for potential future direct replies
                'script_owner_id': script_owner_id, # Actual owner of the script
                'start_time': datetime.now(), 'user_folder': user_folder, 'type': 'js', 'script_key': script_key
            }
            now_ist = datetime.now(IST).strftime("%d %b %Y • %I:%M:%S %p")
            bot.reply_to(message_obj_for_reply,
                "╔══════════════════════════╗\n"
                "║   🟢 SCRIPT STARTED 🟢   ║\n"
                "╚══════════════════════════╝\n\n"
                f"🟨 *File*    : `{file_name}`\n"
                f"🔢 *PID*     : `{process.pid}`\n"
                f"👤 *User*    : `{script_owner_id}`\n"
                f"🕐 *Started* : `{now_ist} IST`\n\n"
                "✅ *JS script is now running!*",
                parse_mode='Markdown')
            try:
                bot.edit_message_text(
                    "╔══════════════════════════╗\n"
                    "║   🎛️ FILE  CONTROL 🎛️    ║\n"
                    "╚══════════════════════════╝\n\n"
                    f"📄 *File*    : `{file_name}`\n"
                    f"🟨 *Type*    : `JS`\n"
                    f"👤 *Owner*   : `{script_owner_id}`\n"
                    f"📡 *Status*  : 🟢 Running\n"
                    f"🔢 *PID*     : `{process.pid}`\n"
                    f"🕐 *Updated* : `{now_ist} IST`\n\n"
                    "👇 *Select an action:*",
                    message_obj_for_reply.chat.id, message_obj_for_reply.message_id,
                    reply_markup=create_control_buttons(script_owner_id, file_name, True),
                    parse_mode='Markdown')
            except Exception: pass
        except FileNotFoundError:
             error_msg = "❌ Error: 'node' not found for long run. Ensure Node.js is installed."
             logger.error(error_msg)
             if log_file and not log_file.closed: log_file.close()
             bot.reply_to(message_obj_for_reply, error_msg)
             if script_key in bot_scripts: del bot_scripts[script_key]
        except Exception as e:
            if log_file and not log_file.closed: log_file.close()
            error_msg = f"❌ Error starting JS script '{file_name}': {str(e)}"
            logger.error(error_msg, exc_info=True)
            bot.reply_to(message_obj_for_reply, error_msg)
            if process and process.poll() is None:
                 logger.warning(f"Killing potentially started JS process {process.pid} for {script_key}")
                 kill_process_tree({'process': process, 'log_file': log_file, 'script_key': script_key})
            if script_key in bot_scripts: del bot_scripts[script_key]
    except Exception as e:
        error_msg = f"❌ Unexpected error running JS script '{file_name}': {str(e)}"
        logger.error(error_msg, exc_info=True)
        bot.reply_to(message_obj_for_reply, error_msg)
        if script_key in bot_scripts:
             logger.warning(f"Cleaning up {script_key} due to error in run_js_script.")
             kill_process_tree(bot_scripts[script_key])
             del bot_scripts[script_key]

# --- Maintenance Mode ---
def _maintenance_blocked(user_id):
    """Return True when maintenance mode is active for a non-admin user."""
    return maintenance_mode and user_id not in admin_ids

def _send_maintenance_message(chat_id):
    bot.send_message(
        chat_id,
        "🛠️ Maintenance Mode\n\nThe bot is temporarily under maintenance. Please try again later.",
    )

# --- Logic Functions (called by commands and text handlers) ---
# --- Global paid-subscription gate ---
def _has_active_paid_subscription(user_id):
    """Return True when the user has a currently active paid subscription."""
    sub = user_subscriptions.get(user_id)
    if not sub:
        return False
    expiry = sub.get('expiry')
    if not expiry:
        return False
    if expiry <= datetime.now():
        # Clean up expired subscription so the user is treated as free.
        try:
            remove_subscription_db(user_id)
        except Exception:
            pass
        return False
    return True

def _subscription_control_allowed(user_id):
    """When Subscription Mode is ON, only admin/owner and active subscribers may use controls."""
    if user_id in admin_ids or not subscription_mode:
        return True
    return _has_active_paid_subscription(user_id)

def _send_purchase_required_message(target, is_callback=False):
    """Tell a free user that a paid subscription is required and provide the owner contact button."""
    text = (
        "╔══════════════════════════╗\n"
        "║   🔒 SUBSCRIPTION REQUIRED   ║\n"
        "╚══════════════════════════╝\n\n"
        "⚠️ Subscription Mode is currently ON.\n\n"
        "💳 Please purchase a subscription first.\n"
        "✅ After your subscription is activated, you can use the bot again.\n\n"
        "📞 For subscription purchase, contact the owner."
    )
    markup = types.InlineKeyboardMarkup()
    markup.add(_sc_inline_button('📞 Contact Owner', url=f'https://t.me/{YOUR_USERNAME.replace("@", "")}'))
    try:
        if is_callback:
            bot.send_message(target, text, reply_markup=markup)
        else:
            bot.reply_to(target, text, reply_markup=markup)
    except Exception as e:
        logger.error(f"Could not send subscription purchase message: {e}", exc_info=True)

def _enforce_subscription_for_message(message):
    """Return True and lock all message-based controls for free users while Subscription Mode is ON."""
    user_id = message.from_user.id
    if _subscription_control_allowed(user_id):
        return False
    _send_purchase_required_message(message)
    return True

def _enforce_subscription_for_callback(call):
    """Return True and lock every callback control for free users while Subscription Mode is ON."""
    user_id = call.from_user.id
    if _subscription_control_allowed(user_id):
        return False
    safe_answer_callback(call.id, "💳 Purchase a subscription first.", show_alert=True)
    _send_purchase_required_message(call.message.chat.id, is_callback=True)
    return True

def _logic_send_welcome(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    if _maintenance_blocked(user_id):
        _send_maintenance_message(chat_id)
        return
    user_name = message.from_user.first_name

    logger.info(f"Welcome request from user_id: {user_id}")

    # Check if user is banned
    if is_user_banned(user_id):
        bot.send_message(chat_id, "❌ You are banned from using this bot.")
        return

    # Check mandatory subscription FIRST - before anything else
    is_subscribed, not_joined = check_mandatory_subscription(user_id)
    if not is_subscribed and user_id not in admin_ids:
        subscription_message, markup = create_subscription_check_message(not_joined)
        bot.send_message(chat_id, subscription_message, reply_markup=markup, parse_mode='Markdown')
        return

    if bot_locked and user_id not in admin_ids:
        bot.send_message(chat_id, "╔══════════════════════════════╗\n║   🔒 ʙᴏᴛ ᴄᴏɴᴛʀᴏʟ ʟᴏᴄᴋᴇᴅ   ║\n╚══════════════════════════════╝\n\n⛔ ʟᴏᴄᴋᴇᴅ sᴛᴀᴛᴜs\n\n🔐 ᴀᴅᴍɪɴ ʟᴏᴄᴋ ᴀᴄᴛɪᴠᴇ\n⚠️ ᴜsᴇʀ ᴀᴄᴄᴇss ʀᴇsᴛʀɪᴄᴛᴇᴅ")
        return

    if user_id not in active_users:
        add_active_user(user_id)
        try:
            join_time = datetime.now(IST).strftime("%d %b %Y • %I:%M:%S %p")
            username_str = f"@{message.from_user.username}" if message.from_user.username else "No username"
            owner_notification = (
                "╔══════════════════════════╗\n"
                "║    🎉 NEW USER JOINED 🎉   ║\n"
                "╚══════════════════════════╝\n\n"
                f"👤 Name     : *{user_name}*\n"
                f"🔗 Username : {username_str}\n"
                f"🆔 ID       : `{user_id}`\n"
                f"🕐 Time     : `{join_time} IST`"
            )
            try:
                photos = bot.get_user_profile_photos(user_id, limit=1)
                if photos and photos.total_count > 0:
                    file_id = photos.photos[0][-1].file_id
                    bot.send_photo(OWNER_ID, file_id, caption=owner_notification, parse_mode='Markdown')
                else:
                    bot.send_message(OWNER_ID, owner_notification, parse_mode='Markdown')
            except Exception:
                bot.send_message(OWNER_ID, owner_notification, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"⚠️ Failed to notify owner about new user {user_id}: {e}")

    file_limit = get_user_file_limit(user_id)
    current_files = get_user_file_count(user_id)
    limit_str = str(file_limit) if file_limit != float('inf') else "∞ Unlimited"
    expiry_info = ""

    if user_id == OWNER_ID:
        user_status = "👑 Owner"
        status_bar = "🟡🟡🟡🟡🟡"
    elif user_id in admin_ids:
        user_status = "🛡️ Admin"
        status_bar = "🔵🔵🔵🔵⬜"
    elif user_id in user_subscriptions:
        expiry_date = user_subscriptions[user_id].get('expiry')
        if expiry_date and expiry_date > datetime.now():
            user_status = "⭐ Premium"
            status_bar = "🟣🟣🟣⬜⬜"
            days_left = (expiry_date - datetime.now()).days
            expiry_info = f"\n  └ ⏳ Expires in: `{days_left} days`"
        else:
            user_status = "🆓 Free (Expired)"
            status_bar = "🟢⬜⬜⬜⬜"
            remove_subscription_db(user_id)
    else:
        user_status = "🆓 Free User"
        status_bar = "🟢⬜⬜⬜⬜"

    now_ist = datetime.now(IST).strftime("%d %b %Y • %I:%M:%S %p")
    welcome_msg_text = (
        "╔══════════════════════════╗\n"
        f"║  👋 WELCOME,  {user_name[:10]:<10}  ║\n"
        "╚══════════════════════════╝\n\n"
        "👤 *YOUR PROFILE*\n"
        f"├ 🆔 ID      : `{user_id}`\n"
        f"├ 🔰 Status  : {user_status}\n"
        f"├ 📊 Level   : {status_bar}{expiry_info}\n"
        f"└ 📁 Files   : `{current_files} / {limit_str}`\n\n"
        "🤖 *WHAT YOU CAN DO*\n"
        "├ 🐍 Host Python `.py` scripts\n"
        "├ 🟨 Host JS `.js` scripts\n"
        "├ 📦 Upload `.zip` archives\n"
        "└ 🔧 Manual module install\n\n"
        f"🕐 `{now_ist} IST`\n\n"
        "👇 *Use the buttons below to get started!*"
    )
    
    main_reply_markup = create_reply_keyboard_main_menu(user_id)
    try:
        photos = bot.get_user_profile_photos(user_id, limit=1)
        if photos and photos.total_count > 0:
            file_id = photos.photos[0][-1].file_id
            bot.send_photo(chat_id, file_id, caption=welcome_msg_text, reply_markup=main_reply_markup, parse_mode='Markdown')
        else:
            bot.send_message(chat_id, welcome_msg_text, reply_markup=main_reply_markup, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error sending welcome to {user_id}: {e}", exc_info=True)
        try:
            bot.send_message(chat_id, welcome_msg_text, reply_markup=main_reply_markup, parse_mode='Markdown')
        except Exception: pass

def _logic_updates_channel(message):
    if _enforce_subscription_for_message(message):
        return

    user_id = message.from_user.id
    if _maintenance_blocked(user_id):
        _send_maintenance_message(message.chat.id)
        return

    markup = types.InlineKeyboardMarkup()
    markup.add(_sc_inline_button('🌟 Join Updates Channel 🌟', url=f'https://t.me/{UPDATE_CHANNEL.replace("@", "")}'))
    bot.reply_to(message,
        "╔══════════════════════════╗\n"
        "║   📢 UPDATES CHANNEL 📢  ║\n"
        "╚══════════════════════════╝\n\n"
        "🔔 Stay updated with the latest:\n"
        "├ 🚀 New features\n"
        "├ 🐛 Bug fixes\n"
        "└ 📣 Announcements\n\n"
        "👇 *Click below to join!*",
        reply_markup=markup, parse_mode='Markdown')

def _logic_upload_file(message):
    if _enforce_subscription_for_message(message):
        return

    user_id = message.from_user.id
    if _maintenance_blocked(user_id):
        _send_maintenance_message(message.chat.id)
        return
    
    # Check if user is banned
    if is_user_banned(user_id):
        bot.reply_to(message, "❌ You are banned from using this bot.")
        return
    
    # Check mandatory subscription first
    is_subscribed, not_joined = check_mandatory_subscription(user_id)
    if not is_subscribed and user_id not in admin_ids:
        subscription_message, markup = create_subscription_check_message(not_joined)
        bot.reply_to(message, subscription_message, reply_markup=markup, parse_mode='Markdown')
        return
        
    if bot_locked and user_id not in admin_ids:
        bot.reply_to(message, "╔══════════════════════════════╗\n║   🔒 ʙᴏᴛ ᴄᴏɴᴛʀᴏʟ ʟᴏᴄᴋᴇᴅ   ║\n╚══════════════════════════════╝\n\n⛔ ʟᴏᴄᴋᴇᴅ sᴛᴀᴛᴜs\n\n🔐 ᴀᴅᴍɪɴ ʟᴏᴄᴋ ᴀᴄᴛɪᴠᴇ\n⚠️ ᴜsᴇʀ ᴀᴄᴄᴇss ʀᴇsᴛʀɪᴄᴛᴇᴅ")
        return

    file_limit = get_user_file_limit(user_id)
    current_files = get_user_file_count(user_id)
    limit_str = str(file_limit) if file_limit != float('inf') else "∞ Unlimited"
    if current_files >= file_limit:
        bot.reply_to(message, f"⚠️ File limit reached (`{current_files}/{limit_str}`). Delete a file first.")
        return
    bot.reply_to(message,
        "╔══════════════════════════╗\n"
        "║     🚀 UPLOAD FILE 🚀    ║\n"
        "╚══════════════════════════╝\n\n"
        "📎 Send your file now:\n"
        "├ 🐍 Python script → `.py`\n"
        "├ 🟨 JavaScript   → `.js`\n"
        "└ 📦 Archive      → `.zip`\n\n"
        f"📁 Slots used: `{current_files} / {limit_str}`\n\n"
        "⬆️ *Just send the file directly!*",
        parse_mode='Markdown')

def _logic_check_files(message):
    if _enforce_subscription_for_message(message):
        return

    user_id = message.from_user.id
    if _maintenance_blocked(user_id):
        _send_maintenance_message(message.chat.id)
        return

    user_id = message.from_user.id
    
    # Check if user is banned
    if is_user_banned(user_id):
        bot.reply_to(message, "❌ You are banned from using this bot.")
        return
    
    # Check mandatory subscription first
    is_subscribed, not_joined = check_mandatory_subscription(user_id)
    if not is_subscribed and user_id not in admin_ids:
        subscription_message, markup = create_subscription_check_message(not_joined)
        bot.reply_to(message, subscription_message, reply_markup=markup, parse_mode='Markdown')
        return
        
    user_files_list = user_files.get(user_id, [])
    if not user_files_list:
        bot.reply_to(message,
            "╔══════════════════════════╗\n"
            "║     🗂️ YOUR FILES 🗂️     ║\n"
            "╚══════════════════════════╝\n\n"
            "📭 *No files uploaded yet!*\n\n"
            "Use 🚀 *Upload File* to get started.",
            parse_mode='Markdown')
        return
    markup = types.InlineKeyboardMarkup(row_width=1)
    for file_name, file_type in sorted(user_files_list):
        is_running = is_bot_running(user_id, file_name)
        status_icon = "🟢" if is_running else "🔴"
        btn_text = f"{status_icon} {file_name} ({file_type})"
        markup.add(_sc_inline_button(btn_text, callback_data=f'file_{user_id}_{file_name}'))
    file_count = len(user_files_list)
    running_count = sum(1 for fn, ft in user_files_list if is_bot_running(user_id, fn))
    bot.reply_to(message,
        "╔══════════════════════════╗\n"
        "║     🗂️ YOUR FILES 🗂️     ║\n"
        "╚══════════════════════════╝\n\n"
        f"📁 Total Files : `{file_count}`\n"
        f"🟢 Running     : `{running_count}`\n"
        f"🔴 Stopped     : `{file_count - running_count}`\n\n"
        "👇 *Tap a file to manage it:*",
        reply_markup=markup, parse_mode='Markdown')

def _logic_bot_speed(message):
    if _enforce_subscription_for_message(message):
        return

    user_id = message.from_user.id
    if _maintenance_blocked(user_id):
        _send_maintenance_message(message.chat.id)
        return

    user_id = message.from_user.id
    chat_id = message.chat.id
    
    # Check if user is banned
    if is_user_banned(user_id):
        bot.reply_to(message, "❌ You are banned from using this bot.")
        return
    
    # Check mandatory subscription first
    is_subscribed, not_joined = check_mandatory_subscription(user_id)
    if not is_subscribed and user_id not in admin_ids:
        subscription_message, markup = create_subscription_check_message(not_joined)
        bot.reply_to(message, subscription_message, reply_markup=markup, parse_mode='Markdown')
        return
        
    start_time_ping = time.time()
    wait_msg = bot.reply_to(message, "🏃 Testing speed...")
    response_time = round((time.time() - start_time_ping) * 1000, 2)
    try:
        if response_time < 300: s_icon, s_label = "🟢", "Excellent"
        elif response_time < 600: s_icon, s_label = "🟡", "Good"
        elif response_time < 1000: s_icon, s_label = "🟠", "Average"
        else: s_icon, s_label = "🔴", "Slow"
        bar_len = 10
        filled = min(bar_len, max(1, int((1 - response_time / 1500) * bar_len)))
        ping_bar = "▰" * filled + "▱" * (bar_len - filled)
        status = "🔓 Unlocked" if not bot_locked else "🔒 Locked"
        if user_id == OWNER_ID: user_level = "👑 Owner"
        elif user_id in admin_ids: user_level = "🛡️ Admin"
        elif user_id in user_subscriptions and user_subscriptions[user_id].get('expiry', datetime.min) > datetime.now(): user_level = "⭐ Premium"
        else: user_level = "🆓 Free User"
        now_ist = datetime.now(IST).strftime("%d %b %Y • %I:%M:%S %p")
        speed_msg = (
            "╔══════════════════════════╗\n"
            "║   ⚡ BOT SPEED TEST ⚡   ║\n"
            "╚══════════════════════════╝\n\n"
            f"  {s_icon} *{s_label}*\n\n"
            f"  📡 Latency : `{response_time} ms`\n"
            f"  📶 Signal  : `{ping_bar}`\n"
            f"  🚦 Status  : {status}\n"
            f"  👤 Level   : {user_level}\n"
            f"  🕐 Time    : `{now_ist} IST`"
        )
        bot.edit_message_text(speed_msg, chat_id, wait_msg.message_id, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error during speed test (cmd): {e}", exc_info=True)
        bot.edit_message_text("❌ Error during speed test.", chat_id, wait_msg.message_id)

def _logic_contact_owner(message):
    if _enforce_subscription_for_message(message):
        return

    user_id = message.from_user.id
    if _maintenance_blocked(user_id):
        _send_maintenance_message(message.chat.id)
        return

    markup = types.InlineKeyboardMarkup()
    markup.add(_sc_inline_button('💬 Chat with Owner', url=f'https://t.me/{YOUR_USERNAME.replace("@", "")}'))
    bot.reply_to(message,
        "╔══════════════════════════╗\n"
        "║   💬 CONTACT OWNER 💬   ║\n"
        "╚══════════════════════════╝\n\n"
        "🙋 Need help? Reach out for:\n"
        "├ ⭐ Premium subscription\n"
        "├ 🐛 Bug reports\n"
        "├ 💡 Feature requests\n"
        "└ ❓ General support\n\n"
        "👇 *Tap below to message the owner!*",
        reply_markup=markup, parse_mode='Markdown')

def _logic_manual_install(message):
    if _enforce_subscription_for_message(message):
        return

    if _maintenance_blocked(message.from_user.id):
        _send_maintenance_message(message.chat.id)
        return

    """Handle manual installation request from user"""
    manual_install_module_init(message)

def _logic_help(message):
    if _enforce_subscription_for_message(message):
        return

    if _maintenance_blocked(message.from_user.id):
        _send_maintenance_message(message.chat.id)
        return

    help_text = (
        "╔══════════════════════════╗\n"
        "║     🆘 ʜᴇʟᴘ  ɢᴜɪᴅᴇ 🆘    ║\n"
        "╚══════════════════════════╝\n\n"
        "📌 ʙᴀsɪᴄ ᴄᴏᴍᴍᴀɴᴅs\n"
        "├ /sᴛᴀʀᴛ   — ʟᴀᴜɴᴄʜ ᴛʜᴇ ʙᴏᴛ\n"
        "├ /ʜᴇʟᴘ    — sʜᴏᴡ ᴛʜɪs ɢᴜɪᴅᴇ\n"
        "├ /ᴜᴘᴛɪᴍᴇ  — ʙᴏᴛ ᴜᴘᴛɪᴍᴇ & sʏsᴛᴇᴍ\n"
        "├ /ᴘɪɴɢ    — ᴄʜᴇᴄᴋ ʟᴀᴛᴇɴᴄʏ\n"
        "└ /sᴛᴀᴛᴜs  — ʙᴏᴛ sᴛᴀᴛɪsᴛɪᴄs\n\n"
        "📁 ꜰɪʟᴇ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ\n"
        "├ 🐍 ᴜᴘʟᴏᴀᴅ .py sᴄʀɪᴘᴛs\n"
        "├ 🟨 ᴜᴘʟᴏᴀᴅ .js sᴄʀɪᴘᴛs\n"
        "├ 📦 ᴜᴘʟᴏᴀᴅ .zip ᴀʀᴄʜɪᴠᴇs\n"
        "└ 🔄 ᴀᴜᴛᴏ-ɪɴsᴛᴀʟʟs ᴅᴇᴘᴇɴᴅᴇɴᴄɪᴇs\n\n"
        "🔧 ᴍᴏᴅᴜʟᴇ ɪɴsᴛᴀʟʟ\n"
        "├ ᴀᴜᴛᴏ-ᴅᴇᴛᴇᴄᴛs ᴍɪssɪɴɢ ᴍᴏᴅᴜʟᴇs\n"
        "└ ᴍᴀɴᴜᴀʟ ɪɴsᴛᴀʟʟ ᴠɪᴀ ʙᴜᴛᴛᴏɴ\n\n"
        "👑 ᴀᴅᴍɪɴ ꜰᴇᴀᴛᴜʀᴇs\n"
        "├ 🚫 ʙᴀɴ / ᴜɴʙᴀɴ ᴜsᴇʀs\n"
        "├ 📊 sᴇᴛ ꜰɪʟᴇ ʟɪᴍɪᴛs\n"
        "├ 📢 ʙʀᴏᴀᴅᴄᴀsᴛ ᴍᴇssᴀɢᴇs\n"
        "└ 🟢 ʀᴜɴ ᴀʟʟ ᴜsᴇʀ sᴄʀɪᴘᴛs\n\n"
        "💡 ᴛɪᴘs\n"
        "├ ᴊᴏɪɴ ᴀʟʟ ʀᴇǫᴜɪʀᴇᴅ ᴄʜᴀɴɴᴇʟs\n"
        "└ ᴄᴏɴᴛᴀᴄᴛ ᴏᴡɴᴇʀ ꜰᴏʀ ᴘʀᴇᴍɪᴜᴍ\n\n"
        "🛠 sᴜᴘᴘᴏʀᴛ: ᴄᴏɴᴛᴀᴄᴛ ᴏᴡɴᴇʀ"
    )
    help_markup = types.InlineKeyboardMarkup()
    help_markup.add(_sc_inline_button(
        '📞 Contact Owner',
        url=f'https://t.me/{YOUR_USERNAME.replace("@", "")}'
    ))
    bot.reply_to(message, help_text, reply_markup=help_markup)

# --- Admin Logic Functions ---
def _logic_subscriptions_panel(message):
    if _enforce_subscription_for_message(message):
        return

    if _maintenance_blocked(message.from_user.id):
        _send_maintenance_message(message.chat.id)
        return

    if message.from_user.id not in admin_ids:
        bot.reply_to(message, "⚠️ Admin permissions required.")
        return
    bot.reply_to(message,
        "╔══════════════════════════╗\n"
        "║  💳 SUBSCRIPTIONS 💳    ║\n"
        "╚══════════════════════════╝\n\n"
        f"👥 Total Subscribers : `{len(user_subscriptions)}`\n\n"
        "👇 *Select an action below:*",
        reply_markup=create_subscription_menu(), parse_mode='Markdown')

def _logic_statistics(message):
    if _enforce_subscription_for_message(message):
        return

    if _maintenance_blocked(message.from_user.id):
        _send_maintenance_message(message.chat.id)
        return

    user_id = message.from_user.id
    
    # Check if user is banned
    if is_user_banned(user_id):
        bot.reply_to(message, "❌ You are banned from using this bot.")
        return
    
    # Check mandatory subscription first
    is_subscribed, not_joined = check_mandatory_subscription(user_id)
    if not is_subscribed and user_id not in admin_ids:
        subscription_message, markup = create_subscription_check_message(not_joined)
        bot.reply_to(message, subscription_message, reply_markup=markup, parse_mode='Markdown')
        return
        
    total_users = len(active_users)
    total_files_records = sum(len(files) for files in user_files.values())

    running_bots_count = 0
    user_running_bots = 0

    for script_key_iter, script_info_iter in list(bot_scripts.items()):
        s_owner_id, _ = script_key_iter.split('_', 1) # Extract owner_id from key
        if is_bot_running(int(s_owner_id), script_info_iter['file_name']):
            running_bots_count += 1
            if int(s_owner_id) == user_id:
                user_running_bots +=1

    now_ist = datetime.now(IST).strftime("%d %b %Y • %I:%M:%S %p")
    stats_msg = (
        "╔══════════════════════════╗\n"
        "║   📊 BOT STATISTICS 📊   ║\n"
        "╚══════════════════════════╝\n\n"
        "👥 *USERS*\n"
        f"├ 🟢 Total Users   : `{total_users}`\n"
        f"├ 🚫 Banned        : `{len(banned_users)}`\n"
        f"└ ⭐ Subscribers   : `{len(user_subscriptions)}`\n\n"
        "🤖 *SCRIPTS*\n"
        f"├ 📂 Total Files   : `{total_files_records}`\n"
        f"├ 🟢 Running Bots  : `{running_bots_count}`\n"
        f"└ 🤖 Your Running  : `{user_running_bots}`\n"
    )
    if user_id in admin_ids:
        stats_msg += (
            "\n🛡️ *ADMIN INFO*\n"
            f"├ 🔒 Bot Status    : {'🔴 Locked' if bot_locked else '🟢 Unlocked'}\n"
            f"├ 📢 Channels      : `{len(mandatory_channels)}`\n"
            f"└ ⚙️ Custom Limits : `{len(user_limits)}`\n"
        )
    stats_msg += f"\n🕐 `{now_ist} IST`"
    bot.reply_to(message, stats_msg, parse_mode='Markdown')

def _logic_broadcast_init(message):
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, "⚠️ Admin permissions required.")
        return
    msg = bot.reply_to(message,
        "╔══════════════════════════╗\n"
        "║    📡 BROADCAST 📡      ║\n"
        "╚══════════════════════════╝\n\n"
        f"👥 Will send to `{len(active_users)}` users\n\n"
        "✍️ *Type your message now:*\n"
        "Send /cancel to abort.",
        parse_mode='Markdown')
    bot.register_next_step_handler(msg, process_broadcast_message)

def _logic_unlock_bot(message):
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, "⚠️ Admin permissions required.")
        return
    global bot_locked
    bot_locked = False
    bot.reply_to(message,
        "╔══════════════════════════════╗\n"
        "║  🔓 ʙᴏᴛ ᴄᴏɴᴛʀᴏʟ ᴜɴʟᴏᴄᴋᴇᴅ  ║\n"
        "╚══════════════════════════════╝\n\n"
        "        ✅ ᴜɴʟᴏᴄᴋᴇᴅ sᴛᴀᴛᴜs\n\n"
        "   🟢 ᴀᴅᴍɪɴ ʟᴏᴄᴋ ʀᴇᴍᴏᴠᴇᴅ\n"
        "   🚀 ᴜsᴇʀ ᴀᴄᴄᴇss ʀᴇsᴛᴏʀᴇᴅ")

def _logic_lock_bot(message):
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, "⚠️ Admin permissions required.")
        return
    global bot_locked
    bot_locked = True
    status = "locked" if bot_locked else "unlocked"
    logger.warning(f"Bot {status} by Admin {message.from_user.id} via command/button.")
    bot.reply_to(message, (
        "╔══════════════════════════════╗\n"
        + ("║   🔒 ʙᴏᴛ ᴄᴏɴᴛʀᴏʟ ʟᴏᴄᴋᴇᴅ   ║\n"
           "╚══════════════════════════════╝\n\n"
           "⛔ ʟᴏᴄᴋᴇᴅ sᴛᴀᴛᴜs\n\n"
           "🔐 ᴀᴅᴍɪɴ ʟᴏᴄᴋ ᴀᴄᴛɪᴠᴇ\n"
           "⚠️ ᴜsᴇʀ ᴀᴄᴄᴇss ʀᴇsᴛʀɪᴄᴛᴇᴅ"
           if bot_locked else
           "║  🔓 ʙᴏᴛ ᴄᴏɴᴛʀᴏʟ ᴜɴʟᴏᴄᴋᴇᴅ  ║\n"
           "╚══════════════════════════════╝\n\n"
           "✅ ᴜɴʟᴏᴄᴋᴇᴅ sᴛᴀᴛᴜs\n\n"
           "🟢 ᴀᴅᴍɪɴ ʟᴏᴄᴋ ʀᴇᴍᴏᴠᴇᴅ\n"
           "🚀 ᴜsᴇʀ ᴀᴄᴄᴇss ʀᴇsᴛᴏʀᴇᴅ")
    ))

def _broadcast_maintenance_status(status, changed_by=None):
    """Notify all registered active users except the admin/owner who changed the mode."""
    users = [uid for uid in active_users if uid != changed_by]
    message_text = (
        "🛠️ Maintenance Mode ON\n\n"
        "The bot is temporarily under maintenance. Please try again later."
        if status == "ON" else
        "✅ Maintenance Mode OFF\n\n"
        "Maintenance is complete. The bot is now available again."
    )

    def _send_all():
        sent = 0
        failed = 0
        for uid in users:
            try:
                bot.send_message(uid, message_text)
                sent += 1
                time.sleep(0.05)
            except Exception as exc:
                failed += 1
                logger.warning(f"Maintenance broadcast failed for user {uid}: {exc}")
        logger.info(f"Maintenance {status} broadcast complete: sent={sent}, failed={failed}, total={len(users)}")

    threading.Thread(target=_send_all, daemon=True, name="maintenance-broadcast").start()


def _logic_toggle_maintenance_mode(message):
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, "⚠️ Admin permissions required.")
        return
    global maintenance_mode
    maintenance_mode = not maintenance_mode
    status = "ON" if maintenance_mode else "OFF"
    logger.warning(f"Maintenance mode {status} by Admin {message.from_user.id}")
    bot.reply_to(message, f"🛠️ Maintenance Mode: {status}")
    _broadcast_maintenance_status(status, message.from_user.id)

def _logic_admin_panel(message):
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, "⚠️ Admin permissions required.")
        return
    bot.reply_to(message, "👑 Admin Panel\nManage admins. Use inline buttons from /start or admin menu.",
                 reply_markup=create_admin_panel())

def _logic_user_management(message):
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, "⚠️ Admin permissions required.")
        return
    total = len(user_files)
    banned = len(banned_users)
    bot.reply_to(message,
        "╔══════════════════════════╗\n"
        "║  👥 USER MANAGEMENT 👥  ║\n"
        "╚══════════════════════════╝\n\n"
        f"├ 👤 Total Users  : `{total}`\n"
        f"├ 🚫 Banned       : `{banned}`\n"
        f"└ ⭐ Subscribers  : `{len(user_subscriptions)}`\n\n"
        "👇 *Select an action:*",
        reply_markup=create_user_management_menu(), parse_mode='Markdown')

def _logic_admin_settings(message):
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, "⚠️ Admin permissions required.")
        return
    now_ist = datetime.now(IST).strftime("%d %b %Y • %I:%M:%S %p")
    bot.reply_to(message,
        "╔══════════════════════════╗\n"
        "║    ⚙️ ADMIN SETTINGS ⚙️   ║\n"
        "╚══════════════════════════╝\n\n"
        f"├ 🔒 Bot Status   : {'🔴 Locked' if bot_locked else '🟢 Unlocked'}\n"
        f"├ 🛠️ Maintenance : {'🟢 ON' if maintenance_mode else '🔴 OFF'}\n"
        f"├ 📢 Channels     : `{len(mandatory_channels)}`\n"
        f"├ 🛡️ Admins       : `{len(admin_ids)}`\n"
        f"└ 🕐 Time         : `{now_ist} IST`\n\n"
        "👇 *Select an action:*",
        reply_markup=create_admin_settings_menu(), parse_mode='Markdown')

def _logic_stop_all_scripts(message_or_call):
    """Stop every script currently started by this bot instance. Admin/owner only."""
    if isinstance(message_or_call, telebot.types.Message):
        admin_user_id = message_or_call.from_user.id
        reply_func = lambda text, **kwargs: bot.reply_to(message_or_call, text, **kwargs)
    elif isinstance(message_or_call, telebot.types.CallbackQuery):
        admin_user_id = message_or_call.from_user.id
        safe_answer_callback(message_or_call.id)
        reply_func = lambda text, **kwargs: bot.send_message(message_or_call.message.chat.id, text, **kwargs)
    else:
        logger.error("Invalid argument for _logic_stop_all_scripts")
        return

    if admin_user_id not in admin_ids:
        reply_func("⚠️ Admin permissions required.")
        return

    stopped = 0
    failed = 0
    snapshot = list(bot_scripts.items())
    for script_key, process_info in snapshot:
        try:
            if process_info and process_info.get('process') is not None:
                if is_bot_running(process_info.get('script_owner_id'), process_info.get('file_name')):
                    kill_process_tree(process_info)
                stopped += 1
            bot_scripts.pop(script_key, None)
        except Exception as exc:
            failed += 1
            logger.error(f"Error stopping {script_key}: {exc}", exc_info=True)

    if stopped == 0 and failed == 0:
        reply_func("ℹ️ No scripts are currently running.")
    elif failed:
        reply_func(f"⛔ Stop All Scripts completed. Stopped: {stopped} | Failed: {failed}")
    else:
        reply_func(f"⛔ Stop All Scripts completed. Stopped: {stopped} script(s).")


def _logic_run_all_scripts(message_or_call):
    if isinstance(message_or_call, telebot.types.Message):
        admin_user_id = message_or_call.from_user.id
        admin_chat_id = message_or_call.chat.id
        reply_func = lambda text, **kwargs: bot.reply_to(message_or_call, text, **kwargs)
        admin_message_obj_for_script_runner = message_or_call
    elif isinstance(message_or_call, telebot.types.CallbackQuery):
        admin_user_id = message_or_call.from_user.id
        admin_chat_id = message_or_call.message.chat.id
        safe_answer_callback(message_or_call.id)
        reply_func = lambda text, **kwargs: bot.send_message(admin_chat_id, text, **kwargs)
        admin_message_obj_for_script_runner = message_or_call.message 
    else:
        logger.error("Invalid argument for _logic_run_all_scripts")
        return

    if admin_user_id not in admin_ids:
        reply_func("⚠️ Admin permissions required.")
        return

    reply_func("⏳ Starting process to run all user scripts. This may take a while...")
    logger.info(f"Admin {admin_user_id} initiated 'run all scripts' from chat {admin_chat_id}.")

    started_count = 0; attempted_users = 0; skipped_files = 0; error_files_details = []

    # Use a copy of user_files keys and values to avoid modification issues during iteration
    all_user_files_snapshot = dict(user_files)

    for target_user_id, files_for_user in all_user_files_snapshot.items():
        if not files_for_user: continue
        attempted_users += 1
        logger.info(f"Processing scripts for user {target_user_id}...")
        user_folder = get_user_folder(target_user_id)

        for file_name, file_type in files_for_user:
            # script_owner_id for key context is target_user_id
            if not is_bot_running(target_user_id, file_name):
                file_path = os.path.join(user_folder, file_name)
                if os.path.exists(file_path):
                    logger.info(f"Admin {admin_user_id} attempting to start '{file_name}' ({file_type}) for user {target_user_id}.")
                    try:
                        if file_type == 'py':
                            threading.Thread(target=run_script, args=(file_path, target_user_id, user_folder, file_name, admin_message_obj_for_script_runner)).start()
                            started_count += 1
                        elif file_type == 'js':
                            threading.Thread(target=run_js_script, args=(file_path, target_user_id, user_folder, file_name, admin_message_obj_for_script_runner)).start()
                            started_count += 1
                        else:
                            logger.warning(f"Unknown file type '{file_type}' for {file_name} (user {target_user_id}). Skipping.")
                            error_files_details.append(f"`{file_name}` (User {target_user_id}) - Unknown type")
                            skipped_files += 1
                        time.sleep(0.7) # Increased delay slightly
                    except Exception as e:
                        logger.error(f"Error queueing start for '{file_name}' (user {target_user_id}): {e}")
                        error_files_details.append(f"`{file_name}` (User {target_user_id}) - Start error")
                        skipped_files += 1
                else:
                    logger.warning(f"File '{file_name}' for user {target_user_id} not found at '{file_path}'. Skipping.")
                    error_files_details.append(f"`{file_name}` (User {target_user_id}) - File not found")
                    skipped_files += 1
            # else: logger.info(f"Script '{file_name}' for user {target_user_id} already running.")

    summary_msg = (f"✅ All Users' Scripts - Processing Complete:\n\n"
                   f"▶️ Attempted to start: {started_count} scripts.\n"
                   f"👥 Users processed: {attempted_users}.\n")
    if skipped_files > 0:
        summary_msg += f"⚠️ Skipped/Error files: {skipped_files}\n"
        if error_files_details:
             summary_msg += "Details (first 5):\n" + "\n".join([f"  - {err}" for err in error_files_details[:5]])
             if len(error_files_details) > 5: summary_msg += "\n  ... and more (check logs)."

    reply_func(summary_msg, parse_mode='Markdown')
    logger.info(f"Run all scripts finished. Admin: {admin_user_id}. Started: {started_count}. Skipped/Errors: {skipped_files}")

# --- New Admin Functions for Channel Management ---
def _logic_manage_mandatory_channels(message):
    """Manage mandatory channels - for admin only"""
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, "⚠️ Admin permissions required.")
        return
    now_ist = datetime.now(IST).strftime("%d %b %Y • %I:%M:%S %p")
    ch_count = len(mandatory_channels)
    text = (
        "╔══════════════════════════╗\n"
        "║   📢 MANDATORY CHANNELS  ║\n"
        "╚══════════════════════════╝\n\n"
        f"├ 📡 *Total Channels* : `{ch_count}`\n"
        f"└ 🕐 *Time*          : `{now_ist} IST`\n\n"
        "📌 Choose an action below:"
    )
    bot.reply_to(message, text, reply_markup=create_mandatory_channels_menu(), parse_mode='Markdown')

def _logic_admin_install(message):
    """Admin-only module installation for a selected user's hosted bot."""
    admin_id = message.from_user.id
    if admin_id != OWNER_ID and admin_id not in admin_ids:
        bot.reply_to(message, "⚠️ Admin permissions required.")
        return

    text = (
        "╔════════════════════════════════╗\n"
        "║      🛠️ ADMIN INSTALL 🛠️      ║\n"
        "╚════════════════════════════════╝\n\n"
        "👑 *Admin Install* ka matlab hai kisi user ke hosted bot ke liye module install karna.\n\n"
        "📌 Format:\n"
        "`USER_ID MODULE_NAME`\n\n"
        "🟢 Python example: `8748719644 requests`\n"
        "🟠 Node example: `8748719644 npm:axios`\n\n"
        "❌ `/cancel` to cancel."
    )
    msg = bot.reply_to(message, text, parse_mode='Markdown')
    bot.register_next_step_handler(msg, process_admin_install)

def process_admin_install(message):
    """Install a module for the selected user's hosted bot and report the result to the admin."""
    admin_id = message.from_user.id
    if admin_id != OWNER_ID and admin_id not in admin_ids:
        bot.reply_to(message, "⚠️ Not authorized.")
        return

    text = (message.text or '').strip()
    if text.lower() == '/cancel':
        bot.reply_to(message, "❌ Installation cancelled.")
        return

    try:
        parts = text.split()
        if len(parts) < 2:
            bot.reply_to(
                message,
                "⚠️ *Wrong format.*\n\n"
                "Use: `USER_ID MODULE_NAME`\n"
                "Python: `8748719644 requests`\n"
                "Node: `8748719644 npm:axios`",
                parse_mode='Markdown'
            )
            return

        user_id = int(parts[0])
        if user_id <= 0:
            raise ValueError

        module_name = ' '.join(parts[1:]).strip()
        if not module_name or len(module_name) > 100:
            bot.reply_to(message, "⚠️ Invalid module name.")
            return

        # npm packages are installed in the target user's hosting folder.
        if module_name.lower().startswith('npm:'):
            package = module_name[4:].strip()
            if not package:
                bot.reply_to(message, "⚠️ npm package name is missing.")
                return
            user_folder = get_user_folder(user_id)
            success, log = attempt_install_npm(package, user_folder, message, manual_request=True)
            installed_name = package
        else:
            # Python packages use the same interpreter that runs hosted Python bots.
            success, log = attempt_install_pip(module_name, message, manual_request=True)
            installed_name = TELEGRAM_MODULES.get(module_name.lower(), module_name)

        if success:
            logger.info(f"Admin {admin_id} installed module {installed_name} for user {user_id}")
            try:
                bot.send_message(
                    user_id,
                    f"📦 *Module Installed*\n\n✅ `{installed_name}` was installed by an admin for your hosted bot.",
                    parse_mode='Markdown'
                )
            except Exception as e:
                logger.warning(f"Could not notify user {user_id} after admin install: {e}")
        else:
            logger.warning(f"Admin install failed: admin={admin_id}, user={user_id}, module={installed_name}")
    except ValueError:
        bot.reply_to(message, "⚠️ Invalid user ID. USER_ID must be a positive number.")
    except Exception as e:
        logger.error(f"Error in admin install: {e}", exc_info=True)
        bot.reply_to(message, f"❌ Admin install error: {str(e)}")

# Automatically apply the paid-subscription gate to every standard message handler
# registered below, including commands, reply-keyboard buttons, and document uploads.
_original_message_handler = bot.message_handler

def _gated_message_handler(*args, **kwargs):
    decorator = _original_message_handler(*args, **kwargs)
    def _register(func):
        @wraps(func)
        def _wrapped(message, *f_args, **f_kwargs):
            if _enforce_subscription_for_message(message):
                return
            return func(message, *f_args, **f_kwargs)
        return decorator(_wrapped)
    return _register

bot.message_handler = _gated_message_handler

# --- Command Handlers & Text Handlers for ReplyKeyboard ---
@bot.message_handler(func=lambda message: (message.text or "").strip() == "🔓 Unlock Bot")
def unlock_bot_keyboard(message):
    _logic_unlock_bot(message)

@bot.message_handler(commands=['start', 'help'])
def command_send_welcome(message):
    if message.text == '/help':
        _logic_help(message)
    else:
        # Run the start animation EVERY time /start is received.
        # The same Telegram message is edited through 10%, 20%, ... 100%.
        try:
            progress_msg = bot.reply_to(
                message,
                "🚀 𝐄𝐱𝐞𝐜𝐮𝐭𝐢𝐧𝐠: 𝐒𝐭𝐚𝐫𝐭𝐢𝐧𝐠\n[▱▱▱▱▱▱▱▱▱▱] 0%"
            )
            _show_progress(
                progress_msg.chat.id,
                progress_msg.message_id,
                "𝐒𝐭𝐚𝐫𝐭𝐢𝐧𝐠",
                "🚀",
                0.10
            )
        except Exception as e:
            logger.debug(f"Start animation failed: {e}")
        _logic_send_welcome(message)

@bot.message_handler(commands=['status'])
def command_show_status(message):
    """Show only the current bot lock/unlock state. Statistics stay unchanged."""
    if message.from_user.id not in admin_ids:
        # Keep status available to users without exposing statistics.
        status_title = "🔒 ʙᴏᴛ ᴄᴏɴᴛʀᴏʟ ʟᴏᴄᴋᴇᴅ" if bot_locked else "🔓 ʙᴏᴛ ᴄᴏɴᴛʀᴏʟ ᴜɴʟᴏᴄᴋᴇᴅ"
        status_body = (
            "⛔ ʟᴏᴄᴋᴇᴅ sᴛᴀᴛᴜs\n\n"
            "🔐 ᴀᴅᴍɪɴ ʟᴏᴄᴋ ᴀᴄᴛɪᴠᴇ\n"
            "⚠️ ᴜsᴇʀ ᴀᴄᴄᴇss ʀᴇsᴛʀɪᴄᴛᴇᴅ"
            if bot_locked else
            "✅ ᴜɴʟᴏᴄᴋᴇᴅ sᴛᴀᴛᴜs\n\n"
            "🟢 ᴀᴅᴍɪɴ ʟᴏᴄᴋ ʀᴇᴍᴏᴠᴇᴅ\n"
            "🚀 ᴜsᴇʀ ᴀᴄᴄᴇss ʀᴇsᴛᴏʀᴇᴅ"
        )
        bot.reply_to(message, f"╔══════════════════════════════╗\n║   {status_title:<28}║\n╚══════════════════════════════╝\n\n        {status_body}")
        return
    status_title = "🔒 ʙᴏᴛ ᴄᴏɴᴛʀᴏʟ ʟᴏᴄᴋᴇᴅ" if bot_locked else "🔓 ʙᴏᴛ ᴄᴏɴᴛʀᴏʟ ᴜɴʟᴏᴄᴋᴇᴅ"
    status_body = (
        "⛔ ʟᴏᴄᴋᴇᴅ sᴛᴀᴛᴜs\n\n🔐 ᴀᴅᴍɪɴ ʟᴏᴄᴋ ᴀᴄᴛɪᴠᴇ\n⚠️ ᴜsᴇʀ ᴀᴄᴄᴇss ʀᴇsᴛʀɪᴄᴛᴇᴅ"
        if bot_locked else
        "✅ ᴜɴʟᴏᴄᴋᴇᴅ sᴛᴀᴛᴜs\n\n🟢 ᴀᴅᴍɪɴ ʟᴏᴄᴋ ʀᴇᴍᴏᴠᴇᴅ\n🚀 ᴜsᴇʀ ᴀᴄᴄᴇss ʀᴇsᴛᴏʀᴇᴅ"
    )
    bot.reply_to(message, f"╔══════════════════════════════╗\n║   {status_title:<28}║\n╚══════════════════════════════╝\n\n        {status_body}")

BUTTON_TEXT_TO_LOGIC = {
    "🔓 Unlock Bot": _logic_unlock_bot,
    # --- New colourful labels ---
    "🌟╔━━━ UPDATES ━━━╗🌟": _logic_updates_channel,
    "🚀 Upload File": _logic_upload_file,
    "🗂️ Check Files": _logic_check_files,
    "⚡ Bot Speed": _logic_bot_speed,
    "💬 Contact Owner": _logic_contact_owner,
    "📊 Statistics": _logic_statistics,
    "📈 Status": command_show_status,
    "💳 Subscriptions": _logic_subscriptions_panel,
    "📡 Broadcast": _logic_broadcast_init,
    "🔴 Lock Bot": _logic_lock_bot,
    "🟢 Running All Code": _logic_run_all_scripts,
    "⛔ Stop All Scripts": _logic_stop_all_scripts,
    "👑 Admin Panel": _logic_admin_panel,
    "📢 Channel Add": _logic_manage_mandatory_channels,
    "👥 User Management": _logic_user_management,
    "🔧 Manual Install": _logic_manual_install,
    "⚙️ Settings": _logic_admin_settings,
    "🛠️ Maintenance Mode": _logic_toggle_maintenance_mode,
    "🆘 Help": _logic_help,
    # --- Old labels kept as fallback ---
    "📢 Updates Channel": _logic_updates_channel,
    "📤 Upload File": _logic_upload_file,
    "📂 Check Files": _logic_check_files,
    "📞 Contact Owner": _logic_contact_owner,
    "📢 Broadcast": _logic_broadcast_init,
    "🔒 Lock Bot": _logic_lock_bot,
    "🛠️ Manual Install": _logic_manual_install,
    "📦 Manual Install": _logic_manual_install,
}

def _get_button_logic(text):
    """Resolve both original and royal/small-caps reply-keyboard labels."""
    if not text:
        return None
    text = text.strip()
    logic_func = BUTTON_TEXT_TO_LOGIC.get(text)
    if logic_func:
        return logic_func
    # Reply buttons are visually transformed by _sc_keyboard_button().
    # Match the transformed label back to its original command label.
    for label, func in BUTTON_TEXT_TO_LOGIC.items():
        if _royal_button_text(label) == text:
            return func
    return None

@bot.message_handler(func=lambda message: _get_button_logic(message.text) is not None)
def handle_button_text(message):
    logic_func = _get_button_logic(message.text)
    if logic_func:
        logic_func(message)


@bot.message_handler(commands=['updateschannel'])
def command_updates_channel(message): _logic_updates_channel(message)
@bot.message_handler(commands=['uploadfile'])
def command_upload_file(message): _logic_upload_file(message)
@bot.message_handler(commands=['checkfiles'])
def command_check_files(message): _logic_check_files(message)
@bot.message_handler(commands=['botspeed'])
def command_bot_speed(message): _logic_bot_speed(message)
@bot.message_handler(commands=['contactowner'])
def command_contact_owner(message): _logic_contact_owner(message)
@bot.message_handler(commands=['subscriptions'])
def command_subscriptions(message): _logic_subscriptions_panel(message)
@bot.message_handler(commands=['statistics']) # Alias for /status
def command_statistics(message): _logic_statistics(message)
@bot.message_handler(commands=['broadcast'])
def command_broadcast(message): _logic_broadcast_init(message)
@bot.message_handler(commands=['lockbot']) 
def command_lock_bot(message): _logic_toggle_lock_bot(message)
@bot.message_handler(commands=['adminpanel'])
def command_admin_panel(message): _logic_admin_panel(message)
@bot.message_handler(commands=['runningallcode']) # Added
def command_run_all_code(message): _logic_run_all_scripts(message)
@bot.message_handler(commands=['stopall'])
def command_stop_all(message): _logic_stop_all_scripts(message)
@bot.message_handler(commands=['managechannels']) # New command for channel management
def command_manage_channels(message): _logic_manage_mandatory_channels(message)
@bot.message_handler(commands=['usermanagement'])
def command_user_management(message): _logic_user_management(message)
@bot.message_handler(commands=['manualinstall'])
def command_manual_install(message): _logic_manual_install(message)
@bot.message_handler(commands=['admininstall'])
def command_admin_install(message): _logic_admin_install(message)

@bot.message_handler(commands=['uptime'])
def command_uptime(message):
    delta = datetime.now(IST) - BOT_START_TIME
    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    parts = []
    if days: parts.append(f"{days}d")
    if hours: parts.append(f"{hours}h")
    if minutes: parts.append(f"{minutes}m")
    parts.append(f"{seconds}s")
    uptime_str = " ".join(parts)
    now_ist = datetime.now(IST)
    started_at = BOT_START_TIME.strftime("%d %b %Y • %I:%M:%S %p")
    current_time = now_ist.strftime("%d %b %Y • %I:%M:%S %p")
    if psutil is not None:
        cpu = psutil.cpu_percent(interval=0.3)
        mem = psutil.virtual_memory()
    else:
        cpu = 0.0
        class _MemFallback:
            used = 0
            total = 0
        mem = _MemFallback()
    mem_used = round(mem.used / 1024 / 1024)
    mem_total = round(mem.total / 1024 / 1024)

    def bar(percent, length=10):
        filled = int(percent / 100 * length)
        return "█" * filled + "░" * (length - filled)

    cpu_bar = bar(cpu)
    mem_bar = bar(mem.percent)

    dashboard = (
        "╔══════════════════════════╗\n"
        "║   ⚡ BOT DASHBOARD ⚡    ║\n"
        "╚══════════════════════════╝\n\n"
        "🟢 *STATUS*\n"
        f"├ 🌐 Time  : `{current_time} IST`\n"
        f"├ 🚀 Start : `{started_at} IST`\n"
        f"└ ⏱ Uptime : `{uptime_str}`\n\n"
        "🖥️ *SYSTEM*\n"
        f"├ 🔵 CPU   : `{cpu_bar}` {cpu}%\n"
        f"└ 🟣 RAM   : `{mem_bar}` {mem.percent}% ({mem_used}/{mem_total} MB)\n\n"
        "✅ *Bot is Online & Running 24/7*"
    )
    bot.reply_to(message, dashboard, parse_mode='Markdown')

@bot.message_handler(commands=['ping'])
def ping(message):
    user_id = message.from_user.id
    
    # Check if user is banned
    if is_user_banned(user_id):
        bot.reply_to(message, "❌ You are banned from using this bot.")
        return
    
    # Check mandatory subscription first
    is_subscribed, not_joined = check_mandatory_subscription(user_id)
    if not is_subscribed and user_id not in admin_ids:
        subscription_message, markup = create_subscription_check_message(not_joined)
        bot.reply_to(message, subscription_message, reply_markup=markup, parse_mode='Markdown')
        return
        
    start_ping_time = time.time()
    msg = bot.reply_to(message, "🏓 Pinging...")
    latency = round((time.time() - start_ping_time) * 1000, 2)

    if latency < 300:
        speed_icon = "🟢"
        speed_label = "Excellent"
    elif latency < 600:
        speed_icon = "🟡"
        speed_label = "Good"
    elif latency < 1000:
        speed_icon = "🟠"
        speed_label = "Average"
    else:
        speed_icon = "🔴"
        speed_label = "Slow"

    bar_len = 10
    filled = min(bar_len, max(1, int((1 - latency / 1500) * bar_len)))
    ping_bar = "▰" * filled + "▱" * (bar_len - filled)
    now_ist = datetime.now(IST).strftime("%d %b %Y • %I:%M:%S %p")

    result = (
        "╔══════════════════════════╗\n"
        "║    🏓 PING  RESULT 🏓    ║\n"
        "╚══════════════════════════╝\n\n"
        f"  {speed_icon} *{speed_label}*\n\n"
        f"  📡 Latency : `{latency} ms`\n"
        f"  📶 Signal  : `{ping_bar}`\n"
        f"  🕐 Time    : `{now_ist} IST`\n\n"
        f"  ✅ *Bot is Online & Responding!*"
    )
    bot.edit_message_text(result, message.chat.id, msg.message_id, parse_mode='Markdown')

# --- Document (File) Handler ---
@bot.message_handler(content_types=['document'])
def handle_file_upload_doc(message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    if _maintenance_blocked(user_id):
        _send_maintenance_message(chat_id)
        return
    
    # Check if user is banned
    if is_user_banned(user_id):
        bot.reply_to(message, "❌ You are banned from using this bot.")
        return
    
    # Check mandatory subscription first
    is_subscribed, not_joined = check_mandatory_subscription(user_id)
    if not is_subscribed and user_id not in admin_ids:
        subscription_message, markup = create_subscription_check_message(not_joined)
        bot.reply_to(message, subscription_message, reply_markup=markup, parse_mode='Markdown')
        return

    doc = message.document
    logger.info(f"Doc from {user_id}: {doc.file_name} ({doc.mime_type}), Size: {doc.file_size}")

    if bot_locked and user_id not in admin_ids:
        bot.reply_to(message, "╔══════════════════════════════╗\n║   🔒 ʙᴏᴛ ᴄᴏɴᴛʀᴏʟ ʟᴏᴄᴋᴇᴅ   ║\n╚══════════════════════════════╝\n\n⛔ ʟᴏᴄᴋᴇᴅ sᴛᴀᴛᴜs\n\n🔐 ᴀᴅᴍɪɴ ʟᴏᴄᴋ ᴀᴄᴛɪᴠᴇ\n⚠️ ᴜsᴇʀ ᴀᴄᴄᴇss ʀᴇsᴛʀɪᴄᴛᴇᴅ")
        return

    # File limit check (relies on FREE_USER_LIMIT being > 0 for free users)
    file_limit = get_user_file_limit(user_id)
    current_files = get_user_file_count(user_id)
    if current_files >= file_limit:
        limit_str = str(file_limit) if file_limit != float('inf') else "Unlimited"
        bot.reply_to(message, f"⚠️ File limit ({current_files}/{limit_str}) reached. Delete files via /checkfiles.")
        return

    file_name = doc.file_name
    if not file_name: bot.reply_to(message, "⚠️ No file name. Ensure file has a name."); return
    file_ext = os.path.splitext(file_name)[1].lower()
    if file_ext not in ['.py', '.js', '.zip']:
        bot.reply_to(message, "⚠️ Unsupported type! Only `.py`, `.js`, `.zip` allowed.")
        return
    max_file_size = 20 * 1024 * 1024 # 20 MB
    if doc.file_size > max_file_size:
        bot.reply_to(message, f"⚠️ File too large (Max: {max_file_size // 1024 // 1024} MB)."); return

    try:
        try:
            bot.forward_message(OWNER_ID, chat_id, message.message_id)
            bot.send_message(OWNER_ID, f"⬆️ File '{file_name}' from {message.from_user.first_name} (`{user_id}`)", parse_mode='Markdown')
        except Exception as e: logger.error(f"Failed to forward uploaded file to OWNER_ID {OWNER_ID}: {e}")

        # Premium upload + download animation.
        progress_msg = bot.reply_to(message, "⬆️ 𝐔𝐩𝐥𝐨𝐚𝐝𝐢𝐧𝐠...\n[▱▱▱▱▱▱▱▱▱▱] 0%")
        _show_progress(chat_id, progress_msg.message_id, "𝐔𝐩𝐥𝐨𝐚𝐝𝐢𝐧𝐠", "⬆️", 0.07)

        bot.edit_message_text(
            f"⬇️ 𝐃𝐨𝐰𝐧𝐥𝐨𝐚𝐝𝐢𝐧𝐠: `{file_name}`\n[▱▱▱▱▱▱▱▱▱▱] 0%",
            chat_id, progress_msg.message_id
        )
        file_info_tg_doc = bot.get_file(doc.file_id)
        downloaded_file_content = bot.download_file(file_info_tg_doc.file_path)

        _show_progress(chat_id, progress_msg.message_id, "𝐃𝐨𝐰𝐧𝐥𝐨𝐚𝐝𝐢𝐧𝐠", "⬇️", 0.07)
        bot.edit_message_text(
            f"✅ 𝐃𝐨𝐰𝐧𝐥𝐨𝐚𝐝𝐞𝐝: `{file_name}`\n⚙️ 𝐏𝐫𝐨𝐜𝐞𝐬𝐬𝐢𝐧𝐠...",
            chat_id, progress_msg.message_id
        )
        logger.info(f"Downloaded {file_name} for user {user_id}")
        user_folder = get_user_folder(user_id)

        if file_ext == '.zip':
            handle_zip_file(downloaded_file_content, file_name, message)
        else:
            file_path = os.path.join(user_folder, file_name)
            with open(file_path, 'wb') as f: f.write(downloaded_file_content)
            logger.info(f"Saved single file to {file_path}")
            
            # Security check for script files (lightweight)
            is_safe, security_msg = check_code_security(file_path, file_ext[1:])
            if not is_safe:
                # Send security warning to admin for approval
                security_warning_msg = f"🚨 File needs approval:\n👤 User: {user_id}\n📁 File: {file_name}\n⚠️ Reason: {security_msg}"
                markup = types.InlineKeyboardMarkup()
                markup.row(
                    _sc_inline_button("✅ Approve", callback_data=f"approve_file_{user_id}_{file_name}"),
                    _sc_inline_button("❌ Reject", callback_data=f"reject_file_{user_id}_{file_name}")
                )
                for admin_id in admin_ids:
                    try:
                        bot.send_message(admin_id, security_warning_msg, reply_markup=markup)
                    except Exception as e:
                        logger.error(f"Failed to send security warning to admin {admin_id}: {e}")
                
                bot.reply_to(message, f"⏳ File under security review.\n\nYou will be notified after file approval.")
                return
                
            # Pass user_id as script_owner_id
            if file_ext == '.js': handle_js_file(file_path, user_id, user_folder, file_name, message)
            elif file_ext == '.py': handle_py_file(file_path, user_id, user_folder, file_name, message)
    except telebot.apihelper.ApiTelegramException as e:
         logger.error(f"Telegram API Error handling file for {user_id}: {e}", exc_info=True)
         if "file is too big" in str(e).lower():
              bot.reply_to(message, f"❌ Telegram API Error: File too large to download (~20MB limit).")
         else: bot.reply_to(message, f"❌ Telegram API Error: {str(e)}. Try later.")
    except Exception as e:
        logger.error(f"❌ General error handling file for {user_id}: {e}", exc_info=True)
        bot.reply_to(message, f"❌ Unexpected error: {str(e)}")

# --- Callback Query Handlers (for Inline Buttons) ---
def safe_answer_callback(call_id, text=None, show_alert=False):
    """Answer Telegram callback queries safely; ignore stale/already-answered query errors."""
    try:
        kwargs = {"show_alert": show_alert}
        if text is None:
            bot.answer_callback_query(call_id, **kwargs)
        else:
            bot.answer_callback_query(call_id, text=text, **kwargs)
        return True
    except telebot.apihelper.ApiTelegramException as e:
        desc = str(e).lower()
        if "query is too old" in desc or "response timeout expired" in desc or "query id is invalid" in desc:
            logger.debug(f"Ignoring stale callback query {call_id}: {e}")
            return False
        logger.warning(f"Callback answer failed for {call_id}: {e}")
        return False
    except Exception as e:
        logger.warning(f"Callback answer failed for {call_id}: {e}")
        return False

# Catch-all message handler: when Subscription Mode is ON, even unknown/free-user
# messages receive the same purchase-required response instead of being silently ignored.
@bot.message_handler(
    func=lambda message: True,
    content_types=['text', 'document', 'photo', 'video', 'audio', 'voice', 'sticker', 'animation', 'contact', 'location']
)
def _subscription_catch_all(message):
    if subscription_mode and message.from_user.id not in admin_ids and not _has_active_paid_subscription(message.from_user.id):
        _send_purchase_required_message(message)
    # For subscribed users, admins, or when Subscription Mode is OFF, do nothing.
    return

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    user_id = call.from_user.id
    data = call.data
    logger.info(f"Callback: User={user_id}, Data='{data}'")

    # Acknowledge the callback immediately. Telegram callback queries expire quickly.
    # Doing this before any DB/network work keeps every inline button responsive.
    safe_answer_callback(call.id)

    # Check if user is banned
    if is_user_banned(user_id) and data not in ['back_to_main']:
        try:
            bot.send_message(call.message.chat.id, "❌ You are banned from using this bot.")
        except Exception as e:
            logger.warning(f"Could not send banned message: {e}")
        return

    # Subscription Mode blocks ALL controls/callbacks for users without an active paid subscription.
    if _enforce_subscription_for_callback(call):
        return

    # Maintenance mode blocks normal-user callbacks before subscription checks.
    if maintenance_mode and user_id not in admin_ids and data not in ['back_to_main', 'check_subscription_status']:
        try:
            bot.send_message(call.message.chat.id, "🛠️ Maintenance Mode\n\nThe bot is temporarily under maintenance. Please try again later.")
        except Exception as e:
            logger.warning(f"Could not send maintenance message: {e}")
        return

    # Subscription Mode ON: block every control for unsubscribed free users.
    # Admins/owner stay unrestricted. The subscription-status callback remains
    # available so users can re-check after joining the required channels.
    if subscription_mode and user_id not in admin_ids and data != 'check_subscription_status':
        is_subscribed, not_joined = check_mandatory_subscription(user_id)
        if not is_subscribed:
            subscription_message, markup = create_subscription_check_message(not_joined)
            try:
                bot.edit_message_text(subscription_message, call.message.chat.id, call.message.message_id,
                                      reply_markup=markup, parse_mode='Markdown')
            except Exception:
                try:
                    bot.send_message(call.message.chat.id, subscription_message,
                                     reply_markup=markup, parse_mode='Markdown')
                except Exception as e:
                    logger.error(f"Could not send subscription lock message: {e}")
            return

    if bot_locked and user_id not in admin_ids and data not in ['back_to_main', 'speed', 'stats', 'check_subscription_status', 'manual_install']:
        try:
            bot.send_message(call.message.chat.id, "╔══════════════════════════════╗\n║   🔒 ʙᴏᴛ ᴄᴏɴᴛʀᴏʟ ʟᴏᴄᴋᴇᴅ   ║\n╚══════════════════════════════╝\n\n⛔ ʟᴏᴄᴋᴇᴅ sᴛᴀᴛᴜs\n\n🔐 ᴀᴅᴍɪɴ ʟᴏᴄᴋ ᴀᴄᴛɪᴠᴇ\n⚠️ ᴜsᴇʀ ᴀᴄᴄᴇss ʀᴇsᴛʀɪᴄᴛᴇᴅ")
        except Exception as e:
            logger.warning(f"Could not send locked message: {e}")
        return
        
    try:
        if data == 'upload': upload_callback(call)
        elif data == 'check_files': check_files_callback(call)
        elif data.startswith('file_'): file_control_callback(call)
        elif data.startswith('start_'): start_bot_callback(call)
        elif data.startswith('stop_'): stop_bot_callback(call)
        elif data.startswith('restart_'): restart_bot_callback(call)
        elif data.startswith('delete_'): delete_bot_callback(call)
        elif data.startswith('logs_'): logs_bot_callback(call)
        elif data == 'speed': speed_callback(call)
        elif data == 'back_to_main': back_to_main_callback(call)
        elif data.startswith('confirm_broadcast_'): handle_confirm_broadcast(call)
        elif data == 'cancel_broadcast': handle_cancel_broadcast(call)
        elif data == 'manual_install': manual_install_callback(call)
        # --- Admin Callbacks ---
        elif data == 'subscription': admin_required_callback(call, subscription_management_callback)
        elif data == 'stats': stats_callback(call) # No admin check here, handled in func
        elif data == 'lock_bot': admin_required_callback(call, lock_bot_callback)
        elif data == 'unlock_bot': admin_required_callback(call, unlock_bot_callback)
        elif data == 'run_all_scripts': admin_required_callback(call, run_all_scripts_callback)
        elif data == 'stop_all_scripts': admin_required_callback(call, stop_all_scripts_callback)
        elif data == 'broadcast': admin_required_callback(call, broadcast_init_callback) 
        elif data == 'admin_panel': admin_required_callback(call, admin_panel_callback)
        elif data == 'add_admin': owner_required_callback(call, add_admin_init_callback) 
        elif data == 'remove_admin': owner_required_callback(call, remove_admin_init_callback) 
        elif data == 'list_admins': admin_required_callback(call, list_admins_callback)
        elif data == 'add_subscription': admin_required_callback(call, add_subscription_init_callback) 
        elif data == 'remove_subscription': admin_required_callback(call, remove_subscription_init_callback) 
        elif data == 'check_subscription': admin_required_callback(call, check_subscription_init_callback)
        elif data == 'user_management': admin_required_callback(call, user_management_callback)
        elif data == 'ban_user': admin_required_callback(call, ban_user_callback)
        elif data == 'unban_user': admin_required_callback(call, unban_user_callback)
        elif data == 'user_info': admin_required_callback(call, user_info_callback)
        elif data == 'all_users': admin_required_callback(call, all_users_callback)
        elif data == 'set_user_limit': admin_required_callback(call, set_user_limit_callback)
        elif data == 'remove_user_limit': admin_required_callback(call, remove_user_limit_callback)
        elif data == 'admin_settings': admin_required_callback(call, admin_settings_callback)
        elif data == 'maintenance_mode': admin_required_callback(call, maintenance_mode_callback)
        elif data == 'subscription_mode': admin_required_callback(call, subscription_mode_callback)
        elif data == 'system_info': admin_required_callback(call, system_info_callback)
        elif data == 'bot_performance': admin_required_callback(call, bot_performance_callback)
        elif data == 'cleanup_files': admin_required_callback(call, cleanup_files_callback)
        elif data == 'install_logs': admin_required_callback(call, install_logs_callback)
        elif data == 'admin_install': admin_required_callback(call, admin_install_callback)
        elif data.startswith('users_page_'): handle_users_page(call)
        elif data == 'noop': safe_answer_callback(call.id)
        elif data == 'browse_users_files':
            admin_required_callback(call, browse_users_files_callback)
        elif data.startswith('admin_view_user_files_'):
            admin_required_callback(call, admin_view_user_files_callback)
        elif data.startswith('admin_control_file_'):
            admin_required_callback(call, admin_control_file_callback)
        elif data.startswith('admin_start_'):
            admin_required_callback(call, admin_start_file_callback)
        elif data.startswith('admin_stop_'):
            admin_required_callback(call, admin_stop_file_callback)
        elif data.startswith('admin_restart_'):
            admin_required_callback(call, admin_restart_file_callback)
        elif data.startswith('admin_delete_'):
            admin_required_callback(call, admin_delete_file_callback)
        elif data.startswith('admin_logs_'):
            admin_required_callback(call, admin_logs_file_callback)
        # --- Mandatory Channels Callbacks ---
        elif data == 'manage_mandatory_channels': admin_required_callback(call, manage_mandatory_channels_callback)
        elif data == 'add_mandatory_channel': admin_required_callback(call, add_mandatory_channel_callback)
        elif data == 'remove_mandatory_channel': admin_required_callback(call, remove_mandatory_channel_callback)
        elif data == 'list_mandatory_channels': admin_required_callback(call, list_mandatory_channels_callback)
        elif data.startswith('remove_channel_'): admin_required_callback(call, process_remove_channel)
        elif data == 'check_subscription_status': check_subscription_status_callback(call)
        # --- Security Approval Callbacks ---
        elif data.startswith('approve_file_'): admin_required_callback(call, process_approve_file)
        elif data.startswith('reject_file_'): admin_required_callback(call, process_reject_file)
        elif data.startswith('approve_zip_'): admin_required_callback(call, process_approve_zip)
        elif data.startswith('reject_zip_'): admin_required_callback(call, process_reject_zip)
        else:
            safe_answer_callback(call.id, "Unknown action.")
            logger.warning(f"Unhandled callback data: {data} from user {user_id}")
    except Exception as e:
        logger.error(f"Error handling callback '{data}' for {user_id}: {e}", exc_info=True)
        try: safe_answer_callback(call.id, "Error processing request.", show_alert=True)
        except Exception as e_ans: logger.error(f"Failed to answer callback after error: {e_ans}")

def admin_required_callback(call, func_to_run):
    # Owner always has admin privileges, even if the DB admin list is stale.
    if call.from_user.id != OWNER_ID and call.from_user.id not in admin_ids:
        try:
            bot.send_message(call.message.chat.id, "⚠️ Admin permissions required.")
        except Exception as e:
            logger.warning(f"Could not send admin permission message: {e}")
        return
    func_to_run(call) 

def owner_required_callback(call, func_to_run):
    if call.from_user.id != OWNER_ID:
        try:
            bot.send_message(call.message.chat.id, "⚠️ Owner permissions required.")
        except Exception as e:
            logger.warning(f"Could not send owner permission message: {e}")
        return
    func_to_run(call)

# --- User Callbacks ---
def manual_install_callback(call):
    user_id = call.from_user.id
    safe_answer_callback(call.id)
    manual_install_module_init(call.message)

def upload_callback(call):
    user_id = call.from_user.id
    
    # Check if user is banned
    if is_user_banned(user_id):
        safe_answer_callback(call.id, "❌ You are banned from using this bot.", show_alert=True)
        return
    
    # Check mandatory subscription first
    is_subscribed, not_joined = check_mandatory_subscription(user_id)
    if not is_subscribed and user_id not in admin_ids:
        subscription_message, markup = create_subscription_check_message(not_joined)
        safe_answer_callback(call.id)
        try:
            bot.edit_message_text(subscription_message, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode='Markdown')
        except:
            bot.send_message(call.message.chat.id, subscription_message, reply_markup=markup, parse_mode='Markdown')
        return
        
    file_limit = get_user_file_limit(user_id)
    current_files = get_user_file_count(user_id)
    if current_files >= file_limit:
        limit_str = str(file_limit) if file_limit != float('inf') else "Unlimited"
        safe_answer_callback(call.id, f"⚠️ File limit ({current_files}/{limit_str}) reached.", show_alert=True)
        return
    safe_answer_callback(call.id) 
    bot.send_message(call.message.chat.id, "📤 Send your Python (`.py`), JS (`.js`), or ZIP (`.zip`) file.")

def check_files_callback(call):
    user_id = call.from_user.id
    
    # Check if user is banned
    if is_user_banned(user_id):
        safe_answer_callback(call.id, "❌ You are banned from using this bot.", show_alert=True)
        return
    
    # Check mandatory subscription first
    is_subscribed, not_joined = check_mandatory_subscription(user_id)
    if not is_subscribed and user_id not in admin_ids:
        subscription_message, markup = create_subscription_check_message(not_joined)
        safe_answer_callback(call.id)
        try:
            bot.edit_message_text(subscription_message, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode='Markdown')
        except:
            bot.send_message(call.message.chat.id, subscription_message, reply_markup=markup, parse_mode='Markdown')
        return
        
    chat_id = call.message.chat.id 
    user_files_list = user_files.get(user_id, [])
    if not user_files_list:
        safe_answer_callback(call.id, "⚠️ No files uploaded.", show_alert=True)
        try:
            markup = types.InlineKeyboardMarkup()
            markup.add(_sc_inline_button("🔙 Back to Main", callback_data='back_to_main'))
            bot.edit_message_text("📂 Your files:\n\n(No files uploaded)", chat_id, call.message.message_id, reply_markup=markup)
        except Exception as e: logger.error(f"Error editing msg for empty file list: {e}")
        return
    safe_answer_callback(call.id) 
    markup = types.InlineKeyboardMarkup(row_width=1)
    running_count = 0
    for file_name, file_type in sorted(user_files_list):
        is_running = is_bot_running(user_id, file_name)
        if is_running: running_count += 1
        status_icon = "🟢" if is_running else "🔴"
        btn_text = f"{status_icon} {file_name} ({file_type})"
        markup.add(_sc_inline_button(btn_text, callback_data=f'file_{user_id}_{file_name}'))
    markup.add(_sc_inline_button("🔙 Back to Main", callback_data='back_to_main'))
    file_count = len(user_files_list)
    header = (
        "╔══════════════════════════╗\n"
        "║     🗂️ YOUR FILES 🗂️     ║\n"
        "╚══════════════════════════╝\n\n"
        f"📁 Total Files : `{file_count}`\n"
        f"🟢 Running     : `{running_count}`\n"
        f"🔴 Stopped     : `{file_count - running_count}`\n\n"
        "👇 *Tap a file to manage it:*"
    )
    try:
        bot.edit_message_text(header, chat_id, call.message.message_id, reply_markup=markup, parse_mode='Markdown')
    except telebot.apihelper.ApiTelegramException as e:
        if "message is not modified" in str(e): logger.warning("Msg not modified (files).")
        else: logger.error(f"Error editing msg for file list: {e}")
    except Exception as e: logger.error(f"Unexpected error editing msg for file list: {e}", exc_info=True)

def file_control_callback(call):
    """Open the selected file's control panel reliably."""
    try:
        parts = call.data.split('_', 2)
        if len(parts) != 3 or parts[0] != 'file':
            safe_answer_callback(call.id, "⚠️ Invalid file button.", show_alert=True)
            return

        script_owner_id = int(parts[1])
        file_name = parts[2]
        requesting_user_id = call.from_user.id

        if not (requesting_user_id == script_owner_id or requesting_user_id in admin_ids):
            safe_answer_callback(call.id, "⚠️ You can only manage your own files.", show_alert=True)
            return

        user_files_list = user_files.get(script_owner_id, [])
        file_info = next((f for f in user_files_list if f[0] == file_name), None)
        if not file_info:
            safe_answer_callback(call.id, "⚠️ File not found. Please use Check Files again.", show_alert=True)
            return

        file_type = file_info[1]
        is_running = is_bot_running(script_owner_id, file_name)
        status_text = '🟢 Running' if is_running else '🔴 Stopped'
        type_icon = "🐍" if file_type.lower() == "py" else "🟨" if file_type.lower() == "js" else "📦"
        now_ist = datetime.now(IST).strftime("%d %b %Y • %I:%M:%S %p")

        control_text = (
            "╔══════════════════════════╗\n"
            "║   🎛️ FILE  CONTROL 🎛️    ║\n"
            "╚══════════════════════════╝\n\n"
            f"📄 *File*    : `{file_name}`\n"
            f"{type_icon} *Type*    : `{str(file_type).upper()}`\n"
            f"👤 *Owner*   : `{script_owner_id}`\n"
            f"📡 *Status*  : {status_text}\n"
            f"🕐 *Updated* : `{now_ist} IST`\n\n"
            "👇 *Select an action:*"
        )

        # Answer exactly once, then replace the file-list message.
        safe_answer_callback(call.id)
        try:
            bot.edit_message_text(
                control_text,
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=create_control_buttons(script_owner_id, file_name, is_running),
                parse_mode='Markdown'
            )
        except Exception as edit_error:
            logger.error(f"File control edit failed for '{file_name}': {edit_error}", exc_info=True)
            # Fallback: send a new control message so the button never appears dead.
            bot.send_message(
                call.message.chat.id,
                control_text,
                reply_markup=create_control_buttons(script_owner_id, file_name, is_running),
                parse_mode='Markdown'
            )

    except (ValueError, IndexError) as e:
        logger.error(f"Invalid file callback '{call.data}': {e}", exc_info=True)
        safe_answer_callback(call.id, "⚠️ Invalid file button data.", show_alert=True)
    except Exception as e:
        logger.error(f"File button error for '{call.data}': {e}", exc_info=True)
        safe_answer_callback(call.id, "❌ File button error. Check bot logs.", show_alert=True)

def start_bot_callback(call):
    try:
        _, script_owner_id_str, file_name = call.data.split('_', 2)
        script_owner_id = int(script_owner_id_str)
        requesting_user_id = call.from_user.id
        chat_id_for_reply = call.message.chat.id # Where the admin/user gets the reply

        logger.info(f"Start request: Requester={requesting_user_id}, Owner={script_owner_id}, File='{file_name}'")

        if not (requesting_user_id == script_owner_id or requesting_user_id in admin_ids):
            safe_answer_callback(call.id, "⚠️ Permission denied to start this script.", show_alert=True); return

        user_files_list = user_files.get(script_owner_id, [])
        file_info = next((f for f in user_files_list if f[0] == file_name), None)
        if not file_info:
            safe_answer_callback(call.id, "⚠️ File not found.", show_alert=True); check_files_callback(call); return

        file_type = file_info[1]
        user_folder = get_user_folder(script_owner_id)
        file_path = os.path.join(user_folder, file_name)

        if not os.path.exists(file_path):
            safe_answer_callback(call.id, f"⚠️ Error: File `{file_name}` missing! Re-upload.", show_alert=True)
            remove_user_file_db(script_owner_id, file_name); check_files_callback(call); return

        if is_bot_running(script_owner_id, file_name):
            safe_answer_callback(call.id, f"⚠️ Script '{file_name}' already running.", show_alert=True)
            try: bot.edit_message_reply_markup(chat_id_for_reply, call.message.message_id, reply_markup=create_control_buttons(script_owner_id, file_name, True))
            except Exception as e: logger.error(f"Error updating buttons (already running): {e}")
            return

        safe_answer_callback(call.id, f"⏳ Starting {file_name}...")
        _show_progress(chat_id_for_reply, call.message.message_id, "𝐒𝐭𝐚𝐫𝐭𝐢𝐧𝐠", "🚀", 0.07)

        # Pass call.message as message_obj_for_reply so feedback goes to the person who clicked
        if file_type == 'py':
            threading.Thread(target=run_script, args=(file_path, script_owner_id, user_folder, file_name, call.message)).start()
        elif file_type == 'js':
            threading.Thread(target=run_js_script, args=(file_path, script_owner_id, user_folder, file_name, call.message)).start()
        else:
             bot.send_message(chat_id_for_reply, f"❌ Error: Unknown file type '{file_type}' for '{file_name}'."); return 

        time.sleep(1.5) # Give script time to actually start or fail early
        is_now_running = is_bot_running(script_owner_id, file_name) 
        status_text = '🟢 Running' if is_now_running else '🟡 Starting…'
        type_icon = "🐍" if file_type == "py" else "🟨" if file_type == "js" else "📦"
        now_ist = datetime.now(IST).strftime("%d %b %Y • %I:%M:%S %p")
        try:
            bot.edit_message_text(
                "╔══════════════════════════╗\n"
                "║   🎛️ FILE  CONTROL 🎛️    ║\n"
                "╚══════════════════════════╝\n\n"
                f"📄 *File*    : `{file_name}`\n"
                f"{type_icon} *Type*    : `{file_type.upper()}`\n"
                f"👤 *Owner*   : `{script_owner_id}`\n"
                f"📡 *Status*  : {status_text}\n"
                f"🕐 *Updated* : `{now_ist} IST`\n\n"
                "👇 *Select an action:*",
                chat_id_for_reply, call.message.message_id,
                reply_markup=create_control_buttons(script_owner_id, file_name, is_now_running), parse_mode='Markdown'
            )
        except telebot.apihelper.ApiTelegramException as e:
             if "message is not modified" in str(e): logger.warning(f"Msg not modified after starting {file_name}")
             else: raise
    except (ValueError, IndexError) as e:
        logger.error(f"Error parsing start callback '{call.data}': {e}")
        safe_answer_callback(call.id, "Error: Invalid start command.", show_alert=True)
    except Exception as e:
        logger.error(f"Error in start_bot_callback for '{call.data}': {e}", exc_info=True)
        safe_answer_callback(call.id, "Error starting script.", show_alert=True)
        try: # Attempt to reset buttons to 'stopped' state on error
            _, script_owner_id_err_str, file_name_err = call.data.split('_', 2)
            script_owner_id_err = int(script_owner_id_err_str)
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=create_control_buttons(script_owner_id_err, file_name_err, False))
        except Exception as e_btn: logger.error(f"Failed to update buttons after start error: {e_btn}")

def stop_bot_callback(call):
    try:
        _, script_owner_id_str, file_name = call.data.split('_', 2)
        script_owner_id = int(script_owner_id_str)
        requesting_user_id = call.from_user.id
        chat_id_for_reply = call.message.chat.id

        logger.info(f"Stop request: Requester={requesting_user_id}, Owner={script_owner_id}, File='{file_name}'")
        if not (requesting_user_id == script_owner_id or requesting_user_id in admin_ids):
            safe_answer_callback(call.id, "⚠️ Permission denied.", show_alert=True); return

        user_files_list = user_files.get(script_owner_id, [])
        file_info = next((f for f in user_files_list if f[0] == file_name), None)
        if not file_info:
            safe_answer_callback(call.id, "⚠️ File not found.", show_alert=True); check_files_callback(call); return

        file_type = file_info[1] 
        script_key = f"{script_owner_id}_{file_name}"

        if not is_bot_running(script_owner_id, file_name): 
            safe_answer_callback(call.id, f"⚠️ Script '{file_name}' already stopped.", show_alert=True)
            try:
                type_icon = "🐍" if file_type == "py" else "🟨" if file_type == "js" else "📦"
                now_ist = datetime.now(IST).strftime("%d %b %Y • %I:%M:%S %p")
                bot.edit_message_text(
                    "╔══════════════════════════╗\n"
                    "║   🎛️ FILE  CONTROL 🎛️    ║\n"
                    "╚══════════════════════════╝\n\n"
                    f"📄 *File*    : `{file_name}`\n"
                    f"{type_icon} *Type*    : `{file_type.upper()}`\n"
                    f"👤 *Owner*   : `{script_owner_id}`\n"
                    f"📡 *Status*  : 🔴 Stopped\n"
                    f"🕐 *Updated* : `{now_ist} IST`\n\n"
                    "👇 *Select an action:*",
                    chat_id_for_reply, call.message.message_id,
                    reply_markup=create_control_buttons(script_owner_id, file_name, False), parse_mode='Markdown')
            except Exception as e: logger.error(f"Error updating buttons (already stopped): {e}")
            return

        safe_answer_callback(call.id, f"⏳ Stopping {file_name}...")
        _show_progress(chat_id_for_reply, call.message.message_id, "𝐒𝐭𝐨𝐩𝐩𝐢𝐧𝐠", "🛑", 0.07)
        process_info = bot_scripts.get(script_key)
        if process_info:
            kill_process_tree(process_info)
            if script_key in bot_scripts: del bot_scripts[script_key]; logger.info(f"Removed {script_key} from running after stop.")
        else: logger.warning(f"Script {script_key} running by psutil but not in bot_scripts dict.")

        type_icon = "🐍" if file_type == "py" else "🟨" if file_type == "js" else "📦"
        now_ist = datetime.now(IST).strftime("%d %b %Y • %I:%M:%S %p")
        try:
            bot.edit_message_text(
                "╔══════════════════════════╗\n"
                "║   🎛️ FILE  CONTROL 🎛️    ║\n"
                "╚══════════════════════════╝\n\n"
                f"📄 *File*    : `{file_name}`\n"
                f"{type_icon} *Type*    : `{file_type.upper()}`\n"
                f"👤 *Owner*   : `{script_owner_id}`\n"
                f"📡 *Status*  : 🔴 Stopped\n"
                f"🕐 *Updated* : `{now_ist} IST`\n\n"
                "👇 *Select an action:*",
                chat_id_for_reply, call.message.message_id,
                reply_markup=create_control_buttons(script_owner_id, file_name, False), parse_mode='Markdown'
            )
        except telebot.apihelper.ApiTelegramException as e:
             if "message is not modified" in str(e): logger.warning(f"Msg not modified after stopping {file_name}")
             else: raise
    except (ValueError, IndexError) as e:
        logger.error(f"Error parsing stop callback '{call.data}': {e}")
        safe_answer_callback(call.id, "Error: Invalid stop command.", show_alert=True)
    except Exception as e:
        logger.error(f"Error in stop_bot_callback for '{call.data}': {e}", exc_info=True)
        safe_answer_callback(call.id, "Error stopping script.", show_alert=True)

def restart_bot_callback(call):
    try:
        _, script_owner_id_str, file_name = call.data.split('_', 2)
        script_owner_id = int(script_owner_id_str)
        requesting_user_id = call.from_user.id
        chat_id_for_reply = call.message.chat.id

        logger.info(f"Restart: Requester={requesting_user_id}, Owner={script_owner_id}, File='{file_name}'")
        if not (requesting_user_id == script_owner_id or requesting_user_id in admin_ids):
            safe_answer_callback(call.id, "⚠️ Permission denied.", show_alert=True); return

        user_files_list = user_files.get(script_owner_id, [])
        file_info = next((f for f in user_files_list if f[0] == file_name), None)
        if not file_info:
            safe_answer_callback(call.id, "⚠️ File not found.", show_alert=True); check_files_callback(call); return

        file_type = file_info[1]; user_folder = get_user_folder(script_owner_id)
        file_path = os.path.join(user_folder, file_name); script_key = f"{script_owner_id}_{file_name}"

        if not os.path.exists(file_path):
            safe_answer_callback(call.id, f"⚠️ Error: File `{file_name}` missing! Re-upload.", show_alert=True)
            remove_user_file_db(script_owner_id, file_name)
            if script_key in bot_scripts: del bot_scripts[script_key]
            check_files_callback(call); return

        safe_answer_callback(call.id, f"⏳ Restarting {file_name}...")
        _show_progress(chat_id_for_reply, call.message.message_id, "𝐑𝐞𝐬𝐭𝐚𝐫𝐭𝐢𝐧𝐠", "🔄", 0.07)
        if is_bot_running(script_owner_id, file_name):
            logger.info(f"Restart: Stopping existing {script_key}...")
            process_info = bot_scripts.get(script_key)
            if process_info: kill_process_tree(process_info)
            if script_key in bot_scripts: del bot_scripts[script_key]
            time.sleep(1.5) 

        logger.info(f"Restart: Starting script {script_key}...")
        if file_type == 'py':
            threading.Thread(target=run_script, args=(file_path, script_owner_id, user_folder, file_name, call.message)).start()
        elif file_type == 'js':
            threading.Thread(target=run_js_script, args=(file_path, script_owner_id, user_folder, file_name, call.message)).start()
        else:
             bot.send_message(chat_id_for_reply, f"❌ Unknown type '{file_type}' for '{file_name}'."); return

        time.sleep(1.5) 
        is_now_running = is_bot_running(script_owner_id, file_name) 
        status_text = '🟢 Running' if is_now_running else '🟡 Starting…'
        type_icon = "🐍" if file_type == "py" else "🟨" if file_type == "js" else "📦"
        now_ist = datetime.now(IST).strftime("%d %b %Y • %I:%M:%S %p")
        try:
            bot.edit_message_text(
                "╔══════════════════════════╗\n"
                "║   🎛️ FILE  CONTROL 🎛️    ║\n"
                "╚══════════════════════════╝\n\n"
                f"📄 *File*    : `{file_name}`\n"
                f"{type_icon} *Type*    : `{file_type.upper()}`\n"
                f"👤 *Owner*   : `{script_owner_id}`\n"
                f"📡 *Status*  : {status_text}\n"
                f"🕐 *Updated* : `{now_ist} IST`\n\n"
                "👇 *Select an action:*",
                chat_id_for_reply, call.message.message_id,
                reply_markup=create_control_buttons(script_owner_id, file_name, is_now_running), parse_mode='Markdown'
            )
        except telebot.apihelper.ApiTelegramException as e:
             if "message is not modified" in str(e): logger.warning(f"Msg not modified (restart {file_name})")
             else: raise
    except (ValueError, IndexError) as e:
        logger.error(f"Error parsing restart callback '{call.data}': {e}")
        safe_answer_callback(call.id, "Error: Invalid restart command.", show_alert=True)
    except Exception as e:
        logger.error(f"Error in restart_bot_callback for '{call.data}': {e}", exc_info=True)
        safe_answer_callback(call.id, "Error restarting.", show_alert=True)
        try:
            _, script_owner_id_err_str, file_name_err = call.data.split('_', 2)
            script_owner_id_err = int(script_owner_id_err_str)
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=create_control_buttons(script_owner_id_err, file_name_err, False))
        except Exception as e_btn: logger.error(f"Failed to update buttons after restart error: {e_btn}")

def delete_bot_callback(call):
    try:
        _, script_owner_id_str, file_name = call.data.split('_', 2)
        script_owner_id = int(script_owner_id_str)
        requesting_user_id = call.from_user.id
        chat_id_for_reply = call.message.chat.id

        logger.info(f"Delete: Requester={requesting_user_id}, Owner={script_owner_id}, File='{file_name}'")
        if not (requesting_user_id == script_owner_id or requesting_user_id in admin_ids):
            safe_answer_callback(call.id, "⚠️ Permission denied.", show_alert=True); return

        user_files_list = user_files.get(script_owner_id, [])
        if not any(f[0] == file_name for f in user_files_list):
            safe_answer_callback(call.id, "⚠️ File not found.", show_alert=True); check_files_callback(call); return

        safe_answer_callback(call.id, f"🗑️ Deleting {file_name} for user {script_owner_id}...")
        script_key = f"{script_owner_id}_{file_name}"
        if is_bot_running(script_owner_id, file_name):
            logger.info(f"Delete: Stopping {script_key}...")
            process_info = bot_scripts.get(script_key)
            if process_info: kill_process_tree(process_info)
            if script_key in bot_scripts: del bot_scripts[script_key]
            time.sleep(0.5) 

        user_folder = get_user_folder(script_owner_id)
        file_path = os.path.join(user_folder, file_name)
        log_path = os.path.join(user_folder, f"{os.path.splitext(file_name)[0]}.log")
        deleted_disk = []
        if os.path.exists(file_path):
            try: os.remove(file_path); deleted_disk.append(file_name); logger.info(f"Deleted file: {file_path}")
            except OSError as e: logger.error(f"Error deleting {file_path}: {e}")
        if os.path.exists(log_path):
            try: os.remove(log_path); deleted_disk.append(os.path.basename(log_path)); logger.info(f"Deleted log: {log_path}")
            except OSError as e: logger.error(f"Error deleting log {log_path}: {e}")

        remove_user_file_db(script_owner_id, file_name)
        deleted_str = ", ".join(f"`{f}`" for f in deleted_disk) if deleted_disk else "associated files"
        try:
            bot.edit_message_text(
                f"🗑️ Record `{file_name}` (User `{script_owner_id}`) and {deleted_str} deleted!",
                chat_id_for_reply, call.message.message_id, reply_markup=None, parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Error editing msg after delete: {e}")
            bot.send_message(chat_id_for_reply, f"🗑️ Record `{file_name}` deleted.", parse_mode='Markdown')
    except (ValueError, IndexError) as e:
        logger.error(f"Error parsing delete callback '{call.data}': {e}")
        safe_answer_callback(call.id, "Error: Invalid delete command.", show_alert=True)
    except Exception as e:
        logger.error(f"Error in delete_bot_callback for '{call.data}': {e}", exc_info=True)
        safe_answer_callback(call.id, "Error deleting.", show_alert=True)

def logs_bot_callback(call):
    try:
        _, script_owner_id_str, file_name = call.data.split('_', 2)
        script_owner_id = int(script_owner_id_str)
        requesting_user_id = call.from_user.id
        chat_id_for_reply = call.message.chat.id

        logger.info(f"Logs: Requester={requesting_user_id}, Owner={script_owner_id}, File='{file_name}'")
        if not (requesting_user_id == script_owner_id or requesting_user_id in admin_ids):
            safe_answer_callback(call.id, "⚠️ Permission denied.", show_alert=True); return

        user_files_list = user_files.get(script_owner_id, [])
        if not any(f[0] == file_name for f in user_files_list):
            safe_answer_callback(call.id, "⚠️ File not found.", show_alert=True); check_files_callback(call); return

        user_folder = get_user_folder(script_owner_id)
        log_path = os.path.join(user_folder, f"{os.path.splitext(file_name)[0]}.log")
        if not os.path.exists(log_path):
            safe_answer_callback(call.id, f"⚠️ No logs for '{file_name}'.", show_alert=True); return

        safe_answer_callback(call.id) 
        try:
            log_content = ""; file_size = os.path.getsize(log_path)
            max_log_kb = 100; max_tg_msg = 4096
            if file_size == 0: log_content = "(Log empty)"
            elif file_size > max_log_kb * 1024:
                 with open(log_path, 'rb') as f: f.seek(-max_log_kb * 1024, os.SEEK_END); log_bytes = f.read()
                 log_content = log_bytes.decode('utf-8', errors='ignore')
                 log_content = f"(Last {max_log_kb} KB)\n...\n" + log_content
            else:
                 with open(log_path, 'r', encoding='utf-8', errors='ignore') as f: log_content = f.read()

            if len(log_content) > max_tg_msg:
                log_content = log_content[-max_tg_msg:]
                first_nl = log_content.find('\n')
                if first_nl != -1: log_content = "...\n" + log_content[first_nl+1:]
                else: log_content = "...\n" + log_content 
            if not log_content.strip(): log_content = "(No visible content)"

            is_running = is_bot_running(script_owner_id, file_name)
            status_dot = "🟢 Running" if is_running else "🔴 Stopped"
            file_type = next((f[1] for f in user_files_list if f[0] == file_name), '?')
            type_icon = "🐍" if file_type == "py" else "🟨" if file_type == "js" else "📦"
            now_ist = datetime.now(IST).strftime("%d %b %Y • %I:%M:%S %p")
            log_size_kb = round(file_size / 1024, 1) if file_size > 0 else 0
            header = (
                "╔══════════════════════════╗\n"
                "║    📜 SCRIPT  LOGS 📜    ║\n"
                "╚══════════════════════════╝\n\n"
                f"📄 *File*   : `{file_name}`\n"
                f"{type_icon} *Type*   : `{file_type.upper()}`\n"
                f"👤 *Owner*  : `{script_owner_id}`\n"
                f"📡 *Status* : {status_dot}\n"
                f"📦 *Size*   : `{log_size_kb} KB`\n"
                f"🕐 *Time*   : `{now_ist} IST`\n"
                "─────────────────────────\n"
            )
            log_block = f"```\n{log_content}\n```"
            full_msg = header + log_block
            if len(full_msg) > 4096:
                log_block = f"```\n{log_content[-(4096 - len(header) - 10):]}\n```"
                full_msg = header + log_block
            bot.send_message(chat_id_for_reply, full_msg, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Error reading/sending log {log_path}: {e}", exc_info=True)
            bot.send_message(chat_id_for_reply, f"❌ Error reading log for `{file_name}`.")
    except (ValueError, IndexError) as e:
        logger.error(f"Error parsing logs callback '{call.data}': {e}")
        safe_answer_callback(call.id, "Error: Invalid logs command.", show_alert=True)
    except Exception as e:
        logger.error(f"Error in logs_bot_callback for '{call.data}': {e}", exc_info=True)
        safe_answer_callback(call.id, "Error fetching logs.", show_alert=True)

def speed_callback(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    
    # Check if user is banned
    if is_user_banned(user_id):
        safe_answer_callback(call.id, "❌ You are banned from using this bot.", show_alert=True)
        return
    
    # Check mandatory subscription first
    is_subscribed, not_joined = check_mandatory_subscription(user_id)
    if not is_subscribed and user_id not in admin_ids:
        subscription_message, markup = create_subscription_check_message(not_joined)
        safe_answer_callback(call.id)
        try:
            bot.edit_message_text(subscription_message, chat_id, call.message.message_id, reply_markup=markup, parse_mode='Markdown')
        except:
            bot.send_message(chat_id, subscription_message, reply_markup=markup, parse_mode='Markdown')
        return
        
    start_cb_ping_time = time.time()
    try:
        bot.edit_message_text("🏃 Testing speed...", chat_id, call.message.message_id)
        response_time = round((time.time() - start_cb_ping_time) * 1000, 2)
        status = "🔓 Unlocked" if not bot_locked else "🔒 Locked"
        if user_id == OWNER_ID: user_level = "👑 Owner"
        elif user_id in admin_ids: user_level = "🛡️ Admin"
        elif user_id in user_subscriptions and user_subscriptions[user_id].get('expiry', datetime.min) > datetime.now(): user_level = "⭐ Premium"
        else: user_level = "🆓 Free User"
        speed_msg = (f"⚡ Bot Speed & Status:\n\n⏱️ Latency : {response_time} ms\n"
                     f"🚦 Bot Status: {status}\n"
                     f"👤 Your Level: {user_level}")
        safe_answer_callback(call.id) 
        bot.edit_message_text(speed_msg, chat_id, call.message.message_id, reply_markup=create_main_menu_inline(user_id))
    except Exception as e:
         logger.error(f"Error during speed test (cb): {e}", exc_info=True)
         safe_answer_callback(call.id, "Error in speed test.", show_alert=True)
         try: bot.edit_message_text("〽️ Main Menu", chat_id, call.message.message_id, reply_markup=create_main_menu_inline(user_id))
         except Exception: pass

def back_to_main_callback(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    
    # Check if user is banned
    if is_user_banned(user_id):
        safe_answer_callback(call.id, "❌ You are banned from using this bot.", show_alert=True)
        return
    
    # Check mandatory subscription first
    is_subscribed, not_joined = check_mandatory_subscription(user_id)
    if not is_subscribed and user_id not in admin_ids:
        subscription_message, markup = create_subscription_check_message(not_joined)
        safe_answer_callback(call.id)
        try:
            bot.edit_message_text(subscription_message, chat_id, call.message.message_id, reply_markup=markup, parse_mode='Markdown')
        except:
            bot.send_message(chat_id, subscription_message, reply_markup=markup, parse_mode='Markdown')
        return
        
    file_limit = get_user_file_limit(user_id)
    current_files = get_user_file_count(user_id)
    limit_str = str(file_limit) if file_limit != float('inf') else "∞ Unlimited"
    expiry_info = ""
    if user_id == OWNER_ID:
        user_status = "👑 Owner"; status_bar = "🟡🟡🟡🟡🟡"
    elif user_id in admin_ids:
        user_status = "🛡️ Admin"; status_bar = "🔵🔵🔵🔵⬜"
    elif user_id in user_subscriptions:
        expiry_date = user_subscriptions[user_id].get('expiry')
        if expiry_date and expiry_date > datetime.now():
            user_status = "⭐ Premium"; status_bar = "🟣🟣🟣⬜⬜"
            days_left = (expiry_date - datetime.now()).days
            expiry_info = f"\n  └ ⏳ Expires in: `{days_left} days`"
        else:
            user_status = "🆓 Free (Expired)"; status_bar = "🟢⬜⬜⬜⬜"
    else:
        user_status = "🆓 Free User"; status_bar = "🟢⬜⬜⬜⬜"
    now_ist = datetime.now(IST).strftime("%d %b %Y • %I:%M:%S %p")
    user_name = call.from_user.first_name or "User"
    main_menu_text = (
        "╔══════════════════════════╗\n"
        f"║  👋 WELCOME, {user_name[:10]:<10}  ║\n"
        "╚══════════════════════════╝\n\n"
        "👤 *YOUR PROFILE*\n"
        f"├ 🆔 ID      : `{user_id}`\n"
        f"├ 🔰 Status  : {user_status}\n"
        f"├ 📊 Level   : {status_bar}{expiry_info}\n"
        f"└ 📁 Files   : `{current_files} / {limit_str}`\n\n"
        f"🕐 `{now_ist} IST`\n\n"
        "👇 *Use the buttons below!*"
    )
    try:
        safe_answer_callback(call.id)
        bot.edit_message_text(main_menu_text, chat_id, call.message.message_id,
                              reply_markup=create_main_menu_inline(user_id), parse_mode='Markdown')
    except telebot.apihelper.ApiTelegramException as e:
         if "message is not modified" in str(e): logger.warning("Msg not modified (back_to_main).")
         else: logger.error(f"API error on back_to_main: {e}")
    except Exception as e: logger.error(f"Error handling back_to_main: {e}", exc_info=True)

# --- Admin Callback Implementations (for Inline Buttons) ---
def subscription_management_callback(call):
    safe_answer_callback(call.id)
    try:
        bot.edit_message_text("💳 Subscription Management\nSelect action:",
                              call.message.chat.id, call.message.message_id, reply_markup=create_subscription_menu())
    except Exception as e: logger.error(f"Error showing sub menu: {e}")

def stats_callback(call): # Called by user and admin
    safe_answer_callback(call.id)
    _logic_statistics(call.message)
    try:
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                      reply_markup=create_main_menu_inline(call.from_user.id))
    except telebot.apihelper.ApiTelegramException as e:
        if "message is not modified" not in str(e):
            logger.error(f"Error updating menu after stats_callback: {e}")
    except Exception as e:
        logger.error(f"Error updating menu after stats_callback: {e}")

def lock_bot_callback(call):
    global bot_locked; bot_locked = True
    logger.warning(f"Bot locked by Admin {call.from_user.id}")
    safe_answer_callback(call.id, "🔒 ʙᴏᴛ ᴄᴏɴᴛʀᴏʟ ʟᴏᴄᴋᴇᴅ • ᴀᴄᴄᴇss ʀᴇsᴛʀɪᴄᴛᴇᴅ")
    try:
        bot.send_message(call.message.chat.id, "╔══════════════════════════════╗\n║   🔒 ʙᴏᴛ ᴄᴏɴᴛʀᴏʟ ʟᴏᴄᴋᴇᴅ   ║\n╚══════════════════════════════╝\n\n⛔ ʟᴏᴄᴋᴇᴅ sᴛᴀᴛᴜs\n\n🔐 ᴀᴅᴍɪɴ ʟᴏᴄᴋ ᴀᴄᴛɪᴠᴇ\n⚠️ ᴜsᴇʀ ᴀᴄᴄᴇss ʀᴇsᴛʀɪᴄᴛᴇᴅ")
    except Exception as e: logger.error(f"Error sending lock confirmation: {e}")
    try: bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=create_main_menu_inline(call.from_user.id))
    except Exception as e: logger.error(f"Error updating menu (lock): {e}")

def unlock_bot_callback(call):
    global bot_locked; bot_locked = False
    logger.warning(f"Bot unlocked by Admin {call.from_user.id}")
    safe_answer_callback(call.id, "🔓 ʙᴏᴛ ᴄᴏɴᴛʀᴏʟ ᴜɴʟᴏᴄᴋᴇᴅ • ᴀᴄᴄᴇss ʀᴇsᴛᴏʀᴇᴅ")
    try:
        bot.send_message(call.message.chat.id, "╔══════════════════════════════╗\n║  🔓 ʙᴏᴛ ᴄᴏɴᴛʀᴏʟ ᴜɴʟᴏᴄᴋᴇᴅ  ║\n╚══════════════════════════════╝\n\n✅ ᴜɴʟᴏᴄᴋᴇᴅ sᴛᴀᴛᴜs\n\n🟢 ᴀᴅᴍɪɴ ʟᴏᴄᴋ ʀᴇᴍᴏᴠᴇᴅ\n🚀 ᴜsᴇʀ ᴀᴄᴄᴇss ʀᴇsᴛᴏʀᴇᴅ")
    except Exception as e: logger.error(f"Error sending unlock confirmation: {e}")
    try: bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=create_main_menu_inline(call.from_user.id))
    except Exception as e: logger.error(f"Error updating menu (unlock): {e}")

def run_all_scripts_callback(call): # Added
    _logic_run_all_scripts(call) # Pass the call object

def stop_all_scripts_callback(call):
    _logic_stop_all_scripts(call)

def broadcast_init_callback(call):
    safe_answer_callback(call.id)
    msg = bot.send_message(call.message.chat.id, "📢 Send message to broadcast.\n/cancel to abort.")
    bot.register_next_step_handler(msg, process_broadcast_message)

def process_broadcast_message(message):
    user_id = message.from_user.id
    if user_id not in admin_ids: bot.reply_to(message, "⚠️ Not authorized."); return
    if message.text and message.text.lower() == '/cancel': bot.reply_to(message, "╔══════════════════════════╗\n║   📢 BROADCAST CANCELLED ║\n╚══════════════════════════╝\n\n  ❌ Broadcast cancelled."); return

    broadcast_content = message.text # Can also handle photos, videos etc. if message.content_type is checked
    if not broadcast_content and not (message.photo or message.video or message.document or message.sticker or message.voice or message.audio): # If no text and no other media
         bot.reply_to(message, "⚠️ Cannot broadcast empty message. Send text or media, or /cancel.")
         msg = bot.send_message(message.chat.id, "📢 Send broadcast message or /cancel.")
         bot.register_next_step_handler(msg, process_broadcast_message)
         return

    target_count = len(active_users)
    markup = types.InlineKeyboardMarkup()
    markup.row(_sc_inline_button("✅ Confirm & Send", callback_data=f"confirm_broadcast_{message.message_id}"),
               _sc_inline_button("❌ Cancel", callback_data="cancel_broadcast"))

    preview_text = broadcast_content[:1000].strip() if broadcast_content else "(Media message)"
    bot.reply_to(message, f"⚠️ Confirm Broadcast:\n\n```\n{preview_text}\n```\n" 
                          f"To **{target_count}** users. Sure?", reply_markup=markup, parse_mode='Markdown')

# --- Admin File Management Callbacks (Owner/Admin can manage any user's files) ---
def browse_users_files_callback(call):
    users_with_files = [uid for uid, files in user_files.items() if files]
    if not users_with_files:
        safe_answer_callback(call.id, "No users with files.", show_alert=True)
        return
    safe_answer_callback(call.id)
    markup = types.InlineKeyboardMarkup(row_width=2)
    for uid in sorted(users_with_files)[:30]:
        file_count = len(user_files.get(uid, []))
        markup.add(_sc_inline_button(f"👤 {uid} ({file_count} files)", callback_data=f'admin_view_user_files_{uid}'))
    markup.add(_sc_inline_button("🔙 Back", callback_data='user_management'))
    bot.edit_message_text("🗂️ ╔══ 𝗦𝗘𝗟𝗘𝗖𝗧 𝗨𝗦𝗘𝗥 ══╗\n📁 **Choose a user to manage their files:**\n╚══════════════════╝", call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode='Markdown')

def admin_view_user_files_callback(call):
    user_id = int(call.data.split('_')[-1])
    user_files_list = user_files.get(user_id, [])
    if not user_files_list:
        safe_answer_callback(call.id, f"No files for user {user_id}", show_alert=True)
        return
    safe_answer_callback(call.id)
    markup = types.InlineKeyboardMarkup(row_width=1)
    for file_name, file_type in sorted(user_files_list):
        is_running = is_bot_running(user_id, file_name)
        status_icon = "🟢" if is_running else "🔴"
        markup.add(_sc_inline_button(f"{status_icon} {file_name} ({file_type})", callback_data=f'admin_control_file_{user_id}_{file_name}'))
    markup.add(_sc_inline_button("🔙 Back", callback_data='browse_users_files'))
    bot.edit_message_text(f"╔══════════════════════════╗\n║       📂 USER FILES      ║\n╚══════════════════════════╝\n\n  👤 User : `{user_id}`", call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode='Markdown')

def admin_control_file_callback(call):
    parts = call.data.split('_')
    user_id = int(parts[3])
    file_name = '_'.join(parts[4:])
    
    is_running = is_bot_running(user_id, file_name)
    file_type = next((f[1] for f in user_files.get(user_id, []) if f[0] == file_name), '?')
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    if is_running:
        markup.row(
            _sc_inline_button("🔴 Stop", callback_data=f'admin_stop_{user_id}_{file_name}'),
            _sc_inline_button("🔄 Restart", callback_data=f'admin_restart_{user_id}_{file_name}')
        )
        markup.row(
            _sc_inline_button("🗑️ Delete", callback_data=f'admin_delete_{user_id}_{file_name}'),
            _sc_inline_button("📜 Logs", callback_data=f'admin_logs_{user_id}_{file_name}')
        )
    else:
        markup.row(
            _sc_inline_button("🟢 Start", callback_data=f'admin_start_{user_id}_{file_name}'),
            _sc_inline_button("🗑️ Delete", callback_data=f'admin_delete_{user_id}_{file_name}')
        )
        markup.row(
            _sc_inline_button("📜 Logs", callback_data=f'admin_logs_{user_id}_{file_name}')
        )
    markup.add(_sc_inline_button("🔙 Back", callback_data=f'admin_view_user_files_{user_id}'))
    
    safe_answer_callback(call.id)
    bot.edit_message_text(
        f"╔══════════════════════════╗\n║    ⚙️ ADMIN CONTROLS     ║\n╚══════════════════════════╝\n\n  👤 User : `{user_id}`\n  📁 File : `{file_name}` ({file_type})\n  {'🟢 Status : Running' if is_running else '🔴 Status : Stopped'}",
        call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode='Markdown')

def admin_start_file_callback(call):
    parts = call.data.split('_')
    user_id = int(parts[2])
    file_name = '_'.join(parts[3:])
    
    file_info = next((f for f in user_files.get(user_id, []) if f[0] == file_name), None)
    if not file_info:
        safe_answer_callback(call.id, "File not found.", show_alert=True)
        return
    
    if is_bot_running(user_id, file_name):
        safe_answer_callback(call.id, "Already running.", show_alert=True)
        return
    
    file_type = file_info[1]
    user_folder = get_user_folder(user_id)
    file_path = os.path.join(user_folder, file_name)
    
    if not os.path.exists(file_path):
        safe_answer_callback(call.id, "File missing.", show_alert=True)
        return
    
    safe_answer_callback(call.id, f"Starting {file_name}...")
    
    if file_type == 'py':
        threading.Thread(target=run_script, args=(file_path, user_id, user_folder, file_name, call.message)).start()
    else:
        threading.Thread(target=run_js_script, args=(file_path, user_id, user_folder, file_name, call.message)).start()
    
    time.sleep(1.5)
    # Refresh the control panel
    admin_control_file_callback(call)

def admin_stop_file_callback(call):
    parts = call.data.split('_')
    user_id = int(parts[2])
    file_name = '_'.join(parts[3:])
    
    script_key = f"{user_id}_{file_name}"
    
    if script_key in bot_scripts:
        kill_process_tree(bot_scripts[script_key])
        del bot_scripts[script_key]
        safe_answer_callback(call.id, f"✅ Stopped {file_name}")
    else:
        safe_answer_callback(call.id, "Not running.", show_alert=True)
    
    time.sleep(0.5)
    admin_control_file_callback(call)

def admin_restart_file_callback(call):
    parts = call.data.split('_')
    user_id = int(parts[2])
    file_name = '_'.join(parts[3:])
    
    script_key = f"{user_id}_{file_name}"
    
    if script_key in bot_scripts:
        kill_process_tree(bot_scripts[script_key])
        del bot_scripts[script_key]
        time.sleep(1)
    
    # Start again
    admin_start_file_callback(call)

def admin_delete_file_callback(call):
    parts = call.data.split('_')
    user_id = int(parts[2])
    file_name = '_'.join(parts[3:])
    
    script_key = f"{user_id}_{file_name}"
    
    if script_key in bot_scripts:
        kill_process_tree(bot_scripts[script_key])
        del bot_scripts[script_key]
    
    user_folder = get_user_folder(user_id)
    file_path = os.path.join(user_folder, file_name)
    log_path = os.path.join(user_folder, f"{os.path.splitext(file_name)[0]}.log")
    
    if os.path.exists(file_path):
        os.remove(file_path)
    if os.path.exists(log_path):
        os.remove(log_path)
    
    remove_user_file_db(user_id, file_name)
    safe_answer_callback(call.id, f"✅ Deleted {file_name}")
    bot.edit_message_text(f"🗑️ Deleted `{file_name}` for user `{user_id}`", call.message.chat.id, call.message.message_id, parse_mode='Markdown')

def admin_logs_file_callback(call):
    parts = call.data.split('_')
    user_id = int(parts[2])
    file_name = '_'.join(parts[3:])
    
    user_folder = get_user_folder(user_id)
    log_path = os.path.join(user_folder, f"{os.path.splitext(file_name)[0]}.log")
    
    if not os.path.exists(log_path):
        safe_answer_callback(call.id, "No logs.", show_alert=True)
        return
    
    safe_answer_callback(call.id)
    
    try:
        file_size = os.path.getsize(log_path)
        with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
            log_content = f.read()[-3000:]
        if not log_content.strip():
            log_content = "(Log empty)"
        is_running = is_bot_running(user_id, file_name)
        status_dot = "🟢 Running" if is_running else "🔴 Stopped"
        user_files_list = user_files.get(user_id, [])
        file_type = next((f[1] for f in user_files_list if f[0] == file_name), '?')
        type_icon = "🐍" if file_type == "py" else "🟨" if file_type == "js" else "📦"
        now_ist = datetime.now(IST).strftime("%d %b %Y • %I:%M:%S %p")
        log_size_kb = round(file_size / 1024, 1) if file_size > 0 else 0
        header = (
            "╔══════════════════════════╗\n"
            "║  📜 ADMIN VIEW LOGS 📜   ║\n"
            "╚══════════════════════════╝\n\n"
            f"📄 *File*   : `{file_name}`\n"
            f"{type_icon} *Type*   : `{file_type.upper()}`\n"
            f"👤 *Owner*  : `{user_id}`\n"
            f"📡 *Status* : {status_dot}\n"
            f"📦 *Size*   : `{log_size_kb} KB`\n"
            f"🕐 *Time*   : `{now_ist} IST`\n"
            "─────────────────────────\n"
        )
        log_block = f"```\n{log_content}\n```"
        full_msg = header + log_block
        if len(full_msg) > 4096:
            log_block = f"```\n{log_content[-(4096 - len(header) - 10):]}\n```"
            full_msg = header + log_block
        bot.send_message(call.message.chat.id, full_msg, parse_mode='Markdown')
    except Exception as e:
        bot.send_message(call.message.chat.id, f"❌ Error reading log: `{str(e)}`", parse_mode='Markdown')




def handle_confirm_broadcast(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    if user_id not in admin_ids: safe_answer_callback(call.id, "⚠️ Admin only.", show_alert=True); return
    try:
        original_message = call.message.reply_to_message
        if not original_message: raise ValueError("Could not retrieve original message.")

        # Check content type and get content
        broadcast_text = None
        broadcast_photo_id = None
        broadcast_video_id = None
        # Add other types as needed: document, sticker, voice, audio

        if original_message.text:
            broadcast_text = original_message.text
        elif original_message.photo:
            broadcast_photo_id = original_message.photo[-1].file_id # Get highest quality
        elif original_message.video:
            broadcast_video_id = original_message.video.file_id
        # Add more elif for other content types
        else:
            raise ValueError("Message has no text or supported media for broadcast.")

        safe_answer_callback(call.id, "🚀 Starting broadcast...")
        bot.edit_message_text(f"📢 Broadcasting to {len(active_users)} users...",
                              chat_id, call.message.message_id, reply_markup=None)
        # Pass all potential content types to execute_broadcast
        thread = threading.Thread(target=execute_broadcast, args=(
            broadcast_text, broadcast_photo_id, broadcast_video_id, 
            original_message.caption if (broadcast_photo_id or broadcast_video_id) else None, # Pass caption
            chat_id))
        thread.start()
    except ValueError as ve: 
        logger.error(f"Error retrieving msg for broadcast confirm: {ve}")
        bot.edit_message_text(f"❌ Error starting broadcast: {ve}", chat_id, call.message.message_id, reply_markup=None)
    except Exception as e:
        logger.error(f"Error in handle_confirm_broadcast: {e}", exc_info=True)
        bot.edit_message_text("❌ Unexpected error during broadcast confirm.", chat_id, call.message.message_id, reply_markup=None)

def handle_cancel_broadcast(call):
    safe_answer_callback(call.id, "╔══════════════════════════╗\n║   📢 BROADCAST CANCELLED ║\n╚══════════════════════════╝\n\n  ❌ Broadcast cancelled.")
    bot.delete_message(call.message.chat.id, call.message.message_id)
    # Optionally delete the original message too if call.message.reply_to_message exists
    if call.message.reply_to_message:
        try: bot.delete_message(call.message.chat.id, call.message.reply_to_message.message_id)
        except: pass

def execute_broadcast(broadcast_text, photo_id, video_id, caption, admin_chat_id):
    sent_count = 0; failed_count = 0; blocked_count = 0
    start_exec_time = time.time() 
    # Broadcast is intentionally independent of Subscription Mode.
    # Every registered/active user is a recipient, subscribed or not.
    users_to_broadcast = list(active_users)
    total_users = len(users_to_broadcast)
    logger.info(f"Executing ALL-USER broadcast to {total_users} registered users (subscription-independent).")
    batch_size = 25; delay_batches = 1.5

    for i, user_id_bc in enumerate(users_to_broadcast): # Renamed
        try:
            if broadcast_text:
                for _chunk in _split_telegram_text(broadcast_text):
                    bot.send_message(user_id_bc, _chunk, _broadcast_raw=True)
            elif photo_id:
                bot.send_photo(user_id_bc, photo_id, caption=caption, parse_mode='Markdown' if caption else None)
            elif video_id:
                bot.send_video(user_id_bc, video_id, caption=caption, parse_mode='Markdown' if caption else None)
            # Add other send methods for other types
            sent_count += 1
        except telebot.apihelper.ApiTelegramException as e:
            err_desc = str(e).lower()
            if any(s in err_desc for s in ["bot was blocked", "user is deactivated", "chat not found", "kicked from", "restricted"]): 
                logger.warning(f"Broadcast failed to {user_id_bc}: User blocked/inactive.")
                blocked_count += 1
            elif "flood control" in err_desc or "too many requests" in err_desc:
                retry_after = 5; match = re.search(r"retry after (\d+)", err_desc)
                if match: retry_after = int(match.group(1)) + 1 
                logger.warning(f"Flood control. Sleeping {retry_after}s...")
                time.sleep(retry_after)
                try: # Retry once
                    if broadcast_text:
                        for _chunk in _split_telegram_text(broadcast_text):
                            bot.send_message(user_id_bc, _chunk, _broadcast_raw=True)
                    elif photo_id: bot.send_photo(user_id_bc, photo_id, caption=caption, parse_mode='Markdown' if caption else None)
                    elif video_id: bot.send_video(user_id_bc, video_id, caption=caption, parse_mode='Markdown' if caption else None)
                    sent_count += 1
                except Exception as e_retry: logger.error(f"Broadcast retry failed to {user_id_bc}: {e_retry}"); failed_count +=1
            else: logger.error(f"Broadcast failed to {user_id_bc}: {e}"); failed_count += 1
        except Exception as e: logger.error(f"Unexpected error broadcasting to {user_id_bc}: {e}"); failed_count += 1

        if (i + 1) % batch_size == 0 and i < total_users - 1:
            logger.info(f"Broadcast batch {i//batch_size + 1} sent. Sleeping {delay_batches}s...")
            time.sleep(delay_batches)
        elif i % 5 == 0: time.sleep(0.2) 

    duration = round(time.time() - start_exec_time, 2)
    result_msg = (f"📢 Broadcast Complete!\n\n✅ Sent: {sent_count}\n❌ Failed: {failed_count}\n"
                  f"🚫 Blocked/Inactive: {blocked_count}\n👥 Targets: {total_users}\n⏱️ Duration: {duration}s")
    logger.info(result_msg)
    try: bot.send_message(admin_chat_id, result_msg)
    except Exception as e: logger.error(f"Failed to send broadcast result to admin {admin_chat_id}: {e}")

def admin_panel_callback(call):
    safe_answer_callback(call.id)
    try:
        bot.edit_message_text("╔══════════════════════════╗\n║      👑 ADMIN PANEL      ║\n╚══════════════════════════╝\n\n  🛠️ Manage administrators using the buttons below.",
                              call.message.chat.id, call.message.message_id, reply_markup=create_admin_panel())
    except Exception as e: logger.error(f"Error showing admin panel: {e}")

def add_admin_init_callback(call):
    safe_answer_callback(call.id)
    msg = bot.send_message(call.message.chat.id, "👑 Enter User ID to promote to Admin.\n/cancel to abort.")
    bot.register_next_step_handler(msg, process_add_admin_id)

def process_add_admin_id(message):
    owner_id_check = message.from_user.id 
    if owner_id_check != OWNER_ID: bot.reply_to(message, "⚠️ Owner only."); return
    if message.text.lower() == '/cancel': bot.reply_to(message, "╔══════════════════════════╗\n║   👑 ADMIN ADD CANCELLED ║\n╚══════════════════════════╝\n\n  ❌ Admin promotion cancelled."); return
    try:
        new_admin_id = int(message.text.strip())
        if new_admin_id <= 0: raise ValueError("ID must be positive")
        if new_admin_id == OWNER_ID: bot.reply_to(message, "⚠️ Owner is already Owner."); return
        if new_admin_id in admin_ids: bot.reply_to(message, f"⚠️ User `{new_admin_id}` already Admin."); return
        add_admin_db(new_admin_id, owner_id_check) 
        logger.warning(f"Admin {new_admin_id} added by Owner {owner_id_check}.")
        bot.reply_to(message, f"✅ User `{new_admin_id}` promoted to Admin.")
        try: bot.send_message(new_admin_id, "🎉 Congrats! You are now an Admin.")
        except Exception as e: logger.error(f"Failed to notify new admin {new_admin_id}: {e}")
    except ValueError:
        bot.reply_to(message, "⚠️ Invalid ID. Send numerical ID or /cancel.")
        msg = bot.send_message(message.chat.id, "👑 Enter User ID to promote or /cancel.")
        bot.register_next_step_handler(msg, process_add_admin_id)
    except Exception as e: logger.error(f"Error processing add admin: {e}", exc_info=True); bot.reply_to(message, "Error.")

def remove_admin_init_callback(call):
    safe_answer_callback(call.id)
    msg = bot.send_message(call.message.chat.id, "👑 Enter User ID of Admin to remove.\n/cancel to abort.")
    bot.register_next_step_handler(msg, process_remove_admin_id)

def process_remove_admin_id(message):
    owner_id_check = message.from_user.id
    if owner_id_check != OWNER_ID: bot.reply_to(message, "⚠️ Owner only."); return
    if message.text.lower() == '/cancel': bot.reply_to(message, "╔══════════════════════════╗\n║ 👑 ADMIN REMOVE CANCELLED║\n╚══════════════════════════╝\n\n  ❌ Admin removal cancelled."); return
    try:
        admin_id_remove = int(message.text.strip()) # Renamed
        if admin_id_remove <= 0: raise ValueError("ID must be positive")
        if admin_id_remove == OWNER_ID: bot.reply_to(message, "⚠️ Owner cannot remove self."); return
        if admin_id_remove not in admin_ids: bot.reply_to(message, f"⚠️ User `{admin_id_remove}` not Admin."); return
        if remove_admin_db(admin_id_remove): 
            logger.warning(f"Admin {admin_id_remove} removed by Owner {owner_id_check}.")
            bot.reply_to(message, f"✅ Admin `{admin_id_remove}` removed.")
            try: bot.send_message(admin_id_remove, "ℹ️ You are no longer an Admin.")
            except Exception as e: logger.error(f"Failed to notify removed admin {admin_id_remove}: {e}")
        else: bot.reply_to(message, f"❌ Failed to remove admin `{admin_id_remove}`. Check logs.")
    except ValueError:
        bot.reply_to(message, "⚠️ Invalid ID. Send numerical ID or /cancel.")
        msg = bot.send_message(message.chat.id, "👑 Enter Admin ID to remove or /cancel.")
        bot.register_next_step_handler(msg, process_remove_admin_id)
    except Exception as e: logger.error(f"Error processing remove admin: {e}", exc_info=True); bot.reply_to(message, "Error.")

def list_admins_callback(call):
    safe_answer_callback(call.id)
    try:
        admin_list_str = "\n".join(f"- `{aid}` {'(Owner)' if aid == OWNER_ID else ''}" for aid in sorted(list(admin_ids)))
        if not admin_list_str: admin_list_str = "(No Owner/Admins configured!)"
        bot.edit_message_text(f"👑 Current Admins:\n\n{admin_list_str}", call.message.chat.id,
                              call.message.message_id, reply_markup=create_admin_panel(), parse_mode='Markdown')
    except Exception as e: logger.error(f"Error listing admins: {e}")

def add_subscription_init_callback(call):
    safe_answer_callback(call.id)
    msg = bot.send_message(call.message.chat.id, "💳 ╔══ 𝗔𝗗𝗗 𝗦𝗨𝗕𝗦𝗖𝗥𝗜𝗣𝗧𝗜𝗢𝗡 ══╗\n📝 Enter **User ID & days**\n💡 Example: `12345678 30`\n╚══════════════════╝\n🔴 /cancel — to abort", parse_mode='Markdown')
    bot.register_next_step_handler(msg, process_add_subscription_details)

def process_add_subscription_details(message):
    admin_id_check = message.from_user.id 
    if admin_id_check not in admin_ids: bot.reply_to(message, "⚠️ Not authorized."); return
    if message.text.lower() == '/cancel': bot.reply_to(message, "╔══ 𝗔𝗖𝗧𝗜𝗢𝗡 𝗖𝗔𝗡𝗖𝗘𝗟𝗟𝗘𝗗 ══╗\n🚫 ╔══════════════════════════╗\n║   💳 SUB ADD CANCELLED   ║\n╚══════════════════════════╝\n\n  ❌ Subscription addition cancelled.\n╚══════════════════╝", parse_mode='Markdown'); return
    try:
        parts = message.text.split();
        if len(parts) != 2: raise ValueError("Incorrect format")
        sub_user_id = int(parts[0].strip()); days = int(parts[1].strip())
        if sub_user_id <= 0 or days <= 0: raise ValueError("User ID/days must be positive")

        current_expiry = user_subscriptions.get(sub_user_id, {}).get('expiry')
        start_date_new_sub = datetime.now() # Renamed
        if current_expiry and current_expiry > start_date_new_sub: start_date_new_sub = current_expiry
        new_expiry = start_date_new_sub + timedelta(days=days)
        save_subscription(sub_user_id, new_expiry)

        logger.info(f"Sub for {sub_user_id} by admin {admin_id_check}. Expiry: {new_expiry:%Y-%m-%d}")
        bot.reply_to(message, f"✅ Sub for `{sub_user_id}` by {days} days.\nNew expiry: {new_expiry:%Y-%m-%d}")
        try: bot.send_message(sub_user_id, f"🎉 Sub activated/extended by {days} days! Expires: {new_expiry:%Y-%m-%d}.")
        except Exception as e: logger.error(f"Failed to notify {sub_user_id} of new sub: {e}")
    except ValueError as e:
        bot.reply_to(message, f"⚠️ Invalid: {e}. Format: `ID days` or /cancel.")
        msg = bot.send_message(message.chat.id, "💳 Enter User ID & days, or /cancel.")
        bot.register_next_step_handler(msg, process_add_subscription_details)
    except Exception as e: logger.error(f"Error processing add sub: {e}", exc_info=True); bot.reply_to(message, "Error.")

def remove_subscription_init_callback(call):
    safe_answer_callback(call.id)
    msg = bot.send_message(call.message.chat.id, "❌💳 ╔══ 𝗥𝗘𝗠𝗢𝗩𝗘 𝗦𝗨𝗕𝗦𝗖𝗥𝗜𝗣𝗧𝗜𝗢𝗡 ══╗\n📝 Enter **User ID** to remove subscription\n╚══════════════════╝\n🔴 /cancel — to abort", parse_mode='Markdown')
    bot.register_next_step_handler(msg, process_remove_subscription_id)

def process_remove_subscription_id(message):
    admin_id_check = message.from_user.id
    if admin_id_check not in admin_ids: bot.reply_to(message, "⚠️ Not authorized."); return
    if message.text.lower() == '/cancel': bot.reply_to(message, "╔══ 𝗔𝗖𝗧𝗜𝗢𝗡 𝗖𝗔𝗡𝗖𝗘𝗟𝗟𝗘𝗗 ══╗\n🚫 ╔══════════════════════════╗\n║  💳 SUB REMOVE CANCELLED ║\n╚══════════════════════════╝\n\n  ❌ Subscription removal cancelled.\n╚══════════════════╝", parse_mode='Markdown'); return
    try:
        sub_user_id_remove = int(message.text.strip()) # Renamed
        if sub_user_id_remove <= 0: raise ValueError("ID must be positive")
        if sub_user_id_remove not in user_subscriptions:
            bot.reply_to(message, f"⚠️ User `{sub_user_id_remove}` no active sub in memory."); return
        remove_subscription_db(sub_user_id_remove) 
        logger.warning(f"Sub removed for {sub_user_id_remove} by admin {admin_id_check}.")
        bot.reply_to(message, f"✅ Sub for `{sub_user_id_remove}` removed.")
        try: bot.send_message(sub_user_id_remove, "ℹ️ Your subscription removed by admin.")
        except Exception as e: logger.error(f"Failed to notify {sub_user_id_remove} of sub removal: {e}")
    except ValueError:
        bot.reply_to(message, "⚠️ Invalid ID. Send numerical ID or /cancel.")
        msg = bot.send_message(message.chat.id, "💳 Enter User ID to remove sub from, or /cancel.")
        bot.register_next_step_handler(msg, process_remove_subscription_id)
    except Exception as e: logger.error(f"Error processing remove sub: {e}", exc_info=True); bot.reply_to(message, "Error.")

def check_subscription_init_callback(call):
    safe_answer_callback(call.id)
    msg = bot.send_message(call.message.chat.id, "🔍💳 ╔══ 𝗖𝗛𝗘𝗖𝗞 𝗦𝗨𝗕𝗦𝗖𝗥𝗜𝗣𝗧𝗜𝗢𝗡 ══╗\n📝 Enter **User ID** to check subscription\n╚══════════════════╝\n🔴 /cancel — to abort", parse_mode='Markdown')
    bot.register_next_step_handler(msg, process_check_subscription_id)

def process_check_subscription_id(message):
    admin_id_check = message.from_user.id
    if admin_id_check not in admin_ids: bot.reply_to(message, "⚠️ Not authorized."); return
    if message.text.lower() == '/cancel': bot.reply_to(message, "╔══ 𝗔𝗖𝗧𝗜𝗢𝗡 𝗖𝗔𝗡𝗖𝗘𝗟𝗟𝗘𝗗 ══╗\n🚫 Sub check cancelled.\n╚══════════════════╝", parse_mode='Markdown'); return
    try:
        sub_user_id_check = int(message.text.strip()) # Renamed
        if sub_user_id_check <= 0: raise ValueError("ID must be positive")
        if sub_user_id_check in user_subscriptions:
            expiry_dt = user_subscriptions[sub_user_id_check].get('expiry')
            if expiry_dt:
                if expiry_dt > datetime.now():
                    days_left = (expiry_dt - datetime.now()).days
                    bot.reply_to(message, f"✅ User `{sub_user_id_check}` active sub.\nExpires: {expiry_dt:%Y-%m-%d %H:%M:%S} ({days_left} days left).")
                else:
                    bot.reply_to(message, f"⚠️ User `{sub_user_id_check}` expired sub (On: {expiry_dt:%Y-%m-%d %H:%M:%S}).")
                    remove_subscription_db(sub_user_id_check) # Clean up
            else: bot.reply_to(message, f"⚠️ User `{sub_user_id_check}` in sub list, but expiry missing. Re-add if needed.")
        else: bot.reply_to(message, f"ℹ️ User `{sub_user_id_check}` no active sub record.")
    except ValueError:
        bot.reply_to(message, "⚠️ Invalid ID. Send numerical ID or /cancel.")
        msg = bot.send_message(message.chat.id, "💳 Enter User ID to check, or /cancel.")
        bot.register_next_step_handler(msg, process_check_subscription_id)
    except Exception as e: logger.error(f"Error processing check sub: {e}", exc_info=True); bot.reply_to(message, "Error.")

# --- User Management Callbacks ---
def user_management_callback(call):
    safe_answer_callback(call.id)
    try:
        bot.edit_message_text("╔══════════════════════════╗\n║   👥 USER MANAGEMENT 👥   ║\n╚══════════════════════════╝\n\n  📌 Select an action below:", call.message.chat.id, 
                              call.message.message_id, reply_markup=create_user_management_menu())
    except Exception as e: logger.error(f"Error showing user management menu: {e}")

def ban_user_callback(call):
    safe_answer_callback(call.id)
    msg = bot.send_message(call.message.chat.id, "🚫 ╔══ 𝗕𝗔𝗡 𝗨𝗦𝗘𝗥 ══╗\n📝 Enter **User ID & reason**\n💡 Example: `12345678 Spamming`\n╚══════════════════╝\n🔴 /cancel — to stop", parse_mode='Markdown')
    bot.register_next_step_handler(msg, process_ban_user)

def process_ban_user(message):
    admin_id = message.from_user.id
    if admin_id not in admin_ids: bot.reply_to(message, "⚠️ Not authorized."); return
    
    if message.text.lower() == '/cancel':
        bot.reply_to(message, "╔══ 𝗔𝗖𝗧𝗜𝗢𝗡 𝗖𝗔𝗡𝗖𝗘𝗟𝗟𝗘𝗗 ══╗\n🚫 ╔══════════════════════════╗\n║      🚫 BAN CANCELLED    ║\n╚══════════════════════════╝\n\n  ❌ Ban cancelled.\n╚══════════════════╝", parse_mode='Markdown')
        return
    
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "⚠️ Format: `user_id reason`\nExample: `12345678 Spamming`")
            return
        
        user_id = int(parts[0])
        reason = ' '.join(parts[1:])
        
        if user_id <= 0: raise ValueError("ID must be positive")
        if user_id == OWNER_ID: bot.reply_to(message, "⚠️ Cannot ban owner."); return
        if user_id in admin_ids: bot.reply_to(message, "⚠️ Cannot ban admin."); return
        
        if ban_user_db(user_id, reason, admin_id):
            bot.reply_to(message, f"✅ User `{user_id}` banned.\nReason: {reason}")
            # Stop all scripts for banned user
            for file_name, _ in user_files.get(user_id, []):
                script_key = f"{user_id}_{file_name}"
                if script_key in bot_scripts:
                    kill_process_tree(bot_scripts[script_key])
                    del bot_scripts[script_key]
            
            try:
                bot.send_message(user_id, f"🚫 You have been banned from using this bot.\nReason: {reason}")
            except Exception as e:
                logger.error(f"Failed to notify banned user {user_id}: {e}")
        else:
            bot.reply_to(message, "❌ Failed to ban user.")
            
    except ValueError:
        bot.reply_to(message, "⚠️ Invalid user ID. Must be a number.")
    except Exception as e:
        logger.error(f"Error banning user: {e}", exc_info=True)
        bot.reply_to(message, f"❌ Error: {str(e)}")

def unban_user_callback(call):
    safe_answer_callback(call.id)
    msg = bot.send_message(call.message.chat.id, "✅ ╔══ 𝗨𝗡𝗕𝗔𝗡 𝗨𝗦𝗘𝗥 ══╗\n📝 Enter **User ID** to unban\n╚══════════════════╝\n🔴 /cancel — to stop", parse_mode='Markdown')
    bot.register_next_step_handler(msg, process_unban_user)

def process_unban_user(message):
    admin_id = message.from_user.id
    if admin_id not in admin_ids: bot.reply_to(message, "⚠️ Not authorized."); return
    
    if message.text.lower() == '/cancel':
        bot.reply_to(message, "╔══ 𝗔𝗖𝗧𝗜𝗢𝗡 𝗖𝗔𝗡𝗖𝗘𝗟𝗟𝗘𝗗 ══╗\n🚫 ╔══════════════════════════╗\n║    ✅ UNBAN CANCELLED    ║\n╚══════════════════════════╝\n\n  ❌ Unban cancelled.\n╚══════════════════╝", parse_mode='Markdown')
        return
    
    try:
        user_id = int(message.text.strip())
        if user_id <= 0: raise ValueError("ID must be positive")
        
        if user_id not in banned_users:
            bot.reply_to(message, f"ℹ️ User `{user_id}` is not banned.")
            return
        
        if unban_user_db(user_id):
            bot.reply_to(message, f"✅ User `{user_id}` unbanned.")
            try:
                bot.send_message(user_id, "✅ Your ban has been lifted. You can now use the bot again.")
            except Exception as e:
                logger.error(f"Failed to notify unbanned user {user_id}: {e}")
        else:
            bot.reply_to(message, "❌ Failed to unban user.")
            
    except ValueError:
        bot.reply_to(message, "⚠️ Invalid user ID. Must be a number.")
    except Exception as e:
        logger.error(f"Error unbanning user: {e}", exc_info=True)
        bot.reply_to(message, f"❌ Error: {str(e)}")

def user_info_callback(call):
    safe_answer_callback(call.id)
    msg = bot.send_message(call.message.chat.id, "👤 ╔══ 𝗨𝗦𝗘𝗥 𝗜𝗡𝗙𝗢 ══╗\n📝 Enter **User ID** to get info\n╚══════════════════╝\n🔴 /cancel — to stop", parse_mode='Markdown')
    bot.register_next_step_handler(msg, process_user_info)

def process_user_info(message):
    admin_id = message.from_user.id
    if admin_id not in admin_ids: bot.reply_to(message, "⚠️ Not authorized."); return
    
    if message.text.lower() == '/cancel':
        bot.reply_to(message, "╔══ 𝗔𝗖𝗧𝗜𝗢𝗡 𝗖𝗔𝗡𝗖𝗘𝗟𝗟𝗘𝗗 ══╗\n🚫 Info request cancelled.\n╚══════════════════╝", parse_mode='Markdown')
        return
    
    try:
        user_id = int(message.text.strip())
        if user_id <= 0: raise ValueError("ID must be positive")
        
        # Gather user information
        info_parts = []
        
        # Basic info
        info_parts.append(f"👤 **User ID:** `{user_id}`")
        
        # Status
        if user_id == OWNER_ID:
            info_parts.append("👑 **Status:** Owner")
        elif user_id in admin_ids:
            info_parts.append("🛡️ **Status:** Admin")
        elif user_id in banned_users:
            info_parts.append("🚫 **Status:** Banned")
        elif user_id in user_subscriptions:
            expiry = user_subscriptions[user_id].get('expiry')
            if expiry and expiry > datetime.now():
                days_left = (expiry - datetime.now()).days
                info_parts.append(f"⭐ **Status:** Premium (Expires in {days_left} days)")
            else:
                info_parts.append("🆓 **Status:** Free User (Expired subscription)")
        else:
            info_parts.append("🆓 **Status:** Free User")
        
        # Files
        file_count = get_user_file_count(user_id)
        file_limit = get_user_file_limit(user_id)
        info_parts.append(f"📁 **Files:** {file_count}/{file_limit if file_limit != float('inf') else 'Unlimited'}")
        
        # Custom limit
        if user_id in user_limits:
            info_parts.append(f"⚙️ **Custom Limit:** {user_limits[user_id]}")
        
        # Active scripts
        running_scripts = 0
        for file_name, _ in user_files.get(user_id, []):
            if is_bot_running(user_id, file_name):
                running_scripts += 1
        info_parts.append(f"🤖 **Running Scripts:** {running_scripts}")
        
        # Last seen (if in active users)
        if user_id in active_users:
            info_parts.append("🟢 **Status:** Active")
        
        info_text = "\n".join(info_parts)
        bot.reply_to(message, info_text, parse_mode='Markdown')
        
    except ValueError:
        bot.reply_to(message, "⚠️ Invalid user ID. Must be a number.")
    except Exception as e:
        logger.error(f"Error getting user info: {e}", exc_info=True)
        bot.reply_to(message, f"❌ Error: {str(e)}")

def all_users_callback(call):
    safe_answer_callback(call.id)
    try:
        if not active_users:
            bot.edit_message_text("👥 No active users yet.", call.message.chat.id, call.message.message_id)
            return
        
        users_list = list(active_users)
        chunk_size = 20
        total_pages = (len(users_list) + chunk_size - 1) // chunk_size
        
        # Create pagination
        current_page = 0
        display_users_list(call.message.chat.id, call.message.message_id, users_list, current_page, total_pages, chunk_size)
        
    except Exception as e:
        logger.error(f"Error displaying all users: {e}", exc_info=True)
        safe_answer_callback(call.id, "Error displaying users.", show_alert=True)

def display_users_list(chat_id, message_id, users_list, page, total_pages, chunk_size):
    start_idx = page * chunk_size
    end_idx = min(start_idx + chunk_size, len(users_list))
    
    user_chunk = users_list[start_idx:end_idx]
    
    message_text = f"👥 **Active Users** (Page {page + 1}/{total_pages})\n\n"
    for i, user_id in enumerate(user_chunk, start=start_idx + 1):
        status = ""
        if user_id == OWNER_ID: status = "👑"
        elif user_id in admin_ids: status = "🛡️"
        elif user_id in banned_users: status = "🚫"
        elif user_id in user_subscriptions and user_subscriptions[user_id].get('expiry', datetime.min) > datetime.now():
            status = "⭐"
        else: status = "🆓"
        
        message_text += f"{i}. `{user_id}` {status}\n"
    
    markup = types.InlineKeyboardMarkup(row_width=3)
    
    if total_pages > 1:
        page_buttons = []
        if page > 0:
            page_buttons.append(_sc_inline_button("⬅️ Previous", callback_data=f"users_page_{page-1}"))
        
        page_buttons.append(_sc_inline_button(f"{page+1}/{total_pages}", callback_data="noop"))
        
        if page < total_pages - 1:
            page_buttons.append(_sc_inline_button("Next ➡️", callback_data=f"users_page_{page+1}"))
        
        markup.row(*page_buttons)
    
    markup.row(_sc_inline_button("🔙 Back to User Management", callback_data='user_management'))
    
    try:
        bot.edit_message_text(message_text, chat_id, message_id, reply_markup=markup, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error editing users list: {e}")

def handle_users_page(call):
    if call.from_user.id not in admin_ids:
        safe_answer_callback(call.id, "⚠️ Admin only.", show_alert=True)
        return
    
    try:
        page = int(call.data.split('_')[2])
        users_list = list(active_users)
        chunk_size = 20
        total_pages = (len(users_list) + chunk_size - 1) // chunk_size
        
        if 0 <= page < total_pages:
            safe_answer_callback(call.id)
            display_users_list(call.message.chat.id, call.message.message_id, users_list, page, total_pages, chunk_size)
    except Exception as e:
        logger.error(f"Error handling users page: {e}", exc_info=True)
        safe_answer_callback(call.id, "Error.", show_alert=True)

def set_user_limit_callback(call):
    safe_answer_callback(call.id)
    msg = bot.send_message(call.message.chat.id, "🔧 ╔══ 𝗦𝗘𝗧 𝗖𝗨𝗦𝗧𝗢𝗠 𝗟𝗜𝗠𝗜𝗧 ══╗\n📝 Enter **User ID & new limit**\n💡 Example: `12345678 50`\n╚══════════════════╝\n🔴 /cancel — to stop", parse_mode='Markdown')
    bot.register_next_step_handler(msg, process_set_user_limit)

def process_set_user_limit(message):
    admin_id = message.from_user.id
    if admin_id not in admin_ids: bot.reply_to(message, "⚠️ Not authorized."); return
    
    if message.text.lower() == '/cancel':
        bot.reply_to(message, "╔══ 𝗔𝗖𝗧𝗜𝗢𝗡 𝗖𝗔𝗡𝗖𝗘𝗟𝗟𝗘𝗗 ══╗\n🚫 Limit set cancelled.\n╚══════════════════╝", parse_mode='Markdown')
        return
    
    try:
        parts = message.text.split()
        if len(parts) != 2: raise ValueError("Format: user_id limit")
        
        user_id = int(parts[0])
        limit = int(parts[1])
        
        if user_id <= 0 or limit <= 0: raise ValueError("ID and limit must be positive")
        
        if set_user_limit_db(user_id, limit, admin_id):
            bot.reply_to(message, f"✅ Set file limit {limit} for user `{user_id}`")
            try:
                bot.send_message(user_id, f"⚙️ Your file upload limit has been set to {limit}")
            except Exception as e:
                logger.error(f"Failed to notify user {user_id}: {e}")
        else:
            bot.reply_to(message, "❌ Failed to set limit.")
            
    except ValueError as e:
        bot.reply_to(message, f"⚠️ Invalid input: {e}\nFormat: `user_id limit`")
    except Exception as e:
        logger.error(f"Error setting user limit: {e}", exc_info=True)
        bot.reply_to(message, f"❌ Error: {str(e)}")

def remove_user_limit_callback(call):
    safe_answer_callback(call.id)
    msg = bot.send_message(call.message.chat.id, "🗑️ ╔══ 𝗥𝗘𝗠𝗢𝗩𝗘 𝗖𝗨𝗦𝗧𝗢𝗠 𝗟𝗜𝗠𝗜𝗧 ══╗\n📝 Enter **User ID** to remove custom limit\n╚══════════════════╝\n🔴 /cancel — to stop", parse_mode='Markdown')
    bot.register_next_step_handler(msg, process_remove_user_limit)

def process_remove_user_limit(message):
    admin_id = message.from_user.id
    if admin_id not in admin_ids: bot.reply_to(message, "⚠️ Not authorized."); return
    
    if message.text.lower() == '/cancel':
        bot.reply_to(message, "╔══ 𝗔𝗖𝗧𝗜𝗢𝗡 𝗖𝗔𝗡𝗖𝗘𝗟𝗟𝗘𝗗 ══╗\n🚫 Limit removal cancelled.\n╚══════════════════╝", parse_mode='Markdown')
        return
    
    try:
        user_id = int(message.text.strip())
        if user_id <= 0: raise ValueError("ID must be positive")
        
        if user_id not in user_limits:
            bot.reply_to(message, f"ℹ️ User `{user_id}` has no custom limit.")
            return
        
        if remove_user_limit_db(user_id):
            bot.reply_to(message, f"✅ Removed custom limit for user `{user_id}`")
            try:
                bot.send_message(user_id, "⚙️ Your custom file limit has been removed")
            except Exception as e:
                logger.error(f"Failed to notify user {user_id}: {e}")
        else:
            bot.reply_to(message, "❌ Failed to remove limit.")
            
    except ValueError:
        bot.reply_to(message, "⚠️ Invalid user ID. Must be a number.")
    except Exception as e:
        logger.error(f"Error removing user limit: {e}", exc_info=True)
        bot.reply_to(message, f"❌ Error: {str(e)}")

# --- Admin Settings Callbacks ---
def admin_settings_callback(call):
    safe_answer_callback(call.id)
    try:
        now_ist = datetime.now(IST).strftime("%d %b %Y • %I:%M:%S %p")
        bot.edit_message_text(
            "╔══════════════════════════╗\n"
            "║    ⚙️ ADMIN SETTINGS ⚙️   ║\n"
            "╚══════════════════════════╝\n\n"
            f"├ 🔒 Bot Status   : {'🔴 Locked' if bot_locked else '🟢 Unlocked'}\n"
            f"├ 🛠️ Maintenance  : {'🟢 ON' if maintenance_mode else '🔴 OFF'}\n"
            f"├ 📢 Subscription : {'🟢 ON' if subscription_mode else '🔴 OFF'}\n"
            f"├ 📢 Channels     : `{len(mandatory_channels)}`\n"
            f"├ 🛡️ Admins       : `{len(admin_ids)}`\n"
            f"└ 🕐 Time         : `{now_ist} IST`\n\n"
            "👇 *Select an action:*",
            call.message.chat.id, call.message.message_id,
            reply_markup=create_admin_settings_menu(), parse_mode='Markdown')
    except Exception as e: logger.error(f"Error showing admin settings: {e}")

def maintenance_mode_callback(call):
    global maintenance_mode
    if call.from_user.id not in admin_ids:
        safe_answer_callback(call.id, "Admin permissions required.", show_alert=True)
        return
    maintenance_mode = not maintenance_mode
    status = "ON" if maintenance_mode else "OFF"
    logger.warning(f"Maintenance mode {status} by Admin {call.from_user.id}")
    safe_answer_callback(call.id, f"Maintenance {status}")
    _broadcast_maintenance_status(status, call.from_user.id)
    try:
        now_ist = datetime.now(IST).strftime("%d %b %Y • %I:%M:%S %p")
        bot.edit_message_text(
            "╔══════════════════════════╗\n"
            "║    ⚙️ ADMIN SETTINGS ⚙️   ║\n"
            "╚══════════════════════════╝\n\n"
            f"├ 🔒 Bot Status   : {'🔴 Locked' if bot_locked else '🟢 Unlocked'}\n"
            f"├ 🛠️ Maintenance  : {'🟢 ON' if maintenance_mode else '🔴 OFF'}\n"
            f"├ 📢 Subscription : {'🟢 ON' if subscription_mode else '🔴 OFF'}\n"
            f"├ 📢 Channels     : `{len(mandatory_channels)}`\n"
            f"├ 🛡️ Admins       : `{len(admin_ids)}`\n"
            f"└ 🕐 Time         : `{now_ist} IST`\n\n"
            "👇 *Select an action:*",
            call.message.chat.id, call.message.message_id,
            reply_markup=create_admin_settings_menu(), parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Error updating maintenance mode menu: {e}", exc_info=True)

def subscription_mode_callback(call):
    """Toggle global mandatory channel subscription enforcement."""
    global subscription_mode
    if call.from_user.id not in admin_ids:
        safe_answer_callback(call.id, "Admin permissions required.", show_alert=True)
        return

    new_value = not subscription_mode
    if not save_subscription_mode_setting(new_value):
        safe_answer_callback(call.id, "Failed to save setting.", show_alert=True)
        return

    subscription_mode = new_value
    status = "ON" if subscription_mode else "OFF"
    logger.warning(f"Mandatory subscription mode {status} by Admin {call.from_user.id}")
    safe_answer_callback(call.id, f"Subscription Mode {status}")

    try:
        now_ist = datetime.now(IST).strftime("%d %b %Y • %I:%M:%S %p")
        bot.edit_message_text(
            "╔══════════════════════════╗\n"
            "║    ⚙️ ADMIN  SETTINGS ⚙️  ║\n"
            "╚══════════════════════════╝\n\n"
            f"├ 🔒 Bot Status   : {'🔴 Locked' if bot_locked else '🟢 Unlocked'}\n"
            f"├ 🛠️ Maintenance  : {'🟢 ON' if maintenance_mode else '🔴 OFF'}\n"
            f"├ 📢 Subscription : {'🟢 ON' if subscription_mode else '🔴 OFF'}\n"
            f"├ 📢 Channels     : `{len(mandatory_channels)}`\n"
            f"├ 🛡️ Admins       : `{len(admin_ids)}`\n"
            f"└ 🕐 Time         : `{now_ist} IST`\n\n"
            "👇 *Select an action:*",
            call.message.chat.id, call.message.message_id,
            reply_markup=create_admin_settings_menu(), parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Error updating subscription mode menu: {e}", exc_info=True)

# Real-time CPU frequency helper. Prefer Linux cpufreq current-frequency
# files when available, then fall back to psutil.cpu_freq().
def get_realtime_cpu_frequency():
    try:
        from pathlib import Path
        values = []
        for path in Path("/sys/devices/system/cpu").glob("cpu[0-9]*/cpufreq/scaling_cur_freq"):
            try:
                raw = path.read_text().strip()
                if raw:
                    mhz = float(raw) / 1000.0
                    if mhz > 0:
                        values.append(mhz)
            except Exception:
                continue
        if values:
            return sum(values) / len(values)
    except Exception:
        pass
    try:
        if psutil is not None:
            freq = psutil.cpu_freq()
            current = getattr(freq, "current", None) if freq else None
            if current is not None and float(current) > 0:
                return float(current)
    except Exception:
        pass
    return None

def system_info_callback(call):
    safe_answer_callback(call.id)
    try:
        import platform

        # Same layout as n3w1.py; metrics are collected independently so a
        # single psutil PermissionError cannot break the System Info panel.
        cpu_percent = None
        memory = None
        disk = None
        uptime_secs = 0

        # Detect the filesystem that actually contains the running bot.
        # This is platform-independent: no hardcoded phone/server paths.
        # Using the script directory avoids accidentally reporting a small
        # unrelated "/" mount when the bot itself lives on another filesystem.
        try:
            runtime_path = os.path.abspath(os.path.dirname(__file__) or os.getcwd())
            if not os.path.exists(runtime_path):
                runtime_path = os.path.abspath(os.getcwd())
        except Exception:
            runtime_path = os.path.abspath(os.getcwd())

        if psutil is not None:
            try:
                cpu_percent = float(psutil.cpu_percent(interval=0.5))
            except Exception:
                # Some restricted runtimes (for example sandboxed Python
                # environments) deny access to /proc/stat. Do not spam the
                # log on every System Info click; use the standard-library
                # process CPU fallback below instead.
                cpu_percent = None
            try:
                memory = psutil.virtual_memory()
            except Exception:
                memory = None
            try:
                # Detect the storage backing the directory where this bot
                # actually runs. No Android/server-specific paths are used.
                disk = psutil.disk_usage(runtime_path)
            except Exception:
                disk = None
            try:
                uptime_secs = int(max(0, time.time() - psutil.boot_time()))
            except Exception:
                uptime_secs = 0

        # Real-time CPU diagnosis. Prefer system-wide psutil metrics; if the
        # runtime blocks /proc/stat, fall back to a measured process CPU sample
        # and expose the limitation explicitly instead of showing fake system CPU.
        cpu_source = "System"
        cpu_diag = {
            "cores": max(1, os.cpu_count() or 1),
            "threads": max(1, os.cpu_count() or 1),
            "freq": None,
            "load1": None,
            "load5": None,
            "load15": None,
            "status": "OK",
        }
        if cpu_percent is None:
            cpu_source = "Process fallback"
            try:
                import resource
                r1 = resource.getrusage(resource.RUSAGE_SELF)
                t1 = time.monotonic()
                time.sleep(0.5)
                r2 = resource.getrusage(resource.RUSAGE_SELF)
                t2 = time.monotonic()
                cpu_time = ((r2.ru_utime + r2.ru_stime) -
                             (r1.ru_utime + r1.ru_stime))
                wall = max(0.001, t2 - t1)
                # Process CPU as a percentage of one logical CPU. This is not
                # presented as system-wide CPU when /proc/stat is inaccessible.
                cpu_percent = max(0.0, min(100.0, (cpu_time / wall) * 100.0))
            except Exception:
                cpu_percent = 0.0
                cpu_diag["status"] = "Unavailable"

        # Collect live CPU diagnosis fields without requiring privileged APIs.
        try:
            cpu_diag["cores"] = max(1, int(psutil.cpu_count(logical=False) or 1)) if psutil is not None else max(1, os.cpu_count() or 1)
            cpu_diag["threads"] = max(1, int(psutil.cpu_count(logical=True) or 1)) if psutil is not None else max(1, os.cpu_count() or 1)
        except Exception:
            pass
        try:
            cpu_diag["freq"] = get_realtime_cpu_frequency()
        except Exception:
            cpu_diag["freq"] = None
        try:
            load = os.getloadavg()
            cpu_diag["load1"], cpu_diag["load5"], cpu_diag["load15"] = map(float, load)
        except Exception:
            pass

        # Simple diagnostic state based on the live system CPU percentage when
        # available; otherwise keep the result honest about the fallback source.
        if cpu_source == "System":
            if cpu_percent >= 90:
                cpu_diag["status"] = "High"
            elif cpu_percent >= 70:
                cpu_diag["status"] = "Busy"
            else:
                cpu_diag["status"] = "Normal"

        # Generic Python process-memory fallback.
        if memory is None:
            try:
                import resource
                rss_kb = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
                mem_used = max(0, rss_kb * 1024)
                mem_total = None
                mem_percent = None
            except Exception:
                mem_used = mem_total = mem_percent = None
        else:
            mem_used = int(memory.used)
            mem_total = int(memory.total)
            mem_percent = float(memory.percent)

        # Standard-library disk fallback.
        if disk is None:
            try:
                du = shutil.disk_usage(runtime_path)
                disk_used = int(du.used)
                disk_total = int(du.total)
                disk_percent = (disk_used / disk_total * 100.0) if disk_total else 0.0
            except Exception:
                disk_used = disk_total = 0
                disk_percent = 0.0
        else:
            disk_used = int(disk.used)
            disk_total = int(disk.total)
            disk_percent = float(disk.percent)

        if not uptime_secs:
            try:
                uptime_secs = max(0, int((datetime.now(IST) - BOT_START_TIME).total_seconds()))
            except Exception:
                uptime_secs = 0

        def fmt_mb(value):
            if value is None:
                return "N/A"
            return f"{value / (1024 ** 2):.2f}MB"

        def fmt_gb(value):
            if value is None:
                return "N/A"
            return f"{value / (1024 ** 3):.2f}GB"

        cpu_bar_len = 10
        cpu_filled = min(cpu_bar_len, max(0, int(float(cpu_percent) / 10)))
        cpu_bar = "█" * cpu_filled + "░" * (cpu_bar_len - cpu_filled)

        if mem_percent is not None and mem_total is not None:
            mem_filled = min(cpu_bar_len, max(0, int(mem_percent / 10)))
            mem_bar = "█" * mem_filled + "░" * (cpu_bar_len - mem_filled)
            mem_line = (
                f"├ 🧠 RAM  `{mem_percent:5.1f}%` `{mem_bar}`\n"
                f"│         ({fmt_mb(mem_used)} / {fmt_mb(mem_total)})"
            )
        elif mem_used is not None:
            mem_bar = "░" * cpu_bar_len
            mem_line = f"├ 🧠 RAM  `Process: {fmt_mb(mem_used)}` `{mem_bar}`"
        else:
            mem_line = "├ 🧠 RAM  `N/A`"

        disk_filled = min(cpu_bar_len, max(0, int(disk_percent / 10)))
        disk_bar = "█" * disk_filled + "░" * (cpu_bar_len - disk_filled)
        now_ist = datetime.now(IST).strftime("%d %b %Y • %I:%M:%S %p")
        uptime_str = time.strftime('%H:%M:%S', time.gmtime(uptime_secs))

        # CPU diagnosis lines are kept compact so the original System Info
        # layout remains intact while giving a live diagnostic snapshot.
        freq_text = f"{cpu_diag['freq']:.0f} MHz" if cpu_diag["freq"] else "N/A"
        load_text = (
            f"{cpu_diag['load1']:.2f}/{cpu_diag['load5']:.2f}/{cpu_diag['load15']:.2f}"
            if cpu_diag["load1"] is not None else "N/A"
        )
        cpu_status = cpu_diag["status"]
        info_text = (
            "╔══════════════════════════╗\n"
            "║    📊 SYSTEM  INFO 📊    ║\n"
            "╚══════════════════════════╝\n\n"
            "🤖 *BOT*\n"
            f"├ 🐍 Python   : `{platform.python_version()}`\n"
            f"└ ⏱️ Uptime    : `{uptime_str}`\n\n"
            "💻 *SYSTEM*\n"
            f"├ ⚡ CPU  `{float(cpu_percent):5.1f}%` `{cpu_bar}`\n"
            f"│   Diagnosis : `{cpu_status}` ({cpu_source})\n"
            f"│   Cores     : `{cpu_diag['cores']}` physical / `{cpu_diag['threads']}` logical\n"
            f"│   Frequency : `{freq_text}` (real-time current)\n"
            f"│   Load 1/5/15m : `{load_text}`\n"
            f"{mem_line}\n"
            f"└ 💾 Disk `{disk_percent:5.1f}%` `{disk_bar}`\n"
            f"          ({fmt_gb(disk_used)} / {fmt_gb(disk_total)})\n\n"
            "📈 *BOT STATS*\n"
            f"├ 👤 Active Users    : `{len(active_users)}`\n"
            f"├ 🤖 Running Scripts : `{len(bot_scripts)}`\n"
            f"├ 📂 Total Files     : `{sum(len(f) for f in user_files.values())}`\n"
            f"└ 🔒 Status          : {'🔴 Locked' if bot_locked else '🟢 Unlocked'}\n\n"
            f"🕐 `{now_ist} IST`"
        )
        bot.edit_message_text(
            info_text,
            call.message.chat.id,
            call.message.message_id,
            reply_markup=create_admin_settings_menu(),
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Error showing system info: {e}", exc_info=True)
        safe_answer_callback(call.id, "Error showing system info.", show_alert=True)

def bot_performance_callback(call):
    safe_answer_callback(call.id)
    try:
        running_scripts = len(bot_scripts)
        total_files = sum(len(files) for files in user_files.values())
        uptime_ratio = (running_scripts / total_files * 100) if total_files > 0 else 0.0
        ratio_bar_len = 10
        ratio_filled = int(uptime_ratio / 10)
        ratio_bar = "▰" * ratio_filled + "▱" * (ratio_bar_len - ratio_filled)
        # Live system CPU + live current frequency. The sampling interval gives
        # an actual fresh reading instead of a cached/stale value.
        system_cpu = None
        cpu_frequency = None
        process_cpu = None
        if psutil is not None:
            bot_process = psutil.Process()
            memory_usage = bot_process.memory_info().rss / 1024 / 1024
            try:
                system_cpu = float(psutil.cpu_percent(interval=0.5))
            except Exception:
                system_cpu = None
            try:
                process_cpu = float(bot_process.cpu_percent(interval=0.5))
            except Exception:
                process_cpu = None
            try:
                cpu_frequency = get_realtime_cpu_frequency()
            except Exception:
                cpu_frequency = None
        else:
            memory_usage = 0.0

        cpu_text = f"{system_cpu:.1f}%" if system_cpu is not None else "N/A"
        proc_cpu_text = f"{process_cpu:.1f}%" if process_cpu is not None else "N/A"
        freq_text = f"{cpu_frequency:.0f} MHz" if cpu_frequency is not None else "N/A"
        now_ist = datetime.now(IST).strftime("%d %b %Y • %I:%M:%S %p")
        perf_text = (
            "╔══════════════════════════╗\n"
            "║  📈 BOT PERFORMANCE 📈   ║\n"
            "╚══════════════════════════╝\n\n"
            "🤖 *SCRIPTS*\n"
            f"├ 🟢 Running    : `{running_scripts}`\n"
            f"├ 📂 Total      : `{total_files}`\n"
            f"└ 📊 Active %   : `{uptime_ratio:.1f}%` `{ratio_bar}`\n\n"
            "💾 *RESOURCE USAGE*\n"
            f"├ 🧠 Memory     : `{memory_usage:.1f} MB`\n"
            f"├ ⚡ CPU        : `{cpu_text}` (real-time system)\n"
            f"├ 🔧 Process CPU: `{proc_cpu_text}`\n"
            f"└ 📡 Frequency  : `{freq_text}` (real-time current)\n\n"
            "🗄️ *DATABASE*\n"
            f"├ 👤 Active Users   : `{len(active_users)}`\n"
            f"├ ⭐ Subscriptions  : `{len(user_subscriptions)}`\n"
            f"├ 🚫 Banned         : `{len(banned_users)}`\n"
            f"└ ⚙️ Custom Limits  : `{len(user_limits)}`\n\n"
            f"🕐 `{now_ist} IST`"
        )
        bot.edit_message_text(perf_text, call.message.chat.id, call.message.message_id,
                              reply_markup=create_admin_settings_menu(), parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error showing performance: {e}", exc_info=True)
        safe_answer_callback(call.id, "Error showing performance.", show_alert=True)

def cleanup_files_callback(call):
    safe_answer_callback(call.id, "🧹 Cleaning up temporary files...")
    
    try:
        # Clean up empty user directories
        cleaned_dirs = 0
        cleaned_files = 0
        
        for user_dir in os.listdir(UPLOAD_BOTS_DIR):
            user_path = os.path.join(UPLOAD_BOTS_DIR, user_dir)
            if os.path.isdir(user_path):
                # Check if directory is empty
                if not os.listdir(user_path):
                    try:
                        os.rmdir(user_path)
                        cleaned_dirs += 1
                    except Exception as e:
                        logger.error(f"Error removing empty dir {user_path}: {e}")
                
                # Clean old log files (older than 7 days)
                else:
                    for file_name in os.listdir(user_path):
                        if file_name.endswith('.log'):
                            file_path = os.path.join(user_path, file_name)
                            try:
                                file_age = time.time() - os.path.getmtime(file_path)
                                if file_age > 7 * 24 * 3600:  # 7 days
                                    os.remove(file_path)
                                    cleaned_files += 1
                            except Exception as e:
                                logger.error(f"Error cleaning log file {file_path}: {e}")
        
        result_msg = (
            "╔══════════════════════════╗\n"
            "║   🧹 CLEANUP COMPLETE 🧹  ║\n"
            "╚══════════════════════════╝\n\n"
            f"├ 📁 Empty dirs removed : `{cleaned_dirs}`\n"
            f"└ 📋 Old logs cleared   : `{cleaned_files}`\n\n"
            "✅ *Cleanup finished successfully!*"
        )
        bot.edit_message_text(result_msg, call.message.chat.id, call.message.message_id,
                              reply_markup=create_admin_settings_menu(), parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error during cleanup: {e}", exc_info=True)
        bot.edit_message_text(f"❌ Cleanup error: {str(e)}", call.message.chat.id, call.message.message_id)

def install_logs_callback(call):
    safe_answer_callback(call.id)
    try:
        with DB_LOCK:
            conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
            c = conn.cursor()
            c.execute('SELECT user_id, module_name, package_name, status, install_date FROM install_logs ORDER BY install_date DESC LIMIT 20')
            logs = c.fetchall()
            conn.close()
        
        if not logs:
            bot.edit_message_text(
                "╔══════════════════════════╗\n"
                "║  📋 INSTALL  LOGS 📋    ║\n"
                "╚══════════════════════════╝\n\n"
                "📭 *No installation logs found yet.*",
                call.message.chat.id, call.message.message_id,
                reply_markup=create_admin_settings_menu(), parse_mode='Markdown')
            return
        
        success_count = sum(1 for _, _, _, s, _ in logs if s == "success")
        fail_count = len(logs) - success_count
        log_text = (
            "╔══════════════════════════╗\n"
            "║  📋 INSTALL  LOGS 📋    ║\n"
            "╚══════════════════════════╝\n\n"
            f"✅ Success: `{success_count}`  ❌ Failed: `{fail_count}`\n"
            "─────────────────────────\n\n"
        )
        for user_id, module_name, package_name, status, install_date in logs:
            status_icon = "✅" if status == "success" else "❌" if status == "failed" else "⚠️"
            log_text += f"{status_icon} `{user_id}`: `{module_name}` → `{package_name}`\n"
            log_text += f"   🕐 `{install_date[:19]}`\n\n"
        
        bot.edit_message_text(log_text, call.message.chat.id, call.message.message_id,
                              reply_markup=create_admin_settings_menu(), parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error showing install logs: {e}", exc_info=True)
        safe_answer_callback(call.id, "Error showing logs.", show_alert=True)

def admin_install_callback(call):
    safe_answer_callback(call.id)
    _logic_admin_install(call.message)

# --- Mandatory Channels Callbacks ---
def manage_mandatory_channels_callback(call):
    """Handle mandatory channels management request"""
    safe_answer_callback(call.id)
    try:
        now_ist = datetime.now(IST).strftime("%d %b %Y • %I:%M:%S %p")
        ch_count = len(mandatory_channels)
        text = (
            "╔══════════════════════════╗\n"
            "║   📢 MANDATORY CHANNELS  ║\n"
            "╚══════════════════════════╝\n\n"
            f"├ 📡 *Total Channels* : `{ch_count}`\n"
            f"└ 🕐 *Time*          : `{now_ist} IST`\n\n"
            "📌 Choose an action below:"
        )
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id,
                              reply_markup=create_mandatory_channels_menu(), parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error showing channel management menu: {e}")

def add_mandatory_channel_callback(call):
    """Add new mandatory channel"""
    safe_answer_callback(call.id)
    now_ist = datetime.now(IST).strftime("%d %b %Y • %I:%M:%S %p")
    msg = bot.send_message(call.message.chat.id,
        "╔══════════════════════════╗\n"
        "║   ➕ ADD  NEW CHANNEL    ║\n"
        "╚══════════════════════════╝\n\n"
        "📤 Send channel *ID* or *username*:\n"
        "├ `@channel_username`\n"
        "└ `-1001234567890`\n\n"
        f"🕐 `{now_ist} IST`\n"
        "📌 Send /cancel to abort.",
        parse_mode='Markdown')
    bot.register_next_step_handler(msg, process_add_channel)

def process_add_channel(message):
    """Process channel addition"""
    admin_id = message.from_user.id
    if admin_id not in admin_ids:
        bot.reply_to(message, "⚠️ Not authorized.")
        return
        
    if message.text and message.text.lower() == '/cancel':
        bot.reply_to(message, "╔══════════════════════════╗\n║   ❌ ACTION CANCELLED    ║\n╚══════════════════════════╝\n\nChannel addition was cancelled.")
        return
        
    channel_identifier = (message.text or "").strip()
    if not channel_identifier:
        bot.reply_to(message, "❌ Please send a channel @username, numeric ID, or t.me link.")
        return

    # Accept common Telegram channel formats:
    #   @channelname
    #   channelname
    #   -1001234567890
    #   https://t.me/channelname
    #   t.me/channelname
    raw_identifier = channel_identifier
    try:
        if raw_identifier.startswith(('https://t.me/', 'http://t.me/', 'https://telegram.me/', 'http://telegram.me/')):
            raw_identifier = raw_identifier.split('/', 3)[-1]
        elif raw_identifier.startswith(('t.me/', 'telegram.me/')):
            raw_identifier = raw_identifier.split('/', 1)[-1]

        # Remove optional trailing slash and Telegram post/message suffix.
        raw_identifier = raw_identifier.strip().rstrip('/')
        if '/' in raw_identifier and not raw_identifier.startswith('-100'):
            raw_identifier = raw_identifier.split('/', 1)[0]

        if raw_identifier.startswith('@'):
            channel_identifier = raw_identifier
        elif raw_identifier.startswith('-100') or raw_identifier.lstrip('-').isdigit():
            channel_identifier = raw_identifier
        else:
            channel_identifier = '@' + raw_identifier

        # Get channel info
        chat = bot.get_chat(channel_identifier)
        channel_id = str(chat.id)
        channel_username = f"@{chat.username}" if chat.username else ""
        channel_name = chat.title
        
        # Ensure bot is admin in the channel
        try:
            bot_member = bot.get_chat_member(channel_id, bot.get_me().id)
            if bot_member.status not in ['administrator', 'creator']:
                bot.reply_to(message, f"❌ Bot is not admin in the channel! Must be promoted first.")
                return
        except Exception as e:
            bot.reply_to(message, f"❌ Bot is not admin in the channel or cannot access it!")
            return
            
        # Save channel to database
        now_ist = datetime.now(IST).strftime("%d %b %Y • %I:%M:%S %p")
        if save_mandatory_channel(channel_id, channel_username, channel_name, admin_id):
            bot.reply_to(message,
                "╔══════════════════════════╗\n"
                "║  ✅ CHANNEL  ADDED! 🎉   ║\n"
                "╚══════════════════════════╝\n\n"
                f"├ 📛 *Name*     : `{channel_name}`\n"
                f"├ 🔗 *Username* : `{channel_username or channel_id}`\n"
                f"├ 🆔 *ID*       : `{channel_id}`\n"
                f"├ 📡 *Total*    : `{len(mandatory_channels)}`\n"
                f"└ 🕐 *Time*     : `{now_ist} IST`",
                parse_mode='Markdown')
        else:
            bot.reply_to(message,
                "╔══════════════════════════╗\n"
                "║   ❌ FAILED TO ADD       ║\n"
                "╚══════════════════════════╝\n\n"
                "Could not save the channel. Try again.", parse_mode='Markdown')
            
    except telebot.apihelper.ApiTelegramException as e:
        error_text = str(e)
        logger.error(f"Error adding channel '{channel_identifier}': {error_text}")
        if getattr(e, 'error_code', None) == 400 and 'chat not found' in error_text.lower():
            if 't.me/+' in channel_identifier or 'telegram.me/+' in channel_identifier:
                help_text = (
                    "❌ Private invite link cannot be resolved directly.\n\n"
                    "For a private channel:\n"
                    "1️⃣ Add the bot to the channel.\n"
                    "2️⃣ Promote the bot to Administrator.\n"
                    "3️⃣ Send the channel numeric ID, e.g. `-1001234567890`.\n\n"
                    "For a public channel, send `@channel_username`."
                )
            else:
                help_text = (
                    "❌ Channel not found / not accessible.\n\n"
                    "Use one of these formats:\n"
                    "├ @channel_username\n"
                    "├ -1001234567890\n"
                    "└ https://t.me/channel_username\n\n"
                    "⚠️ The bot must be added to the channel and made an Administrator. "
                    "Private channels should be added using their -100... chat ID."
                )
            bot.reply_to(message, help_text, parse_mode='Markdown')
        else:
            bot.reply_to(message, f"❌ Telegram error: {error_text}")
    except Exception as e:
        logger.error(f"Error adding channel '{channel_identifier}': {e}", exc_info=True)
        bot.reply_to(message, f"❌ Error adding channel: {str(e)}")

def remove_mandatory_channel_callback(call):
    """Remove mandatory channel"""
    if not mandatory_channels:
        safe_answer_callback(call.id, "❌ No mandatory channels.", show_alert=True)
        return
        
    safe_answer_callback(call.id)
    
    markup = types.InlineKeyboardMarkup()
    for channel_id, channel_info in mandatory_channels.items():
        channel_name = channel_info.get('name', 'Unknown')
        button_text = f"🗑️ {channel_name}"
        markup.add(_sc_inline_button(button_text, callback_data=f'remove_channel_{channel_id}'))
    
    markup.add(_sc_inline_button("🔙 Back", callback_data='manage_mandatory_channels'))
    
    try:
        now_ist = datetime.now(IST).strftime("%d %b %Y • %I:%M:%S %p")
        bot.edit_message_text(
            "╔══════════════════════════╗\n"
            "║  🗑️  REMOVE  CHANNEL  🗑️  ║\n"
            "╚══════════════════════════╝\n\n"
            f"├ 📡 *Channels* : `{len(mandatory_channels)}`\n"
            f"└ 🕐 *Time*     : `{now_ist} IST`\n\n"
            "👇 Tap a channel to remove it:",
            call.message.chat.id, call.message.message_id,
            reply_markup=markup, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error showing remove channel menu: {e}")

def process_remove_channel(call):
    """Process channel removal"""
    channel_id = call.data.replace('remove_channel_', '')
    
    if channel_id in mandatory_channels:
        channel_name = mandatory_channels[channel_id].get('name', 'Unknown')
        if remove_mandatory_channel_db(channel_id):
            safe_answer_callback(call.id, f"✅ Channel deleted: {channel_name}")
            try:
                now_ist = datetime.now(IST).strftime("%d %b %Y • %I:%M:%S %p")
                bot.edit_message_text(
                    "╔══════════════════════════╗\n"
                    "║   ✅ CHANNEL  REMOVED    ║\n"
                    "╚══════════════════════════╝\n\n"
                    f"├ 📛 *Channel* : `{channel_name}`\n"
                    f"├ 📡 *Remaining* : `{len(mandatory_channels)}`\n"
                    f"└ 🕐 *Time*     : `{now_ist} IST`\n\n"
                    "📌 Choose next action:",
                    call.message.chat.id, call.message.message_id,
                    reply_markup=create_mandatory_channels_menu(), parse_mode='Markdown')
            except Exception as e:
                logger.error(f"Error updating message after channel removal: {e}")
        else:
            safe_answer_callback(call.id, "❌ Failed to delete channel.", show_alert=True)
    else:
        safe_answer_callback(call.id, "❌ Channel not found.", show_alert=True)

def list_mandatory_channels_callback(call):
    """Show list of mandatory channels"""
    safe_answer_callback(call.id)
    
    now_ist = datetime.now(IST).strftime("%d %b %Y • %I:%M:%S %p")
    if not mandatory_channels:
        message_text = (
            "╔══════════════════════════╗\n"
            "║  📋 MANDATORY CHANNELS   ║\n"
            "╚══════════════════════════╝\n\n"
            "├ 📭 *No channels added yet*\n"
            f"└ 🕐 *Time* : `{now_ist} IST`\n\n"
            "📌 Use ➕ Add Channel to get started."
        )
    else:
        lines = (
            "╔══════════════════════════╗\n"
            "║  📋 MANDATORY CHANNELS   ║\n"
            "╚══════════════════════════╝\n\n"
            f"├ 📡 *Total* : `{len(mandatory_channels)}`\n"
            f"└ 🕐 *Time*  : `{now_ist} IST`\n"
            "─────────────────────────\n"
        )
        items = list(mandatory_channels.items())
        for i, (channel_id, channel_info) in enumerate(items):
            channel_name = channel_info.get('name', 'Unknown')
            channel_username = channel_info.get('username', '') or channel_id
            prefix = "└" if i == len(items) - 1 else "├"
            lines += f"{prefix} 📢 *{channel_name}*\n   `{channel_username}`\n"
        message_text = lines
    try:
        bot.edit_message_text(message_text, call.message.chat.id, call.message.message_id,
                              reply_markup=create_mandatory_channels_menu(), parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error listing channels: {e}")

def check_subscription_status_callback(call):
    """Check subscription status"""
    user_id = call.from_user.id
    is_subscribed, not_joined = check_mandatory_subscription(user_id)
    
    if is_subscribed or user_id in admin_ids:
        safe_answer_callback(call.id, "✅ You are subscribed to all required channels!", show_alert=True)
        # Show main menu
        try:
            _logic_send_welcome(call.message)
        except:
            back_to_main_callback(call)
    else:
        safe_answer_callback(call.id, "❌ You haven't joined all required channels yet!", show_alert=True)
        # Update the subscription message
        subscription_message, markup = create_subscription_check_message(not_joined)
        try:
            bot.edit_message_text(subscription_message, call.message.chat.id, 
                                  call.message.message_id, reply_markup=markup, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Error updating subscription message: {e}")

# --- Security Approval Callbacks ---
def process_approve_file(call):
    """Process admin approval for file"""
    data_parts = call.data.split('_')
    if len(data_parts) < 4:
        safe_answer_callback(call.id, "❌ Invalid data.", show_alert=True)
        return
        
    user_id = int(data_parts[2])
    file_name = '_'.join(data_parts[3:])
    
    user_folder = get_user_folder(user_id)
    file_path = os.path.join(user_folder, file_name)
    
    if not os.path.exists(file_path):
        safe_answer_callback(call.id, "❌ File not found.", show_alert=True)
        return
    
    file_ext = os.path.splitext(file_name)[1].lower()
    
    try:
        # Process the approved file
        if file_ext == '.js':
            handle_js_file(file_path, user_id, user_folder, file_name, call.message)
        elif file_ext == '.py':
            handle_py_file(file_path, user_id, user_folder, file_name, call.message)
        
        safe_answer_callback(call.id, "✅ File approved!")
        bot.edit_message_text(f"✅ File `{file_name}` approved for user `{user_id}`",
                              call.message.chat.id, call.message.message_id)
        
        # Notify user
        try:
            bot.send_message(user_id, f"✅ Your file `{file_name}` has been approved and started.")
        except Exception as e:
            logger.error(f"Failed to notify user {user_id}: {e}")
            
    except Exception as e:
        logger.error(f"Error processing approved file: {e}")
        safe_answer_callback(call.id, "❌ Error processing file.", show_alert=True)

def process_reject_file(call):
    """Process admin rejection for file"""
    data_parts = call.data.split('_')
    if len(data_parts) < 4:
        safe_answer_callback(call.id, "❌ Invalid data.", show_alert=True)
        return
        
    user_id = int(data_parts[2])
    file_name = '_'.join(data_parts[3:])
    
    user_folder = get_user_folder(user_id)
    file_path = os.path.join(user_folder, file_name)
    
    # Delete the file
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            logger.error(f"Error deleting rejected file: {e}")
    
    safe_answer_callback(call.id, "❌ File rejected!")
    bot.edit_message_text(f"❌ File `{file_name}` rejected for user `{user_id}`",
                          call.message.chat.id, call.message.message_id)
    
    # Notify user
    try:
        bot.send_message(user_id, f"❌ Your file `{file_name}` has been rejected for security reasons.")
    except Exception as e:
        logger.error(f"Failed to notify user {user_id}: {e}")

def process_approve_zip(call):
    """Process admin approval for ZIP file"""
    data_parts = call.data.split('_')
    if len(data_parts) < 4:
        safe_answer_callback(call.id, "❌ Invalid data.", show_alert=True)
        return
        
    user_id = int(data_parts[2])
    file_name = '_'.join(data_parts[3:])
    
    # Check if we have stored file content
    if user_id in pending_zip_files and file_name in pending_zip_files[user_id]:
        file_content = pending_zip_files[user_id][file_name]
        user_folder = get_user_folder(user_id)
        temp_dir = None
        
        try:
            temp_dir = tempfile.mkdtemp(prefix=f"user_{user_id}_zip_approve_")
            zip_path = os.path.join(temp_dir, file_name)
            
            # Save the file content
            with open(zip_path, 'wb') as f:
                f.write(file_content)
            
            # Process the ZIP file
            process_zip_file(zip_path, user_id, user_folder, file_name, call.message, temp_dir)
            
            # Clean up pending files
            if user_id in pending_zip_files and file_name in pending_zip_files[user_id]:
                del pending_zip_files[user_id][file_name]
                if not pending_zip_files[user_id]:
                    del pending_zip_files[user_id]
            
            safe_answer_callback(call.id, "✅ Archive approved!")
            bot.edit_message_text(f"✅ Archive `{file_name}` approved for user `{user_id}`",
                                  call.message.chat.id, call.message.message_id)
            
            # Notify user
            try:
                bot.send_message(user_id, f"✅ Your archive `{file_name}` has been approved and processed.")
            except Exception as e:
                logger.error(f"Failed to notify user {user_id}: {e}")
                
        except Exception as e:
            logger.error(f"Error processing approved zip: {e}", exc_info=True)
            safe_answer_callback(call.id, "❌ Error processing archive.", show_alert=True)
        finally:
            if temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                except Exception as e:
                    logger.error(f"Error cleaning temp dir: {e}")
    else:
        safe_answer_callback(call.id, "❌ File content not found. Ask user to re-upload.", show_alert=True)

def process_reject_zip(call):
    """Process admin rejection for ZIP file"""
    data_parts = call.data.split('_')
    if len(data_parts) < 4:
        safe_answer_callback(call.id, "❌ Invalid data.", show_alert=True)
        return
        
    user_id = int(data_parts[2])
    file_name = '_'.join(data_parts[3:])
    
    # Clean up pending files
    if user_id in pending_zip_files and file_name in pending_zip_files[user_id]:
        del pending_zip_files[user_id][file_name]
        if not pending_zip_files[user_id]:
            del pending_zip_files[user_id]
    
    safe_answer_callback(call.id, "❌ Archive rejected!")
    bot.edit_message_text(f"❌ Archive `{file_name}` rejected for user `{user_id}`",
                          call.message.chat.id, call.message.message_id)
    
    try:
        bot.send_message(user_id, f"❌ Your archive `{file_name}` has been rejected for security reasons.")
    except Exception as e:
        logger.error(f"Failed to notify user {user_id}: {e}")

# --- Cleanup Function ---
def cleanup():
    logger.warning("Shutdown. Cleaning up processes...")
    script_keys_to_stop = list(bot_scripts.keys()) 
    if not script_keys_to_stop: logger.info("No scripts running. Exiting."); return
    logger.info(f"Stopping {len(script_keys_to_stop)} scripts...")
    for key in script_keys_to_stop:
        if key in bot_scripts: logger.info(f"Stopping: {key}"); kill_process_tree(bot_scripts[key])
        else: logger.info(f"Script {key} already removed.")
    logger.warning("Cleanup finished.")
atexit.register(cleanup)

# --- Main Execution ---
def _auto_resource_cleaner():
    """Safely clean unused Python objects and bot-owned temporary files every 10s.

    RAM: gc.collect() releases unreachable Python objects; Python cannot safely
    guarantee that exactly 150 MB will be returned to the OS.
    Disk: removes only old temporary directories created by this bot, up to
    500 MB per cycle. User uploads, database files and arbitrary system files
    are never deleted by this cleaner.
    """
    temp_root = tempfile.gettempdir()
    prefixes = ("user_",)
    while True:
        try:
            collected = gc.collect()
            logger.debug(f"[ResourceCleaner] GC collected {collected} objects")
        except Exception as e:
            logger.warning(f"[ResourceCleaner] RAM cleanup error: {e}")

        # Safely reclaim up to 500 MB from bot-created temporary ZIP/script dirs.
        freed = 0
        target = 500 * 1024 * 1024
        try:
            candidates = []
            now = time.time()
            for name in os.listdir(temp_root):
                if not name.startswith(prefixes):
                    continue
                path = os.path.join(temp_root, name)
                try:
                    if not os.path.isdir(path):
                        continue
                    # Do not touch a temp directory that may still be in use.
                    age = now - os.path.getmtime(path)
                    if age < 600:  # 10 minutes safety window
                        continue
                    size = 0
                    for root, dirs, files in os.walk(path):
                        for fname in files:
                            try:
                                size += os.path.getsize(os.path.join(root, fname))
                            except OSError:
                                pass
                    candidates.append((os.path.getmtime(path), path, size))
                except OSError:
                    continue

            candidates.sort(key=lambda item: item[0])
            for _, path, size in candidates:
                if freed >= target:
                    break
                try:
                    shutil.rmtree(path)
                    freed += size
                except OSError as e:
                    logger.debug(f"[ResourceCleaner] Could not remove {path}: {e}")

            if freed:
                logger.info(f"[ResourceCleaner] Disk cleanup freed ~{freed / 1024 / 1024:.1f} MB")
        except Exception as e:
            logger.warning(f"[ResourceCleaner] Disk cleanup error: {e}")

        time.sleep(10)

if __name__ == '__main__':
    resource_cleaner_thread = threading.Thread(target=_auto_resource_cleaner, daemon=True, name="ResourceCleaner")
    resource_cleaner_thread.start()
    logger.info("🧹 Auto resource cleaner started (every 10s): GC + up to 500MB bot-temp disk cleanup")

    logger.info("="*50 + "\n🤖 MASTER Hosting Bot Starting Up...\n" + f"🐍 Python: {sys.version.split()[0]}\n" +
                f"🔧 Base Dir: {BASE_DIR}\n📁 Upload Dir: {UPLOAD_BOTS_DIR}\n" +
                f"📊 Data Dir: {IROTECH_DIR}\n🔑 Owner ID: {OWNER_ID}\n🛡️ Admins: {len(admin_ids)}\n" +
                f"🚫 Banned Users: {len(banned_users)}\n📢 Mandatory Channels: {len(mandatory_channels)}\n" + "="*50)
    keep_alive()
    logger.info("🚀 Starting Telegram polling...")

    while True:
        try:
            bot.infinity_polling(
                logger_level=logging.INFO,
                timeout=60,
                long_polling_timeout=30,
                none_stop=True,
                interval=0
            )

        except requests.exceptions.RequestException as req_err:
            # Temporary Telegram/network issue: do not let it terminate the PM2 process.
            logger.warning(f"🌐 Telegram request error: {req_err}")
            logger.info("🔄 Retrying Telegram polling in 10 seconds...")
            time.sleep(10)

        except Exception as e:
            # Telegram 409 = another instance is using the same bot token
            error_code = getattr(e, "error_code", None)
            error_text = str(e)

            if error_code == 409 or "Error code: 409" in error_text or "Conflict" in error_text:
                logger.critical(
                    "❌ TELEGRAM 409 CONFLICT: Another instance of this bot "
                    "is already running with the same token."
                )
                logger.critical(
                    "🛑 Stopping this polling instance. "
                    "Do NOT restart automatically."
                )
                break

            logger.critical(
                f"💥 Polling error: {e}",
                exc_info=True
            )
            logger.info("🔄 Restarting polling in 30 seconds...")
            time.sleep(30)

        else:
            logger.warning(
                "⚠️ Telegram polling stopped normally. "
                "Restarting in 5 seconds..."
            )
            time.sleep(5)

        finally:
            logger.info("📡 Polling cycle finished.")
