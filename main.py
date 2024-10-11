import discord
import os
import re
from discord.app_commands import describe
from discord.ext import commands
from discord.ext.commands import Context
from dotenv import load_dotenv
from datetime import datetime
from pytz import timezone

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

TIMEZONES = {
    "EST": "America/New_York",
    "PST": "America/Los_Angeles",
    "CST": "America/Chicago",
    "MST": "America/Denver",
    "BST": "Europe/London",
    "CET": "Europe/Paris",
    "IST": "Asia/Kolkata",
    "JST": "Asia/Tokyo",
    "AEST": "Australia/Sydney"
}

# Time format
format = "%Y-%m-%d %I:%M %p %Z"
global_time_format = "%I:%M %p"

intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user} successfully logged in")

def parse_time_and_timezone(content):
    pattern = r'<(\d{1,2}:\d{2})([APMapm]{2}) ([A-Z]+)>'
    match = re.search(pattern, content)
    
    if match:
        time_str = match.group(1) 
        am_pm = match.group(2)    
        tz = match.group(3)      

        return time_str, am_pm, tz
    return None

def convert_time_to_timezones(time_str, am_pm, from_tz):
    try:
        time_format = "%I:%M %p"
        full_time_str = f"{time_str} {am_pm}"
        
        from_tz_obj = timezone(TIMEZONES[from_tz])
        now = datetime.now()
        dt = datetime.strptime(full_time_str, time_format)
        dt = from_tz_obj.localize(datetime.combine(now.date(), dt.time())) 


        converted_times = {}
        for tz_name, tz_string in TIMEZONES.items():
            target_tz = timezone(tz_string)
            converted_time = dt.astimezone(target_tz).strftime(global_time_format)
            if tz_name != from_tz:
                converted_times[tz_name] = converted_time
        return converted_times
    except Exception as e:
        print(f"Error during time conversion: {e}")
        return None

@bot.event
async def on_message(message: discord.Message):
    if message.author == bot.user:
        return

    parsed = parse_time_and_timezone(message.content)

    if not parsed:
        return
        # await message.channel.send("Please use the format `<6:00AM EST>` to specify time and timezone.")
    else:
        time_str, am_pm, tz = parsed
        if tz not in TIMEZONES:
            await message.channel.send(f"Timezone `{tz}` is not recognized.")
            return

        converted_times = convert_time_to_timezones(time_str, am_pm, tz)
        if not converted_times:
            await message.channel.send("Sorry, I couldn't convert the time.")
            return
        else:
            description = ""
            for tz_name, full_time in converted_times.items():
                description += f"{tz_name:<5} ➡️ {full_time}\n"
            
            embed = discord.Embed(
                title=f"🕒 **{time_str} {am_pm} {tz} in other timezones:**",
                description=f"```md\n{description}```",  
                colour=0x00aff5,
                timestamp=datetime.now()
            )
            
            embed.set_footer(
                text="Converted Timezones",
                icon_url="https://slate.dan.onl/slate.png"
            )
            
            await message.channel.send(embed=embed)


if BOT_TOKEN is not None:
    bot.run(BOT_TOKEN)
else:
    print("BOT_TOKEN is missing")
