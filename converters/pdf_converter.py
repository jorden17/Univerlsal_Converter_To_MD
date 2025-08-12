# import os
# import fitz  # PyMuPDF
# import pdfplumber
# import camelot
# import uuid

# def extract_text_from_pdf(pdf_path):
#     """Extracts text using pdfplumber."""
#     text_content = []
#     with pdfplumber.open(pdf_path) as pdf:
#         for page in pdf.pages:
#             text = page.extract_text()
#             if text:
#                 text_content.append(text)
#     return "\n".join(text_content)


# def extract_tables_from_pdf(pdf_path):
#     """Tries to extract tables using Camelot first, then falls back to pdfplumber."""
#     tables_md = []
#     try:
#         # First try with Camelot (works for vector-based PDFs)
#         tables = camelot.read_pdf(pdf_path, pages="all", flavor='lattice')
#         if tables:
#             for i, table in enumerate(tables):
#                 tables_md.append(table.df.to_markdown(index=False))
#     except Exception:
#         pass  # Ignore Camelot errors

#     # Fallback to pdfplumber table extraction
#     try:
#         with pdfplumber.open(pdf_path) as pdf:
#             for page in pdf.pages:
#                 tables = page.extract_tables()
#                 for table in tables:
#                     md_table = "\n".join(
#                         ["| " + " | ".join(row) + " |" for row in table if any(row)]
#                     )
#                     tables_md.append(md_table)
#     except Exception:
#         pass  # Ignore any table extraction errors

#     return "\n\n".join(tables_md)


# def extract_images_from_pdf(pdf_path, output_dir):
#     """Extracts images from the PDF and saves them in output_dir."""
#     images_md = []
#     pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]

#     with fitz.open(pdf_path) as pdf:
#         for page_num, page in enumerate(pdf, start=1):
#             for img_index, img in enumerate(page.get_images(full=True), start=1):
#                 xref = img[0]
#                 base_image = pdf.extract_image(xref)
#                 image_bytes = base_image["image"]
#                 image_ext = base_image["ext"]

#                 image_filename = f"{pdf_name}_page{page_num}_{img_index}.{image_ext}"
#                 image_path = os.path.join(output_dir, image_filename)

#                 os.makedirs(output_dir, exist_ok=True)
#                 with open(image_path, "wb") as img_file:
#                     img_file.write(image_bytes)

#                 images_md.append(f"![Image](images/{image_filename})")

#     return "\n".join(images_md)


# def convert_pdf_to_md(pdf_path, output_md_path=None, images_output_dir=None):
#     """
#     Main function to convert PDF to Markdown.
#     If output_md_path or images_output_dir are not provided, defaults will be used.
#     """
#     try:
#         # Set default output paths if not provided
#         base_name = os.path.splitext(os.path.basename(pdf_path))[0]
#         if images_output_dir is None:
#             images_output_dir = os.path.join("output", "images")
#         if output_md_path is None:
#             output_md_path = os.path.join("output", f"{base_name}.md")

#         # Ensure output directories exist
#         os.makedirs(os.path.dirname(output_md_path), exist_ok=True)
#         os.makedirs(images_output_dir, exist_ok=True)

#         md_content = []

#         # Extract text
#         text_data = extract_text_from_pdf(pdf_path)
#         if text_data.strip():
#             md_content.append("# Extracted Text\n" + text_data)

#         # Extract tables
#         table_data = extract_tables_from_pdf(pdf_path)
#         if table_data.strip():
#             md_content.append("\n# Extracted Tables\n" + table_data)

#         # Extract images
#         image_data = extract_images_from_pdf(pdf_path, images_output_dir)
#         if image_data.strip():
#             md_content.append("\n# Extracted Images\n" + image_data)

#         # Save Markdown file
#         with open(output_md_path, "w", encoding="utf-8") as f:
#             f.write("\n\n".join(md_content))

#         return "\n\n".join(md_content)  # So main.py can display it directly

#     except Exception as e:
#         print(f"Error processing PDF: {e}")
#         return None

import os
import fitz  # PyMuPDF
import camelot
import pdfplumber
import pandas as pd

def extract_pdf_content_in_order(pdf_path, images_output_dir):
    """
    Extract text, tables, and images from PDF in the order they appear.
    """
    md_content = []
    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]

    with fitz.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf, start=1):
            blocks = page.get_text("blocks")  # list of (x0, y0, x1, y1, text, block_no, type)
            blocks.sort(key=lambda b: (b[1], b[0]))  # Sort top-to-bottom, left-to-right

            for b in blocks:
                text = b[4].strip()
                if not text:
                    continue

                # Replace plain URLs with markdown links
                links = page.get_links()
                for link in links:
                    if "uri" in link:
                        uri = link["uri"]
                        if uri in text:
                            text = text.replace(uri, f"[{uri}]({uri})")

                md_content.append(text)

            # Try extracting tables with Camelot
            try:
                tables = camelot.read_pdf(pdf_path, pages=str(page_num), flavor='lattice')
                for table in tables:
                    df = table.df
                    md_table = df.to_markdown(index=False, headers=df.iloc[0] if len(df) > 1 else None)
                    md_content.append(md_table)
            except:
                pass

            # Extract images
            for img_index, img in enumerate(page.get_images(full=True), start=1):
                xref = img[0]
                base_image = pdf.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]

                image_filename = f"{pdf_name}_page{page_num}_{img_index}.{image_ext}"
                image_path = os.path.join(images_output_dir, image_filename)
                os.makedirs(images_output_dir, exist_ok=True)
                with open(image_path, "wb") as img_file:
                    img_file.write(image_bytes)

                md_content.append(f"![Image](images/{image_filename})")

    return "\n\n".join(md_content)

def convert_pdf_to_md(pdf_path, output_md_path=None, images_output_dir=None):
    try:
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        if images_output_dir is None:
            images_output_dir = os.path.join("output", "images")
        if output_md_path is None:
            output_md_path = os.path.join("output", f"{base_name}.md")

        os.makedirs(os.path.dirname(output_md_path), exist_ok=True)
        os.makedirs(images_output_dir, exist_ok=True)

        md_content = extract_pdf_content_in_order(pdf_path, images_output_dir)

        with open(output_md_path, "w", encoding="utf-8") as f:
            f.write(md_content)

        return md_content
    except Exception as e:
        print(f"Error processing PDF: {e}")
        return None
