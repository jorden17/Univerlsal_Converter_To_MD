import os

def save_markdown(content, output_path):
    """
    Save the given content to a .md file at the specified output path.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Markdown saved to: {output_path}")


def format_table_as_markdown(table_data):
    """
    Convert a 2D list (table_data) into markdown table format.
    Example:
    [["Name", "Age"], ["John", "30"]]
    """
    if not table_data or not isinstance(table_data, list):
        return ""

    # Create header
    header = "| " + " | ".join(str(cell) for cell in table_data[0]) + " |"
    separator = "| " + " | ".join("---" for _ in table_data[0]) + " |"

    # Create rows
    rows = []
    for row in table_data[1:]:
        rows.append("| " + " | ".join(str(cell) for cell in row) + " |")

    return "\n".join([header, separator] + rows)


def image_to_markdown(image_path, alt_text="Image"):
    """
    Return a markdown-formatted string for an image.
    """
    return f"![{alt_text}]({image_path})"


def sanitize_filename(filename):
    """
    Remove unsafe characters from filenames.
    """
    keepcharacters = (" ", ".", "_", "-")
    return "".join(c for c in filename if c.isalnum() or c in keepcharacters).rstrip()
