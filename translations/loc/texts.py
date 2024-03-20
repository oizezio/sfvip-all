import dataclasses
from typing import ClassVar

# TODO force IPTV no translate


# pylint: disable=too-many-instance-attributes, invalid-name
@dataclasses.dataclass
class Texts:
    language: ClassVar[str] = "english"

    User: str = "User"
    UserProxy: str = "User Proxy"
    NoProxy: str = "Proxy missing"
    Proxy: str = "%s Proxy"
    ShowProxies: str = "Show proxies"
    HideProxies: str = "Hide proxies"
    RestartFixProxy: str = "Restart to fix the proxies"
    ShouldUseVersion: str = "You should use the %s version"
    SearchWholeCatalog: str = "Search your whole catalog"
    Download: str = "Download"
    Install: str = "Install"
    Extract: str = "Extract"
    Update: str = "Update"
    Restart: str = "Restart"
    Cancel: str = "Cancel"
    Search: str = "Search"
    Retry: str = "Retry"
    CheckUpdate: str = "Check updates"
    UnknownVersion: str = "Unknown version"
    PleaseWait: str = "Please wait"
    CheckLastestLibmpv: str = "Check latest libmpv update"
    RestartInstall: str = "Do you want to restart to install %s ?"
    SearchOrDownload: str = "Do you want to search or download it ?"
    NoSocketPort: str = "No socket port available !"
    CantStartProxies: str = "Can't start local proxies !"
    NotFound: str = "%s not found"
    AllSeries: str = "All Series"
    AllMovies: str = "All Movies"
    AllChannels: str = "All Channels"
    FastCached: str = "fast in cache"
    AlreadyRunning: str = "%s is running. Please close it to continue."
    PlayerTooOld: str = "%s is too old. Version %s or above is needed."
    UpgradeFailed: str = "%s upgrade failed. Do you want to retry ?"
    LoadCache: str = "Loading cache"
    SaveCache: str = "Saving cache"
    Downloading: str = "Downloading"
    Processing: str = "Processing"
    Ready: str = "Ready"
    Failed: str = "Failed"
    NoEpg: str = "No EPG"
    EpgUrl: str = "External EPG"
    InvalidUrl: str = "Invalid url"
    EpgConfidence: str = "EPG confidence level"
    EPGFoundConfidence: str = "%s found in the external EPG with %s confidence"
    ChangeLog: str = "Change log for %s"
    UpdatedToday: str = "Updated today"
    Updated1DayAgo: str = "Updated 1 day ago"
    UpdatedDaysAgo: str = "Updated %s days ago"
    Confidence0: str = "0 %: You don't trust the EPG and you'll only get an exact match and often none"
    Confidence100: str = (
        "100 %: You completely trust the EPG and you'll always get a match even one of poor quality"
    )
    EPGPrefer: str = "Search the IPTV provider first"
    Yes: str = "Yes"
    No: str = "No"
    EPGPreferYes: str = "Yes: Search the IPTV provider EPG first. Use the external EPG only when it fails."
    EPGPreferNo: str = "No: Search the external EPG first. Use the IPTV provider EPG only when it fails."
    EPGUrlTip: str = "Enter the URL of the external EPG, it should end up with '%s' or '%s'"
    LibmpvTip: str = (
        "Libmpv decodes & renders audio and video. "
        "Enable the updates to get the last version optimized for your computer."
    )
    ProxyTip: str = (
        "%s uses a local proxy to intercept all requests to the IPTV provider "
        "and inject the 'all' categories and the external EPG"
    )
    UserProxyTip: str = "Actual user proxy if it exists"
    Missing: str = "%s missing"
    Complete: str = "Complete"

    def as_dict(self) -> dict[str, str]:
        return dataclasses.asdict(self)
