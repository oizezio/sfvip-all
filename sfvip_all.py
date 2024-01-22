# nuitka-project: --include-module=mitmproxy_windows
# nuitka-project: --enable-plugin=tk-inter

from src import set_logging_and_exclude

set_logging_and_exclude("ipytv.playlist", "ipytv.channel", "mitmproxy.proxy.server")

if __name__ == "__main__":
    from shared import is_py_installer

    if is_py_installer():
        import multiprocessing

        # if it's a subprocess execution will stop here
        multiprocessing.freeze_support()

    # pylint: disable=ungrouped-imports
    # reduce what's imported in the subprocesses
    import logging
    import sys
    from pathlib import Path

    from build_config import Build, Github
    from shared import LogProcess
    from src import at_very_last
    from src.sfvip import AppInfo, run_app

    # for debug purpose only
    if len(sys.argv) > 1 and sys.argv[1] == "fakev0":
        Build.version = "0"

    logger = logging.getLogger(__name__)
    with LogProcess(logger, "Main"):
        run_app(
            at_very_last.register,
            AppInfo.from_build(Build, Github, app_dir=Path(__file__).parent),
            keep_logs=6,
        )
