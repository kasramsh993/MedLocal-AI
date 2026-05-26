# MedLocal AI

Local German medical documentation assistant for generating structured Arztbrief drafts with local transcription and local Ollama models.

## Ubuntu Setup

Tested target: Ubuntu 22.04/24.04 with Python 3.11 or 3.12.

### 1. Install system packages

```bash
sudo apt update
sudo apt install -y \
  python3 python3-venv python3-dev build-essential \
  ffmpeg portaudio19-dev libsndfile1
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

If Whisper/Torch installation is slow, install a CPU-only Torch build first, then rerun the requirements install:

```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
```

### 4. Install and start Ollama

Follow the official Ollama Linux installation instructions, then run:

```bash
ollama serve
ollama pull qwen2.5:0.5b
```

For larger models, ensure the machine has enough RAM.

### 5. Run the app

```bash
streamlit run app.py
```

Open the printed localhost URL, usually:

```text
http://localhost:8501
```

## Notes For Production

- Use only synthetic data for demos unless the deployment is legally and technically prepared for patient data.
- Approved reports are stored in `data/medlocal.db`.
- Approved PDFs are exported to `exports/reports/`.
- The physician remains responsible for review, correction, approval, and signature.

## Manual Test Checklist

### Transcript workflow

1. Record audio.
2. Confirm the generated transcript appears under "Generated Transcript".
3. Confirm "Additional Clinical Notes" remains unchanged.
4. Click "Edit Transcript", modify text, then save.
5. Click "Approve Transcript".
6. Generate the report and confirm the approved transcript is used.

### ICD-10-GM local search

1. Enter notes such as `Thoraxdruck, Hypertonie, EKG`.
2. Confirm ICD suggestions appear from "Local ICD-10-GM search".
3. Confirm displayed ICD codes exist in `data/icd10gm/icd10gm_mock.json`.

### Billing Optimizer

1. Select GKV and enter clinical actions such as Beratung, EKG, Labor.
2. Confirm EBM suggestions appear.
3. Confirm each suggestion shows an estimated EUR range and cautious value note.
4. Confirm the total estimated additional billing potential appears.
5. Select Privat (PKV) or Selbstzahler.
6. Confirm GOÄ suggestions appear with estimated EUR values.
7. Confirm documentation requirements and disclaimer are visible.

### Language switching

1. Use the language dropdown in the top header.
2. Switch between Deutsch and English.
3. Confirm major labels, buttons, status messages, ICD disclaimer, and billing disclaimer change language.
4. In German mode, confirm progress messages and system-health labels do not show English UI text.

### Tone dropdown

1. Confirm "Tone of Voice" / "Tonfall" is a dropdown, not radio buttons.
2. Select "Detailed" / "Detailliert".
3. Switch language and confirm the displayed label changes while the selected tone remains equivalent.

### PDF export

1. Generate or correct an Arztbrief.
2. Click "Export PDF" / "PDF exportieren".
3. Confirm the PDF download button appears.
4. Confirm the file is saved under `exports/reports/`.
5. Confirm there is no `col_approve` error and no raw traceback.

### Arztbrief quality validation

Run the demo validation cases:

```bash
python scripts/validate_demo_reports.py
```

The script checks three realistic demo cases for placeholders, required sections, metadata usage, local ICD suggestions, and insurance-specific billing systems.

### Dynamic time-saved estimate

1. Open the app before generation and confirm it says the estimate appears after generation.
2. Generate a short report and note the dynamic saved-time value.
3. Generate a longer report and confirm the manual estimate increases.
4. If a local model is slow, confirm the measured AI workflow time increases and the saved-time value decreases.
5. Switch between Deutsch and English and confirm the time-saved label and explanation are translated.

Run the lightweight validation script:

```bash
python scripts/validate_time_savings.py
```
