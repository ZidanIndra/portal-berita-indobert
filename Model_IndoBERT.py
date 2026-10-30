# ==============================================================================
# MODEL INDOBERT - KLASIFIKASI BERITA
# Versi VS Code
# ==============================================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import torch
import re
import os
import time

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)

from transformers import AutoTokenizer, AutoModelForSequenceClassification
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from tqdm.auto import tqdm
from torch.utils.data import DataLoader
from torch.optim import AdamW


# ==============================================================================
# TAHAP 1: ANALISIS AWAL DAN PEMERIKSAAN DATASET
# ==============================================================================

print("\n" + "=" * 70)
print("TAHAP 1: ANALISIS AWAL DAN PEMERIKSAAN DATASET")
print("=" * 70)

print("\nPyTorch version :", torch.__version__)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

print("Device          :", device)

if torch.cuda.is_available():
    print("Nama GPU        :", torch.cuda.get_device_name(0))
else:
    print("GPU tidak tersedia, menggunakan CPU.")


# Membaca dataset
df = pd.read_excel("dataset_Berita(Fix).xlsx")

print("\nJumlah data  :", df.shape[0])
print("Jumlah kolom :", df.shape[1])

print("\n5 Data Pertama:")
print(df.head())

print("\nNama kolom:")
print(df.columns.tolist())

print("\nJumlah data kosong:")
print(df.isnull().sum())

print("\nJumlah data duplikat:", df.duplicated().sum())

print("\nKategori yang tersedia:")
print(df["Kategori"].unique())

print("\nJumlah berita setiap kategori:")
print(df["Kategori"].value_counts())


# ==============================================================================
# TAHAP 2: PERSIAPAN DATA AWAL
# ==============================================================================

print("\n" + "=" * 70)
print("TAHAP 2: PERSIAPAN DATA AWAL")
print("=" * 70)

# Menghapus 4 data bermasalah
index_bermasalah = [44, 45, 59, 66]

df = df.drop(
    index=index_bermasalah,
    errors="ignore"
).copy()

print("\nJumlah data setelah menghapus data bermasalah:", len(df))

# Membaca 4 data pengganti
df_pengganti = pd.read_excel(
    "dataset_berita-tambahan 4.xlsx"
)

print("Jumlah data pengganti:", len(df_pengganti))

# Menambahkan data pengganti
df = pd.concat(
    [df, df_pengganti],
    ignore_index=True
)

print("Jumlah data setelah penambahan:", len(df))

print("\nJumlah data setiap kategori:")
print(df["Kategori"].value_counts())


# ==============================================================================
# TAHAP 3: CLEANING DAN PREPROCESSING
# ==============================================================================

print("\n" + "=" * 70)
print("TAHAP 3: CLEANING DAN PREPROCESSING")
print("=" * 70)

# ------------------------------------------------------------------------------
# Cleaning
# ------------------------------------------------------------------------------

df["Isi Berita Bersih"] = df["Isi Berita"].copy()


def cleaning_teks(teks):

    teks = str(teks)

    teks = re.sub(
        r"Ayo baca konten menarik lainnya dan follow kami di Google News",
        " ",
        teks,
        flags=re.IGNORECASE
    )

    teks = re.sub(
        r"Baca Juga\s*:?",
        " ",
        teks,
        flags=re.IGNORECASE
    )

    teks = re.sub(
        r"Editor\s*:.*?(?=\n|$)",
        " ",
        teks,
        flags=re.IGNORECASE
    )

    teks = re.sub(
        r"Tags",
        " ",
        teks,
        flags=re.IGNORECASE
    )

    teks = re.sub(
        r"\bkomentar\b",
        " ",
        teks,
        flags=re.IGNORECASE
    )

    teks = re.sub(
        r"[\r\n\t]+",
        " ",
        teks
    )

    teks = re.sub(
        r"\s+",
        " ",
        teks
    )

    return teks.strip()


df["Isi Berita Bersih"] = df["Isi Berita"].apply(
    cleaning_teks
)

print("\nCleaning teks selesai.")


# ------------------------------------------------------------------------------
# Merapikan awal teks
# ------------------------------------------------------------------------------

def rapikan_awal_teks(teks):

    teks = str(teks)

    teks = re.sub(
        r"^[\s:;\-,]+",
        "",
        teks
    )

    return teks.strip()


df["Isi Berita Bersih"] = df["Isi Berita Bersih"].apply(
    rapikan_awal_teks
)

print("Perapian awal teks selesai.")


# ------------------------------------------------------------------------------
# Pemeriksaan hasil cleaning
# ------------------------------------------------------------------------------

kata_template = [
    "Ayo baca konten menarik lainnya",
    "Baca Juga",
    "Editor :",
    "Tags",
    "komentar"
]

print("\nPemeriksaan sisa template:")

for kata in kata_template:

    jumlah = df["Isi Berita Bersih"].str.contains(
        kata,
        case=False,
        na=False
    ).sum()

    print(
        f'Jumlah yang masih mengandung "{kata}": {jumlah}'
    )


jumlah_kosong = (
    df["Isi Berita Bersih"].isna()
    |
    (df["Isi Berita Bersih"].str.strip() == "")
).sum()

print(
    "\nJumlah berita kosong setelah cleaning:",
    jumlah_kosong
)


# ------------------------------------------------------------------------------
# Label
# ------------------------------------------------------------------------------

label_map = {
    "Ekonomi": 0,
    "Hukum": 1,
    "Olahraga": 2,
    "Pendidikan": 3,
    "Politik": 4
}

df["label"] = df["Kategori"].map(label_map)

print("\nPemetaan label:")
print(label_map)

print("\nJumlah label kosong:", df["label"].isna().sum())


# ------------------------------------------------------------------------------
# Case Folding
# ------------------------------------------------------------------------------

df["Teks Case Folding"] = (
    df["Isi Berita Bersih"].str.lower()
)

print("\nCase folding selesai.")


# ------------------------------------------------------------------------------
# Tokenizer IndoBERT
# ------------------------------------------------------------------------------

model_name = "indobenchmark/indobert-base-p1"

print("\nMemuat tokenizer IndoBERT...")
print("Model:", model_name)

tokenizer = AutoTokenizer.from_pretrained(
    model_name
)

print("Tokenizer IndoBERT berhasil dimuat.")


# ------------------------------------------------------------------------------
# Stopword Removal
# ------------------------------------------------------------------------------

print("\nMemulai stopword removal...")

factory = StopWordRemoverFactory()

stopword_remover = (
    factory.create_stop_word_remover()
)

df["Teks Stopword"] = df["Teks Case Folding"].apply(
    lambda x: stopword_remover.remove(x)
)

print("Stopword removal selesai.")


# ------------------------------------------------------------------------------
# Stemming
# ------------------------------------------------------------------------------

print("\nMemulai proses stemming...")

stemmer_factory = StemmerFactory()

stemmer = stemmer_factory.create_stemmer()

semua_kata = set()

for teks in df["Teks Stopword"]:

    semua_kata.update(
        teks.split()
    )

print(
    "Jumlah kata unik yang akan di-stemming:",
    len(semua_kata)
)


stem_cache = {}

for kata in tqdm(
    semua_kata,
    desc="Proses stemming"
):

    stem_cache[kata] = stemmer.stem(kata)


print("Stemming kata unik selesai.")


def stemming_cepat(teks):

    return " ".join(
        stem_cache.get(kata, kata)
        for kata in teks.split()
    )


df["Teks Stemming"] = df["Teks Stopword"].apply(
    stemming_cepat
)

print("Stemming selesai.")


# ==============================================================================
# TAHAP 4: PEMBAGIAN DATASET
# ==============================================================================

print("\n" + "=" * 70)
print("TAHAP 4: PEMBAGIAN DATASET")
print("=" * 70)

df_train, df_test = train_test_split(
    df,
    test_size=0.20,
    random_state=42,
    stratify=df["Kategori"]
)

df_train = df_train.reset_index(drop=True)

df_test = df_test.reset_index(drop=True)

print("\nJumlah data keseluruhan :", len(df))
print("Jumlah data training    :", len(df_train))
print("Jumlah data testing     :", len(df_test))

print("\nDistribusi DATA TRAINING:")
print(
    df_train["Kategori"].value_counts().sort_index()
)

print("\nDistribusi DATA TESTING:")
print(
    df_test["Kategori"].value_counts().sort_index()
)


# ==============================================================================
# TAHAP 5: TOKENISASI INDOBERT
# ==============================================================================

print("\n" + "=" * 70)
print("TAHAP 5: TOKENISASI INDOBERT")
print("=" * 70)

# Dipertahankan sama seperti kode Colab kamu.
# Model menggunakan Teks Stopword.

train_texts = df_train["Teks Stopword"].tolist()

test_texts = df_test["Teks Stopword"].tolist()

train_labels = df_train["label"].tolist()

test_labels = df_test["label"].tolist()


print("\nMelakukan tokenisasi data training...")

train_encodings = tokenizer(
    train_texts,
    truncation=True,
    padding=True,
    max_length=256
)


print("Melakukan tokenisasi data testing...")

test_encodings = tokenizer(
    test_texts,
    truncation=True,
    padding=True,
    max_length=256
)

print("\nTokenisasi seluruh data selesai.")

print(
    "Jumlah data training :",
    len(train_texts)
)

print(
    "Jumlah data testing  :",
    len(test_texts)
)

print(
    "Panjang input        :",
    len(train_encodings["input_ids"][0])
)


# ==============================================================================
# TAHAP 6: DATASET PYTORCH
# ==============================================================================

print("\n" + "=" * 70)
print("TAHAP 6: MENYIAPKAN DATASET UNTUK MODEL")
print("=" * 70)


class BeritaDataset(torch.utils.data.Dataset):

    def __init__(self, encodings, labels):

        self.encodings = encodings

        self.labels = labels


    def __getitem__(self, idx):

        item = {
            key: torch.tensor(val[idx])
            for key, val in self.encodings.items()
        }

        item["labels"] = torch.tensor(
            self.labels[idx]
        )

        return item


    def __len__(self):

        return len(self.labels)


train_dataset = BeritaDataset(
    train_encodings,
    train_labels
)

test_dataset = BeritaDataset(
    test_encodings,
    test_labels
)


print(
    "Jumlah data training :",
    len(train_dataset)
)

print(
    "Jumlah data testing  :",
    len(test_dataset)
)


# ==============================================================================
# TAHAP 7: FINE-TUNING INDOBERT
# ==============================================================================

print("\n" + "=" * 70)
print("TAHAP 7: FINE-TUNING INDOBERT")
print("=" * 70)


print("\nMemuat model IndoBERT...")

model = AutoModelForSequenceClassification.from_pretrained(
    model_name,
    num_labels=5
)


model.to(device)


print("\nModel IndoBERT berhasil dimuat.")
print("Jumlah kelas :", model.config.num_labels)
print("Device       :", device)


# ------------------------------------------------------------------------------
# DataLoader
# ------------------------------------------------------------------------------

batch_size = 8

train_loader = DataLoader(
    train_dataset,
    batch_size=batch_size,
    shuffle=True
)

test_loader = DataLoader(
    test_dataset,
    batch_size=batch_size,
    shuffle=False
)


print("\nDataLoader berhasil dibuat.")

print(
    "Batch size :",
    batch_size
)

print(
    "Jumlah batch training :",
    len(train_loader)
)

print(
    "Jumlah batch testing  :",
    len(test_loader)
)


# ------------------------------------------------------------------------------
# Optimizer
# ------------------------------------------------------------------------------

learning_rate = 2e-5

optimizer = AdamW(
    model.parameters(),
    lr=learning_rate
)

print(
    "\nLearning rate :",
    learning_rate
)


# ------------------------------------------------------------------------------
# Training
# ------------------------------------------------------------------------------

num_epochs = 3

model.train()

print("\nMulai proses fine-tuning IndoBERT...")

print(
    "Jumlah epoch :",
    num_epochs
)

print(
    "Jumlah data training :",
    len(train_dataset)
)

print(
    "Device :",
    device
)


train_losses = []

start_time = time.time()


for epoch in range(num_epochs):

    total_loss = 0

    print(
        f"\n===== Epoch {epoch + 1}/{num_epochs} ====="
    )


    for batch_idx, batch in enumerate(
        train_loader
    ):

        input_ids = batch[
            "input_ids"
        ].to(device)

        attention_mask = batch[
            "attention_mask"
        ].to(device)

        labels = batch[
            "labels"
        ].to(device)


        optimizer.zero_grad()


        outputs = model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            labels=labels
        )


        loss = outputs.loss


        loss.backward()

        optimizer.step()


        total_loss += loss.item()


        if (
            (batch_idx + 1) % 10 == 0
            or
            (batch_idx + 1) == len(train_loader)
        ):

            print(
                f"Batch {batch_idx + 1}/"
                f"{len(train_loader)} "
                f"- Loss: {loss.item():.4f}"
            )


    average_loss = (
        total_loss / len(train_loader)
    )

    train_losses.append(
        average_loss
    )


    print(
        f"Average Training Loss: "
        f"{average_loss:.4f}"
    )


end_time = time.time()

training_time = (
    end_time - start_time
)


print("\n" + "=" * 70)
print("FINE-TUNING SELESAI")
print("=" * 70)

print(
    f"Total waktu training : "
    f"{training_time / 60:.2f} menit"
)

print(
    f"Training loss akhir  : "
    f"{train_losses[-1]:.4f}"
)


# ==============================================================================
# TAHAP 8: EVALUASI MODEL
# ==============================================================================

print("\n" + "=" * 70)
print("TAHAP 8: EVALUASI MODEL")
print("=" * 70)


model.eval()

all_predictions = []

all_labels = []


print(
    "Mulai evaluasi pada data testing..."
)


with torch.no_grad():

    for batch in test_loader:

        input_ids = batch[
            "input_ids"
        ].to(device)

        attention_mask = batch[
            "attention_mask"
        ].to(device)

        labels = batch[
            "labels"
        ].to(device)


        outputs = model(
            input_ids=input_ids,
            attention_mask=attention_mask
        )


        predictions = torch.argmax(
            outputs.logits,
            dim=1
        )


        all_predictions.extend(
            predictions.cpu().numpy()
        )

        all_labels.extend(
            labels.cpu().numpy()
        )


print("Evaluasi selesai.")

print(
    "Jumlah data yang diuji :",
    len(all_labels)
)


# ------------------------------------------------------------------------------
# Metrik
# ------------------------------------------------------------------------------

accuracy = accuracy_score(
    all_labels,
    all_predictions
)

precision = precision_score(
    all_labels,
    all_predictions,
    average="weighted",
    zero_division=0
)

recall = recall_score(
    all_labels,
    all_predictions,
    average="weighted",
    zero_division=0
)

f1 = f1_score(
    all_labels,
    all_predictions,
    average="weighted",
    zero_division=0
)


print("\n" + "=" * 70)
print("HASIL EVALUASI MODEL INDOBERT")
print("=" * 70)

print(
    f"Accuracy  : {accuracy * 100:.2f}%"
)

print(
    f"Precision : {precision * 100:.2f}%"
)

print(
    f"Recall    : {recall * 100:.2f}%"
)

print(
    f"F1-Score  : {f1 * 100:.2f}%"
)


# ------------------------------------------------------------------------------
# Classification Report
# ------------------------------------------------------------------------------

target_names = [
    "Ekonomi",
    "Hukum",
    "Olahraga",
    "Pendidikan",
    "Politik"
]


print("\n" + "=" * 70)
print("CLASSIFICATION REPORT")
print("=" * 70)


print(
    classification_report(
        all_labels,
        all_predictions,
        target_names=target_names,
        digits=4,
        zero_division=0
    )
)


# ------------------------------------------------------------------------------
# Confusion Matrix
# ------------------------------------------------------------------------------

cm = confusion_matrix(
    all_labels,
    all_predictions
)


plt.figure(
    figsize=(8, 6)
)

sns.heatmap(
    cm,
    annot=True,
    fmt="d",
    xticklabels=target_names,
    yticklabels=target_names
)

plt.xlabel("Prediksi")

plt.ylabel("Aktual")

plt.title(
    "Confusion Matrix IndoBERT"
)

plt.tight_layout()

plt.show()


# ==============================================================================
# TAHAP 9: PENGUJIAN PREDIKSI BERITA BARU
# ==============================================================================

print("\n" + "=" * 70)
print("TAHAP 9: PENGUJIAN PREDIKSI BERITA BARU")
print("=" * 70)


label_mapping = {
    0: "Ekonomi",
    1: "Hukum",
    2: "Olahraga",
    3: "Pendidikan",
    4: "Politik"
}


def prediksi_berita(teks):

    model.eval()


    encoding = tokenizer(
        teks,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=256
    )


    encoding = {
        key: value.to(device)
        for key, value in encoding.items()
    }


    with torch.no_grad():

        outputs = model(
            **encoding
        )


    predicted_label = torch.argmax(
        outputs.logits,
        dim=1
    ).item()


    probabilities = torch.softmax(
        outputs.logits,
        dim=1
    )


    confidence = probabilities[
        0
    ][
        predicted_label
    ].item()


    return (
        label_mapping[predicted_label],
        confidence
    )


# ------------------------------------------------------------------------------
# Contoh prediksi
# ------------------------------------------------------------------------------

teks_baru_example = """
Besok ada pertandingan bola di lapangan martubung
pada pukul 10.10
"""


kategori, confidence = prediksi_berita(
    teks_baru_example
)


print("\nContoh Prediksi:")

print(
    "Teks berita:",
    teks_baru_example
)

print(
    "Kategori   :",
    kategori
)

print(
    f"Confidence : "
    f"{confidence * 100:.2f}%"
)


# ==============================================================================
# TAHAP 10: MENYIMPAN MODEL
# ==============================================================================

print("\n" + "=" * 70)
print("TAHAP 10: MENYIMPAN MODEL")
print("=" * 70)


model_path = "model_indobert"


os.makedirs(
    model_path,
    exist_ok=True
)


print("\nMenyimpan model...")


model.save_pretrained(
    model_path
)


tokenizer.save_pretrained(
    model_path
)


print("\n============================================")
print("MODEL BERHASIL DISIMPAN")
print("============================================")

print(
    "Lokasi :",
    os.path.abspath(model_path)
)


# ==============================================================================
# VERIFIKASI MODEL
# ==============================================================================

print("\n--- Verifikasi Loading Model ---")


tokenizer_loaded = AutoTokenizer.from_pretrained(
    model_path
)


model_loaded = AutoModelForSequenceClassification.from_pretrained(
    model_path
)


model_loaded = model_loaded.to(device)

model_loaded.eval()


print("\n============================================")
print("MODEL BERHASIL DI-LOAD ULANG")
print("============================================")

print(
    "Device :",
    device
)

print(
    "Jumlah label :",
    model_loaded.config.num_labels
)


# ------------------------------------------------------------------------------
# Tes model setelah load ulang
# ------------------------------------------------------------------------------

teks_uji = input(
    "\nMasukkan berita untuk pengujian setelah "
    "load ulang: "
)


encoding_loaded = tokenizer_loaded(
    teks_uji,
    return_tensors="pt",
    truncation=True,
    padding=True,
    max_length=256
)


encoding_loaded = {
    key: value.to(device)
    for key, value in encoding_loaded.items()
}


with torch.no_grad():

    outputs_loaded = model_loaded(
        **encoding_loaded
    )


predicted_label_loaded = torch.argmax(
    outputs_loaded.logits,
    dim=1
).item()


probabilities_loaded = torch.softmax(
    outputs_loaded.logits,
    dim=1
)


confidence_loaded = probabilities_loaded[
    0
][
    predicted_label_loaded
].item()


kategori_loaded = label_mapping[
    predicted_label_loaded
]


print("\n============================================")
print("HASIL PREDIKSI MODEL HASIL LOAD ULANG")
print("============================================")

print(
    "Kategori   :",
    kategori_loaded
)

print(
    f"Confidence : "
    f"{confidence_loaded * 100:.2f}%"
)

print("\nPROGRAM SELESAI.")