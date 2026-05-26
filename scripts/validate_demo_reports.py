from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from billing.billing_optimizer import format_billing_suggestions, suggest_billing_codes
from coding.icd10_search import format_icd10_suggestions, search_icd10gm
from validation.report_validator import validate_report


CASES = [
    {
        "name": "General medicine / GKV cold",
        "language": "de",
        "specialty": "Allgemeinmedizin",
        "insurance_type": "GKV",
        "patient": {
            "name": "Max Mustermann",
            "dob": "1980-01-01",
            "visit_date": "2026-05-21",
        },
        "notes": "Fieber, Infekt und Erkältung seit 3 Tagen, keine Dyspnoe, Rachen gerötet, Ruhe empfohlen.",
        "report": """## Briefkopf / Praxisdaten
Praxis Dr. med. Müller, hausärztliche Versorgung.

## Patientendaten
Max Mustermann, geboren am 1980-01-01.

## Versicherungsdaten
GKV, AOK.

## Empf?nger
An die zust?ndige Krankenversicherung

## Behandlungsdatum
2026-05-21

## Betreff
Arztbrief zur akuten oberen Atemwegsinfektion.

## Diagnosen
Akute Infektion der oberen Atemwege bei fieberhaftem Infekt.

## Anamnese
Der Patient berichtet über Fieber und Erkältungsbeschwerden seit drei Tagen. Dyspnoe wird verneint.

## Befund
Rachen gerötet, klinisch kein Hinweis auf respiratorische Dekompensation.

## Beurteilung
Vereinbar mit unkompliziertem oberen Atemwegsinfekt.

## Durchgef?hrte ?rztliche Leistungen
Dokumentierte ?rztliche Bewertung und Beratung entsprechend der klinischen Angaben.

## Therapie / Empfehlung
Körperliche Schonung, ausreichende Flüssigkeitszufuhr und symptomatische Therapie.

## Weiteres Vorgehen
Wiedervorstellung bei Verschlechterung, Dyspnoe oder anhaltendem Fieber.

## Ärztliche Hinweise / Abrechnungshinweise
Abrechnungshinweise sind als unverbindliche Unterstützung zu verstehen und müssen anhand der jeweils gültigen EBM-/GOÄ-Regeln geprüft werden.

## Schlussformel
Mit freundlichen kollegialen Grüßen.

## Unterschrift / Praxisstempel
Ärztliche Prüfung und Unterschrift / Praxisstempel.
Dieses Dokument wurde lokal mit MedLocal AI erstellt. Es ersetzt keine ärztliche Prüfung und Unterschrift.""",
    },
    {
        "name": "Urology / GKV dysuria",
        "language": "de",
        "specialty": "Urologie",
        "insurance_type": "GKV",
        "patient": {
            "name": "Anna Beispiel",
            "dob": "1976-03-15",
            "visit_date": "2026-05-21",
        },
        "notes": "Dysurie, Pollakisurie, kein Fieber, Urinstatus Leukozyten und Nitrit positiv, V.a. Harnwegsinfekt.",
        "report": """## Briefkopf / Praxisdaten
Urologische Praxis Dr. med. Weber.

## Patientendaten
Anna Beispiel, geboren am 1976-03-15.

## Versicherungsdaten
GKV, TK.

## Empf?nger
An die zust?ndige Krankenversicherung

## Behandlungsdatum
2026-05-21

## Betreff
Urologischer Arztbrief bei Dysurie und Pollakisurie.

## Diagnosen
Verdacht auf akuten unkomplizierten Harnwegsinfekt.

## Anamnese
Die Patientin berichtet über Dysurie und Pollakisurie. Fieber wird verneint.

## Befund
Urinstatus mit Leukozyten und Nitrit auffällig, klinisch kein Hinweis auf febrilen Verlauf.

## Beurteilung
Die Befundkonstellation ist vereinbar mit einem unkomplizierten Harnwegsinfekt.

## Durchgef?hrte ?rztliche Leistungen
Dokumentierte ?rztliche Bewertung und Beratung entsprechend der klinischen Angaben.

## Therapie / Empfehlung
Ausreichende Trinkmenge, symptomatische Maßnahmen und leitliniengerechte Therapieprüfung.

## Weiteres Vorgehen
Kontrolle bei Persistenz, Fieber, Flankenschmerz oder Verschlechterung.

## Ärztliche Hinweise / Abrechnungshinweise
Abrechnungshinweise sind als unverbindliche Unterstützung zu verstehen und müssen anhand der jeweils gültigen EBM-/GOÄ-Regeln geprüft werden.

## Schlussformel
Mit freundlichen kollegialen Grüßen.

## Unterschrift / Praxisstempel
Ärztliche Prüfung und Unterschrift / Praxisstempel.
Dieses Dokument wurde lokal mit MedLocal AI erstellt. Es ersetzt keine ärztliche Prüfung und Unterschrift.""",
    },
    {
        "name": "Orthopedics / PKV knee pain",
        "language": "de",
        "specialty": "Orthopädie",
        "insurance_type": "Privat (PKV)",
        "patient": {
            "name": "Petra Privat",
            "dob": "1969-09-09",
            "visit_date": "2026-05-21",
        },
        "notes": "Knieschmerz nach Sport, Schwellung, Bewegungsschmerz, NSAR empfohlen und Verlaufskontrolle.",
        "report": """## Briefkopf / Praxisdaten
Orthopädische Praxis Dr. med. Schneider.

## Patientendaten
Petra Privat, geboren am 1969-09-09.

## Versicherungsdaten
Privat (PKV), Allianz Private KV.

## Empf?nger
An die zust?ndige Krankenversicherung

## Behandlungsdatum
2026-05-21

## Betreff
Orthopädischer Arztbrief bei Knieschmerz nach sportlicher Belastung.

## Diagnosen
Akuter Knieschmerz mit Schwellung nach sportlicher Belastung, differentialdiagnostisch Distorsion oder Reizzustand.

## Anamnese
Die Patientin berichtet über Knieschmerzen nach Sport mit Schwellung und belastungsabhängigem Bewegungsschmerz.

## Befund
Kniegelenksschwellung und schmerzhafte Bewegung, keine weitergehenden nicht dokumentierten Befunde angenommen.

## Beurteilung
Die Beschwerden sprechen für einen akuten Reizzustand nach Belastung; weitere Diagnostik abhängig vom Verlauf.

## Durchgef?hrte ?rztliche Leistungen
Dokumentierte ?rztliche Bewertung und Beratung entsprechend der klinischen Angaben.

## Therapie / Empfehlung
NSAR nach Verträglichkeit, Schonung, Kühlung und Verlaufskontrolle.

## Weiteres Vorgehen
Wiedervorstellung bei Persistenz, Zunahme der Schwellung oder Instabilitätsgefühl.

## Ärztliche Hinweise / Abrechnungshinweise
Abrechnungshinweise sind als unverbindliche Unterstützung zu verstehen und müssen anhand der jeweils gültigen EBM-/GOÄ-Regeln geprüft werden.

## Schlussformel
Mit freundlichen kollegialen Grüßen.

## Unterschrift / Praxisstempel
Ärztliche Prüfung und Unterschrift / Praxisstempel.
Dieses Dokument wurde lokal mit MedLocal AI erstellt. Es ersetzt keine ärztliche Prüfung und Unterschrift.""",
    },
]


def main() -> int:
    failed = 0
    for case in CASES:
        validation = validate_report(case["report"], case["patient"], case["language"])
        icd = format_icd10_suggestions(search_icd10gm(case["notes"], language=case["language"], limit=5), language=case["language"])
        billing = format_billing_suggestions(
            suggest_billing_codes(case["notes"], case["insurance_type"], case["specialty"], language=case["language"], limit=8),
            language=case["language"],
        )
        ok = validation["ok"] and bool(icd)
        if case["insurance_type"] == "GKV":
            ok = ok and all(item["system"] == "EBM" for item in billing)
        else:
            ok = ok and all(item["system"] == "GOÄ" for item in billing)

        print(f"{'PASS' if ok else 'FAIL'} - {case['name']}")
        print(f"  Missing sections: {validation['missing']}")
        print(f"  Detected placeholders: {validation['placeholders']}")
        print(f"  Metadata present: {not any(label in validation['missing'] for label in ['Patient name', 'Date of birth', 'Treatment date'])}")
        print(f"  ICD suggestions: {[item['code'] for item in icd]}")
        print(f"  Billing systems: {[item['system'] for item in billing]}")
        if not ok:
            failed += 1
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
