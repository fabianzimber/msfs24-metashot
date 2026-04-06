"""
Device preset templates for metadata simulation.

Provides built-in device profiles (e.g. iPhone 17 Pro) that set
Make, Model, Software, LensMake, LensModel, FocalLength, and FNumber
EXIF fields to mimic photos from specific devices.
"""

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class DevicePreset:
    """A collection of EXIF device fields for a specific camera/phone model."""

    label: str  # human-readable name shown in the UI dropdown
    make: str
    model: str
    software: str
    lens_make: str
    lens_model: str
    focal_length: Optional[float]  # mm
    f_number: Optional[float]

    def __str__(self) -> str:
        return self.label


# Key used internally; the label is what the user sees.
PRESET_DEFAULT = "default"
PRESET_IPHONE_17_PRO = "iphone_17_pro"
PRESET_IPHONE_17_PRO_MAX = "iphone_17_pro_max"
PRESET_CUSTOM = "custom"

DEVICE_PRESETS: Dict[str, DevicePreset] = {
    PRESET_DEFAULT: DevicePreset(
        label="MSFS MetaShot (default)",
        make="MSFS MetaShot",
        model="MSFS MetaShot",
        software="MSFS MetaShot",
        lens_make="",
        lens_model="",
        focal_length=None,
        f_number=None,
    ),
    PRESET_IPHONE_17_PRO: DevicePreset(
        label="Apple iPhone 17 Pro",
        make="Apple",
        model="iPhone 17 Pro",
        software="18.0",
        lens_make="Apple",
        lens_model="iPhone 17 Pro back triple camera 6.765mm f/1.78",
        focal_length=6.765,
        f_number=1.78,
    ),
    PRESET_IPHONE_17_PRO_MAX: DevicePreset(
        label="Apple iPhone 17 Pro Max",
        make="Apple",
        model="iPhone 17 Pro Max",
        software="18.0",
        lens_make="Apple",
        lens_model="iPhone 17 Pro Max back triple camera 6.765mm f/1.78",
        focal_length=6.765,
        f_number=1.78,
    ),
}

# Ordered list of preset keys for the UI dropdown (Custom goes last)
PRESET_ORDER = [
    PRESET_DEFAULT,
    PRESET_IPHONE_17_PRO,
    PRESET_IPHONE_17_PRO_MAX,
    PRESET_CUSTOM,
]


def get_preset_labels() -> Dict[str, str]:
    """Return mapping of preset key -> display label, including Custom."""
    labels = {key: DEVICE_PRESETS[key].label for key in PRESET_ORDER if key in DEVICE_PRESETS}
    labels[PRESET_CUSTOM] = "Custom"
    return labels
