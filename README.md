<p align="center">
  <img src="https://img.shields.io/badge/version-1.0.0-blue?style=flat-square" />
  <img src="https://img.shields.io/badge/status-stable-brightgreen?style=flat-square" />
  <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" />
  <img src="https://img.shields.io/badge/python-3.10+-blue?style=flat-square&logo=python" />
  <img src="https://img.shields.io/badge/discord.py-2.x-blueviolet?style=flat-square&logo=discord" />
</p>

# 🌐 Polyglot — Ephemeral Message Translator

**Polyglot** lets you add on-the-fly, ephemeral translations directly in your Discord server. Users can choose a language via a dropdown under any message in configured channels, and receive a private (ephemeral) embed with the translated text. Administrators can configure which text channels and which target languages are available — no more clutter, only the translations you need.

## 🛠️ Features
- 🔄 Automatic Translation Panel.
Adds a language dropdown under messages in configured channels.

- 👻 Ephemeral Translations.
Translated text appears only to the user who selected the language.

- 🛠️ Admin Commands.
Easily configure which channels and languages are enabled.

- 🌍 Multi-language Support.
All bot messages are fully localizable via simple JSON file.

- 🧩 Zero Database.
All settings are stored in editable local JSON file.

## 🚀 Getting Started

```bash
# 1. Clone the repository
git clone https://github.com/VarikSoft/polyglot-bot.git
cd polyglot-bot

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create a .env file in the project root
#    See “🔐 .env File Example” below

# 4. Run the bot
python bot.py
```

## 📁 Project Structure
```bash
polyglot/
├── lang/
│ ├── en.json
│ └── ru.json
├── bot.py
├── config.json
├── .env
```

## 🧰 Slash Commands
- `/add_translate_channel` – Add a text channel for translation.
- `/remove_translate_channel` – Remove a translation channel.
- `/list_translate_channels` – List configured translation channels.
- `/add_translate_language` – Add a target language.
- `/remove_translate_language` – Remove a previously added language.
- `/list_translate_languages` – List available languages.
- `/set_locale` – Set the bot’s interface language for this server.

## ⚙️ Configuration
### 🔐 .env File Example
.env — Environment Variables

```bash
TOKEN=your_discord_bot_token
CONFIG_FILE=config.json     # optional, defaults to config.json
LANG_DIR=lang               # optional, defaults to lang/
```

### config.json — Guild Settings
```json
{
  "123456789012345678": {
    "channels": [111111111111111111],
    "languages": ["en", "ru", "fr"],
    "locale": "en"
  }
}
```

## 📄 en.json Example
```json
{
  "channel_already": "❗ Channel is already configured.",
  "channel_added": "✅ Channel {channel} added to auto-translate.",
  "channel_not_found": "❗ Channel not found in configuration.",
  "channel_removed": "✅ Channel {channel} removed from auto-translate.",
  "no_channels": "🚫 No channels configured.",
  "list_channels": "📜 Configured auto-translate channels:",
  "lang_not_supported": "❌ Language “{lang}” is not supported.",
  "lang_already": "❗ Language already added.",
  "lang_added": "✅ Language **{lang}** added to auto-translate.",
  "lang_not_found": "❗ Language “{lang}” not found in configuration.",
  "lang_removed": "✅ Language **{lang}** removed from auto-translate.",
  "list_languages": "🌐 Auto-translate languages:",
  "select_placeholder": "Choose a language to translate…",
  "embed_title": "Translation to {lang}",
  "translate_error": "❌ An error occurred while translating.",
  "reply_prompt": "Choose a language to translate:",
  "cmd_add_channel": "Add a channel to auto-translate",
  "cmd_remove_channel": "Remove a channel from auto-translate",
  "cmd_list_channels": "List configured auto-translate channels",
  "cmd_add_lang": "Add a language to auto-translate",
  "cmd_remove_lang": "Remove a language from auto-translate",
  "cmd_list_langs": "List auto-translate languages",
  "cmd_set_locale": "Set the bot interface language"
}
```

## 🛠️ Make It Yours

Customize **Polyglot** to fit your server’s personality and needs.  
From languages to looks — it’s all in your hands!
