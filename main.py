import streamlit as st
import os
import tempfile
import sys

# Ensure the converters folder is in Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "converters")))

# Safe imports
try:
    from converters.pdf_converter import convert_pdf_to_md
except ImportError:
    convert_pdf_to_md = None

try:
    from converters.pptx_converter import convert_pptx_to_md
except ImportError:
    convert_pptx_to_md = None

try:
    from converters.image_converter import convert_image_to_md
except ImportError:
    convert_image_to_md = None

try:
    from converters.docx_converter import convert_docx_to_md
except ImportError:
    convert_docx_to_md = None

# Streamlit config
st.set_page_config(page_title="Universal File to Markdown Converter", layout="centered")

st.title("📄 Universal File → Markdown Converter")
st.write("Drag and drop your file below. Supported formats: **PDF, PPT, PPTX, DOCX, PNG, JPG, JPEG**")

uploaded_file = st.file_uploader(
    "Drop your file here or click to upload",
    type=["pdf", "ppt", "pptx", "docx", "png", "jpg", "jpeg"]  # Added pptx explicitly
)

if uploaded_file:
    file_ext = uploaded_file.name.split(".")[-1].lower()

    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_ext}") as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    st.info(f"Processing `{uploaded_file.name}`... Please wait.")

    try:
        md_content = None

        if file_ext == "pdf" and convert_pdf_to_md:
            md_content = convert_pdf_to_md(tmp_path)

        elif file_ext in ["ppt", "pptx"] and convert_pptx_to_md:
            # Allow .ppt by trying to convert it directly or converting to .pptx internally
            md_content = convert_pptx_to_md(tmp_path)

        elif file_ext in ["png", "jpg", "jpeg"] and convert_image_to_md:
            md_content = convert_image_to_md(tmp_path)

        elif file_ext == "docx" and convert_docx_to_md:
            md_content = convert_docx_to_md(tmp_path)

        else:
            st.error(f"Unsupported file type or missing converter for `{file_ext}`.")

        if md_content:
            st.success("✅ Conversion completed!")

            # Markdown preview
            st.subheader("📜 Markdown Preview")
            st.markdown(md_content)

            # Download button
            st.download_button(
                label="💾 Download Markdown File",
                data=md_content.encode("utf-8"),
                file_name=f"{os.path.splitext(uploaded_file.name)[0]}.md",
                mime="text/markdown"
            )

    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
