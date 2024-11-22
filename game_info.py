import requests


class DictAccessMixin:
    """Mixin to allow dictionary-like and attribute access to nested data."""

    def __getitem__(self, key):
        return getattr(self, key)

    def __getattr__(self, key):
        try:
            return self.__dict__[key]
        except KeyError:
            raise AttributeError(
                f"'{self.__class__.__name__}' object has no attribute '{key}'"
            )


class GameInfo(DictAccessMixin):
    def __init__(self, data):
        if data != None:
            self.id = data.get("id", "")
            self.slug = data.get("slug", "")
            self.title = data.get("title", "")
            self.type = data.get("type", "")
            self.mature = data.get("mature", False)
            self.assets = Assets(data.get("assets", {}))
            self.earlyAccess = data.get("earlyAccess", False)
            self.achievements = data.get("achievements", False)
            self.tradingCards = data.get("tradingCards", False)
            self.appid = data.get("appid", None)
            self.tags = data.get("tags", [])
            self.releaseDate = data.get("releaseDate", None)
            self.developers = [Developer(d) for d in data.get("developers", [])]
            self.publishers = [Publisher(p) for p in data.get("publishers", [])]
            self.reviews = [Review(r) for r in data.get("reviews", [])]
            self.stats = Stats(data.get("stats", {}))
            self.players = Players(data.get("players", {}))
            self.urls = Urls(data.get("urls", {}))


class Assets(DictAccessMixin):
    def __init__(self, data):
        if data != None:
            self.boxart = data.get("boxart", None)
            self.banner145 = data.get("banner145", None)
            self.banner300 = data.get("banner300", None)
            self.banner400 = data.get("banner400", None)
            self.banner600 = data.get("banner600", None)


class Developer(DictAccessMixin):
    def __init__(self, data):
        if data != None:
            self.id = data.get("id", "")
            self.name = data.get("name", "")


class Publisher(DictAccessMixin):
    def __init__(self, data):
        if data != None:
            self.id = data.get("id", "")
            self.name = data.get("name", "")


class Review(DictAccessMixin):
    def __init__(self, data):
        if data != None:
            self.score = data.get("score", 0)
            self.source = data.get("source", "")
            self.count = data.get("count", 0)
            self.url = data.get("url", "")


class Stats(DictAccessMixin):
    def __init__(self, data):
        if data != None:
            self.rank = data.get("rank", None)
            self.waitlisted = data.get("waitlisted", 0)
            self.collected = data.get("collected", 0)


class Players(DictAccessMixin):
    def __init__(self, data):
        if data != None:
            self.recent = data.get("recent", 0)
            self.day = data.get("day", 0)
            self.week = data.get("week", 0)
            self.peak = data.get("peak", 0)


class Urls(DictAccessMixin):
    def __init__(self, data):
        if data != None:
            self.game = data.get("game", "")


# Fetch and parse the data
def get_data(id):
    api_key = "07b0e806aacf15f38b230a850b424b2542dd71af"
    base_url = "https://api.isthereanydeal.com/games/info/v2"

    # Parameters for the request
    params = {
        "key": api_key,
        "id": id,
    }

    response = requests.get(base_url, params=params,timeout=10)

    # Check the response
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return {}


class GameView:
    def __init__(self, id):
        data = get_data(id)
        self.info = GameInfo(data)  # Assuming data is nested under "data"
