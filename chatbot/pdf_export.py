"""
PDF Export for Question Papers
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO
from django.http import HttpResponse


def export_question_paper_pdf(paper, questions_by_marks):
    """
    Export question paper as PDF
    
    Args:
        paper: QuestionPaper model instance
        questions_by_marks: Dict of questions organized by marks
        
    Returns:
        HttpResponse with PDF file
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=18)
    
    # Container for PDF elements
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor='#1e293b',
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subject_style = ParagraphStyle(
        'SubjectStyle',
        parent=styles['Normal'],
        fontSize=14,
        textColor='#475569',
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica'
    )
    
    section_style = ParagraphStyle(
        'SectionStyle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor='#667eea',
        spaceAfter=10,
        spaceBefore=15,
        fontName='Helvetica-Bold'
    )
    
    question_style = ParagraphStyle(
        'QuestionStyle',
        parent=styles['Normal'],
        fontSize=11,
        textColor='#1e293b',
        spaceAfter=12,
        leftIndent=20,
        fontName='Helvetica'
    )
    
    # Header
    elements.append(Paragraph(paper.title, title_style))
    elements.append(Paragraph(f"Subject: {paper.subject}", subject_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Questions organized by marks
    for marks in sorted(questions_by_marks.keys(), key=lambda x: int(x)):
        questions = questions_by_marks[marks]
        if not questions:
            continue
            
        # Section header
        section_title = f"Section: {marks} Marks Questions"
        elements.append(Paragraph(section_title, section_style))
        elements.append(Spacer(1, 0.1*inch))
        
        # Questions
        for idx, q in enumerate(questions, 1):
            question_text = f"{idx}. {q['question']}"
            elements.append(Paragraph(question_text, question_style))
            
            # Add hint if available
            if q.get('hint') or q.get('reasoning'):
                hint_text = f"<i>Hint: {q.get('hint') or q.get('reasoning')}</i>"
                hint_style = ParagraphStyle(
                    'HintStyle',
                    parent=styles['Normal'],
                    fontSize=9,
                    textColor='#64748b',
                    leftIndent=40,
                    spaceAfter=8,
                    fontName='Helvetica-Oblique'
                )
                elements.append(Paragraph(hint_text, hint_style))
        
        elements.append(Spacer(1, 0.2*inch))
    
    # Build PDF
    doc.build(elements)
    
    # Get PDF data
    pdf = buffer.getvalue()
    buffer.close()
    
    # Create response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{paper.title}.pdf"'
    response.write(pdf)
    
    return response
