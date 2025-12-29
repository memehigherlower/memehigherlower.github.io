"""
Meme Verification PDF Generator
Generates a PDF showing all memes with their images for manual verification.
"""

import json
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Image, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
import os

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
MEMES_JSON_PATH = PROJECT_ROOT / "src" / "data" / "memes.json"
IMAGES_DIR = PROJECT_ROOT / "public" / "images" / "memes"
OUTPUT_PDF = Path.home() / "Desktop" / "meme-verification.pdf"

def get_image_path(meme_id, image_url):
    """Get the actual image file path, checking for different extensions."""
    # Extract extension from imageUrl
    ext = Path(image_url).suffix
    image_path = IMAGES_DIR / f"{meme_id}{ext}"

    if image_path.exists():
        return image_path

    # Try other extensions if the specified one doesn't exist
    for extension in ['.jpg', '.png', '.gif']:
        alt_path = IMAGES_DIR / f"{meme_id}{extension}"
        if alt_path.exists():
            return alt_path

    return None

def create_pdf():
    """Generate the meme verification PDF."""
    # Load meme data
    with open(MEMES_JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    memes = data['memes']
    print(f"Loaded {len(memes)} memes")

    # Create PDF document
    doc = SimpleDocTemplate(
        str(OUTPUT_PDF),
        pagesize=letter,
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )

    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'MemeTitle',
        parent=styles['Heading2'],
        fontSize=12,
        spaceAfter=6,
        alignment=TA_CENTER
    )
    desc_style = ParagraphStyle(
        'MemeDesc',
        parent=styles['Normal'],
        fontSize=9,
        alignment=TA_CENTER,
        textColor=colors.gray
    )
    id_style = ParagraphStyle(
        'MemeId',
        parent=styles['Normal'],
        fontSize=8,
        alignment=TA_CENTER,
        textColor=colors.darkgray
    )

    # Build content - 2 memes per row, 3 rows per page = 6 memes per page
    story = []

    # Add title
    story.append(Paragraph("Meme Verification Sheet", styles['Title']))
    story.append(Paragraph(f"Total Memes: {len(memes)}", styles['Normal']))
    story.append(Spacer(1, 0.3*inch))

    # Process memes in groups of 6 (2 columns x 3 rows per page)
    memes_per_page = 6
    image_width = 2.5*inch
    image_height = 2*inch

    for page_start in range(0, len(memes), memes_per_page):
        page_memes = memes[page_start:page_start + memes_per_page]

        # Create rows of 2 memes each
        for row_start in range(0, len(page_memes), 2):
            row_memes = page_memes[row_start:row_start + 2]
            row_data = []

            for meme in row_memes:
                meme_id = meme['id']
                meme_name = meme['name']
                meme_desc = meme.get('description', '')
                image_url = meme['imageUrl']

                # Get image
                image_path = get_image_path(meme_id, image_url)

                cell_content = []

                # Add number and name
                meme_index = memes.index(meme) + 1
                cell_content.append(Paragraph(f"#{meme_index}: {meme_name}", title_style))

                # Add image or placeholder
                if image_path and image_path.exists():
                    try:
                        img = Image(str(image_path), width=image_width, height=image_height)
                        img.hAlign = 'CENTER'
                        cell_content.append(img)
                    except Exception as e:
                        cell_content.append(Paragraph(f"[Image Error: {e}]", desc_style))
                else:
                    cell_content.append(Paragraph("[Image Not Found]", desc_style))

                # Add description and ID
                cell_content.append(Paragraph(meme_desc[:50] + "..." if len(meme_desc) > 50 else meme_desc, desc_style))
                cell_content.append(Paragraph(f"ID: {meme_id}", id_style))

                row_data.append(cell_content)

            # Pad row if only one meme
            while len(row_data) < 2:
                row_data.append([])

            # Create table for this row
            table = Table([row_data], colWidths=[3.5*inch, 3.5*inch])
            table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(table)

        # Add page break after each page (except the last)
        if page_start + memes_per_page < len(memes):
            story.append(PageBreak())

    # Build PDF
    print(f"Generating PDF...")
    doc.build(story)
    print(f"PDF saved to: {OUTPUT_PDF}")

if __name__ == "__main__":
    create_pdf()
