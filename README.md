# LLM Training Pipeline — CPT & IFT (S&K & FAQ)

Repository ini berisi pipeline **Continual Pre-Training (CPT)** dan **Instruction Fine-Tuning (IFT)** untuk Large Language Model (LLM) berbasis **dokumen Syarat & Ketentuan (S&K)** dan **FAQ mobile banking**.

Tujuan utama:
- Membuat model **memahami domain & aturan produk** (CPT)
- Membuat model **mampu menjawab pertanyaan pengguna dengan benar & natural** (IFT)

---

## 🎯 Scope Project

✔ Continual Pre-Training (CPT)  
✔ Instruction Fine-Tuning (IFT)  

❌ Retrieval Augmented Generation (RAG)  
❌ Online inference / API  
❌ Prompt engineering production  

---

## 🧠 Konsep Singkat

| Tahap | Fungsi | Dataset |
|-----|------|--------|
| CPT | Domain adaptation (aturan, istilah, konteks) | S&K (teks naratif, tanpa Q/A) |
| IFT | Cara menjawab pertanyaan user | FAQ (instruction → response) |

**Urutan WAJIB:**
```
Base Model → CPT → IFT
```

---

## 📁 Struktur Folder

```
llm_training/
│
├── raw/
│   ├── sk/
│   │   └── sk_wondr.txt
│   │
│   └── faq/
│       └── faq_wondr.xlsx
│
├── cpt/
│   ├── data/
│   │   └── cpt_sk_wondr.jsonl
│   │
│   └── config/
│       └── cpt_training.yaml
│
├── ift/
│   ├── data/
│   │   └── ift_faq_wondr.jsonl
│   │
│   └── config/
│       └── ift_training.yaml
│
└── models/
    ├── base_model/
    ├── cpt_model/
    └── ift_model/
```

---

## 📦 Dataset Format

### 1️⃣ CPT Dataset (Unsupervised)

- Sumber: S&K yang sudah dinarasikan
- Tidak mengandung Q/A
- Format: JSONL

Contoh:
```json
{"text": "Akun mobile banking dapat diblokir apabila terjadi kesalahan PIN berulang atau aktivitas tidak wajar."}
```

---

### 2️⃣ IFT Dataset (Instruction Fine-Tuning)

- Sumber: FAQ
- Format: instruction → output
- Kategori opsional sebagai konteks

Contoh:
```json
{
  "instruction": "Kenapa transaksi PIN-less saya tidak aktif?",
  "input": "Kategori: Mobile Tunai",
  "output": "Transaksi PIN-less dapat dinonaktifkan otomatis jika terjadi aktivasi ulang atau pergantian perangkat."
}
```

---

## ⚙️ Training Flow

### Step 1 — Continual Pre-Training (CPT)
```bash
python train_cpt.py \
  --model_path models/base_model \
  --data_path cpt/data/cpt_sk_wondr.jsonl \
  --output_path models/cpt_model
```

### Step 2 — Instruction Fine-Tuning (IFT)
```bash
python train_ift.py \
  --model_path models/cpt_model \
  --data_path ift/data/ift_faq_wondr.jsonl \
  --output_path models/ift_model
```

---

## ⚠️ Best Practices (WAJIB DIIKUTI)

- Jangan gunakan S&K mentah (pasal, enumerasi) langsung untuk CPT
- Jangan masukkan FAQ ke CPT
- Jangan melakukan IFT sebelum CPT
- Gunakan bahasa jawaban yang:
  - netral
  - tidak menyalahkan pengguna
  - tidak terlalu legalistik

---

## 📊 Skala Data (Rekomendasi)

| Tahap | Jumlah Data Ideal |
|-----|----------------|
| CPT | ≥ 500k token |
| IFT | 1.000 – 5.000 instruction |

---

## 🧪 Validasi Sederhana

Contoh prompt uji setelah IFT:
```text
Kenapa transaksi tanpa PIN saya tidak bisa digunakan?
```

Output yang baik:
- relevan
- singkat
- sesuai konteks produk
- tidak menyebut pasal hukum

---

## 🔐 Catatan Keamanan & Compliance

- Dataset wajib sudah dianonimkan
- Tidak boleh mengandung:
  - nomor rekening
  - nomor telepon
  - NIK
  - data transaksi spesifik nasabah

---

## 📌 Ringkasan

> CPT mengajarkan **apa itu produk dan aturannya**  
> IFT mengajarkan **bagaimana menjelaskannya ke pengguna**

Pipeline ini dirancang untuk **POC hingga pilot**, dan dapat dikembangkan lebih lanjut sesuai kebutuhan.
