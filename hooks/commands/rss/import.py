from discord import Client, Message

from policy import AccessControl

import feed_state

SHORT_HELP_TEXT = '$$$rss import <dados em JSON> - Importa lista de feeds substituindo os existentes'

def help(**kwargs):
    """
    Show help
    """
    return SHORT_HELP_TEXT

@AccessControl(roles=['Staff'], relax_in=[], relax_pm=True)
async def run(client: Client, message: Message, **kwargs):
    """
    Run command
    """
    await feed_state.loads(str.join(' ', kwargs['args']))

    await message.channel.send(content='Feeds importados com sucesso.')
