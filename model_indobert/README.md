---
language:
- id
license: mit
tags:
- text-classification
- bert
- indobert
- indonesian-news
metrics:
- accuracy
- recall
- precision
- f1
pipeline_tag: text-classification
widget:
- text: "KPK melakukan OTT terhadap oknum pejabat dinas PU terkait suap proyek"
---

# IndoBERT Fine-Tuned untuk Klasifikasi Berita Indonesia

Model IndoBERT (`indobenchmark/indobert-base-p1`) yang telah di-finetune untuk mengklasifikasikan berita ke dalam 5 kategori:
- Ekonomi
- Hukum
- Olahraga
- Pendidikan
- Politik

## Metrik Evaluasi
- **Akurasi**: 92.00%
- **Macro Recall**: 91.68%
- **Macro Presisi**: 91.56%
- **Macro F1-Score**: 91.52%
- **5-Fold Cross Validation (Best Fold 4)**: 93.18%
