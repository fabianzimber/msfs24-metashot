import winsound
from pathlib import Path
from typing import Optional

from PyQt5.QtCore import QEvent, QSize, Qt, QTimer, QUrl, pyqtSignal, pyqtSlot
from PyQt5.QtGui import (
    QCloseEvent,
    QCursor,
    QDesktopServices,
    QIcon,
    QKeySequence,
    QPixmap,
)
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPlainTextEdit,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from .. import RESOURCES_PATH, __app_name__, __author__, __store_url__, __version__
from ..device_presets import (
    DEVICE_PRESETS,
    PRESET_CUSTOM,
    PRESET_ORDER,
    get_preset_labels,
)
from ..metadata import Metadata
from ..names import FileNameComposer
from ..screenshots import ImageFormat
from .controller import ScreenShotResult
from .forms.main_window import Ui_MainWindow
from .hotkeys import HotkeyID
from .keyedit import CustomKeySequenceEdit
from .notification import NotificationColor, NotificationHandler
from .settings import AppSettings
from .thumbnails import ThumbnailWidget
from .util import open_url
from .validators import DateFormatValidator, FileNameFormatValidator


class MainWindow(QMainWindow):

    screenshot_requested = pyqtSignal()
    credits_requested = pyqtSignal()
    hotkey_changed = pyqtSignal(HotkeyID, str)
    closed = pyqtSignal()

    _maps_url = "https://www.google.com/maps/search/?api=1&query={latitude},{longitude}"
    _shutter_sound_path = str(RESOURCES_PATH / "shutter.wav")

    def __init__(
        self,
        file_name_composer: FileNameComposer,
        settings: AppSettings,
        app_icon: QIcon,
    ):
        super().__init__()

        self._file_name_composer = file_name_composer
        self._settings = settings

        self._last_screenshot: Optional[Path] = None
        self._last_metadata: Optional[Metadata] = None

        self._notification_handler = NotificationHandler(parent=self)

        self._form = Ui_MainWindow()
        self._form.setupUi(self)

        self._form.view_last_location.hide()

        self._select_hotkey = CustomKeySequenceEdit(parent=self)
        self._form.layout_select_hotkey.addWidget(self._select_hotkey)
        self._form.open_screenshots.setFocus()  # prevent focus steal by hotkey

        self._thumbnail_widget = ThumbnailWidget(self)
        self._form.thumbnail_layout.insertWidget(0, self._thumbnail_widget)
        self._thumbnail_widget.clicked.connect(self._on_open_last_screenshot)  # type: ignore
        self._thumbnail_widget.setPixmap(app_icon.pixmap(QSize(170, 96)))

        self._setup_metadata_tab()

        self._load_ui_state_from_settings()
        self._setup_input_validators()
        self._setup_format_field_description()
        self._setup_button_labels()

        self._setup_input_widget_connections()
        self._setup_button_connections()

        self._form.title.setText(
            f"<b>{__app_name__}</b> v{__version__} by {__author__}"
        )
        self.setWindowTitle(__app_name__)

    def _setup_metadata_tab(self):
        """Create and add the Metadata Settings tab programmatically."""
        metadata_tab = QWidget()
        metadata_layout = QVBoxLayout(metadata_tab)
        metadata_layout.setSpacing(12)

        # Description label
        intro_label = QLabel(
            "Configure metadata fields that will be automatically embedded "
            "into every screenshot you take. These values are written as "
            "EXIF/XMP tags and are visible in photo viewers and file explorers."
        )
        intro_label.setWordWrap(True)
        intro_label.setStyleSheet("color: #a6adc8; font-size: 9pt; padding: 4px 0;")
        metadata_layout.addWidget(intro_label)

        # --- Device Preset Group ---
        device_group = QGroupBox("📱 Device Preset")
        device_layout = QVBoxLayout(device_group)
        device_layout.setSpacing(8)

        # Preset selector row
        preset_row = QHBoxLayout()
        preset_label = QLabel("Device Template:")
        preset_label.setFixedWidth(120)
        preset_label.setToolTip(
            "Select a device preset to simulate photos taken from that device. "
            "GPS location data still comes from your live flight."
        )
        self._device_preset_combo = QComboBox()
        preset_labels = get_preset_labels()
        for key in PRESET_ORDER:
            self._device_preset_combo.addItem(preset_labels[key], key)
        self._device_preset_combo.setToolTip(
            "Choose a built-in device template or 'Custom' to enter your own values."
        )
        preset_row.addWidget(preset_label)
        preset_row.addWidget(self._device_preset_combo)
        preset_row.addStretch()
        device_layout.addLayout(preset_row)

        # Device detail fields
        self._device_make_edit = self._make_device_field(
            device_layout, "Make:", "e.g. Apple", "Device manufacturer (EXIF Make)"
        )
        self._device_model_edit = self._make_device_field(
            device_layout, "Model:", "e.g. iPhone 17 Pro", "Device model (EXIF Model)"
        )
        self._device_software_edit = self._make_device_field(
            device_layout, "Software:", "e.g. 18.0", "Software version (EXIF Software)"
        )
        self._device_lens_make_edit = self._make_device_field(
            device_layout, "Lens Make:", "e.g. Apple", "Lens manufacturer (EXIF LensMake)"
        )
        self._device_lens_model_edit = self._make_device_field(
            device_layout,
            "Lens Model:",
            "e.g. iPhone 17 Pro back triple camera 6.765mm f/1.78",
            "Lens model (EXIF LensModel)",
        )
        self._device_focal_length_edit = self._make_device_field(
            device_layout, "Focal Length:", "e.g. 6.765", "Focal length in mm (EXIF FocalLength)"
        )
        self._device_f_number_edit = self._make_device_field(
            device_layout, "F-Number:", "e.g. 1.78", "Aperture f-number (EXIF FNumber)"
        )

        preset_hint = QLabel(
            "💡 Select a template above to auto-fill these fields. "
            "Choose 'Custom' to enter your own values. "
            "GPS coordinates are always live from your flight."
        )
        preset_hint.setWordWrap(True)
        preset_hint.setStyleSheet("color: #6c7086; font-size: 8pt; padding-top: 2px;")
        device_layout.addWidget(preset_hint)

        metadata_layout.addWidget(device_group)

        # --- Author / Copyright Group ---
        author_group = QGroupBox("Author && Copyright")
        author_layout = QVBoxLayout(author_group)
        author_layout.setSpacing(8)

        # Author Name
        author_row = QHBoxLayout()
        author_label = QLabel("Author / Artist:")
        author_label.setFixedWidth(120)
        author_label.setToolTip("Sets the EXIF Artist and XMP Creator fields")
        self._meta_author = QLineEdit()
        self._meta_author.setPlaceholderText("e.g. Your Name")
        self._meta_author.setToolTip(
            "Your name or alias. Written to EXIF Artist and XMP Creator tags."
        )
        author_row.addWidget(author_label)
        author_row.addWidget(self._meta_author)
        author_layout.addLayout(author_row)

        # Copyright
        copyright_row = QHBoxLayout()
        copyright_label = QLabel("Copyright:")
        copyright_label.setFixedWidth(120)
        copyright_label.setToolTip("Sets the EXIF Copyright field")
        self._meta_copyright = QLineEdit()
        self._meta_copyright.setPlaceholderText("e.g. © 2024 Your Name. All rights reserved.")
        self._meta_copyright.setToolTip(
            "Copyright notice. Written to the EXIF Copyright tag."
        )
        copyright_row.addWidget(copyright_label)
        copyright_row.addWidget(self._meta_copyright)
        author_layout.addLayout(copyright_row)

        metadata_layout.addWidget(author_group)

        # --- Tags / Keywords Group ---
        tags_group = QGroupBox("Tags && Classification")
        tags_layout = QVBoxLayout(tags_group)
        tags_layout.setSpacing(8)

        # Keywords
        keywords_row = QHBoxLayout()
        keywords_label = QLabel("Keywords:")
        keywords_label.setFixedWidth(120)
        keywords_label.setToolTip("Sets XMP Subject tags (semicolon-separated)")
        self._meta_keywords = QLineEdit()
        self._meta_keywords.setPlaceholderText(
            "e.g. MSFS; Aviation; Screenshot; Airbus A320"
        )
        self._meta_keywords.setToolTip(
            "Semicolon-separated keywords/tags. Written as XMP Subject tags. "
            "Useful for searching and filtering screenshots."
        )
        keywords_row.addWidget(keywords_label)
        keywords_row.addWidget(self._meta_keywords)
        tags_layout.addLayout(keywords_row)

        # Rating
        rating_row = QHBoxLayout()
        rating_label = QLabel("Rating:")
        rating_label.setFixedWidth(120)
        rating_label.setToolTip("Sets the XMP Rating field (0-5 stars)")
        self._meta_rating = QSpinBox()
        self._meta_rating.setRange(0, 5)
        self._meta_rating.setSuffix(" ★")
        self._meta_rating.setToolTip(
            "Star rating from 0 (unrated) to 5. Written to the XMP Rating tag."
        )
        self._meta_rating.setFixedWidth(100)
        rating_hint = QLabel("0 = unrated, 1-5 = star rating")
        rating_hint.setStyleSheet("color: #6c7086; font-size: 8pt;")
        rating_row.addWidget(rating_label)
        rating_row.addWidget(self._meta_rating)
        rating_row.addWidget(rating_hint)
        rating_row.addStretch()
        tags_layout.addLayout(rating_row)

        metadata_layout.addWidget(tags_group)

        # --- Comment Group ---
        comment_group = QGroupBox("Comment")
        comment_layout = QVBoxLayout(comment_group)
        comment_layout.setSpacing(8)

        comment_label = QLabel("Custom Comment:")
        comment_label.setToolTip("Sets the EXIF UserComment field")
        comment_layout.addWidget(comment_label)

        self._meta_comment = QPlainTextEdit()
        self._meta_comment.setPlaceholderText(
            "Add a comment that will be embedded in every screenshot...\n"
            "e.g. Captured during a flight from KJFK to EGLL"
        )
        self._meta_comment.setToolTip(
            "Free-form comment text. Written to the EXIF UserComment tag."
        )
        self._meta_comment.setMaximumHeight(80)
        comment_layout.addWidget(self._meta_comment)

        metadata_layout.addWidget(comment_group)

        # Auto-save hint
        hint_label = QLabel(
            "💡 Changes are saved automatically when you modify a field."
        )
        hint_label.setStyleSheet("color: #6c7086; font-size: 8pt; padding-top: 4px;")
        metadata_layout.addWidget(hint_label)

        metadata_layout.addStretch()

        self._form.tabWidget.addTab(metadata_tab, "🏷️ Metadata Settings")

    @staticmethod
    def _make_device_field(
        parent_layout: QVBoxLayout,
        label_text: str,
        placeholder: str,
        tooltip: str,
    ) -> QLineEdit:
        """Helper to create a labeled device-field row."""
        row = QHBoxLayout()
        label = QLabel(label_text)
        label.setFixedWidth(120)
        label.setToolTip(tooltip)
        edit = QLineEdit()
        edit.setPlaceholderText(placeholder)
        edit.setToolTip(tooltip)
        row.addWidget(label)
        row.addWidget(edit)
        parent_layout.addLayout(row)
        return edit

    @pyqtSlot(QPixmap)
    def on_thumbnail_ready(self, thumbnail: QPixmap):
        cursor = QCursor()
        cursor.setShape(Qt.CursorShape.PointingHandCursor)
        self._thumbnail_widget.setCursor(cursor)
        self._thumbnail_widget.setPixmap(thumbnail)

    @pyqtSlot(ScreenShotResult)
    def on_screenshot_taken(self, result: ScreenShotResult):
        if self._settings.show_notification:
            self._notification_handler.notify(
                message=f"<b>Screenshot saved</b>: {result.path.name}",
                color=NotificationColor.success,
                onclick=self._on_open_last_screenshot,  # type: ignore
            )
        self._set_last_opened_screenshot(path=result.path, metadata=result.metadata)

    @pyqtSlot(str)
    def on_screenshot_error(self, message: str):
        self._notification_handler.notify(
            message=f"<b>Error</b>: {message}",
            color=NotificationColor.error,
        )

    @pyqtSlot()
    def on_sim_window_found(self):
        if self._settings.play_sound:
            winsound.PlaySound(
                self._shutter_sound_path, winsound.SND_FILENAME | winsound.SND_ASYNC
            )

    def _setup_format_field_description(self):
        supported_fields = self._file_name_composer.get_supported_fields()

        lines = []

        for field in supported_fields:
            text = f"<b>{{{field.name}}}</b>: {field.description}"
            if field.required:
                text += " Required."
            lines.append(text)

        text = "<br>".join(lines)

        self._form.available_fields.setText(text)

    def _setup_input_validators(self):
        self._file_name_format_validator = FileNameFormatValidator(
            line_edit=self._form.file_name_format,
            warning_label=self._form.file_name_format_warning,
            save_button=self._form.file_name_format_save,
            file_name_composer=self._file_name_composer,
            parent=self,
        )
        self._date_format_validator = DateFormatValidator(
            line_edit=self._form.date_format,
            warning_label=self._form.date_format_warning,
            save_button=self._form.date_format_save,
            file_name_composer=self._file_name_composer,
            parent=self,
        )
        self._form.file_name_format.setValidator(self._file_name_format_validator)
        self._form.date_format.setValidator(self._date_format_validator)

    def _setup_button_connections(self):
        self._form.take_screenshot.clicked.connect(self.screenshot_requested)
        self._form.quit_button.clicked.connect(
            self.quit, Qt.ConnectionType.QueuedConnection
        )  # queued connection recommended on slots that close QApplication
        self._form.select_folder.clicked.connect(self._on_select_folder)
        self._form.restore_defaults.clicked.connect(self._on_restore_defaults)
        self._form.restore_defaults_advanced.clicked.connect(
            self._on_restore_defaults_advanced
        )
        self._form.open_screenshots.clicked.connect(self._on_open_folder)
        # self._form.view_last_screenshot.clicked.connect(self._on_open_last_screenshot)
        self._form.view_last_location.clicked.connect(self._on_open_last_location)
        self._form.file_name_format_save.clicked.connect(self._on_file_name_format_save)
        self._form.date_format_save.clicked.connect(self._on_date_format_save)
        self._form.credits.clicked.connect(self.credits_requested)
        self._form.updates.clicked.connect(self._on_open_store)

    def _setup_button_labels(self):
        self._form.take_screenshot.setText(
            f"📷 Screenshot ({self._settings.screenshot_hotkey})"
        )

    def _setup_input_widget_connections(self):
        self._form.select_format.currentTextChanged.connect(
            self._on_format_selection_changed
        )
        self._select_hotkey.keySequenceChanged.connect(self._on_hotkey_changed)
        self._form.minimize_to_tray.stateChanged.connect(
            self._on_minimize_to_tray_changed
        )
        self._form.start_to_tray.stateChanged.connect(
            self._on_start_to_tray_changed
        )
        self._form.play_sound.stateChanged.connect(self._on_play_sound_changed)
        self._form.show_notification.stateChanged.connect(
            self._on_show_Notification_changed
        )
        # Metadata fields - auto-save on edit
        self._meta_author.textChanged.connect(self._on_meta_author_changed)
        self._meta_copyright.textChanged.connect(self._on_meta_copyright_changed)
        self._meta_keywords.textChanged.connect(self._on_meta_keywords_changed)
        self._meta_rating.valueChanged.connect(self._on_meta_rating_changed)
        self._meta_comment.textChanged.connect(self._on_meta_comment_changed)
        # Device preset fields
        self._device_preset_combo.currentIndexChanged.connect(
            self._on_device_preset_changed
        )
        self._device_make_edit.textChanged.connect(self._on_device_field_changed)
        self._device_model_edit.textChanged.connect(self._on_device_field_changed)
        self._device_software_edit.textChanged.connect(self._on_device_field_changed)
        self._device_lens_make_edit.textChanged.connect(self._on_device_field_changed)
        self._device_lens_model_edit.textChanged.connect(self._on_device_field_changed)
        self._device_focal_length_edit.textChanged.connect(self._on_device_field_changed)
        self._device_f_number_edit.textChanged.connect(self._on_device_field_changed)

    def _tear_down_input_widget_connections(self):
        self._form.select_format.currentTextChanged.disconnect(
            self._on_format_selection_changed
        )
        self._select_hotkey.keySequenceChanged.disconnect(self._on_hotkey_changed)
        self._form.minimize_to_tray.stateChanged.disconnect(
            self._on_minimize_to_tray_changed
        )
        self._form.start_to_tray.stateChanged.disconnect(
            self._on_start_to_tray_changed
        )
        self._form.play_sound.stateChanged.disconnect(self._on_play_sound_changed)
        self._form.show_notification.stateChanged.disconnect(
            self._on_show_Notification_changed
        )
        # Metadata fields
        self._meta_author.textChanged.disconnect(self._on_meta_author_changed)
        self._meta_copyright.textChanged.disconnect(self._on_meta_copyright_changed)
        self._meta_keywords.textChanged.disconnect(self._on_meta_keywords_changed)
        self._meta_rating.valueChanged.disconnect(self._on_meta_rating_changed)
        self._meta_comment.textChanged.disconnect(self._on_meta_comment_changed)
        # Device preset fields
        self._device_preset_combo.currentIndexChanged.disconnect(
            self._on_device_preset_changed
        )
        self._device_make_edit.textChanged.disconnect(self._on_device_field_changed)
        self._device_model_edit.textChanged.disconnect(self._on_device_field_changed)
        self._device_software_edit.textChanged.disconnect(self._on_device_field_changed)
        self._device_lens_make_edit.textChanged.disconnect(self._on_device_field_changed)
        self._device_lens_model_edit.textChanged.disconnect(self._on_device_field_changed)
        self._device_focal_length_edit.textChanged.disconnect(self._on_device_field_changed)
        self._device_f_number_edit.textChanged.disconnect(self._on_device_field_changed)

    def _load_ui_state_from_settings(self):
        self._form.current_folder.setText(str(self._settings.screenshot_folder))
        self._select_hotkey.setKeySequence(
            QKeySequence(self._settings.screenshot_hotkey)
        )
        self._form.select_format.clear()
        self._form.select_format.addItems(format.name for format in ImageFormat)
        self._form.select_format.setCurrentText(self._settings.image_format.name)
        self._form.file_name_format.setText(self._settings.file_name_format)
        self._form.date_format.setText(self._settings.date_format)
        self._form.minimize_to_tray.setChecked(self._settings.minimize_to_tray)
        self._form.start_to_tray.setChecked(self._settings.start_to_tray)
        self._form.play_sound.setChecked(self._settings.play_sound)
        self._form.show_notification.setChecked(self._settings.show_notification)
        # Metadata fields
        self._meta_author.setText(self._settings.author_name)
        self._meta_copyright.setText(self._settings.copyright_text)
        self._meta_keywords.setText(self._settings.keywords)
        self._meta_rating.setValue(self._settings.rating)
        self._meta_comment.setPlainText(self._settings.custom_comment)
        # Device preset
        preset_key = self._settings.device_preset
        index = self._device_preset_combo.findData(preset_key)
        if index >= 0:
            self._device_preset_combo.setCurrentIndex(index)
        self._load_device_fields_from_settings()
        self._update_device_fields_editable()

    @pyqtSlot()
    def _on_file_name_format_save(self):
        if not self._form.file_name_format.hasAcceptableInput():
            return  # should not happen
        self._settings.file_name_format = self._form.file_name_format.text()
        self._form.file_name_format.setPalette(QLineEdit().palette())
        self._form.file_name_format_save.setDisabled(True)

    @pyqtSlot()
    def _on_date_format_save(self):
        if not self._form.date_format.hasAcceptableInput():
            return  # should not happen
        self._settings.date_format = self._form.date_format.text()
        self._form.date_format.setPalette(QLineEdit().palette())
        self._form.date_format_save.setDisabled(True)

    @pyqtSlot()
    def _on_restore_defaults(self):
        self._settings.restore_defaults()
        # Avoid loops by temporarily disenganging connections
        self._tear_down_input_widget_connections()
        self._load_ui_state_from_settings()
        self._setup_input_widget_connections()
        self._setup_button_labels()
        # FIXME: should not have to do this manually
        self.hotkey_changed.emit(
            HotkeyID.take_screenshot, self._settings.defaults.screenshot_hotkey
        )

    @pyqtSlot()
    def _on_restore_defaults_advanced(self):
        self._form.file_name_format.setText(self._settings.defaults.file_name_format)
        self._form.date_format.setText(self._settings.defaults.date_format)
        self._form.file_name_format_save.click()
        self._form.date_format_save.click()

    @pyqtSlot()
    def _on_select_folder(self):
        screenshot_folder = QFileDialog.getExistingDirectory(
            self,
            "Choose where to save MSFS screenshots",
            str(self._settings.screenshot_folder),
        )
        if not screenshot_folder:
            return

        self._form.current_folder.setText(screenshot_folder)
        self._settings.screenshot_folder = Path(screenshot_folder)

    @pyqtSlot(str)
    def _on_format_selection_changed(self, new_name: str):
        format = ImageFormat[new_name]
        self._settings.image_format = format

    @pyqtSlot(QKeySequence)
    def _on_hotkey_changed(self, new_hotkey: QKeySequence):
        if not new_hotkey or not new_hotkey.toString():
            return

        key = new_hotkey.toString()
        self.hotkey_changed.emit(HotkeyID.take_screenshot, key)
        self._settings.screenshot_hotkey = key
        self._setup_button_labels()

    @pyqtSlot(int)
    def _on_minimize_to_tray_changed(self, state: int):
        self._settings.minimize_to_tray = state == Qt.CheckState.Checked

    @pyqtSlot(int)
    def _on_start_to_tray_changed(self, state: int):
        self._settings.start_to_tray = state == Qt.CheckState.Checked

    @pyqtSlot(int)
    def _on_play_sound_changed(self, state: int):
        self._settings.play_sound = state == Qt.CheckState.Checked

    @pyqtSlot(int)
    def _on_show_Notification_changed(self, state: int):
        self._settings.show_notification = state == Qt.CheckState.Checked

    # ---- Metadata field handlers ----

    @pyqtSlot(str)
    def _on_meta_author_changed(self, text: str):
        self._settings.author_name = text

    @pyqtSlot(str)
    def _on_meta_copyright_changed(self, text: str):
        self._settings.copyright_text = text

    @pyqtSlot(str)
    def _on_meta_keywords_changed(self, text: str):
        self._settings.keywords = text

    @pyqtSlot(int)
    def _on_meta_rating_changed(self, value: int):
        self._settings.rating = value

    @pyqtSlot()
    def _on_meta_comment_changed(self):
        self._settings.custom_comment = self._meta_comment.toPlainText()

    # ---- Device preset handlers ----

    def _load_device_fields_from_settings(self):
        """Populate device field widgets from persisted settings."""
        self._device_make_edit.setText(self._settings.device_make)
        self._device_model_edit.setText(self._settings.device_model)
        self._device_software_edit.setText(self._settings.device_software)
        self._device_lens_make_edit.setText(self._settings.device_lens_make)
        self._device_lens_model_edit.setText(self._settings.device_lens_model)
        self._device_focal_length_edit.setText(self._settings.device_focal_length)
        self._device_f_number_edit.setText(self._settings.device_f_number)

    def _update_device_fields_editable(self):
        """Enable/disable device fields based on whether the preset is 'Custom'."""
        is_custom = self._get_current_preset_key() == PRESET_CUSTOM
        for field in self._get_device_field_widgets():
            field.setReadOnly(not is_custom)

    def _get_current_preset_key(self) -> str:
        return self._device_preset_combo.currentData() or PRESET_CUSTOM

    def _get_device_field_widgets(self):
        return [
            self._device_make_edit,
            self._device_model_edit,
            self._device_software_edit,
            self._device_lens_make_edit,
            self._device_lens_model_edit,
            self._device_focal_length_edit,
            self._device_f_number_edit,
        ]

    @pyqtSlot(int)
    def _on_device_preset_changed(self, _index: int):
        preset_key = self._get_current_preset_key()
        self._settings.device_preset = preset_key

        if preset_key != PRESET_CUSTOM and preset_key in DEVICE_PRESETS:
            preset = DEVICE_PRESETS[preset_key]
            # Auto-fill the fields from the preset and persist them
            self._device_make_edit.setText(preset.make)
            self._device_model_edit.setText(preset.model)
            self._device_software_edit.setText(preset.software)
            self._device_lens_make_edit.setText(preset.lens_make)
            self._device_lens_model_edit.setText(preset.lens_model)
            self._device_focal_length_edit.setText(
                str(preset.focal_length) if preset.focal_length else ""
            )
            self._device_f_number_edit.setText(
                str(preset.f_number) if preset.f_number else ""
            )

        self._update_device_fields_editable()

    @pyqtSlot(str)
    def _on_device_field_changed(self, _text: str):
        """Persist all device fields whenever any field changes."""
        self._settings.device_make = self._device_make_edit.text()
        self._settings.device_model = self._device_model_edit.text()
        self._settings.device_software = self._device_software_edit.text()
        self._settings.device_lens_make = self._device_lens_make_edit.text()
        self._settings.device_lens_model = self._device_lens_model_edit.text()
        self._settings.device_focal_length = self._device_focal_length_edit.text()
        self._settings.device_f_number = self._device_f_number_edit.text()

    @pyqtSlot()
    def _on_open_folder(self):
        url = QUrl.fromLocalFile(str(self._settings.screenshot_folder))
        QDesktopServices.openUrl(url)

    @pyqtSlot()
    def _on_open_store(self):
        open_url(__store_url__)

    def _set_last_opened_screenshot(
        self, path: Path, metadata: Optional[Metadata] = None
    ):
        # self._form.view_last_screenshot.setEnabled(True)
        self._last_screenshot = path

        if (
            metadata
            and metadata.GPSLatitude is not None
            and metadata.GPSLongitude is not None
        ):
            self._form.view_last_location.show()
            self._form.view_last_location.setEnabled(True)
        self._last_metadata = metadata

    @pyqtSlot()
    def _on_open_last_screenshot(self):
        if not self._last_screenshot:
            return False
        elif not self._last_screenshot.is_file():
            self._notification_handler.notify(
                "File no longer exists", color=NotificationColor.error
            )
            return False
        url = QUrl.fromLocalFile(str(self._last_screenshot))
        QDesktopServices.openUrl(url)

    @pyqtSlot()
    def _on_open_last_location(self):
        if not self._last_metadata:
            return
        latitude = self._last_metadata.GPSLatitude
        longitude = self._last_metadata.GPSLongitude

        if latitude is None or longitude is None:
            print("Invalid GPS data for last screenshot")
            return

        url = self._maps_url.format(latitude=latitude, longitude=longitude)
        open_url(url)

    @pyqtSlot()
    def quit(self):
        self.closed.emit()
        QApplication.quit()

    def closeEvent(self, close_event: QCloseEvent) -> None:
        if self._settings.minimize_to_tray:
            self.showMinimized()
            close_event.ignore()
        else:
            self.closed.emit()
            return super().closeEvent(close_event)

    def changeEvent(self, event: QEvent):
        if event.type() != QEvent.Type.WindowStateChange:
            return super().changeEvent(event)
        if self.isMinimized() and self._settings.minimize_to_tray:
            event.ignore()
            QTimer.singleShot(0, self.hide)
