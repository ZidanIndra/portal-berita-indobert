# 📰 Portal Berita IndoBERT & Sistem Intelijen Klasifikasi Redaksi

[![Python Version](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-ee4c2c.svg)](https://pytorch.org/)
[![Transformers](https://img.shields.io/badge/Transformers-Hugging%20Face-yellow.svg)](https://huggingface.co/docs/transformers)
[![Flask](https://img.shields.io/badge/Flask-Framework-black.svg)](https://flask.palletsprojects.com/)
[![Hugging Face Spaces](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Spaces%20Live%20Demo-blue)](https://huggingface.co/spaces/zidanindraa2/portal-berita-indobert)
[![Hugging Face Model](https://img.shields.io/badge/%F0%9F%A4%97%20Model%20Hub-IndoBERT%20News-orange)](https://huggingface.co/zidanindraa2/indobert-klasifikasi-berita)
[![Year](https://img.shields.io/badge/Tahun-2025-success.svg)](#pengembang--hak-cipta)

> **Sistem Klasifikasi Berita Otomatis Berbasis Deep Learning Transformer IndoBERT (`indobenchmark/indobert-base-p1`) untuk 5 Rubrik Jurnalistik: Politik, Ekonomi, Hukum, Olahraga, dan Pendidikan.**

---

## 📑 Daftar Isi

- [Tentang Proyek](#-tentang-proyek)
- [Tautan Langsung (Live Demo & Model)](#-tautan-langsung)
- [Fitur Utama](#-fitur-utama)
- [Arsitektur & Hasil Riset](#-arsitektur--hasil-riset)
- [Struktur Direktori](#-struktur-direktori)
- [Panduan Instalasi & Penggunaan (Localhost)](#-panduan-instalasi--penggunaan-localhost)
- [Dokumentasi API](#-dokumentasi-api)
- [Pengembang & Hak Cipta](#-pengembang--hak-cipta)

---

## 🌟 Tentang Proyek

**Portal Berita IndoBERT** adalah platform intelijen redaksi berita digital interaktif yang dirancang untuk mengotomatisasi proses kurasi dan kategorisasi naskah jurnalistik berbahasa Indonesia. Menggunakan arsitektur model bahasa prapelatihan **IndoBERT Base Phase 1**, sistem ini mampu memahami konteks semantik, terminologi, dan pola sintaksis berita secara mendalam.

Sistem ini dikembangkan atas kerja sama riset dan pengujian dataset bersama mitra media cetak dan digital **Harian Medan Pos**.

---

## 🔗 Tautan Langsung

| Platform | Tautan | Keterangan |
| :--- | :--- | :--- |
| **Hugging Face Space** | [🚀 Live Web App Portal Berita](https://huggingface.co/spaces/zidanindraa2/portal-berita-indobert) | Akses interaktif langsung di cloud Hugging Face |
| **Hugging Face Model** | [🤗 indobert-klasifikasi-berita](https://huggingface.co/zidanindraa2/indobert-klasifikasi-berita) | Model weights, tokenizer & config di Model Hub |

---

## ✨ Fitur Utama

1. **Editorial Motion UI & Interaktivitas Modern**:
   - Efek *perspective 3D tilt* dinamis pada kartu berita dan dokumentasi riset saat direspons kursor mouse.
   - Animasi *count-up* persentase kepercayaan (*confidence meter*) dan probabilitas distribusi kategori berbasis `requestAnimationFrame`.
   - Indikator bilah probabilitas dengan efek cahaya dinamis (*shimmer light sweep*).
   - Efek selebrasi partikel konfeti (*confetti celebration*) saat tingkat keyakinan model tinggi (>75%).
   - Animasi *scroll reveal* bertingkat (*staggered entrance*) saat menavigasi bagian artikel dan metrik riset.
   - Sistem notifikasi mengambang (*floating toast alerts*) untuk aksi salin, muat preset, reset, dan inferensi.

2. **25 Sampel Naskah Autentik (5 per Kategori)**:
   - Dilengkapi preset naskah berita aktual berbahasa Indonesia terverifikasi untuk kategori **Politik**, **Ekonomi**, **Hukum**, **Olahraga**, dan **Pendidikan**.

3. **Dual-Mode Inference Engine**:
   - **Mode REST API Backend**: Didukung server Flask dengan akselerasi PyTorch pada server lokal.
   - **Mode Semantic Client Fallback**: Memungkinkan antarmuka web tetap berjalan interaktif 100% pada *static web hosting* seperti Hugging Face Spaces tanpa ketergantungan server runtime Python aktif.

4. **Dashboard Admin Manajemen Redaksi (`/admin`)**:
   - Manajemen nama media, pembuat/pengembang, tahun edisi, tagline, dan konfigurasi endpoint API kustom secara *real-time* via `localStorage`.

---

## 🧠 Arsitektur & Hasil Riset

### Konfigurasi Model
- **Model Fondasi:** `indobenchmark/indobert-base-p1`
- **Jumlah Lapisan Transformer:** 12 Encoder Layers
- **Hidden Size:** 768
- **Attention Heads:** 12
- **Total Parameter:** ~124.5 Juta Parameter
- **Panjang Token Maksimum:** 512 Token
- **Jumlah Kelas Klasifikasi:** 5 Kategori Jurnalistik

### Performa Pengujian Model
| Metrik Evaluasi | Skor Pengujian | Catatan Validasi |
| :--- | :---: | :--- |
| **Akurasi Pengujian (Test Accuracy)** | **92.00%** | Evaluasi pada data uji terisolasi |
| **Macro Average Recall** | **91.68%** | Keseimbangan deteksi seluruh kategori |
| **Macro Average Precision** | **92.20%** | Akurasi prediksi label positif |
| **Macro Average F1-Score** | **91.80%** | Rata-rata harmonik performa |
| **5-Fold Cross Validation** | **89.70%** | Rata-rata stabilitas model antarlipatan |

---

## 📁 Struktur Direktori

```text
Klasifikasi berita/
│
├── .venv/                               # Python Virtual Environment
├── model_indobert/                      # Direktori bobot model & tokenizer IndoBERT
│   ├── config.json                      # Konfigurasi arsitektur BERT
│   ├── label_mapping.json               # Pemetaan ID ke nama kategori
│   ├── model.safetensors                # Bobot model (Safetensors)
│   ├── pytorch_model.bin                # Bobot model (PyTorch binary)
│   ├── tokenizer.json                   # Tokenizer vocabulary & BPE rules
│   └── vocab.txt                        # Kosakata subword IndoBERT
│
├── img/                                 # Aset gambar & logo pendukung
│   └── Lambang_Universitas_Negeri_Medan.png
│
├── app.py                               # Server backend Flask & endpoint REST API
├── index.html                           # Antarmuka utama Portal Redaksi Berita
├── admin.html                           # Dashboard Admin manajemen konten
├── style.css                            # Desain sistem editorial & animasi interaktif
├── script.js                            # Logika interaktif, preset, & inferensi naskah
├── requirements.txt                     # Daftar dependensi pustaka Python
├── LOGO.jpeg                            # Logo utama portal
├── FotoKoran.png                        # Dokumentasi riset koran Medan Pos
├── PANDUAN_MENJALANKAN_LOCALHOST.md     # Panduan teknis eksekusi lokal
└── README.md                            # Dokumentasi resmi proyek
```

---

## 💻 Panduan Instalasi & Penggunaan (Localhost)

### 1. Klon Repositori
```bash
git clone https://github.com/ZidanIndra/klasifikasi-berita-indobert.git
cd klasifikasi-berita-indobert
```

### 2. Buat & Aktifkan Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Pasang Dependensi
```bash
pip install -r requirements.txt
```

> **Catatan Dependensi:**
> - `flask` & `flask-cors`
> - `torch` (PyTorch)
> - `transformers` (Hugging Face)
> - `safetensors`

### 4. Jalankan Server Flask
```bash
python app.py
```

### 5. Akses Melalui Peramban Web
- **Portal Berita & Meja Redaksi:** [http://localhost:5000](http://localhost:5000)
- **Dashboard Admin Konten:** [http://localhost:5000/admin](http://localhost:5000/admin)

---

## 🔌 Dokumentasi API

### Prediksi Kategori Naskah
- **URL Endpoint:** `/prediksi`
- **Metode:** `POST`
- **Headers:** `Content-Type: application/json`

#### Contoh Request Payload:
```json
{
  "judul": "Bank Indonesia Tahan Suku Bunga Acuan BI-Rate di Level 6 Persen",
  "isi": "Rapat Dewan Gubernur Bank Indonesia memutuskan untuk mempertahankan suku bunga acuan BI-Rate pada level 6,00 persen demi menjaga stabilitas moneter dan inflasi nasional."
}
```

#### Contoh Response:
```json
{
  "kategori": "Ekonomi",
  "confidence": 98.42,
  "probabilities": {
    "Politik": 0.45,
    "Ekonomi": 98.42,
    "Hukum": 0.62,
    "Olahraga": 0.18,
    "Pendidikan": 0.33
  },
  "metadata": {
    "device": "cpu",
    "input_mode": "title_content_pair",
    "token_count": 48
  }
}
```

---

## 👨‍💻 Pengembang & Hak Cipta

- **Nama Pengembang:** **Zidan indra nugraha**
- **Tahun Pembuatan:** **2025**
- **Institusi Pendidikan:** Universitas Negeri Medan (UNIMED)
- **Mitra Riset Media:** Harian Medan Pos
- **Lisensi:** MIT License
