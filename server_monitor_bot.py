"""
Server Monitor Discord Bot

A Discord bot that monitors and displays server system metrics in real-time,
including CPU usage, RAM usage, disk space, network activity, and more.

This bot uses discord.py and psutil to gather and display system information
in a clean, visual format through Discord embeds.

MIT License

Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
"""

import discord
from discord.ext import commands, tasks
import psutil
import platform
import time
import datetime
import os
import subprocess
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Bot configuration
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
MONITOR_CHANNEL_ID = int(os.getenv('MONITOR_CHANNEL_ID', 0))
UPDATE_INTERVAL = int(os.getenv('UPDATE_INTERVAL', 60))  # Update interval in seconds

# Initialize bot with intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Store the message ID for updating
monitor_message_id = None
bot_start_time = time.time()

def get_server_uptime():
    """Get the server uptime using neofetch command"""
    try:
        # Run neofetch command and capture output
        result = subprocess.run(['neofetch', '--stdout'], capture_output=True, text=True)
        output = result.stdout

        # Extract uptime using regex
        uptime_match = re.search(r'Uptime: (.+)', output)
        if uptime_match:
            return uptime_match.group(1).strip()

        # Fallback if the specific pattern isn't found
        uptime_match = re.search(r'up (.+?)(,|\n)', output)
        if uptime_match:
            return uptime_match.group(1).strip()

        return "Unknown (neofetch available but format not recognized)"
    except (subprocess.SubprocessError, FileNotFoundError) as e:
        print(f"Error running neofetch: {e}")
        # Fallback method if neofetch isn't available
        try:
            if platform.system() == "Linux":
                # Try using the uptime command on Linux
                result = subprocess.run(['uptime', '-p'], capture_output=True, text=True)
                return result.stdout.strip().replace('up ', '')
            elif platform.system() == "Darwin":  # macOS
                result = subprocess.run(['uptime'], capture_output=True, text=True)
                uptime_match = re.search(r'up (.+?),', result.stdout)
                if uptime_match:
                    return uptime_match.group(1).strip()
        except Exception as e:
            print(f"Error getting uptime: {e}")

        # If all else fails, return a message
        return "Unknown (neofetch not available)"

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    print(f'Bot is in {len(bot.guilds)} guilds')
    
    # Start the background task for updating server stats
    update_stats.start()

@tasks.loop(seconds=UPDATE_INTERVAL)
async def update_stats():
    """Background task to update server stats periodically"""
    if MONITOR_CHANNEL_ID == 0:
        print("Error: MONITOR_CHANNEL_ID is not set.")
        return

    channel = bot.get_channel(MONITOR_CHANNEL_ID)
    if not channel:
        print(f"Error: Could not find channel with ID {MONITOR_CHANNEL_ID}")
        return

    embed = create_stats_embed()

    global monitor_message_id
    if monitor_message_id:
        try:
            # Try to edit the existing message
            message = await channel.fetch_message(monitor_message_id)
            await message.edit(embed=embed)
        except discord.NotFound:
            # If message was deleted, send a new one
            message = await channel.send(embed=embed)
            monitor_message_id = message.id
        except discord.Forbidden:
            print(f"Error: Missing permissions to edit message in channel {MONITOR_CHANNEL_ID}")
            return
        except discord.HTTPException as e:
            print(f"Error editing message: {e}")
            return
    else:
        try:
            # Send initial message
            message = await channel.send(embed=embed)
            monitor_message_id = message.id
        except discord.Forbidden:
            print(f"Error: Missing permissions to send message in channel {MONITOR_CHANNEL_ID}")
            return
        except discord.HTTPException as e:
            print(f"Error sending message: {e}")
            return

@update_stats.before_loop
async def before_update_stats():
    """Wait until the bot is ready before starting the task"""
    await bot.wait_until_ready()

def create_stats_embed():
    """Create a Discord embed with server stats"""
    # Get system information
    cpu_usage = psutil.cpu_percent(interval=1)
    cpu_freq = psutil.cpu_freq()
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    disk_io = psutil.disk_io_counters()
    net_io = psutil.net_io_counters()

    # Get server uptime from neofetch
    server_uptime = get_server_uptime()

    # Calculate bot uptime
    bot_uptime_seconds = int(time.time() - bot_start_time)
    bot_uptime = str(datetime.timedelta(seconds=bot_uptime_seconds))

    # Create embed
    embed = discord.Embed(
        title="🖥️ Server Monitor",
        description=f"Stats for **{platform.node()}**",
        color=0x1E90FF,  # DodgerBlue
        timestamp=datetime.datetime.now()
    )

    # Add system info fields
    embed.add_field(name="🔄 System", value=f"{platform.system()} {platform.release()}", inline=True)
    embed.add_field(name="⏱️ Server Uptime", value=server_uptime, inline=True)
    embed.add_field(name="🤖 Bot Uptime", value=bot_uptime, inline=True)

    # Add CPU usage with frequency
    embed.add_field(name="🧠 CPU Usage", value=f"{cpu_usage}%", inline=True)
    if cpu_freq:
        embed.add_field(
            name="CPU Frequency",
            value=f"Current: {cpu_freq.current:.2f} MHz\nMax: {cpu_freq.max:.2f} MHz",
            inline=True
        )

    # Add memory usage with progress bar
    mem_percent = memory.percent
    mem_bar = create_progress_bar(mem_percent)
    embed.add_field(
        name="💾 Memory Usage",
        value=f"{mem_bar} {mem_percent}%\n{memory.used // (1024**2)} MB / {memory.total // (1024**2)} MB",
        inline=False
    )

    # Add disk usage with progress bar
    disk_percent = disk.percent
    disk_bar = create_progress_bar(disk_percent)
    embed.add_field(
        name="💿 Disk Usage",
        value=f"{disk_bar} {disk_percent}%\n{disk.used // (1024**3)} GB / {disk.total // (1024**3)} GB",
        inline=False
    )

    # Add disk I/O stats
    embed.add_field(
        name="Disk I/O",
        value=f"Read: {disk_io.read_bytes // (1024**2)} MB\nWritten: {disk_io.write_bytes // (1024**2)} MB",
        inline=True
    )

    # Add network info
    embed.add_field(
        name="🌐 Network",
        value=f"Sent: {net_io.bytes_sent // (1024**2)} MB\nReceived: {net_io.bytes_recv // (1024**2)} MB",
        inline=True
    )

    # Add temperatures if available
    try:
        temps = psutil.sensors_temperatures()
        if temps:
            temp_text = ""
            for name, entries in temps.items():
                for entry in entries:
                    temp_text += f"{entry.label or name}: {entry.current}°C\n"
            if temp_text:
                embed.add_field(name="🌡️ Temperatures", value=temp_text.strip(), inline=True)
    except:
        pass  # Temperatures might not be available on all systems

    embed.set_footer(text=f"Last updated • Auto-updates every {UPDATE_INTERVAL} seconds")
    return embed

def create_progress_bar(percent, length=10):
    """Create a text-based progress bar"""
    filled_length = int(length * percent / 100)
    bar = '█' * filled_length + '░' * (length - filled_length)
    return bar

@bot.command(name='stats')
async def stats(ctx):
    """Command to show current server stats"""
    embed = create_stats_embed()
    embed.color = 0x32CD32  # LimeGreen
    await ctx.send(embed=embed)

@bot.command(name='uptime')
async def uptime(ctx):
    """Command to show server and bot uptime"""
    # Get server uptime from neofetch
    server_uptime = get_server_uptime()

    # Calculate bot uptime
    bot_uptime_seconds = int(time.time() - bot_start_time)
    bot_uptime = str(datetime.timedelta(seconds=bot_uptime_seconds))

    embed = discord.Embed(
        title="⏱️ Uptime Information",
        color=0xFFA500,  # Orange
        timestamp=datetime.datetime.now()
    )

    embed.add_field(name="️ Server Uptime", value=server_uptime, inline=False)
    embed.add_field(name="🤖 Bot Uptime", value=bot_uptime, inline=False)

    await ctx.send(embed=embed)

@bot.command(name='cpu')
async def cpu(ctx):
    """Command to show CPU usage"""
    cpu_usage = psutil.cpu_percent(interval=1)
    cpu_count = psutil.cpu_count()
    cpu_freq = psutil.cpu_freq()
    cpu_times = psutil.cpu_times()

    embed = discord.Embed(
        title="🧠 CPU Information",
        color=0x1E90FF,  # DodgerBlue
        timestamp=datetime.datetime.now()
    )

    embed.add_field(name="Usage", value=f"{cpu_usage}%", inline=True)
    embed.add_field(name="Cores", value=f"{cpu_count}", inline=True)

    if cpu_freq:
        embed.add_field(
            name="Frequency",
            value=f"Current: {cpu_freq.current:.2f} MHz\nMax: {cpu_freq.max:.2f} MHz",
            inline=True
        )

    embed.add_field(
        name="Time Spent",
        value=f"User: {cpu_times.user:.2f}s\nSystem: {cpu_times.system:.2f}s\nIdle: {cpu_times.idle:.2f}s",
        inline=False
    )

    await ctx.send(embed=embed)

@bot.command(name='memory', aliases=['ram'])
async def memory(ctx):
    """Command to show memory usage"""
    memory = psutil.virtual_memory()
    swap = psutil.swap_memory()

    embed = discord.Embed(
        title="💾 Memory Information",
        color=0xFF69B4,  # HotPink
        timestamp=datetime.datetime.now()
    )

    mem_bar = create_progress_bar(memory.percent)
    embed.add_field(
        name="RAM Usage",
        value=f"{mem_bar} {memory.percent}%\n{memory.used // (1024**2)} MB / {memory.total // (1024**2)} MB",
        inline=False
    )

    swap_bar = create_progress_bar(swap.percent)
    embed.add_field(
        name="Swap Usage",
        value=f"{swap_bar} {swap.percent}%\n{swap.used // (1024**2)} MB / {swap.total // (1024**2)} MB",
        inline=False
    )

    embed.add_field(
        name="Memory Details",
        value=f"Available: {memory.available // (1024**2)} MB\nCached: {memory.cached // (1024**2)} MB\nBuffers: {memory.buffers // (1024**2)} MB",
        inline=False
    )

    await ctx.send(embed=embed)

@bot.command(name='disk')
async def disk(ctx):
    """Command to show disk usage"""
    disk = psutil.disk_usage('/')
    disk_io = psutil.disk_io_counters()

    embed = discord.Embed(
        title="💿 Disk Information",
        color=0xFFD700,  # Gold
        timestamp=datetime.datetime.now()
    )

    disk_bar = create_progress_bar(disk.percent)
    embed.add_field(
        name="Disk Usage",
        value=f"{disk_bar} {disk.percent}%\n{disk.used // (1024**3)} GB / {disk.total // (1024**3)} GB",
        inline=False
    )

    embed.add_field(
        name="Disk I/O",
        value=f"Read: {disk_io.read_bytes // (1024**2)} MB\nWritten: {disk_io.write_bytes // (1024**2)} MB",
        inline=True
    )

    embed.add_field(
        name="Disk Details",
        value=f"Free: {disk.free // (1024**3)} GB\nUsed: {disk.used // (1024**3)} GB\nTotal: {disk.total // (1024**3)} GB",
        inline=False
    )

    await ctx.send(embed=embed)

@bot.command(name='network', aliases=['net'])
async def network(ctx):
    """Command to show network usage"""
    net_io = psutil.net_io_counters()
    net_connections = psutil.net_connections()

    embed = discord.Embed(
        title="🌐 Network Information",
        color=0x8A2BE2,  # BlueViolet
        timestamp=datetime.datetime.now()
    )

    embed.add_field(
        name="Data Transferred",
        value=f"Sent: {net_io.bytes_sent // (1024**2)} MB\nReceived: {net_io.bytes_recv // (1024**2)} MB",
        inline=True
    )

    embed.add_field(
        name="Packets",
        value=f"Sent: {net_io.packets_sent}\nReceived: {net_io.packets_recv}",
        inline=True
    )

    embed.add_field(
        name="Network Connections",
        value=f"Total: {len(net_connections)}\nEstablished: {len([conn for conn in net_connections if conn.status == 'ESTABLISHED'])}",
        inline=False
    )

    await ctx.send(embed=embed)

@bot.command(name='help_monitor')
async def help_monitor(ctx):
    """Show help for the monitor commands"""
    embed = discord.Embed(
        title="📊 Server Monitor Help",
        description="Available commands for the server monitor bot",
        color=0x0088ff
    )
    
    commands_list = [
        ("!stats", "Show all server statistics"),
        ("!uptime", "Show both server and bot uptime"),
        ("!cpu", "Show CPU usage and information"),
        ("!memory", "Show RAM usage and information"),
        ("!disk", "Show disk usage and information"),
        ("!network", "Show network usage and information"),
        ("!help_monitor", "Show this help message")
    ]
    
    for cmd, desc in commands_list:
        embed.add_field(name=cmd, value=desc, inline=False)
    
    embed.set_footer(text="Server stats are automatically updated in the monitoring channel")
    await ctx.send(embed=embed)

# Run the bot
if __name__ == "__main__":
    if not DISCORD_TOKEN:
        print("Error: No Discord token provided. Please set the DISCORD_TOKEN environment variable.")
    else:
        bot.run(DISCORD_TOKEN)
