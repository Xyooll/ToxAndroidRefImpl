#!/usr/bin/env python3
"""Validate Xyool Connect branding without running or changing Tox networking."""
from pathlib import Path
from xml.etree import ElementTree as ET

BASE = Path(__file__).resolve().parent.parent / "android-refimpl-app/app/src/main"
A = "{http://schemas.android.com/apk/res/android}"


def main():
    manifest = ET.parse(BASE / "AndroidManifest.xml").getroot()
    application = manifest.find("application")
    assert application is not None
    assert application.attrib[A + "label"] == "@string/app_name"
    assert application.attrib[A + "icon"] == "@mipmap/xyool_launcher"
    assert application.attrib[A + "roundIcon"] == "@mipmap/xyool_launcher"

    strings = ET.parse(BASE / "res/values/strings.xml").getroot()
    values = {x.attrib.get("name"): (x.text or "") for x in strings if x.tag == "string"}
    assert values["app_name"] == "Xyool Connect"
    assert "Xyool Connect" in values["title_activity_share"]
    assert "powered by Tox" in values["Aboutpage_5a"]
    assert "Xyool Connect" in values["MainActivity_add_to_batt_opt"]
    assert values["layout___copy_toxid"] == "Copy my peer ID"

    colors = ET.parse(BASE / "res/values/colors.xml").getroot()
    palette = {x.attrib.get("name"): (x.text or "").upper() for x in colors if x.tag == "color"}
    assert palette["colorPrimary"] == "#12334A"
    assert palette["colorPrimaryDark"] == "#081825"
    assert palette["colorAccent"] == "#14B8A6"

    mark = ET.parse(BASE / "res/drawable/xyool_connect_mark.xml").getroot()
    assert mark.tag == "vector", "Keep Xyool launcher mark vector"
    assert len(mark.findall("path")) >= 4
    assert len(mark.findall("group")) >= 1

    legacy_icon = ET.parse(BASE / "res/mipmap-anydpi/xyool_launcher.xml").getroot()
    adaptive = ET.parse(BASE / "res/mipmap-anydpi-v26/xyool_launcher.xml").getroot()
    assert legacy_icon.tag == "vector"
    assert adaptive.tag == "adaptive-icon"
    assert adaptive.find("foreground").attrib[A + "drawable"] == "@drawable/xyool_connect_mark"

    screen = ET.parse(BASE / "res/layout/activity_main.xml").getroot()
    image = screen.find(".//ImageView/..")  # structural XML parsing sanity
    assert image is not None
    toolbar_logo = next((x for x in screen.iter() if x.attrib.get(A + "id") == "@+id/xyool_toolbar_mark"), None)
    assert toolbar_logo is not None
    assert toolbar_logo.attrib.get(A + "src") == "@drawable/xyool_connect_mark"
    assert any(x.attrib.get(A + "id") == "@+id/spinner_own_status" for x in screen.iter()), \
        "Presence controls must survive the visual rebrand"

    print("PASS: Xyool brand name, launcher icon, toolbar, theme and settings identity")


if __name__ == "__main__":
    main()
