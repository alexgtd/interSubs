import argparse
import logging
import sys
from typing import Optional

from PyQt5.QtWidgets import QApplication

import config
from data.subtitles_data_source import SubtitlesDataSourceWorker
from ui.popup_view import PopupView
from ui.subtitles_view import SubtitlesView

log = logging.getLogger(__name__)


def parse_command_line_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--ipc-file-path", required=True)
    parser.add_argument("-s", "--subs-file-path", required=True)
    return parser.parse_args()


class GUI:
    def __init__(self, config_) -> None:
        self._app = QApplication(sys.argv)

        self._init_config(config_)
        self._init_views()
        self._init_data_sources()

    def enter_event_loop(self) -> int:
        return self._app.exec_()

    def _init_config(self, config_) -> None:
        self._cfg = config_
        self._cfg.screen_width = self._app.primaryScreen().size().width()
        self._cfg.screen_height = self._app.primaryScreen().size().height()

    def _init_views(self) -> None:
        self.subs_view = SubtitlesView(self._cfg)
        self.popup_view = PopupView(self._cfg)
        self.subs_view.register_text_hover_event_handler(self.popup_view.pop)

    def _init_data_sources(self) -> None:
        self.subs_data_source = SubtitlesDataSourceWorker(parse_command_line_arguments().subs_file_path)
        self.subs_data_source.on_subtitles_change.connect(self.popup_view.hide)
        self.subs_data_source.on_subtitles_change.connect(self.subs_view.submit_subs)
        self.subs_data_source.on_error.connect(
            lambda e: log.error("Exception occurred while watching the subtitles file.", exc_info=e)
        )
        self.subs_data_source.start()


_ui: Optional[GUI] = None


def run() -> None:
    global _ui
    log.info("Start.")
    _ui = GUI(config)

    log.info("Enter event loop.")
    sys.exit(_ui.enter_event_loop())
