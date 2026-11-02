# Tasks

## 1. Karten und Broker

- [ ] 1.1 `beispiele/pubsub/topic-karte.folk` (Vorlage `Claim $this is topic "…"` + Beschriftung) und `retain-karte.folk` anlegen, Karten `halle/motor1`, `halle/motor2`, `halle/#` und Retain drucken; prüfen: `:4273/statements` zeigt `… is topic halle/motor1` bzw. `… is the retain card`, sobald die Karte liegt
- [ ] 1.2 `beispiele/pubsub/broker.folk`: `Claim $this is the broker`, `fn passt`, `Subscribe: publish …` mit `Query!` der Abonnenten und `Notify: … receives …`, Hold `letzte` pro Topic, Topic-Tabelle per `draws text`; prüfen: Test-Blatt mit `Subscribe: $this receives /m/ …` + Karte `halle/#` und manuellem `Notify: publish x on topic halle/a from test retain 0` (Web-Editor) zeigt Empfang; Musterfälle `halle/a`/`halle/#`/`#`/`andere/a` geprüft
- [ ] 1.3 Verifizieren, dass `Query!` im `Subscribe:`-Body aktuelle Abonnenten liefert (Risiko aus design.md); prüfen: Abonnent hinlegen und sofort publizieren → wird zugestellt; sonst Abonnentenliste per `When` in Hold spiegeln
- [ ] 1.4 Retained im Broker (Hold `retained … at <ms>`, `When`-Match mit 300-ms-Regel); prüfen: Szenarien „Neuer Abonnent mit Retain“ (retained 1) und „Bestehender Abonnent erhält Retained Message einmal“ (genau ein Event, retained 0) mit dem Test-Blatt; Topic-Tabelle zeigt „R“
- [ ] 1.5 Broker-Blatt entfernen und publizieren; prüfen: Test-Blatt empfängt nichts (Spec „Broker abgedeckt“); Code ≤ ca. 25 Zeilen, sonst Hilfsfunktionen in Hintergrundprogramm verschieben

## 2. Taster

- [ ] 2.1 `beispiele/pubsub/knopf.folk` (Beschriftung „Hand drauf“) drucken, Tag-ID notieren
- [ ] 2.2 `beispiele/pubsub/taster.folk`: Knopf-ID, Topic-Karte links, Retain-Karte rechts, Negations-`When` für `gedrückt`/`losgelassen`, 200-ms-Entprellung, Hold `knopf gesehen`, `Notify: publish …`, Footnote „kein Broker“ / „Knopf-Karte fehlt“; prüfen: mit Test-Abonnent Szenarien „Drücken und Loslassen“ (genau 2 Events), „Flackern“ (Karte kurz anheben → kein Event), „Taster ohne bisher gesehene Knopf-Karte“
- [ ] 2.3 Wiederholung prüfen: zweimal kurz drücken; prüfen: Test-Abonnent zählt 4 Events (Spec „Wiederholte gleiche Nachricht“)

## 3. Motor und DB

- [ ] 3.1 `beispiele/pubsub/motor.folk`: `Subscribe:`, Hold `läuft`, Zahnrad dreht per Uhrzeit, Anzeige letzte Nachricht (+ „R“); prüfen: Szenarien „Motor an und aus“, „Abonnieren durch Hinlegen“, „Abbestellen durch Wegnehmen“, „Topic wechseln“
- [ ] 3.2 `beispiele/pubsub/db.folk`: `Subscribe:`, Liste der letzten 8 Einträge (Uhrzeit, Topic, Payload, R), neueste oben; prüfen: Szenarien „Protokoll“, „Wildcard“ (zweiter Taster auf `halle/motor2`), „Entkopplung“
- [ ] 3.3 Retained mit echten Blättern: Szenarien „Neuer Abonnent mit Retain“ / „ohne Retain“ am Tisch; prüfen: Motor dreht bzw. steht wie spezifiziert, DB-Zeile mit „R“

## 4. Visualisierung

- [ ] 4.1 `user-programs/carthag/pubsub-pakete.folk`: Linien Client↔Broker über `connections.folk`; prüfen: graue Linien zu Taster, Motor, DB, verschwinden beim Wegnehmen der Topic-Karte
- [ ] 4.2 Paket-Animation (Hold mit Startzeit, Interpolation zwischen Quad-Mitten, Broker→Empfänger startet nach 1 s); prüfen: Szenarien „Paket bei Fan-out“ und „Kein Empfänger“ am Tisch
- [ ] 4.3 `pubsub-pakete.folk` nach carthag deployen und Folk neu laden; prüfen: läuft ohne roten Fehlerrahmen, `./sync.sh` holt die Datei identisch zurück

## 5. Unterrichtsmaterial

- [ ] 5.1 `beispiele/pubsub/README.md`: Aufbau-Skizze, Druckreihenfolge (Knopf-ID eintragen), Experimente (Fan-out, Entkopplung, Topic wechseln, Wildcard, Broker weg, Retain an/aus), bekannte Grenzen (Re-Evaluation, 300-ms-Heuristik); prüfen: Aufbau nach README von Grund auf durchgespielt, alle Experimente funktionieren
- [ ] 5.2 Projekt-README: Abschnitt-Tabelle um `beispiele/` ergänzen, TODO.md um Folgeschritt „Simulations-Broker durch MQTT-Bridge ersetzen“ ergänzen; prüfen: Links/Pfade stimmen

## 6. Integration

- [ ] 6.1 Gesamtdurchlauf mit allen Blättern (2 Taster, Broker, 2 Motoren, DB) über 5 Minuten; prüfen: alle Spec-Szenarien erfüllt, keine roten Fehlerrahmen, `./sync.sh` sichert gedruckte Blätter
