import discord
import logging
import random

from hooks import run_hooks
import rss_autorefresh

PIN_MIN_REACTIONS = 1

# Current category to create channels
CHANNELS_CATEGORY = discord.CategoryChannel

# @everyone role
EVERYONE_ROLE = 0

# Basic permissions for new roles/channels
ROLE_PERMISSIONS = 0
ROLE_CHANNEL_PERMISSIONS = discord.PermissionOverwrite(view_channel=True)
EVERYONE_PERMISSIONS = discord.PermissionOverwrite(view_channel=False)

# Messages to get roles
special_messages = []
ROLE_REACTION = '✋'
ROLES_CHANNEL_ID = 750825003402133524

client = discord.Client()

logging.basicConfig(level=logging.INFO)

@client.event
async def on_ready() -> None:
    """
    Action to take when bot starts
    """
    from feed_state import init

    logging.info('We have logged in as {0.user}'.format(client))

    big_brother = discord.Streaming(name='BigBrother@LEIC 👀', \
                                    url='https://bit.ly/BigBrotherLEIC', \
                                    game='BigBrother@LEIC 👀')
    await client.change_presence(activity=big_brother)

    # Default category to create channels (most recently created)
    # Important to avoid trash channels
    global CHANNELS_CATEGORY
    CHANNELS_CATEGORY = sorted(client.guilds[0].categories, \
                               key=(lambda x: x.created_at), \
                               reverse=True)[0]

    # Get @everyone role
    global EVERYONE
    EVERYONE = client.guilds[0].default_role
    global ROLE_PERMISSIONS
    ROLE_PERMISSIONS = EVERYONE.permissions

    # RSS initialization
    # Needs async to create roles/channels
    await client.loop.create_task(init())

    # RSS auto-refresh
    client.loop.create_task(rss_autorefresh.run(client))

@client.event
async def on_message(message: discord.Message) -> None:
    """
    Action to take when a message is published
    """

    # Avoid answering itself
    if message.author == client.user:
        return

    await run_hooks(client, message)

@client.event
async def on_reaction_add(reaction: discord.Reaction, user: discord.User) -> None:
    """
    Action to take when a reaction is added to a message
    """
    if reaction.emoji == '📌' and reaction.count >= PIN_MIN_REACTIONS and not reaction.message.pinned:
        await reaction.message.pin()

async def check_role_channel(feed: str) -> None:
    """
    Check if pair Role/Channel already exists and create it if not
    """
    global CHANNELS_CATEGORY
    guild = client.guilds[0]
    roles = dict(zip(list(map(lambda x: x.name, guild.roles)), guild.roles))
    channels = list(map(lambda x: x.name, CHANNELS_CATEGORY.text_channels))

    role = 0
    # Check role
    if feed not in roles:
        try:
            role = await guild.create_role(name=feed, \
                                           color=discord.Colour(random.randint(0, 0xffffff)), \
                                           mentionable=True, \
                                           permissions=ROLE_PERMISSIONS)

            # Send message to receive roles
            await notify_new_role(role)
        except Exception as err:
            logging.error('Couldn\'t create role: %s' % err)
            pass
    else:
        role = roles[feed]

    # Check textchannel
    if feed.lower() not in channels:
        try:
            await CHANNELS_CATEGORY.create_text_channel(name=feed,
                                                        overwrites={
                                                            EVERYONE: EVERYONE_PERMISSIONS,
                                                            role: ROLE_CHANNEL_PERMISSIONS
                                                        })
        except Exception as err:
            logging.error('Couldn\'t create channel: %s' % err)
            pass

async def check_category(category: str) -> None:
    """
    Check if category exists and create it if not
    """
    global CHANNELS_CATEGORY

    category = category.lower()

    guild = client.guilds[0]
    categories = dict(zip(list(map(lambda x: x.name.lower(), guild.categories)), guild.categories))

    if category not in categories:
        CHANNELS_CATEGORY = await guild.create_category_channel(name=category)
    else:
        CHANNELS_CATEGORY = categories[category]

async def notify_new_role(role: discord.Role) -> None:
    """
    Send special message for users to react and receive the role
    """
    channel = client.get_channel(ROLES_CHANNEL_ID)
    message = await channel.send(embed=discord.Embed(title='**[' + role.name + ']** Nova cadeira disponível', \
                          type='rich', \
                          color=role.color, \
                          description='Se vais fazer a cadeira **' + role.name + '** reage com ' + \
                                           ROLE_REACTION + ' para teres acesso ao role ' + role.mention + ', ao canal e receberes notificações de anúncios'))

    message.add_reaction(ROLE_REACTION)
