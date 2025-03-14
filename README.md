# Server Monitor Discord Bot

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![discord.py](https://img.shields.io/badge/discord-py-blue.svg)](https://github.com/Rapptz/discord.py)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)
[![Open Source Love](https://badges.frapsoft.com/os/v1/open-source.png?v=103)](https://github.com/ellerbrock/open-source-badges/)

A Discord bot that monitors and displays your server's system metrics in real-time, including CPU usage, RAM usage, disk space, network activity, and more.

![Bot Preview](https://i.postimg.cc/pr6rxcTm/Screenshot-2025-03-15-at-1-18-52-AM.png)

## Table of Contents
- [Features](#features)
- [Screenshots](#screenshots)
- [Commands](#commands)
- [Setup Instructions](#setup-instructions)
  - [Prerequisites](#prerequisites)
  - [Discord Bot Setup](#step-1-create-a-discord-bot)
  - [Server Installation](#step-3-set-up-the-bot-on-your-server)
- [Running as a Service](#running-as-a-service-linux)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Customization](#customization)
- [Troubleshooting](#troubleshooting)
- [Security Notes](#security-notes)
- [Contributing](#contributing)
- [License](#license)

## Features

- Real-time monitoring of system resources through Discord embeds
- Auto-updating statistics in a designated channel at configurable intervals
- Individual commands to check specific metrics on demand
- Clean, visual representation of data with progress bars
- Cross-platform compatibility (Linux, Windows, macOS)
- Separate tracking of server uptime (via neofetch) and bot uptime
- Temperature monitoring when available
- Network statistics including data sent/received

## Screenshots

*Add screenshots of your bot in action here*

## Commands

| Command | Description |
|---------|-------------|
| `!stats` | Show all server statistics in one embed |
| `!uptime` | Display both server and bot uptime |
| `!cpu` | Show detailed CPU information including usage and frequency |
| `!memory` | Show RAM and swap usage statistics with progress bars |
| `!disk` | Show disk usage, capacity, and I/O statistics |
| `!network` | Show network usage statistics (sent/received) |
| `!help_monitor` | Display help information about available commands |

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- A Discord account and a registered bot
- Permissions to add bots to your Discord server
- neofetch installed (optional, for accurate server uptime)

### Step 1: Create a Discord Bot

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name
3. Navigate to the "Bot" tab and click "Add Bot"
4. Under the "Privileged Gateway Intents" section, enable "Message Content Intent"
5. Copy your bot token (you'll need this later)

### Step 2: Invite the Bot to Your Server

1. In the Developer Portal, go to the "OAuth2" tab
2. In the "URL Generator" section, select the "bot" scope
3. Select the following permissions:
   - Read Messages/View Channels
   - Send Messages
   - Embed Links
   - Read Message History
4. Copy the generated URL and open it in your browser
5. Select your server and authorize the bot

### Step 3: Set Up the Bot on Your Server

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/server-monitor-bot.git
   cd server-monitor-bot
   ```

2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your bot token and channel ID:
   ```
   DISCORD_TOKEN=your_discord_token_here
   MONITOR_CHANNEL_ID=your_channel_id_here
   UPDATE_INTERVAL=60  # Update interval in seconds
   ```
   
   To get a channel ID, enable Developer Mode in Discord (Settings > Advanced), 
   then right-click on the channel and select "Copy ID"

5. Run the bot:
   ```bash
   python server_monitor_bot.py
   ```

## Running as a Service (Linux)

To keep the bot running in the background on Linux, you can set it up as a systemd service:

1. Create a service file:
   ```bash
   sudo nano /etc/systemd/system/discord-monitor.service
   ```

2. Add the following content (adjust paths as needed):
   ```ini
   [Unit]
   Description=Discord Server Monitor Bot
   After=network.target

   [Service]
   User=your_username
   WorkingDirectory=/path/to/bot/directory
   ExecStart=/usr/bin/python3 /path/to/bot/directory/server_monitor_bot.py
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

3. Enable and start the service:
   ```bash
   sudo systemctl enable discord-monitor
   sudo systemctl start discord-monitor
   ```

4. Check the status:
   ```bash
   sudo systemctl status discord-monitor
   ```

## Project Structure

```
server-monitor-bot/
├── server_monitor_bot.py # Main bot script
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables (not committed to git)
├── .env.example          # Example environment file (safe to commit)
├── README.md             # This documentation
└── LICENSE               # MIT License file
```

## Configuration

The bot is configured using environment variables in the `.env` file:

| Variable | Description | Default |
|----------|-------------|---------|
| DISCORD_TOKEN | Your Discord bot token | Required |
| MONITOR_CHANNEL_ID | Channel ID for auto-updates | Required |
| UPDATE_INTERVAL | Time between updates (seconds) | 60 |

## Customization

You can customize the bot by:

- Changing the command prefix (default is `!`) in the bot initialization
- Modifying the embed colors in `create_stats_embed` and other embed creation functions
- Adding additional system metrics by extending the psutil usage
- Adjusting the progress bar appearance in the `create_progress_bar` function
- Changing the emoji icons used in the embed fields

To modify the update interval, simply change the `UPDATE_INTERVAL` in your `.env` file.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Bot doesn't start | Verify your Discord token is correct |
| Metrics not showing | Ensure the bot has the necessary permissions |
| "NotFound" errors | Verify the channel ID is correct |
| Server uptime showing "Unknown" | Install neofetch (`sudo apt install neofetch` on Debian/Ubuntu) |
| Temperature not showing | Temperature monitoring may not be available on all systems |
| Bot crashes after a while | Check your system's memory usage or set up the systemd service for auto-restart |

## Security Notes

- **IMPORTANT:** Never commit your `.env` file to a public repository as it contains your Discord token
- Add `.env` to your `.gitignore` file to prevent accidental commits
- Periodically rotate your Discord token, especially if you suspect it may have been compromised
- The bot only requires the minimum necessary permissions to function

## Contributing

Contributions are welcome! Here's how you can contribute:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add some amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

Please make sure to update tests as appropriate and adhere to the existing code style.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Created with ❤️ by [Your Name]

If you find this bot useful, please consider giving it a star on GitHub!
