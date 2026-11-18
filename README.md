# Essensplaner (PWA)

Wochenplaner für Mittagessen: 58 Rezepte, automatischer Wochenplan, Einkaufsliste nach Kategorien,
Budgetkontrolle, Favoriten/Bewertungen, eigene Rezepte. Läuft komplett offline, ohne Server-Code,
ohne KI- oder Preis-Schnittstellen.

## Lokal starten (zum Ausprobieren)
    python3 -m http.server 8765        # im Ordner dieser Datei
    # dann http://localhost:8765/ im Browser öffnen

Die Dateien müssen über http(s) ausgeliefert werden (nicht per Doppelklick), sonst sind
Service Worker und Installation nicht möglich.

## Auf dem iPhone installieren
Eine PWA braucht eine öffentliche HTTPS-Adresse. Den ganzen Ordner auf einen statischen Hoster legen
(z. B. GitHub Pages, Netlify oder Cloudflare Pages), dann auf dem iPhone:
1. Die Adresse in **Safari** öffnen.
2. Unten auf **Teilen** (Quadrat mit Pfeil) tippen.
3. **„Zum Home-Bildschirm“** wählen, Namen bestätigen, **Hinzufügen**.
4. Die App über das neue Symbol starten – sie öffnet ohne Browserleisten.
5. Einmal online öffnen, danach funktioniert alles auch offline.

## Tests
    node tests/engine.test.js                       # Budget, Einkaufsliste, Ausschlüsse, Planregeln
    python3 tests/ui.test.py http://localhost:8765/ # Browser-Test inkl. Offline (Playwright)

## Aufbau
    index.html, manifest.webmanifest, sw.js   PWA-Grundlage
    js/data.js      Zutatenkatalog (Preis-Schätzwerte) und Rezepte
    js/engine.js    Planer, Kosten, Einkaufsliste, Tausch, Optimierung
    js/store.js     Speicherung (IndexedDB)
    js/sync.js      optionale Synchronisierung mit eigenem Speicher
    js/app.js       Oberfläche;  css/style.css  Design
