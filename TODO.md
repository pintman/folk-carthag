# TODO

## MQTT-Anbindung

Quelle: <https://folk.computer/notes/mqtt> (Jacob Haip, April 2024)

Ziel: WLAN-Mikrocontroller (Pico W, MatrixPortal …), Handys und Webseiten
als Sensoren/Aktoren über MQTT an Folk anbinden.

- [ ] Mosquitto auf carthag installieren (`apt install mosquitto mosquitto-clients`),
      Dienst aktivieren, Port 1883; Test mit `mosquitto_sub`/`mosquitto_pub`
- [ ] Bridge `user-programs/carthag/mqtt.folk`: Wish zum Publizieren,
      Claims für eingehende Nachrichten
- [ ] Umsetzung über `mosquitto_sub`/`mosquitto_pub` als Unix-Prozess
      (Artikel nutzt Tcl-MQTT-Bibliothek für Tcl 8.6 mit TclOO/Coroutinen –
      läuft nicht unter Jim Tcl):
  - Empfangen: `mosquitto_sub -v -t '#'` dauerhaft starten, Ausgabe
    zeilenweise (`topic payload`) lesen → `Claim mqtt topic /t/ has message /m/`
  - Senden: `Wish mqtt publishes /m/ on topic /t/` → `mosquitto_pub -t $t -m $m`
  - Vorhandenes `Wish $this runs Unix command …` nutzen oder eigenes
    `open "|mosquitto_sub …"` mit `$f readable`
  - Später ggf. libmosquitto per C-FFI, falls Performance nötig
- [ ] Optional: Websocket-Listener in Mosquitto für MQTT.js-Webseiten
- [ ] Beispiel: Button am Pico W (MicroPython) → Label auf Blatt

## Sprite-Bug in Folk (`builtin-programs/sprites.folk`)

`Wish $this draws sprite … with frames N columns C` berechnet die Zeile
falsch: `y = (frameNumber % rows) * spriteHeight` statt
`(frameNumber / columns) * spriteHeight`. Bei mehrzeiligen Spritesheets
springt die Animation (z. B. 8 Frames/4 Spalten: Frame 1 zeigt Kachel 5).

- [ ] Patch in `folk-patches/` anlegen:
      `set y [expr {($frameNumber / $columns) * $spriteHeight}]`
- [ ] Testen mit mehrzeiligem Sheet (z. B. 8 Frames, 4 Spalten)
- [ ] Optional upstream melden
- Workaround bis dahin: einzeilige Spritesheets (`columns` = `frames`)
- Hinweis: `frames` muss durch `columns` teilbar sein (Ganzzahldivision)
