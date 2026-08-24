# Vorsorge-Ordner – Proxmox LXC One-Liner-App

Selbst gehosteter **digitaler Vorsorge-Ordner**: ein 8-Schritte-Wizard (Vertrauenspersonen → Vollmachten &
Verfügungen → Hausarzt & Medizin → Testament & Urkunden → Bank & digitaler Nachlass → Bestattung/Organspende/
Haustiere → Ordner-Inhalt → Checkliste & Export), der am Ende einen **kompletten, druckfertigen Ordner mit
21 Registern** erzeugt – als **PDF** *und* als **Word (.docx)**.

Angelehnt an die Web-App unter https://www.lichtvalleyapps.de/vorsorge.

---

## ⚡ Installation (Einzeiler auf dem Proxmox-Host)

```bash
bash -c "$(wget -qLO - https://raw.githubusercontent.com/HatchetMan111/VorsorgeOrdner/main/install/vorsorgeordner.sh)"
```

Das Script (Community-Scripts-Stil):

1. prüft root + Proxmox VE,
2. erstellt einen **unprivilegierten Debian-12-LXC** (Standard: CTID automatisch, 1 vCPU, 1024 MB RAM,
   4 GB Disk, DHCP an `vmbr0`, `onboot: 1`, nesting für pip/venv),
3. klont dieses Repo in den Container, legt ein Python-venv an,
4. registriert den **systemd-Service** `vorsorgeordner` (`Restart=always`, `After=network-online.target`),
5. **verifiziert** selbst: `systemctl is-active` + HTTP-Check auf `/api/health`,
6. gibt die finale URL aus.

Erwartete Ausgabe am Ende:

```
═══════════════════════════════════════════════════════════
  Vorsorge-Ordner erfolgreich installiert!
═══════════════════════════════════════════════════════════
  Web UI      : http://192.168.x.x:8080
  Container   : CTID 100 (Hostname: vorsorgeordner)
  Service     : systemctl status vorsorgeordner   # innerhalb des CT
  Logs        : pct exec 100 -- journalctl -u vorsorgeordner -f
  Update      : dieses Script einfach erneut ausführen
  Entfernen   : pct stop 100 && pct destroy 100
  Install-Log : /tmp/vorsorgeordner-install-<timestamp>.log
═══════════════════════════════════════════════════════════
```

## 🔧 Konfiguration per Umgebungsvariable (optional)

| Variable   | Default                                        | Bedeutung                     |
|------------|------------------------------------------------|-------------------------------|
| `CTID`     | nächste freie ID                               | Container-ID                  |
| `PORT`     | `8080`                                         | Web-UI-Port                   |
| `CORES`    | `1`                                            | vCPUs                         |
| `MEM_MB`   | `1024`                                         | RAM                           |
| `DISK_GB`  | `4`                                            | Root-Disk                     |
| `STORAGE`  | `local`                                        | PVE-Storage                   |
| `BRIDGE`   | `vmbr0`                                        | Netzwerkbrücke                |
| `VLAN_TAG` | leer                                           | VLAN-Tag                      |
| `VERBOSE`  | `0`                                            | `1` = volle Live-Ausgabe      |
| `REPO_URL` / `BRANCH` | siehe oben / `main`                 | Code-Quelle                   |

Beispiel: `CTID=150 PORT=9000 VERBOSE=1 bash -c "$(wget -qLO - …)"`

## 🔄 Update

Einfach **denselben Einzeiler erneut ausführen** – bei existierender CT wird gefragt, ob aktualisiert werden
soll (git fetch/reset, `pip install -r requirements.txt`, Service-Restart). Idempotent.

## 🗑 Deinstallation

```bash
pct stop <CTID> && pct destroy <CTID>       # Container samt App löschen
rm /tmp/vorsorgeordner-*                    # evtl. Logs aufräumen
```

## 🐞 Debugging

Bei Fehlern gibt das Script automatisch die **vollständige Fehlerkette** aus (Exit-Code, Zeile, Befehl,
letzte 50 Log-Zeilen). Für einen kompletten Trace:

```bash
wget -qO /tmp/vo.sh https://raw.githubusercontent.com/HatchetMan111/VorsorgeOrdner/main/install/vorsorgeordner.sh
bash -x /tmp/vo.sh 2>&1 | tee /tmp/vorsorgeordner-debug.log
```

Service-Probleme direkt im Container prüfen:

```bash
pct exec <CTID> -- systemctl status vorsorgeordner --no-pager -l
pct exec <CTID> -- journalctl -u vorsorgeordner -n 100 --no-pager
```

## ✅ Verifikation nach Installation (Reboot-sicher)

```bash
pct reboot <CTID>
sleep 10
pct exec <CTID> -- systemctl is-active vorsorgeordner          # -> active
pct exec <CTID> -- curl -fsS http://127.0.0.1:8080/api/health  # -> {"status":"ok",...}
```

Danach Web UI wieder erreichbar unter `http://<LXC-IP>:8080`.

## 🏗 Architektur

| Komponente | Technologie |
|---|---|
| Backend | Python 3.11+ · FastAPI · Uvicorn (`0.0.0.0:8080`) |
| PDF-Export | ReportLab (Deckblatt, Registerschilder, Einhefte-Kästen, Notfallkarte) |
| DOC-Export | python-docx |
| Frontend | Vanilla HTML/CSS/JS, keine CDNs, Wizard mit Autosave |
| Datenspeicher | **Nur `localStorage` des Browsers** – der Server speichert nichts |

**Datenschutz:** Die persönlichen Angaben verlassen dein Gerät nie Richtung Server-Speicher; sie werden nur im
Browser (localStorage) gehalten und ausschließlich für den Export als JSON an die lokale API geschickt.
Trotzdem: niemals echte Passwörter eintragen – dafür sind Leerlinien zum handschriftlichen Ergänzen vorgesehen.

## ⚖️ Rechtlicher Hinweis

Dieser Ordner ist eine **Organisationshilfe und ersetzt keine Rechtsberatung**. Für die rechtliche Wirksamkeit
einzelner Dokumente (insbesondere Testament § 2247 BGB, Patientenverfügung § 1901a BGB, Erbvertrag § 2276 BGB)
gelten gesetzliche Formvorschriften – die letzte PDF-Seite fasst diese zusammen. Bei Unsicherheiten Notar,
Anwalt oder Hausarzt konsultieren.
