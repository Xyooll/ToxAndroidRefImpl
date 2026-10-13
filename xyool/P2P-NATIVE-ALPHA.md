# Xyool Connect — decentralized Tox phone (P2P-only alpha)

**Work branch:** xyool/tox-p2p-only-20261013, based on the already-branded Tox-native fork. This uses established Tox DHT, native ToxAV encrypted audio/video calls, messages and file transfer rather than inventing another signaling protocol.

## What "no middlemen" means here

- No Xyool-operated central call router or Railway/WebRTC signaling requirement. Tox nodes identify each other by native Tox IDs; phones are communicating peers.
- No third-party mobile push wakeups in this alpha. xyool/p2p-only.py fails closed when expected upstream code changes, resets old opt-ins to OFF and gates known push URL/token-sending code. Policy is reapplied in CI to check idempotence.
- Not absolute infrastructure independence. Bootstrap DHT nodes assist joining the public Tox network. When direct traffic is blocked by NAT or firewalls, volunteer TCP relay nodes may transport encrypted packets. Those nodes cannot read application plaintext, but may observe network metadata. No internet app can promise global connectivity with zero intermediary packets behind all mobile NATs.
- Not the cellular telephone network. No carrier SMS/MMS, E.164 phone number interoperability, or emergency 911 calling. Both people need compatible Tox/Xyool clients and Internet access.

## Features retained from existing code

Tox-native client code provides text messaging, contact requests, sending files/images, encrypted voice and video calls and decentralized discovery. This branch leaves those engines intact. The Android package is org.xyool.connect.tox; it does not share the older Xyool XY-.... WebRTC ID database. Existing TRIfA installs are left alone.

## Build

The GitHub Actions workflow Xyool Connect P2P Native Alpha produces an artifact named Xyool-Connect-P2P-Native-Alpha containing app-debug.apk.

Local build sequence:

    bash xyool/brand-alpha.sh
    python3 xyool/p2p-only.py
    python3 xyool/p2p-only.py --verify
    cd android-refimpl-app
    ./gradlew :app:assembleDebug

Temporary debug signing means independently built APKs may not install as updates to one another. Do not store irreplaceable chats/identities in an alpha. Establish durable protected signing before release. Keep upstream GPL notices, licenses and matching source availability.

## Real phone acceptance gates — not proven by CI

1. Install the identical build on two physical Android phones. Create and mutually add native Tox IDs via QR or copied Tox address, not legacy Xyool IDs.
2. Test two-way text, photos/files, voice call, accept/decline, mute, speaker and hang-up across distinct Wi-Fi and mobile data networks.
3. Repeat voice calls five times in each direction. Check ringing with both apps open, then Home, screen lock, rotation, network transitions, ordinary Android service suspension and force-stop.
4. Confirm calls do not use Xyool/Railway signaling. Record direct UDP versus relay connection type, without publishing peer IDs, credentials, IP addresses, or message content.
5. Attempt restrictive cellular and guest Wi-Fi. With push OFF, Android sleep or force-stop can delay/miss calls; do not suppress or misrepresent such failures. Obtain explicit consent for any future optional helper/wakeup service.
6. Complete a security/privacy review including the original native dependencies and practical two-device test before production approval.

**An APK build alone cannot prove live encrypted two-way audio or dependable background ringing on the target phones.** This is an experimental installable app with a real established P2P transport, not a completed carrier-replacement telephone service.
