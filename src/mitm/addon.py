# use separate named package to reduce what's imported by multiprocessing
import json
import logging
import multiprocessing
from dataclasses import dataclass
from enum import Enum
from typing import Any, NamedTuple, Optional

from mitmproxy import http
from mitmproxy.coretypes.multidict import MultiDictView

from .epg import EPG, UpdateStatusT

logger = logging.getLogger(__name__)


class AllCategoryName(NamedTuple):
    live: Optional[str]
    vod: str
    series: str


@dataclass
class Panel:
    get_categories: str
    get_category: str
    all_category_name: str
    all_category_id: str = "0"


class PanelType(Enum):
    LIVE = "live"
    VOD = "vod"
    SERIES = "series"


def get_panel(panel_type: PanelType, all_category_name: str, streams: bool = True) -> Panel:
    return Panel(
        get_categories=f"get_{panel_type.value}_categories",
        get_category=f"get_{panel_type.value}{'_streams' if streams else ''}",
        all_category_name=all_category_name,
    )


def _is_api_request(request: http.Request) -> bool:
    return "player_api.php?" in request.path


def _query(request: http.Request) -> MultiDictView[str, str]:
    return getattr(request, "urlencoded_form" if request.method == "POST" else "query")


def _del_query_key(request: http.Request, key: str) -> None:
    del _query(request)[key]


def _get_query_key(request: http.Request, key: str) -> Optional[str]:
    return _query(request).get(key)


def _response_json(response: http.Response) -> Optional[Any]:
    if response and response.text and response.headers.get("content-type") == "application/json":
        try:
            return json.loads(response.text)
        except json.JSONDecodeError:
            return None
    return None


def _unused_category_id(categories: list[dict]) -> str:
    if ids := [
        int(cat_id)
        for category in categories
        if (cat_id := category.get("category_id")) is not None and isinstance(cat_id, (int, str))
    ]:
        return str(max(ids) + 1)
    return "0"


def _log(verb: str, panel: Panel, action: str) -> None:
    txt = "%s category '%s' (id=%s) for '%s' request"
    logger.info(txt, verb, panel.all_category_name, panel.all_category_id, action)


def fix_info_serie(info: Any) -> Optional[dict[str, Any]]:
    if isinstance(info, dict):
        if episodes := info.get("episodes"):
            # fix episode list : Xtream code api recommend a dictionary
            if isinstance(episodes, list):
                info["episodes"] = {str(season[0]["season"]): season for season in episodes}
                logger.info("fix serie info")
                return info
    return None


class SfVipAddOn:
    """mitmproxy addon to inject the all category"""

    def __init__(self, all_name: AllCategoryName, update_status: UpdateStatusT) -> None:
        panels = [
            get_panel(PanelType.VOD, all_name.vod),
            get_panel(PanelType.SERIES, all_name.series, streams=False),
        ]
        if all_name.live:
            panels.append(get_panel(PanelType.LIVE, all_name.live))
        self._category_panel = {panel.get_category: panel for panel in panels}
        self._categories_panel = {panel.get_categories: panel for panel in panels}
        self._running = multiprocessing.Event()
        self.epg = EPG(update_status)

    def epg_update(self, url: str):
        self.epg.ask_update(url)

    def done(self):
        self.epg.stop()

    def running(self) -> None:
        self._running.set()
        self.epg.start()

    def wait_running(self, timeout: Optional[float] = None) -> bool:
        return self._running.wait(timeout)

    def request(self, flow: http.HTTPFlow) -> None:
        if _is_api_request(flow.request):
            action = _get_query_key(flow.request, "action")
            if action in self._category_panel:
                panel = self._category_panel[action]
                category_id = _get_query_key(flow.request, "category_id")
                if category_id == panel.all_category_id:
                    # turn an all category query into a whole catalog query
                    _del_query_key(flow.request, "category_id")
                    _log("serve", panel, action)

    def inject_all(self, categories: Any, action: str) -> Optional[list[Any]]:
        if isinstance(categories, list):
            # response with the all category injected @ the beginning
            panel = self._categories_panel[action]
            panel.all_category_id = _unused_category_id(categories)
            all_category = dict(
                category_id=panel.all_category_id,
                category_name=panel.all_category_name,
                parent_id=0,
            )
            categories.insert(0, all_category)
            _log("inject", panel, action)
            return categories
        return None

    def response(self, flow: http.HTTPFlow) -> None:
        # pylint: disable=too-many-nested-blocks
        if flow.response and not flow.response.stream:
            if _is_api_request(flow.request):
                action = _get_query_key(flow.request, "action")
                if action in self._categories_panel:
                    categories = _response_json(flow.response)
                    if all_injected := self.inject_all(categories, action):
                        flow.response.text = json.dumps(all_injected)
                elif action == "get_series_info":
                    info = _response_json(flow.response)
                    if fixed_info := fix_info_serie(info):
                        flow.response.text = json.dumps(fixed_info)
                elif action == "get_live_streams":
                    category_id = _get_query_key(flow.request, "category_id")
                    if not category_id:
                        server = flow.request.host_header
                        self.epg.set_server_channels(server, _response_json(flow.response))
                elif action == "get_short_epg":
                    if stream_id := _get_query_key(flow.request, "stream_id"):
                        server = flow.request.host_header
                        limit = _get_query_key(flow.request, "limit")
                        if epg_listings := tuple(self.epg.get(server, stream_id, limit)):
                            flow.response.text = json.dumps({"epg_listings": epg_listings})

    @staticmethod
    def responseheaders(flow: http.HTTPFlow) -> None:
        """all reponses are streamed except the api requests"""
        if not _is_api_request(flow.request):
            if flow.response:
                flow.response.stream = True
