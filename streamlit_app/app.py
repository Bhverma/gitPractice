import streamlit as st
from enhancer import enhance_resume, extract_text_from_bytes
import os
import io
import base64

st.set_page_config(page_title="Resume Enhancer", layout="centered")

st.title("Resume Enhancer")

st.markdown("Upload your resume (TXT, PDF, or DOCX) or paste text and get an enhanced preview.")

# Preview display height (user-adjustable) to enable scrollbars
preview_height = st.sidebar.slider('Preview height (px)', min_value=200, max_value=1400, value=600, step=50)

uploaded_file = st.file_uploader("Upload a resume file", type=["txt", "pdf", "docx"], help="Upload .txt, .pdf or .docx files")

# keep uploaded bytes for potential preview (PDF)
uploaded_bytes = None
input_text = ""
detected_name = None
plain_extracted_text = ""
if uploaded_file is not None:
    detected_name = uploaded_file.name
    # read bytes and try to extract text according to file type
    raw = uploaded_file.read()
    uploaded_bytes = raw
    try:
        input_text = extract_text_from_bytes(raw, detected_name)
    except Exception as e:
        st.error(f"Failed to parse uploaded file: {e}")
        input_text = ""
    # keep raw text for plain display
    plain_extracted_text = input_text
else:
    input_text = st.text_area("Or paste your resume here", height=300)
    # when user pastes text, also set plain_extracted_text
    plain_extracted_text = input_text

# If the uploaded file was a PDF, offer an inline preview immediately after upload
if detected_name and detected_name.lower().endswith('.pdf') and uploaded_bytes:
    if st.checkbox("Preview uploaded PDF", value=False, key="preview_pdf"):
        try:
            import base64
            pdf_base64 = base64.b64encode(uploaded_bytes).decode('utf-8')

            # Offer a download button (reliable). Also render with object/embed fallback.
            st.download_button("Download uploaded PDF", uploaded_bytes, file_name=detected_name, mime='application/pdf')

            pdf_display = f'''
            <object data="data:application/pdf;base64,{pdf_base64}" type="application/pdf" width="100%" height="{preview_height}">
                <embed src="data:application/pdf;base64,{pdf_base64}" type="application/pdf" width="100%" height="{preview_height}" />
                <p>This browser does not support inline PDFs. <a href="data:application/pdf;base64,{pdf_base64}" target="_blank" rel="noreferrer">Open the PDF in a new tab</a> or download it.</p>
            </object>
            '''

            st.components.v1.html(pdf_display, height=preview_height + 50)
        except Exception as e:
            st.error(f"Could not render PDF preview: {e}")

# ---------- New: formatted text preview (preserve font and size when possible) ----------
def docx_bytes_to_html(docx_bytes: bytes) -> str:
    """Convert DOCX bytes to simple HTML preserving run font and size where available."""
    try:
        from docx import Document
    except Exception:
        raise RuntimeError("python-docx is required to render DOCX with formatting")

    doc = Document(io.BytesIO(docx_bytes))
    parts = ["<div>"]
    for para in doc.paragraphs:
        runs_html = []
        for run in para.runs:
            text = (run.text or "").replace("\n", "<br/>")
            styles = []
            font = run.font
            # font name
            if font and getattr(font, 'name', None):
                styles.append(f"font-family: '{font.name}'")
            # font size (python-docx uses Pt objects)
            if font and getattr(font, 'size', None):
                try:
                    size_pt = font.size.pt
                    styles.append(f"font-size: {size_pt}pt")
                except Exception:
                    pass
            # bold/italic/underline handled with tags
            open_tags = []
            close_tags = []
            if run.bold:
                open_tags.append('<strong>')
                close_tags.insert(0, '</strong>')
            if run.italic:
                open_tags.append('<em>')
                close_tags.insert(0, '</em>')
            if run.underline:
                open_tags.append('<u>')
                close_tags.insert(0, '</u>')

            style_attr = f" style=\"{'; '.join(styles)}\"" if styles else ''
            span = f"{''.join(open_tags)}<span{style_attr}>{text}</span>{''.join(close_tags)}"
            runs_html.append(span)
        parts.append(f"<p>{''.join(runs_html)}</p>")
    parts.append("</div>")
    return '\n'.join(parts)

def pdf_bytes_to_html(pdf_bytes: bytes) -> str:
    """Try to extract text with font and size info from PDF using PyMuPDF (fitz).
    If PyMuPDF is not available, raise RuntimeError.
    """
    try:
        import fitz
    except Exception:
        raise RuntimeError("PyMuPDF (fitz) is required to extract PDF formatting")

    doc = fitz.open(stream=pdf_bytes, filetype='pdf')
    parts = ["<div>"]
    for page in doc:
        page_dict = page.get_text('dict')
        # iterate blocks -> lines -> spans
        for block in page_dict.get('blocks', []):
            if block.get('type') != 0:
                continue
            for line in block.get('lines', []):
                line_html = []
                for span in line.get('spans', []):
                    text = span.get('text', '').replace('\n', '<br/>')
                    font = span.get('font', '')
                    size = span.get('size', None)
                    styles = []
                    if font:
                        styles.append(f"font-family: '{font}'")
                    if size:
                        styles.append(f"font-size: {size}pt")
                    style_attr = f" style=\"{'; '.join(styles)}\"" if styles else ''
                    line_html.append(f"<span{style_attr}>{text}</span>")
                parts.append(f"<p>{''.join(line_html)}</p>")
    parts.append("</div>")
    return '\n'.join(parts)

def show_formatted_preview(file_bytes: bytes, filename: str):
    """Render a formatted (HTML) preview when possible. Falls back to plain textarea.
    This function tries DOCX first, then PDF, then plain text.
    """
    ext = (filename or '').lower()
    html = None
    err = None
    if ext.endswith('.docx'):
        try:
            html = docx_bytes_to_html(file_bytes)
        except Exception as e:
            err = str(e)
    elif ext.endswith('.pdf'):
        try:
            html = pdf_bytes_to_html(file_bytes)
        except Exception as e:
            err = str(e)
    else:
        # for txt and other types, display plain text
        html = '<pre style="white-space:pre-wrap; font-family: monospace;">' + (file_bytes.decode('utf-8', errors='replace')) + '</pre>'

    if html:
        # Wrap in an editable container if requested
        editable = st.checkbox('Make editable (contenteditable)', value=False, key='editable_formatted')
        if editable:
            # put the HTML into a contenteditable div
            wrapper = f'<div contenteditable="true" style="border:1px solid #ddd; padding:12px; overflow:auto; height:{preview_height}px;">{html}</div>'
            st.components.v1.html(wrapper, height=preview_height + 50)
        else:
            wrapper = f'<div style="overflow:auto; height:{preview_height}px;">{html}</div>'
            st.components.v1.html(wrapper, height=preview_height + 50)
    else:
        st.warning('Could not render formatted preview. Showing plain extracted text below.')
    st.text_area('Extracted resume text', plain_extracted_text or file_bytes.decode('utf-8', errors='replace'), height=preview_height)

# Add a button that triggers formatted preview (preserve fonts/sizes where possible)
if uploaded_bytes and detected_name:
    if st.button('Show formatted resume'):
        show_formatted_preview(uploaded_bytes, detected_name)

if st.button("Enhance Resume"):
    if not input_text or not input_text.strip():
        st.warning("Please provide a resume by uploading a file or pasting it into the text area.")
    else:
        with st.spinner("Enhancing..."):
            enhanced = enhance_resume(input_text)

        st.subheader("Preview")
        st.markdown("---")

        # (PDF preview moved above so it can be seen immediately after upload)

        # Show side-by-side: original and enhanced
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Original**")
            # show filename if available
            if detected_name:
                st.caption(f"Uploaded: {os.path.basename(detected_name)}")
            st.code(input_text, language='text')
        with col2:
            st.markdown("**Enhanced**")
            st.code(enhanced, language='text')

        st.download_button("Download enhanced resume", enhanced, file_name="enhanced_resume.txt")
