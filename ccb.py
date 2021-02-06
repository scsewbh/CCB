import asyncio
from discord.ext import commands
import discord
import random
import os
import config
#You will be notified when profuct drops below $_____

#TOKEN = os.environ.get("TOKEN")
TOKEN = config.TOKEN
bot = commands.Bot(command_prefix=commands.when_mentioned_or('!'))


class Main(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def watch(self, ctx, arg):
        author = ctx.message.author.id
        channel_id = ctx.message.channel.id
        if channel_id == 805212937438101535:
            print(author)
            a = '<@{0}>'.format(author)
            msg = ' Price Drop Alert for ...'
            await author.send(a + msg)
        else:
            print("That's you")

    @commands.command(pass_context=True)
    async def sanjay(self, ctx):
        author = ctx.message.author.id
        a = '<@{0}>'.format(author)
        msg = ', did you know Sanjay is god?'
        await ctx.send(a + msg)


    @commands.command(pass_context=True)
    async def test(self, ctx):
        user_id = ctx.author.id
        channel = bot.get_channel(805212937438101535)
        await channel.send("SOLVED!! THE RIDDLE HAS BEEN SOLVED BY <@{0}>".format(user_id))

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

    @commands.command()
    async def mcnerds2020(self, ctx):
        user = bot.get_user(ctx.author.id)
        print("Step 5 Completed:" + str(user))
        id = ctx.author.id
        await ctx.send("Congratulations you won it is time to let everyone know!")
        y = 1
        dot = ' . '
        msg = await ctx.send('Loading')

        con = 'Loading'
        x = 1
        while x <= 4:
            await asyncio.sleep(1.0)
            await msg.edit(content=con)
            con += dot
            x += 1
        await msg.edit(content="Done!")

        channel = bot.get_channel(805212937438101535)
        await channel.send("SOLVED!! THE RIDDLE HAS BEEN SOLVED BY <@{0}>".format(id))


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


bot.add_cog(Main(bot))
bot.run(TOKEN)