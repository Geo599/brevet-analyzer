
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
    images = convert_from_bytes(pdf_file.read(), dpi=300)
    img = images[0]
    counts = count_colors(img, color_refs)
    if sum(counts.values()) == 0:
        return "Erreur : aucune couleur détectée", ""
    dominant = max(counts.items(), key=lambda x: x[1])[0]
    score = color_score_map[dominant]
    total_score = int(score * len(competences))
    note_sur_20 = round((total_score / 400) * 20, 2)
    return f"{total_score} / 400", f"{note_sur_20} / 20"

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
        pdf_input = gr.File(label="Téléverser un PDF")
        score400_pdf = gr.Textbox(label="Points (PDF)")
        score20_pdf = gr.Textbox(label="Note sur 20 (PDF)")
        pdf_btn = gr.Button("Analyser PDF")
        pdf_btn.click(fn=process_pdf, inputs=pdf_input, outputs=[score400_pdf, score20_pdf])

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
