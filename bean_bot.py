# bot.py
import os

import discord
from dotenv import load_dotenv
from discord.ext import commands

from beano import Beano

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(command_prefix='!beano ')

bot.beano = Beano()

bot.emotions = {"idle": "bean_pet/beano_idle.gif",
                "happy": "bean_pet/beano_fed.gif",
                "sad": "bean_pet/beano_sad.gif",
                "evil":"bean_pet/beano_evil.gif",
                "coin": "bean_pet/beano_coin.gif",
                "future": "bean_pet/beanopod.gif",
                None:"bean_pet/beano_idle.gif"}

def get_sprite(sprite_name):
    return discord.File(bot.emotions[sprite_name])


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("```Beano does not understand, but he will do better next time.```",file=get_sprite("sad"))
    else:
        raise error


@bot.command(name='pspspsps', help="Here's Beano!")
async def bean_pet_summon(ctx):

    await(ctx.send("You summon Beano."))

    beano_stats = bot.beano.get_beano_stats()

    message = "```It's Beano! \nHunger : {}\nWater  : {}\nEnergy : {}\nLove   : {}\nAGE    : {}```".format(beano_stats['hunger'],beano_stats['thirst'],beano_stats['energy'],beano_stats['affection'],beano_stats['age'])
    await ctx.send(file=discord.File(bot.emotions['idle']))


    await ctx.send(message)

@bot.command(name='pat',help="Pat Beano.  He will give you a coin if he is happy!")
async def beano_pat(ctx):
    await ctx.send("You pat Beano.")

    user_id = ctx.author.id
    response = bot.beano.pat_beano(user_id)
    await ctx.send(file=get_sprite(response[0]))
    await ctx.send(response[1])

    if response[0] == "happy":
        bot.beano.give_user_coins(user_id,1)
        await ctx.send("```What's this?  Beano loves you so much, he has spit something onto the ground! \nIt's a Beano Coin!\nUSER {} now has {} coins! \nUse it in the Beano Store!```".format(user_id,bot.beano.get_user_coins(user_id)),file=get_sprite("coin"))
        

@bot.command(name="store",help="View the Beano Store.")
async def beano_store(ctx,arg=None):

    user = ctx.author
    user_coin_count = bot.beano.get_user_coins(user.id)
    print(f"Coin count {user_coin_count} {user.id} {user.name}")
    store_inventory_response = build_beano_store_embed(bot.beano.get_store_inventory(),user,user_coin_count)
    await ctx.send(embed=store_inventory_response)


def build_beano_store_embed(inventory,user,coin_count):

    embed = discord.Embed()
    embed.title = "Beano Store!"
    embed.description = f"Welcome to the Beano Store.  You currently have {coin_count} Beano Coins."
    embed.url = "https://www.youtube.com/watch?v=8avMLHvLwRQ"
    embed.color = discord.Colour.blurple()
    embed.set_footer(text="To purchase, use `!beano buy item_number`.")

    for item in inventory:
        effects = "\n".join([f"Decreases {stat} by {amount}" for stat,amount in item['effect'].items()])
        description = f"{item['description']}\n {effects} \n{item['cost']} BC \n\n"
        embed.add_field(name=f"{item['item_id']} {item['name']}",value=description,inline=False)

    return embed



@bot.command(name="whats_to_come",help="View a nightmare.")
async def beano_future(ctx):

    await ctx.send("```Beanopod.```",file=get_sprite("future"))

@bot.command(name="assist",help="Claim a quest before someone else gets to help Beano.")
async def assist_beano(ctx):

    channel_id = ctx.channel.id
    print(channel_id)

    await bot.get_channel(channel_id).send("Beano currently does not need help.")

@bot.command(name="buy",help="Purchase an item from the store.")
async def buy_from_store(ctx,arg):

    response = bot.beano.buy_item_from_store(item_id=arg, user_id=ctx.author.id)
    await ctx.send(response)

@bot.command(name='inventory',help="View your inventory. Beano loves gifts.")
async def view_player_inventory(ctx):

    author = ctx.author

    stats = bot.beano.get_player_stats(user_id=author.id)

    current_inventory = {}

    for item in stats['inventory']:
        if item['id'] not in current_inventory:
            current_inventory[item['id']] = item
            current_inventory[item['id']]['amount'] = 1
        else:
            current_inventory[item['id']]['amount'] += 1

    print(current_inventory)
    embed = discord.Embed()
    embed.title = "Inventory"
    embed.description = f"You currently have {stats['beano_coin_count']} Beano Coins."
    embed.color = discord.Colour.green()
    embed.set_footer(text="To use an item, !beano use item_id")


    for item in current_inventory.values():
        effects = "\n".join([f"Decreases {stat} by {amount}" for stat,amount in item['effect'].items()])
        description = f"{item['description']}\n {effects} \n item_id : {item['id']}"
        embed.add_field(name=f"{item['name']} x {item['amount']}",value=description,inline=False)

    await ctx.send(embed=embed)
    # return embed

@bot.command(name="use",help="Use an item.")
async def use_item(ctx,item_id):
    
    response = bot.beano.use_item(item_id = item_id,user_id=ctx.author.id)
    await ctx.send(response,file=get_sprite("sad"))


# @bot.command(name='walk')

# async def bean_pet_walk(ctx):

#     bot.happiness += 1
#     await ctx.send(file=bot.beano_happy)
#     await ctx.send("```Beano accepts your walkies. Beano happiness now at level {}.```".format(bot.happiness))

# @bot.command(name='feed')
# async def bean_pet_feed(ctx,*args):

#     bot.food += 1

#     if args:
#         object = args[0]
#     else:
#         object = "food"

#     await ctx.send(file=bot.beano_fed)
#     await ctx.send("```Beano eats the {}. Beano food now at level {}.```".format(object,bot.food))

bot.run(TOKEN)
