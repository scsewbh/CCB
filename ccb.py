import asyncio
from discord.ext import commands
import discord
import random
import os
import config


#TOKEN = os.environ.get("TOKEN")
TOKEN = config.TOKEN
bot = commands.Bot(command_prefix=commands.when_mentioned_or('!'))


class Main(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def sanjay(self, ctx):
        author = ctx.message.author.id
        a = '<@{0}>'.format(author)
        msg = ', did you know Sanjay is god?'
        await ctx.send(a + msg)


    @commands.command(pass_context=True)
    async def validuser(self, ctx):
        mikeid = 298282227047989262
        print(ctx.author.id)
        if ctx.author.id == mikeid:
            await ctx.send("Mike is here!")
        else:
            await ctx.send("You are An Impostor")

    @commands.command(pass_context=True)
    async def spam(self, ctx):
        striy = ctx.message.content
        strigy = striy[6:]
        lol = random.randint(4, 8)
        for x in range(0, lol):
            await ctx.send(strigy)

    @commands.command(pass_context=True)
    async def loading(self, ctx):
        y = 1
        dot = ' . '
        msg = await ctx.send('Loading')
        while y <= 2:
            con = 'Loading'
            x = 1
            while x <= 10:
                await asyncio.sleep(0.5)
                await msg.edit(content=con)
                con += dot
                x += 1
            y += 1

    @commands.command(pass_context=True)
    async def time(self, ctx):
        timestr = ctx.message.content
        time = int(timestr[6:])
        count = time
        msg = await ctx.send(str(time))
        while count >= 0:
            count -= 1
            await asyncio.sleep(1)
            await msg.edit(content=str(count))

    @commands.command(pass_context=True)
    async def embed(self, ctx):
        embed = discord.Embed()
        embed.set_author(name='School')  # title of course
        embed.title = 'KSFSKDJSKFH'  # name of link to course page
        embed.url = 'https://www.google.com/'  # actual link to course
        embed.description = 'description'  # description
        embed.set_thumbnail(
            url='https://interactive-examples.mdn.mozilla.net/media/cc0-images/grapefruit-slice-332-332.jpg')  # image top right small
        embed.colour = 0x046a38  # left line color

        embed.add_field(name='Syllabus', value='[test](https://www.google.com/)')

        embed.set_footer(text='Challenge Released')
        await ctx.send(embed=embed)


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


bot.add_cog(Main(bot))
bot.run(TOKEN)