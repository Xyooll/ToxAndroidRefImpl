#!/usr/bin/env python3
"""Static cross-layer smoke test for the *assembled* Xyool Connect/Tox alpha.

Run after brand-alpha.sh and p2p-only.py. This proves that source entrypoints
and Android declarations are wired together; it cannot prove live P2P reachability.
"""
from pathlib import Path
from xml.etree import ElementTree as ET
import re

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / "android-refimpl-app/app"
MAIN = APP / "src/main"
SRC = MAIN / "java/com/zoffcc/applications/trifa"
A = "{http://schemas.android.com/apk/res/android}"


def require(test, description):
    if not test:
        raise AssertionError("Xyool assembly failed: " + description)
    print("PASS:", description)


def source(name):
    return (SRC / name).read_text(encoding="utf-8")


def main():
    gradle = (APP / "build.gradle").read_text(encoding="utf-8")
    require('applicationId "org.xyool.connect.tox"' in gradle,
            "single Xyool Connect Android application identity")
    require("namespace 'com.zoffcc.applications.trifa'" in gradle,
            "preserve original Tox/JNI package namespace")

    xml = ET.parse(MAIN / "AndroidManifest.xml").getroot()
    app = xml.find("application")
    require(app is not None, "Android application declared")
    require(app.get(A + "label") == "@string/app_name",
            "launcher label from Xyool brand resource")
    require(app.get(A + "icon") == "@mipmap/xyool_launcher",
            "launcher artwork and shared brand in one APK")
    permissions = {x.get(A + "name") for x in xml.findall("uses-permission")}
    require({"android.permission.INTERNET", "android.permission.RECORD_AUDIO"} <= permissions,
            "internet and microphone permissions available for native calling")

    activities = {x.get(A + "name"): x for x in app.findall("activity")}
    for name in (".StartMainActivityWrapper", ".MainActivity", ".AddFriendActivity",
                 ".MessageListActivity", ".CallingActivity", ".ShareActivity", ".ProfileActivity"):
        require(name in activities, name + " activity wired in the same app")

    incoming_actions = set()
    schemes = set()
    mime = set()
    for filt in activities[".ShareActivity"].findall("intent-filter"):
        incoming_actions |= {x.get(A + "name") for x in filt.findall("action")}
        for x in filt.findall("data"):
            if x.get(A + "scheme"):
                schemes.add(x.get(A + "scheme"))
            if x.get(A + "mimeType"):
                mime.add(x.get(A + "mimeType"))
    require({"android.intent.action.SEND", "android.intent.action.SEND_MULTIPLE",
             "android.intent.action.VIEW"} <= incoming_actions,
            "share single/multiple content and open peer links")
    require("tox" in schemes and "image/*" in mime,
            "existing Tox ID links and image sharing retained")

    service = {x.get(A + "name"): x for x in app.findall("service")}
    require(".TrifaToxService" in service and
            service[".TrifaToxService"].get(A + "exported") == "false",
            "service-owned phone node is not externally exported")

    providers = [x.get(A + "authorities") for x in app.findall("provider")]
    expected = {f"org.xyool.connect.tox.{suffix}" for suffix in
                ("std_fileprovider", "ext2_provider", "ext1_fileprovider")}
    require(expected <= set(providers),
            "providers migrated with package to support Android file sharing")

    # Fail CI if Android component export scopes regress after the build-time rebrand.
    provider_nodes = {x.get(A + "name"): x for x in app.findall("provider")}
    for name in (".StdContentProvider", ".Ext2ContentProvider", ".IOCipherContentProvider"):
        provider = provider_nodes.get(name)
        require(provider is not None and provider.get(A + "exported") == "false" and
                provider.get(A + "grantUriPermissions") == "true",
                name + " private provider with explicit URI grants")
    receiver_nodes = {x.get(A + "name"): x for x in app.findall("receiver")}
    wakeup = receiver_nodes.get(".WakeupAlarmReceiver")
    require(wakeup is not None and wakeup.get(A + "exported") == "false",
            "internal wakeup alarm receiver cannot be triggered by external apps")

    ui = ET.parse(MAIN / "res/layout/activity_main.xml").getroot()
    ids = {x.get(A + "id") for x in ui.iter()}
    require({"@+id/xyool_toolbar_mark", "@+id/spinner_own_status",
             "@+id/drawer_container", "@+id/fl_fragment"} <= ids,
            "branded home and original contact/presence navigation coexist")

    main_java = source("MainActivity.java")
    calls = source("CallingActivity.java")
    messages = source("MessageListActivity.java")
    files = source("HelperFiletransfer.java")
    friends = source("HelperFriend.java")
    tox_service = source("TrifaToxService.java")
    require(re.search(r"native int toxav_call\s*\(", main_java) is not None and
            re.search(r"native int toxav_answer\s*\(", main_java) is not None,
            "native encrypted ToxAV call/answer available to app")
    require("toxav_answer(" in calls and "setContentView(R.layout.activity_calling)" in calls,
            "native ToxAV answer wired to call screen")
    require("tox_friend_send_message_wrapper" in messages and
            "R.layout." in messages, "peer messages wired to Android message screen")
    require("tox_file_send(" in files and "start_outgoing_ft(" in files,
            "photos and files wired to Tox native file transfer")
    require("add_friend_real(" in friends,
            "peer ID contact add wired to Tox friend engine")
    require("tox_iterate();" in tox_service and "add_tcp_relay_single_wrapper" in tox_service,
            "phone service uses original DHT iteration and optional Tox TCP relay")
    require("PREF__use_push_service = true;" not in main_java and
            'PREF__use_push_service = settings.getBoolean' not in main_java,
            "optional legacy third-party push disabled in Xyool build")

    strings = ET.parse(MAIN / "res/values/strings.xml").getroot()
    names = {x.get("name"): (x.text or "") for x in strings if x.tag == "string"}
    require(names.get("app_name") == "Xyool Connect", "coherent Xyool app name")
    require("Tox" in names.get("Aboutpage_5a", ""), "upstream Tox compatibility attribution")
    require("peer id" in names.get("add_friend_activity_help", "").lower(),
            "contact onboarding explains native peer ID")
    print("PASS: assembled Xyool Connect app source integration checks")
    print("NOT RUN: actual Android runtime, network traversal, calls or push/sleep behavior")


if __name__ == "__main__":
    main()
