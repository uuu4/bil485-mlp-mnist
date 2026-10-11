# BIL485 Derin Öğrenme — Ödev 1: MNIST ile MLP Tabanlı El Yazısı Rakam Tanıma

MNIST üzerinde sıfırdan eğitilen bir MLP (CNN yok, hazır model yok), hiperparametre karşılaştırması ve kendi el yazımla yazdığım okul numarası üzerinde değerlendirme.

Tüm çalışma tek notebook'ta: [`mlp_mnist.ipynb`](mlp_mnist.ipynb) (PyTorch).

## Yapı

| Dosya / klasör | İçerik |
|---|---|
| `mlp_mnist.ipynb` | Veri bölünmesi, Deney 1 (temel MLP), Deney 2 (hiperparametre karşılaştırması), final test, kendi el yazım, değerlendirme |
| `my_digits/` | Okul numaramın rakamları; trackpad ile kendim çizdim (`01.png`, `02.png`, … soldan sağa) |
| `tools/draw_digits.py` | Rakamları çizip `my_digits/`'e kaydeden yerel çizim tahtası (`python3 tools/draw_digits.py <numara>`) |
| `results/` | Notebook çalışınca üretilen grafikler, tablolar (`.csv`) ve final model ağırlıkları |
| `requirements.txt` | Gerekli kütüphaneler |

## Deneysel tasarım (özet)

- **Veri:** MNIST eğitim kümesi 50 000 *train* + 10 000 *validation*; resmi 10 000'lik *test* kümesi ayrı tutulur.
- **Test verisi kuralı:** Tüm konfigürasyon seçimi yalnızca validation accuracy ile yapılır; test kümesi en sonda, seçimden sonra bir kez ölçülür.
- **Deney 1:** 784-256-128-10, ReLU, CrossEntropyLoss, Adam (lr 1e-3), batch 128, 15 epoch.
- **Deney 2:** Temel modelden her seferinde tek hiperparametre değişir: öğrenme oranı, batch size, genişlik, derinlik, dropout, optimizer (SGD+momentum).
- **Kendi el yazım:** gri tonlama → kontrast germe → gerekirse renk ters çevirme → kırpma + 20 px ölçekleme + 28×28'e kütle merkeziyle yerleştirme → train istatistikleriyle normalizasyon. Karşılaştırma için yalnızca 28×28'e küçültülmüş sürüm de değerlendirilir.

## Sonuçlar (Colab, GPU, SEED=42)

| Model | Train acc | Val acc | **Test acc** |
|---|---|---|---|
| Deney 1 — temel MLP (256-128, Adam 1e-3) | 0,9984 | 0,9773 | **0,9802** |
| Final — SGD lr=0,05 m=0,9 (validation'a göre seçildi) | 1,0000 | 0,9799 | **0,9829** |

Kendi el yazımla okul numarası (11 hane, trackpad çizimi): MNIST-tarzı hazırlıkla **11/11**, yalnızca 28×28'e küçültülünce 5/11. Ayrıntı ve yorum: notebook §6–§7.

## Çalıştırma

```bash
pip install -r requirements.txt
jupyter notebook mlp_mnist.ipynb
```

veya Colab'de açıp (GPU önerilir) hücreleri sırayla çalıştırın. MNIST ilk çalıştırmada `data/` altına indirilir.

`my_digits/` içine her hane için bir görüntü koyup notebook'taki `STUDENT_NUMBER` değişkenini doldurmadan §6 çalışmaz.
