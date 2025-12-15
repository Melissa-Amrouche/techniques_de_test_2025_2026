#!/usr/bin/env python3
"""Script simple pour générer documentation.pdf à partir de DOCUMENTATION.md"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Preformatted, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from pathlib import Path
import re

def parse_markdown_to_pdf():
    """Parse le Markdown et génère un PDF."""

    # Chemins
    md_file = Path("docs/DOCUMENTATION.md")
    pdf_file = Path("docs/documentation.pdf")

    # Lire le fichier Markdown
    print(f" Lecture de {md_file}...")
    with open(md_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Créer le PDF
    print(f" Création du PDF...")
    doc = SimpleDocTemplate(
        str(pdf_file),
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    # Styles
    styles = getSampleStyleSheet()

    # Style titre principal (H1)
    h1_style = ParagraphStyle(
        'CustomH1',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=12,
        spaceBefore=20,
        borderWidth=2,
        borderColor=colors.HexColor('#3498db'),
        borderPadding=5,
    )

    # Style H2
    h2_style = ParagraphStyle(
        'CustomH2',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=10,
        spaceBefore=15,
        borderWidth=1,
        borderColor=colors.HexColor('#95a5a6'),
        borderPadding=3,
    )

    # Style H3
    h3_style = ParagraphStyle(
        'CustomH3',
        parent=styles['Heading3'],
        fontSize=13,
        textColor=colors.HexColor('#7f8c8d'),
        spaceAfter=8,
        spaceBefore=12,
    )

    # Style H4
    h4_style = ParagraphStyle(
        'CustomH4',
        parent=styles['Heading4'],
        fontSize=11,
        textColor=colors.HexColor('#95a5a6'),
        spaceAfter=6,
        spaceBefore=10,
    )

    # Style code - fond gris clair avec texte noir pour meilleure lisibilité
    code_style = ParagraphStyle(
        'Code',
        parent=styles['Code'],
        fontSize=8,
        fontName='Courier',
        textColor=colors.HexColor('#000000'),  # Noir pour le texte
        backColor=colors.HexColor('#f5f5f5'),  # Gris très clair pour le fond
        leftIndent=10,
        rightIndent=10,
        spaceAfter=10,
        spaceBefore=10,
        borderWidth=1,
        borderColor=colors.HexColor('#cccccc'),
        borderPadding=5,
    )

    # Style normal
    normal_style = styles['Normal']
    normal_style.fontSize = 10
    normal_style.alignment = TA_LEFT

    # Contenu du PDF
    story = []

    in_code_block = False
    code_buffer = []
    is_first_h1 = True
    empty_line_count = 0

    for line in lines:
        line = line.rstrip()

        # Gestion des blocs de code
        if line.startswith('```'):
            if in_code_block:
                # Fin du bloc de code
                if code_buffer:
                    # Limiter la largeur des lignes de code
                    code_lines = []
                    for code_line in code_buffer:
                        if len(code_line) > 90:
                            code_lines.append(code_line[:87] + '...')
                        else:
                            code_lines.append(code_line)
                    code_text = '\n'.join(code_lines)
                    story.append(Preformatted(code_text, code_style))
                    story.append(Spacer(1, 0.2*cm))  # Espace après le code
                    code_buffer = []
                in_code_block = False
                empty_line_count = 0
            else:
                # Début du bloc de code
                in_code_block = True
                empty_line_count = 0
            continue

        if in_code_block:
            code_buffer.append(line)
            continue

        # Lignes vides - éviter trop d'espaces consécutifs
        if not line.strip():
            empty_line_count += 1
            if empty_line_count <= 1:  # Max 1 ligne vide
                story.append(Spacer(1, 0.2*cm))
            continue

        empty_line_count = 0

        # Titres
        if line.startswith('# '):
            text = line[2:].strip()
            # Ne pas ajouter PageBreak avant le tout premier H1
            if not is_first_h1:
                story.append(PageBreak())
            is_first_h1 = False
            story.append(Paragraph(text, h1_style))
            story.append(Spacer(1, 0.3*cm))
        elif line.startswith('## '):
            text = line[3:].strip()
            story.append(Spacer(1, 0.4*cm))
            story.append(Paragraph(text, h2_style))
            story.append(Spacer(1, 0.2*cm))
        elif line.startswith('### '):
            text = line[4:].strip()
            story.append(Spacer(1, 0.3*cm))
            story.append(Paragraph(text, h3_style))
            story.append(Spacer(1, 0.15*cm))
        elif line.startswith('#### '):
            text = line[5:].strip()
            story.append(Spacer(1, 0.2*cm))
            story.append(Paragraph(text, h4_style))
            story.append(Spacer(1, 0.1*cm))

        # Séparateurs
        elif line.strip() == '---':
            story.append(Spacer(1, 0.5*cm))

        # Listes à puces
        elif line.strip().startswith('- ') or line.strip().startswith('* '):
            text = '• ' + line.strip()[2:]
            # Nettoyer le texte des balises Markdown
            text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)  # Gras
            text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)      # Italique
            text = re.sub(r'`(.*?)`', r'<font face="Courier" color="#c7254e">\1</font>', text)  # Code inline
            story.append(Paragraph(text, normal_style))

        # Listes numérotées
        elif re.match(r'^\d+\.\s', line.strip()):
            text = line.strip()
            # Nettoyer le texte
            text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
            text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
            text = re.sub(r'`(.*?)`', r'<font face="Courier" color="#c7254e">\1</font>', text)
            story.append(Paragraph(text, normal_style))

        # Paragraphes normaux
        else:
            text = line.strip()
            # Ignorer UNIQUEMENT les tableaux Markdown avec | (pas les tableaux ASCII)
            # Les tableaux ASCII (┌├│└) dans les blocs de code sont gérés par Preformatted
            if '|' in text and not any(c in text for c in '┌├│└'):
                continue

            # Nettoyer le texte
            text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
            text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
            text = re.sub(r'`(.*?)`', r'<font face="Courier" color="#c7254e">\1</font>', text)
            text = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', text)  # Liens

            if text:
                story.append(Paragraph(text, normal_style))

    # Construire le PDF
    print(f"🔨 Construction du PDF...")
    doc.build(story)

    print(f" PDF généré avec succès : {pdf_file}")
    print(f" Taille du fichier : {pdf_file.stat().st_size / 1024:.1f} Ko")
    return pdf_file

if __name__ == "__main__":
    try:
        pdf_path = parse_markdown_to_pdf()
        print(f"\n Documentation PDF prête : {pdf_path}")
        print(f" Pour l'ouvrir : open {pdf_path}")
    except ImportError as e:
        print(f" Erreur : Module manquant - {e}")
        print("\n Installation requise :")
        print("   pip install reportlab")
    except Exception as e:
        print(f" Erreur lors de la génération : {e}")
        import traceback
        traceback.print_exc()
