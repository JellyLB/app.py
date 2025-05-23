
import streamlit as st
from fpdf import FPDF
from datetime import datetime
from streamlit_drawable_canvas import st_canvas
import os
import tempfile
from PIL import Image

class CleanHoneyBatchReport(FPDF):
    def header(self):
        self.set_fill_color(30, 60, 90)
        self.set_text_color(255, 255, 255)
        self.set_font("Arial", "B", 16)
        self.cell(0, 12, "HONEY BATCH MANUFACTURING REPORT", ln=True, align="C", fill=True)
        self.ln(6)

    def section_title(self, title):
        self.set_fill_color(220, 230, 240)
        self.set_text_color(0)
        self.set_font("Arial", "B", 13)
        self.cell(0, 10, f"{title}", ln=True, fill=True)
        self.ln(1)

    def field_row(self, fields, widths=None):
        self.set_font("Arial", "", 11)
        if widths is None:
            widths = [60] * len(fields)
        for field, width in zip(fields, widths):
            self.cell(width, 8, field, border=1)
        self.ln()

    def add_batch_info(self, date, number, product):
        self.section_title("Batch Information")
        self.field_row([f"Date: {date}", f"Batch No: {number}", f"Product: {product}"], [60, 65, 65])

    def add_tipping_details(self, tipping_date, start, end, flow, temp, loss, operator, visual):
        self.section_title("Tipping Details")
        self.field_row([f"Tipping Date: {tipping_date}", f"Start: {start}", f"End: {end}"], [60, 65, 65])
        self.field_row([f"Thermaliser: {flow}", f"Temp: {temp}°C", f"Loss: {loss} Kg"], [60, 65, 65])
        self.field_row([f"Operator: {operator}", f"Visual Check: {visual}", ""], [60, 65, 65])

    def add_drum_details(self, drums):
        self.section_title("Drum Details")
        self.set_font("Arial", "B", 11)
        headers = ["Drum ID", "RMP Code", "Weight", "MGO"]
        self.field_row(headers, [40, 50, 40, 50])
        self.set_font("Arial", "", 11)
        for row in drums:
            self.field_row(row, [40, 50, 40, 50])

    def add_signature_footer(self):
        self.ln(12)
        self.set_font("Arial", "I", 11)
        self.cell(0, 10, "Approved By: _______________________     Date: ________________", ln=True, align="L")
        self.cell(0, 10, "Signature:    _______________________", ln=True, align="L")

st.set_page_config(page_title="Honey Batch Entry Form", layout="wide")
st.title("🍯 Honey Batch Entry Form")

st.header("Batch Information")
col1, col2, col3 = st.columns(3)
with col1:
    batch_date = st.date_input("Date in Hot Room", value=datetime.today())
with col2:
    batch_number = st.text_input("Batch Number")
with col3:
    product_description = st.text_input("Product Description (e.g. MGO 406)")

st.header("Tipping Details")
col1, col2 = st.columns(2)
with col1:
    tipping_date = st.date_input("Tipping Date")
    start_time = st.time_input("Start Time")
    end_time = st.time_input("End Time")
    honey_temp = st.number_input("Honey Temp. on completion (°C)", min_value=0.0, step=0.1)
with col2:
    thermaliser_flow = st.text_input("Thermaliser Flow Rate (Kg/hr)")
    honey_loss = st.text_input("Honey Lost/Spilled (Kg)")
    pig_visual_check = st.text_input("Pig Visual Check Initials")
    operator_initials = st.text_input("Operator Initials")

st.header("Drum Details")
num_drums = st.number_input("Number of Drums", min_value=1, max_value=10, step=1)
drum_data = []
for i in range(num_drums):
    with st.expander(f"Drum {i+1}"):
        drum_id = st.text_input(f"Drum ID {i+1}", key=f"drum_id_{i}")
        rmp_code = st.text_input(f"RMP Code {i+1}", key=f"rmp_code_{i}")
        drum_weight = st.number_input(f"Weight (Kg) {i+1}", key=f"weight_{i}", min_value=0.0)
        mgo_detail = st.text_input(f"MGO Detail {i+1}", key=f"mgo_detail_{i}")
        drum_data.append((drum_id, rmp_code, drum_weight, mgo_detail))

st.header("Production Manager Signature")
canvas_result = st_canvas(
    fill_color="#000000",
    stroke_width=2,
    stroke_color="#000000",
    background_color="#ffffff",
    height=150,
    width=400,
    drawing_mode="freedraw",
    key="canvas"
)

st.header("Save Form as PDF")
def generate_pdf():
    filename = f"honey_batch_{batch_number.replace('/', '_')}.pdf"
    temp_dir = tempfile.gettempdir()
    pdf_path = os.path.join(temp_dir, filename)

    pdf = CleanHoneyBatchReport()
    pdf.add_page()
    pdf.add_batch_info(batch_date.strftime('%d/%m/%Y'), batch_number, product_description)
    pdf.add_tipping_details(tipping_date.strftime('%d/%m/%Y'), start_time.strftime('%H:%M'), end_time.strftime('%H:%M'), thermaliser_flow, honey_temp, honey_loss, operator_initials, pig_visual_check)
    drum_rows = [[d[0], d[1], f"{d[2]} Kg", d[3]] for d in drum_data]
    pdf.add_drum_details(drum_rows)
    pdf.add_signature_footer()

    if canvas_result.image_data is not None:
        sig_path = os.path.join(temp_dir, f"signature_{batch_number}.png")
        img = Image.fromarray(canvas_result.image_data.astype('uint8'), 'RGBA')
        img.save(sig_path)
        pdf.image(sig_path, x=140, y=pdf.get_y(), w=60)

    pdf.output(pdf_path)
    return pdf_path

if st.button("Generate PDF"):
    file_path = generate_pdf()
    st.success("PDF generated successfully!")
    st.markdown(f"""
✅ **PDF File Generated**

**Temporary Save Location:**
```
{file_path}
```

> Use the **Download PDF** button below to save it to your computer.
""")
    with open(file_path, "rb") as f:
        st.download_button(label="Download PDF", file_name=os.path.basename(file_path), data=f.read())
