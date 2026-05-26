from datetime import date
from html import escape

import markdown as md_lib
import streamlit as st
import streamlit.components.v1 as components

from i18n import t


REPORT_SECTION_HEADERS = {
    "Ärztliche Stellungnahme zur Vorlage bei der Krankenversicherung",
    "Praxisdaten",
    "Patienten- und Versicherungsdaten",
    "Betreff",
    "Anlass der Vorstellung",
    "Anamnese",
    "Untersuchungsbefund",
    "Diagnostische Einschätzung / Diagnosen",
    "Diagnosen",
    "Durchgeführte ärztliche Leistungen",
    "Therapie / Empfehlung",
    "Medizinische Begründung",
    "Abrechnungshinweise",
    "Hinweis",
    "Ort, Datum",
    "Ärztliche Unterschrift / Praxisstempel",
}


def _status_label(status: str, lang: str) -> str:
    return {
        "Draft": t("status_draft", lang),
        "Generated": t("status_generated", lang),
        "Approved": t("status_approved", lang),
        "Correction in progress": t("status_correction", lang),
    }.get(status, status)


def _validation_item(label: str, lang: str) -> str:
    if lang == "en":
        return label
    return {
        "Realistic document length": "realistische Dokumentlänge",
        "Patient name": "Patientenname",
        "Date of birth": "Geburtsdatum",
        "Treatment date": "Behandlungsdatum",
        "Diagnoses": "Diagnosen",
        "Findings": "Befund",
        "Treatment / Recommendation": "Therapie / Empfehlung",
        "Follow-up": "Weiteres Vorgehen",
        "Signature / practice stamp": "Unterschrift / Praxisstempel",
        "Medical review notice": "Hinweis zur ärztlichen Prüfung",
    }.get(label, label)


def _copy_button(text: str, label: str) -> None:
    safe = escape(text)
    components.html(
        f"""
<button onclick="navigator.clipboard.writeText(document.getElementById('arztbrief-copy').innerText)"
        style="width:100%;height:38px;border-radius:12px;border:1px solid #c8d1dc;background:#ffffff;color:#102a43;font-weight:800;cursor:pointer;">
  {escape(label)}
</button>
<pre id="arztbrief-copy" style="display:none">{safe}</pre>
        """,
        height=44,
    )


def render_output_panel(patient: dict, report: str | None, is_pkv: bool, visit_date: str, lang: str) -> dict:
    st.markdown(
        f"""
<div class="ml-workflow-header">
  <div>
    <div class="ml-section-kicker">{t("professional_output", lang)}</div>
    <div class="ml-section-title">{t("report_review", lang)}</div>
    <div class="ml-section-note">{t("report_review_note", lang)}</div>
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )

    status = st.session_state.get("report_status", "Draft")
    st.markdown(f'<div class="ml-badge">{t("status", lang)} · {escape(_status_label(status, lang))}</div>', unsafe_allow_html=True)

    if st.session_state.get("success_message"):
        st.success(st.session_state.success_message)

    if not report:
        st.markdown(
            f"""
<div class="ml-empty-output">
  <strong>{t("no_report", lang)}</strong><br>
  {t("no_report_note", lang)}
</div>
            """,
            unsafe_allow_html=True,
        )
        return {"correct_clicked": False, "approve_clicked": False, "export_clicked": False}

    action_cols = st.columns(4, gap="small")
    with action_cols[0]:
        _copy_button(st.session_state.get("corrected_report") or report, t("copy_report", lang))
    with action_cols[1]:
        export_clicked = st.button(t("export_pdf", lang), use_container_width=True)
    with action_cols[2]:
        correct_clicked = st.button(t("correct_report", lang), use_container_width=True)
    with action_cols[3]:
        approve_clicked = st.button(t("approve_report", lang), use_container_width=True, type="primary")

    if (
        st.session_state.get("pdf_download_ready")
        and st.session_state.get("exported_pdf_hash") == st.session_state.get("current_generation_hash")
        and st.session_state.get("exported_pdf_bytes")
    ):
        st.download_button(
            t("download_pdf", lang),
            st.session_state.exported_pdf_bytes,
            file_name=st.session_state.get("exported_pdf_file_name", "arztbrief.pdf"),
            mime="application/pdf",
            use_container_width=True,
        )

    if correct_clicked:
        st.session_state.report_status = "Correction in progress"
        if not st.session_state.get("corrected_report"):
            st.session_state.corrected_report = report
        st.rerun()

    if st.session_state.get("report_status") == "Correction in progress":
        corrected_report = st.text_area(
            t("corrected_report", lang),
            value=st.session_state.get("corrected_report") or report,
            height=240,
            key="corrected_report_input",
        )
        st.session_state.corrected_report = corrected_report

    final_preview = st.session_state.get("corrected_report") or report
    validation = st.session_state.get("report_validation_result")
    if validation and not validation.get("ok", True):
        st.warning(t("validation_warnings", lang))
        details = []
        if validation.get("missing"):
            details.append(f"{t('validation_missing', lang)}: " + ", ".join(_validation_item(item, lang) for item in validation["missing"]))
        if validation.get("placeholders"):
            details.append(f"{t('validation_placeholders', lang)}: " + ", ".join(validation["placeholders"]))
        if validation.get("artifacts"):
            details.append(f"{t('validation_artifacts', lang)}: " + ", ".join(validation["artifacts"]))
        if details:
            st.caption(" · ".join(details))

    _render_letter(patient, final_preview, is_pkv, visit_date)

    return {"correct_clicked": correct_clicked, "approve_clicked": approve_clicked, "export_clicked": export_clicked}


def _render_letter(patient: dict, report: str, is_pkv: bool, visit_date: str) -> None:
    report_html = md_lib.markdown(_bold_report_headers(report), extensions=["extra", "nl2br", "sane_lists"])
    footer = (
        "Privatärztliche Abrechnung gemäß GOÄ. Eine detaillierte Kostenaufstellung wird separat bereitgestellt."
        if is_pkv
        else "Dieses Dokument wurde lokal mit MedLocal AI erstellt. Es ersetzt keine ärztliche Unterschrift."
    )

    st.markdown(
        f"""
<div class="ml-letter-shell">
  <div class="ml-letter-paper">
    <div class="ml-letter-head">
      <div>
        <div class="ml-practice-name">Praxis {escape(patient.get("doctor_name", "Dr. med. Muster"))}</div>
        <div class="ml-practice-meta">Fachärztliche Versorgung · Musterstraße 12 · 80331 München<br>
        Tel. +49 89 000000 · praxis@example.de</div>
      </div>
      <div class="ml-letter-meta">
        Behandlungsdatum: {escape(str(visit_date))}<br>
        Erstellt: {date.today().strftime("%d.%m.%Y")}<br>
        Dokumenttyp: Arztbrief
      </div>
    </div>
    <div class="ml-letter-title">Arztbrief</div>
    <div class="ml-patient-grid">
      <div><strong>Patient</strong><br>{escape(patient.get("name", "-"))}</div>
      <div><strong>Geburtsdatum</strong><br>{escape(patient.get("dob", "-"))}</div>
      <div><strong>Adresse</strong><br>{escape(patient.get("address", "-"))}</div>
      <div><strong>Versicherung</strong><br>{escape(patient.get("insurance_type", "-"))} · {escape(patient.get("insurance_provider", "-"))}</div>
    </div>
    {report_html}
    <div class="ml-signature">
      <div class="ml-signature-line">Ort, Datum</div>
      <div class="ml-signature-line">Ärztliche Unterschrift / Praxisstempel</div>
    </div>
    <div class="a4-footer">{escape(footer)}</div>
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )


def _bold_report_headers(report: str) -> str:
    lines = []
    for line in str(report or "").splitlines():
        stripped = line.strip()
        if stripped in REPORT_SECTION_HEADERS or stripped.startswith("An die zuständige Krankenversicherung"):
            lines.append(f"**{stripped}**")
        else:
            lines.append(line)
    return "\n".join(lines)
