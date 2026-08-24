"""Gemeinsame statische Inhalte für PDF- und DOCX-Export."""
from __future__ import annotations

APP_TITLE = "Mein Vorsorge-Ordner"
APP_SUBTITLE = "Alle wichtigen Unterlagen an einem Ort"
BRAND_FOOTER = "Vorsorge-Ordner · lokal gehostet"

DISCLAIMER_KURZ = (
    "Dieser Ordner ist eine Organisationshilfe und ersetzt keine Rechtsberatung. "
    "Für die rechtliche Wirksamkeit einzelner Dokumente (insbesondere Testament, "
    "Vorsorgevollmacht) gelten gesetzliche Formvorschriften – siehe letzte Seite. "
    "Lass dich bei Unsicherheiten von einem Notar, Anwalt bzw. deinem Hausarzt beraten."
)

# (Titel, kurzer Rechtshinweis)
CHECKLIST_ITEMS = [
    ("Vorsorgevollmacht",
     "Keine feste gesetzliche Form, schriftlich dringend empfohlen. Für Immobilien-/Bankgeschäfte "
     "verlangen Banken/Grundbuchamt oft eine notarielle Beglaubigung. Eintrag im Zentralen "
     "Vorsorgeregister der Bundesnotarkammer möglich (vorsorgeregister.de)."),
    ("Patientenverfügung",
     "Schriftform gesetzlich vorgeschrieben (§ 1901a BGB), keine Notarpflicht. "
     "Mit dem Hausarzt besprechen."),
    ("Betreuungsverfügung",
     "Schriftform reicht; das Betreuungsgericht berücksichtigt sie im Bedarfsfall."),
    ("Sorgerechtsverfügung (bei minderjährigen Kindern)",
     "Wird erst wirksam, falls kein sorgeberechtigter Elternteil mehr lebt; legt fest, wer Vormund wird."),
    ("Testament oder Erbvertrag",
     "Eigenhändiges Testament muss vollständig handschriftlich verfasst und unterschrieben sein "
     "(§ 2247 BGB) – ausgedruckt/getippt ist es ungültig. Ein Erbvertrag muss immer notariell "
     "beurkundet werden (§ 2276 BGB)."),
    ("Unternehmens- oder Hofnachfolge",
     "In manchen Bundesländern gilt die Höfeordnung (Anerbenrecht); Gesellschaftsvertrag beachten; "
     "Grundstücke notariell."),
    ("Bankvollmacht / Depotvollmacht",
     "Viele Banken verlangen ihr eigenes internes Vollmachtsformular."),
    ("Vollmacht über den Tod hinaus",
     "Meist als transmortale Vollmacht innerhalb der Vorsorgevollmacht geregelt."),
    ("Bestattungsverfügung",
     "Nicht formvorgeschrieben, aber schriftlich festhalten – Bestattungspflichtige sind an Wünsche gebunden."),
    ("Organspendeausweis oder Registereintrag",
     "Ergänzt, ersetzt aber nicht die Patientenverfügung. Registereintrag seit 2024 online möglich."),
    ("Digitaler Nachlass",
     "Niemals echte Passwörter eintragen – nur Hinterlegungshinweise (z. B. Passwort-Manager, Ort)."),
    ("Schlüssel & Zugänge",
     "Wo liegen Schlüssel, Codes, Zugangsmittel?"),
    ("Liste wichtiger Kontakte",
     "Angehörige, Arzt, Anwalt/Notar, Steuerberater, Versicherung."),
    ("Liste wichtiger Verträge",
     "Miete, Strom, Telefon, Versicherungen, Abos, Mitgliedschaften inkl. Kündigungsfristen."),
    ("Vermögensübersicht",
     "Konten, Immobilien, Fahrzeuge, Schulden/Kredite, Wertgegenstände."),
    ("Versicherungsunterlagen",
     "Kranken-, Pflege-, Lebens-, Unfall-, Haftpflicht-, Sterbegeldversicherung mit Police-Standort."),
    ("Renten- und Steuerunterlagen",
     "Rentenbescheide, Steuerbescheide, Bescheinigungen."),
    ("Geburtsurkunde, Heiratsurkunde, Scheidungsurteil, Ausweiskopie",
     "Original-Urkunden nicht lose einlegen – in Hülle/Klarsichthülle einheften."),
    ("Medikamentenplan, Diagnosen, Allergien, Arztkontakte",
     "Im Notfall entscheidend – z. B. Medikamentenplan an der Kühlschranktür."),
    ("Haustier-Regelung",
     "Wer betreut Tiere im Notfall? Tierarzt-Kontakte notieren."),
    ("Notfallkarte für den Geldbeutel",
     "Verweist Rettungskräften/Angehörigen den Ort des Ordners."),
]

# (Dokument, Formvorschrift, Notar/Beglaubigung nötig?)
LEGAL_TABLE = [
    ("Vorsorgevollmacht", "Keine feste Form; Schriftform dringend empfohlen",
     "Für Bank/Grundbuch häufig notarielle Beglaubigung"),
    ("Patientenverfügung", "Schriftform Pflicht (§ 1901a BGB)", "Nein"),
    ("Betreuungsverfügung", "Schriftform ausreichend", "Nein"),
    ("Sorgerechtsverfügung", "Schriftform empfohlen", "Nein"),
    ("Eigenhändiges Testament", "Vollständig handschriftlich + Unterschrift (§ 2247 BGB)",
     "Nein (Verwahrung beim Amtsgericht möglich)"),
    ("Notarielles Testament / Erbvertrag", "Notarielle Beurkundung (§ 2276 BGB)", "Ja"),
    ("Bankvollmacht", "Bankinternes Formular häufig erforderlich", "Je nach Bank"),
    ("Bestattungsverfügung", "Keine Form vorgeschrieben; schriftlich empfohlen", "Nein"),
]

WEGWEISER = [
    ("Vertrauenspersonen auswählen",
     "Haupt- und Ersatzvertrauensperson festlegen, Familie samt Geburtsdaten eintragen."),
    ("Vollmachten & Verfügungen ausfüllen",
     "Vorsorgevollmacht, Patientenverfügung, Betreuungsverfügung, ggf. Sorgerechtsverfügung."),
    ("Mit dem Hausarzt sprechen",
     "Patientenverfügung besprechen; Diagnosen, Allergien, Medikamente dokumentieren."),
    ("Testament erstellen",
     "Eigenhändig handschriftlich oder notariell; Erben und Vermächtnisse festlegen."),
    ("Bank & digitaler Nachlass",
     "Bank-/Depotvollmachten klären; Online-Konten und Geräte dokumentieren."),
    ("Bestattungswünsche festhalten",
     "Art der Bestattung, Grab, Trauerfeier; Organspende-Entscheidung treffen."),
    ("Ordner zusammenstellen",
     "Alles in diesen Ordner einheften, Kopien an Vertrauenspersonen geben, Vollmacht im Zentralen "
     "Vorsorgeregister registrieren (vorsorgeregister.de)."),
    ("Jährlich prüfen",
     "Nach Heirat, Scheidung, Umzug oder neuen Diagnosen: Passt noch alles?"),
]

STATUS_OFFEN = "Offen"


def checklist_status(checkliste: dict, idx: int) -> str:
    val = checkliste.get(str(idx), checkliste.get(idx))
    return val if isinstance(val, str) and val else STATUS_OFFEN
