# Music Cog
My implementation of a music cog from my bot which I don't use anymore. It is mostly based off the offical [discord.py's basic voice example](https://github.com/Rapptz/discord.py/blob/master/examples/basic_voice.py), with a few changes and more features.

The local filesystem component along with it's respective cog, has now been removed from my bot instance.

This code was written in discord.py, and was working as of v2.4 (27th June 2024)

## Intents
```py
# Only subscribe to intents this cog needs
intents = discord.Intents.none()
intents.members = True
intents.guild_messages = True
intents.guilds = True
intents.voice_states = True
```
This implementation doesn't have a guild only decorator in the commands because of the intents.

It is not subscribed to DM message events at all so it never receives them, meaning the command is never invoked in DM contexts.

## Requirements
The requirements are in the text file.
