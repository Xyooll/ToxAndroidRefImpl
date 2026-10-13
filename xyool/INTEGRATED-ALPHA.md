# Xyool Connect — integrated Android alpha

This branch assembles the existing Xyool Connect rebrand with its existing native Tox peer network in **one installable Android application**. It does **not** replace Tox with separate Xyool WebRTC signaling, create competing identity/address systems, or add new required infrastructure.

## Source-to-screen wiring

| User action / UI | Android component | Native implementation |
|---|---|---|
| Launch app / see brand + startup | StartMainActivityWrapper → MainActivity, activity_main.xml | TrifaToxService and native JNI toxcore |
| Show identity, exchange QR / add contacts | ProfileActivity, AddFriendActivity | Native Tox ID and HelperFriend |
| Write a message | FriendListFragment → MessageListActivity | tox_friend_send_message_wrapper / Tox |
| Share a photo/file | ShareActivity, MessageListActivity | HelperFiletransfer, native tox_file_send |
| Call / answer / hang up | CallingWaitingActivity, CallingActivity | toxav_call, toxav_answer and ToxAV |
| Maintain phone node across UI changes | TrifaToxService | Tox DHT iteration, ordinary bootstrap and optional encrypted TCP relay |
| Disable optional third-party push | xyool/p2p-only.py | Build-time policy defaults, preference hiding and gated push send paths |
| Xyool name / icon / colors | AndroidManifest, values, toolbar, mipmap | xyool/brand-alpha.sh, verify-brand.py |

An accessible DHT bootstrap node and sometimes TCP relay can still be required for reachability behind restrictive NAT. Neither role is a mandatory Xyool account or central call controller. **The main screen's “Xyool engine ready” means native libraries loaded, not that a remote phone is reachable.**

## Reproducible unified build

From this branch:

    bash xyool/brand-alpha.sh
    python3 xyool/p2p-only.py
    python3 xyool/p2p-only.py --verify
    python3 xyool/verify-brand.py
    python3 xyool/verify-integration.py
    cd android-refimpl-app
    ./gradlew :app:assembleDebug --no-daemon

GitHub Actions workflow **Xyool Connect P2P Native Alpha** runs the same policy + static integration checks, compiles Android, checks native ARM64 libraries and signature, and creates the APK artifact. Static integration checks are only source wiring assertions. A passing workflow is **not** real-device proof.

## Device test acceptance, in order

1. One installable package displays Xyool Connect icon and name, opens without crash, and leaves its existing Tox identity intact on reopen.
2. Phone A and B, each with Xyool Network running, exchange native Tox IDs or QR. Verify contact entry and delivery of plain text.
3. Share a photo to Xyool Connect from Android's share sheet, and return photo/file both ways. Verify incoming file accessibility with user consent.
4. Make an audible **two-way voice call** across independent Wi-Fi/cellular networks. Check ringing, answer, decline, hang-up, microphone, mute and speaker.
5. Repeat with app backgrounded/locked, network switches and Android battery restrictions. If no optional push wakeup is configured, some incoming rings can be delayed/missed when Android suspends the service.
6. Security review exported Android receivers/providers, privacy, key handling, open-source licenses, and signing-key continuity before general release.

**Do not mix this APK with the separate Xyool WebRTC alpha.** Different app IDs use different peer identities; the legacy XY-.... WebRTC aliases are not native Tox addresses. This build supports encrypted app-to-app messages, photos and calling, not ordinary carrier SMS/MMS or 911.

### Integration rules

- Single P2P transport: keep established Tox DHT + native media/file protocol and avoid inventing another identity system.
- One brand/UI and one Android APK for phone users.
- Never expose unverified “online”, “guaranteed delivery”, “no intermediary packets” or “works when force-stopped” claims.
- Maintain source attribution and GPL obligations, document limitations.
- Build success, physical device success and carrier interoperability must be reported separately.
