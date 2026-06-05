"""
PDF report generator.

Uses table-based HTML only — no <div> layout — because Qt's QTextDocument
supports only a limited HTML/CSS subset (roughly HTML 3.2 + basic CSS 2.1).
All images are embedded as base64 data URIs to avoid Windows path issues.
"""
import os
import base64
from datetime import datetime
from PyQt5.QtCore import QSizeF
from PyQt5.QtGui import QTextDocument
from PyQt5.QtPrintSupport import QPrinter
from PyQt5.QtWidgets import QApplication, QMessageBox
from utils import resource_path

_AUTHORS = (
    "Elias Escobar Pereira &nbsp;&bull;&nbsp; "
    "Kevin David Ortega Qui&ntilde;ones &nbsp;&bull;&nbsp; "
    "Daniela Buitrago Largo &nbsp;&bull;&nbsp; "
    "Mauricio Holgu&iacute;n Londo&ntilde;o &nbsp;&bull;&nbsp; "
    "German Andres Holgu&iacute;n Londo&ntilde;o"
)
_POSE_LABELS = [
    "Punto de Muestreo 1",
    "Punto de Muestreo 2",
    "Punto de Muestreo 3",
]

# Minimal CSS — only font, color, and spacing that Qt honours reliably.
_CSS = """
body  { font-family: Arial, sans-serif; font-size: 11px; color: #202124; margin: 0; padding: 0; }
b     { font-weight: bold; }
td    { font-size: 11px; }
th    { font-size: 11px; }
.mono { font-family: Courier New, monospace; font-size: 10px; }
"""


# ──────────────────────────────────────────────────────────────────────────────
# Public entry point
# ──────────────────────────────────────────────────────────────────────────────

def generate_pdf_report(traj_name, snapshots):
    QApplication.processEvents()

    # Configure printer first so we can read the exact printable rect.
    printer = QPrinter(QPrinter.ScreenResolution)
    printer.setOutputFormat(QPrinter.PdfFormat)
    printer.setPageMargins(8, 8, 8, 8, QPrinter.Millimeter)
    safe_name = (
        traj_name.replace(" ", "_")
                 .replace("(", "").replace(")", "")
                 .replace("/", "-")
    )
    pdf_path = os.path.abspath(f"Reporte_{safe_name}.pdf")
    printer.setOutputFileName(pdf_path)

    html = _build_html(traj_name, snapshots)

    doc = QTextDocument()
    # Without this the document uses its own default width and leaves wide
    # blank margins — setting it to the printer's printable rect makes
    # width="100%" tables actually span the full page.
    doc.setPageSize(QSizeF(printer.pageRect().size()))
    doc.setHtml(html)
    doc.print_(printer)

    _cleanup_images(snapshots)

    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setWindowTitle("PDF Generado")
    msg.setText(
        f"<b>Trayectoria completada.</b><br><br>"
        f"PDF guardado en:<br>{pdf_path}"
    )
    msg.exec_()


# ──────────────────────────────────────────────────────────────────────────────
# HTML assembly
# ──────────────────────────────────────────────────────────────────────────────

def _build_html(traj_name, snapshots):
    cover = _cover(traj_name)
    sections = "".join(_section(i, s) for i, s in enumerate(snapshots))
    return (
        f"<html><head>"
        f"<meta charset='utf-8'>"
        f"<style>{_CSS}</style>"
        f"</head><body>"
        f"{cover}"
        f"{sections}"
        f"</body></html>"
    )


# ──────────────────────────────────────────────────────────────────────────────
# Cover page
# ──────────────────────────────────────────────────────────────────────────────

def _cover(traj_name):
    logo_utp   = _b64_img("Logo_UTP.png",  width=90)
    logo_gseea = _b64_img("gseea.png",     width=110)
    date_str   = datetime.now().strftime("%d/%m/%Y  %H:%M")

    # ── Blue header bar with logos flanking the title ──────────────────
    header = f"""
    <table width="100%" cellspacing="0" cellpadding="0"
           style="background-color:#1a73e8;">
      <tr>
        <td width="130" align="center" valign="middle"
            style="padding:14px 10px; background-color:#ffffff;">
          {logo_utp}
        </td>
        <td align="center" valign="middle" style="padding:14px 20px;">
          <b style="font-size:17px; color:#ffffff;">
            REPORTE DE AN&Aacute;LISIS CINEM&Aacute;TICO
          </b><br>
          <span style="font-size:11px; color:#c6dafc;">
            Robot Manipulador PAROL6 &mdash; 6 Grados de Libertad
          </span><br>
          <span style="font-size:10px; color:#c6dafc;">
            HMI Industrial &nbsp;/&nbsp; Simulaci&oacute;n PyBullet
          </span>
        </td>
        <td width="140" align="center" valign="middle"
            style="padding:14px 10px; background-color:#ffffff;">
          {logo_gseea}
        </td>
      </tr>
    </table>"""

    # ── Info block below the header ────────────────────────────────────
    def row(label, value):
        return (
            f"<tr>"
            f"<td width='22%' valign='top'"
            f"    style='font-weight:bold; color:#1a73e8; padding:4px 8px;'>{label}</td>"
            f"<td valign='top' style='padding:4px 8px; color:#3c4043;'>{value}</td>"
            f"</tr>"
        )

    info = f"""
    <table width="100%" cellspacing="0" cellpadding="0"
           style="background-color:#f0f4ff; border-left:2px solid #1a73e8;
                  border-right:2px solid #1a73e8; border-bottom:2px solid #1a73e8;
                  margin-bottom:16px;">
      {row("Trayectoria:",  f"<b>{traj_name}</b>")}
      {row("Fecha:",         date_str)}
      {row("Universidad:",  "Universidad Tecnol&oacute;gica de Pereira &mdash; Facultad de Ingenier&iacute;as")}
      {row("Grupo:",        "GIGSEEA &mdash; Grupo de Investigaci&oacute;n en Gesti&oacute;n de Sistemas El&eacute;ctricos, Electr&oacute;nicos y Autom&aacute;ticos")}
      {row("Autores:",      _AUTHORS)}
    </table>"""

    return header + info

# ──────────────────────────────────────────────────────────────────────────────
# Snapshot section
# ──────────────────────────────────────────────────────────────────────────────

def _section(idx, snap):
    label      = _POSE_LABELS[idx] if idx < len(_POSE_LABELS) else f"Punto {idx+1}"
    joints_txt = "   ".join(f"q{i+1}={v:+.3f}" for i, v in enumerate(snap["joints"]))

    sim_img  = _b64_img_from_file(snap["sim_img"],  width=340)
    wire_img = _b64_img_from_file(snap["wire_img"], width=340)

    t_tbl = _t_matrix(snap["T_matrix"])
    r_tbl = _r_matrix(snap["R_matrix"])
    e_tbl = _euler(snap["euler"])

    # ── Section title bar ───────────────────────────────────────────────
    title = f"""
    <table width="100%" cellspacing="0" cellpadding="0"
           style="margin-top:18px; margin-bottom:4px;">
      <tr bgcolor="#1a73e8">
        <td style="padding:7px 12px; color:#ffffff; font-weight:bold; font-size:13px;">
          &#9654;&nbsp; {label} &mdash; Muestra Aleatoria de Trayectoria
        </td>
      </tr>
    </table>"""

    # ── Joint values badge ──────────────────────────────────────────────
    badge = f"""
    <table width="100%" cellspacing="0" cellpadding="0"
           style="margin-bottom:8px;">
      <tr bgcolor="#e8f0fe">
        <td style="padding:5px 10px; border-left:4px solid #1a73e8;
                   font-family:'Courier New',monospace; font-size:10px; color:#202124;">
          <b>Articulaciones [rad]:</b>&nbsp; {joints_txt}
        </td>
      </tr>
    </table>"""

    # ── Images side by side ─────────────────────────────────────────────
    images = f"""
    <table width="100%" cellspacing="0" cellpadding="6">
      <tr>
        <td width="50%" align="center" valign="top">
          {sim_img}
          <br>
          <b style="font-size:10px; color:#3c4043;">Simulador PyBullet (Estado Real)</b>
        </td>
        <td width="50%" align="center" valign="top">
          {wire_img}
          <br>
          <b style="font-size:10px; color:#3c4043;">Reconstrucci&oacute;n Anal&iacute;tica (6 Eslabones)</b>
        </td>
      </tr>
    </table>"""

    # ── Matrices side by side ───────────────────────────────────────────
    matrices = f"""
    <table width="100%" cellspacing="0" cellpadding="0">
      <tr>
        <td width="56%" valign="top" style="padding-right:8px;">
          {t_tbl}
        </td>
        <td width="44%" valign="top">
          {r_tbl}
          <br>
          {e_tbl}
        </td>
      </tr>
    </table>"""

    divider = "<hr style='border:none; border-top:1px solid #dadce0; margin:14px 0;'>"

    return title + badge + images + matrices + divider


# ──────────────────────────────────────────────────────────────────────────────
# Matrix table builders
# ──────────────────────────────────────────────────────────────────────────────

def _header_row(label, color="#1a73e8"):
    return (
        f"<tr>"
        f"<td colspan='4' style='background-color:{color}; color:#ffffff; "
        f"font-weight:bold; font-size:10px; padding:4px 6px;'>"
        f"{label}</td></tr>"
    )

def _t_matrix(T):
    col_headers = ["col-1", "col-2", "col-3", "Posición [m]"]
    row_headers = ["Fila 1", "Fila 2", "Fila 3", "Perspect."]
    th_style = "background-color:#e8eaed; font-size:9px; padding:3px 4px; text-align:center;"
    td_style = "border:1px solid #dadce0; font-family:'Courier New',monospace; font-size:10px; padding:3px 5px; text-align:center;"
    pos_style = "border:1px solid #1a73e8; background-color:#e8f0fe; font-weight:bold; color:#1a73e8; font-family:'Courier New',monospace; font-size:10px; padding:3px 5px; text-align:center;"

    # Column header row
    th_cells = f"<th style='{th_style}'>—</th>" + "".join(
        f"<th style='{th_style}'>{h}</th>" for h in col_headers
    )
    rows = f"<tr>{th_cells}</tr>"

    for ri, row in enumerate(T):
        cells = f"<td style='{th_style}'>{row_headers[ri]}</td>"
        for ci, v in enumerate(row):
            s = pos_style if ci == 3 else td_style
            fmt = f"{v:+.4f}" if ci == 3 else f"{v:+.3f}"
            cells += f"<td style='{s}'>{fmt}</td>"
        rows += f"<tr>{cells}</tr>"

    return (
        f"<b style='font-size:10px; color:#202124;'>Cinemática Directa — Matriz T [4×4, m]</b>"
        f"<table width='100%' cellspacing='0' cellpadding='0' style='border-collapse:collapse; margin-top:3px;'>"
        f"{rows}</table>"
    )


def _r_matrix(R):
    td_style = "border:1px solid #dadce0; font-family:'Courier New',monospace; font-size:10px; padding:3px 5px; text-align:center;"
    th_style = "background-color:#5f6368; color:#ffffff; font-size:9px; padding:3px 5px; text-align:center;"

    header = "<tr>" + "".join(
        f"<th style='{th_style}'>{h}</th>"
        for h in ["R₁ᵢ", "R₂ᵢ", "R₃ᵢ"]
    ) + "</tr>"
    rows = "".join(
        "<tr>" + "".join(f"<td style='{td_style}'>{v:+.3f}</td>" for v in row) + "</tr>"
        for row in R
    )
    return (
        f"<b style='font-size:10px; color:#202124;'>Matriz de Rotación R [3×3]</b>"
        f"<table width='100%' cellspacing='0' cellpadding='0' style='border-collapse:collapse; margin-top:3px;'>"
        f"{header}{rows}</table>"
    )


def _euler(angles):
    td_style = "border:1px solid #f5c6c2; background-color:#fce8e6; font-family:'Courier New',monospace; font-size:11px; padding:4px 6px; text-align:center; font-weight:bold; color:#d93025;"
    th_style = "background-color:#d93025; color:#ffffff; font-size:9px; padding:3px 5px; text-align:center;"

    header = "<tr>" + "".join(
        f"<th style='{th_style}'>{h}</th>"
        for h in ["Roll (X) [rad]", "Pitch (Y) [rad]", "Yaw (Z) [rad]"]
    ) + "</tr>"
    vals = "<tr>" + "".join(
        f"<td style='{td_style}'>{v:+.4f}</td>" for v in angles
    ) + "</tr>"
    return (
        f"<b style='font-size:10px; color:#202124;'>Ángulos de Euler ZYX</b>"
        f"<table width='100%' cellspacing='0' cellpadding='0' style='border-collapse:collapse; margin-top:3px;'>"
        f"{header}{vals}</table>"
    )


# ──────────────────────────────────────────────────────────────────────────────
# Image helpers — all base64 to avoid Windows file:// path issues
# ──────────────────────────────────────────────────────────────────────────────

def _b64_img(filename, width=100):
    """Logo from bundled resources — embedded as base64 data URI."""
    path = resource_path(filename)
    if not os.path.isfile(path):
        return f"<span style='color:#aaa; font-size:9px;'>[{filename}]</span>"
    ext = os.path.splitext(filename)[1].lstrip(".").lower()
    with open(path, "rb") as fh:
        data = base64.b64encode(fh.read()).decode("ascii")
    return f'<img src="data:image/{ext};base64,{data}" width="{width}">'


def _b64_img_from_file(filepath, width=300):
    """Snapshot PNG from absolute path — embedded as base64 data URI."""
    if not os.path.isfile(filepath):
        return f"<span style='color:#aaa;'>[imagen no disponible]</span>"
    with open(filepath, "rb") as fh:
        data = base64.b64encode(fh.read()).decode("ascii")
    return f'<img src="data:image/png;base64,{data}" width="{width}">'


def _cleanup_images(snapshots):
    for snap in snapshots:
        for key in ("sim_img", "wire_img"):
            try:
                os.remove(snap[key])
            except OSError:
                pass
