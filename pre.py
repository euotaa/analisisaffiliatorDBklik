import pandas as pd

# 1. Baca file CSV mentah
df = pd.read_csv("AMSAffiliatePerformanceJuni.csv")

# 2. Bersihkan kolom ROI → ubah '--' menjadi NaN
df['ROI'] = df['ROI'].replace('--', pd.NA)

# 3. Pastikan kolom angka dibaca sebagai numerik
#    Contoh: Omzet Penjualan(Rp), Estimasi Komisi(Rp), Produk Terjual, Pesanan, Kliks, Total Pembeli, Pembeli Baru
numeric_cols = [
    "Omzet Penjualan(Rp)", 
    "Estimasi Komisi(Rp)", 
    "Produk Terjual", 
    "Pesanan", 
    "Clicks", 
    "Total Pembeli", 
    "Pembeli Baru",
    "ROI"
]

# Hapus karakter non-angka seperti "Rp", koma, atau titik ribuan jika ada
for col in numeric_cols:
    df[col] = (
        df[col]
        .astype(str)                 # ubah dulu ke string biar aman
        .str.replace(r"[^0-9.]", "", regex=True)  # hapus semua selain angka & titik
        .replace("", pd.NA)          # kalau hasil kosong → jadi NaN
    )
    df[col] = pd.to_numeric(df[col], errors="coerce")

# 4. Simpan hasil preprocessing ke file baru
output_file = "AffiliatePerformanceJuni_Clean.csv"
df.to_csv(output_file, index=False)

print(f"Preprocessing selesai! File bersih tersimpan sebagai {output_file}")
