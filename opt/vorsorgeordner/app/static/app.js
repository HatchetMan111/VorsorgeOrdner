"use strict";

const STORAGE_KEY = "vorsorgeordner_v1";
const CHECK_KEY = "vorsorgeordner_check_v1";

/* ----------------------------- Checkliste (21 Punkte) ------------------- */
const CHECKLIST = [
  ["Vorsorgevollmacht", "Schriftlich dringend empfohlen; für Bank/Grundbuch oft notarielle Beglaubigung; Eintrag im Zentralen Vorsorgeregister möglich."],
  ["Patientenverfügung", "Schriftform Pflicht (§ 1901a BGB), keine Notarpflicht – mit dem Hausarzt besprechen."],
  ["Betreuungsverfügung", "Schriftform reicht; Betreuungsgericht berücksichtigt sie im Bedarfsfall."],
  ["Sorgerechtsverfügung (minderjährige Kinder)", "Wird erst wirksam, falls kein sorgeberechtigter Elternteil mehr lebt."],
  ["Testament oder Erbvertrag", "Eigenhändig = vollständig handschriftlich (§ 2247 BGB); Erbvertrag immer notariell (§ 2276 BGB)."],
  ["Unternehmens- oder Hofnachfolge", "Höfeordnung/Anerbenrecht je nach Bundesland; Gesellschaftsvertrag beachten."],
  ["Bankvollmacht / Depotvollmacht", "Banken verlangen oft ihr eigenes internes Formular."],
  ["Vollmacht über den Tod hinaus", "Meist als transmortale Vollmacht in der Vorsorgevollmacht."],
  ["Bestattungsverfügung", "Nicht formvorgeschrieben, aber schriftlich festhalten."],
  ["Organspendeausweis oder Registereintrag", "Ergänzt die Patientenverfügung; Registereintrag seit 2024 online möglich."],
  ["Digitaler Nachlass", "Niemals echte Passwörter – nur Hinterlegungshinweise."],
  ["Schlüssel & Zugänge", "Wo liegen Schlüssel, Codes, Zugangsmittel?"],
  ["Liste wichtiger Kontakte", "Angehörige, Arzt, Anwalt/Notar, Steuerberater, Versicherung."],
  ["Liste wichtiger Verträge", "Inkl. Kündigungsfristen."],
  ["Vermögensübersicht", "Konten, Immobilien, Fahrzeuge, Schulden, Wertgegenstände."],
  ["Versicherungsunterlagen", "Mit Police-Standort."],
  ["Renten- und Steuerunterlagen", "Bescheide, Bescheinigungen."],
  ["Geburtsurkunde, Heiratsurkunde, Scheidungsurteil, Ausweiskopie", "Originale in Klarsichthülle einheften."],
  ["Medikamentenplan, Diagnosen, Allergien, Arztkontakte", "Im Notfall entscheidend."],
  ["Haustier-Regelung", "Wer betreut die Tiere im Notfall?"],
  ["Notfallkarte für den Geldbeutel", "Verweist auf den Ordner."],
];

const STATUS_OPTIONS = ["Offen", "In Arbeit", "Erledigt", "Nicht zutreffend"];
const JN = ["", "Ja", "Nein"];
const JA_NEIN_ARZT = ["", "Ja", "Nein", "Nach ärztlicher Einschätzung"];

/* --------------------------------- Defaults ----------------------------- */
function defaultState() {
  return {
    person: { name: "", geburtsdatum: "", geburtsort: "", anschrift: "" },
    vertrauenspersonen: {
      haupt: { name: "", beziehung: "", telefon: "", adresse: "" },
      ersatz: { name: "", beziehung: "", telefon: "", adresse: "" },
      notizen: "",
      familie: [],
    },
    vorsorgevollmacht: {
      status: "Offen", aufbewahrung: "", register_eingetragen: null,
      bevollmaechtigter: { name: "", anschrift: "" },
      ersatz_bevollmaechtigter: { name: "", anschrift: "" },
      bereiche: ["Gesundheitssorge", "Aufenthalt/Wohnungsangelegenheiten", "Vermögenssorge/Bankgeschäfte",
        "Post-/Fernmeldeverkehr", "Behörden/Gerichte", "Rechtsgeschäfte"],
      ueber_tod_hinaus: null,
    },
    patientenverfuegung: {
      status: "Offen", aufbewahrung: "",
      situationen: ["Unheilbare, zum Tode führende Erkrankung", "Dauerhafter irreversibler Bewusstseinsverlust",
        "Fortgeschrittene Demenz"],
      lebenserhaltend: "", wiederbelebung: "", kuenstliche_ernaehrung: "", schmerzlinderung: "",
      text: "",
    },
    betreuungsverfuegung: {
      status: "Offen", ort: "",
      betreuer: { name: "", anschrift: "" }, ersatz_betreuer: { name: "", anschrift: "" },
      pflegewunsch: "", wuensche: "",
    },
    sorgerecht: {
      relevant: null, status: "Offen",
      vormund: { name: "", anschrift: "" }, ersatz_vormund: { name: "", anschrift: "" },
      aufbewahrung: "", erziehungswuensche: "",
    },
    medizin: {
      hausarzt_name: "", hausarzt_praxis: "", hausarzt_telefon: "", blutgruppe: "",
      aerzte: [], diagnosen: "", allergien: "", medikamentenplan_ort: "", medikamente: [],
    },
    testament: {
      art: "", datum: "", aufbewahrung: "", notar_anwalt: "", erben: [],
      vermaechtnisse: "", testamentsvollstrecker: "", schlussbestimmungen: "",
    },
    nachfolge: { relevant: null, art_regelung: "", nachfolger: "", berater: "", hinweise: "" },
    urkunden: { geburtsurkunde: "", heiratsurkunde: "", scheidungsurteil: "", ausweiskopie: "", weitere: "" },
    bank: {
      vollmacht_erteilt: "", vollmacht_an: "", ueber_tod_hinaus: "",
      banken: [],
    },
    digital: { passwort_manager: "", master_zugang_hinweis: "", geraete: "", konten: [] },
    bestattung: {
      art: "", friedhof: "", vorsorgevertrag: "", grabart: "", sarg_urne: "",
      trauerfeier: "", redner: "", kleidung: "", musik: "", blumen_spende: "", anzeige: "", grabgestaltung: "",
    },
    organspende: { entscheidung: "", details: "" },
    haustiere: [],
    schluessel: "", zugaenge: "",
    kontakte: [], vertrage: [],
    vermoegen: { konten: "", immobilien: "", fahrzeuge: "", schulden_kredite: "", wertgegenstaende: "" },
    versicherungen: [],
    rente_steuer: { rente: "", steuer: "", unterlagen_ort: "" },
    checkliste: {},
    notfallkarte: { aufbewahrung: "", kontakt: "", telefon: "" },
    jaehrlich_pruefen_am: "",
  };
}

/* --------------------------------- Schema ------------------------------- */
const F = (path, label, type = "text", opts = {}) => ({ path, label, type, opts });
const LIST = (path, title, itemFields, addLabel) => ({ path, title, itemFields, addLabel });

const STEPS = [
  {
    tab: "Vertrauens-personen",
    sections: [
      {
        title: "Deine Angaben",
        fields: [
          F("person.name", "Vollständiger Name", "text", { full: true }),
          F("person.geburtsdatum", "Geburtsdatum", "date"),
          F("person.geburtsort", "Geburtsort"),
          F("person.anschrift", "Anschrift", "textarea", { full: true }),
        ],
      },
      {
        title: "Haupt-Vertrauensperson",
        intro: "Wähle eine Person, der du im Ernstfall voll vertraust.",
        fields: [
          F("vertrauenspersonen.haupt.name", "Name"),
          F("vertrauenspersonen.haupt.beziehung", "Beziehung (z. B. Ehepartner, Kind)"),
          F("vertrauenspersonen.haupt.telefon", "Telefon"),
          F("vertrauenspersonen.haupt.adresse", "Adresse"),
        ],
      },
      {
        title: "Ersatz-Vertrauensperson",
        fields: [
          F("vertrauenspersonen.ersatz.name", "Name"),
          F("vertrauenspersonen.ersatz.beziehung", "Beziehung"),
          F("vertrauenspersonen.ersatz.telefon", "Telefon"),
          F("vertrauenspersonen.ersatz.adresse", "Adresse"),
        ],
      },
      {
        title: "Familie / Kinder",
        intro: "Einmal hier eintragen – Namen und Geburtsdaten werden bei Sorgerecht und Testament wiederverwendet.",
        lists: [LIST("vertrauenspersonen.familie", "Familienmitglied",
          [F("name", "Name"), F("beziehung", "Beziehung"), F("geburtsdatum", "Geburtsdatum", "date")],
          "Person hinzufügen")],
      },
      {
        title: "Notizen",
        fields: [F("vertrauenspersonen.notizen", "Notizen", "textarea", { full: true })],
      },
    ],
  },
  {
    tab: "Vollmachten",
    sections: [
      {
        title: "Vorsorgevollmacht",
        legal: "Keine feste gesetzliche Form vorgeschrieben, schriftlich dringend empfohlen. Für Immobilien- oder Bankgeschäfte verlangen Banken/Grundbuchamt oft eine notarielle Beglaubigung.",
        fields: [
          F("vorsorgevollmacht.status", "Status", "select", { options: ["Offen", "In Arbeit", "Erstellt"] }),
          F("vorsorgevollmacht.register_eingetragen", "Im Zentralen Vorsorgeregister eingetragen?", "bool"),
          F("vorsorgevollmacht.aufbewahrung", "Aufbewahrungsort", "text", { full: true }),
          F("vorsorgevollmacht.bevollmaechtigter.name", "Bevollmächtigte Person"),
          F("vorsorgevollmacht.ersatz_bevollmaechtigter.name", "Ersatz-Bevollmächtigte(r)"),
          F("vorsorgevollmacht.bevollmaechtigter.anschrift", "Anschrift Bevollmächtigte(r)"),
          F("vorsorgevollmacht.ersatz_bevollmaechtigter.anschrift", "Anschrift Ersatz"),
          F("vorsorgevollmacht.bereiche", "Geltungsbereiche", "checks", {
            options: ["Gesundheitssorge", "Aufenthalt/Wohnungsangelegenheiten", "Vermögenssorge/Bankgeschäfte",
              "Post-/Fernmeldeverkehr", "Behörden/Gerichte", "Rechtsgeschäfte"], full: true,
          }),
          F("vorsorgevollmacht.ueber_tod_hinaus", "Gilt die Vollmacht über den Tod hinaus?", "bool"),
        ],
      },
      {
        title: "Patientenverfügung",
        legal: "Schriftform gesetzlich vorgeschrieben (§ 1901a BGB), keine Notarpflicht. Besprich sie mit deinem Hausarzt.",
        fields: [
          F("patientenverfuegung.status", "Status", "select", { options: ["Offen", "In Arbeit", "Erstellt"] }),
          F("patientenverfuegung.aufbewahrung", "Aufbewahrungsort"),
          F("patientenverfuegung.situationen", "Situationen, für die festgelegt wird", "checks", {
            options: ["Unheilbare, zum Tode führende Erkrankung", "Dauerhafter irreversibler Bewusstseinsverlust",
              "Fortgeschrittene Demenz"], full: true,
          }),
          F("patientenverfuegung.lebenserhaltend", "Lebenserhaltende Maßnahmen", "select", { options: JA_NEIN_ARZT }),
          F("patientenverfuegung.wiederbelebung", "Wiederbelebung", "select", { options: JA_NEIN_ARZT }),
          F("patientenverfuegung.kuenstliche_ernaehrung", "Künstliche Ernährung", "select", { options: JA_NEIN_ARZT }),
          F("patientenverfuegung.schmerzlinderung", "Schmerz- & Symptomlinderung", "select", { options: JA_NEIN_ARZT }),
          F("patientenverfuegung.text", "Weitere Festlegungen (Freitext)", "textarea", { full: true }),
        ],
      },
      {
        title: "Betreuungsverfügung",
        legal: "Schriftform ausreichend, keine Notarpflicht. Das Betreuungsgericht berücksichtigt sie im Bedarfsfall.",
        fields: [
          F("betreuungsverfuegung.status", "Status", "select", { options: ["Offen", "In Arbeit", "Erstellt"] }),
          F("betreuungsverfuegung.ort", "Ort der Ausfertigung"),
          F("betreuungsverfuegung.betreuer.name", "Vorgeschlagene(r) Betreuer(in)"),
          F("betreuungsverfuegung.ersatz_betreuer.name", "Ersatz-Betreuer(in)"),
          F("betreuungsverfuegung.betreuer.anschrift", "Anschrift Betreuer(in)"),
          F("betreuungsverfuegung.ersatz_betreuer.anschrift", "Anschrift Ersatz"),
          F("betreuungsverfuegung.pflegewunsch", "Wunsch im Pflegefall", "select",
            { options: ["", "Zuhause", "Bei Angehörigen", "Pflegeheim"] }),
          F("betreuungsverfuegung.wuensche", "Besondere Wünsche", "textarea", { full: true }),
        ],
      },
      {
        title: "Sorgerechtsverfügung (minderjährige Kinder)",
        legal: "Nur relevant bei minderjährigen Kindern: legt fest, wer Vormund werden soll, falls kein sorgeberechtigter Elternteil mehr lebt.",
        fields: [
          F("sorgerecht.relevant", "Hast du minderjährige Kinder?", "bool"),
          F("sorgerecht.status", "Status", "select", { options: ["Offen", "In Arbeit", "Erstellt"] }),
          F("sorgerecht.vormund.name", "Zum Vormund bestimmt"),
          F("sorgerecht.ersatz_vormund.name", "Ersatz-Vormund"),
          F("sorgerecht.vormund.anschrift", "Anschrift Vormund"),
          F("sorgerecht.ersatz_vormund.anschrift", "Anschrift Ersatz-Vormund"),
          F("sorgerecht.aufbewahrung", "Aufbewahrungsort"),
          F("sorgerecht.erziehungswuensche", "Erziehungswünsche", "textarea", { full: true }),
        ],
      },
    ],
  },
  {
    tab: "Hausarzt & Medizin",
    sections: [
      {
        title: "Hausarzt & Basisdaten",
        intro: "Diese Angaben helfen im medizinischen Notfall.",
        fields: [
          F("medizin.hausarzt_name", "Hausarzt / Ärztin"),
          F("medizin.hausarzt_praxis", "Praxis"),
          F("medizin.hausarzt_telefon", "Telefon"),
          F("medizin.blutgruppe", "Blutgruppe"),
          F("medizin.medikamentenplan_ort", "Ort des Medikamentenplans (z. B. Kühlschranktür)"),
        ],
      },
      {
        title: "Diagnosen & Allergien",
        fields: [
          F("medizin.diagnosen", "Diagnosen / Vorerkrankungen", "textarea", { full: true }),
          F("medizin.allergien", "Allergien / Unverträglichkeiten", "textarea", { full: true }),
        ],
      },
      {
        title: "Weitere Ärzte",
        lists: [LIST("medizin.aerzte", "Arzt / Facharzt",
          [F("name", "Name"), F("fachrichtung", "Fachrichtung"), F("telefon", "Telefon")], "Arzt hinzufügen")],
      },
      {
        title: "Aktuelle Medikamente",
        lists: [LIST("medizin.medikamente", "Medikament",
          [F("name", "Name"), F("dosierung", "Dosierung")], "Medikament hinzufügen")],
      },
    ],
  },
  {
    tab: "Testament",
    sections: [
      {
        title: "Testament oder Erbvertrag",
        legal: "Ein eigenhändiges Testament muss vollständig handschriftlich verfasst und unterschrieben sein (§ 2247 BGB) – ausgedruckt/getippt ist es ungültig! Ein Erbvertrag muss immer notariell beurkundet werden (§ 2276 BGB).",
        fields: [
          F("testament.art", "Art", "select",
            { options: ["", "Eigenhändiges Testament (handschriftlich)", "Notarielles Testament", "Erbvertrag"] }),
          F("testament.datum", "Datum", "date"),
          F("testament.aufbewahrung", "Aufbewahrungsort (z. B. Amtsgericht)"),
          F("testament.notar_anwalt", "Notar / Anwalt"),
        ],
      },
      {
        title: "Erben",
        intro: "Nahe Angehörige haben gesetzlich Anspruch auf einen Pflichtteil.",
        lists: [LIST("testament.erben", "Erbe",
          [F("name", "Name"), F("beziehung", "Beziehung"), F("anteil", "Anteil"), F("ersatzerbe", "Ersatzerbe")],
          "Erbe hinzufügen")],
      },
      {
        title: "Weitere Regelungen",
        fields: [
          F("testament.vermaechtnisse", "Vermächtnisse", "textarea", { full: true }),
          F("testament.testamentsvollstrecker", "Testamentsvollstrecker"),
          F("testament.schlussbestimmungen", "Schlussbestimmungen", "textarea", { full: true }),
        ],
      },
      {
        title: "Unternehmens- / Hofnachfolge",
        legal: "In manchen Bundesländern gilt die Höfeordnung (Anerbenrecht). Grundstücksübertragungen sind notariell.",
        fields: [
          F("nachfolge.relevant", "Unternehmen oder Hof vorhanden?", "bool"),
          F("nachfolge.art_regelung", "Art der Regelung"),
          F("nachfolge.nachfolger", "Nachfolger(in)"),
          F("nachfolge.berater", "Berater (Steuerberater/Anwalt)"),
          F("nachfolge.hinweise", "Hinweise", "textarea", { full: true }),
        ],
      },
      {
        title: "Persönliche Urkunden (Aufbewahrungsorte)",
        fields: [
          F("urkunden.geburtsurkunde", "Geburtsurkunde"),
          F("urkunden.heiratsurkunde", "Heiratsurkunde"),
          F("urkunden.scheidungsurteil", "Scheidungsurteil"),
          F("urkunden.ausweiskopie", "Personalausweis-Kopie"),
          F("urkunden.weitere", "Weitere Urkunden", "textarea", { full: true }),
        ],
      },
    ],
  },
  {
    tab: "Bank & Digital",
    sections: [
      {
        title: "Bankvollmacht",
        legal: "Viele Banken verlangen ihr eigenes internes Vollmachtsformular – kläre das direkt bei deiner Bank.",
        fields: [
          F("bank.vollmacht_erteilt", "Bankvollmacht erteilt?", "select", { options: ["", "Ja", "Nein", "Geplant"] }),
          F("bank.vollmacht_an", "An wen"),
          F("bank.ueber_tod_hinaus", "Vollmacht über den Tod hinaus?", "select", { options: JN }),
        ],
      },
      {
        title: "Meine Banken & Konten",
        lists: [LIST("bank.banken", "Bank",
          [F("institut", "Institut"), F("ansprechpartner", "Ansprechpartner"), F("kontoart", "Kontoart")],
          "Bank hinzufügen")],
      },
      {
        title: "Digitaler Nachlass",
        legal: "Niemals echte Passwörter eintragen – nur Hinweise, wo Zugänge hinterlegt sind (z. B. Passwort-Manager).",
        fields: [
          F("digital.passwort_manager", "Passwort-Manager"),
          F("digital.master_zugang_hinweis", "Wo ist der Master-Zugang hinterlegt?"),
          F("digital.geraete", "Geräte & Zugänge", "textarea", { full: true }),
        ],
      },
      {
        title: "Online-Konten",
        lists: [LIST("digital.konten", "Online-Konto",
          [F("dienst", "Dienst"), F("benutzername", "Benutzername (ohne Passwort!)"),
           F("aktion", "Aktion im Ernstfall", "select", { options: ["", "Löschen", "Übertragen", "Erinnern"] })],
          "Konto hinzufügen")],
      },
    ],
  },
  {
    tab: "Bestattung",
    sections: [
      {
        title: "Bestattungswünsche",
        intro: "Schriftlich festgehaltene Wünsche entlasten deine Angehörigen in einer schweren Zeit sehr.",
        fields: [
          F("bestattung.art", "Art der Bestattung", "select",
            { options: ["", "Erdbestattung", "Feuerbestattung", "Seebestattung"] }),
          F("bestattung.friedhof", "Wunsch-Friedhof / Ort"),
          F("bestattung.vorsorgevertrag", "Bestattungsvorsorgevertrag", "select", { options: JN }),
          F("bestattung.grabart", "Grabart", "select",
            { options: ["", "Reihengrab", "Wahlgrab", "Urnenwand", "Baumbestattung", "Anonym"] }),
          F("bestattung.sarg_urne", "Sarg / Urne"),
          F("bestattung.trauerfeier", "Trauerfeier", "select",
            { options: ["", "Kirchlich", "Weltlich", "Keine"] }),
          F("bestattung.redner", "Redner / Musik"),
          F("bestattung.musik", "Musikwünsche"),
          F("bestattung.kleidung", "Kleidung"),
          F("bestattung.blumen_spende", "Blumen / Spende statt Blumen"),
          F("bestattung.anzeige", "Traueranzeige"),
          F("bestattung.grabgestaltung", "Grabgestaltung"),
        ],
      },
      {
        title: "Organspende",
        legal: "Ein Organspendeausweis oder Registereintrag (seit 2024 online möglich) ergänzt die Patientenverfügung.",
        fields: [
          F("organspende.entscheidung", "Meine Entscheidung", "select",
            { options: ["", "Organspendeausweis vorhanden", "Registereintrag", "Nicht festgelegt"] }),
          F("organspende.details", "Details / Einschränkungen", "textarea", { full: true }),
        ],
      },
      {
        title: "Haustiere",
        lists: [LIST("haustiere", "Tier",
          [F("name", "Name"), F("tierart", "Tierart"), F("betreuungsperson", "Betreuungsperson im Notfall"),
           F("tierarzt", "Tierarzt")], "Tier hinzufügen")],
      },
    ],
  },
  {
    tab: "Ordner-Inhalt",
    sections: [
      {
        title: "Schlüssel & Zugänge",
        fields: [
          F("schluessel", "Wo liegen die Schlüssel?", "textarea", { full: true }),
          F("zugaenge", "Zugänge / Codes / Schlösser", "textarea", { full: true }),
        ],
      },
      {
        title: "Wichtige Kontakte",
        lists: [LIST("kontakte", "Kontakt", [F("rolle", "Rolle"), F("name", "Name"), F("telefon", "Telefon")],
          "Kontakt hinzufügen")],
      },
      {
        title: "Wichtige Verträge",
        lists: [LIST("vertrage", "Vertrag",
          [F("art", "Art (Miete/Strom/Versicherung/Abo…)"), F("partner", "Partner"),
           F("kuendigungsfrist", "Kündigungsfrist"), F("ort_unterlagen", "Ort der Unterlagen")],
          "Vertrag hinzufügen")],
      },
      {
        title: "Vermögensübersicht",
        fields: [
          F("vermoegen.konten", "Konten / Depots", "textarea", { full: true }),
          F("vermoegen.immobilien", "Immobilien / Grundstücke", "textarea", { full: true }),
          F("vermoegen.fahrzeuge", "Fahrzeuge", "textarea", { full: true }),
          F("vermoegen.schulden_kredite", "Schulden / Kredite", "textarea", { full: true }),
          F("vermoegen.wertgegenstaende", "Wertgegenstände", "textarea", { full: true }),
        ],
      },
      {
        title: "Versicherungen",
        lists: [LIST("versicherungen", "Versicherung",
          [F("art", "Art"), F("gesellschaft", "Gesellschaft"), F("police_ort", "Police / Standort")],
          "Versicherung hinzufügen")],
      },
      {
        title: "Rente & Steuern",
        fields: [
          F("rente_steuer.rente", "Rentenversicherung / Rentenbescheide", "textarea", { full: true }),
          F("rente_steuer.steuer", "Steuerunterlagen / Steuer-ID", "textarea", { full: true }),
          F("rente_steuer.unterlagen_ort", "Ort der Unterlagen"),
        ],
      },
    ],
  },
  { tab: "Abschluss & PDF", special: "final" },
];

/* ------------------------------- Utilities ------------------------------ */
const $ = (sel, el = document) => el.querySelector(sel);
const $$ = (sel, el = document) => Array.from(el.querySelectorAll(sel));
const escHtml = s => String(s ?? "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

function getByPath(obj, path) {
  return path.split(".").reduce((acc, key) => (acc == null ? undefined : acc[key]), obj);
}
function setByPath(obj, path, value) {
  const keys = path.split(".");
  let cur = obj;
  for (let i = 0; i < keys.length - 1; i++) {
    if (cur[keys[i]] == null) cur[keys[i]] = /^\d+$/.test(keys[i + 1]) ? [] : {};
    cur = cur[keys[i]];
  }
  cur[keys[keys.length - 1]] = value;
}

function deepMerge(defaults, saved) {
  if (Array.isArray(defaults)) return Array.isArray(saved) ? saved : defaults;
  if (defaults && typeof defaults === "object") {
    const out = { ...defaults };
    if (saved && typeof saved === "object") {
      for (const k of Object.keys(saved)) {
        out[k] = k in defaults ? deepMerge(defaults[k], saved[k]) : saved[k];
      }
    }
    return out;
  }
  return saved === undefined ? defaults : saved;
}

let state = defaultState();
let currentStep = 0;

function loadState() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) state = deepMerge(defaultState(), JSON.parse(raw));
  } catch (e) {
    console.warn("Konnte gespeicherte Angaben nicht laden:", e);
  }
}

let saveTimer = null;
function scheduleSave() {
  clearTimeout(saveTimer);
  saveTimer = setTimeout(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
      const t = new Date().toLocaleTimeString("de-DE");
      $("#saveStatus").textContent = `✓ Gespeichert um ${t} Uhr`;
    } catch (e) {
      $("#saveStatus").textContent = "⚠ Speichern fehlgeschlagen";
    }
  }, 350);
}

function progressPercent() {
  const done = CHECKLIST.filter((_, i) =>
    ["Erledigt", "Nicht zutreffend"].includes(state.checkliste[String(i + 1)] || "Offen")
  ).length;
  return Math.round((done / CHECKLIST.length) * 100);
}

function updateProgress() {
  const pct = progressPercent();
  $("#progressBar").style.width = pct + "%";
  $("#progressText").textContent = `${pct} % der Checkliste erledigt (${CHECKLIST.filter((_, i) =>
    ["Erledigt", "Nicht zutreffend"].includes(state.checkliste[String(i + 1)] || "Offen")
  ).length} von ${CHECKLIST.length})`;
}

/* ------------------------------- Rendering ------------------------------ */
const LIST_DEFS = {};
STEPS.forEach(s => (s.sections || []).forEach(sec => (sec.lists || []).forEach(l => { LIST_DEFS[l.path] = l; })));

function fieldHTML(f) {
  const full = f.opts.full || f.type === "textarea" ? " full" : "";
  const label = `<label>${f.label}</label>`;
  if (f.type === "textarea") {
    return `<div class="field${full}">${label}<textarea data-path="${f.path}"></textarea></div>`;
  }
  if (f.type === "date") {
    return `<div class="field${full}">${label}<input type="date" data-path="${f.path}"></div>`;
  }
  if (f.type === "select") {
    const opts = (f.opts.options || []).map(o => `<option value="${o}">${o}</option>`).join("");
    return `<div class="field${full}">${label}<select data-path="${f.path}"><option value=""></option>${opts}</select></div>`;
  }
  if (f.type === "bool") {
    return `<div class="field${full}">${label}<select data-bool="${f.path}">
      <option value="">—</option><option value="true">Ja</option><option value="false">Nein</option></select></div>`;
  }
  if (f.type === "checks") {
    const chips = (f.opts.options || []).map(o =>
      `<label class="chip"><input type="checkbox" data-check="${f.path}" value="${o}">${o}</label>`).join("");
    return `<div class="field${full}">${label}<div class="checks">${chips}</div></div>`;
  }
  return `<div class="field${full}">${label}<input type="text" data-path="${f.path}"></div>`;
}

function listItemHTML(def, idx) {
  const inner = def.itemFields.map(f => fieldHTML({ ...f, path: `${def.path}.${idx}.${f.path}` })).join("");
  return `<div class="list-item" data-item="${def.path}.${idx}">
    <button class="remove" data-action="remove" data-list="${def.path}" data-idx="${idx}" title="Entfernen">×</button>
    <div class="grid">${inner}</div></div>`;
}

function renderListInto(container, def) {
  const arr = getByPath(state, def.path) || [];
  container.innerHTML = `<div class="list-items">${
    arr.map((_, i) => listItemHTML(def, i)).join("")}</div>
    <button class="btn secondary small add" data-action="add" data-list="${def.path}">+ ${def.addLabel}</button>`;
}

function sectionHTML(sec) {
  let html = `<div class="card"><h2>${sec.title}</h2>`;
  if (sec.intro) html += `<p class="intro">${sec.intro}</p>`;
  if (sec.legal) html += `<div class="legal">⚖ ${sec.legal}</div>`;
  if (sec.fields) html += `<div class="grid">${sec.fields.map(fieldHTML).join("")}</div>`;
  (sec.lists || []).forEach(l => {
    html += `<h2 style="margin-top:16px">${l.title}</h2><div data-list-container="${l.path}"></div>`;
  });
  return html + `</div>`;
}

function checklistHTML() {
  return `<div class="card"><h2>Checkliste: alle 21 Punkte</h2>
    <p class="intro">Setze den Status, sobald ein Dokument erstellt bzw. eingeheftet ist.</p>
    ${CHECKLIST.map((item, i) => {
      const n = i + 1;
      return `<div class="checkrow">
        <div class="num">${n}</div>
        <div><div class="titel">${item[0]}</div><div class="hinttext">${item[1]}</div></div>
        <select data-path="checkliste.${n}">${STATUS_OPTIONS.map(s => `<option>${s}</option>`).join("")}</select>
      </div>`;
    }).join("")}</div>`;
}

function finalExtrasHTML() {
  const nk = state.notfallkarte;
  return `
  <div class="card"><h2>Notfallkarte für den Geldbeutel</h2>
    <p class="intro">Diese Karte wird auf der letzten Registerseite des PDFs mit Schnittkante erzeugt –
    ausschneiden und in den Geldbeutel legen.</p>
    <div class="grid">
      ${fieldHTML(F("notfallkarte.aufbewahrung", "Meine Vorsorgedokumente liegen bei …"))}
      ${fieldHTML(F("notfallkarte.kontakt", "Kontaktperson"))}
      ${fieldHTML(F("notfallkarte.telefon", "Telefon"))}
      ${fieldHTML(F("jaehrlich_pruefen_am", "Nächste jährliche Prüfung", "date"))}
    </div>
    <div class="notfallkarte" style="margin-top:14px">
      <div class="nk-head">MEIN VORSORGE-ORDNER</div>
      <div class="nk-body">
        <div style="font-size:.78rem;color:#607d8b">Meine Vorsorgedokumente liegen bei:</div>
        <div class="nk-line">${escHtml(nk.aufbewahrung) || "&nbsp;"}</div>
        <div style="font-size:.78rem;color:#607d8b">Kontaktperson:</div>
        <div class="nk-line">${escHtml(nk.kontakt) || "&nbsp;"}</div>
        <div style="font-size:.78rem;color:#607d8b">Telefon:</div>
        <div class="nk-line">${escHtml(nk.telefon) || "&nbsp;"}</div>
      </div>
    </div>
  </div>
  <div class="card"><h2>Ordner erstellen</h2>
    <p class="intro">Erzeugt einen kompletten, druckfertigen Ordner mit Deckblatt, Checkliste, Wegweiser,
    21 Registern, Notfallkarte und rechtlichen Hinweisen. Im Word-Format kannst du Felder später am PC nachtragen.</p>
    <div class="exportrow">
      <button class="btn success" data-action="export" data-kind="pdf">📄 Als PDF herunterladen</button>
      <button class="btn primary" data-action="export" data-kind="docx">📝 Als Word (.docx) herunterladen</button>
      <button class="btn danger small" data-action="reset">Alle Eingaben zurücksetzen</button>
    </div>
    <div class="hint privacy" style="margin-top:4px">Tipp: Nach dem Ausdrucken handschriftlich ergänzen –
    besonders Passwörter und Master-Zugänge (Register „Digitaler Nachlass“).</div>
  </div>`;
}

function renderTabs() {
  $("#tabs").innerHTML = STEPS.map((s, i) =>
    `<button class="tab${i === currentStep ? " active" : ""}" data-step="${i}">${i + 1}. ${s.tab}</button>`).join("");
}

function renderStep() {
  const step = STEPS[currentStep];
  let html = "";
  if (step.special === "final") {
    html = checklistHTML() + finalExtrasHTML();
  } else {
    html = step.sections.map(sectionHTML).join("");
  }
  $("#wizard").innerHTML = html;

  $$("[data-list-container]").forEach(c => renderListInto(c, LIST_DEFS[c.dataset.listContainer]));
  hydrate();
  $("#btnPrev").classList.toggle("hidden", currentStep === 0);
  $("#btnNext").classList.toggle("hidden", currentStep === STEPS.length - 1);
  $("#btnFinish").classList.toggle("hidden", currentStep !== STEPS.length - 1);
  renderTabs();
  updateProgress();
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function hydrate() {
  $$("[data-path]").forEach(el => {
    if (el.tagName === "SELECT" && el.dataset.bool === undefined) {
      const v = getByPath(state, el.dataset.path);
      el.value = v == null ? "" : v;
      if (el.value !== (v ?? "")) { el.value = ""; }
    } else if (el.tagName === "TEXTAREA" || el.tagName === "INPUT") {
      el.value = getByPath(state, el.dataset.path) ?? "";
    }
  });
  $$("[data-bool]").forEach(el => {
    const v = getByPath(state, el.dataset.bool);
    el.value = v === true ? "true" : v === false ? "false" : "";
  });
  $$("[data-check]").forEach(el => {
    const arr = getByPath(state, el.dataset.check) || [];
    el.checked = arr.includes(el.value);
    el.closest(".chip").classList.toggle("on", el.checked);
  });
}

/* ------------------------------- Events --------------------------------- */
$("#wizard").addEventListener("input", e => {
  const t = e.target;
  if (t.dataset.path) {
    setByPath(state, t.dataset.path, t.value);
    scheduleSave();
    if (t.dataset.path.startsWith("notfallkarte.")) renderNotfallPreview();
    if (t.dataset.path.startsWith("checkliste.")) updateProgress();
  }
});

$("#wizard").addEventListener("change", e => {
  const t = e.target;
  if (t.dataset.bool !== undefined) {
    setByPath(state, t.dataset.bool, t.value === "" ? null : t.value === "true");
    scheduleSave();
  }
  if (t.dataset.check) {
    const arr = getByPath(state, t.dataset.check) || [];
    const val = t.value;
    const idx = arr.indexOf(val);
    if (t.checked && idx === -1) arr.push(val);
    if (!t.checked && idx > -1) arr.splice(idx, 1);
    setByPath(state, t.dataset.check, arr);
    t.closest(".chip").classList.toggle("on", t.checked);
    scheduleSave();
  }
});

$("#wizard").addEventListener("click", e => {
  const btn = e.target.closest("button");
  if (!btn) return;
  const action = btn.dataset.action;

  if (action === "add") {
    const def = LIST_DEFS[btn.dataset.list];
    const arr = getByPath(state, def.path) || [];
    arr.push(Object.fromEntries(def.itemFields.map(f => [f.path.split(".").pop(), ""])));
    setByPath(state, def.path, arr);
    renderListInto($(`[data-list-container="${def.path}"]`), def);
    hydrate();
    scheduleSave();
  }
  if (action === "remove") {
    const path = btn.dataset.list;
    const idx = parseInt(btn.dataset.idx, 10);
    const arr = getByPath(state, path) || [];
    arr.splice(idx, 1);
    setByPath(state, path, arr);
    renderListInto($(`[data-list-container="${path}"]`), LIST_DEFS[path]);
    scheduleSave();
  }
  if (action === "export") exportDoc(btn.dataset.kind);
  if (action === "reset") {
    if (confirm("Wirklich alle Eingaben löschen? Das kann nicht rückgängig gemacht werden.")) {
      localStorage.removeItem(STORAGE_KEY);
      state = defaultState();
      renderStep();
      $("#saveStatus").textContent = "";
    }
  }
});

function renderNotfallPreview() {
  const card = $(".notfallkarte .nk-body");
  if (!card) return;
  const nk = state.notfallkarte;
  card.innerHTML = `
    <div style="font-size:.78rem;color:#607d8b">Meine Vorsorgedokumente liegen bei:</div>
    <div class="nk-line">${escHtml(nk.aufbewahrung) || "&nbsp;"}</div>
    <div style="font-size:.78rem;color:#607d8b">Kontaktperson:</div>
    <div class="nk-line">${escHtml(nk.kontakt) || "&nbsp;"}</div>
    <div style="font-size:.78rem;color:#607d8b">Telefon:</div>
    <div class="nk-line">${escHtml(nk.telefon) || "&nbsp;"}</div>`;
}

$("#tabs").addEventListener("click", e => {
  const tab = e.target.closest(".tab");
  if (tab) { currentStep = parseInt(tab.dataset.step, 10); renderStep(); }
});
$("#btnPrev").addEventListener("click", () => { if (currentStep > 0) { currentStep--; renderStep(); } });
$("#btnNext").addEventListener("click", () => { if (currentStep < STEPS.length - 1) { currentStep++; renderStep(); } });
$("#btnFinish").addEventListener("click", () => exportDoc("pdf"));

/* ------------------------------- Export --------------------------------- */
function showError(title, detail) {
  const box = $("#errorBox");
  box.classList.remove("hidden");
  box.innerHTML = `<b>⚠ ${title}</b><pre></pre>`;
  $("pre", box).textContent = detail;
}

async function exportDoc(kind) {
  const labels = { pdf: "PDF", docx: "Word" };
  try {
    scheduleSave();
    const res = await fetch(`/api/export/${kind}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(state),
    });
    if (!res.ok) {
      let body;
      try { body = JSON.stringify(JSON.parse(await res.text()), null, 2); }
      catch (_) { body = "(Konnte Antworttext nicht lesen)"; }
      throw new Error(`HTTP ${res.status} ${res.statusText}\n\nAntwort des Servers:\n${body}`);
    }
    const blob = await res.blob();
    const cd = res.headers.get("Content-Disposition") || "";
    let name = `Vorsorge-Ordner.${kind}`;
    const m1 = /filename\*=UTF-8''([^;]+)/.exec(cd);
    const m2 = /filename="([^"]+)"/.exec(cd);
    if (m1) name = decodeURIComponent(m1[1]);
    else if (m2) name = m2[1];
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = name;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
    $("#errorBox").classList.add("hidden");
  } catch (err) {
    showError(`${labels[kind]}-Export fehlgeschlagen`,
      `${err.message}\n\n${err.stack || ""}\n\nBitte prüfe: Läuft der Dienst? (systemctl status vorsorgeordner)`);
  }
}

/* --------------------------------- Init --------------------------------- */
loadState();
renderStep();
