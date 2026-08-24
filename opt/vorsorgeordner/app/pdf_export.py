"""PDF-Export des kompletten Vorsorge-Ordners (ReportLab/platypus)."""
from __future__ import annotations

import io
import os
import re
from datetime import date
from xml.sax.saxutils import escape as esc

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas as pdfcanvas
from reportlab.platypus import (HRFlowable, PageBreak, Paragraph,
                                SimpleDocTemplate, Spacer, Table, TableStyle)

from content import (APP_SUBTITLE, APP_TITLE, BRAND_FOOTER, CHECKLIST_ITEMS,
                     DISCLAIMER_KURZ, LEGAL_TABLE, WEGWEISER, checklist_status)
from models import VorsorgeDaten

BRAND = os.environ.get("VO_BRAND", "Vorsorge-Ordner")

LEFT_M = 22 * mm
RIGHT_M = 15 * mm
TOP_M = 18 * mm
BOTTOM_M = 20 * mm
CW = A4[0] - LEFT_M - RIGHT_M

GREEN = colors.HexColor("#2e7d32")
GREEN_DARK = colors.HexColor("#1b5e20")
GREEN_BG = colors.HexColor("#e8f5e9")
AMBER_BG = colors.HexColor("#fff8e1")
AMBER_BD = colors.HexColor("#f9a825")
RED_BG = colors.HexColor("#fdecea")
RED_BD = colors.HexColor("#c62828")
GRAY_TXT = colors.HexColor("#607d8b")
LINE_GRAY = colors.HexColor("#b0bec5")

STATUS_COLORS = {
    "Erledigt": GREEN_BG,
    "In Arbeit": AMBER_BG,
    "Offen": colors.HexColor("#ffebee"),
    "Nicht zutreffend": colors.HexColor("#eceff1"),
}

_erstellt_am = date.today().strftime("%d.%m.%Y")

_base = getSampleStyleSheet()["Normal"]
_base.fontName = "Helvetica"
_base.fontSize = 9.5


def _st(name: str, **kw) -> ParagraphStyle:
    return ParagraphStyle(name=name, parent=_base, **kw)


ST_TITLE = _st("voTitle", fontName="Helvetica-Bold", fontSize=26, leading=32,
               alignment=TA_CENTER, textColor=GREEN_DARK)
ST_SUB = _st("voSub", fontSize=12, alignment=TA_CENTER, textColor=GRAY_TXT)
ST_H1 = _st("voH1", fontName="Helvetica-Bold", fontSize=16, leading=20,
            textColor=GREEN_DARK, spaceAfter=6)
ST_H2 = _st("voH2", fontName="Helvetica-Bold", fontSize=11.5, leading=15,
            textColor=GREEN_DARK, spaceBefore=8, spaceAfter=3)
ST_BODY = _st("voBody", fontSize=9.5, leading=13.5)
ST_KV = _st("voKv", fontSize=10, leading=15.5)
ST_SMALL = _st("voSmall", fontSize=8.5, leading=11.5, textColor=GRAY_TXT)
ST_HINT = _st("voHint", fontSize=9, leading=12.5)
ST_CENTER = _st("voCenter", alignment=TA_CENTER)
ST_TH = _st("voTh", fontName="Helvetica-Bold", fontSize=9, leading=11,
            textColor=colors.white)
ST_TD = _st("voTd", fontSize=9, leading=11.5)
ST_LINES = _st("voLines", fontSize=10, leading=17)


class OrdnerCanvas(pdfcanvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_states = []

    def showPage(self):
        self._saved_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total = len(self._saved_states)
        for state in self._saved_states:
            self.__dict__.update(state)
            self._decorate(total)
            pdfcanvas.Canvas.showPage(self)
        pdfcanvas.Canvas.save(self)

    def _decorate(self, total: int):
        self.saveState()
        self.setStrokeColor(LINE_GRAY)
        self.setLineWidth(0.7)
        for y in (105 * mm, 192 * mm):
            self.circle(10 * mm, y, 2.6 * mm, stroke=1, fill=0)
        self.setStrokeColor(LINE_GRAY)
        self.setLineWidth(0.4)
        self.line(LEFT_M, 14 * mm, A4[0] - RIGHT_M, 14 * mm)
        self.setFont("Helvetica", 7.5)
        self.setFillColor(GRAY_TXT)
        self.drawString(LEFT_M, 10 * mm, f"{BRAND_FOOTER} · erstellt am {_erstellt_am}")
        self.drawRightString(A4[0] - RIGHT_M, 10 * mm, f"Seite {self._pageNumber} von {total}")
        self.restoreState()


def P(text: str, style=ST_BODY) -> Paragraph:
    return Paragraph(text, style)


def kv(label: str, value, style=ST_KV, blank="—") -> Paragraph:
    val = str(value or "").strip()
    shown = esc(val) if val else f'<font color="#90a4ae">{blank}</font>'
    return P(f"<b>{esc(label)}:</b> {shown}", style)


def lines(n: int = 3) -> list:
    return [P("_" * 92, ST_LINES) for _ in range(n)]


def hint_box(text: str, bg=AMBER_BG, border=AMBER_BD, title="Rechtlicher Hinweis") -> Table:
    flow = [P(f"<b>{esc(title)}</b><br/>{esc(text)}", ST_HINT)]
    t = Table([[flow]], colWidths=[CW])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("BOX", (0, 0), (-1, -1), 0.8, border),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


def legal(text: str) -> Table:
    return hint_box(text)


def warn_box(text: str, title="Wichtig") -> Table:
    return hint_box(text, bg=RED_BG, border=RED_BD, title=title)


def info_box(text: str, title="Tipp") -> Table:
    return hint_box(text, bg=GREEN_BG, border=GREEN, title=title)


def register_header(nr: int, title: str) -> Table:
    t = Table([[
        P(f"<b>REGISTER {nr}</b>", ST_TH),
        P(f"<b>{esc(title)}</b>", ST_TH),
    ]], colWidths=[30 * mm, CW - 30 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), GREEN),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


def section(title: str):
    return [Spacer(1, 6), P(esc(title), ST_H2),
            HRFlowable(width="100%", thickness=0.7, color=GREEN_BG, spaceAfter=5)]


def einhefte_box(note: str = "") -> Table:
    inner = [
        P("<b>ZUM EINHEFTEN / ÜBERKLEBEN</b>", ST_CENTER),
        P(esc(note) if note else
          "Platz für das Original bzw. eine Kopie – hier später mit Klarsichthülle befestigen.",
          ST_SMALL),
        Spacer(1, 18 * mm),
    ]
    t = Table([[inner]], colWidths=[CW], rowHeights=[38 * mm])
    t.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1, LINE_GRAY, None, (3, 3)),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
    ]))
    return t


def data_table(headers: list, rows: list, widths_mm: list, empty_note="Noch keine Einträge.") -> Table:
    body = [[P(f"<b>{esc(h)}</b>", ST_TH) for h in headers]]
    for row in rows:
        body.append([P(esc(str(c)) if c else "", ST_TD) for c in row])
    if not rows:
        body.append([P(f"<i>{esc(empty_note)}</i>", ST_TD)] + [""] * (len(headers) - 1))
    t = Table(body, colWidths=[w * mm for w in widths_mm], repeatRows=1)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), GREEN),
        ("GRID", (0, 0), (-1, -1), 0.5, LINE_GRAY),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    for i in range(1, len(body)):
        if i % 2 == 0:
            style.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor("#f6f9f6")))
    t.setStyle(TableStyle(style))
    return t


def signature_block() -> Table:
    t = Table([[P("Ort, Datum: ____________________________", ST_BODY),
                P("Unterschrift: ____________________________", ST_BODY)]],
              colWidths=[CW / 2, CW / 2])
    t.setStyle(TableStyle([("TOPPADDING", (0, 0), (-1, -1), 14)]))
    return t


def draft_box(title: str, paragraphs: list[str]) -> Table:
    inner = [P(f"<b>{esc(title)}</b>", ST_H2)]
    inner += [P(esc(p)) for p in paragraphs]
    t = Table([[inner]], colWidths=[CW])
    t.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1, GREEN),
        ("BACKGROUND", (0, 0), (-1, -1), colors.white),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    return t


def yn(v) -> str:
    return {True: "Ja", False: "Nein"}.get(v, "")


def person_line(p) -> str:
    parts = [p.name, p.geburtsdatum, p.geburtsort]
    return ", ".join(x for x in (str(i).strip() for i in parts) if x)


def vp_line(vp) -> str:
    parts = [vp.name, vp.beziehung, vp.telefon]
    return ", ".join(x for x in (str(i).strip() for i in parts) if x)


# ---------------------------------------------------------------- Registers --

def reg_01(d: VorsorgeDaten) -> list:
    v = d.vorsorgevollmacht
    out = [legal(CHECKLIST_ITEMS[0][1]), Spacer(1, 6)]
    out += section("Angaben")
    out += [
        kv("Status", v.status),
        kv("Aufbewahrungsort", v.aufbewahrung),
        kv("Im Zentralen Vorsorgeregister eingetragen", yn(v.register_eingetragen)),
        kv("Bevollmächtigte Person", v.bevollmaechtigter.name),
        kv("Anschrift Bevollmächtigte(r)", v.bevollmaechtigter.anschrift),
        kv("Ersatz-Bevollmächtigte(r)", person_line(v.ersatz_bevollmaechtigter)),
        kv("Anschrift Ersatz", v.ersatz_bevollmaechtigter.anschrift),
        kv("Gilt über den Tod hinaus", yn(v.ueber_tod_hinaus)),
    ]
    bereiche = ", ".join(v.bereiche) if v.bereiche else \
        "Gesundheits- und Pflegeangelegenheiten, Aufenthalts-/Wohnungsangelegenheiten, Vermögenssorge und Bankgeschäfte, Post- und Fernmeldeverkehr, Behörden und Gerichte, sonstige Rechtsgeschäfte"
    out += section("Geltungsbereiche der Vollmacht")
    out.append(P(esc(bereiche)))
    out += lines(2)
    entwurf = [
        f"Ich, {d.person.name or '____________________'}"
        f"{', geboren am ' + d.person.geburtsdatum if d.person.geburtsdatum else ''}"
        f"{', in ' + d.person.geburtsort if d.person.geburtsort else ''}"
        f"{', wohnhaft ' + d.person.anschrift if d.person.anschrift else ''}, "
        f"erteile hiermit {v.bevollmaechtigter.name or '____________________'} "
        f"{('wohnhaft ' + v.bevollmaechtigter.anschrift) if v.bevollmaechtigter.anschrift else ''} "
        f"Vollmacht, mich in folgenden Angelegenheiten zu vertreten: {bereiche}.",
        "Der/die Bevollmächtigte ist berechtigt, für einzelne Angelegenheiten Unterbevollmächtigte zu "
        "bestellen sowie Erklärungen abzugeben, die ich selbst abgeben könnte.",
        f"Diese Vollmacht {'gilt über meinen Tod hinaus' if v.ueber_tod_hinaus else 'endet mit meinem Tod'} "
        "und ist jederzeit widerruflich. Mir ist bekannt, dass ich die Vollmacht jederzeit widerrufen kann.",
        "Ort, Datum: ______________________     Unterschrift: ______________________",
    ]
    out += [Spacer(1, 8), draft_box("Entwurf – bitte abschreiben/anpassen und eigenhändig unterschreiben", entwurf)]
    out += [Spacer(1, 6), einhefte_box()]
    return out


def reg_02(d: VorsorgeDaten) -> list:
    pv = d.patientenverfuegung
    out = [legal(CHECKLIST_ITEMS[1][1]), Spacer(1, 6)]
    out += section("Angaben")
    out += [kv("Status", pv.status), kv("Aufbewahrungsort", pv.aufbewahrung)]
    out += section("Situationen, für die ich festlege")
    out.append(P(esc("; ".join(pv.situationen) if pv.situationen else "—")))
    out += section("Meine Wünsche zu medizinischen Maßnahmen")
    out += [
        kv("Lebenserhaltende Maßnahmen", pv.lebenserhaltend),
        kv("Wiederbelebung", pv.wiederbelebung),
        kv("Künstliche Ernährung", pv.kuenstliche_ernaehrung),
        kv("Schmerz- und Symptomlinderung", pv.schmerzlinderung),
    ]
    if pv.text:
        out += section("Weitere Festlegungen")
        out.append(P(esc(pv.text)))
    sit = "; ".join(pv.situationen) if pv.situationen else "den genannten Situationen"
    entwurf = [
        f"Ich, {d.person.name or '____________________'}, lege für den Fall fest, dass ich meinen Willen "
        f"nicht mehr bilden oder verständlich äußern kann, für folgende Situationen: {sit}.",
        "Zu lebenserhaltenden Maßnahmen äußere ich mich wie folgt – Lebenserhaltung: "
        f"{pv.lebenserhaltend or 'nach ärztlicher Einschätzung'}; Wiederbelebung: "
        f"{pv.wiederbelebung or 'nach ärztlicher Einschätzung'}; künstliche Ernährung: "
        f"{pv.kuenstliche_ernaehrung or 'nach ärztlicher Einschätzung'}; Schmerz- und Symptomlinderung: "
        f"{pv.schmerzlinderung or 'nach ärztlicher Einschätzung'}.",
        pv.text or "",
        "Ich bitte meinen Hausarzt und mein Behandlungsteam, diese Verfügung zu beachten.",
        "Ort, Datum: ______________________     Unterschrift: ______________________",
    ]
    out += [Spacer(1, 8), draft_box("Entwurf – bitte abschreiben/anpassen und eigenhändig unterschreiben", [e for e in entwurf if e])]
    out += [Spacer(1, 6), einhefte_box()]
    return out


def reg_03(d: VorsorgeDaten) -> list:
    b = d.betreuungsverfuegung
    out = [legal(CHECKLIST_ITEMS[2][1]), Spacer(1, 6)]
    out += section("Angaben")
    out += [
        kv("Status", b.status),
        kv("Ort der Ausfertigung", b.ort),
        kv("Von mir vorgeschlagene(r) Betreuer(in)", person_line(b.betreuer)),
        kv("Anschrift", b.betreuer.anschrift),
        kv("Ersatz-Betreuer(in)", person_line(b.ersatz_betreuer)),
        kv("Wunsch im Pflegefall", b.pflegewunsch),
        kv("Besondere Wünsche", b.wuensche),
    ]
    entwurf = [
        f"Sollte für mich ein Betreuer bestellt werden müssen, schlage ich hierfür "
        f"{b.betreuer.name or '____________________'} vor, als Ersatzperson {b.ersatz_betreuer.name or '____________________'}.",
        f"Ich wünsche, im Pflegefall {b.pflegewunsch or 'zu Hause bzw. bei meinen Angehörigen'} betreut zu werden.",
        b.wuensche or "",
        "Das Betreuungsgericht möge diese Wünsche nach § 1816 BGB berücksichtigen.",
        "Ort, Datum: ______________________     Unterschrift: ______________________",
    ]
    out += [Spacer(1, 8), draft_box("Entwurf – bitte abschreiben/anpassen und eigenhändig unterschreiben", [e for e in entwurf if e])]
    out += [Spacer(1, 6), einhefte_box()]
    return out


def reg_04(d: VorsorgeDaten) -> list:
    s = d.sorgerecht
    out = [legal(CHECKLIST_ITEMS[3][1]), Spacer(1, 6)]
    if not s.relevant:
        out += [info_box("Du hast angegeben, dass dieses Register nicht zutreffend ist (keine minderjährigen "
                         "Kinder). Die Seite kann leer bleiben oder entfernt werden.", title="Nicht zutreffend")]
        return out
    kinder = ", ".join(f.name for f in d.vertrauenspersonen.familie) or "siehe Register „Vertrauenspersonen“"
    out += [
        kv("Betroffene Kinder", kinder),
        kv("Status", s.status),
        kv("Zum Vormund bestimmt", person_line(s.vormund)),
        kv("Anschrift", s.vormund.anschrift),
        kv("Ersatz-Vormund", person_line(s.ersatz_vormund)),
        kv("Aufbewahrungsort", s.aufbewahrung),
        kv("Erziehungswünsche", s.erziehungswuensche),
    ]
    entwurf = [
        "Sollten beide sorgeberechtigten Elternteile vor der Volljährigkeit unserer Kinder versterben, "
        f"wünschen wir als Vormund {s.vormund.name or '____________________'}"
        f", als Ersatzvormund {s.ersatz_vormund.name or '____________________'}.",
        s.erziehungswuensche or "",
        "Ort, Datum: ______________________     Unterschriften (beide Elternteile): ______________________",
    ]
    out += [Spacer(1, 8), draft_box("Entwurf – bitte abschreiben/anpassen und unterschreiben", [e for e in entwurf if e])]
    out += [Spacer(1, 6), einhefte_box()]
    return out


def reg_05(d: VorsorgeDaten) -> list:
    t = d.testament
    out = [legal(CHECKLIST_ITEMS[4][1]),
           warn_box("Ein ausgedrucktes oder getipptes Testament ist ungültig! Ein eigenhändiges Testament muss "
                    "vollständig handschriftlich verfasst und unterschrieben sein (§ 2247 BGB). Der unten stehende "
                    "Entwurf dient nur als Struktur-Hilfe.", title="ACHTUNG – Formvorschrift"),
           Spacer(1, 6)]
    out += section("Angaben")
    out += [
        kv("Art", t.art or "Eigenhändiges Testament (handschriftlich)"),
        kv("Datum", t.datum),
        kv("Aufbewahrungsort", t.aufbewahrung),
        kv("Notar / Anwalt", t.notar_anwalt),
    ]
    out += section("Erben")
    rows = [(e.name, e.beziehung, e.anteil, e.ersatzerbe) for e in t.erben]
    out.append(data_table(["Name", "Beziehung", "Anteil", "Ersatzerbe"], rows, [45, 35, 20, 40]))
    out.append(P("<i>Nahe Angehörige haben gesetzlich Anspruch auf einen Pflichtteil – dieser kann nicht "
                 "komplett entzogen werden.</i>", ST_SMALL))
    out += section("Weitere Regelungen")
    out += [
        kv("Vermächtnisse", t.vermaechtnisse),
        kv("Testamentsvollstrecker", t.testamentsvollstrecker),
        kv("Schlussbestimmungen", t.schlussbestimmungen),
    ]
    entwurf = [
        "Mein letzter Wille.",
        f"Ich setze zu meinen Erben ein: {', '.join(e.name + (' (' + e.anteil + ')' if e.anteil else '') for e in t.erben) or '____________________'}.",
        f"Vermächtnisse: {t.vermaechtnisse or 'keine'}.",
        f"Testamentsvollstrecker: {t.testamentsvollstrecker or 'nicht bestellt'}.",
        "Ort, Datum: ______________________     Unterschrift: ______________________",
    ]
    out += [Spacer(1, 8), draft_box("Struktur-Entwurf – vollständig EIGENHÄNDIG abschreiben!", entwurf)]
    out += [Spacer(1, 6), einhefte_box("Hier das Original (Umschlag!) bzw. den Verwahrungs-Nachweis einheften.")]
    return out


def reg_06(d: VorsorgeDaten) -> list:
    n = d.nachfolge
    out = [legal(CHECKLIST_ITEMS[5][1]), Spacer(1, 6)]
    if not n.relevant:
        out.append(info_box("Kein Unternehmen / kein Hof vorhanden – Register kann übersprungen werden.",
                            title="Nicht zutreffend"))
        return out
    out += [
        kv("Art der Regelung", n.art_regelung),
        kv("Nachfolger(in)", n.nachfolger),
        kv("Berater (Steuerberater/Anwalt)", n.berater),
        kv("Hinweise", n.hinweise),
    ]
    out += [Spacer(1, 6), einhefte_box("Gesellschaftsvertrag, Nachfolgevereinbarung o. Ä. einheften.")]
    return out


def reg_07(d: VorsorgeDaten) -> list:
    b = d.bank
    out = [legal(CHECKLIST_ITEMS[6][1]), Spacer(1, 6)]
    out += section("Bankvollmacht")
    out += [
        kv("Bankvollmacht erteilt", b.vollmacht_erteilt),
        kv("An wen", b.vollmacht_an),
        kv("Hinweis", "Viele Banken verlangen ihr eigenes internes Vollmachtsformular – dort direkt ausfüllen lassen."),
    ]
    out += section("Meine Banken & Konten")
    rows = [(x.institut, x.ansprechpartner, x.kontoart) for x in b.banken]
    out.append(data_table(["Institut", "Ansprechpartner", "Kontoart"], rows, [55, 55, 40]))
    entwurf = [
        f"Hiermit bevollmächtige ich {b.vollmacht_an or '____________________'}, alle meine Konten und "
        "Depots bei den oben aufgeführten Instituten im Rahmen der üblichen Geschäfte zu verwalten, "
        "Verfügungen zu tätigen und Verträge zu ändern oder zu kündigen.",
        "Ort, Datum: ______________________     Unterschrift: ______________________",
    ]
    out += [Spacer(1, 8), draft_box("Formulierungshilfe (bankinternes Formular hat Vorrang)", entwurf)]
    out += [Spacer(1, 6), einhefte_box("Vollmachtsformulare der Bank(en) einheften.")]
    return out


def reg_08(d: VorsorgeDaten) -> list:
    v = d.vorsorgevollmacht
    out = [legal(CHECKLIST_ITEMS[7][1]), Spacer(1, 6)]
    out += [
        kv("In meiner Vorsorgevollmacht geregelt", yn(v.ueber_tod_hinaus) or "Bitte in Register 1 festlegen"),
        kv("Ort der Regelung", "Register 1 · Vorsorgevollmacht („transmortale Vollmacht“)"),
    ]
    out += section("Warum wichtig?")
    out.append(P("Ohne Vollmacht über den Tod hinaus endet die Vorsorgevollmacht mit dem Tod – die Erben können "
                 "z. B. Konten dann erst nach Eröffnung der Erbschaft verwalten. Mit transmortaler Vollmacht kann "
                 "die Vertrauensperson sofort handeln (Miete zahlen, Kündigungen aussprechen, Abos stoppen)."))
    return out


def reg_09(d: VorsorgeDaten) -> list:
    b = d.bestattung
    out = [legal(CHECKLIST_ITEMS[8][1]), Spacer(1, 6)]
    out += section("Bestattungsart & Grab")
    out += [
        kv("Art der Bestattung", b.art),
        kv("Friedhof / Ort", b.friedhof),
        kv("Grabart", b.grabart),
        kv("Bestattungsvorsorgevertrag vorhanden", b.vorsorgevertrag),
        kv("Sarg / Urne", b.sarg_urne),
    ]
    out += section("Trauerfeier")
    out += [
        kv("Trauerfeier", b.trauerfeier),
        kv("Redner / Musik", b.redner),
        kv("Musikwünsche", b.musik),
        kv("Blumen / Spende statt Blumen", b.blumen_spende),
        kv("Traueranzeige", b.anzeige),
        kv("Grabgestaltung", b.grabgestaltung),
        kv("Kleidung", b.kleidung),
    ]
    out += [Spacer(1, 6), einhefte_box("Bestattungsvorsorgevertrag bzw. Bestätigung des Bestatters einheften.")]
    return out


def reg_10(d: VorsorgeDaten) -> list:
    o = d.organspende
    out = [legal(CHECKLIST_ITEMS[9][1]), Spacer(1, 6)]
    out += [
        kv("Meine Entscheidung", o.entscheidung or "Organspendeausweis ausfüllen und hier einheften"),
        kv("Details / Einschränkungen", o.details),
        kv("Registereintrag", "Seit 2024 online möglich: organspende-register.de"),
    ]
    out += [Spacer(1, 6), einhefte_box("Ausgefüllten Organspendeausweis hier einheften.")]
    return out


def reg_11(d: VorsorgeDaten) -> list:
    g = d.digital
    out = [legal(CHECKLIST_ITEMS[10][1]),
           warn_box("Trage niemals echte Passwörter in diesen ausgedruckten Ordner ein, solange er nicht "
                    "gesichert aufbewahrt wird! Nutze Hinweise wie „Passwort-Manager im Safe“.", title="Sicherheit"),
           Spacer(1, 6)]
    out += [
        kv("Passwort-Manager", g.passwort_manager),
        kv("Geräte & Zugänge", g.geraete),
        P("<b>Master-Zugang (handschriftlich ergänzen):</b> ______________________________________", ST_KV),
        P("<b>Notfall-Kontakt für Passwort-Manager:</b> _______________________________________________", ST_KV),
    ]
    out += section("Online-Konten (Aktion im Ernstfall)")
    rows = [(k.dienst, k.benutzername, k.aktion) for k in g.konten]
    out.append(data_table(["Dienst", "Benutzername (ohne Passwort!)", "Aktion (Löschen/Übertragen/Erinnern)"],
                          rows, [45, 50, 65]))
    out += [Spacer(1, 6), einhefte_box()]
    return out


def reg_12(d: VorsorgeDaten) -> list:
    out = [P(esc(CHECKLIST_ITEMS[11][1]), ST_BODY), Spacer(1, 6)]
    out += [
        kv("Wo liegen die Schlüssel?", d.schluessel, blank="_____________________________________"),
        kv("Zugänge / Codes / Schlösser", d.zugaenge, blank="_____________________________________"),
    ]
    out += lines(4)
    out += [Spacer(1, 6), einhefte_box("Ersatzschlüssel ggf. bei Vertrauensperson hinterlegen – hier nur NOTIEREN.")]
    return out


def reg_13(d: VorsorgeDaten) -> list:
    rows = [(k.rolle, k.name, k.telefon) for k in d.kontakte]
    out = [data_table(["Rolle", "Name", "Telefon"], rows, [50, 60, 50],
                      empty_note="Noch keine Kontakte eingetragen.")]
    out += [Spacer(1, 8), data_table(["Rolle", "Name", "Telefon"],
                                     [("", "", ""), ("", "", ""), ("", "", "")], [50, 60, 50],
                                     empty_note="(Platz zum Handschriftlichen Ergänzen)")]
    return out


def reg_14(d: VorsorgeDaten) -> list:
    rows = [(v.art, v.partner, v.kuendigungsfrist, v.ort_unterlagen) for v in d.vertrage]
    out = [data_table(["Art (Miete/Strom/Versicherung/Abo…)", "Partner", "Kündigungsfrist", "Ort der Unterlagen"],
                      rows, [50, 40, 30, 40], empty_note="Noch keine Verträge eingetragen.")]
    out += [Spacer(1, 8), data_table(["Art", "Partner", "Kündigungsfrist", "Ort"],
                                     [("", "", "", ""), ("", "", "", "")], [50, 40, 30, 40],
                                     empty_note="(Platz zum Ergänzen)")]
    return out


def reg_15(d: VorsorgeDaten) -> list:
    v = d.vermoegen
    out = [
        kv("Konten / Depots", v.konten, blank="_______________________________________________"),
        kv("Immobilien / Grundstücke", v.immobilien, blank="_______________________________________________"),
        kv("Fahrzeuge", v.fahrzeuge, blank="_______________________________________________"),
        kv("Schulden / Kredite", v.schulden_kredite, blank="_______________________________________________"),
        kv("Wertgegenstände (Schmuck, Sammlungen …)", v.wertgegenstaende, blank="_______________________________________________"),
    ]
    out += lines(4)
    out += [Spacer(1, 6), einhefte_box("Aktuelle Kontoauszüge / Gutachten NICHT einstecken – nur Übersicht.")]
    return out


def reg_16(d: VorsorgeDaten) -> list:
    rows = [(x.art, x.gesellschaft, x.police_ort) for x in d.versicherungen]
    out = [data_table(["Versicherungsart", "Gesellschaft", "Police / Standort"], rows, [50, 55, 55],
                      empty_note="Noch keine Versicherungen eingetragen.")]
    out += [Spacer(1, 8), data_table(["Art", "Gesellschaft", "Standort"],
                                     [("", "", ""), ("", "", "")], [50, 55, 55],
                                     empty_note="(Platz zum Ergänzen)")]
    out += [Spacer(1, 6), einhefte_box("Versicherungspolicen (oder Kopien) hier einheften.")]
    return out


def reg_17(d: VorsorgeDaten) -> list:
    r = d.rente_steuer
    out = [
        kv("Rentenversicherung / Rentenbescheide", r.rente, blank="____________________________________________"),
        kv("Steuerunterlagen / Steuer-ID", r.steuer, blank="____________________________________________"),
        kv("Ort der Unterlagen", r.unterlagen_ort, blank="____________________________________________"),
    ]
    out += lines(3)
    return out


def reg_18(d: VorsorgeDaten) -> list:
    u = d.urkunden
    out = [info_box("Original-Urkunden nicht lose einlegen – in Klarsichthülle einheften oder nur den "
                    "Aufbewahrungsort notieren.", title="So geht's richtig"),
           Spacer(1, 6)]
    out += [
        kv("Geburtsurkunde", u.geburtsurkunde, blank="________________________________________"),
        kv("Heiratsurkunde", u.heiratsurkunde, blank="________________________________________"),
        kv("Scheidungsurteil", u.scheidungsurteil, blank="________________________________________"),
        kv("Personalausweis / Reisepass (Kopie)", u.ausweiskopie, blank="________________________________________"),
        kv("Weitere Urkunden", u.weitere, blank="________________________________________"),
    ]
    out += [Spacer(1, 6), einhefte_box("Urkunden in Klarsichthüllen einheften.")]
    return out


def reg_19(d: VorsorgeDaten) -> list:
    m = d.medizin
    out = [P("Dieses Blatt ist aufgebaut, wie Rettungskräfte oder Ärzte im Notfall Informationen brauchen.", ST_BODY),
           Spacer(1, 6)]
    out += [
        kv("Name", d.person.name),
        kv("Geburtsdatum", d.person.geburtsdatum),
        kv("Blutgruppe", m.blutgruppe, blank="__________"),
        kv("Hausarzt", f"{m.hausarzt_name}{(', ' + m.hausarzt_praxis) if m.hausarzt_praxis else ''}"),
        kv("Telefon Hausarzt", m.hausarzt_telefon, blank="__________________"),
    ]
    out += section("Weitere Ärzte / Fachärzte")
    rows = [(a.name, a.fachrichtung, a.telefon) for a in m.aerzte]
    out.append(data_table(["Name", "Fachrichtung", "Telefon"], rows, [55, 45, 45]))
    out += section("Diagnosen / Vorerkrankungen")
    out += [P(esc(m.diagnosen or "—")), Spacer(1, 4)]
    out.append(warn_box(m.allergien or "— keine Angaben —", title="ALLERGIEN / UNVERTRÄGLICHKEITEN"))
    out += section("Medikamente")
    rows = [(x.name, x.dosierung) for x in m.medikamente]
    out.append(data_table(["Medikament", "Dosierung"], rows, [80, 65]))
    out += [kv("Ort des Medikamentenplans", m.medikamentenplan_ort, blank="____________________________")]
    return out


def reg_20(d: VorsorgeDaten) -> list:
    out = [legal(CHECKLIST_ITEMS[19][1]), Spacer(1, 6)]
    rows = [(t.name, t.tierart, t.betreuungsperson, t.tierarzt) for t in d.haustiere]
    out.append(data_table(["Name", "Tierart", "Betreuungsperson im Notfall", "Tierarzt"],
                          rows, [30, 30, 50, 50], empty_note="Keine Haustiere eingetragen."))
    out += [Spacer(1, 8), data_table(["Name", "Tierart", "Betreuungsperson", "Tierarzt"],
                                     [("", "", "", "")], [30, 30, 50, 50],
                                     empty_note="(Platz zum Ergänzen)")]
    out += [Spacer(1, 6), einhefte_box("Futter-/Pflegeanweisungen und Impfpass-Kopien einheften.")]
    return out


def reg_21(d: VorsorgeDaten) -> list:
    nf = d.notfallkarte
    cut = Table([[P("- - - - - - - - - - - - - - - -  SCHNITTKANTE: HIER AUSNEHMEN  - - - - - - - - - - - - - - - -", ST_SMALL)]],
                colWidths=[CW])
    cut.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER")]))
    card_w = 95 * mm
    card = Table([
        [P("<b>MEIN VORSORGE-ORDNER</b>", ST_CENTER)],
        [P("Meine Vorsorgedokumente liegen bei:", ST_SMALL)],
        [P(f"<b>{esc(nf.aufbewahrung) or '_____________________'}</b>", ST_CENTER)],
        [P("Kontaktperson:", ST_SMALL)],
        [P(f"<b>{esc(nf.kontakt) or '_____________________'}</b>", ST_CENTER)],
        [P("Telefon:", ST_SMALL)],
        [P(f"<b>{esc(nf.telefon) or '_____________________'}</b>", ST_CENTER)],
        [P(BRAND_FOOTER, ST_SMALL)],
    ], colWidths=[card_w])
    card.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1.2, GREEN),
        ("BACKGROUND", (0, 0), (-1, 0), GREEN_BG),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    wrap = Table([[card]], colWidths=[CW])
    wrap.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER"),
                              ("TOPPADDING", (0, 0), (-1, -1), 10)]))
    return [
        cut,
        P("Karte ausschneiden, laminieren/festigen und in den Geldbeutel legen – sie verweist Rettungskräften "
          "und Angehörigen auf diesen Ordner.", ST_SMALL),
        wrap,
        Spacer(1, 10),
        info_box("Nach dem Ausdrucken: Karte ausschneiden und handschriftlich ergänzen, falls Felder noch leer sind."),
    ]


REGISTERS = [
    ("Vorsorgevollmacht", reg_01),
    ("Patientenverfügung", reg_02),
    ("Betreuungsverfügung", reg_03),
    ("Sorgerechtsverfügung", reg_04),
    ("Testament oder Erbvertrag", reg_05),
    ("Unternehmens- oder Hofnachfolge", reg_06),
    ("Bankvollmacht / Depotvollmacht", reg_07),
    ("Vollmacht über den Tod hinaus", reg_08),
    ("Bestattungsverfügung", reg_09),
    ("Organspendeausweis / Registereintrag", reg_10),
    ("Digitaler Nachlass", reg_11),
    ("Schlüssel & Zugänge", reg_12),
    ("Wichtige Kontakte", reg_13),
    ("Wichtige Verträge", reg_14),
    ("Vermögensübersicht", reg_15),
    ("Versicherungsunterlagen", reg_16),
    ("Renten- und Steuerunterlagen", reg_17),
    ("Persönliche Urkunden", reg_18),
    ("Medizinisches Notfallblatt", reg_19),
    ("Haustier-Regelung", reg_20),
    ("Notfallkarte für den Geldbeutel", reg_21),
]

# ------------------------------------------------------------- Front matter --


def deckblatt(d: VorsorgeDaten) -> list:
    vp = d.vertrauenspersonen
    card = Table([
        [P("<b>Person</b>"), P(esc(d.person.name) or "—")],
        [P("<b>Geburtsdatum</b>"), P(esc(d.person.geburtsdatum) or "—")],
        [P("<b>Geburtsort</b>"), P(esc(d.person.geburtsort) or "—")],
        [P("<b>Anschrift</b>"), P(esc(d.person.anschrift) or "—")],
        [P("<b>Vertrauensperson</b>"), P(esc(vp_line(vp.haupt)) or "—")],
        [P("<b>Ersatzperson</b>"), P(esc(vp_line(vp.ersatz)) or "—")],
    ], colWidths=[42 * mm, 98 * mm])
    card.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, LINE_GRAY),
        ("BACKGROUND", (0, 0), (0, -1), GREEN_BG),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    center = Table([[card]], colWidths=[CW])
    center.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER")]))
    return [
        Spacer(1, 28 * mm),
        P(esc(APP_TITLE), ST_TITLE),
        Spacer(1, 4),
        P(esc(APP_SUBTITLE), ST_SUB),
        Spacer(1, 10),
        HRFlowable(width="60%", thickness=1, color=GREEN),
        Spacer(1, 24),
        center,
        Spacer(1, 26),
        hint_box(DISCLAIMER_KURZ, title="Bitte lesen"),
        Spacer(1, 8),
        info_box("Fülle die Felder am PC aus oder drucke den Ordner leer aus und schreibe von Hand – "
                 "besonders Passwörter und Master-Zugänge gehören nie ungeschützt hinein.", title="Handschriftlich ergänzen"),
        PageBreak(),
    ]


def checklist_page(d: VorsorgeDaten) -> list:
    out = [P("Inhaltsverzeichnis & Checkliste", ST_H1),
           P("Die 21 Punkte entsprechen den Registern 1–21 dieses Ordners. Setze den Status, sobald ein "
             "Dokument erstellt bzw. eingeheftet ist.", ST_BODY), Spacer(1, 8)]
    body = [[P("<b>Nr</b>", ST_TH), P("<b>Punkt</b>", ST_TH), P("<b>Status</b>", ST_TH)]]
    styles_extra = []
    for i, (titel, _hint) in enumerate(CHECKLIST_ITEMS, start=1):
        status = checklist_status(d.checkliste, i)
        body.append([P(str(i), ST_TD), P(esc(titel), ST_TD), P(esc(status), ST_TD)])
        color = STATUS_COLORS.get(status, colors.white)
        styles_extra.append(("BACKGROUND", (2, i), (2, i), color))
    t = Table(body, colWidths=[12 * mm, 118 * mm, CW - 130 * mm], repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), GREEN),
        ("GRID", (0, 0), (-1, -1), 0.5, LINE_GRAY),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ] + styles_extra))
    out += [t, PageBreak()]
    return out


def wegweiser_page() -> list:
    out = [P("Der Weg dorthin – in 8 Schritten", ST_H1), Spacer(1, 4)]
    for i, (titel, desc) in enumerate(WEGWEISER, start=1):
        out += [P(f"<b>Schritt {i} · {esc(titel)}</b>", ST_H2), P(esc(desc)), Spacer(1, 2)]
    out += [Spacer(1, 10),
            info_box("Registriere deine Vorsorgevollmacht im Zentralen Vorsorgeregister der Bundesnotarkammer "
                     "(vorsorgeregister.de) – dort können Ärzte und Gerichte im Ernstfall prüfen, ob eine "
                     "Vollmacht existiert.", title="Empfehlung"),
            PageBreak()]
    return out


def legal_page() -> list:
    out = [P("Rechtliche Hinweise & Formvorschriften", ST_H1), Spacer(1, 6)]
    body = [[P("<b>Dokument</b>", ST_TH), P("<b>Formvorschrift</b>", ST_TH), P("<b>Notar nötig?</b>", ST_TH)]]
    for row in LEGAL_TABLE:
        body.append([P(esc(c), ST_TD) for c in row])
    t = Table(body, colWidths=[48 * mm, 78 * mm, CW - 126 * mm], repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), GREEN),
        ("GRID", (0, 0), (-1, -1), 0.5, LINE_GRAY),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    out.append(t)
    out += section("Empfehlungen")
    for txt in [
        "Lass Vollmachten und Testament von einem Notar bzw. Anwalt prüfen, bevor es darauf ankommt.",
        "Sprich deine Patientenverfügung mit deinem Hausarzt durch – so ist sie im Ernstfall bekannt.",
        "Registriere die Vorsorgevollmacht im Zentralen Vorsorgeregister (vorsorgeregister.de).",
        "Gib Kopien bzw. Hinweise an deine Vertrauenspersonen – ein Ordner im Schrank hilft niemandem, "
        "der ihn nicht kennt.",
        "Prüfe alles jährlich und nach Heirat, Scheidung, Umzug oder neuen Diagnosen.",
    ]:
        out.append(P(f"•  {esc(txt)}", ST_BODY))
    out += [Spacer(1, 10), hint_box(
        DISCLAIMER_KURZ + " Dieses Werkzeug wird als kostenloser Organisationsservice bereitgestellt; "
        "es werden keine Rechts-, Steuer- oder Elektroleistungen erbracht.",
        title="Abschließender Hinweis")]
    return out


# ------------------------------------------------------------------- Build ---

def build_pdf(data: VorsorgeDaten) -> bytes:
    global _erstellt_am
    _erstellt_am = date.today().strftime("%d.%m.%Y")
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=LEFT_M, rightMargin=RIGHT_M, topMargin=TOP_M, bottomMargin=BOTTOM_M,
        title=f"{APP_TITLE} – {APP_SUBTITLE}", author=BRAND,
    )
    story: list = deckblatt(data) + checklist_page(data) + wegweiser_page()
    for i, (title, builder) in enumerate(REGISTERS, start=1):
        story.append(PageBreak())
        story.append(register_header(i, title))
        story.append(Spacer(1, 8))
        story.extend(builder(data))
    story.append(PageBreak())
    story.extend(legal_page())
    doc.build(story, canvasmaker=OrdnerCanvas)
    return buf.getvalue()


def safe_filename(name: str, ext: str) -> str:
    base = re.sub(r"[^\w\s.-]", "", name, flags=re.UNICODE).strip().replace(" ", "-")
    base = re.sub(r"-+", "-", base)[:60] or "Ordner"
    return f"Vorsorge-Ordner-{base}.{ext}"
