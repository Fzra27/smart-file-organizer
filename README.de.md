# Derli — Intelligente Dateiverwaltung

Lokale Dateiverwaltung mit türkischer und deutscher Oberfläche. Keine zusätzlichen Python-Pakete und keine Internetverbindung erforderlich.

## Ubuntu / Linux starten

Benötigt Python **3.10 oder neuer**. Entpacke das Archiv, öffne ein Terminal im Programmordner und starte:

```sh
sh Baslat.sh
```

Falls Python fehlt: `sudo apt install python3`. Starte das Programm anschließend **ohne sudo**.

Der Browser öffnet sich unter `http://127.0.0.1:8765`. Falls er sich nicht automatisch öffnet, rufe diese Adresse manuell auf. Beenden: **Strg+C** im Terminal. Das Schließen des Browserfensters beendet den Server nicht.

```sh
sh Baslat.sh --folder "/home/name/Downloads"
sh Baslat.sh --port 8766
sh Baslat.sh --no-browser
```

Rechts oben unter **Dil / Sprache** die Option **Deutsch** wählen. Die Auswahl wird im Browser für diese lokale Adresse gespeichert. Der Download-Ordner wird anhand der Linux-Einstellung `XDG_DOWNLOAD_DIR` vorgeschlagen.

## Funktionen

- Dateien im Hauptordner nach Typ sortieren, immer mit manueller Vorschau oder optional automatisch alle 15 Sekunden bei laufendem Programm.
- Duplikate anhand des vollständigen SHA-256-Inhalts erkennen. Die älteste Kopie bleibt erhalten.
- Ordnergröße, größte Dateien und freien Festplattenspeicher anzeigen.
- Verschiebungen im Verlauf rückgängig machen, ohne vorhandene Dateien zu überschreiben.

**Quarantäne gibt noch keinen Speicher frei.** Duplikate werden in `.akilli-duzenleyici/karantina` verschoben. Lösche diesen Ordner erst selbst, nachdem du die Dateien geprüft hast. Danach können diese Dateien nicht mehr über die Anwendung wiederhergestellt werden. Verlaufseinträge liegen in `.akilli-duzenleyici/history`.

Dateinamen und Pfade bleiben unverändert. Die Zielordner heißen auch bei deutscher Oberfläche `Belgeler` (Dokumente), `Görseller` (Bilder), `Videolar` (Videos) usw. Ein Sprachwechsel verschiebt keine Dateien.

Versteckte Dateien, symbolische Verknüpfungen und temporäre Downloads werden übersprungen. Dateien mit Änderungen in den letzten 10 Sekunden werden nicht einsortiert. Für Verschiebungen ist Hardlink-Unterstützung auf demselben Dateisystem erforderlich, wie sie etwa ext4 bietet. Externe Dateisystemgrenzen werden nicht überschritten.

## Prüfung

11 automatische Tests unter Ubuntu 24.04 / Python 3.12 in einem Container mit einem Benutzer ohne Administratorrechte; Linux-Startskript und lokaler HTTP-Server eingeschlossen. Sprachwechsel, gespeicherte Sprachauswahl, deutsche Vorschauen, Verlauf, Fehlermeldungen, Dateioperationen und mobiles Layout wurden zusätzlich mit Chromium unter Debian geprüft. Das automatische Öffnen eines Ubuntu-Desktop-Browsers wurde nicht direkt getestet.

```sh
python3 -m unittest -v
```
