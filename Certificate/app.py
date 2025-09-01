from flask import Flask, render_template, request, send_file
from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import io
import os

app = Flask(__name__)

# Load participant data
df = pd.read_csv("participants.csv", encoding='utf-8-sig')  # CSV columns: bib_no,name,distance

@app.route('/')
def home():
    return render_template("index.html")  # HTML form to input Bib No.
@app.route("/generate", methods=["POST"])
def generate_certificate():
    bib_no = request.form.get("bib_no")
    
    # Load participants
    participants = pd.read_csv("participants.csv")
    participant = participants[participants["bib_no"] == int(bib_no)]

    if participant.empty:
        return "Bib number not found!"

    name = participant.iloc[0]["name"]
    distance = participant.iloc[0]["distance"]

    # Load certificate template
    img = Image.open("certificate_template.jpg")
    draw = ImageDraw.Draw(img)

    # Load fonts safely with fallback
    try:
        font_path = os.path.join("fonts", "DejaVuSans-Bold.ttf")
        font_large = ImageFont.truetype(font_path, 56)   # For Name
        font_medium = ImageFont.truetype(font_path, 40)  # For Distance
    except OSError:
        try:
            font_large = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 56)
            font_medium = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 40)
            print("Custom font failed. Using Arial.")
        except OSError:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            print("No TTF font found. Using default font.")

    # --- Draw Name (centered, slightly above middle) ---
    w, h = img.size
    name_text = name.upper()
    bbox_name = draw.textbbox((0, 0), name_text, font=font_large)
    w_name = bbox_name[2] - bbox_name[0]
    h_name = bbox_name[3] - bbox_name[1]
    x_name = (w - w_name) / 2
    y_name = int(h * 0.60)   # Move name higher
    draw.text((x_name, y_name), name_text, font=font_large, fill="black")

    # --- Draw Completion Line (below name) ---
    completion_text = f"Has Successfully Completed the {distance}"
    bbox_dist = draw.textbbox((0, 0), completion_text, font=font_medium)
    w_dist = bbox_dist[2] - bbox_dist[0]
    h_dist = bbox_dist[3] - bbox_dist[1]
    x_dist = (w - w_dist) / 2
    y_dist = y_name + h_name + 40   # 20px gap below name
    draw.text((x_dist, y_dist), completion_text, font=font_medium, fill="black")

    # Save certificate to memory
    img_io = io.BytesIO()
    img.save(img_io, "PNG")
    img_io.seek(0)

    # Send file as download
    return send_file(
        img_io,
        mimetype="image/png",
        as_attachment=True,
        attachment_filename=f"{name}_certificate.png"  # use attachment_filename for Flask<2.0
    )


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=True)

