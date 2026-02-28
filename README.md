# Inglewood Discord Bot

A python discord designed to run in a docker container.

## Functions

- Tracks the status of Minecraft Servers and updated a discord message upon changes.
- Allows discord users to assign themselve roles via slash commands.
- Allows discord users to assign other users roles via slash commands.
- Allows discord users to get a randomly rolled tier for world of tanks. Tiers can not repeat. Tier I is limted to once per day. The base odds of tier I, II, and III are halved. Tier I, II, and III are only availble at certain times of day. Tier I, II, and III can be disabled entirely using the battle pass version of the command. When tiers II, IV, V, VI, VII, and VIII are drawn preferential status may be rolled with 1 in 30 chance. When preferential status is drawn at tier IV, 

## Quick Start

In order to start the bot, download the `Dockerfile`and all `.py` files. Then put them in a directory of your choosing. Next create a `constants.py` file and add all the relavent details. This should take the following form:

```
import pytz

TOKEN = {your discord api token}
SERVER_ID = {your discord server's ID}
CHANNEL_ID = {the ID of the discord channel containing the minecraft server status message}
MESSAGE_ID = {the ID of the minecraft server status message}
USER_ID = {your discord user ID}
DOMAIN = {the domain of your minecraft servers}
SUR_PORT = {the java port of your minecraft survival server}
SUR_BED = {the bedrock port of your minecraft survival server}
RED_PORT = {the java port of your minecraft creative server}
RED_BED = {the bedrock port of your minecraft creative server}
ADV_PORT = {the java port of your minecraft adventure server}
FAIL_OVER_VER = {the version of your minecraft adventure server}
SERVER_MSG_PERIOD = {time between minecraft server checks in seconds}
DAILY_TIER_RESET_TIME = {time of day to reset tier roll mechanics in seconds}
LOW_TIER_BLOCK_BEFORE = {earliest time of day where low tiers can be rolled in seconds}
LOW_TIER_BLOCK_AFTER = {latest time of day where low tiers can be rolled in seconds}
TIME_ZONE = pytz.timezone('{your timezone}')
```

Then run the following yaml script in Docker, including all the relavent details:

```
services:
  {service name}:
    build:
      context: {directory written as '/path/to/'}
      dockerfile: Dockerfile
    container_name: {service name}
    environment:
      - PYTHONUNBUFFERED=1
    restart: unless-stopped
    volumes:
      - {directory written as '/path/to'}:/app
```

Important note: the directory paths are written differently, with only the context path ending with a slash.