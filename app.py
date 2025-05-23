
import streamlit as st
from fpdf import FPDF
from datetime import datetime
from streamlit_drawable_canvas import st_canvas
import base64
import os
import tempfile
from PIL import Image

st.set_page_config(page_title="Honey Batch Entry Form", layout="wide")
st.title("\U0001F36F Honey Batch Entry Form")

# --- Section: Batch Info ---
st.header("Batch Information")
col1, col2, col3 = st.columns(3)
with col1:
    batch_date = st.date_input("Date in Hot Room", value=datetime.today())
with col2:
    batch_number = st.text_input("Batch Number")
with col3:
    product_description = st.text_input("Product Description (e.g. MGO 406)")

# --- Section: Tipping Details ---
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

# --- Section: Drums Used ---
st.header("Drum Details")
num_drums = st.number_input("Number of Drums", min_value=1, max_value=10, step=1)
drum_data = []
for i in range(num_drums):
    with st.expander(f"Drum {i+1}"):
        drum_id = st.text_input(f"Drum ID {i+1}")
        rmp_code = st.text_input(f"RMP Code {i+1}")
        drum_weight = st.number_input(f"Weight (Kg) {i+1}", min_value=0.0)
        mgo_detail = st.text_input(f"MGO Detail {i+1}")
        drum_data.append((drum_id, rmp_code, drum_weight, mgo_detail))

# --- Section: Weight Monitoring ---
st.header("Weight Monitoring")
pallets = st.number_input("Number of Pallets", min_value=1, max_value=3)
weight_monitoring = []
for p in range(pallets):
    with st.expander(f"Pallet {p+1} Weights"):
        for layer in range(1, 12):
            row = st.columns(5)
            row_values = [row[i].number_input(f"P{p+1} L{layer} Head {i+1}", key=f"p{p+1}l{layer}h{i+1}", step=1) for i in range(4)]
            weight_monitoring.append((p+1, layer, *row_values))

# --- Section: X-ray Checks ---
st.header("X-Ray Challenge Tests")
xray_checks = []
xray_times = ["09:00", "11:00", "13:00", "15:00"]
for time in xray_times:
    with st.expander(f"Time: {time}"):
        ss = st.radio(f"Stainless Steel Pass @ {time}?", ["Yes", "No"], horizontal=True)
        gl = st.radio(f"Glass Pass @ {time}?", ["Yes", "No"], horizontal=True)
        operator = st.text_input(f"Operator Initials @ {time}")
        xray_checks.append((time, ss, gl, operator))

# --- Section: Signature Capture ---
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

# --- Generate PDF ---
st.header("Save Form as PDF")
def generate_pdf():
    filename = f"honey_batch_{batch_number.replace('/', '_')}.pdf"
    temp_dir = tempfile.gettempdir()
    pdf_path = os.path.join(temp_dir, filename)
    sig_path = os.path.join(temp_dir, f"signature_{batch_number}.png")

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Honey Batch Entry Summary", ln=True, align='C')
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Date: {batch_date.strftime('%d/%m/%Y')} | Batch No: {batch_number} | Product: {product_description}", ln=True)
    pdf.cell(200, 10, txt=f"Tipping Date: {tipping_date.strftime('%d/%m/%Y')} | Start: {start_time} | End: {end_time}", ln=True)
    pdf.cell(200, 10, txt=f"Thermaliser: {thermaliser_flow} | Temp: {honey_temp}°C | Loss: {honey_loss} Kg | Operator: {operator_initials}", ln=True)
    pdf.ln(5)
    pdf.cell(200, 10, txt="Drum Details:", ln=True)
    for drum in drum_data:
        pdf.cell(200, 10, txt=f"Drum ID: {drum[0]} | RMP: {drum[1]} | Weight: {drum[2]} Kg | MGO: {drum[3]}", ln=True)

    pdf.add_page()
    pdf.cell(200, 10, txt="Weight Monitoring:", ln=True)
    for wm in weight_monitoring:
        pdf.cell(200, 10, txt=f"Pallet {wm[0]} Layer {wm[1]} Weights: {wm[2]}, {wm[3]}, {wm[4]}, {wm[5]}", ln=True)

    pdf.add_page()
    pdf.cell(200, 10, txt="X-Ray Checks:", ln=True)
    for check in xray_checks:
        pdf.cell(200, 10, txt=f"Time: {check[0]} | Stainless Steel: {check[1]} | Glass: {check[2]} | Operator: {check[3]}", ln=True)

    if canvas_result.image_data is not None:
        img = Image.fromarray(canvas_result.image_data.astype('uint8'), 'RGBA')
        img.save(sig_path)
        pdf.image(sig_path, x=10, y=250, w=60)

    pdf.output(pdf_path)
    return pdf_path

if st.button("Generate PDF"):
    file_path = generate_pdf()
    st.success(f"PDF generated successfully!")
    st.markdown(f'''✅ Your PDF has been successfully generated!

**Save location on server (temporary):**
`{}`

If you're running this app locally, the file is saved in your system's temporary directory.
If you're on Streamlit Cloud, please use the **Download PDF** button below to save it to your device.'''.format(file_path))
    with open(file_path, "rb") as f:
        st.download_button(label="Download PDF", file_name=os.path.basename(file_path), data=f.read())
