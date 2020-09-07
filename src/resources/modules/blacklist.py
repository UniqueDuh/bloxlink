from ..structures import Bloxlink
from aiotrello.exceptions import TrelloNotFound, TrelloUnauthorized
from aiohttp.client_exceptions import ClientOSError, ServerDisconnectedError
import re


trello = Bloxlink.get_module("trello", attrs="trello")
cache_set, cache_get, cache_pop = Bloxlink.get_module("cache", attrs=["set", "get", "pop"])


@Bloxlink.module
class Blacklist(Bloxlink.Module):
    def __init__(self):
        self.option_regex = re.compile("(.+):(.+)")

        self.trello_board = None

    async def __setup__(self):
        await self.load_blacklist()

    async def parse_data(self, trello_list, directory):
        for card in await trello_list.get_cards():
            match = self.option_regex.search(card.name)

            if match:
                name = match.group(1)
                ID = match.group(2)
                desc = card.desc

                if directory == "discord_ids":
                    ID = int(ID)

                await cache_set(f"blacklist:{directory}", ID, desc)


    async def load_blacklist(self):
        try:
            self.trello_board = await trello.get_board("https://trello.com/b/jkvnyaJo/blacklist")
        except (TrelloNotFound, TrelloUnauthorized, ConnectionResetError, ClientOSError, ServerDisconnectedError):
            pass
        else:
            roblox_ids = await self.trello_board.get_list(lambda l: l.name == "Roblox Accounts")
            discord_ids = await self.trello_board.get_list(lambda l: l.name == "Discord Accounts")

            await self.parse_data(roblox_ids, "roblox_ids")
            await self.parse_data(discord_ids, "discord_ids")