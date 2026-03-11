# Inglewood Discord Bot

A python discord designed to run in a docker container.

## Functions

- Tracks the status of Minecraft Servers and updated a discord message upon changes.
- Allows discord users to assign themselve roles via slash commands.
- Allows discord users to assign other users roles via slash commands.
- Allows discord users to get a randomly rolled tier for world of tanks. Tiers can not repeat. Tier I is limted to once per day. The base odds of tier I, II, and III are halved. Tier I, II, and III are only availble at certain times of day. Tier I, II, and III can be disabled entirely using the battle pass version of the command. When tiers II, IV, V, VI, VII, and VIII are drawn preferential status may be rolled with 1 in 30 chance. When preferential status is drawn at tier IV, 

## Quick Start

In order to start the bot, download the `Dockerfile`and `inglewood.py` files. Then put them in a directory of your choosing. Next create a `constants.py` file.

### constants.py

Put the following imports in the header of the file:

```
import pytz
from mcstatus import JavaServer, BedrockServer, LegacyServer
```

Then add the following constants:

- `TOKEN` which is your bot's discord api token as a string
- `SERVER_ID` which is your discord server's ID as an integer
- `CHANNEL_ID` which is the ID of the discord channel containing the minecraft server status message  as an integer
- `USER_ID` which is your discord user ID as an integer
- `TIME_ZONE` which is time zone described using the pytz package, for example `pytz.timezone('Europe/London')`. A complete list of time zones is can be obtained by running `pytz.all_timezones`.
- `DAILY_TIER_RESET_TIME` which is the time of day to reset tier roll mechanics in seconds.
- `LOW_TIER_BLOCK_BEFORE` which is the earliest time of day where low tiers - can be rolled in seconds.
- `LOW_TIER_BLOCK_AFTER` which is the latest time of day where low tiers can be rolled in seconds.
- `SERVER_MSG_PERIOD` which is time between minecraft server checks in seconds.
- `DOMAIN` which is the domain or IP adresses of your minecraft servers.
- `MINECRAFT_SERVERS` which is several nested dictionaries containing names, ports and types of minecraft servers to be monitored.

#### `MINECRAFT_SERVERS` Dictionary Structure

Each Minecraft server that you want to monitor include an entry in this dictionary where the key is the `SERVER_NAME` and the value is a nested dictionary.

Inside that nested dictionary should have the following keys:
- For a Java version 1.7 or later server, the nested dictionary should have a `JavaServer` key,
- For a Bedrock server, the nested dictionary should have a `BedrockServer` key,
- For a Java version Beta 1.8 to 1.6, the nested dictionary should have a `LegacyServer` key,
- In situations where the server is a combination of the above, for example if the GeyserMC mod is in use, include multiple keys.

For each key in the nested dictionary, include the following value:
- For a Java version 1.4 or later server or a Bedrock server, the value should be `{'port': PORT}`,
- For a Java version Beta 1.8 to 1.3, the value should be `{'port': PORT, 'Version': 'VERSION'}`.

### YAML Script

Once all files are in place run the following yaml script in Docker:

```
services:
  SERVICE_NAME:
    build:
      context: /PATH/TO/
      dockerfile: Dockerfile
    container_name: SERVICE_NAME
    environment:
      - PYTHONUNBUFFERED=1
    restart: unless-stopped
    volumes:
      - /PATH/TO:/app
```

Replacing `/PATH/TO` with the absolute path of the Dockerfile's directory (not including the name of your Dockerfile), and `SERVICE_NAME` with a name of your choosing.

Important note: the directory paths are written differently, with only the context path ending with a slash.