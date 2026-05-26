from datetime import datetime
import logging
import os
import time

import streamlit as st

from billing.billing_optimizer import (
    calculate_billing_potential,
    detect_clinical_actions,
    format_billing_suggestions,
    suggest_billing_codes,
)
from coding.icd10_search import format_icd10_suggestions, search_icd10gm
from components.code_suggestions import render_code_suggestions
from components.input_panel import render_input_panel, render_patient_sidebar
from components.output_panel import render_output_panel
from components.progress_indicator import run_generation_flow
from components.system_health import render_system_health
from exports.pdf_export import build_pdf_file_name, build_report_pdf_bytes, export_report_to_pdf
from generation.clinical_extractor import extract_clinical_sections
from generation.context_builder import build_generation_context
from generation.fallback_report import build_insurance_ready_fallback_report
from generation.input_builder import build_normalized_clinical_input
from generation.report_renderer import render_insurance_report
from generation.report_schema import build_report_object
from i18n import lang_code, t
from state.reset import DERIVED_GENERATION_KEYS, reset_generation_state
from storage.database import init_db, save_approved_report, update_report_pdf_path
from templates.prompts import build_system_prompt, build_user_prompt
from theme import apply_theme
from utils.input_hash import build_generation_input_hash
from utils.ollama_client import DEFAULT_MODEL, query_ollama
from utils.report_cleaning import clean_final_report_text
from utils.text_cleaning import clean_transcript_text
from utils.time_savings import estimate_manual_documentation_time
from validation.input_validator import validate_generation_input
from validation.final_report_guard import sanitize_and_validate_final_report
from validation.report_validator import contains_internal_prompt_artifacts, validate_report


APP_DEBUG = os.environ.get("APP_DEBUG", "").lower() == "true"


GKV_PROVIDERS = ["AOK", "Barmer", "DAK-Gesundheit", "TK (Techniker Krankenkasse)", "KKH", "IKK classic", "BKK VBU", "Knappschaft", "Sonstige GKV"]
PKV_PROVIDERS = ["Allianz Private KV", "AXA / DBV", "Barmenia", "Continentale", "DKV (Deutsche Krankenversicherung)", "Gothaer", "Hallesche", "Münchener Verein", "Signal Iduna", "Universa", "Württembergische", "Sonstige PKV"]


def initialize_state() -> None:
    defaults = {
        "original_transcript": "",
        "transcript_draft": "",
        "transcript_edit_mode": False,
        "approved_transcript": "",
        "transcript_status": "empty",
        "notes_text": "",
        "whisper_size": "base",
        "last_specialty": "Allgemeinmedizin",
        "last_tone": "short_concise",
        "tone_of_voice": "short_concise",
        "language": "de",
        "selected_language": "de",
        "transcription_started_at": 0,
        "transcription_duration_sec": 0,
        "current_generation_hash": "",
    }
    defaults.update(DERIVED_GENERATION_KEYS)
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value.copy() if isinstance(value, (list, dict)) else value


def render_header(lang: str) -> None:
    left, right = st.columns([1, 0.22])
    with right:
        selected = st.selectbox(t("language", lang), ["Deutsch", "English"], index=0 if lang == "de" else 1)
        st.session_state.selected_language = lang_code(selected)
        st.session_state.language = st.session_state.selected_language
    with left:
        st.markdown(
            f"""
<div class="ml-app-header">
  <div class="ml-brand">
    <div class="ml-logo">ML</div>
    <div>
      <div class="ml-title">MedLocal AI</div>
      <div class="ml-subtitle">{t("app_subtitle", lang)}</div>
    </div>
  </div>
  <div class="ml-status-pill">● {t("local_processing", lang)}</div>
</div>
            """,
            unsafe_allow_html=True,
        )


def show_friendly_error(message_key: str, lang: str, exc: Exception | None = None) -> None:
    if exc:
        logging.exception(message_key)
    st.error(f"{t(message_key, lang)}: {exc}" if APP_DEBUG and exc else t(message_key, lang))


def generation_hash_context(patient: dict, input_state: dict, insurance_type: str, lang: str, transcript: str, notes: str) -> dict:
    return {
        "patient": patient,
        "insurance_type": insurance_type,
        "specialty": input_state["specialty"],
        "tone": input_state["tone"],
        "language": lang,
        "transcript": transcript,
        "clinical_notes": notes,
    }


def total_ai_workflow_duration() -> int:
    total = sum(
        float(st.session_state.get(key, 0) or 0)
        for key in ["transcription_duration_sec", "generation_duration_sec", "coding_duration_sec", "billing_duration_sec", "pdf_export_duration_sec"]
    )
    st.session_state.total_ai_workflow_duration_sec = int(round(total))
    return st.session_state.total_ai_workflow_duration_sec


def recalculate_time_savings(input_state: dict, generated_report: str, includes_icd: bool, includes_billing: bool, input_hash: str) -> None:
    result = estimate_manual_documentation_time(
        transcript_text=st.session_state.get("approved_transcript") or st.session_state.get("transcript_draft", ""),
        clinical_notes=input_state.get("clinical_notes", ""),
        generated_report=generated_report,
        specialty=input_state.get("specialty", "Allgemeinmedizin"),
        includes_icd=includes_icd,
        includes_billing=includes_billing,
        ai_workflow_sec=total_ai_workflow_duration(),
        language=st.session_state.get("selected_language", "de"),
    )
    st.session_state.time_manual_estimate_sec = result["manual_estimate_sec"]
    st.session_state.time_ai_workflow_sec = result["ai_workflow_sec"]
    st.session_state.time_saved_sec = result["estimated_saved_sec"]
    st.session_state.time_savings_assumptions = result["assumptions"]
    st.session_state.time_savings_hash = input_hash
    st.session_state.time_savings_status = "ready"


def validate_current_report(patient: dict, lang: str, report_text: str) -> dict:
    result = validate_report(report_text, patient, lang)
    st.session_state.report_validation_result = result
    return result


def _report_is_bad(report_text: str | None) -> bool:
    if contains_internal_prompt_artifacts(report_text):
        return True
    text = report_text or ""
    return len(text.split()) < 45


def build_final_insurance_report(
    clinical_input: str,
    raw_model_output: str,
    patient: dict,
    specialty: str,
    insurance_type: str,
    lang: str,
) -> str:
    sections = extract_clinical_sections(clinical_input, patient, language=lang, model_output=raw_model_output)
    report_object = build_report_object(patient, specialty, insurance_type, sections, language=lang)
    rendered = render_insurance_report(report_object, language=lang)
    cleaned, warnings = sanitize_and_validate_final_report(rendered, language=lang)
    if warnings:
        st.session_state.report_guard_warnings = warnings
    if warnings and any("remains" in warning.lower() for warning in warnings):
        rendered = render_insurance_report(report_object, language=lang)
        cleaned, warnings = sanitize_and_validate_final_report(rendered, language=lang)
        st.session_state.report_guard_warnings = warnings
    return cleaned


def build_report_data(patient: dict, input_state: dict, insurance_type: str, lang: str, context_text: str, final_report: str) -> dict:
    insurer = patient.get("insurance_provider", "")
    return {
        "patient_name": patient.get("name", ""),
        "patient_date_of_birth": patient.get("dob", ""),
        "patient_insurance": f'{patient.get("insurance_type", "")} · {insurer}',
        "treatment_date": patient.get("visit_date", ""),
        "doctor_name": patient.get("doctor_name", ""),
        "specialty": input_state["specialty"],
        "original_transcript": st.session_state.get("original_transcript", ""),
        "corrected_transcript": st.session_state.get("transcript_draft", ""),
        "generated_report": st.session_state.get("generated_report", ""),
        "final_report": final_report,
        "icd10_codes": st.session_state.get("icd10_suggestions", []),
        "goz_codes": [item for item in st.session_state.get("billing_suggestions", []) if item["system"] == "GOÄ"],
        "billing_codes": st.session_state.get("billing_suggestions", []),
        "model_name": DEFAULT_MODEL,
        "language": lang,
        "recipient": f"An die zuständige Krankenversicherung ({insurer})" if insurer else "An die zuständige Krankenversicherung",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "approved_at": datetime.now().isoformat(timespec="seconds"),
        "status": "Approved",
    }


def export_current_report(patient: dict, input_state: dict, insurance_type: str, lang: str, context_text: str) -> None:
    final_report = (st.session_state.get("corrected_report") or st.session_state.get("final_report") or st.session_state.get("generated_report") or "").strip()
    final_report, guard_warnings = sanitize_and_validate_final_report(final_report, language=lang)
    st.session_state.report_guard_warnings = guard_warnings
    current_hash = st.session_state.get("current_generation_hash", "")
    if not final_report or st.session_state.get("generated_report_hash") != current_hash:
        st.warning(t("no_report_export_warning", lang))
        return

    try:
        report_data = build_report_data(patient, input_state, insurance_type, lang, context_text, final_report)
        start = time.perf_counter()
        pdf_bytes = build_report_pdf_bytes(report_data)
        st.session_state.pdf_export_duration_sec = time.perf_counter() - start
        st.session_state.exported_pdf_bytes = pdf_bytes
        st.session_state.exported_pdf_file_name = build_pdf_file_name(report_data)
        st.session_state.exported_pdf_hash = current_hash
        st.session_state.last_exported_report_hash = current_hash
        st.session_state.pdf_download_ready = True
        st.session_state.success_message = t("pdf_export_success", lang)
        recalculate_time_savings(input_state, final_report, includes_icd=True, includes_billing=bool(st.session_state.get("billing_suggestions")), input_hash=current_hash)
        st.success(t("pdf_export_success", lang))
    except Exception as exc:
        show_friendly_error("pdf_create_failed", lang, exc)


def approve_report(patient: dict, input_state: dict, insurance_type: str, lang: str, context_text: str) -> None:
    final_report = (st.session_state.get("corrected_report") or st.session_state.get("generated_report") or "").strip()
    final_report, guard_warnings = sanitize_and_validate_final_report(final_report, language=lang)
    st.session_state.report_guard_warnings = guard_warnings
    current_hash = st.session_state.get("current_generation_hash", "")
    if not final_report or st.session_state.get("generated_report_hash") != current_hash:
        st.error(t("empty_report_error", lang))
        return
    try:
        report_data = build_report_data(patient, input_state, insurance_type, lang, context_text, final_report)
        report_id = save_approved_report(report_data)
        start = time.perf_counter()
        pdf_path = export_report_to_pdf(report_data)
        st.session_state.pdf_export_duration_sec = time.perf_counter() - start
        update_report_pdf_path(report_id, pdf_path)
        st.session_state.final_report = final_report
        st.session_state.approved_report_id = report_id
        st.session_state.approved_pdf_path = str(pdf_path)
        st.session_state.approved_at = datetime.now().isoformat(timespec="seconds")
        st.session_state.approval_status = "Approved"
        st.session_state.saved_to_database = True
        st.session_state.report_status = "Approved"
        st.session_state.exported_pdf_bytes = pdf_path.read_bytes()
        st.session_state.exported_pdf_file_name = pdf_path.name
        st.session_state.exported_pdf_hash = current_hash
        st.session_state.pdf_download_ready = True
        st.session_state.success_message = t("approval_success", lang)
        recalculate_time_savings(input_state, final_report, includes_icd=True, includes_billing=bool(st.session_state.get("billing_suggestions")), input_hash=current_hash)
        st.success(t("approval_success", lang))
    except Exception as exc:
        show_friendly_error("approval_failed", lang, exc)


def main() -> None:
    st.set_page_config(page_title="MedLocal AI", page_icon="🏥", layout="wide", initial_sidebar_state="expanded")
    apply_theme()
    initialize_state()
    init_db()
    lang = st.session_state.get("selected_language", st.session_state.get("language", "de"))
    st.session_state.language = lang

    patient, is_pkv, insurance_type, visit_date = render_patient_sidebar(GKV_PROVIDERS, PKV_PROVIDERS, lang)
    render_header(lang)
    lang = st.session_state.get("selected_language", st.session_state.get("language", lang))

    left_col, right_col = st.columns([0.6, 0.4], gap="medium")

    with left_col:
        st.markdown('<div class="ml-panel">', unsafe_allow_html=True)
        input_state = render_input_panel(lang)
        st.session_state.last_specialty = input_state["specialty"]
        st.session_state.last_tone = input_state["tone"]

        transcript_for_generation = clean_transcript_text(input_state["approved_transcript"] or input_state["transcript_draft"])
        additional_notes = input_state["clinical_notes"]

        if input_state["generate"]:
            valid, message = validate_generation_input(transcript_for_generation, additional_notes, lang)
            if not valid:
                st.warning(message)
            else:
                voice_input = bool(transcript_for_generation.strip())
                clinical_input_for_generation = (
                    build_normalized_clinical_input(transcript_for_generation, "", additional_notes)
                    if voice_input
                    else additional_notes
                )
                context_transcript = "" if voice_input else transcript_for_generation
                context_notes = clinical_input_for_generation
                input_hash = build_generation_input_hash(generation_hash_context(patient, input_state, insurance_type, lang, transcript_for_generation, additional_notes))
                reset_generation_state(st.session_state)
                st.session_state.current_generation_hash = input_hash
                st.session_state.generation_stage = "running"
                st.session_state.time_savings_status = "calculating"

                coding_context = clinical_input_for_generation.strip()
                try:
                    coding_start = time.perf_counter()
                    icd_for_prompt = format_icd10_suggestions(search_icd10gm(coding_context, language=lang, limit=5), language=lang)
                    st.session_state.coding_duration_sec = time.perf_counter() - coding_start
                    st.session_state.icd10_suggestions = icd_for_prompt
                    st.session_state.icd10_search_query = coding_context
                    st.session_state.icd10_hash = input_hash

                    billing_start = time.perf_counter()
                    billing_raw = suggest_billing_codes(coding_context, insurance_type, input_state["specialty"], language=lang, limit=8)
                    billing_for_prompt = format_billing_suggestions(billing_raw, language=lang)
                    st.session_state.billing_duration_sec = time.perf_counter() - billing_start
                    st.session_state.billing_suggestions = billing_for_prompt
                    st.session_state.billing_potential = calculate_billing_potential(billing_for_prompt, language=lang)
                    st.session_state.billing_total_min = st.session_state.billing_potential.get("total_min", 0)
                    st.session_state.billing_total_max = st.session_state.billing_potential.get("total_max", 0)
                    st.session_state.detected_clinical_actions = detect_clinical_actions(coding_context, language=lang)
                    st.session_state.billing_hash = input_hash

                    system_prompt = (
                        "Extract clinical facts from German medical notes. Return strict JSON only. "
                        "Do not write a letter, markdown, HTML, tables, headings, or explanations."
                    )
                    user_prompt = f"""
Return only this JSON object:
{{
  "reason_for_visit": "",
  "history": "",
  "findings": "",
  "assessment": "",
  "diagnoses": [],
  "services_performed": [],
  "therapy_recommendation": "",
  "medical_justification": "",
  "billing_notes": ""
}}

Clinical input:
{clinical_input_for_generation}
"""

                    def generate_report() -> str:
                        try:
                            return query_ollama(DEFAULT_MODEL, system_prompt, user_prompt)
                        except Exception:
                            return ""

                    st.session_state.generation_started_at = time.perf_counter()
                    raw_report = run_generation_flow(generate_report, lang)
                    st.session_state.generation_duration_sec = time.perf_counter() - st.session_state.generation_started_at
                    st.session_state.generated_report = build_final_insurance_report(
                        clinical_input_for_generation,
                        raw_report,
                        patient,
                        input_state["specialty"],
                        insurance_type,
                        lang,
                    )
                    st.session_state.generated_report_source = "voice" if voice_input else "text"
                    st.session_state.generated_report_hash = input_hash
                    validate_current_report(patient, lang, st.session_state.generated_report or "")
                    recalculate_time_savings(input_state, st.session_state.generated_report or "", includes_icd=bool(icd_for_prompt), includes_billing=bool(billing_for_prompt), input_hash=input_hash)
                    st.session_state.report_status = "Generated"
                    st.session_state.generation_stage = ""
                    st.session_state.time_savings_status = "ready"
                    st.rerun()
                except Exception as exc:
                    st.session_state.last_generation_error = str(exc)
                    st.session_state.time_savings_status = "error"
                    show_friendly_error("friendly_error", lang, exc)
                finally:
                    st.session_state.generation_stage = ""
                    if st.session_state.get("time_savings_status") == "calculating":
                        st.session_state.time_savings_status = "ready"

        context_text = "\n".join([
            st.session_state.get("approved_transcript", ""),
            st.session_state.get("transcript_draft", ""),
            additional_notes,
            st.session_state.get("generated_report") or "",
        ])
        render_system_health(lang)
        st.markdown("</div>", unsafe_allow_html=True)

    with right_col:
        st.markdown('<div class="ml-panel">', unsafe_allow_html=True)
        current_hash = st.session_state.get("current_generation_hash", "")
        visible_report = st.session_state.get("generated_report") if st.session_state.get("generated_report_hash") == current_hash else None
        actions = render_output_panel(patient, visible_report, is_pkv, visit_date, lang)
        render_code_suggestions(context_text if visible_report else "", insurance_type, input_state["specialty"], lang)
        if st.session_state.get("corrected_report") and visible_report:
            recalculate_time_savings(input_state, st.session_state.get("corrected_report", ""), includes_icd=True, includes_billing=bool(st.session_state.get("billing_suggestions")), input_hash=current_hash)
        if actions.get("approve_clicked"):
            approve_report(patient, input_state, insurance_type, lang, context_text)
            st.rerun()
        if actions.get("export_clicked"):
            export_current_report(patient, input_state, insurance_type, lang, context_text)
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
