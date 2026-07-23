# Telegram Post Bot

A powerful Telegram bot for managing and publishing posts to channels. Built with Aiogram 3.x and JSON database.

## Features

- **Multi-Channel Management**: Add and manage multiple Telegram channels
- **Rich Post Creation**: Create posts with photos, text, and inline buttons
- **Preview System**: Preview your post before publishing
- **Easy Setup**: Simple channel integration with admin rights requirement
- **JSON Database**: Lightweight data storage using JSON files

## How It Works

1. **Start**: Use `/start` to begin
2. **Add Channel**: Invite the bot to your channel with admin privileges
3. **Create Post**: 
   - Select channel
   - Add photo (or skip with "нет")
   - Add text (or skip with "нет") 
   - Add button in format `[Button Text + URL]` (or skip with "нет")
4. **Publish**: Preview and publish to your channel

## Installation

1. Unpack the archive to a place convenient for you
2. Open the project in PyCharm and write in the treterminal command pip install aiogram==3.3.0 python-dotenv==1.0.0 
3. Change the TOKEN of the bot in the .env file
4. Start the bot!
