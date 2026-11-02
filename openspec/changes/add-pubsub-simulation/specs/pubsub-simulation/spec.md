# Spec Delta

## Purpose

Macht das Publish/Subscribe-Prinzip (Broker, Topics, Fan-out, Wildcards, Retained
Messages) mit Folk-Blättern am Tisch erfahrbar, ohne echten MQTT-Broker – als
Unterrichtsbeispiel für IT-Azubis.

## ADDED Requirements

### Requirement: Topic-Karten bestimmen das Topic
Ein Client-Blatt (Taster, Motor, DB) SHALL das Topic verwenden, das auf der Topic-Karte
steht, die links neben ihm liegt. Ein Taster publiziert auf dieses Topic, Motor und DB
abonnieren es. Liegt keine Topic-Karte an, publiziert bzw. abonniert das Blatt nichts.

#### Scenario: Abonnieren durch Hinlegen
- **WHEN** die Karte `halle/motor1` links neben das Motor-Blatt gelegt wird
- **THEN** empfängt der Motor ab sofort Nachrichten auf `halle/motor1`

#### Scenario: Abbestellen durch Wegnehmen
- **WHEN** die Topic-Karte des Motors entfernt wird und danach der Taster gedrückt wird
- **THEN** reagiert der Motor nicht

#### Scenario: Topic wechseln
- **WHEN** am Motor die Karte `halle/motor1` gegen `halle/motor2` getauscht wird und der Taster auf `halle/motor1` publiziert
- **THEN** reagiert der Motor nicht

### Requirement: Taster publiziert Zustandswechsel
Der Taster SHALL `gedrückt` publizieren, wenn seine Knopf-Karte verdeckt wird, und
`losgelassen`, wenn sie wieder sichtbar wird. Jeder Wechsel erzeugt genau eine
Nachricht; kurzes Flackern der Erkennung (unter 200 ms) erzeugt keine Nachricht.

#### Scenario: Drücken und Loslassen
- **WHEN** eine Hand die Knopf-Karte 2 s lang verdeckt und dann wegzieht
- **THEN** werden nacheinander genau `gedrückt` und `losgelassen` publiziert

#### Scenario: Flackern
- **WHEN** die Knopf-Karte für weniger als 200 ms nicht erkannt wird
- **THEN** wird keine Nachricht publiziert

#### Scenario: Taster ohne bisher gesehene Knopf-Karte
- **WHEN** der Taster hingelegt wird, seine Knopf-Karte aber noch nie erkannt wurde
- **THEN** publiziert er nichts und zeigt den Hinweis, dass die Knopf-Karte fehlt

### Requirement: Broker stellt an alle passenden Abonnenten zu
Liegt das Broker-Blatt auf dem Tisch, SHALL jede publizierte Nachricht genau einmal an
jedes Blatt zugestellt werden, dessen abonniertes Topic passt. Ein Topic passt, wenn es
gleich ist oder das Abo auf `/#` endet und das Topic mit dem Teil davor beginnt; `#`
allein passt auf alles.

#### Scenario: Fan-out
- **WHEN** Motor (`halle/motor1`) und DB (`halle/#`) liegen und der Taster auf `halle/motor1` `gedrückt` publiziert
- **THEN** erhalten Motor und DB je genau einmal `gedrückt`

#### Scenario: Wildcard
- **WHEN** ein zweiter Taster auf `halle/motor2` publiziert
- **THEN** erhält die DB (`halle/#`) die Nachricht, der Motor (`halle/motor1`) nicht

#### Scenario: Wiederholte gleiche Nachricht
- **WHEN** zweimal hintereinander dieselbe Nachricht auf demselben Topic publiziert wird
- **THEN** wird sie jedem Abonnenten zweimal zugestellt

### Requirement: Ohne Broker keine Zustellung
Liegt kein Broker-Blatt auf dem Tisch, SHALL keine Nachricht zugestellt oder gespeichert
werden; der Taster SHALL anzeigen, dass kein Broker erreichbar ist.

#### Scenario: Broker abgedeckt
- **WHEN** das Broker-Blatt entfernt ist und der Taster gedrückt wird
- **THEN** reagieren weder Motor noch DB und am Taster erscheint „kein Broker“

#### Scenario: Broker zurück
- **WHEN** das Broker-Blatt wieder hingelegt wird und der Taster danach gedrückt wird
- **THEN** werden Nachrichten wieder normal zugestellt

### Requirement: Retained Messages
Liegt die Retain-Karte rechts neben dem Taster, SHALL dessen Nachricht als retained
publiziert werden: Der Broker speichert pro Topic die letzte retained Nachricht und SHALL
sie jedem Blatt sofort zustellen, das ein passendes Topic neu abonniert. Zugestellte
gespeicherte Nachrichten sind als retained gekennzeichnet.

#### Scenario: Neuer Abonnent mit Retain
- **WHEN** der Taster mit Retain-Karte `gedrückt` publiziert hat und danach ein Motor-Blatt mit Karte `halle/motor1` hingelegt wird
- **THEN** dreht dieser Motor sofort, und die DB-Zeile bzw. Anzeige trägt die Kennzeichnung „R“

#### Scenario: Neuer Abonnent ohne Retain
- **WHEN** der Taster ohne Retain-Karte `gedrückt` publiziert hat und danach ein Motor-Blatt hingelegt wird
- **THEN** steht dieser Motor, bis die nächste Nachricht kommt

#### Scenario: Bestehender Abonnent erhält Retained Message einmal
- **WHEN** ein Motor bereits abonniert hat und der Taster mit Retain-Karte publiziert
- **THEN** erhält der Motor die Nachricht genau einmal, ohne Kennzeichnung „R“

### Requirement: Broker zeigt Topic-Tabelle
Das Broker-Blatt SHALL pro Topic die zuletzt publizierte Nachricht anzeigen und Topics
mit gespeicherter Retained Message mit „R“ kennzeichnen.

#### Scenario: Anzeige
- **WHEN** auf `halle/motor1` mit Retain `gedrückt` publiziert wurde
- **THEN** zeigt das Broker-Blatt die Zeile `halle/motor1  gedrückt  R`

### Requirement: Motor reagiert auf Nachrichten
Das Motor-Blatt SHALL bei empfangenem `gedrückt` ein projiziertes Zahnrad drehen und bei
`losgelassen` anhalten sowie die zuletzt empfangene Nachricht anzeigen. Andere Payloads
ändern den Zustand nicht.

#### Scenario: Motor an und aus
- **WHEN** der Motor `gedrückt` und danach `losgelassen` empfängt
- **THEN** dreht sich das Zahnrad zuerst und steht danach still

### Requirement: DB protokolliert jede Nachricht
Das DB-Blatt SHALL jede empfangene Nachricht mit Uhrzeit, Topic, Payload und
Retained-Kennzeichen protokollieren und die letzten 8 Einträge, neueste oben, anzeigen.
Das Protokoll lebt nur im Speicher von Folk.

#### Scenario: Protokoll
- **WHEN** der Taster gedrückt und losgelassen wird
- **THEN** zeigt die DB zwei neue Zeilen mit Uhrzeit, `halle/motor1`, `gedrückt` bzw. `losgelassen`

#### Scenario: Entkopplung
- **WHEN** das DB-Blatt entfernt ist und der Taster gedrückt wird
- **THEN** dreht der Motor trotzdem, und die DB enthält die Nachricht nicht

### Requirement: Nachrichtenfluss sichtbar
Folk SHALL zwischen dem Broker und jedem Client mit Topic-Karte eine Linie projizieren
und für jede Nachricht ein Paket zeigen, das in etwa 1 s vom Publisher zum Broker und
anschließend vom Broker zu jedem Empfänger wandert.

#### Scenario: Paket bei Fan-out
- **WHEN** der Taster `gedrückt` an Motor und DB publiziert
- **THEN** wandert ein Paket zum Broker und danach je ein Paket zu Motor und DB

#### Scenario: Kein Empfänger
- **WHEN** eine Nachricht auf ein Topic ohne Abonnenten publiziert wird
- **THEN** wandert nur das Paket vom Taster zum Broker
