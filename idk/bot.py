import discord as disc
import DiscordUtils
from discord import Member
import random
from discord import Embed
from discord.ext import commands
import sqlite3
import matplotlib.pyplot as plt
import numpy as np

from idk.db import *

intents = disc.Intents(messages=True, guilds=True, reactions=True, members=True, presences=True)
client = commands.Bot(command_prefix='.', intents=intents)
guild = disc.Guild
connection = sqlite3.connect('/Users/joshuali/Desktop/sqlite/discordbot.db')
c = connection.cursor()


@client.event
async def on_ready():
    create_guild(c, connection)
    if not check_word_table_exists(c):
        create_word_table(c)
    if not check_user_table_exists(connection, c):
        create_user(connection, c)

    for guild in client.guilds:
        insert_guild(connection, c, guild.id, guild.name)
        members = await guild.fetch_members().flatten()
        for member in members:
            if str(member) == 'WordCountBot#6084':
                continue
            insert_user(connection, c, username_to_id(member), guild.id)
    print('Bot ready')


@client.event
async def on_guild_join(guild):
    insert_guild(connection, c, guild.id, guild.name)


@client.event
async def on_member_join(member):
    store = str(member)
    first = store[0:store.find('#')]
    second = store[store.find('#') + 1: len(store)]
    id = disc.utils.get(client.get_all_members(), name=first, discriminator=second).id
    print(id)
    insert_user(connection, c, id, member.guild.id)


@client.event
async def on_member_remove(member):
    print(f'{member} has left the server')


@client.event
async def on_message(message):
    print(message.content)
    if message.author == client or len(message.content) == 0:
        return
    elif message.content is not None and message.content[0] != '.':
        print(message.content)
        words_store = message.content.split(' ')
        for word in words_store:
            if len(word) > 10:
                continue
            insert_word(connection, c, username_to_id(message.author), word)

    await client.process_commands(message)


@client.command(aliases=['rng', 'random', 'number-generator'])
async def random_number_generator(ctx, number):
    await ctx.send(f'{random.randint(0, int(number))}')


@client.command(aliases=['ws'])
async def word_search(ctx, message):
    if message is None:
        await ctx.send("Please provide a word to search for!")
        return
    users_tuple = get_users_by_word(c, ctx.message.guild.id, message)
    list_store = list(users_tuple)
    for i in range(0, len(users_tuple)):
        tuple_store = list(list_store[i])
        tuple_store[0] = str(client.get_user(tuple_store[0]))[0: str(client.get_user(tuple_store[0])).find('#')]
        list_store[i] = tuple_store
    if len(list_store) == 0:
        embed = disc.Embed(title="No one has used this word yet!", description="\u200b", colour=disc.Colour.red())
        await ctx.send(embed=embed)
    else:
        await display_words_embed(ctx, "https://icon-library.com/images/high-score-icon/high-score-icon-24.jpg",
                                  tuple(list_store),
                                  f'Leaderboard for the word {message}',
                                  "Ranking for users who have said this word", disc.Colour.purple())


@client.command(aliases=['w', 'word'])
async def words(ctx, message=None):
    searched_id = 0
    if message != "graph":
        if message is not None:
            searched_id = ret_mention_to_id(message)
            words_tuple = get_all_user_words(connection, c, searched_id)
        else:
            searched_id = ctx.message.author.id
            words_tuple = get_all_user_words(connection, c, ctx.message.author.id)
    else:
        searched_id = ctx.message.author.id
        words_tuple = get_all_user_words(connection, c, searched_id, 8)
    un = str(client.get_user(searched_id))[0: str(client.get_user(searched_id)).find('#')]
    pfp = client.get_user(searched_id).avatar_url
    if len(words_tuple) == 0:
        embed = disc.Embed(title="This user has not used any words yet!", description="\u200b",
                           colour=disc.Colour.red())
        await ctx.send(embed=embed)
    elif message == "graph":
        display_graph_embed(ctx, words_tuple, f"{un}'s words")
    else:
        await display_words_embed(ctx, pfp, words_tuple, f'{un}s words', "All words said by this user",
                                  disc.Colour.blue())


@client.command(aliases=['comp', 'c'])
async def compare(ctx, arg1, arg2):
    compid = ret_mention_to_id(arg1)
    sendid = ctx.message.author.id
    guildid = ctx.message.guild.id
    if user_exists_in_guild(c, sendid, guildid) and user_exists_in_guild(c, compid, guildid):
        send_count = get_single_word_count(c, sendid, arg2)
        comp_count = get_single_word_count(c, compid, arg2)
        embed = disc.Embed(title=f"Comparing these two user's word counts for {arg2}", description="\u200b",
                           colour=disc.Colour.green())
        embed.add_field(name=str(client.get_user(sendid)), value=send_count, inline=True)
        embed.add_field(name=str(client.get_user(compid)), value=comp_count, inline=True)
        await ctx.send(embed=embed)


def username_to_id(un):
    username = str(un)
    first = username[0:username.find('#')]
    second = username[username.find('#') + 1: len(username)]
    return disc.utils.get(client.get_all_members(), name=first, discriminator=second).id


def ret_mention_to_id(message):
    return int(str(message)[3: len(str(message)) - 1])


async def display_words_embed(ctx, pfp, tuple, title, description, colour):
    embeds = []
    if len(tuple) % 8 == 0:
        div = int((len(tuple) / 8))
        print('yet')
    else:
        div = int((len(tuple) / 8) + 1)
    last_store = (0, 1)
    for i in range(0, div):
        lim = 8
        if i == div - 1 and div % 8 != 0:
            lim = int(len(tuple)) - (i * 8)
        embed_store = disc.Embed(title=title, description=description,
                                 colour=colour)
        embed_store.set_thumbnail(url=pfp)
        embed_store.set_footer(text=f"Displaying page {i + 1} of {div}")
        for x in range(0, lim):
            tuple_store = tuple[(i * 8) + x]
            if tuple_store[1] == last_store[0]:
                number = last_store[1]
            else:
                number = (i * 8) + x + 1
                last_store = (tuple_store[1], number)
            embed_store.add_field(name=f"{number}.", value='\u200b', inline=True)
            embed_store.add_field(name=tuple_store[0], value='\u200b', inline=True)
            embed_store.add_field(name=tuple_store[1], value='\u200b', inline=True)
            if x == lim - 1:
                embeds.append(embed_store)
    paginator = DiscordUtils.Pagination.CustomEmbedPaginator(ctx)
    paginator.add_reaction('⏮️', "first")
    paginator.add_reaction('⏪', "back")
    paginator.add_reaction('🔐', "lock")
    paginator.add_reaction('⏩', "next")
    paginator.add_reaction('⏭️', "last")
    await paginator.run(embeds)


def display_graph_embed(ctx, tuple, title):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    words = []
    counts = []
    for tuple_store in tuple:
        words.append(tuple_store[0])
        counts.append(tuple_store[1])
    ypos = np.arange(len(tuple))
    plt.xticks(ypos, words)
    plt.title(title)
    ax.bar(ypos, counts)
    ax.patch.set_facecolor('black')
    plt.savefig('/Users/joshuali/Documents/test_graphs/test1')
    plt.show()


client.run('ODY3NTI3MzI5ODM5MzE3MDE0.YPiZyQ.1fuHCHkuu-YcQnBFZt7Kb7rq23M')
