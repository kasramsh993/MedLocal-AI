import time
from collections.abc import Callable

import streamlit as st

from i18n import t


STAGE_KEYS = [
    "progress_reading_transcript",
    "progress_structuring_context",
    "progress_generating_letter",
    "progress_searching_codes",
    "progress_analyzing_billing",
]


def run_generation_flow(generate_fn: Callable[[], str], lang: str = "de") -> str:
    progress = st.progress(0)
    label = st.empty()
    result = ""

    for index, stage_key in enumerate(STAGE_KEYS):
        label.markdown(f'<div class="ml-progress-stage">{t(stage_key, lang)}</div>', unsafe_allow_html=True)
        progress.progress(int((index / len(STAGE_KEYS)) * 100))
        if stage_key == "progress_generating_letter":
            result = generate_fn()
        else:
            time.sleep(0.18)

    progress.progress(100)
    label.markdown(f'<div class="ml-progress-stage">{t("progress_output_ready", lang)}</div>', unsafe_allow_html=True)
    time.sleep(0.1)
    return result
