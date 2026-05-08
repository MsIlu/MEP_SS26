# Requires: reportlab (install via: pip install reportlab)

# PDF generation dependencies
# (ReportLab is used to create PDFs)
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# In-memory buffer for PDF (no file saved on disk)
from io import BytesIO

def generate_chat_pdf(messages):

    # Create an in-memory byte buffer (no file saved on disk)
    buffer = BytesIO()

    # Create a PDF document object (automatically handles pages)
    doc = SimpleDocTemplate(buffer, pagesize=A4)

    # Load default style sheet for text formatting
    styles = getSampleStyleSheet()

    # Select normal text style 
    normal = styles["Normal"]

    # Create a list that will hold all PDF elements
    elements = []

    # Loop through all chat messages
    for msg in messages:

        # Skip system messages (not shown in PDF)
        if msg["role"] =="system":
            continue

        # Determine message sender label
        role = "User" if msg["role"] == "user" else "Bot"

        # Format message text with bold role label (HTML-like formatting supported)
        text = f"<b>{role}:</b> {msg['content']}"

        # Add formatted text as a paragraph element
        elements.append(Paragraph(text, style=normal))

        # Add vertical spacing between messages
        elements.append(Spacer(1,10))

    # If no chat messages exist, add placeholder text
    if not elements:
        elements.append(
            Paragraph(
                "No chat messages available.",
                style= normal
            )
        )
    # Build the final PDF document from all elements
    doc.build(elements)

    # Reset bufffer pointer to beginning
    buffer.seek(0)

    # Return the PDF as an in-memory byte stream
    return buffer

