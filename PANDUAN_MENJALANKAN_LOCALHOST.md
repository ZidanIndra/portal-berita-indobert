# PANDUAN MENJALANKAN WEBSITE DI LOCALHOST

Panduan lengkap untuk mengaktifkan dan menjalankan portal web klasifikasi berita **IndoBERT** di komputer lokal (localhost).

---

## 1. Pilihan Mode Menjalankan Website

Website ini mendukung 2 (dua) cara pengoperasian di komputer lokal:

| Mode | Kebutuhan | Kelebihan | Endpoint |
| :--- | :--- | :--- | :--- |
| **Mode A: Server Backend Flask (Direkomendasikan)** | Python, Flask, PyTorch, Transformers | Menjalankan model IndoBERT asli (`model_indobert/`) dengan inferensi PyTorch (CPU/CUDA) | `http://localhost:5000` |
| **Mode B: Server Statis Cepat (Tanpa PyTorch)** | Python bawaan (atau peramban langsung) | Ringan, cepat dibuka tanpa unduh dependensi AI yang berat, inferensi menggunakan Client-Side Fallback Engine | `http://localhost:8000` |

---

## 2. Persyaratan Awal (Prerequisites)

1. **Python 3.8 hingga 3.12** sudah terpasang di komputer Anda.
   - Cek versi Python di terminal/CMD:
     ```bash
     python --version
     ```
2. Pastikan file model sudah berada di dalam folder `model_indobert/`:
   - `model.safetensors` (atau `pytorch_model.bin`)
   - `config.json`
   - `tokenizer.json` / `vocab.txt`
   - `label_mapping.json`

---

## 3. Langkah Menjalankan: Mode A (Server Flask + Model IndoBERT Penuh)

### Langkah 1: Buka Terminal di Direktori Proyek
Buka Command Prompt (CMD), PowerShell, atau Terminal VS Code, lalu arahkan ke folder proyek:
```bash
cd "D:\Zidan\Git\Klasifikasi berita"
```
*(Sesuaikan path folder jika lokasi folder Anda berbeda)*

### Langkah 2: Buat & Aktifkan Virtual Environment (Opsional tapi Direkomendasikan)
Gunakan virtual environment agar paket tidak bentrok dengan instalasi Python global:

- **Windows (PowerShell):**
  ```powershell
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  ```
  *(Jika muncul policy restriction di PowerShell, jalankan: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`)*

- **Windows (Command Prompt / CMD):**
  ```cmd
  python -m venv .venv
  .venv\Scripts\activate.bat
  ```

- **Linux / macOS:**
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```

### Langkah 3: Pasang Dependensi Python
Jalankan perintah instalasi paket yang dibutuhkan:
```bash
pip install -r requirements.txt
```

> **Catatan untuk pengguna GPU NVIDIA (CUDA):**
> Jika Anda memiliki GPU NVIDIA dan ingin inferensi ekstra cepat, pasang PyTorch CUDA sesuai instruksi di [pytorch.org](https://pytorch.org/). Jika menggunakan CPU biasa, perintah `pip install torch` standar di atas sudah mencukupi.

### Langkah 4: Jalankan Server Flask
Jalankan file `app.py`:
```bash
python app.py
```

Jika berhasil, terminal akan menampilkan log seperti berikut:
```text
Loading model and tokenizer from model_indobert...
Model and tokenizer loaded successfully!
Using device: cpu (atau cuda)
 * Running on http://127.0.0.1:5000
 * Press CTRL+C to quit
```

### Langkah 5: Buka di Browser
Buka peramban (Google Chrome, Microsoft Edge, Firefox, dsb.) dan akses URL:
- **Portal Utama Berita:** `http://localhost:5000` atau `http://127.0.0.1:5000`
- **Dashboard Admin Konten:** `http://localhost:5000/admin`

---

## 4. Langkah Menjalankan: Mode B (Server Statis Cepat)

Jika Anda hanya ingin mengecek tampilan antarmuka, menguji tata letak UI/UX, atau mengedit konten di Dashboard Admin tanpa perlu mengunduh library PyTorch/Transformers:

1. Buka terminal di folder proyek:
   ```bash
   cd "D:\Zidan\Git\Klasifikasi berita"
   ```
2. Jalankan HTTP server bawaan Python:
   ```bash
   python -m http.server 8000
   ```
3. Buka browser di:
   - **Halaman Utama:** `http://localhost:8000/index.html`
   - **Dashboard Admin:** `http://localhost:8000/admin.html`

> Pada Mode B, pengujian naskah dan tombol 1-Klik Preset akan otomatis dilayani oleh **Client-Side Smart Semantic Classifier Engine** sehingga inferensi tetap berfungsi 100% tanpa kendala status 404.

---

## 5. Fitur Halaman & Struktur Navigasi

### A. Lembar Kerja Redaksi (`index.html`)
- **Pilih Naskah Uji Cepat (1-Click Preset):**
  - Terdapat 5 Kategori: **Politik**, **Ekonomi**, **Hukum**, **Olahraga**, **Pendidikan**.
  - Setiap kategori memiliki **5 contoh berita riil** (total 25 contoh).
  - Klik kategori untuk memuat contoh pertama, lalu klik nomor sub-naskah (`#1`, `#2`, `#3`, `#4`, `#5`) untuk berganti variasi naskah.
- **Formulir Redaksi:**
  - `Judul Berita` & `Isi Naskah Berita` (terpisah untuk pair-tokenization IndoBERT).
  - Penghitung karakter & kata live.
  - Tombol **Salin Naskah** dan **Bersihkan Form**.
  - Tombol utama **Proses Klasifikasi IndoBERT**.
- **Panel Hasil Prediksi:**
  - Badge kategori hasil prediksi.
  - Nilai tingkat keyakinan (Confidence Score) & meteran bar.
  - Distribusi probabilitas 5 kategori lengkap dengan grafik persentase.
  - Rincian metadata (Token Length, Device, Model Name, Input Mode).
- **Dashboard Evaluasi & Metrik:**
  - Tab **Locked Test Set** (Akurasi 92.00%, Macro Recall 91.68%, Macro Presisi 91.56%, Macro F1 91.52%).
  - Tab **5-Fold Cross Validation** (Validasi Fold 1 - 5, Best Fold 4: Val Acc 93.18%, Val Macro Recall 93.20%).
- **Kemitraan Pers:**
  - Profil Harian Medan Pos & portal `medanposonline.com`, alamat redaksi, email, serta struktur pimpinan pers.

### B. Dashboard Admin (`admin.html` atau `/admin`)
- Akses via navbar menu **Admin** atau buka `http://localhost:5000/admin`.
- Fitur pengaturan:
  - **Identitas Portal:** Judul koran, subtitle, tagline, brand navbar, logo (unggah file gambar atau masukkan URL).
  - **Hero & Banner:** Badge headline, judul hero, highlight, deskripsi berita utama, gambar banner koran (unggah/URL), caption foto.
  - **Kemitraan Redaksi:** Nama media, alamat kantor redaksi, email redaksi, website, serta susunan dewan redaksi.
  - **Koneksi Model / API:** URL endpoint API klasifikasi kustom dan Hugging Face Model ID.
  - **Footer:** Teks footer, identitas pengembang, program studi, kampus, dan hak cipta.
- Klik tombol **Simpan Seluruh Perubahan** di bagian atas/bawah panel. Data tersimpan secara instan di `localStorage` peramban.

---

## 6. Pemecahan Masalah (Troubleshooting)

| Gejala Masalah | Penyebab | Solusi |
| :--- | :--- | :--- |
| `ModuleNotFoundError: No module named 'flask'` | Dependensi belum terpasang | Jalankan: `pip install flask flask-cors torch transformers safetensors` |
| `OSError: [Errno 98] Address already in use` atau `Port 5000 is in use` | Port 5000 sedang dipakai aplikasi lain (misal AirPlay di Mac atau server lain) | Ganti port di baris terakhir `app.py`: `app.run(debug=True, port=5001)` lalu buka `http://localhost:5001` |
| Form prediksi error / lambat saat pertama kali | Model IndoBERT sedang dimuat ke memori RAM | Tunggu 3-5 detik saat server pertama kali dinyalakan agar bobot model selesai di-load |
| Tampilan logo/gambar belum terupdate setelah simpan di Admin | Cache browser masih menyimpan gambar lama | Tekan `Ctrl + F5` (atau `Cmd + Shift + R` di Mac) untuk hard refresh halaman |

---

## 7. Cara Menghentikan Server Localhost

Untuk mematikan server Flask atau HTTP server di terminal:
- Klik pada jendela terminal/CMD.
- Tekan kombinasi tombol **`Ctrl + C`**.
