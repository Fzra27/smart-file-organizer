# Derli — Intelligente Dateiverwaltung

Lokale Dateiverwaltung mit türkischer und deutscher Oberfläche. Die Oberfläche startet standardmäßig als eigenes GTK/WebKit-Fenster mit dunklem Design. Für die einmalige Einrichtung werden Ubuntu-Systempakete benötigt; anschließend läuft die Anwendung lokal.

## Ubuntu / Linux starten

Benötigt Python **3.10 oder neuer**. Entpacke das Archiv, öffne ein Terminal im Programmordner und starte:

```sh
sh Kur-Ubuntu.sh  # einmalig: GTK/WebKit installieren und Menüeintrag anlegen
sh Baslat.sh
```

Falls Python fehlt: `sudo apt install python3`. Starte das Programm anschließend **ohne sudo**.

Die Anwendung öffnet ein eigenes Fenster. Du kannst sie auch über **Derli** im Anwendungsmenü starten. Beim Schließen des Fensters wird der lokale Server beendet. Eine alte laufende Browser-Version zuerst mit **Strg+C** im Terminal beenden. `--no-browser` startet ausdrücklich nur den lokalen Server; `--browser` öffnet ausdrücklich einen Webbrowser.

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

Das native GTK/WebKit-Fenster wurde unter Ubuntu 24.04 mit einem Benutzer ohne Administratorrechte und virtuellem Bildschirm geöffnet: dunkler Hintergrund, Hilfetexte und Deutsch-Auswahl erfolgreich. Zusätzlich bestanden 13 automatische Prüfungen unter Debian sowie die TR/DE-Dateiabläufe in Chromium. Hardwarebeschleunigung und der Menüeintrag auf einem echten Ubuntu-Desktop wurden nicht direkt getestet.

```sh
python3 -m unittest -v
```
