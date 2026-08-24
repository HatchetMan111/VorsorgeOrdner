#!/usr/bin/env bash
# =============================================================================
#  Vorsorge-Ordner – Proxmox VE Installer (Community-Scripts-Stil)
# -----------------------------------------------------------------------------
#  Erstellt einen unprivilegierten LXC-Container (Debian 12) und installiert
#  die FastAPI-App "Vorsorge-Ordner" vollständig inkl. systemd-Service.
#
#  Einzeiler:
#    bash -c "$(wget -qLO - https://raw.githubusercontent.com/HatchetMan111/VorsorgeOrdner/main/install/vorsorgeordner.sh)"
#
#  Update bestehender Installation: dasselbe Script erneut ausführen.
#  Konfiguration: Variablen unten oder per Umgebungsvariable überschreiben,
#  z. B.: CTID=150 PORT=9000 bash -c "$(wget -qLO - ...)"
# =============================================================================

# ------------------------------- Variablen ----------------------------------
APP="vorsorgeordner"
APP_DIR="/opt/vorsorgeordner"

REPO_URL="${REPO_URL:-https://github.com/HatchetMan111/VorsorgeOrdner.git}"
BRANCH="${BRANCH:-main}"
PORT="${PORT:-8080}"

CTID="${CTID:-}"                 # leer = automatisch naechste freie ID ab 100
HN="${HN:-vorsorgeordner}"
CORES="${CORES:-1}"
MEM_MB="${MEM_MB:-1024}"
SWAP_MB="${SWAP_MB:-512}"
DISK_GB="${DISK_GB:-4}"
BRIDGE="${BRIDGE:-vmbr0}"
STORAGE="${STORAGE:-local}"
VLAN_TAG="${VLAN_TAG:-}"

VERBOSE="${VERBOSE:-0}"          # VERBOSE=1 -> volle Ausgabe statt Spinner
LOGFILE="/tmp/${APP}-install-$(date +%Y%m%d-%H%M%S).log"

# -------------------------------- Helpers -----------------------------------
set -Eeuo pipefail

BFR=$'\r'
CL='\033[0m'
GN='\033[32m'
RD='\033[01;31m'
YLW='\033[33m'
BLD='\033[1m'

msg_info() { echo -ne " ${YLW}⏳${CL} $1${BFR}"; }
msg_ok()   { echo -e "${BFR} ${GN}✔${CL} $1"; }
msg_error(){ echo -e "${BFR}${RD}✘ Fehler:${CL} $1"; }
header()   { echo -e "${BLD}${GN}
  __     __              ___                  _   _
  \\ \\   / /__ _  _ _ __ / __| ___ __ _ _ __ _| |_(_)___ _ _
   \\ \\/\\/ / _ \\|| \\ \\ / / _ \\/ -_) _\` | '  \\_  _| / _ \\ ' \\
    \\_/\\_/\\___/\\_,_/_\\_\\_\\___/\\___\\__,_|_|_|__/__/_\\___/_||_|
                     Proxmox LXC Installer${CL}\n"; }

on_error() {
  local exit_code="$1" line_no="$2"
  echo ""
  msg_error "Installation fehlgeschlagen."
  {
    echo "==============================================================="
    echo " FEHLERKETTE"
    echo "   Exit-Code : ${exit_code}"
    echo "   Zeile     : ${line_no}"
    echo "   Befehl    : ${BASH_COMMAND}"
    echo "   Log-Datei : ${LOGFILE}"
    echo "---------------------------------------------------------------"
    echo "--- Letzte 50 Log-Zeilen -------------------------------------"
    tail -n 50 "${LOGFILE}" 2>/dev/null || echo "(kein Log verfügbar)"
    echo "==============================================================="
  } | tee -a "${LOGFILE}" >&2
  echo ""
  msg_info "Debug-Tipp: Script mit vollem Trace erneut ausführen:"
  msg_ok   "  wget -qO /tmp/${APP}.sh <URL> && bash -x /tmp/${APP}.sh 2>&1 | tee /tmp/${APP}-debug.log"
  msg_info "oder: VERBOSE=1 vor den Einzeiler setzen."
  exit "$exit_code"
}

trap 'on_error $? $LINENO' ERR

STD() {
  if [[ "$VERBOSE" == "1" ]]; then
    "$@" 2>&1 | tee -a "$LOGFILE"
  else
    "$@" >>"$LOGFILE" 2>&1
  fi
}

require_root() {
  if [[ $EUID -ne 0 ]]; then
    msg_error "Bitte als root ausführen (Proxmox-Host)."
    exit 1
  fi
}

require_proxmox() {
  if ! command -v pveversion >/dev/null 2>&1; then
    msg_error "pveversion nicht gefunden – dieses Script gehört auf einen Proxmox-VE-Host."
    exit 1
  fi
}

next_ctid() {
  pvesh get /cluster/nextid 2>/dev/null || echo 100
}

ct_exists() {
  pct status "$1" >/dev/null 2>&1
}

wait_for_network() {
  local ctid="$1"
  for _ in $(seq 1 60); do
    if pct exec "$ctid" -- getent hosts deb.debian.org >/dev/null 2>&1; then
      return 0
    fi
    sleep 1
  done
  msg_error "Container hatte nach 60s kein Netzwerk (DNS/Brücke prüfen)."
  return 1
}

# ------------------------- Inner-CT Installationslogik ----------------------
INNER_SCRIPT=$(cat <<'INNER'
#!/usr/bin/env bash
set -Eeuo pipefail
export DEBIAN_FRONTEND=noninteractive
export PIP_DISABLE_PIP_VERSION_CHECK=1

APP="$1"; APP_DIR="$2"; PORT="$3"; REPO_URL="$4"; BRANCH="$5"
SRC_DIR="${APP_DIR}/opt/vorsorgeordner"
SERVICE="/etc/systemd/system/${APP}.service"

echo ":: apt-get update + upgrade"
apt-get update -qq
apt-get -y -qq full-upgrade
apt-get install -y -qq git curl ca-certificates python3 python3-venv

echo ":: Code holen ($REPO_URL @$BRANCH)"
mkdir -p "$(dirname "$APP_DIR")"
if [ -d "${APP_DIR}/.git" ]; then
  git -C "$APP_DIR" fetch --all --prune
  git -C "$APP_DIR" reset --hard "origin/${BRANCH}"
else
  rm -rf "${APP_DIR}.tmp"
  git clone --depth 1 --branch "$BRANCH" "$REPO_URL" "${APP_DIR}.tmp"
  rm -rf "$APP_DIR"
  mv "${APP_DIR}.tmp" "$APP_DIR"
fi

echo ":: Python venv + Abhängigkeiten"
cd "$SRC_DIR"
[ -d venv ] || python3 -m venv venv
./venv/bin/pip install --upgrade pip setuptools wheel -q
./venv/bin/pip install -r requirements.txt -q

echo ":: Systembenutzer anlegen"
id "$APP" >/dev/null 2>&1 || useradd --system --home-dir "$APP_DIR" --shell /usr/sbin/nologin "$APP"
chown -R "$APP:$APP" "$APP_DIR"

echo ":: systemd-Unit schreiben (Port $PORT)"
cat > "$SERVICE" <<UNIT
[Unit]
Description=Vorsorge-Ordner (FastAPI Web-App)
Documentation=${REPO_URL}
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=${APP}
Group=${APP}
WorkingDirectory=${SRC_DIR}/app
ExecStart=${APP_DIR}/venv/bin/uvicorn main:app --host 0.0.0.0 --port ${PORT}
Restart=always
RestartSec=3
Environment=PYTHONUNBUFFERED=1
NoNewPrivileges=true
ProtectSystem=full
ProtectHome=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
UNIT

systemctl daemon-reload
systemctl enable --now "$APP"
sleep 2

if ! systemctl is-active --quiet "$APP"; then
  echo ":: SERVICE NICHT AKTIV – Journal-Auszug:"
  journalctl -u "$APP" --no-pager -n 80
  ss -tlnp || true
  exit 1
fi

if ! curl -fsS "http://127.0.0.1:${PORT}/api/health"; then
  echo ""
  echo ":: HEALTH-CHECK FEHLGESCHLAGEN – Journal-Auszug:"
  journalctl -u "$APP" --no-pager -n 80
  exit 1
fi
echo ""
echo "INNER_OK"
INNER
)

install_in_ct() {
  local ctid="$1"
  local tmp_host="/tmp/${APP}-inner.sh"
  printf '%s\n' "$INNER_SCRIPT" >"$tmp_host"
  pct push "$ctid" "$tmp_host" "/tmp/${APP}-inner.sh"
  pct exec "$ctid" -- bash "/tmp/${APP}-inner.sh" \
    "$APP" "$APP_DIR" "$PORT" "$REPO_URL" "$BRANCH"
}

verify_from_host() {
  local ctid="$1"
  msg_info "Verifikation vom Host …"
  pct exec "$ctid" -- systemctl is-active --quiet "$APP"
  msg_ok "Service läuft im Container (systemctl is-active: active)"
  pct exec "$ctid" -- curl -fsS "http://127.0.0.1:${PORT}/api/health" >/dev/null
  msg_ok "Web UI antwortet (HTTP 200 auf /api/health)"
}

print_summary() {
  local ctid="$1" ip="$2"
  echo ""
  echo -e "${BLD}${GN}═══════════════════════════════════════════════════════════${CL}"
  echo -e "${BLD}  Vorsorge-Ordner erfolgreich installiert!${CL}"
  echo -e "${GN}═══════════════════════════════════════════════════════════${CL}"
  echo "  Web UI      : http://${ip}:${PORT}"
  echo "  Container   : CTID ${ctid} (Hostname: ${HN})"
  echo "  Service     : systemctl status vorsorgeordner   # innerhalb des CT"
  echo "  Logs        : pct exec ${ctid} -- journalctl -u vorsorgeordner -f"
  echo "  Update      : dieses Script einfach erneut ausführen"
  echo "  Entfernen   : pct stop ${ctid} && pct destroy ${ctid}"
  echo "  Install-Log : ${LOGFILE}"
  echo -e "${GN}═══════════════════════════════════════════════════════════${CL}"
}

# --------------------------------- Main --------------------------------------
main() {
  header
  require_root
  require_proxmox
  msg_ok "Läuft als root auf Proxmox VE $(pveversion)"

  # CTID ermitteln
  if [[ -z "$CTID" ]]; then
    CTID="$(next_ctid)"
  fi

  # Existierender Container -> Update-Modus
  if ct_exists "$CTID"; then
    echo ""
    msg_info "Container ${CTID} existiert bereits."
    if [[ ! -t 0 ]]; then
      msg_error "Nicht-interaktiv: für Update explizit ausführen mit CTID=${CTID} in einer interaktiven Shell."
      exit 1
    fi
    read -r -p "  App im Container aktualisieren statt neu installieren? [J/n] " answer </dev/tty
    answer="${answer:-J}"
    if [[ ! "$answer" =~ ^[JjYy] ]]; then
      msg_error "Abgebrochen. Wähle eine freie CT-ID mit CTID=<n>."
      exit 1
    fi
    msg_info "Starte Container …"
    STD pct start "$CTID" || true
    wait_for_network "$CTID"
    msg_ok "Netzwerk steht."
    msg_info "Update läuft …"
    install_in_ct "$CTID" | tee -a "$LOGFILE"
    verify_from_host "$CTID"
    IP=$(pct exec "$CTID" -- hostname -I | awk '{print $1}')
    print_summary "$CTID" "$IP"
    return 0
  fi

  # Template suchen/laden
  msg_info "Suche Debian-12-Template …"
  STD pveam update
  TEMPLATE=$(pveam available --section system 2>/dev/null \
             | awk '/debian-12-standard/ {print $2}' | sort -V | tail -n1)
  [[ -n "$TEMPLATE" ]] || { msg_error "Kein debian-12-standard Template gefunden."; exit 1; }
  if ! pveam list "$STORAGE" 2>/dev/null | grep -q "$TEMPLATE"; then
    msg_info "Lade Template ${TEMPLATE} herunter …"
    STD pveam download "$STORAGE" "$TEMPLATE"
  fi
  msg_ok "Template bereit: ${TEMPLATE}"

  # Container erstellen
  NET_OPTS="name=eth0,bridge=${BRIDGE},ip=dhcp"
  [[ -n "$VLAN_TAG" ]] && NET_OPTS+=",tag=${VLAN_TAG}"

  msg_info "Erstelle LXC ${CTID} (${HN}, ${CORES} vCPU, ${MEM_MB} MB RAM, ${DISK_GB} GB) …"
  STD pct create "$CTID" "${STORAGE}:vztmpl/${TEMPLATE}" \
    --hostname "$HN" \
    --cores "$CORES" \
    --memory "$MEM_MB" \
    --swap "$SWAP_MB" \
    --rootfs "${STORAGE}:${DISK_GB}" \
    --net0 "$NET_OPTS" \
    --onboot 1 \
    --ostype debian \
    --unprivileged 1 \
    --features nesting=1 \
    --start 1
  msg_ok "Container erstellt und gestartet."

  wait_for_network "$CTID"
  msg_ok "Container-Netzwerk steht."

  msg_info "Installiere Abhängigkeiten & App im Container (kann einige Minuten dauern) …"
  install_in_ct "$CTID" | tee -a "$LOGFILE"
  grep -q "INNER_OK" "$LOGFILE" || { msg_error "Innerer Installer meldete kein INNER_OK."; exit 1; }
  msg_ok "App installiert."

  verify_from_host "$CTID"

  IP=$(pct exec "$CTID" -- hostname -I | awk '{print $1}')
  print_summary "$CTID" "$IP"
}

main "$@"
