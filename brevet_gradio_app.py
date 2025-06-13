
import gradio as gr
from pdf2image import convert_from_bytes
from PIL import Image
import numpy as np

competences = [
    "Langue française",
    "Langue étrangère",
    "Mathématiques et sciences",
    "Arts et corps",
    "Méthodes et outils",
    "Citoyenneté",
    "Sciences techniques",
    "Représentation du monde"
]

color_score_map = {
    "Très bonne maîtrise (dark green)": 50,
    "Maîtrise satisfaisante (light green)": 40,
    "Maîtrise fragile (yellow)": 25,
    "Maîtrise insuffisante (orange)": 10
}

color_refs = {
    "Très bonne maîtrise (dark green)": (0, 100, 0),
    "Maîtrise satisfaisante (light green)": (144, 238, 144),
    "Maîtrise fragile (yellow)": (255, 255, 0),
    "Maîtrise insuffisante (orange)": (245, 130, 32)
}

def count_colors(img, color_defs, tolerance=80):
    img_np = np.array(img)
    counts = {}
    for label, rgb_ref in color_defs.items():
        dist = np.sqrt(np.sum((img_np - rgb_ref) ** 2, axis=2))
        match_pixels = dist < tolerance
        counts[label] = int(np.sum(match_pixels))
    return counts

def process_pdf(pdf_file):
    try:
        content = pdf_file.read()
        if not content:
            return 0
        images = convert_from_bytes(content, dpi=300)
        img = images[0]
        counts = count_colors(img, color_refs)
        if sum(counts.values()) == 0:
            return 0
        dominant = max(counts.items(), key=lambda x: x[1])[0]
        return color_score_map[dominant]
    except Exception as e:
        print("Erreur PDF:", e)
        return 0

def dual_pdf_upload(pdf1, pdf2):
    score1 = process_pdf(pdf1) if pdf1 else 0
    score2 = process_pdf(pdf2) if pdf2 else 0
    if score1 == 0 and score2 == 0:
        return "Aucune couleur détectée", ""
    avg = (score1 + score2) / 2 if pdf1 and pdf2 else score1 if pdf1 else score2
    total = int(avg * len(competences))
    note = round((total / 400) * 20, 2)
    return f"{total} / 400", f"{note} / 20"

niveau_choices = ["Très bonne maîtrise", "Maîtrise satisfaisante", "Maîtrise fragile", "Maîtrise insuffisante"]

def niveau_vers_points(niveau):
    mapping = {
        "Très bonne maîtrise": 50,
        "Maîtrise satisfaisante": 40,
        "Maîtrise fragile": 25,
        "Maîtrise insuffisante": 10
    }
    return mapping.get(niveau, 0)

def calculer_manuel(*args):
    sem1 = args[:8]
    sem2 = args[8:]
    total = 0
    for s1, s2 in zip(sem1, sem2):
        total += (niveau_vers_points(s1) + niveau_vers_points(s2)) / 2
    note_sur_20 = round((total / 400) * 20, 2)
    return f"{int(total)} / 400", f"{note_sur_20} / 20"

with gr.Blocks() as demo:
    gr.Markdown("## 🎓 Calcul du Contrôle Continu du Brevet")

    with gr.Tab("📄 Analyse PDF"):
        with gr.Row():
            pdf_input_1 = gr.File(label="📘 PDF Semestre 1", file_types=[".pdf"])
            pdf_input_2 = gr.File(label="📗 PDF Semestre 2", file_types=[".pdf"])
        score400_pdf = gr.Textbox(label="Points (PDF)")
        score20_pdf = gr.Textbox(label="Note sur 20 (PDF)")
        pdf_btn = gr.Button("Analyser")
        pdf_btn.click(fn=dual_pdf_upload, inputs=[pdf_input_1, pdf_input_2], outputs=[score400_pdf, score20_pdf])

    with gr.Tab("✍️ Entrée manuelle"):
        gr.Markdown("### Choisissez le niveau pour chaque compétence (Semestre 1 et 2)")
        sem1_inputs, sem2_inputs = [], []

        for comp in competences:
            with gr.Row():
                s1 = gr.Dropdown(niveau_choices, label=f"{comp} - S1", scale=1)
                s2 = gr.Dropdown(niveau_choices, label=f"{comp} - S2", scale=1)
                sem1_inputs.append(s1)
                sem2_inputs.append(s2)

        score400_manual = gr.Textbox(label="Points (manuel)")
        score20_manual = gr.Textbox(label="Note sur 20 (manuel)")
        calc_btn = gr.Button("Calculer")
        calc_btn.click(fn=calculer_manuel, inputs=[*sem1_inputs, *sem2_inputs], outputs=[score400_manual, score20_manual])

demo.launch(server_name="0.0.0.0", server_port=7860)
