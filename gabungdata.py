import pandas as pd

# Baca semua file
juni = pd.read_csv("AffiliatePerformanceJuni_Clean.csv")
juli = pd.read_csv("AffiliatePerformanceJuli_Clean.csv")
agustus = pd.read_csv("AffiliatePerformanceAgustus_Clean.csv")

# Tambahkan kolom 'Bulan' biar tau asalnya
juni["Bulan"] = "Juni"
juli["Bulan"] = "Juli" 
agustus["Bulan"] = "Agustus"

# Gabung jadi satu dataframe
df = pd.concat([juni, juli, agustus], ignore_index=True)

# Simpan jadi 1 CSV
df.to_csv("Affiliate_Juni_Juli_Agustus.csv", index=False)
print("Data berhasil digabung jadi 1 file.")

