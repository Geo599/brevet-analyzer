
import gradio as gr
from pdf2image import convert_from_bytes
from PIL import Image
import numpy as np
import fitz  # for text (emoji symbol) detection

# --- Settings ---
competences = [
    "Langue française", "Langue étrangère", "Mathématiques et sciences", "Arts et corps",
    "Méthodes et outils", "Citoyenneté", "Sciences techniques", "Représentation du monde"
]

# Color and symbol mappings
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
    "Maîtrise insuffisante (orange)": (255, 165, 0)
}

symbol_score_map = {
    "🟢➕": 50,
    "🟢": 40,
    "🟡": 25,
    "🟠": 10
}

# --- Color analysis ---
def count_colors(img, color_defs, tolerance=40):
    img_np = np.array(img)
    counts = {}
    for label, rgb_ref in color_defs.items():
        dist = np.sqrt(np.sum((img_np - rgb_ref) ** 2, axis=2))
        match_pixels = dist < tolerance
        counts[label] = int(np.sum(match_pixels))
    return counts

def process_color_based(content):
    images = convert_from_bytes(content, dpi=300)
    img = images[0]
    counts = count_colors(img, color_refs)
    if sum(counts.values()) == 0:
        return None  # fallback to symbol
    dominant = max(counts.items(), key=lambda x: x[1])[0]
    return color_score_map[dominant]

# --- Symbol-based fallback ---
def process_symbol_based(content):
    try:
        with fitz.open(stream=content, filetype="pdf") as doc:
            text = "".join([page.get_text() for page in doc])
        counts = {s: text.count(s) for s in symbol_score_map}
        if sum(counts.values()) == 0:
            return None
        dominant = max(counts.items(), key=lambda x: x[1])[0]
        return symbol_score_map[dominant]
    except Exception as e:
        print("Symbol detection failed:", e)
        return None

# --- Combined scoring logic ---
def detect_score(pdf_file):
    content = pdf_file.read()
    color_score = process_color_based(content)
    if color_score is not None:
        return color_score
    symbol_score = process_symbol_based(content)
    if symbol_score is not None:
        return symbol_score
    return 0

def analyze_two_pdfs(pdf1, pdf2):
    score1 = detect_score(pdf1) if pdf1 else 0
    score2 = detect_score(pdf2) if pdf2 else 0
    if score1 == 0 and score2 == 0:
        return "Aucun résultat détecté", ""
    avg = (score1 + score2) / 2 if pdf1 and pdf2 else score1 if pdf1 else score2
    total = round(avg * len(competences))
    note = round((total / 400) * 20, 2)
    return f"{total} / 400", f"{note} / 20"

# --- Manual fallback ---
def niveau_vers_points(niveau):
    return {
        "Très bonne maîtrise": 50,
        "Maîtrise satisfaisante": 40,
        "Maîtrise fragile": 25,
        "Maîtrise insuffisante": 10
    }.get(niveau, 0)

def calculer_manuel(*args):
    sem1 = args[:8]
    sem2 = args[8:]
    total = sum((niveau_vers_points(s1) + niveau_vers_points(s2)) / 2 for s1, s2 in zip(sem1, sem2))
    note = round((total / 400) * 20, 2)
    return f"{int(total)} / 400", f"{note} / 20"

# --- Gradio App ---
niveau_choices = list(niveau_vers_points("").keys())

with gr.Blocks() as demo:
    gr.Markdown("## 🎓 Calcul du Contrôle Continu du Brevet")

    with gr.Tab("📄 PDF Upload (couleurs ou symboles)"):
        with gr.Row():
            pdf_input_1 = gr.File(label="📘 PDF Semestre 1", file_types=[".pdf"])
            pdf_input_2 = gr.File(label="📗 PDF Semestre 2", file_types=[".pdf"])
        score400 = gr.Textbox(label="Points détectés")
        score20 = gr.Textbox(label="Note sur 20")
        run_btn = gr.Button("Analyser les PDFs")
        run_btn.click(analyze_two_pdfs, inputs=[pdf_input_1, pdf_input_2], outputs=[score400, score20])

    with gr.Tab("✍️ Saisie manuelle"):
        gr.Markdown("### Entrez les niveaux par compétence (2 semestres)")
        sem1_inputs, sem2_inputs = [], []
        for comp in competences:
            with gr.Row():
                s1 = gr.Dropdown(niveau_choices, label=f"{comp} - S1", scale=1)
                s2 = gr.Dropdown(niveau_choices, label=f"{comp} - S2", scale=1)
                sem1_inputs.append(s1)
                sem2_inputs.append(s2)

        score400_manual = gr.Textbox(label="Total des points (manuel)")
        score20_manual = gr.Textbox(label="Note sur 20 (manuel)")
        calc_btn = gr.Button("Calculer")
        calc_btn.click(fn=calculer_manuel, inputs=[*sem1_inputs, *sem2_inputs], outputs=[score400_manual, score20_manual])

demo.launch(server_name="0.0.0.0", server_port=7860)
