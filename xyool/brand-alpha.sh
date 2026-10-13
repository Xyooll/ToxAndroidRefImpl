#!/usr/bin/env bash
# Xyool Connect (Tox) alpha. Rebrand copies at build-time; keep toxcore/JNI APIs unchanged.
set -euo pipefail
ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
python3 - "$ROOT" <<'PY'
from pathlib import Path
import sys

root = Path(sys.argv[1])
app = root / "android-refimpl-app" / "app"
gradle = app / "build.gradle"
manifest = app / "src" / "main" / "AndroidManifest.xml"
original_id = 'applicationId "com.zoffcc.applications.trifa"'
xyool_id = 'applicationId "org.xyool.connect.tox"'
body = gradle.read_text(encoding="utf-8")
if original_id in body:
    body = body.replace(original_id, xyool_id, 1)
elif xyool_id not in body:
    raise SystemExit("Cannot find verified TRIfA applicationId; refusing unsafe build")
gradle.write_text(body, encoding="utf-8")

text = manifest.read_text(encoding="utf-8")
if 'android:label="TRIfA"' in text:
    text = text.replace('android:label="TRIfA"',
                        'android:label="Xyool Connect (Tox)"', 1)
elif 'android:label="Xyool Connect (Tox)"' not in text:
    raise SystemExit("Cannot find expected upstream launcher label")
manifest.write_text(text, encoding="utf-8")

# The Java namespace stays upstream-compatible. These three authorities must be
# updated in Java and XML together to prevent cross-package install conflicts.
authorities = ("std_fileprovider", "ext2_provider", "ext1_fileprovider")
found = {x: 0 for x in authorities}
for path in (app / "src").rglob("*"):
    if not path.is_file() or path.suffix not in (".java", ".xml", ".kt"):
        continue
    original = path.read_text(encoding="utf-8")
    edited = original
    for suffix in authorities:
        old = "com.zoffcc.applications.trifa." + suffix
        new = "org.xyool.connect.tox." + suffix
        found[suffix] += original.count(old)
        edited = edited.replace(old, new)
    if edited != original:
        path.write_text(edited, encoding="utf-8")
for suffix in authorities:
    manifest_now = manifest.read_text(encoding="utf-8")
    if 'android:authorities="org.xyool.connect.tox.' + suffix + '"' not in manifest_now:
        raise SystemExit("Missing branded provider authority: " + suffix)
    if not found[suffix]:
        # Already branded source is allowed when script is rerun.
        if ("org.xyool.connect.tox." + suffix) not in manifest_now:
            raise SystemExit("Provider " + suffix + " could not be migrated")
print("Xyool alpha branding applied. Original native Tox/JNI APIs preserved.")
print("Provider rewrites:", found)
PY
