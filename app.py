```
import streamlit as st
import pandas as pd
import io
from datetime import date
from reportlab.lib.pagesizes import LETTER
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable

# Konfigurasi Halaman Streamlit
st.set_page_config(page_title="Audit Internal LSP Pertanian Presisi", page_icon="🌱", layout="wide")

st.markdown("<h1>🌱 Aplikasi Audit Internal LSP Pertanian Presisi</h1>", unsafe_allow_html=True)
st.markdown("### Instrumen Evaluasi Kesesuaian Pedoman BNSP 201 &amp; ISO 19011")

# Sidebar Parameter Audit
st.sidebar.header("📋 Parameter Audit")
lsp_nama = st.sidebar.text_input("Nama LSP", "LSP Pertanian Presisi")
lsp_alamat = st.sidebar.text_area("Alamat", "Jl. Tol Gempol – Pasuruan Kedungringin Selatan, RT 20 RW 06 Beji, Pasuruan INDONESIA")
tgl_audit = st.sidebar.date_input("Tanggal Audit", date(2026, 9, 26))
auditor_lead = st.sidebar.text_input("Ketua Tim Auditor", "Erlita Ratna Asih, STP.")
ketua_lsp = st.sidebar.text_input("Ketua LSP", "Dr. Ir. Eko Murniyanto, MP.")

# Data Checklist Default
if "checklists" not in st.session_state:
    st.session_state["checklists"] = {
        "Mutu": [
            {"klausul": "PBNSP 201 - 10.6", "item": "SOP Pengendalian Dokumen &amp; Rekaman", "status": "Sesuai", "catatan": "Dokumen edisi terkini tersedia."},
            {"klausul": "PBNSP 201 - 10.6", "item": "SOP Audit Internal &amp; Kaji Ulang Manajemen", "status": "Sesuai", "catatan": "Program &amp; SK Penunjukan 2026 lengkap."}
        ],
        "Sertifikasi": [
            {"klausul": "PBNSP 201 - 8 &amp; 9", "item": "Skema Sertifikasi &amp; Perangkat Asesmen (MUK)", "status": "Sesuai", "catatan": "MUK tersimpan dalam Brankas terkunci."},
            {"klausul": "PBNSP 201 - 6.4", "item": "SOP Verifikasi TUK", "status": "Minor NC", "catatan": "1 Berita Acara TUK sewaktu belum stempel basah."}
        ],
        "Administrasi": [
            {"klausul": "PBNSP 201 - 7.1", "item": "Pengendalian Rekaman Persuratan &amp; Asesi", "status": "Observasi", "catatan": "Perlu penambahan folder tertutup di rak."}
        ],
        "Keuangan": [
            {"klausul": "PBNSP 201 &amp; 202", "item": "Tata Kelola &amp; Pelaporan Keuangan", "status": "Sesuai", "catatan": "Pencatatan keuangan tertib &amp; transparan."}
        ]
    }

tab1, tab2, tab3 = st.tabs(["📊 Score Compliance", "📝 Isian Form Audit", "📥 Download Laporan PDF"])

with tab1:
    all_items = [it for dept in st.session_state["checklists"].values() for it in dept]
    total = len(all_items)
    sesuai = sum(1 for x in all_items if x["status"] == "Sesuai")
    score = round((sesuai / total) * 100, 1) if total &gt; 0 else 0
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Compliance Score", f"{score}%")
    col2.metric("Sesuai (S)", sesuai)
    col3.metric("Ketidaksesuaian / Obs", total - sesuai)

with tab2:
    dept_choice = st.selectbox("Pilih Bagian/Unit:", list(st.session_state["checklists"].keys()))
    items = st.session_state["checklists"][dept_choice]
    updated = []
    for i, it in enumerate(items):
        st.write(f"**{it['item']}** ({it['klausul']})")
        c1, c2 = st.columns(2)
        st_val = c1.selectbox(f"Status #{i+1}", ["Sesuai", "Minor NC", "Major NC", "Observasi"], index=["Sesuai", "Minor NC", "Major NC", "Observasi"].index(it["status"]))
        cat_val = c2.text_input(f"Catatan/Bukti #{i+1}", value=it["catatan"])
        updated.append({"klausul": it["klausul"], "item": it["item"], "status": st_val, "catatan": cat_val})
    st.session_state["checklists"][dept_choice] = updated

with tab3:
    st.write("Cetak dokumen resmi dalam bentuk PDF:")
    def make_pdf():
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=LETTER, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
        styles = getSampleStyleSheet()
        story = []
        
        story.append(Paragraph(f"<b>{lsp_nama.upper()}</b>", ParagraphStyle('T', fontName='Helvetica-Bold', fontSize=14, alignment=TA_CENTER)))
        story.append(Paragraph(f"{lsp_alamat}", ParagraphStyle('S', fontName='Helvetica', fontSize=8, alignment=TA_CENTER)))
        story.append(HRFlowable(width="100%", thickness=1, color=HexColor('#1b4332'), spaceAfter=10))
        story.append(Paragraph("<b>LAPORAN AUDIT INTERNAL SISTEM MANAJEMEN MUTU</b>", ParagraphStyle('T2', fontName='Helvetica-Bold', fontSize=11, alignment=TA_CENTER)))
        story.append(Spacer(1, 10))
        
        rows = [[Paragraph("<b>Unit</b>", styles['Normal']), Paragraph("<b>Item SOP</b>", styles['Normal']), Paragraph("<b>Status</b>", styles['Normal']), Paragraph("<b>Catatan</b>", styles['Normal'])]]
        for dept, list_it in st.session_state["checklists"].items():
            for it in list_it:
                rows.append([Paragraph(dept, styles['Normal']), Paragraph(it["item"], styles['Normal']), Paragraph(it["status"], styles['Normal']), Paragraph(it["catatan"], styles['Normal'])])
        
        t = Table(rows, colWidths=[100, 180, 80, 180])
        t.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 0.5, colors.grey), ('BACKGROUND', (0,0), (-1,0), colors.lightgrey)]))
        story.append(t)
        doc.build(story)
        buf.seek(0)
        return buf.getvalue()

    st.download_button("📥 Unduh Laporan PDF", data=make_pdf(), file_name="Laporan_Audit_LSP_Pertanian_Presisi.pdf", mime="application/pdf")

```
