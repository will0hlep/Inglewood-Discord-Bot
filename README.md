# Inglewood Discord Bot

A Python Discord designed to run in a Docker container.

## Functions

- Tracks the status of Minecraft Servers and updates a Discord message upon changes.
- Allows Discord users to ping all tracked Minecraft Servers.
- Allows Discord users to assign themselves roles via slash commands.
- Allows Discord users to assign roles to other users via slash commands.
- Allows Discord users to get a randomly rolled tier between I and XI, plus Wildcard, for World of Tanks.
  - Tiers can not repeat.
  - Tier I is limited to once per day.
  - The base odds of tiers I, II, III, and IV are halved.
  - Tiers I, II, and III are only available at certain times of day.
  - Tiers I, II, and III can be disabled entirely using the battle pass version of the command.
  - When tiers II, IV, V, VI, VII, and VIII are drawn, preferential status may be rolled with a 1 in 30 chance.
  - When preferential status is drawn at tier IV, double preferential status may be rolled with a 1 in 2 chance.

## Quick Start

In order to start the bot, download the `Dockerfile` and `inglewood.py` files. Then save them to a directory of your choosing. Next, create a `constants.py` file in the same directory.

### constants.py

Put the following in `constants.py`:

```
"""
This module defines constants.
"""

from mcstatus import JavaServer, BedrockServer, LegacyServer
import pytz

CONSTANTS = {
    #Minecraft Server Types
    "server_types" : {
        JavaServer: "Java",
        LegacyServer: "Java",
        BedrockServer: "Bedrock"
        },
    #Discord API values
    "token" : "___",
    "server_id" : ___,
    "channel_id" : ___,
    "user_id" : ___,
    #Bot Settings
    "time_zone" : pytz.timezone("___"),
    "daily_tier_reset_time" : ___,
    "low_tier_block_before" : ___,
    "low_tier_block_after" : ___,
    "server_msg_period" : ___,
    #Minecraft Server Addresses
    "domain" : "___",
    "minecraft_servers" : {
      ___
      }
}

```

Then fill in the following values for each of the keys:

- `token`, your bot's Discord api token as a string.
- `server_id`, your Discord server's ID as an integer.
- `channel_id`, the ID of the Discord channel containing the Minecraft server status message  as an integer.
- `user_id`, your Discord user ID as an integer.
- `time_zone`, your time zone described using the pytz package, for example `pytz.timezone('Europe/London')`.
  - A complete list of time zones can be obtained by running `pytz.all_timezones`.
- `daily_tier_reset_time`, the time of day to reset tier roll mechanics in seconds as an integer.
- `low_tier_block_before`, the earliest time of day at which low tiers can be rolled in seconds as an integer.
- `low_tier_block_after`, the latest time of day at which low tiers can be rolled in seconds as an integer.
- `server_msg_period`, the time between Minecraft server checks in seconds as an integer.
- `domain`, the domain or IP addresses of your Minecraft servers as a string.
- `minecraft_servers`, a further nested dictionary containing names, ports, and types of Minecraft servers to be monitored.

#### `minecraft_servers` Dictionary Structure

For each Minecraft server you want to monitor, include an entry in this dictionary where the key is the `SERVER_NAME` and the value is a nested dictionary.

Inside each nested dictionary should have the following keys:
- For a Java version 1.7 or later server, the nested dictionary should have a `JavaServer` key,
- For a Bedrock server, the nested dictionary should have a `BedrockServer` key,
- For a Java version Beta 1.8 to 1.6, the nested dictionary should have a `LegacyServer` key,
- In situations where the server is a combination of the above, as will be the case if the GeyserMC mod is in use, include multiple of the above keys as needed.

For each key in the nested dictionary, include the following value:
- For a Java version 1.4 or later server or a Bedrock server, the value should be `{'port': PORT}`,
- For a Java version Beta 1.8 to 1.3, the value should be `{'port': PORT, 'Version': 'VERSION'}`.

### YAML Script

Once all files are in place, run the following YAML script in Docker:

```
services:
  SERVICE_NAME:
    build:
      context: /PATH/TO/
      dockerfile: Dockerfile
      args:
        - PYTHONVERSION=3.14
    container_name: SERVICE_NAME
    environment:
      - PYTHONUNBUFFERED=1
    volumes:
      - /PATH/TO:/app
```

Replace `/PATH/TO` with the absolute path of the Dockerfile's directory (not including the name of your Dockerfile), and `SERVICE_NAME` with a name of your choosing.

Important note: the directory paths are written differently, with only the context path ending with a slash.