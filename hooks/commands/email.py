from discord import Client, Message

SHORT_HELP_TEXT = '$$$email - Avisa-te sobre os problemas de usar o email'

def help(**kwargs):
    return SHORT_HELP_TEXT

# TODO: implement cooldown
async def run(client: Client, message: Message, **kwargs):
    await client.send_message(message.channel, \
                              content='Usem o suporte de problemas, idiotas!')
