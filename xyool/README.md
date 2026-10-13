# Xyool Connect — Tox-native alpha

This Xyool-owned fork is based on the functioning TRIfA Android client and Tox network. It is **not** a new networking protocol.

## Reproduce the alpha build

```bash
git clone https://github.com/Xyooll/ToxAndroidRefImpl
cd ToxAndroidRefImpl
git checkout xyool/tox-branded-alpha-20261013
bash xyool/brand-alpha.sh
cd android-refimpl-app
./gradlew :app:assembleDebug
```

The script only changes the application ID, launcher label and the three hard-coded Android FileProvider authorities in the local build tree. Original native Tox/JNI symbol packages, DHT, ToxAV, encryption and relay behavior remain unchanged. It intentionally does **not** import the legacy Xyool WebRTC `XY-....` aliases or install Cloudflare/Railway.

The APK has a **different application ID** (`org.xyool.connect.tox`) from existing Xyool Connect WebRTC alpha and upstream TRIfA. The new app generates its own native Tox ID. No claims are made that the build has passed real-world calls until two phones confirm audible two-way audio.

**This stage still inherits upstream's optional Google/Firebase wakeup capability.** Do not call this a fully third-party-free build. Do not enable third-party push settings. A later review must remove optional dependencies *without* replacing the Tox network or weakening call reliability.

**Signing:** GitHub CI uses Android's temporary debug signature. APKs from separate CI runs may not update over one another. Do not put valuable contact history into this prototype before stable, securely-held release/test signing is configured.

## Next acceptance test

1. On two phones, install this experimental alpha; create native Tox identities.
2. Add each other as contacts via **Tox IDs** (not legacy XY aliases). Test text and pictures.
3. With each phone on a separate Wi-Fi network, perform a two-way encrypted audio call. Check both earpiece/speaker/mute.
4. Rotate, background, lock screen, end call, redial. Repeat 5 times and record what fails.
5. Evaluate mobile DHT bootstrap requirements, direct UDP and volunteer TCP relay fallback. Nodes may bootstrap the DHT; an online, reachable volunteer relay can still be required for certain NAT pairs.
6. Only after passing, begin user interface adaptation, contacts migration and removal of optional Google push.

## Attribution and license

Preserve `LICENSE-zzGPLv2`, `LICENSE-GPLv3`, original author notices, provenance and applicable dependencies' licenses. Forking/modifying software does not transfer copyright ownership over upstream work. Follow applicable GPL source distribution obligations. This Xyool-specific packaging work does not imply endorsement by TRIfA/Tox maintainers.
