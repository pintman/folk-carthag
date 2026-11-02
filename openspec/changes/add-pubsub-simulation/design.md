# Design

## Context

- Motivation und Umfang: siehe proposal.md; Verhalten: specs/pubsub-simulation/spec.md.
- Folk auf carthag (Jim Tcl) bietet neben Claims auch **Events**: `Notify: …` löst alle
  aktuell existierenden `Subscribe: … { body }` aus (`prelude.tcl:621`, genutzt z. B. von
  `keyboard.folk` für Tastenereignisse). Ein `Subscribe:` existiert nur, solange das Blatt
  liegt, das es äußert.
- `When /nobody/ claims …` matcht, wenn ein Statement fehlt (z. B. `points-at.folk:108`).
- `programs.folk` claimt `tag <id> is a tag` mit `-keep 100ms` – kurze Aussetzer der
  Erkennung werden bereits geglättet.
- `Hold! -key …` hält Zustand über Re-Evaluationen hinweg; `When $this points left at /p/`
  liefert Nachbarblätter; `user-programs/carthag/connections.folk` zeichnet Linien.
- Gedruckte Programme werden im Web-Editor (`:4273/new`) erstellt und gedruckt; Tag-IDs
  vergibt Folk beim Druck.

## Goals / Non-Goals

**Goals:**
- Jedes gedruckte Blatt hat höchstens ca. 25 Zeilen gut lesbaren Code, deutsche
  Bezeichner/Kommentare – der Code ist Unterrichtsmaterial.
- Event- und Claim-Namen orientieren sich an MQTT-Begriffen, damit ein späteres
  Bridge-Blatt (aus `add-mqtt-bridge`) den Simulations-Broker ersetzen kann.
- Gemeinsame Technik (Paket-Animation, Linien) liegt im Hintergrundprogramm, nicht auf
  den Blättern.

**Non-Goals:**
- Exakte MQTT-Semantik jenseits der Spec (Sessions, QoS, Clean Start, Löschen von
  Retained Messages per leerer Payload).

## Decisions

1. **Nachrichten sind Events, Zustand sind Holds.**
   - Publizieren: `Notify: publish <m> on topic <t> from <client> retain <0|1>`
   - Zustellen: `Notify: <client> receives <m> on topic <t> retained <0|1>`
   - Abonnieren: Client claimt `<client> subscribes to <muster>`; Publisher claimt
     `<client> publishes on <topic>`.
   Events machen wiederholte gleiche Nachrichten sichtbar (Spec „Wiederholte gleiche
   Nachricht“) – mit reinen Claims würde `gedrückt, gedrückt` zu einem Statement verschmelzen.
   *Alternative:* Claims mit Zähler/Zeitstempel – mehr Code auf jedem Blatt.

2. **Broker = `Subscribe: publish …` auf dem Broker-Blatt.** Da das `Subscribe:` nur
   existiert, solange das Broker-Blatt liegt, gilt „ohne Broker keine Zustellung“ ohne
   Zusatzcode. Im Body: `Query!` aller `/c/ subscribes to /muster/`, Musterprüfung per
   kleiner `fn passt {muster topic}` (gleich, `#`, oder Präfix vor `/#`), `Notify:` pro
   Treffer. Außerdem `Hold! -key [list letzte $t]` für die Topic-Tabelle.
   Der Broker claimt `$this is the broker`; der Taster prüft das per `Query!` und zeigt
   sonst „kein Broker“ (Footnote).

3. **Retained über einen `When`-Match mit Zeitstempel.** Bei `retain 1` hält der Broker
   `Hold! -key [list retained $t] Claim retained <m> on topic <t> at <ms>` und stellt
   *nicht* direkt zu. Stattdessen:
   `When /c/ subscribes to /muster/ & retained /m/ on topic /t/ at /ts/ { if passt … }`
   Dieser Body läuft einmal pro neuem Match – also sowohl bei neuer Retained Message
   (für alle bestehenden Abonnenten) als auch bei neuem Abonnenten (für alle gespeicherten
   Topics). Unterscheidung über das Alter: `ts` jünger als 300 ms ⇒ frisch publiziert ⇒
   `retained 0`; sonst neuer Abonnent ⇒ `retained 1`. Der neue Zeitstempel sorgt dafür,
   dass auch identische Retained Messages erneut zugestellt werden.
   *Alternative:* direkt zustellen + `When` nur für Spätabonnenten – braucht Buchführung,
   wer schon beliefert wurde (doppelte Zustellung sonst).

4. **Taster: Knopf-Tag-ID fest im Code, Erkennung per Negation.**
   `set knopf 45xxx`. `When tag $knopf is a tag { … }` ⇒ `losgelassen`,
   `When /nobody/ claims tag $knopf is a tag { … }` ⇒ `gedrückt`. Entprellung: Der
   Wechsel wird erst publiziert, wenn der neue Zustand 200 ms stabil ist (Zeitstempel im
   Hold, Prüfung über `When the clock time is /now/`), zusätzlich zu den 100 ms `-keep` aus
   `programs.folk`. Ein Hold `knopf gesehen` verhindert `gedrückt` beim ersten Hinlegen
   ohne Knopf-Karte. Topic: `When $this points left at /k/ & /k/ is topic /t/`; Retain:
   `points right at /r/ & /r/ is the retain card`, abgefragt per `Query!` beim Publizieren.
   *Alternative:* Knopf-Karte über „zuletzt gezeigt“ merken – flexibler, schwerer lesbar.

5. **Topic- und Retain-Karten sind einzeilige Blätter**:
   `Claim $this is topic "halle/motor1"` bzw. `Claim $this is the retain card`, plus
   Beschriftung. Die Karte liegt links (Topic) bzw. rechts (Retain) vom Client; der Client
   zeigt darauf.

6. **Motor**: `Subscribe: $this receives /m/ on topic /t/ retained /r/` setzt
   `Hold! läuft 0|1` und Anzeige; Zahnrad als `draws a shape with sides 10 … radians`
   mit Winkel aus der Uhrzeit, wenn `läuft`.

7. **DB**: dasselbe `Subscribe:`; Liste der letzten 8 Zeilen wird mit `Query!` des alten
   Holds gelesen, vorn ergänzt, gekürzt und neu gehalten; Anzeige per `draws text`.

8. **Hintergrundprogramm `user-programs/carthag/pubsub-pakete.folk`:**
   - Linien: für jedes `/c/ subscribes to …` bzw. `/c/ publishes on …` und den Broker
     `Wish $c is connected to $broker` (connections.folk), grau.
   - Pakete: `Subscribe: publish … from /c/ …` ⇒ Paket Client→Broker;
     `Subscribe: /c/ receives …` ⇒ Paket Broker→Client, startet nach 1 s (wartet das
     erste Paket ab). Paket = Hold mit Startzeit, gezeichnet als Kreis, Position linear
     zwischen den Quad-Mittelpunkten interpoliert (`When the clock time is /t/`), nach
     Ablauf entfernt. Hört auf dieselben Events, die Blätter brauchen davon nichts zu wissen.
   *Alternative:* `is dynamically connected` – wandert dauerhaft, zeigt keine einzelnen
   Nachrichten.

9. **Quellen im Repo unter `beispiele/pubsub/`.** Die Blätter werden aus diesen Dateien in
   den Web-Editor kopiert und gedruckt; `folk-data/program/` bleibt die Sicherung der
   gedruckten Stände. README dort mit Aufbauskizze und Experimenten.

## Risks / Trade-offs

- [Hand verdeckt beim Drücken andere Blätter oder Topic-Karten] → Aufbau-Skizze im README
  mit Knopf-Karte außen; Knopf-Karte etwas abseits legen.
- [Erkennung flackert stärker als 200 ms bei schlechtem Licht] → Entprell-Zeit als
  Variable oben im Taster-Code.
- [Re-Evaluation eines Blatts (z. B. Taster neu erkannt) führt `When`-Bodies erneut aus und
  publiziert erneut] → erwartetes Folk-Verhalten; im README als „echte Taster prellen auch“
  thematisieren.
- [300-ms-Fenster bei Retained ist eine Heuristik; bei Folk-Hängern kann ein bestehender
  Abonnent `R` sehen] → akzeptiert für Simulation; im README erwähnen.
- [Paket-Bibliothek setzt Folk-Interna (Quad-Library wie connections.folk) voraus] →
  dieselben Statements wie das funktionierende `connections.folk` verwenden.
- [`Query!` innerhalb `Subscribe:`-Body sieht evtl. nicht den allerneusten Stand] → in Task
  2.x verifizieren; notfalls Abonnenten-Liste per `When` in einen Hold spiegeln.

## Migration Plan

1. `pubsub-pakete.folk` nach `/home/folk/folk/user-programs/carthag/` kopieren.
2. Blätter in Reihenfolge Topic-/Retain-Karten, Knopf, Taster (Knopf-ID eintragen),
   Broker, Motor, DB im Web-Editor anlegen und drucken.
3. Rollback: Hintergrundprogramm entfernen, Blätter vom Tisch nehmen.
