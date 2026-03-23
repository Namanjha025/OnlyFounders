"""Convert the Phase 1 marketplace plan markdown to PDF using fpdf2."""
import re
import sys
from pathlib import Path

from fpdf import FPDF


class PlanPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, "OnlyFounders -- Marketplace Phase 1 Plan", align="R", new_x="LMARGIN", new_y="NEXT")
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")


def sanitize(text: str) -> str:
    """Replace Unicode chars that latin-1 can't encode."""
    replacements = {
        "\u2014": "--",  # em dash
        "\u2013": "-",   # en dash
        "\u2018": "'",   # left single quote
        "\u2019": "'",   # right single quote
        "\u201c": '"',   # left double quote
        "\u201d": '"',   # right double quote
        "\u2026": "...", # ellipsis
        "\u2192": "->",  # right arrow
        "\u2022": "-",   # bullet
        "\u2502": "|",   # box drawing
        "\u251c": "|--", # box drawing
        "\u2514": "`--", # box drawing
        "\u2500": "-",   # box drawing
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text


def render_md_to_pdf(md_path: str, out_path: str):
    text = sanitize(Path(md_path).read_text())
    pdf = PlanPDF()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    in_table = False
    in_code = False
    code_lines = []

    for line_num, line in enumerate(text.split("\n"), 1):
        # Code blocks
        if line.strip().startswith("```"):
            if in_code:
                # End code block
                pdf.set_font("Courier", size=8)
                pdf.set_fill_color(245, 245, 245)
                for cl in code_lines:
                    pdf.cell(0, 4.5, "  " + cl, new_x="LMARGIN", new_y="NEXT", fill=True)
                pdf.ln(3)
                code_lines = []
                in_code = False
            else:
                in_code = True
            continue

        if in_code:
            code_lines.append(line)
            continue

        # Reset X position to left margin for every non-table line
        if not ("|" in line and line.strip().startswith("|")):
            pdf.set_x(10)

        # Horizontal rule
        if line.strip() == "---":
            pdf.ln(3)
            pdf.set_draw_color(200, 200, 200)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(5)
            continue

        # Headers
        if line.startswith("# "):
            pdf.set_font("Helvetica", "B", 18)
            pdf.set_text_color(0, 0, 0)
            pdf.ln(4)
            pdf.cell(0, 10, line[2:].strip(), new_x="LMARGIN", new_y="NEXT")
            pdf.ln(2)
            continue
        if line.startswith("## "):
            pdf.set_font("Helvetica", "B", 14)
            pdf.set_text_color(30, 30, 30)
            pdf.ln(4)
            pdf.cell(0, 8, line[3:].strip(), new_x="LMARGIN", new_y="NEXT")
            pdf.ln(2)
            continue
        if line.startswith("### "):
            pdf.set_font("Helvetica", "B", 11)
            pdf.set_text_color(50, 50, 50)
            pdf.ln(3)
            pdf.cell(0, 7, line[4:].strip(), new_x="LMARGIN", new_y="NEXT")
            pdf.ln(1)
            continue

        # Table rows
        if "|" in line and line.strip().startswith("|"):
            cols = [c.strip() for c in line.strip().strip("|").split("|")]
            # Skip separator rows
            if all(set(c) <= {"-", ":", " "} for c in cols):
                continue

            if not in_table:
                in_table = True
                # Header row
                pdf.set_font("Helvetica", "B", 8)
                pdf.set_fill_color(240, 240, 240)
            else:
                pdf.set_font("Helvetica", size=8)
                pdf.set_fill_color(255, 255, 255)

            col_width = 190 / max(len(cols), 1)
            pdf.set_text_color(0, 0, 0)
            for c in cols:
                clean = re.sub(r'[`*]', '', c)
                pdf.cell(col_width, 5.5, clean[:50], border=1, fill=True)
            pdf.ln()
            continue
        else:
            if in_table:
                in_table = False
                pdf.ln(3)

        # Bold text lines
        if line.strip().startswith("**") and line.strip().endswith("**"):
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(0, 0, 0)
            clean = line.strip().strip("*")
            pdf.multi_cell(0, 5, clean)
            pdf.ln(1)
            continue

        # Bullet points
        if line.strip().startswith("- ") or line.strip().startswith("* "):
            pdf.set_font("Helvetica", size=9)
            pdf.set_text_color(0, 0, 0)
            bullet_text = line.strip()[2:]
            clean = re.sub(r'[`*]', '', bullet_text)
            pdf.multi_cell(0, 5, "  - " + clean)
            continue

        # Numbered items
        m = re.match(r'^(\d+)\.\s+(.+)', line.strip())
        if m:
            pdf.set_font("Helvetica", size=9)
            pdf.set_text_color(0, 0, 0)
            clean = re.sub(r'[`*]', '', m.group(2))
            pdf.cell(5, 5, "")
            pdf.cell(6, 5, f"{m.group(1)}.")
            pdf.multi_cell(0, 5, clean)
            continue

        # Regular paragraph text
        if line.strip():
            pdf.set_font("Helvetica", size=9)
            pdf.set_text_color(0, 0, 0)
            clean = re.sub(r'[`*]', '', line.strip())
            pdf.multi_cell(0, 5, clean)
            pdf.ln(1)
        else:
            pdf.ln(2)

    pdf.output(out_path)
    print(f"PDF generated: {out_path}")


if __name__ == "__main__":
    md_file = sys.argv[1] if len(sys.argv) > 1 else "/home/sidda/.claude/plans/noble-splashing-swan.md"
    out_file = sys.argv[2] if len(sys.argv) > 2 else "/home/sidda/OnlyFounders/specs/marketplace/phase1-plan.pdf"
    render_md_to_pdf(md_file, out_file)
