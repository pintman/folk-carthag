# Spec Delta

## Purpose

Bindet externe Geräte (Mikrocontroller, Handys, Webseiten) über MQTT an Folk auf
carthag an: eingehende Nachrichten werden zu Statements, Folk-Programme können
Nachrichten senden.

## ADDED Requirements

### Requirement: Broker im LAN erreichbar
carthag SHALL einen MQTT-Broker auf TCP-Port 1883 betreiben, der aus dem lokalen Netz
ohne Anmeldung erreichbar ist und nach einem Neustart von carthag automatisch startet.

#### Scenario: Gerät im LAN verbindet sich
- **WHEN** ein Client im LAN sich ohne Zugangsdaten mit `carthag.local:1883` verbindet
- **THEN** wird die Verbindung angenommen und der Client kann publizieren und abonnieren

#### Scenario: Neustart von carthag
- **WHEN** carthag neu gestartet wurde
- **THEN** ist der Broker ohne manuellen Eingriff wieder auf Port 1883 erreichbar

### Requirement: Eingehende Nachrichten als Claim
Für jede Nachricht auf einem beliebigen Topic (außer `$SYS/…`) SHALL Folk den Claim
`mqtt topic <topic> has message <payload>` bereitstellen. Pro Topic gilt nur die zuletzt
empfangene Nachricht; eine neue Nachricht ersetzt den vorherigen Claim desselben Topics.

#### Scenario: Nachricht empfangen
- **WHEN** ein Client `42` auf Topic `sensor/temp` publiziert
- **THEN** existiert in Folk der Claim `mqtt topic sensor/temp has message 42`

#### Scenario: Neuere Nachricht ersetzt ältere
- **WHEN** auf `sensor/temp` erst `42`, dann `43` publiziert wird
- **THEN** existiert nur noch `mqtt topic sensor/temp has message 43`

#### Scenario: Unterschiedliche Topics bleiben nebeneinander
- **WHEN** auf `a` die Nachricht `1` und auf `b` die Nachricht `2` publiziert wird
- **THEN** existieren beide Claims gleichzeitig

#### Scenario: Payload mit Leerzeichen
- **WHEN** auf `display/text` die Nachricht `Hallo Welt` publiziert wird
- **THEN** ist die Message im Claim der vollständige String `Hallo Welt`

### Requirement: Nachrichten aus Folk senden
Ein Folk-Programm SHALL über `Wish mqtt publishes <message> on topic <topic>` eine
Nachricht an den Broker senden können. Gesendet wird einmal, sobald der Wish entsteht
bzw. sich Topic oder Message ändern.

#### Scenario: Blatt sendet Nachricht
- **WHEN** ein Blatt `Wish mqtt publishes on on topic led/1` äußert
- **THEN** erhält ein Abonnent von `led/1` genau einmal die Nachricht `on`

#### Scenario: Nachricht ändert sich
- **WHEN** der Wish von Message `on` auf `off` wechselt
- **THEN** erhält ein Abonnent von `led/1` zusätzlich die Nachricht `off`

#### Scenario: Eigene Nachricht wird auch empfangen
- **WHEN** Folk `Wish mqtt publishes 5 on topic test/x` äußert
- **THEN** existiert danach auch der Claim `mqtt topic test/x has message 5`

### Requirement: Robustheit gegenüber Broker-Ausfall
Die Bridge SHALL einen Ausfall oder Neustart des Brokers ohne Neustart von Folk
überstehen und den Empfang danach selbstständig wieder aufnehmen. Fehler beim Senden
DÜRFEN Folk NICHT blockieren oder abstürzen lassen.

#### Scenario: Broker wird neu gestartet
- **WHEN** der Broker-Dienst neu gestartet wird und danach eine Nachricht eintrifft
- **THEN** erscheint diese Nachricht nach wenigen Sekunden als Claim in Folk

#### Scenario: Broker nicht erreichbar beim Senden
- **WHEN** ein Blatt eine Nachricht sendet, während der Broker gestoppt ist
- **THEN** läuft Folk normal weiter und der Fehler wird im Folk-Log ausgegeben
