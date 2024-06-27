from typing import Literal
from os.path import basename
from asyncio import get_event_loop
from logging import info as log_info

import discord
import yt_dlp as youtube_dl
from discord.ext import commands


# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''


YTDL_FORMAT_OPTIONS = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 
    'options': '-vn -filter:a "volume=0.25"'
}

ytdl = youtube_dl.YoutubeDL(YTDL_FORMAT_OPTIONS)


def membed(custom_description: Optional[str] = None) -> discord.Embed:
    """Quickly construct an embed with an optional description."""
    membedder = discord.Embed(colour=0x2B2D31, description=custom_description)
    return membedder


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5) -> None:
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None) -> "YTDLSource":
        loop = loop or get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url']
        return cls(discord.FFmpegPCMAudio(filename, **FFMPEG_OPTIONS), data=data)


class Music(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot

    async def do_join_checks(self, ctx: commands.Context):
        if (ctx.author.voice is None):
            await ctx.reply(embed=membed("Connect to a voice channel first."))
            return
        
        if ctx.voice_client is not None:
            if (ctx.author not in ctx.guild.me.voice.channel.members):
                await ctx.reply(
                    embed=membed(f"Connect to {ctx.guild.me.voice.channel.mention} first.")
                )
                return
            return ctx.voice_client
        
        voice = await ctx.author.voice.channel.connect()
        await ctx.guild.me.edit(deafen=True)
        return voice

    @commands.command(description='Plays a file from the local filesystem')
    async def play(
        self, 
        ctx: commands.Context, 
        song: Literal["Say You Won't Let Go"]
    ) -> None:
        
        voice = await self.do_join_checks(ctx)
        if not voice:
            return

        if voice.is_playing():
            voice.stop()

        pathn = f"C:\\Users\\Music\\{song}.mp3"
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(pathn))
        file_name = basename(pathn)
        
        voice.play(source, after=lambda e: log_info(f'Player error: {e}') if e else None)
        await ctx.send(embed=membed(f'Now playing: ` {file_name} `.'))

    @commands.command(description="Streams music via url/search term from YouTube")
    async def stream(self, ctx: commands.Context, query: str):
        voice = await self.do_join_checks(ctx)
        if not voice:
            return

        if voice.is_playing():
            voice.stop()

        player = await YTDLSource.from_url(query, loop=self.bot.loop)
        voice.play(player)
        await ctx.send(embed=membed(f'Now playing: [{player.title}]({player.url}).'))

    @commands.command(description='Pause the player')
    async def pause(self, ctx: commands.Context):
        voice = await self.do_join_checks(ctx)
        if not voice:
            return
        
        if not voice.is_playing():
            return await ctx.reply(embed=membed("The player is already paused."))
        
        voice.pause()
        return await ctx.reply(embed=membed("Paused the player."))

    @commands.command(description='Resume the player')
    async def resume(self, ctx: commands.Context):
        voice = await self.do_join_checks(ctx)
        if not voice:
            return
        
        if not voice.is_paused():
            return await ctx.reply(embed=membed("The player is not paused."))
        
        voice.resume()
        await ctx.reply(embed=membed("Resumed the player."))

    @commands.command(description="Changes the player's volume")
    async def volume(self, ctx: commands.Context, volume: int):
        if not (1 <= volume <= 250):
            await ctx.reply(embed=membed("Volume needs to be between 1 and 250."))
            pass

        voice = await self.do_join_checks(ctx)
        if not voice:
            return

        voice.source.volume = volume / 100
        await ctx.reply(embed=membed(f"Changed volume of the player to {volume}%."))

    @commands.command(description='Stop the player')
    async def stop(self, ctx: commands.Context):

        voice = await self.do_join_checks(ctx)
        if not voice:
            return
        
        if not voice.is_playing():
            return await ctx.reply(embed=membed("The player is not playing."))
        
        voice.stop()
        await ctx.reply(embed=membed("Stopped the player."))

    @commands.command(description='Disconnect the bot from voice')
    async def leave(self, ctx: commands.Context):
        if ctx.guild.me.voice is None:
            return await ctx.reply(embed=membed("I'm not in a voice channel."))
        
        if ctx.author not in ctx.guild.me.voice.channel.members:
            return await ctx.reply(
                embed=membed(f"Connect to {ctx.guild.me.voice.channel.mention} first.")
            )
        
        if ctx.guild.voice_client.is_playing():
            ctx.guild.voice_client.stop()

        await ctx.guild.voice_client.disconnect()
        await ctx.reply(embed=membed("Disconnected the player."))


async def setup(bot: commands.Bot):
    await bot.add_cog(Music(bot))
