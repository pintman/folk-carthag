# Design

## Context

- carthag: Linux Mint 22.2 (Ubuntu 24.04-Basis), Folk-Repo `/home/folk/folk`
  (Stand `11121f5`), Jim Tcl. Mosquitto ist noch nicht installiert.
- Folk bringt `builtin-programs/unix-commands.folk` mit: startet einen Prozess per
  `open "|cmd …" r`, liest nicht-blockierend in einer Schleife (`gets`, `after 100`),
  räumt per `On unmatch` auf (SIGTERM/SIGKILL) und veröffentlicht Ergebnisse mit
  `Hold! -key … Claim …`. Es sammelt aber alle Zeilen in einem 500-Zeilen-Fenster als
  einen Claim – ungeeignet, um pro Nachricht/Topic einen eigenen Claim zu bilden.
- Eigene Programme liegen in `user-programs/carthag/` und werden beim Start geladen.

## Goals / Non-Goals

**Goals:**
- Ein einziges, selbstständiges User-Programm ohne Folk-Patch.
- Muster aus `unix-commands.folk` wiederverwenden (Prozess, Non-Blocking-Read, Hold!).

**Non-Goals:**
- Wildcard-Abos pro Blatt (`When mqtt topic sensor/# …` erledigt Folk-Pattern-Matching
  über `/t/` ohnehin), QoS-/Retain-Steuerung, mehrzeilige Payloads.

## Decisions

1. **Empfang über eigenen `mosquitto_sub`-Prozess statt `Wish … runs Unix command`.**
   `mosquitto_sub -h localhost -v -t '#'` liefert pro Nachricht eine Zeile
   `topic payload`. Aufgeteilt wird am ersten Leerzeichen (`string first`), damit
   Payloads mit Leerzeichen erhalten bleiben. `#` schließt `$SYS/…` per MQTT-Standard
   bereits aus.
   *Alternative:* Builtin-Wish nutzen und neue Zeilen aus dem 500er-Fenster diffen –
   fehleranfällig (Fenster rotiert, gleiche Zeilen doppelt).

2. **Ein Claim pro Topic via `Hold! -key [list mqtt $topic]`.**
   Neue Nachricht überschreibt den Hold desselben Keys → genau ein Claim pro Topic,
   Claims verschiedener Topics bleiben bestehen (Spec „Neuere Nachricht ersetzt ältere“).
   *Alternative:* `Claim -keep 5s` – Nachrichten verschwänden, Zustand (z. B. letzter
   Sensorwert) ginge verloren.

3. **Prozess-Schleife in einem `When`-Body, der durch einen eigenen Claim ausgelöst wird**
   (`Claim $this runs the mqtt subscriber` + `When $this runs the mqtt subscriber { … }`),
   analog zum Body in `unix-commands.folk`. Äußere Schleife: endet `mosquitto_sub`
   (EOF, z. B. Broker-Neustart), nach 2 s neu starten. `On unmatch` beendet den Prozess,
   wenn das Programm neu geladen wird. Pro Tick höchstens N Zeilen lesen (wie Builtin),
   damit Nachrichtenfluten nicht blockieren.

4. **Senden mit `exec mosquitto_pub -h localhost -t $t -m $m &` im Hintergrund**,
   ausgelöst von `When /someone/ wishes mqtt publishes /m/ on topic /t/`. Hintergrund-
   `exec` blockiert Folk nicht; Fehler werden per `catch` abgefangen und mit `puts stderr`
   ins Folk-Log geschrieben. Der When-Body läuft einmal pro neuem Match → einmal senden
   pro Wish bzw. pro geänderter Message/Topic.
   *Alternative:* dauerhaft offener `mosquitto_pub -l` (liest Zeilen von stdin) – spart
   Prozessstarts, unterstützt aber nur ein festes Topic pro Prozess.

5. **Broker-Konfiguration `mosquitto/folk.conf` im Repo** mit `listener 1883` und
   `allow_anonymous true`, deployt nach `/etc/mosquitto/conf.d/folk.conf`. Mosquitto 2.x
   lauscht ohne `listener` nur auf localhost.

## Risks / Trade-offs

- [Mehrzeilige Payloads werden falsch zerlegt (Folgezeilen ohne Topic)] → als
  Einschränkung im README dokumentieren; später ggf. `-F` mit Hex-Payload oder C-FFI.
- [Topics mit Leerzeichen werden falsch getrennt] → in MQTT unüblich; dokumentieren.
- [Anonymer Broker im LAN: jeder im Netz kann publizieren/lesen] → akzeptiert für
  Schul-/Heimnetz; TLS/Auth bleibt Non-Goal.
- [Viele Topics → viele Holds, die nie verschwinden] → akzeptiert; Neustart von Folk
  leert sie.
- [Re-Evaluation eines Blatts (Neu-Erkennen nach Verdecken) löst erneutes Senden aus]
  → erwartetes Folk-Verhalten, im README erwähnen.
- [Endlosschleife im When-Body läuft nach Unmatch weiter] → in der Umsetzung prüfen, ob
  Folk den Body abbricht (wie bei `unix-commands.folk`); sonst Schleife bei geschlossenem
  fd verlassen.

## Migration Plan

1. `sudo apt install mosquitto mosquitto-clients` auf carthag, `folk.conf` deployen,
   `sudo systemctl enable --now mosquitto`.
2. `mqtt.folk` nach `/home/folk/folk/user-programs/carthag/` kopieren; Folk lädt es
   (fswatch-Patch) bzw. Folk neu starten.
3. Rollback: `mqtt.folk` entfernen, `sudo systemctl disable --now mosquitto`.
