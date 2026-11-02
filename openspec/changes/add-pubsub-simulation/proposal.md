# Proposal

## Why

IT-Azubis sollen das Publish/Subscribe-Prinzip von MQTT (Broker, Topics, Fan-out,
Entkopplung, Retained Messages) am Tisch begreifen, bevor echte Hardware und ein echter
Broker ins Spiel kommen. Folk macht jede Rolle zu einem Blatt Papier: Abonnieren heißt
eine Karte hinlegen, eine Nachricht ist ein sichtbar wanderndes Paket. Die Simulation
läuft vollständig in Folk und hängt nicht von der noch offenen MQTT-Bridge
(`add-mqtt-bridge`) ab.

## What Changes

- Beispielanwendung „Taster → Broker → Motor + DB“ als Satz druckbarer Folk-Blätter:
  - **Taster** mit **Knopf-Karte**: Hand auf die Knopf-Karte = `gedrückt`, Hand weg =
    `losgelassen`; jeder Wechsel wird als Nachricht publiziert.
  - **Topic-Karten** (z. B. `halle/motor1`, `halle/#`): legen fest, auf welches Topic ein
    Taster publiziert bzw. was Motor/DB abonnieren.
  - **Retain-Karte**: neben dem Taster ⇒ Nachrichten werden als retained publiziert.
  - **Broker**-Blatt: verteilt Nachrichten an alle passenden Abonnenten (Fan-out,
    Wildcard `#`), speichert Retained Messages, zeigt eine Topic-Tabelle. Ohne Broker-Blatt
    wird nichts zugestellt.
  - **Motor**-Blatt: projiziertes Zahnrad dreht bei `gedrückt`, steht bei `losgelassen`.
  - **DB**-Blatt: protokolliert jede empfangene Nachricht (auch Wiederholungen) und zeigt
    die letzten Einträge als Tabelle; nur im Speicher von Folk.
- Visualisierung: Linien zwischen Clients und Broker, pro Nachricht wandernde Pakete
  (Taster → Broker → jeder Abonnent).
- Hilfsprogramm in `user-programs/carthag/` für Paket-Animation, damit die gedruckten
  Programme kurz und für Azubis lesbar bleiben.
- Quellen der Blätter und eine Anleitung mit Experimenten für den Unterricht im Repo.

Nicht im Umfang: echtes MQTT/Mosquitto, QoS, persistente Datenbank (SQLite),
Wildcard `+`, mehrere Broker, Last Will.

## Capabilities

### New Capabilities
- `pubsub-simulation`: Simulation eines Publish/Subscribe-Systems mit Folk-Blättern
  (Broker, Publisher, Subscriber, Topic- und Retain-Karten) inkl. Visualisierung des
  Nachrichtenflusses.

### Modified Capabilities
<!-- keine -->

## Impact

- Neue Datei `user-programs/carthag/pubsub-pakete.folk` (Paket-Animation, Verbindungslinien).
- Neues Verzeichnis `beispiele/pubsub/` mit Blatt-Quellen (`broker.folk`, `taster.folk`,
  `knopf.folk`, `motor.folk`, `db.folk`, `topic-karte.folk`, `retain-karte.folk`) und
  `README.md` (Aufbau, Druck, Experimente).
- Gedruckte Blätter landen wie üblich in `folk-data/program/` (per `sync.sh` gesichert).
- Nutzt vorhandenes `user-programs/carthag/connections.folk` für Linien.
- Keine Folk-Patches, keine neuen Pakete auf carthag. `add-mqtt-bridge` bleibt unberührt;
  die Event-Namen sind so gewählt, dass ein späteres Bridge-Blatt den Broker ersetzen kann.
