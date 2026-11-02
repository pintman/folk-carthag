# Tasks

## 1. Broker auf carthag

- [ ] 1.1 `mosquitto/folk.conf` im Repo anlegen (`listener 1883`, `allow_anonymous true`); prüfen: Datei enthält genau diese Einstellungen mit Kommentar
- [ ] 1.2 Auf carthag `sudo apt install mosquitto mosquitto-clients`, `folk.conf` nach `/etc/mosquitto/conf.d/` kopieren, `sudo systemctl enable --now mosquitto`; prüfen: `systemctl is-enabled mosquitto` = enabled, `ss -tln` zeigt `0.0.0.0:1883`
- [ ] 1.3 Test vom Mac: `mosquitto_sub -h carthag.local -t test` und `mosquitto_pub -h carthag.local -t test -m hallo`; prüfen: Nachricht kommt an (Spec „Gerät im LAN verbindet sich“)
- [ ] 1.4 README-Abschnitt „MQTT – Broker“ (Installation, Deployment der Konfiguration, Testbefehle) und Wiederherstellen-Abschnitt um `folk.conf` ergänzen; prüfen: dokumentierte Befehle laufen wie beschrieben

## 2. Empfangen (mosquitto_sub → Claim)

- [ ] 2.1 `user-programs/carthag/mqtt.folk` anlegen mit Subscriber-Schleife (Claim `$this runs the mqtt subscriber`, `open "|mosquitto_sub -h localhost -v -t #" r`, non-blocking, max. N Zeilen/Tick, Split am ersten Leerzeichen, `Hold! -key [list mqtt $topic] Claim mqtt topic $topic has message $payload`, `On unmatch` beendet Prozess); prüfen: nach `mosquitto_pub -t sensor/temp -m 42` zeigt `http://carthag.local:4273/statements` den Claim
- [ ] 2.2 Ersetzen und Nebeneinander prüfen: `42` dann `43` auf `sensor/temp`, zusätzlich `a`/`b`, und `Hallo Welt` auf `display/text`; prüfen: Claims wie in den Spec-Szenarien, `Hallo Welt` vollständig
- [ ] 2.3 Neustart-Schleife: bei EOF von `mosquitto_sub` nach 2 s neu öffnen; prüfen: `sudo systemctl restart mosquitto`, danach publizierte Nachricht erscheint als Claim (Spec „Broker wird neu gestartet“)
- [ ] 2.4 Unmatch-Verhalten prüfen: `mqtt.folk` bearbeiten/neu laden; prüfen: `pgrep -c mosquitto_sub` liefert danach 1 (kein verwaister Prozess, keine weiterlaufende alte Schleife)
- [ ] 2.5 README-Abschnitt „MQTT – Empfangen“ mit Beispiel (`When mqtt topic sensor/temp has message /m/ { Wish $this is labelled $m }`) und Einschränkungen (mehrzeilige Payloads, Topics mit Leerzeichen); prüfen: Beispiel als Blatt ausprobiert, Label erscheint

## 3. Senden (Wish → mosquitto_pub)

- [ ] 3.1 In `mqtt.folk` `When /someone/ wishes mqtt publishes /m/ on topic /t/` mit `catch {exec mosquitto_pub -h localhost -t $t -m $m &}` und `puts stderr` bei Fehler; prüfen: Blatt mit `Wish mqtt publishes on on topic led/1`, `mosquitto_sub -h carthag.local -t led/1` empfängt genau einmal `on`
- [ ] 3.2 Message-Wechsel und Rückkanal prüfen: Wish auf `off` ändern → `off` kommt an; Claim `mqtt topic led/1 has message off` existiert
- [ ] 3.3 Broker gestoppt (`sudo systemctl stop mosquitto`) und Blatt sendet; prüfen: Folk läuft weiter, Fehler im Log (`journalctl -u folk`), danach Broker wieder starten
- [ ] 3.4 README-Abschnitt „MQTT – Senden“ inkl. Hinweis, dass erneutes Erkennen eines Blatts erneut sendet; prüfen: Beispiel aus README funktioniert

## 4. Abschluss

- [ ] 4.1 `./sync.sh` ausführen; prüfen: `user-programs/carthag/mqtt.folk` im Repo identisch mit carthag
- [ ] 4.2 TODO.md aktualisieren: erledigte Punkte abhaken/entfernen, offene (Websocket, Pico-W-Beispiel, C-FFI) behalten; prüfen: TODO.md enthält nur offene Punkte
