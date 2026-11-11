# AION 2 Discord Patchnotes-Bot

Prüft alle 30 Minuten den offiziellen AION-2-Ankündigungsfeed auf Steam. Nur Titel mit „Patch Notes“ oder „Hotfix“ (inkl. einiger Schreibvarianten) werden verarbeitet. Der Text wird über einen **inoffiziellen** Google-Translate-Zugriff (`deep-translator`) ins Deutsche übersetzt und in Discord-Nachrichten aufgeteilt.

## Einrichtung

1. Auf GitHub ein **neues Repository** erstellen (für kostenlose GitHub-Actions-Minuten am einfachsten **Public**). **Keine Webhook-URL in Dateien eintragen.**
2. Alle Dateien **einschließlich `.github/workflows/aion2.yml`** in das Repository hochladen. GitHub erlaubt Ordnerstruktur auch über die Weboberfläche, alternativ ZIP lokal entpacken und mit GitHub Desktop hochladen.
3. In Discord: **Servereinstellungen → Integrationen → Webhooks → Neuer Webhook**. Zielkanal auswählen, Webhook-URL kopieren.
4. GitHub: **Settings → Secrets and variables → Actions → New repository secret**. Name: `DISCORD_WEBHOOK_URL`; Wert: kopierte Webhook-URL.
5. GitHub: **Settings → Actions → General → Workflow permissions**: **Read and write permissions** wählen, falls verfügbar. (Workflow hat außerdem `contents: write`.)
6. GitHub: **Actions → AION 2 Patch Notes → Run workflow**. Beim ersten Lauf wird `seen.json` angelegt und **es werden keine alten Nachrichten versendet**.
7. Beim nächsten neuen Patchnote- oder Hotfix-Eintrag postet der Bot automatisch. Optional: Test mit einem neuen Eintrag oder `seen.json` gezielt ändern (Vorsicht: erneute Posts).

## Hinweise

- Keine Kosten für Code oder Übersetzungs-API eingeplant; GitHub Actions ist bei öffentlichen Repositories in der Regel kostenlos. Die inoffizielle Übersetzung kann durch Änderungen am Drittanbieter ausfallen oder gedrosselt werden. Dann werden Einträge später erneut versucht, nicht auf Englisch veröffentlicht.
- GitHub kann geplante Jobs verzögert ausführen; in **öffentlichen** Repositories werden Schedules nach **60 Tagen ohne Repository-Aktivität** deaktiviert.
- Der Bot kann nur Beiträge erkennen, die in Steams Ankündigungsfeed auftauchen und im Titel die Filterwörter tragen.
- `seen.json` speichert bereits bearbeitete IDs. Ein Neustart ohne diese Datei initialisiert nur den aktuellen Feed, statt alte Beiträge zu versenden.
- GitHub-Webhooks sind geheim: niemals öffentlich posten.
- Discord begrenzt Nachrichten auf 2000 Zeichen; der Bot teilt längere Patch Notes auf.
