# Resume Enhancer (Streamlit)

This small Streamlit app provides a local, heuristic resume enhancer and preview. It is intentionally simple and runs locally without external APIs.

Files
- `app.py` - Streamlit app
- `enhancer.py` - Local enhancement logic
- `requirements.txt` - Python dependencies

Run (PowerShell):

```powershell
python -m pip install -r requirements.txt
python app.py
```

Then open the Streamlit URL shown in the terminal.

Notes / next steps
- Replace heuristic enhancer with an LLM-backed enhancer if desired.
- Add file-type support (docx, pdf) and more robust parsing.

Venv and file-type notes
- We recommend creating a Python 3.11 venv and installing requirements there to avoid compilation issues with some binary deps on newer Python versions.
- After creating/activating your venv, run:

```powershell
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Supported upload types: `.txt`, `.pdf`, `.docx`. PDFs are parsed with `PyPDF2` and DOCX with `python-docx`.
