# Music Cog
My implementation of a music cog from my bot which I don't use anymore. It is still on my bot, but the streaming component of it has been stripped off since it violates Discord's ToS. The only part that exists is on my instance is the local filesystem version. It is mostly based off the offical discord.py's basic voice example, with a few breaking changes.

## Intents
```py
intents = Intents(
    members=True,
    guild_messages=True,
    emojis_and_stickers=True,
    guilds=True,
    voice_states=True
)
```
This implementation doesn't have a guild_only decorator in the commands because of the intents. It is not subscribed to DM messages at all so it never receives them, meaning the command is never invoked.

## Requirements
The requirements are in the text file.

The stream code is run in another CPU thread and probably won't work in a few years so it is here to remember what it did.
