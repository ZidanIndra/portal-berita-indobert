import html
import json
import os
import re
import unicodedata
from flask import Flask, jsonify, request, send_from_directory
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOCAL_MODEL_DIR = os.path.join(BASE_DIR, "model_indobert")
HF_MODEL_ID = "zidanindraa2/indobert-klasifikasi-berita"

# Prioritaskan bobot lokal jika tersedia, atau unduh otomatis dari Hugging Face Hub
if os.path.exists(LOCAL_MODEL_DIR) and (
    os.path.exists(os.path.join(LOCAL_MODEL_DIR, "model.safetensors"))
    or os.path.exists(os.path.join(LOCAL_MODEL_DIR, "pytorch_model.bin"))
):
    MODEL_PATH = LOCAL_MODEL_DIR
else:
    alt_path = os.path.join(BASE_DIR, "model_indoBERT")
    if os.path.exists(alt_path) and (
        os.path.exists(os.path.join(alt_path, "model.safetensors"))
        or os.path.exists(os.path.join(alt_path, "pytorch_model.bin"))
    ):
        MODEL_PATH = alt_path
    else:
        MODEL_PATH = HF_MODEL_ID

# Label mapping default & loader
DEFAULT_LABELS = {
    0: "Ekonomi",
    1: "Hukum",
    2: "Olahraga",
    3: "Pendidikan",
    4: "Politik",
}

label_file = os.path.join(MODEL_PATH, "label_mapping.json")
if os.path.exists(label_file):
    try:
        with open(label_file, "r", encoding="utf-8") as f:
            mapping = json.load(f)
            LABELS = {int(k): v for k, v in mapping.get("id2label", {}).items()}
    except Exception:
        LABELS = DEFAULT_LABELS
else:
    LABELS = DEFAULT_LABELS

# Regex prekompilasi untuk preprocessing
BOILERPLATE_INLINE_RE = re.compile(
    r"(?i)\b(?:baca\s+juga\s*:|editor\s*:|ayo\s+baca\b|tags\b|komentar\b).*"
)
EMPTY_MARKDOWN_TABLE_RE = re.compile(
    r"(?ms)^\s*\|\s*(?:\xa0|&nbsp;)?\s*\|\s*\|\s*\|\s*\|\s*\n"
    r"\s*\|\s*-+\s*\|\s*-+\s*\|\s*-+\s*\|\s*-+\s*\|\s*-+\s*\|\s*$"
)
URL_RE = re.compile(r"https?://\S+|www\.\S+", re.I)
CTRL_RE = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]")


def clean_title(raw_title: str) -> str:
    if not raw_title:
        return ""
    text = html.unescape(str(raw_title))
    return unicodedata.normalize("NFKC", text).strip()


def clean_text(raw_text: str) -> str:
    if not raw_text:
        return ""
    text = html.unescape(str(raw_text))
    text = unicodedata.normalize("NFKC", text)
    text = EMPTY_MARKDOWN_TABLE_RE.sub("\n", text)
    text = BOILERPLATE_INLINE_RE.sub("", text)
    text = URL_RE.sub(" ", text)
    text = CTRL_RE.sub(" ", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n", text)
    text = re.sub(r"(?:\*{2,}|#{2,})\s*$", "", text)
    return text.strip()


print("Memuat tokenizer dari:", MODEL_PATH)
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)

print("Memuat model IndoBERT dari:", MODEL_PATH)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
model.eval()

print("Model IndoBERT siap. Device:", device)

# Inisialisasi Flask dengan static serving dari BASE_DIR
app = Flask(__name__, static_folder=BASE_DIR, static_url_path="")


# ponytail: CORS headers via after_request - simple and zero external dependency
@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    return response


@app.route("/")
def home():
    return send_from_directory(BASE_DIR, "index.html")


@app.route("/prediksi", methods=["POST", "OPTIONS"])
def prediksi():
    if request.method == "OPTIONS":
        return "", 204

    data = request.get_json(silent=True) or {}
    raw_judul = data.get("judul", "")
    raw_isi = data.get("isi", "") or data.get("teks", "")

    judul_clean = clean_title(raw_judul)
    isi_clean = clean_text(raw_isi)

    if not isi_clean:
        return jsonify({"error": "Isi berita tidak boleh kosong."}), 400

    if judul_clean:
        inputs = tokenizer(
            judul_clean,
            isi_clean,
            truncation=True,
            max_length=512,
            return_tensors="pt",
        )
    else:
        inputs = tokenizer(
            isi_clean,
            truncation=True,
            max_length=512,
            return_tensors="pt",
        )

    token_count = int(inputs["input_ids"].shape[1])
    device_inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model(**device_inputs)

    probs = torch.softmax(outputs.logits, dim=1)[0]
    confidence, predicted_idx = torch.max(probs, dim=0)

    predicted_label = LABELS.get(predicted_idx.item(), f"Kelas_{predicted_idx.item()}")
    confidence_val = round(float(confidence.item() * 100), 2)

    probabilities = {
        LABELS.get(i, f"Kelas_{i}"): round(float(probs[i].item() * 100), 2)
        for i in range(len(LABELS))
    }

    metadata = {
        "token_count": token_count,
        "tokens_length": token_count,
        "device": str(device),
        "model_name": "indobenchmark/indobert-base-p1",
        "input_mode": "title_content_pair" if judul_clean else "content_only",
    }

    return jsonify({
        "kategori": predicted_label,
        "confidence": confidence_val,
        "probabilities": probabilities,
        "metadata": metadata,
    })


@app.route("/admin")
@app.route("/admin/")
def admin_page():
    return send_from_directory(BASE_DIR, "admin.html")


if __name__ == "__main__":
    app.run(debug=True, port=5000)
