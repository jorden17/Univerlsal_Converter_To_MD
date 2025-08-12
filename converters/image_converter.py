import pytesseract
import cv2
from pathlib import Path
import uuid
import pandas as pd
import numpy as np

# If Tesseract is not in PATH, uncomment and set correct path
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_table_from_image(img):
    """
    Detect and extract tables from an image using OpenCV and OCR.
    Returns markdown table(s) as string.
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY_INV, 15, 8
    )

    # Detect horizontal lines
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
    detect_horizontal = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)

    # Detect vertical lines
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
    detect_vertical = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, vertical_kernel, iterations=2)

    # Combine lines
    table_mask = cv2.add(detect_horizontal, detect_vertical)

    contours, _ = cv2.findContours(table_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    tables_md = []

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if w > 50 and h > 30:  # Avoid small artifacts
            table_roi = img[y:y+h, x:x+w]
            table_text = pytesseract.image_to_string(table_roi, config="--psm 6")
            rows = [r.strip() for r in table_text.split("\n") if r.strip()]
            split_rows = [row.split() for row in rows]
            if split_rows:
                try:
                    df = pd.DataFrame(split_rows)
                    tables_md.append(df.to_markdown(index=False, headers=None))
                except Exception:
                    md_fallback = "\n".join(["| " + " | ".join(r) + " |" for r in split_rows])
                    tables_md.append(md_fallback)

    return "\n\n".join(tables_md) if tables_md else ""


def convert_image_to_md(image_path, output_dir="output"):
    """
    Converts image to Markdown:
    - Saves original image
    - Extracts OCR text
    - Extracts tables
    """
    image_path = Path(image_path)
    output_dir = Path(output_dir)
    images_dir = output_dir / "images"
    output_dir.mkdir(parents=True, exist_ok=True)
    images_dir.mkdir(parents=True, exist_ok=True)

    markdown_lines = []

    # ---------- STEP 1: Save Original Image ----------
    image_ext = image_path.suffix.lstrip(".")
    image_name = f"{uuid.uuid4()}.{image_ext}"
    saved_image_path = images_dir / image_name
    with open(saved_image_path, "wb") as f:
        f.write(open(str(image_path), "rb").read())

    markdown_lines.append(f"![Image](images/{image_name})\n")

    # ---------- STEP 2: Load Image ----------
    img = cv2.imread(str(image_path))

    # ---------- STEP 3: Extract Text ----------
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray, config="--psm 6")
    if text.strip():
        markdown_lines.append("## Extracted Text\n")
        markdown_lines.append(text.strip() + "\n")

    # ---------- STEP 4: Extract Tables ----------
    table_md = extract_table_from_image(img)
    if table_md:
        markdown_lines.append("## Extracted Table(s)\n")
        markdown_lines.append(table_md + "\n")

    # ---------- STEP 5: Save Markdown ----------
    output_md_path = output_dir / f"{image_path.stem}.md"
    with open(str(output_md_path), "w", encoding="utf-8") as md_file:
        md_file.write("\n".join(markdown_lines))

    return str(output_md_path)


# Example usage:
if __name__ == "__main__":
    img_file = "test_image.png"  # Change to your image file path
    md_file = convert_image_to_md(img_file)
    print(f"Markdown saved at: {md_file}")
