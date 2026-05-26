import logging

import streamlit as st

from billing.billing_optimizer import (
    calculate_billing_potential,
    detect_clinical_actions,
    format_billing_suggestions,
    suggest_billing_codes,
)
from coding.icd10_search import format_icd10_suggestions, search_icd10gm
from i18n import t


def render_code_suggestions(query_text: str, insurance_type: str, specialty: str, lang: str) -> tuple[list[dict], list[dict]]:
    current_hash = st.session_state.get("current_generation_hash", "")
    if st.session_state.get("icd10_hash") == current_hash:
        icd = st.session_state.get("icd10_suggestions", [])
    else:
        icd_raw = search_icd10gm(query_text, language=lang, limit=5) if query_text.strip() else []
        icd = format_icd10_suggestions(icd_raw, language=lang)

    st.markdown(
        f"""
<div class="ml-card">
  <div class="ml-section-kicker">{t("source", lang)}: {t("icd_source", lang)}</div>
  <div class="ml-section-title">{t("icd_panel", lang)}</div>
        """,
        unsafe_allow_html=True,
    )
    if not icd:
        st.caption(t("icd_no_matches", lang))
    for item in icd:
        matched = ", ".join(item.get("matched_terms", []))
        st.markdown(
            f"""
<div class="ml-code-row">
  <div class="ml-code">{item["code"]}</div>
  <div class="ml-code-label">{item["label"]}<br><small>{matched}</small></div>
  <div class="ml-confidence">{item["confidence"]}</div>
</div>
            """,
            unsafe_allow_html=True,
        )
    st.caption(t("icd_disclaimer", lang))
    st.markdown("</div>", unsafe_allow_html=True)

    try:
        if st.session_state.get("billing_hash") == current_hash:
            billing = st.session_state.get("billing_suggestions", [])
            potential = st.session_state.get("billing_potential") or calculate_billing_potential([], language=lang)
            actions = st.session_state.get("detected_clinical_actions", [])
        else:
            billing_raw = suggest_billing_codes(query_text, insurance_type, specialty, language=lang, limit=8)
            billing = format_billing_suggestions(billing_raw, language=lang)
            potential = calculate_billing_potential(billing, language=lang)
            actions = detect_clinical_actions(query_text, language=lang)
    except Exception:
        logging.exception("Billing optimizer failed")
        st.warning(t("friendly_error", lang))
        return icd, []

    with st.expander(t("billing_optimizer", lang), expanded=True):
        st.caption(t("billing_support", lang))
        st.markdown(f"**{t('billing_actions', lang)}:** {', '.join(actions) if actions else '-'}")
        st.markdown(f"**{t('billing_suggestions', lang)}**")
        for item in billing:
            amount = calculate_billing_potential([item], language=lang)["display_total"]
            st.markdown(
                f"""
<div class="ml-billing-row">
  <div><strong>{item["system"]} {item["code"]}</strong> · {item["label"]}</div>
  <div><small>{t("billing_value", lang)}: {amount or t("unknown", lang)}</small></div>
  <div><small>{t("why", lang)}: {item["why"]}</small></div>
  <div><small>{t("documentation_requirements", lang)}: {"; ".join(item["documentation_requirements"])}</small></div>
  <div><small>{item.get("value_note", "")}</small></div>
  <div><small>{item["warning"]}</small></div>
</div>
                """,
                unsafe_allow_html=True,
            )
        if not billing:
            st.caption(t("billing_no_suggestions", lang))
            st.caption(t("billing_zero_evidence", lang))
        st.markdown(f"**{t('billing_potential_total', lang).format(amount=potential['display_total'])}**")
        st.caption(t("billing_value_disclaimer", lang))

    return icd, billing
