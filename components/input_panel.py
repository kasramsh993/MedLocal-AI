from datetime import date
import time

import streamlit as st
from streamlit_mic_recorder import mic_recorder

from i18n import t
from state.reset import reset_generation_state
from utils.text_cleaning import clean_transcript_text
from utils.time_savings import format_duration
from utils.whisper_client import transcribe_audio


SPECIALTIES = [
    "Allgemeinmedizin",
    "Urologie",
    "Zahnmedizin",
    "Kardiologie",
    "Dermatologie",
    "Orthopädie",
]

TONE_VALUES = ["short_concise", "detailed", "patient_friendly"]

SPECIALTY_ICONS = {
    "Allgemeinmedizin": "AM",
    "Urologie": "UR",
    "Zahnmedizin": "ZM",
    "Kardiologie": "KA",
    "Dermatologie": "DE",
    "Orthopädie": "OR",
}


def tone_label(value: str, lang: str) -> str:
    return {
        "short_concise": t("tone_short_concise", lang),
        "detailed": t("tone_detailed", lang),
        "patient_friendly": t("tone_patient_friendly", lang),
    }.get(value, t("tone_short_concise", lang))


def _reset_time_savings() -> None:
    for key in [
        "time_manual_estimate_sec",
        "time_ai_workflow_sec",
        "time_saved_sec",
        "time_savings_assumptions",
        "transcription_duration_sec",
        "generation_duration_sec",
        "coding_duration_sec",
        "billing_duration_sec",
        "pdf_export_duration_sec",
        "total_ai_workflow_duration_sec",
    ]:
        st.session_state[key] = 0 if key.endswith("_sec") else []


def render_patient_sidebar(gkv_providers: list[str], pkv_providers: list[str], lang: str) -> tuple[dict, bool, str, str]:
    with st.sidebar:
        st.markdown(f"### {t('patient_practice', lang)}")
        name = st.text_input(t("name", lang), placeholder="Max Mustermann")
        dob = st.date_input(t("date_of_birth", lang), value=date(1980, 1, 1), min_value=date(1900, 1, 1), max_value=date.today())
        address = st.text_input(t("address", lang), placeholder="Musterstr. 1, 80331 München")
        doctor_name = st.text_input(t("doctor_name", lang), placeholder="Dr. med. Muster")
        visit_date = st.date_input(t("treatment_date", lang), value=date.today())

        st.markdown("---")
        insurance_type = st.selectbox(t("insurance_type", lang), ["GKV", "Privat (PKV)", "Selbstzahler"])
        is_pkv = insurance_type in {"Privat (PKV)", "Selbstzahler"}
        if is_pkv:
            insurance_provider = st.selectbox(t("pkv_provider", lang), pkv_providers)
            insurance_number = st.text_input(t("policy_number", lang), placeholder="PKV-2026-XXXXX")
        else:
            insurance_provider = st.selectbox(t("gkv_provider", lang), gkv_providers)
            insurance_number = st.text_input(t("insurance_number", lang), placeholder="A123456789")

        st.markdown("---")
        st.markdown(f'<div class="ml-status-pill">● {t("local_processing", lang)}</div>', unsafe_allow_html=True)

    patient = {
        "name": name or "-",
        "dob": str(dob),
        "address": address or "-",
        "visit_date": str(visit_date),
        "insurance_type": insurance_type,
        "insurance_provider": insurance_provider,
        "insurance_number": insurance_number,
        "doctor_name": doctor_name or "Dr. med. Muster",
    }
    return patient, is_pkv, insurance_type, str(visit_date)


def render_input_panel(lang: str) -> dict:
    st.markdown(
        f"""
<div class="ml-workflow-header">
  <div>
    <div class="ml-section-kicker">{t("clinical_workflow", lang)}</div>
    <div class="ml-section-title">{t("input_transcript_notes", lang)}</div>
    <div class="ml-section-note">{t("workflow_note", lang)}</div>
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )

    top_a, top_b = st.columns([1.05, 1.45], gap="small")
    with top_a:
        specialty = st.selectbox(t("specialty", lang), SPECIALTIES)
        st.markdown(f'<div class="ml-badge">{SPECIALTY_ICONS.get(specialty, "MD")} · {specialty}</div>', unsafe_allow_html=True)
    with top_b:
        current_tone = st.session_state.get("tone_of_voice", "short_concise")
        tone = st.selectbox(
            t("tone", lang),
            TONE_VALUES,
            index=TONE_VALUES.index(current_tone) if current_tone in TONE_VALUES else 0,
            format_func=lambda value: tone_label(value, lang),
        )
        st.session_state.tone_of_voice = tone
    with st.expander(t("audio_settings", lang), expanded=False):
        st.session_state.whisper_size = st.selectbox("Whisper", ["base", "small", "tiny", "medium"], index=0)

    st.markdown(f'<div class="ml-mini-label">{t("audio_recording", lang)}</div>', unsafe_allow_html=True)
    audio = mic_recorder(
        start_prompt=t("record", lang),
        stop_prompt=t("stop", lang),
        just_once=True,
        use_container_width=True,
        key="mic_recorder",
    )

    if audio is not None:
        try:
            st.session_state.transcription_started_at = time.perf_counter()
            with st.status(t("transcribing", lang), expanded=False):
                transcribed = clean_transcript_text(transcribe_audio(audio["bytes"], st.session_state.get("whisper_size", "base")))
            st.session_state.transcription_duration_sec = time.perf_counter() - st.session_state.transcription_started_at
            st.session_state.original_transcript = transcribed
            st.session_state.transcript_draft = transcribed
            st.session_state.transcript_edit_mode = False
            st.session_state.approved_transcript = ""
            st.session_state.transcript_status = "draft"
            reset_generation_state(st.session_state)
            st.session_state.current_generation_hash = ""
            st.session_state.transcription_duration_sec = time.perf_counter() - st.session_state.transcription_started_at
            st.toast(t("dictation_added", lang))
            st.rerun()
        except Exception as exc:
            st.error(f"Transkriptionsfehler: {exc}")

    _render_transcript_workflow(lang)

    clinical_notes = st.text_area(
        t("additional_notes", lang),
        placeholder=t("additional_notes_placeholder", lang),
        key="notes_text",
        height=135,
    )

    transcript_for_generation = st.session_state.get("approved_transcript", "")
    button_col, meta_col = st.columns([1.2, 1], gap="small")
    with button_col:
        generate = st.button(t("generate_report", lang), use_container_width=True, type="primary")
        if generate:
            reset_generation_state(st.session_state)
            st.session_state.current_generation_hash = ""
            st.session_state.generation_stage = "running"
    with meta_col:
        _render_time_saved_widget(lang)

    return {
        "specialty": specialty,
        "tone": tone,
        "clinical_notes": clinical_notes,
        "approved_transcript": transcript_for_generation,
        "transcript_draft": st.session_state.get("transcript_draft", ""),
        "transcript_status": st.session_state.get("transcript_status", "empty"),
        "generate": generate,
    }


def _render_transcript_workflow(lang: str) -> None:
    status = st.session_state.get("transcript_status", "empty")
    status_label = t("transcript_approved", lang) if status == "approved" else t("transcript_draft", lang)
    st.markdown(f'<div class="ml-mini-label">{t("generated_transcript", lang)} · {status_label}</div>', unsafe_allow_html=True)

    transcript = st.session_state.get("transcript_draft", "")
    if st.session_state.get("transcript_edit_mode") and transcript:
        edited = st.text_area(
            t("generated_transcript", lang),
            value=transcript,
            height=120,
            key="transcript_edit_value",
            label_visibility="collapsed",
        )
        st.session_state.transcript_draft = edited
    else:
        body = clean_transcript_text(transcript) or t("transcript_placeholder", lang)
        st.markdown(f'<div class="ml-transcript-card">{body}</div>', unsafe_allow_html=True)

    col_edit, col_approve = st.columns(2, gap="small")
    with col_edit:
        edit_label = t("save_transcript_edits", lang) if st.session_state.get("transcript_edit_mode") else t("edit_transcript", lang)
        if st.button(edit_label, use_container_width=True, disabled=not bool(transcript)):
            if st.session_state.get("transcript_edit_mode"):
                st.session_state.transcript_edit_mode = False
                st.session_state.transcript_draft = clean_transcript_text(st.session_state.get("transcript_draft", ""))
                st.session_state.transcript_status = "draft"
            else:
                st.session_state.transcript_edit_mode = True
            st.rerun()
    with col_approve:
        if st.button(t("approve_transcript", lang), use_container_width=True, disabled=not bool(st.session_state.get("transcript_draft", "").strip())):
            st.session_state.transcript_draft = clean_transcript_text(st.session_state.get("transcript_draft", ""))
            st.session_state.approved_transcript = st.session_state.transcript_draft
            st.session_state.transcript_edit_mode = False
            st.session_state.transcript_status = "approved"
            st.success(t("transcript_approved", lang))
            st.rerun()


def _render_time_saved_widget(lang: str) -> None:
    saved = st.session_state.get("time_saved_sec", 0)
    manual = st.session_state.get("time_manual_estimate_sec", 0)
    ai = st.session_state.get("time_ai_workflow_sec", 0)
    assumptions = st.session_state.get("time_savings_assumptions", [])

    if st.session_state.get("time_savings_status") == "calculating":
        st.markdown(f'<div class="ml-time-saved">{t("time_saved_recalculating", lang)}</div>', unsafe_allow_html=True)
        return
    if not saved and not st.session_state.get("generated_report"):
        st.markdown(f'<div class="ml-time-saved">{t("time_saved_pending", lang)}</div>', unsafe_allow_html=True)
        return

    st.markdown(
        f'<div class="ml-time-saved">{t("time_saved", lang)}: {format_duration(saved, lang)}</div>',
        unsafe_allow_html=True,
    )
    st.caption(t("time_saved_detail", lang).format(manual=format_duration(manual, lang), ai=format_duration(ai, lang)))
    with st.expander(t("time_saved_method", lang), expanded=False):
        st.write(f"{t('time_saved_manual', lang)}: {format_duration(manual, lang)}")
        st.write(f"{t('time_saved_ai', lang)}: {format_duration(ai, lang)}")
        st.write(f"{t('time_saved_result', lang)}: {format_duration(saved, lang)}")
        for assumption in assumptions:
            st.caption(f"- {assumption}")
        st.caption(t("time_saved_disclaimer", lang))
