#!/usr/bin/env python3
"""Xyool Tox P2P-only build: disable optional third-party push paths.

Runs only in an isolated checked-out build tree. Do not alter native Tox
networking, ToxAV, bootstrap/DHT, local message or file-transfer behavior.
"""
from pathlib import Path
import argparse
import re

ROOT = Path(__file__).resolve().parent.parent
JAVA = ROOT / "android-refimpl-app/app/src/main/java/com/zoffcc/applications/trifa"


def substitute(data: str, before: str, after: str, count: int, label: str) -> str:
    """Exact, idempotent edits; abort when an upstream change invalidates a guard."""
    existing = data.count(before)
    if existing == count:
        return data.replace(before, after)
    if existing == 0 and data.count(after) >= count:
        return data
    raise ValueError(f"{label}: expected {count} original or patched occurrences, found {existing}")


def apply() -> None:
    main = JAVA / "MainActivity.java"
    data = main.read_text(encoding="utf-8")
    for old, new, count in (
        ('PREF__use_push_service = true;', 'PREF__use_push_service = false;', 3),
        ('PREF__use_push_service = settings.getBoolean("use_push_service", true);',
         'PREF__use_push_service = false; // Xyool P2P-only: ignore stored push opt-ins', 2),
        ('PREF__allow_push_server_ntfy = settings.getBoolean("allow_push_server_ntfy", false);',
         'PREF__allow_push_server_ntfy = false; // Xyool P2P-only', 2),
        ('PREF__allow_push_server_sunup = settings.getBoolean("allow_push_server_sunup", false);',
         'PREF__allow_push_server_sunup = false; // Xyool P2P-only', 2),
        ('PREF__hide_setup_push_tip = false;', 'PREF__hide_setup_push_tip = true;', 1),
    ):
        data = substitute(data, old, new, count, str(main))
    main.write_text(data, encoding="utf-8")

    guards = {
        "HelperFriend.java": (
            '    static void send_pushurl_to_friend(final String friend_pubkey)\n    {',
            '    static void send_pushurl_to_all_friends()\n    {',
        ),
        "HelperRelay.java": (
            '    static void own_push_token_load()\n    {',
            '    static void send_pushtoken_to_relay()\n    {',
        ),
    }
    for filename, methods in guards.items():
        file = JAVA / filename
        source = file.read_text(encoding="utf-8")
        for signature in methods:
            guarded = signature + '\n        if (!MainActivity.PREF__use_push_service) return; // Xyool P2P-only'
            if guarded in source:
                continue
            if source.count(signature) != 1:
                raise ValueError(f"{filename}: expected one signature {signature.strip()}")
            source = source.replace(signature, guarded, 1)
        file.write_text(source, encoding="utf-8")
    verify()


def verify() -> None:
    main = (JAVA / "MainActivity.java").read_text(encoding="utf-8")
    assert 'PREF__use_push_service = true;' not in main
    assert 'PREF__use_push_service = settings.getBoolean' not in main
    assert 'PREF__allow_push_server_ntfy = settings.getBoolean' not in main
    assert 'PREF__allow_push_server_sunup = settings.getBoolean' not in main
    assert 'PREF__hide_setup_push_tip = true;' in main
    assert len(re.findall(r'PREF__use_push_service = false;', main)) >= 5
    for filename, names in {
        "HelperFriend.java": ["send_pushurl_to_friend", "send_pushurl_to_all_friends"],
        "HelperRelay.java": ["own_push_token_load", "send_pushtoken_to_relay"],
    }.items():
        source = (JAVA / filename).read_text(encoding="utf-8")
        for name in names:
            pattern = r'static void ' + name + r'\([^)]*\)\s*\{\s*if \(!MainActivity\.PREF__use_push_service\) return;'
            if not re.search(pattern, source):
                raise AssertionError(f"Ungated third-party push path: {filename}::{name}")
    print("PASS: legacy third-party push delivery is disabled in Xyool build")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    verify() if args.verify else apply()
