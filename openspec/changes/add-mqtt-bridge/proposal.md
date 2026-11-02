# Proposal

## Why

Folk auf carthag kennt bisher nur Kamera, Projektor, Tastatur und Unix-Befehle als
Ein-/Ausgabe. Über MQTT lassen sich WLAN-Mikrocontroller (Pico W, MatrixPortal …),
Handys und Webseiten als Sensoren und Aktoren an Folk-Blätter anbinden
(Idee: <https://folk.computer/notes/mqtt>). Die im Artikel genutzte Tcl-MQTT-Bibliothek
(Tcl 8.6, TclOO, Coroutinen) läuft nicht unter Jim Tcl – daher eine Bridge über die
`mosquitto`-Kommandozeilenwerkzeuge.

## What Changes

- Mosquitto-Broker auf carthag (Port 1883, im LAN erreichbar, anonym), Konfiguration
  als Datei im Repo versioniert.
- Neues User-Programm `user-programs/carthag/mqtt.folk`:
  - Empfangen: dauerhaft laufendes `mosquitto_sub`, jede eingehende Nachricht wird zu
    `Claim mqtt topic <t> has message <m>` (letzte Nachricht pro Topic).
  - Senden: `Wish mqtt publishes <m> on topic <t>` ruft `mosquitto_pub` auf.
  - Automatischer Neustart von `mosquitto_sub`, falls der Prozess endet.
- README-Abschnitt „MQTT“ mit Benutzung und Testbefehlen; Sicherung/Wiederherstellung
  der Mosquitto-Konfiguration.
- TODO.md entsprechend aktualisieren.

Nicht im Umfang (bleiben in TODO.md): Websocket-Listener für MQTT.js-Webseiten,
Pico-W-Beispiel, libmosquitto per C-FFI, Retained-Publish/QoS-Optionen, TLS/Auth.

## Capabilities

### New Capabilities
- `mqtt-bridge`: MQTT-Broker auf carthag und Abbildung von MQTT-Nachrichten auf
  Folk-Statements (Empfangen als Claim, Senden per Wish).

### Modified Capabilities
<!-- keine -->

## Impact

- carthag: neues Paket `mosquitto`/`mosquitto-clients`, systemd-Dienst `mosquitto`,
  offener Port 1883 im LAN.
- Neue Dateien: `user-programs/carthag/mqtt.folk`, `mosquitto/folk.conf` (Repo),
  Deployment nach `/etc/mosquitto/conf.d/folk.conf`.
- `README.md`, `TODO.md`. `sync.sh` bleibt unverändert: die Repo-Kopie der
  Mosquitto-Konfiguration ist die Quelle, carthag erhält sie per Deployment.
- Keine Änderung an Folk-Builtins; keine Patches nötig.
