# Xyool Connect — decentralized P2P Android alpha

Xyool Connect is a separately branded Android client built from the open-source TRIfA/Tox implementation. It reuses the existing Tox distributed hash table, encrypted calls (ToxAV), conversations, identity and file transfer. **Xyool does not invent a second phone protocol or require the Xyool/Railway rendezvous backend.**

## Current Xyool identity

- App launcher and primary title: **Xyool Connect**
- App ID: `org.xyool.connect.tox` (stable alpha identity, distinct from upstream TRIfA and from Xyool's separate WebRTC app)
- Launcher icon: Xyool network nodes surrounding a phone receiver; vector fallback and adaptive launcher asset
- Colors: deep navy `#081825`, secondary navy `#12334A`, teal accent `#14B8A6`, glowing node detail `#2ED8C7`
- Main toolbar: Xyool symbol and title, without removing Tox online/away/busy presence controls
- Sharing, peer ID, settings and About text reflect the Xyool brand; About retains Tox/TRIfA attribution.

## Build the branded P2P alpha

```bash
git clone https://github.com/Xyooll/ToxAndroidRefImpl.git
cd ToxAndroidRefImpl
git checkout xyool/tox-connect-rebrand-20261013
bash xyool/brand-alpha.sh
python3 xyool/p2p-only.py
python3 xyool/p2p-only.py --verify
python3 xyool/verify-brand.py
cd android-refimpl-app
./gradlew :app:assembleDebug --no-daemon
```

The GitHub Actions workflow **Xyool Connect P2P Native Alpha** performs these policy/brand checks plus Android build, app identity and native library verification, then uploads the test APK as a workflow artifact. Debug signing may change across runs. Preserve contact history and identities only after configuring stable secure signing.

## Architecture and honest limitations

This alpha uses the existing Tox public DHT and available public bootstrap nodes. Some restrictive NAT pairs need volunteer TCP relay nodes that carry encrypted traffic; this is still peer-to-peer communication, but not literally zero intermediaries at the network layer. Optional third-party push notification paths are disabled by build policy, so Android battery savings/sleep may block timely off-screen incoming calls. No carrier SMS, telephone numbers, or emergency 911 calling is implemented.

## Required acceptance testing

Use the same signed APK on **two Android phones** across separate networks. Exchange native Tox peer IDs (not legacy `XY-...` IDs). Test text, photos, encrypted audio both ways, decline/hang-up/mute/speaker, contact persistence, Home/rotation/lock screen, app sleep and Wi-Fi/cellular changes. Test icon visibility, launcher name, status selector and About attribution. An Android CI success alone does not prove real-device audio or mobile background reliability.

## Source licenses

The Java package names, upstream native JNI symbols and Tox APIs intentionally remain compatible with the fork. Keep upstream author credits, `LICENSE-zzGPLv2`, `LICENSE-GPLv3` and other dependency licenses, and satisfy the GPL source availability terms. Xyool-specific name/artwork does not imply endorsement by upstream authors.
