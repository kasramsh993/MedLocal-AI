from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from utils.time_savings import estimate_manual_documentation_time, format_duration


SHORT_REPORT = """## Diagnosen
Akuter Infekt.
## Befund
Rachen gerötet.
## Therapie / Empfehlung
Schonung.
## Weiteres Vorgehen
Kontrolle bei Verschlechterung.
## Unterschrift / Praxisstempel
Ärztliche Prüfung und Unterschrift."""

LONG_REPORT = "\n".join([SHORT_REPORT] + ["Ausführliche klinische Dokumentation mit Befund und Empfehlung."] * 60)


def main() -> int:
    short = estimate_manual_documentation_time(
        transcript_text="Patient has fever for 3 days.",
        clinical_notes="No dyspnea.",
        generated_report=SHORT_REPORT,
        specialty="Allgemeinmedizin",
        includes_icd=True,
        includes_billing=False,
        ai_workflow_sec=20,
    )
    long = estimate_manual_documentation_time(
        transcript_text="Patient has fever for 3 days. " * 40,
        clinical_notes="No dyspnea. Rest recommended. " * 20,
        generated_report=LONG_REPORT,
        specialty="Kardiologie",
        includes_icd=True,
        includes_billing=True,
        ai_workflow_sec=120,
    )
    slow = estimate_manual_documentation_time(
        transcript_text="Patient has fever for 3 days.",
        clinical_notes="No dyspnea.",
        generated_report=SHORT_REPORT,
        specialty="Allgemeinmedizin",
        includes_icd=True,
        includes_billing=False,
        ai_workflow_sec=180,
    )

    checks = [
        ("Short report produces a positive dynamic estimate", short["estimated_saved_sec"] > 0),
        ("Long report has higher manual estimate than short report", long["manual_estimate_sec"] > short["manual_estimate_sec"]),
        ("Slow AI workflow reduces saved time", slow["estimated_saved_sec"] < short["estimated_saved_sec"]),
        ("German duration formatter works", "Min." in format_duration(160, "de")),
        ("English duration formatter works", format_duration(160, "en") == f"{2}m {40}s"),
    ]

    for label, ok in checks:
        print(f"{'PASS' if ok else 'FAIL'} - {label}")
    print(f"Short saved: {format_duration(short['estimated_saved_sec'], 'en')}")
    print(f"Long manual estimate: {format_duration(long['manual_estimate_sec'], 'en')}")
    return 0 if all(ok for _, ok in checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
