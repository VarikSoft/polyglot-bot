import os
import json
import asyncio
from dotenv import load_dotenv
import discord
from discord import app_commands
from discord.ext import commands
from deep_translator import GoogleTranslator

# ——— Environment Configuration ———————————————————————————————————————
load_dotenv()
TOKEN       = os.getenv("TOKEN")
CONFIG_FILE = os.getenv("CONFIG_FILE", "config.json")
LANG_DIR    = os.getenv("LANG_DIR", "lang")

# ——— Default Languages ———————————————————————————————————————
DEFAULT_LANGUAGES = ["en", "ru", "es", "fr", "de"]

# ——— Localization ———————————————————————————————————————
# Load interface translations from JSON files in LANG_DIR
TRANSLATIONS = {}
for filename in os.listdir(LANG_DIR):
    if filename.endswith(".json"):
        locale = filename[:-5]  # strip ".json"
        path = os.path.join(LANG_DIR, filename)
        with open(path, encoding="utf-8") as f:
            TRANSLATIONS[locale] = json.load(f)

def t(guild_id: int, key: str, **kwargs) -> str:
    """
    Fetch a translated interface string for the guild's locale.
    Falls back to English or to the key itself.
    """
    gid    = str(guild_id)
    guildc = config.get(gid, {})
    locale = guildc.get("locale", "en")
    text   = TRANSLATIONS.get(locale, {}).get(key) \
           or TRANSLATIONS["en"].get(key) \
           or key
    return text.format(**kwargs)

# ——— Translator & Language Data ———————————————————————————————————————
_translator = GoogleTranslator(source="auto", target="en")
# supported: { name: code }
_supported = _translator.get_supported_languages(as_dict=True)
# LANGUAGES: { code: EnglishName }
LANGUAGES = {code: name.title() for name, code in _supported.items()}

# Native (endonym) names for default languages
NATIVE_LANGUAGES = {
    "en": "English",
    "ru": "Русский",
    "es": "Español",
    "fr": "Français",
    "de": "Deutsch"
}

# ——— Config Management ———————————————————————————————————————
def load_config() -> dict:
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_config(cfg: dict):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)

config = load_config()

def get_guild_config(guild_id: int) -> dict:
    """
    Ensure a config entry exists for the guild,
    initialize default channels, languages, and locale.
    """
    gid = str(guild_id)
    if gid not in config:
        config[gid] = {
            "channels": [],
            "languages": DEFAULT_LANGUAGES.copy(),
            "locale": "en"
        }
    entry = config[gid]
    if not entry.get("languages"):
        entry["languages"] = DEFAULT_LANGUAGES.copy()
    if entry.get("locale") not in TRANSLATIONS:
        entry["locale"] = "en"
    save_config(config)
    return entry

# ——— Autocomplete Callbacks ———————————————————————————————————————
async def add_language_autocomplete(interaction: discord.Interaction, current: str):
    """
    Suggest any supported language from Google as user types.
    """
    suggestions = []
    lower = current.lower()
    for name, code in _supported.items():
        if lower in name or lower in code.lower():
            disp = NATIVE_LANGUAGES.get(code, name.title())
            suggestions.append(app_commands.Choice(
                name=f"{disp} ({code})", value=code
            ))
            if len(suggestions) >= 25:
                break
    return suggestions

async def remove_language_autocomplete(interaction: discord.Interaction, current: str):
    """
    Suggest only the languages already added on this server.
    """
    cfg = get_guild_config(interaction.guild_id)
    suggestions = []
    lower = current.lower()
    for code in cfg["languages"]:
        disp = NATIVE_LANGUAGES.get(code, LANGUAGES.get(code, code))
        if lower in disp.lower() or lower in code.lower():
            suggestions.append(app_commands.Choice(
                name=f"{disp} ({code})", value=code
            ))
            if len(suggestions) >= 25:
                break
    return suggestions

# ——— Bot & Command Setup ———————————————————————————————————————
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ——— Admin Commands: Channel Management ———————————————————————————————————————
@bot.tree.command(
    name="add_translate_channel",
    description="Add a channel for auto-translation"
)
@app_commands.checks.has_permissions(administrator=True)
async def add_translate_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    cfg = get_guild_config(interaction.guild_id)
    if channel.id in cfg["channels"]:
        return await interaction.response.send_message(
            t(interaction.guild_id, "channel_already"), ephemeral=True
        )
    cfg["channels"].append(channel.id)
    save_config(config)
    await interaction.response.send_message(
        t(interaction.guild_id, "channel_added", channel=channel.mention),
        ephemeral=True
    )

@bot.tree.command(
    name="remove_translate_channel",
    description="Remove a channel from auto-translation"
)
@app_commands.checks.has_permissions(administrator=True)
async def remove_translate_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    cfg = get_guild_config(interaction.guild_id)
    if channel.id not in cfg["channels"]:
        return await interaction.response.send_message(
            t(interaction.guild_id, "channel_not_found"), ephemeral=True
        )
    cfg["channels"].remove(channel.id)
    save_config(config)
    await interaction.response.send_message(
        t(interaction.guild_id, "channel_removed", channel=channel.mention),
        ephemeral=True
    )

@bot.tree.command(
    name="list_translate_channels",
    description="List auto-translation channels"
)
@app_commands.checks.has_permissions(administrator=True)
async def list_translate_channels(interaction: discord.Interaction):
    cfg = get_guild_config(interaction.guild_id)
    if not cfg["channels"]:
        msg = t(interaction.guild_id, "no_channels")
    else:
        lines = "\n".join(f"<#{c}>" for c in cfg["channels"])
        msg = t(interaction.guild_id, "list_channels") + "\n" + lines
    await interaction.response.send_message(msg, ephemeral=True)

# ——— Admin Commands: Language Management ———————————————————————————————————————
@bot.tree.command(
    name="add_translate_language",
    description="Add a language for auto-translation"
)
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(language="Start typing a language")
@app_commands.autocomplete(language=add_language_autocomplete)
async def add_translate_language(interaction: discord.Interaction, language: str):
    cfg = get_guild_config(interaction.guild_id)
    code = language
    if code not in LANGUAGES:
        return await interaction.response.send_message(
            t(interaction.guild_id, "lang_not_supported", lang=language),
            ephemeral=True
        )
    if code in cfg["languages"]:
        return await interaction.response.send_message(
            t(interaction.guild_id, "lang_already"), ephemeral=True
        )
    # fetch native (endonym) dynamically
    try:
        native = await asyncio.to_thread(
            lambda: GoogleTranslator(source="en", target=code)
                          .translate(LANGUAGES[code])
        )
    except:
        native = LANGUAGES[code]
    NATIVE_LANGUAGES[code] = native
    cfg["languages"].append(code)
    save_config(config)
    await interaction.response.send_message(
        t(interaction.guild_id, "lang_added", lang=native),
        ephemeral=True
    )

@bot.tree.command(
    name="remove_translate_language",
    description="Remove a language from auto-translation"
)
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(language="Start typing a language")
@app_commands.autocomplete(language=remove_language_autocomplete)
async def remove_translate_language(interaction: discord.Interaction, language: str):
    cfg = get_guild_config(interaction.guild_id)
    code = language
    if code not in cfg["languages"]:
        return await interaction.response.send_message(
            t(interaction.guild_id, "lang_not_found", lang=language),
            ephemeral=True
        )
    native = NATIVE_LANGUAGES.get(code, LANGUAGES.get(code, code))
    cfg["languages"].remove(code)
    save_config(config)
    await interaction.response.send_message(
        t(interaction.guild_id, "lang_removed", lang=native),
        ephemeral=True
    )

@bot.tree.command(
    name="list_translate_languages",
    description="List auto-translation languages"
)
@app_commands.checks.has_permissions(administrator=True)
async def list_translate_languages(interaction: discord.Interaction):
    cfg = get_guild_config(interaction.guild_id)
    natives = [NATIVE_LANGUAGES.get(c, LANGUAGES[c]) for c in cfg["languages"]]
    lines = "\n".join(f"- {n}" for n in natives)
    await interaction.response.send_message(
        t(interaction.guild_id, "list_languages") + "\n" + lines,
        ephemeral=True
    )

@bot.tree.command(
    name="set_locale",
    description="Set the bot interface language"
)
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(locale="Locale code, e.g. en, ru")
async def set_locale(interaction: discord.Interaction, locale: str):
    if locale not in TRANSLATIONS:
        return await interaction.response.send_message(
            f"❌ Locale `{locale}` not found.", ephemeral=True
        )
    cfg = get_guild_config(interaction.guild_id)
    cfg["locale"] = locale
    save_config(config)
    await interaction.response.send_message(
        t(interaction.guild_id, "locale_set", locale=locale),
        ephemeral=True
    )

# ——— UI: LanguageSelect & TranslateView ———————————————————————————————————————
class LanguageSelect(discord.ui.Select):
    def __init__(self, original_msg: discord.Message):
        cfg = get_guild_config(original_msg.guild.id)
        options = [
            discord.SelectOption(
                label=NATIVE_LANGUAGES.get(c, LANGUAGES[c]),
                value=c
            )
            for c in cfg["languages"]
        ]
        super().__init__(
            placeholder=t(original_msg.guild.id, "select_placeholder"),
            min_values=1,
            max_values=1,
            options=options
        )
        self.original = original_msg

    async def callback(self, interaction: discord.Interaction):
        dest = self.values[0]
        try:
            text = await asyncio.to_thread(
                lambda: GoogleTranslator(source="auto", target=dest)
                               .translate(self.original.content)
            )
            title = t(interaction.guild_id, "embed_title", lang=NATIVE_LANGUAGES.get(dest, LANGUAGES[dest]))
            embed = discord.Embed(title=title, description=text, color=0x00AE86)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except:
            await interaction.response.send_message(
                t(interaction.guild_id, "translate_error"),
                ephemeral=True
            )

class TranslateView(discord.ui.View):
    def __init__(self, original_msg: discord.Message):
        super().__init__(timeout=None)
        self.add_item(LanguageSelect(original_msg))

# ——— Event Handlers ———————————————————————————————————————
@bot.event
async def on_message(message: discord.Message):
    if message.author.bot or not message.guild:
        return
    cfg = get_guild_config(message.guild.id)
    if message.channel.id in cfg["channels"]:
        await message.reply(
            t(message.guild.id, "reply_prompt"),
            view=TranslateView(message)
        )
    await bot.process_commands(message)

# ——— Run Bot ———————————————————————————————————————
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    await bot.tree.sync()

bot.run(TOKEN)