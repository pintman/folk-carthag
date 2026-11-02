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
