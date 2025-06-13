
import gradio as gr
import fitz  # PyMuPDF
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

symbol_map = {
    "🟢➕": 50,  # Très bonne maîtrise
    "🟢": 40,   # Maîtrise satisfaisante
    "🟡": 25,   # Maîtrise fragile
    "🟠": 10    # Maîtrise insuffisante
}

def process_pdf_symbols(pdf_file):
    try:
        with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
            text = ""
            for page in doc:
                text += page.get_text()

        symbol_counts = {k: text.count(k) for k in symbol_map}
        total_symbols = sum(symbol_counts.values())

        if total_symbols == 0:
            return "Aucun symbole détecté", ""

        dominant = max(symbol_counts.items(), key=lambda x: x[1])[0]
        score = symbol_map[dominant]
        total_score = int(score * len(competences))
        note_sur_20 = round((total_score / 400) * 20, 2)

        return f"{total_score} / 400", f"{note_sur_20} / 20"

    except Exception as e:
        print("Erreur lors de la lecture du PDF:", e)
        return "Erreur PDF", ""

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
    gr.Markdown("## 🎓 Calcul du Contrôle Continu du Brevet (Détection par symbole)")

    with gr.Tab("📄 Analyse PDF"):
        pdf_input = gr.File(label="Téléverser un PDF contenant les symboles 🟢➕ 🟢 🟡 🟠", file_types=[".pdf"])
        score400_pdf = gr.Textbox(label="Points (PDF)")
        score20_pdf = gr.Textbox(label="Note sur 20 (PDF)")
        pdf_btn = gr.Button("Analyser le PDF")
        pdf_btn.click(fn=process_pdf_symbols, inputs=pdf_input, outputs=[score400_pdf, score20_pdf])

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
