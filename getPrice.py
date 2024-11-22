import requests
import json
from game import *
from game_info import *

# Set up your API key and base URL


class GetPrice:
    def __init__(self, id):
        self.id = id
        self.deals = []
        self.best_deal = None
        self.getData()
        self.getBestDeal()

    def getBestDeal(self):
        if len(self.deals) != 0:
            self.best_deal = self.deals[0]
            for deal in self.deals:
                if deal.price.amount > self.best_deal.price.amount:
                    self.best_deal = deal
        else:
            print("check")
            self.best_deal = Deal(
                "Free", "Free", "Free", None, None, None, None, None, None, None
            )

    def getData(self):
        payload = [self.id]
        api_key = "07b0e806aacf15f38b230a850b424b2542dd71af"
        base_url = "https://api.isthereanydeal.com/games/prices/v3"
        params = {
            "key": api_key,
            "shops": "19,2,4,13,15,52,16,67,6,17,20,68,24,25,27,28,26,29,35,26,27,42,65,47,48,49,66,50,70,61,62,64",
        }
        headers = {"Content-Type": "application/json"}
        response = requests.post(base_url, headers=headers, json=payload, params=params)
        payload = []

        # Check the response
        if response.status_code == 200:
            data = response.json()
            print(data)
            for game in data:
                # print(json.dumps(game, indent=4))
                for item in game["deals"]:

                    try:
                        shop_info = item["shop"]
                        shop = Shop(shop_info["id"], shop_info["name"])

                        price_info = item["price"]
                        price = Price(
                            price_info["amount"],
                            price_info["amountInt"],
                            price_info["currency"],
                        )

                        regular_price_info = item["regular"]
                        regular = Price(
                            regular_price_info["amount"],
                            regular_price_info["amountInt"],
                            regular_price_info["currency"],
                        )

                        deal_info = item
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
                            history_low=Price(None, None, None),
                            platforms=deal_info["platforms"],
                            timestamp=deal_info["timestamp"],
                            expiry=deal_info["expiry"],
                            url=deal_info["url"],
                        )
                        if deal.price.amount != 0:
                            self.deals.append(deal)
                    except:
                        print("Error")
                        continue
            # Pretty print the JSON response
        else:
            print(f"Error: {response.status_code} - {response.text}")


# game_price = GetPrice("018d937f-57ce-723f-b7e7-7c7b5df93471")
# game_info = GameView(game_price.id)
# game = Game(game_price.id, None, game_info.info.title, game_price.best_deal)
# print(game.deal.price)
