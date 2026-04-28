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

Put the following in the header of `constants.py`:

```
from mcstatus import JavaServer, BedrockServer, LegacyServer
import pytz

#Minecraft Server Types
SERVER_TYPES = {
    JavaServer: 'Java',
    LegacyServer: 'Java',
    BedrockServer: 'Bedrock'
    }
```

Then add the following constants:

- `TOKEN`, which is your bot's Discord api token as a string
- `SERVER_ID`, which is your Discord server's ID as an integer
- `CHANNEL_ID`, which is the ID of the Discord channel containing the Minecraft server status message  as an integer
- `USER_ID`, which is your Discord user ID as an integer
- `TIME_ZONE`, which is the time zone described using the pytz package, for example `pytz.timezone('Europe/London')`.
  - A complete list of time zones can be obtained by running `pytz.all_timezones`.
- `DAILY_TIER_RESET_TIME`, which is the time of day to reset tier roll mechanics in seconds.
- `LOW_TIER_BLOCK_BEFORE`, which is the earliest time of day at which low tiers can be rolled in seconds.
- `LOW_TIER_BLOCK_AFTER`, which is the latest time of day at which low tiers can be rolled in seconds.
- `SERVER_MSG_PERIOD`, which is the time between Minecraft server checks in seconds.
- `DOMAIN`, which is the domain or IP addresses of your Minecraft servers.
- `MINECRAFT_SERVERS`, which is several nested dictionaries containing names, ports, and types of Minecraft servers to be monitored.

#### `MINECRAFT_SERVERS` Dictionary Structure

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