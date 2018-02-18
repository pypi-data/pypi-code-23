import logging
import random
import aiohttp
import discord
from discord.ext.commands import Bot


# TODO add "Roll" for dice roll
# TODO Weather?
# TODO Define?
# TODO urbandefine?
# TODO fortune cookie
# TODO !remind me
# TODO On ready announce to server or to channel - I'm here to help! Just type ?help in the #help-desk channel.
# TODO Joke command
# TODO color commands? like pbot
# TODO crypto commands like pbot?
# TODO news or feed command


BOT_PREFIX = ("?", "!")


class HelpDeskBot:

    def __init__(self, channel_name, token, debug_file_name):
        logging.basicConfig(
            filename=debug_file_name,
            level=logging.INFO,
            format='%(asctime)s %(module)s %(msg)s',
        )
        logging.info("[*] Initializing bot...")
        self.token = token
        self.designated_channel_name = channel_name
        self.client = Bot(command_prefix=BOT_PREFIX)
        self.setup()

    def run(self):
        logging.info("[*] Running...")
        self.client.run(self.token)

    def setup(self):

        @self.client.event
        async def on_ready():
            logging.info("[+] Connected as " + self.client.user.name)
            logging.info("[+] Listening for private messages and in channel #" + self.designated_channel_name)
            await self.client.change_presence(game=discord.Game(name='Help Desk'))

        @self.client.event
        async def on_message(message):
            # Ignore messages by bots (including self)
            if message.author.bot:
                return
            # Only respond to the channel designated and private messages.
            if not message.channel.is_private and message.channel.name != self.designated_channel_name:
                return
            # Pass on to rest of the client commands
            if message.content.startswith(BOT_PREFIX):
                await self.client.process_commands(message)

        @self.client.command(description="Checks the current Bitcoin price in US Dollars from Coinbase.",
                             brief="Get current Bitcoin price",
                             aliases=['btc'])
        async def bitcoin():
            url = 'https://api.coindesk.com/v1/bpi/currentprice/BTC.json'
            raw_response = await aiohttp.ClientSession().get(url)
            response = await raw_response.json()
            await self.client.say("Bitcoin price is: $" + response['bpi']['USD']['rate'])

        @self.client.command(name='8ball',
                             description="Answers a yes/no question.",
                             brief="Answers from the beyond.",
                             aliases=['eight_ball', 'eightball', '8-ball'],
                             pass_context=True)
        async def eight_ball(context):
            possible_responses = [
                'That is a resounding no',
                'It is not looking likely',
                'Too hard to tell',
                'It is quite possible',
                'Definitely',
            ]
            await self.client.say(random.choice(possible_responses) + ", " + context.message.author.mention)
