import ctypes

import streamlit as st

from i18n import t


def _health_values() -> tuple[str, str]:
    try:
        import psutil

        return f"{psutil.cpu_percent(interval=0.1):.0f}%", f"{psutil.virtual_memory().percent:.0f}%"
    except Exception:
        try:
            class MEMORYSTATUSEX(ctypes.Structure):
                _fields_ = [
                    ("dwLength", ctypes.c_ulong),
                    ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong),
                    ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong),
                    ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong),
                    ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
                ]

            status = MEMORYSTATUSEX()
            status.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status))
            return "Lokal", f"{status.dwMemoryLoad}%"
        except Exception:
            return "Lokal", "OK"


def render_system_health(lang: str = "de") -> None:
    cpu, ram = _health_values()
    st.markdown(
        f"""
<div class="ml-card">
  <div class="ml-section-kicker">{t("system_health", lang)}</div>
  <div class="ml-section-title">{t("local_processing", lang)}</div>
  <div class="ml-status-pill">● {t("local_processing", lang)}</div>
  <div style="height:0.85rem"></div>
  <div class="ml-health-grid">
    <div>
      <div class="ml-mini-label">{t("cpu", lang)}</div>
      <div class="ml-health-value">{cpu}</div>
    </div>
    <div>
      <div class="ml-mini-label">{t("ram", lang)}</div>
      <div class="ml-health-value">{ram}</div>
    </div>
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )
