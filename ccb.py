import asyncio
from discord.ext import commands
import discord
import random
import os
import time
import config
import mysql.connector
import db
#You will be notified when product drops below $_____

#TOKEN = os.environ.get("TOKEN")
TOKEN = config.TOKEN
bot = commands.Bot(command_prefix=commands.when_mentioned_or('-'))


mydb = mysql.connector.connect(
    host="34.86.36.213",
    user="root",
    password="Heroku3031*SPN",
    database="discord"
)

amzn_basep_url = 'https://www.amazon.com/dp/'

def removeFrom(num, user_id):
    path = 'PID_' + str(num)
    mycursor = mydb.cursor()
    sql = "UPDATE members SET %s = %s where USER_ID = '%s'" % (path, 'null', user_id)
    mycursor.execute(sql)
    mydb.commit()
    mycursor.close()
    print(mycursor.rowcount, "item was removed from Member Table.")

def verify_watch(PID, author):
    mycursor = mydb.cursor()
    sql = "SELECT PID_1, PID_2, PID_3, PID_4, PID_5 from members where USER_ID = '%s'" % (author)
    # msql = "SELECT * FROM members"
    # qsql = "INSERT IGNORE INTO members (Username, PID_1, PID_2, PID_3, PID_4, PID_5) VALUES (%s, %s, %s, %s, %s, %s)"
    # Insert Ignore allows me to insert products and skip over the duplicates and the error it gives.
    mycursor.execute(sql)
    PIDs = mycursor.fetchall()
    if PIDs == []:
        sql = "INSERT IGNORE INTO members (USER_ID, PID_1) VALUES ('%s', '%s')" % (author, PID)
        mycursor.execute(sql)
        mydb.commit()
        mycursor.close()
        return -2
    else:
        mycursor.close()
        if PID in PIDs[0]:
            return -1  # One for PID already in your personal monitor
        elif not PIDs[0][0] or not PIDs[0][1] or not PIDs[0][2] or not PIDs[0][3] or not PIDs[0][4]:
            for x in range(0,5):
                if not PIDs[0][x]:
                    return x
        else:
            return -3  # Full or Error

def verify_stop(PID, author):
    mycursor = mydb.cursor()
    sql = "SELECT PID_1, PID_2, PID_3, PID_4, PID_5 from members where USER_ID = '%s'" % (author)
    mycursor.execute(sql)
    PIDs = mycursor.fetchall()
    mycursor.close()
    if PIDs == []:
        return -1 #There are no products in your personal monitor.
    else:
        if PID in PIDs[0]:
            index = PIDs[0].index(PID)
            index += 1
            return index
        else:
            return -3  # Full or Error


def link_format_verifier(url):
    if 'amazon.com' not in url:
        return None
    try:
        x = url.split('/dp/')[1]
        try:
            if x == '':
                return None
            elif '/' in x:
                x = x.split('/')[0]
                return x
            elif len(x) < 15:
                return x
            elif '?ref' in x:
                x = x.split('?ref')[0]
                return x
        except IndexError:
            return None
    except IndexError:
        return None

def removeall(author):
    mycursor = mydb.cursor()
    checksql = "SELECT EXISTS(SELECT * from members WHERE USER_ID = '%s')" % (author)
    mycursor.execute(checksql)
    flagged = mycursor.fetchall()
    mydb.commit()
    flagged = flagged[0][0]
    if flagged == 1:
        sql = "DELETE FROM members where USER_ID = '%s'" % (author)
        mycursor.execute(sql)
        mydb.commit()
        mycursor.close()
        print(mycursor.rowcount, "row deleted from Member Table.")
        return 0
    else:
        mycursor.close()
        return 1

def grab_balance(author):
    mycursor = mydb.cursor()
    sql = "SELECT PID_1, PID_2, PID_3, PID_4, PID_5 from members where USER_ID = '%s'" % (author)
    mycursor.execute(sql)
    PIDs = mycursor.fetchall()
    mycursor.close()
    if PIDs == []:
        return -1, -1
    else:
        data = []
        count = 0
        for PID in PIDs[0]:
            print(PID)
            if PID:
                count += 1
                data.append(amzn_basep_url+PID)
        print(data)
        return count, data


class Main(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channel_id = 805212937438101535

    def monitor(self):
        time.sleep(180)
        mycursor = mydb.cursor()
        sql = "select p.PID, i.Name, i.Price as I_Price, s.Price as S_Price, i.Img_URL, i.Price-s.Price as P_Value from sync_data s, item_data i, products p where p.PID = i.PID and p.PID = s.PID and i.Price-s.Price>=1 and i.Price>0 and s.Price>0"
        mycursor.execute(sql)
        data = mycursor.fetchall()
        mycursor.close()
        if data == []:
            pass
        else:
            for var in data:


    def get_users(self, PID):
        mycursor = mydb.cursor()
        sql = "select USER_ID from members where PID_1 = %s OR PID_2 = %s OR  PID_3 = %s OR PID_4 = %s OR PID_5 = %s)" %(PID, PID, PID, PID, PID)
        mycursor.execute(sql)
        data = mycursor.fetchall()
        mycursor.close()


    @commands.command(pass_context=True)
    async def balance(self, ctx):
        author = ctx.message.author.id
        a_tag = '<@{0}>'.format(author)
        channel_id = ctx.message.channel.id
        if channel_id == self.channel_id:
            num, data = grab_balance(author)
            msg = ' ~ (' + str(num) + '/5) Slots Used'
            if num != -1:
                for link in data:
                    msg = msg + '\n'+link
                await ctx.send(a_tag + msg)
            else:
                await ctx.send(a_tag + ' ~ You currently have no products in your personal monitor.')

    @commands.command(pass_context=True)
    async def stopall(self, ctx):
        author = ctx.message.author.id
        a_tag = '<@{0}>'.format(author)
        channel_id = ctx.message.channel.id
        if channel_id == self.channel_id:
            val = removeall(author)
            if val == 1:
                await ctx.send(a_tag + ' ~ There are no products currently in your personal monitor.')
            else:
                await ctx.send(a_tag + ' ~ All products *Successfully Removed* from your personal monitor.')

    @commands.command(pass_context=True)
    async def stop(self, ctx, arg):
        author = ctx.message.author.id
        a_tag = '<@{0}>'.format(author)
        channel_id = ctx.message.channel.id
        if channel_id == self.channel_id:
            PID = link_format_verifier(arg)
            if PID != None:
                flag = verify_stop(PID, author)
                if flag == -1:
                    await ctx.send(a_tag + ' ~ There are no products currently in your personal monitor.')
                elif flag == -3:
                    await ctx.send(a_tag + ' ~ This product is not in your personal monitor. Please use the *-balance* command to view your products.')
                else:
                    removeFrom(flag, author)
                    await ctx.send(a_tag + ' ~ Successfully Removed.')
            else:
                await ctx.send(a_tag + ' ~ Your link appears to be invalid. Please make sure your link is a product link. Also, double check your link is valid. Please contact a moderator for additional support.')

    @commands.command(pass_context=True)
    async def watch(self, ctx, arg):

        author = ctx.message.author.id
        a_tag = '<@{0}>'.format(author)
        channel_id = ctx.message.channel.id
        if channel_id == self.channel_id:
            PID = link_format_verifier(arg)
            if PID != None:
                flag = verify_watch(PID, author)
                if flag == -1:
                    await ctx.send(a_tag + ' ~ This product is already in your personal monitor.')
                elif flag == -3:
                    await ctx.send(a_tag + ' ~ Your personal monitor is full (5/5). Please remove one with the *-stop* command to add another.')
                else:
                    loading = await ctx.send('https://cdn.discordapp.com/attachments/805212937438101535/808186294144335872/loading.gif')
                    instance = db.AMZN(mydb)
                    value = instance.page_parser(PID, flag, author)
                    await loading.delete()
                    if value:
                        if value == -1:
                            await ctx.send(a_tag + ' ~ Sorry price cannot be found.')
                        else:
                            msg = ' ~ You will be notified when your product (*' + value[1] + '*) drops below the current price of $' + value[0] +'.'
                            await ctx.send(a_tag + msg)
                    else:
                        await ctx.send(a_tag + ' ~ Your link appears to be invalid. Please make sure your link is a product link and has a visible price. Please contact a moderator for additional support.')
            else:
                await ctx.send(a_tag + ' ~ Your link appears to be invalid. Please make sure your link is a product link. Also, double check your link is valid. Please contact a moderator for additional support.')

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
    bot.loop.create_task(monitor())


bot.add_cog(Main(bot))
bot.run(TOKEN)