from pathlib import Path
from typing import Optional

from PyQt5.QtCore import QObject, QSettings, QStandardPaths

from .. import __app_name__, __author__
from ..device_presets import PRESET_DEFAULT
from ..screenshots import ImageFormat

from dataclasses import dataclass, asdict


@dataclass
class _SettingsData:
    screenshot_folder: Path = (
        Path(QStandardPaths.writableLocation(QStandardPaths.PicturesLocation)) / "MSFS"
    )
    image_format: ImageFormat = ImageFormat.JPEG
    screenshot_hotkey: str = "Ctrl+Shift+S"
    file_name_format: str = "MSFS_{datetime}_{geocode}"
    date_format: str = "%Y-%m-%d-%H%M%S"
    minimize_to_tray: bool = False
    start_to_tray: bool = False
    play_sound: bool = True
    show_notification: bool = True
    # Metadata settings
    author_name: str = ""
    copyright_text: str = ""
    keywords: str = ""
    rating: int = 0
    custom_comment: str = ""
    # Device preset
    device_preset: str = PRESET_DEFAULT
    device_make: str = ""
    device_model: str = ""
    device_software: str = ""
    device_lens_make: str = ""
    device_lens_model: str = ""
    device_focal_length: str = ""  # stored as string for easy QSettings handling
    device_f_number: str = ""  # stored as string for easy QSettings handling


class AppSettings(QObject):
    _defaults = _SettingsData()

    def __init__(self, parent: Optional[QObject]):
        super().__init__(parent)

        self._settings = QSettings(
            QSettings.Format.IniFormat,
            QSettings.Scope.UserScope,
            __author__,
            application=__app_name__,
            parent=self,
        )

    # ---- General methods -----

    @property
    def defaults(self):
        return self._defaults

    def restore_defaults(self):
        for attribute, value in asdict(self._defaults).items():
            setattr(self, attribute, value)

    # ---- Settings getters/setters -----

    @property
    def screenshot_folder(self) -> Path:
        key = "screenshot_folder"
        if not self._settings.contains(key):
            return self._defaults.screenshot_folder
        return Path(self._settings.value(key, type=str))

    @screenshot_folder.setter
    def screenshot_folder(self, value: Path):
        self._settings.setValue("screenshot_folder", str(value))

    @property
    def image_format(self) -> ImageFormat:
        key = "image_format"
        if not self._settings.contains(key):
            return self._defaults.image_format
        return ImageFormat[self._settings.value(key, type=str)]

    @image_format.setter
    def image_format(self, value: ImageFormat):
        self._settings.setValue("image_format", value.name)

    @property
    def screenshot_hotkey(self) -> str:
        key = "screenshot_hotkey"
        if not self._settings.contains(key):
            return self._defaults.screenshot_hotkey
        return self._settings.value(key, type=str)

    @screenshot_hotkey.setter
    def screenshot_hotkey(self, value: str):
        self._settings.setValue("screenshot_hotkey", value)

    @property
    def file_name_format(self) -> str:
        key = "file_name_format"
        if not self._settings.contains(key):
            return self._defaults.file_name_format
        return self._settings.value(key, type=str)

    @file_name_format.setter
    def file_name_format(self, value: str):
        self._settings.setValue("file_name_format", value)

    @property
    def date_format(self) -> str:
        key = "date_format"
        if not self._settings.contains(key):
            return self._defaults.date_format
        return self._settings.value(key, type=str)

    @date_format.setter
    def date_format(self, value: str):
        self._settings.setValue("date_format", value)

    @property
    def minimize_to_tray(self) -> bool:
        key = "minimize_to_tray"
        if not self._settings.contains(key):
            return self._defaults.minimize_to_tray
        return self._settings.value(key, type=bool)

    @minimize_to_tray.setter
    def minimize_to_tray(self, value: bool):
        self._settings.setValue("minimize_to_tray", value)
    
    @property
    def start_to_tray(self) -> bool:
        key = "start_to_tray"
        if not self._settings.contains(key):
            return self._defaults.start_to_tray
        return self._settings.value(key, type=bool)

    @start_to_tray.setter
    def start_to_tray(self, value: bool):
        self._settings.setValue("start_to_tray", value)
    
    @property
    def play_sound(self) -> bool:
        key = "play_sound"
        if not self._settings.contains(key):
            return self._defaults.play_sound
        return self._settings.value(key, type=bool)

    @play_sound.setter
    def play_sound(self, value: bool):
        self._settings.setValue("play_sound", value)

    @property
    def show_notification(self) -> bool:
        key = "show_notification"
        if not self._settings.contains(key):
            return self._defaults.show_notification
        return self._settings.value(key, type=bool)

    @show_notification.setter
    def show_notification(self, value: bool):
        self._settings.setValue("show_notification", value)

    @property
    def times_launched(self) -> int:
        key = "internal/times_launched"
        if not self._settings.contains(key):
            return 0
        return self._settings.value(key, type=int)

    @times_launched.setter
    def times_launched(self, value: int):
        self._settings.setValue("internal/times_launched", value)

    # ---- Metadata settings -----

    @property
    def author_name(self) -> str:
        key = "metadata/author_name"
        if not self._settings.contains(key):
            return self._defaults.author_name
        return self._settings.value(key, type=str)

    @author_name.setter
    def author_name(self, value: str):
        self._settings.setValue("metadata/author_name", value)

    @property
    def copyright_text(self) -> str:
        key = "metadata/copyright_text"
        if not self._settings.contains(key):
            return self._defaults.copyright_text
        return self._settings.value(key, type=str)

    @copyright_text.setter
    def copyright_text(self, value: str):
        self._settings.setValue("metadata/copyright_text", value)

    @property
    def keywords(self) -> str:
        key = "metadata/keywords"
        if not self._settings.contains(key):
            return self._defaults.keywords
        return self._settings.value(key, type=str)

    @keywords.setter
    def keywords(self, value: str):
        self._settings.setValue("metadata/keywords", value)

    @property
    def rating(self) -> int:
        key = "metadata/rating"
        if not self._settings.contains(key):
            return self._defaults.rating
        return self._settings.value(key, type=int)

    @rating.setter
    def rating(self, value: int):
        self._settings.setValue("metadata/rating", value)

    @property
    def custom_comment(self) -> str:
        key = "metadata/custom_comment"
        if not self._settings.contains(key):
            return self._defaults.custom_comment
        return self._settings.value(key, type=str)

    @custom_comment.setter
    def custom_comment(self, value: str):
        self._settings.setValue("metadata/custom_comment", value)

    # ---- Device preset settings -----

    @property
    def device_preset(self) -> str:
        key = "device/preset"
        if not self._settings.contains(key):
            return self._defaults.device_preset
        return self._settings.value(key, type=str)

    @device_preset.setter
    def device_preset(self, value: str):
        self._settings.setValue("device/preset", value)

    @property
    def device_make(self) -> str:
        key = "device/make"
        if not self._settings.contains(key):
            return self._defaults.device_make
        return self._settings.value(key, type=str)

    @device_make.setter
    def device_make(self, value: str):
        self._settings.setValue("device/make", value)

    @property
    def device_model(self) -> str:
        key = "device/model"
        if not self._settings.contains(key):
            return self._defaults.device_model
        return self._settings.value(key, type=str)

    @device_model.setter
    def device_model(self, value: str):
        self._settings.setValue("device/model", value)

    @property
    def device_software(self) -> str:
        key = "device/software"
        if not self._settings.contains(key):
            return self._defaults.device_software
        return self._settings.value(key, type=str)

    @device_software.setter
    def device_software(self, value: str):
        self._settings.setValue("device/software", value)

    @property
    def device_lens_make(self) -> str:
        key = "device/lens_make"
        if not self._settings.contains(key):
            return self._defaults.device_lens_make
        return self._settings.value(key, type=str)

    @device_lens_make.setter
    def device_lens_make(self, value: str):
        self._settings.setValue("device/lens_make", value)

    @property
    def device_lens_model(self) -> str:
        key = "device/lens_model"
        if not self._settings.contains(key):
            return self._defaults.device_lens_model
        return self._settings.value(key, type=str)

    @device_lens_model.setter
    def device_lens_model(self, value: str):
        self._settings.setValue("device/lens_model", value)

    @property
    def device_focal_length(self) -> str:
        key = "device/focal_length"
        if not self._settings.contains(key):
            return self._defaults.device_focal_length
        return self._settings.value(key, type=str)

    @device_focal_length.setter
    def device_focal_length(self, value: str):
        self._settings.setValue("device/focal_length", value)

    @property
    def device_f_number(self) -> str:
        key = "device/f_number"
        if not self._settings.contains(key):
            return self._defaults.device_f_number
        return self._settings.value(key, type=str)

    @device_f_number.setter
    def device_f_number(self, value: str):
        self._settings.setValue("device/f_number", value)
