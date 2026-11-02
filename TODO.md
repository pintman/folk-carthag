# TODO

## MQTT-Anbindung

Quelle: <https://folk.computer/notes/mqtt> (Jacob Haip, April 2024)

Ziel: WLAN-Mikrocontroller (Pico W, MatrixPortal …), Handys und Webseiten
als Sensoren/Aktoren über MQTT an Folk anbinden.

- [ ] Mosquitto auf carthag installieren (`apt install mosquitto mosquitto-clients`),
      Dienst aktivieren, Port 1883; Test mit `mosquitto_sub`/`mosquitto_pub`
- [ ] Bridge `user-programs/carthag/mqtt.folk`: Wish zum Publizieren,
      Claims für eingehende Nachrichten
- [ ] Prüfen: Artikel nutzt Tcl-MQTT-Bibliothek (Tcl 8.6). Aktuelles Folk läuft
      auf Jim Tcl → evtl. stattdessen `mosquitto_sub`/`mosquitto_pub` als
      Unix-Prozess oder libmosquitto per C-FFI
- [ ] Optional: Websocket-Listener in Mosquitto für MQTT.js-Webseiten
- [ ] Beispiel: Button am Pico W (MicroPython) → Label auf Blatt
