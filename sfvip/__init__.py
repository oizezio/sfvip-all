import os
from pathlib import Path

import sfvip_all_config as Config

from .config import Loader
from .player import Player
from .proxy import Proxies
from .users import UsersDatabase, UsersProxies

# TODO test standalone
# TODO watchdog users !
# TODO m3u playlist
# TODO test async vs sync


def run(config: Config, app_name: str):
    config_json = Path(os.getenv("APPDATA")) / app_name / "Config.json"
    config_loader = Loader(config, config_json)
    config_loader.update()

    player = Player(config_loader, config.Player, app_name)
    users_database = UsersDatabase(config_loader, config.Player)
    users_proxies = UsersProxies(users_database)
    with Proxies(config.AllCat, users_proxies.users_to_set) as proxies:
        with users_proxies.set(proxies.by_upstreams) as restore_proxies:
            with player.run():
                restore_proxies()
