#!/usr/bin/env python3
"""
Generate Word documents (.docx) from Markdown documentation files.

This script converts key Markdown files into professionally formatted Word documents
for stakeholder review and client deliverables.

Usage:
    python generate_docx.py

Outputs 8 .docx files in deliverables/ directory:
    1. Project_Overview.docx (from README.md)
    2. Product_Requirements_Document.docx (from PRD.md)
    3. Software_Requirements_Specification.docx (from SRS.md)
    4. Software_Architecture_and_Design.docx (from ARCHITECTURE.md)
    5. Data_Analysis_and_Forecast_Methodology.docx (from DATA_DICTIONARY.md + FORECAST_METHODOLOGY.md)
    6. User_Guide.docx (from USER_GUIDE.md)
    7. Deployment_and_Setup_Guide.docx (from DEPLOYMENT.md)
    8. Technical_Handover.docx (from TESTING.md + API.md + DECISIONS.md)
"""

import re
from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn


PROJECT_ROOT = Path(__file__).parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"
DELIVERABLES_DIR = PROJECT_ROOT / "deliverables"


def read_markdown_file(filepath: Path) -> str:
    """Read Markdown file, return content."""
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def add_title_page(doc: Document, title: str, subtitle: str, date: str):
    """Add a formatted title page."""
    # Title
    title_para = doc.add_paragraph()
    title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_run = title_para.add_run(title)
    title_run.font.size = Pt(24)
    title_run.font.bold = True
    title_run.font.color.rgb = RGBColor(30, 58, 138)  # Blue-900

    # Subtitle
    if subtitle:
        subtitle_para = doc.add_paragraph()
        subtitle_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        subtitle_run = subtitle_para.add_run(subtitle)
        subtitle_run.font.size = Pt(16)
        subtitle_run.font.italic = True

    # Spacing
    doc.add_paragraph()
    doc.add_paragraph()

    # Date
    date_para = doc.add_paragraph()
    date_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    date_run = date_para.add_run(f"Date: {date}")
    date_run.font.size = Pt(12)

    # Page break
    doc.add_page_break()


def parse_markdown_to_docx(doc: Document, markdown_content: str):
    """Parse Markdown content and add to Word document with formatting."""
    lines = markdown_content.split("\n")
    i = 0

    while i < len(lines):
        line = lines[i]

        # Skip YAML frontmatter (if any)
        if i == 0 and line.strip() == "---":
            i += 1
            while i < len(lines) and lines[i].strip() != "---":
                i += 1
            i += 1
            continue

        # Heading 1 (# Title)
        if line.startswith("# "):
            heading = line[2:].strip()
            p = doc.add_heading(heading, level=1)
            p.runs[0].font.color.rgb = RGBColor(30, 58, 138)

        # Heading 2 (## Title)
        elif line.startswith("## "):
            heading = line[3:].strip()
            p = doc.add_heading(heading, level=2)

        # Heading 3 (### Title)
        elif line.startswith("### "):
            heading = line[4:].strip()
            p = doc.add_heading(heading, level=3)

        # Heading 4 (#### Title)
        elif line.startswith("#### "):
            heading = line[5:].strip()
            p = doc.add_heading(heading, level=4)

        # Code block (```language)
        elif line.strip().startswith("```"):
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            code_text = "\n".join(code_lines)
            p = doc.add_paragraph(code_text)
            p.style = "No Spacing"
            for run in p.runs:
                run.font.name = "Courier New"
                run.font.size = Pt(9)
                run.font.color.rgb = RGBColor(51, 51, 51)
            # Light gray background (shading)
            shading_elm = p._element.get_or_add_pPr()
            shading = OxmlElement("w:shd")
            shading.set(qn("w:fill"), "F3F4F6")
            shading_elm.append(shading)

        # Table (| Header | Header |)
        elif line.strip().startswith("|") and "|" in line[1:]:
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i].strip())
                i += 1
            i -= 1  # Back up one line

            # Parse table
            rows = [
                [cell.strip() for cell in row.split("|")[1:-1]] for row in table_lines
            ]
            # Skip separator row (| --- | --- |)
            if len(rows) > 1 and all("--" in cell for cell in rows[1]):
                rows = [rows[0]] + rows[2:]

            # Create table
            if rows:
                # Determine max columns (handle uneven tables)
                max_cols = max(len(row) for row in rows)
                table = doc.add_table(rows=len(rows), cols=max_cols)
                table.style = "Light Grid Accent 1"

                for row_idx, row_data in enumerate(rows):
                    for col_idx, cell_data in enumerate(row_data):
                        if col_idx < max_cols:  # Safety check
                            cell = table.rows[row_idx].cells[col_idx]
                            cell.text = cell_data
                            # Bold header row
                            if row_idx == 0:
                                for paragraph in cell.paragraphs:
                                    for run in paragraph.runs:
                                        run.font.bold = True

                doc.add_paragraph()  # Spacing after table

        # Bullet list (- Item or * Item)
        elif line.strip().startswith("- ") or line.strip().startswith("* "):
            text = line.strip()[2:]
            p = doc.add_paragraph(text, style="List Bullet")

        # Numbered list (1. Item)
        elif re.match(r"^\d+\.\s", line.strip()):
            text = re.sub(r"^\d+\.\s", "", line.strip())
            p = doc.add_paragraph(text, style="List Number")

        # Blockquote (> Text)
        elif line.strip().startswith("> "):
            text = line.strip()[2:]
            p = doc.add_paragraph(text)
            p.paragraph_format.left_indent = Inches(0.5)
            p.paragraph_format.right_indent = Inches(0.5)
            p.runs[0].font.italic = True
            p.runs[0].font.color.rgb = RGBColor(75, 85, 99)

        # Horizontal rule (--- or ***)
        elif line.strip() in ["---", "***", "___"]:
            doc.add_paragraph("_" * 60)

        # Empty line
        elif line.strip() == "":
            # Skip consecutive empty lines (avoid excessive spacing)
            if i > 0 and lines[i - 1].strip() != "":
                doc.add_paragraph()

        # Regular paragraph
        else:
            if line.strip():
                # Handle inline formatting: **bold**, *italic*, `code`
                formatted_text = line.strip()
                p = doc.add_paragraph()

                # Split by inline code first
                parts = re.split(r"(`[^`]+`)", formatted_text)
                for part in parts:
                    if part.startswith("`") and part.endswith("`"):
                        # Inline code
                        run = p.add_run(part[1:-1])
                        run.font.name = "Courier New"
                        run.font.size = Pt(10)
                        run.font.color.rgb = RGBColor(220, 38, 38)
                    else:
                        # Bold and italic
                        subparts = re.split(r"(\*\*[^*]+\*\*|\*[^*]+\*)", part)
                        for subpart in subparts:
                            if subpart.startswith("**") and subpart.endswith("**"):
                                run = p.add_run(subpart[2:-2])
                                run.font.bold = True
                            elif subpart.startswith("*") and subpart.endswith("*"):
                                run = p.add_run(subpart[1:-1])
                                run.font.italic = True
                            else:
                                p.add_run(subpart)

        i += 1


def OxmlElement(tag):
    """Helper to create an OOXML element with proper namespace."""
    from docx.oxml import OxmlElement as BaseOxmlElement
    return BaseOxmlElement(tag)


def create_combined_document(
    output_filename: str,
    title: str,
    subtitle: str,
    source_files: list[tuple[str, Path]],
):
    """Create a Word document by combining multiple Markdown sources."""
    doc = Document()

    # Title page
    add_title_page(doc, title, subtitle, "October 26, 2026")

    # Process each source file
    for section_title, filepath in source_files:
        if not filepath.exists():
            print(f"Warning: {filepath} not found, skipping.")
            continue

        # Section title
        if section_title:
            doc.add_heading(section_title, level=1)
            doc.add_paragraph()

        # Parse Markdown content
        markdown_content = read_markdown_file(filepath)
        parse_markdown_to_docx(doc, markdown_content)

        # Page break between sections (except last)
        if source_files.index((section_title, filepath)) < len(source_files) - 1:
            doc.add_page_break()

    # Save
    output_path = DELIVERABLES_DIR / output_filename
    doc.save(output_path)
    print(f"[OK] Created: {output_path}")


def main():
    """Generate all Word documents."""
    print("Generating Word documents from Markdown...\n")

    DELIVERABLES_DIR.mkdir(exist_ok=True)

    # Document 1: Project Overview
    create_combined_document(
        output_filename="Project_Overview.docx",
        title="UK Wind Forecast Accuracy Dashboard",
        subtitle="Project Overview",
        source_files=[
            ("", PROJECT_ROOT / "README.md"),
        ],
    )

    # Document 2: Product Requirements Document
    create_combined_document(
        output_filename="Product_Requirements_Document.docx",
        title="Product Requirements Document",
        subtitle="UK Wind Forecast Accuracy Dashboard",
        source_files=[
            ("", DOCS_DIR / "PRD.md"),
        ],
    )

    # Document 3: Software Requirements Specification
    create_combined_document(
        output_filename="Software_Requirements_Specification.docx",
        title="Software Requirements Specification",
        subtitle="UK Wind Forecast Accuracy Dashboard",
        source_files=[
            ("", DOCS_DIR / "SRS.md"),
        ],
    )

    # Document 4: Software Architecture and Design
    create_combined_document(
        output_filename="Software_Architecture_and_Design.docx",
        title="Software Architecture and Design",
        subtitle="UK Wind Forecast Accuracy Dashboard",
        source_files=[
            ("", DOCS_DIR / "ARCHITECTURE.md"),
            ("Design System", DOCS_DIR / "UI_UX_DESIGN_SYSTEM.md"),
        ],
    )

    # Document 5: Data Analysis and Forecast Methodology
    create_combined_document(
        output_filename="Data_Analysis_and_Forecast_Methodology.docx",
        title="Data Analysis and Forecast Methodology",
        subtitle="UK Wind Forecast Accuracy Dashboard",
        source_files=[
            ("Data Dictionary", DOCS_DIR / "DATA_DICTIONARY.md"),
            ("Forecast Methodology", DOCS_DIR / "FORECAST_METHODOLOGY.md"),
            ("Assumptions and Limitations", DOCS_DIR / "ASSUMPTIONS_AND_LIMITATIONS.md"),
        ],
    )

    # Document 6: User Guide
    create_combined_document(
        output_filename="User_Guide.docx",
        title="User Guide",
        subtitle="UK Wind Forecast Accuracy Dashboard",
        source_files=[
            ("", DOCS_DIR / "USER_GUIDE.md"),
            ("Glossary", DOCS_DIR / "GLOSSARY.md"),
        ],
    )

    # Document 7: Deployment and Setup Guide
    create_combined_document(
        output_filename="Deployment_and_Setup_Guide.docx",
        title="Deployment and Setup Guide",
        subtitle="UK Wind Forecast Accuracy Dashboard",
        source_files=[
            ("", DOCS_DIR / "DEPLOYMENT.md"),
            ("Security Considerations", DOCS_DIR / "SECURITY.md"),
        ],
    )

    # Document 8: Technical Handover
    create_combined_document(
        output_filename="Technical_Handover.docx",
        title="Technical Handover",
        subtitle="UK Wind Forecast Accuracy Dashboard",
        source_files=[
            ("Testing Strategy", DOCS_DIR / "TESTING.md"),
            ("API Reference", DOCS_DIR / "API.md"),
            ("Architecture Decisions", DOCS_DIR / "DECISIONS.md"),
            ("Known Issues", DOCS_DIR / "KNOWN_ISSUES.md"),
        ],
    )

    print("\n[SUCCESS] All Word documents generated successfully!")
    print(f"Output directory: {DELIVERABLES_DIR}")


if __name__ == "__main__":
    main()
