import json
import sqlite3
import requests
import time
from game_info import *

api_key = "07b0e806aacf15f38b230a850b424b2542dd71af"


class GetDaiLyGames:
    def __init__(self, country, limit: int, shop: tuple):
        base_url = "https://api.isthereanydeal.com/deals/v2"

        self.game_list = []
        params = {
            "key": api_key,
            "country": country,
            "offset": 0,
            "limit": str(limit),
            "sort": "-trending",
            "nondeals": False,
            "mature": False,
            "shops": ",".join(map(str, shop)),
            "filter": "N4IgLgngDgpgcgezCAXAbQMwF0C+Q===",
        }

        # Send the GET request with a retry mechanism
        retries = 3
        for i in range(retries):
            try:
                response = requests.get(base_url, params=params)
                response.raise_for_status()  # Check for HTTP errors
                data = response.json()
                self.game_list = GetDaiLyGames.parse_api_response(data).game_list
                break  
            except requests.exceptions.ReadTimeout:
                print("Request timed out, retrying...")
                time.sleep(2)  
            except requests.exceptions.RequestException as e:
                print(f"Error: {e}")
                break

    # Function to create instances from the API response
    def parse_api_response(data):
        game_list = []
        for item in data["list"]:
            shop_info = item["deal"]["shop"]
            shop = Shop(shop_info["id"], shop_info["name"])

            price_info = item["deal"]["price"]
            price = Price(
                price_info["amount"], price_info["amountInt"], price_info["currency"]
            )

            regular_price_info = item["deal"]["regular"]
            regular = Price(
                regular_price_info["amount"],
                regular_price_info["amountInt"],
                regular_price_info["currency"],
            )

            deal_info = item["deal"]
            deal = Deal(
                shop=shop,
                price=price,
                regular=regular,
                cut=deal_info["cut"],
                store_low=Price(
                    deal_info["storeLow"]["amount"],
                    deal_info["storeLow"]["amountInt"],
                    deal_info["storeLow"]["currency"],
                ),
                history_low=Price(
                    deal_info["historyLow"]["amount"],
                    deal_info["historyLow"]["amountInt"],
                    deal_info["historyLow"]["currency"],
                ),
                platforms=deal_info["platforms"],
                timestamp=deal_info["timestamp"],
                expiry=deal_info["expiry"],
                url=deal_info["url"],
            )

            game = Game(
                game_id=item["id"], slug=item["slug"], title=item["title"], deal=deal
            )

            game_list.append(game)

        return GameDealsResponse(data["nextOffset"], data["hasMore"], game_list)


class Price:
    def __init__(self, amount, amount_int, currency):
        self.amount = amount
        self.amount_int = amount_int
        self.currency = currency


class Shop:
    def __init__(self, shop_id, name):
        self.id = shop_id
        self.name = name


class Deal:
    def __init__(
        self,
        shop,
        price,
        regular,
        cut,
        store_low,
        history_low,
        platforms,
        timestamp,
        expiry,
        url,
    ):
        self.shop = shop
        self.price = price
        self.regular = regular
        self.cut = cut
        self.store_low = store_low
        self.history_low = history_low
        self.platforms = platforms
        self.timestamp = timestamp
        self.expiry = expiry
        self.url = url


class Game:
    def __init__(self, game_id, slug, title, deal):
        self.id = game_id
        self.steam_id = self.get_steam_id()
        self.slug = slug
        self.title = title
        self.deal = deal
        self.details = GameView(self.id)
        self.logo = None
        self.logo = self.get_image()

    def get_image(self) -> str:
        conn = sqlite3.connect("SearchBar_game.db")
        cursor = conn.cursor()
        cursor.execute("SELECT image_url FROM game_info WHERE id = ?", (self.id,))
        rows = cursor.fetchall()
        for row in rows:
            return row[0]
        return None

    def get_steam_id(self) -> str:
        conn = sqlite3.connect("SearchBar_game.db")
        cursor = conn.cursor()
        cursor.execute("SELECT steam_id FROM game_info WHERE id = ?", (self.id,))
        rows = cursor.fetchall()
        for row in rows:
            return row[0]
        return None


class GameDealsResponse:
    def __init__(self, next_offset, has_more, game_list):
        self.next_offset = next_offset
        self.has_more = has_more
        self.game_list = game_list


"""

# Test
daily = GetDaiLyGames("VN", 1, (61, 35))
for game in daily.game_list:
    # test1.ui
    print(
        f"Game Title: {game.title},Current Price: {game.deal.price.amount} {game.deal.price.currency},Current regular:{game.deal.regular.amount}, logo: {game.logo}"
    )

    # test2.ui

    # Game review
    list_review = game.details.info.reviews
    for review in list_review:
        print(f"Source: {review.source}, Score: {review.score}, Count: {review.count}")

    # Game stat
    stat = game.details.info.stats
    print(f"Rank: {stat.rank}, Score: {stat.waitlisted}, Count: {stat.collected}")

    # Players:
    players_count = game.details.info.players
    print(
        f"Recents: {players_count.recent}, Day: {players_count.day}, Week: {players_count.week}, Peak :{players_count.peak}"
    )

    # releaseDate:
    releaseDate = game.details.info.releaseDate
    print(f"releaseDate: {releaseDate}")

    # game tags:
    tags = game.details.info.tags
    print("All tags are:")
    for tag in tags:
        print(tag)
"""
