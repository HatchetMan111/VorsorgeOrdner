"""Datenmodell des Vorsorge-Ordners.

Alle Felder haben Defaults, damit Teil-JSON problemlos verarbeitet werden kann.
Das Frontend schickt exakt diese Struktur an /api/export/pdf und /api/export/docx.
"""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class Strict(BaseModel):
    model_config = ConfigDict(extra="ignore")


class Person(Strict):
    name: str = ""
    geburtsdatum: str = ""
    geburtsort: str = ""
    anschrift: str = ""


class VertrauensPerson(Strict):
    name: str = ""
    beziehung: str = ""
    telefon: str = ""
    adresse: str = ""


class FamilienMitglied(Strict):
    name: str = ""
    beziehung: str = ""
    geburtsdatum: str = ""


class Vertrauenspersonen(Strict):
    haupt: VertrauensPerson = Field(default_factory=VertrauensPerson)
    ersatz: VertrauensPerson = Field(default_factory=VertrauensPerson)
    notizen: str = ""
    familie: List[FamilienMitglied] = Field(default_factory=list)


class Vorsorgevollmacht(Strict):
    status: str = "Offen"
    aufbewahrung: str = ""
    register_eingetragen: bool = False
    bevollmaechtigter: Person = Field(default_factory=Person)
    ersatz_bevollmaechtigter: Person = Field(default_factory=Person)
    bereiche: List[str] = Field(default_factory=list)
    ueber_tod_hinaus: Optional[bool] = None


class Patientenverfuegung(Strict):
    status: str = "Offen"
    aufbewahrung: str = ""
    situationen: List[str] = Field(default_factory=list)
    lebenserhaltend: str = ""
    wiederbelebung: str = ""
    kuenstliche_ernaehrung: str = ""
    schmerzlinderung: str = ""
    text: str = ""


class Betreuungsverfuegung(Strict):
    status: str = "Offen"
    ort: str = ""
    betreuer: Person = Field(default_factory=Person)
    ersatz_betreuer: Person = Field(default_factory=Person)
    pflegewunsch: str = ""
    wuensche: str = ""


class Sorgerecht(Strict):
    relevant: bool = False
    status: str = "Offen"
    vormund: Person = Field(default_factory=Person)
    ersatz_vormund: Person = Field(default_factory=Person)
    aufbewahrung: str = ""
    erziehungswuensche: str = ""


class Arzt(Strict):
    name: str = ""
    fachrichtung: str = ""
    telefon: str = ""


class Medikament(Strict):
    name: str = ""
    dosierung: str = ""


class Medizin(Strict):
    hausarzt_name: str = ""
    hausarzt_praxis: str = ""
    hausarzt_telefon: str = ""
    blutgruppe: str = ""
    aerzte: List[Arzt] = Field(default_factory=list)
    diagnosen: str = ""
    allergien: str = ""
    medikamentenplan_ort: str = ""
    medikamente: List[Medikament] = Field(default_factory=list)


class Erbe(Strict):
    name: str = ""
    beziehung: str = ""
    anteil: str = ""
    ersatzerbe: str = ""


class Testament(Strict):
    art: str = ""
    datum: str = ""
    aufbewahrung: str = ""
    notar_anwalt: str = ""
    erben: List[Erbe] = Field(default_factory=list)
    vermaechtnisse: str = ""
    testamentsvollstrecker: str = ""
    schlussbestimmungen: str = ""


class Nachfolge(Strict):
    relevant: bool = False
    art_regelung: str = ""
    nachfolger: str = ""
    berater: str = ""
    hinweise: str = ""


class Urkunden(Strict):
    geburtsurkunde: str = ""
    heiratsurkunde: str = ""
    scheidungsurteil: str = ""
    ausweiskopie: str = ""
    weitere: str = ""


class BankInstitut(Strict):
    institut: str = ""
    ansprechpartner: str = ""
    kontoart: str = ""


class Bank(Strict):
    vollmacht_erteilt: str = ""
    vollmacht_an: str = ""
    ueber_tod_hinaus: str = ""
    banken: List[BankInstitut] = Field(default_factory=list)


class OnlineKonto(Strict):
    dienst: str = ""
    benutzername: str = ""
    aktion: str = ""


class Digital(Strict):
    passwort_manager: str = ""
    master_zugang_hinweis: str = ""
    geraete: str = ""
    konten: List[OnlineKonto] = Field(default_factory=list)


class Bestattung(Strict):
    art: str = ""
    friedhof: str = ""
    vorsorgevertrag: str = ""
    grabart: str = ""
    sarg_urne: str = ""
    trauerfeier: str = ""
    redner: str = ""
    kleidung: str = ""
    musik: str = ""
    blumen_spende: str = ""
    anzeige: str = ""
    grabgestaltung: str = ""


class Organspende(Strict):
    entscheidung: str = ""
    details: str = ""


class Haustier(Strict):
    name: str = ""
    tierart: str = ""
    betreuungsperson: str = ""
    tierarzt: str = ""


class Kontakt(Strict):
    rolle: str = ""
    name: str = ""
    telefon: str = ""


class Vertrag(Strict):
    art: str = ""
    partner: str = ""
    kuendigungsfrist: str = ""
    ort_unterlagen: str = ""


class Vermoegen(Strict):
    konten: str = ""
    immobilien: str = ""
    fahrzeuge: str = ""
    schulden_kredite: str = ""
    wertgegenstaende: str = ""


class Versicherung(Strict):
    art: str = ""
    gesellschaft: str = ""
    police_ort: str = ""


class RenteSteuer(Strict):
    rente: str = ""
    steuer: str = ""
    unterlagen_ort: str = ""


class Notfallkarte(Strict):
    aufbewahrung: str = ""
    kontakt: str = ""
    telefon: str = ""


class VorsorgeDaten(BaseModel):
    model_config = ConfigDict(extra="ignore")

    person: Person = Field(default_factory=Person)
    vertrauenspersonen: Vertrauenspersonen = Field(default_factory=Vertrauenspersonen)
    vorsorgevollmacht: Vorsorgevollmacht = Field(default_factory=Vorsorgevollmacht)
    patientenverfuegung: Patientenverfuegung = Field(default_factory=Patientenverfuegung)
    betreuungsverfuegung: Betreuungsverfuegung = Field(default_factory=Betreuungsverfuegung)
    sorgerecht: Sorgerecht = Field(default_factory=Sorgerecht)
    medizin: Medizin = Field(default_factory=Medizin)
    testament: Testament = Field(default_factory=Testament)
    nachfolge: Nachfolge = Field(default_factory=Nachfolge)
    urkunden: Urkunden = Field(default_factory=Urkunden)
    bank: Bank = Field(default_factory=Bank)
    digital: Digital = Field(default_factory=Digital)
    bestattung: Bestattung = Field(default_factory=Bestattung)
    organspende: Organspende = Field(default_factory=Organspende)
    haustiere: List[Haustier] = Field(default_factory=list)
    schluessel: str = ""
    zugaenge: str = ""
    kontakte: List[Kontakt] = Field(default_factory=list)
    vertrage: List[Vertrag] = Field(default_factory=list)
    vermoegen: Vermoegen = Field(default_factory=Vermoegen)
    versicherungen: List[Versicherung] = Field(default_factory=list)
    rente_steuer: RenteSteuer = Field(default_factory=RenteSteuer)
    checkliste: dict = Field(default_factory=dict)
    notfallkarte: Notfallkarte = Field(default_factory=Notfallkarte)
    jaehrlich_pruefen_am: str = ""
