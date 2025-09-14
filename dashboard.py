import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Load data
df = pd.read_csv("Affiliate_Juni_Juli_Agustus.csv")

# Preprocessing
def clean_numeric(series):
    if series.dtype == "object":  # kalau masih string, buang karakter non-angka
        return pd.to_numeric(series.str.replace("[^0-9]", "", regex=True), errors="coerce")
    else:  # kalau sudah numeric, langsung return
        return pd.to_numeric(series, errors="coerce")
    
df["Omzet Penjualan(Rp)"] = clean_numeric(df["Omzet Penjualan(Rp)"])
df["Estimasi Komisi(Rp)"] = clean_numeric(df["Estimasi Komisi(Rp)"])
df["Clicks"] = clean_numeric(df["Clicks"])
df["Pesanan"] = clean_numeric(df["Pesanan"])
df["Produk Terjual"] = clean_numeric(df["Produk Terjual"])
df["ROI"] = pd.to_numeric(df["ROI"], errors="coerce")
df["Total Pembeli"] = clean_numeric(df["Total Pembeli"])
df["Pembeli Baru"] = clean_numeric(df["Pembeli Baru"])

# ================= Sidebar Pilihan Mode =================
mode = st.sidebar.radio("Pilih Tindakan", ["Dashboard Statistik", "Clustering"])

# ================= DASHBOARD =================
if mode == "Dashboard Statistik":
    # Pilihan bulan (multi-select biar bisa pilih Juni, Juli, Agustus sekaligus)
    bulan_list = sorted(df["Bulan"].unique())
    bulan_pilihan = st.sidebar.multiselect("Pilih Bulan", bulan_list, default=[bulan_list[-1]])

    df_bulan = df[df["Bulan"].isin(bulan_pilihan)]

    st.title(f"📊 Dashboard Affiliate DB Klik- {', '.join(bulan_pilihan)}")

    # KPI
    total_omzet = df_bulan["Omzet Penjualan(Rp)"].sum()
    total_komisi = df_bulan["Estimasi Komisi(Rp)"].sum()
    total_pesanan = df_bulan["Pesanan"].sum()
    jumlah_affiliator = df_bulan["Nama Affiliate"].nunique()

    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)
    col1.metric("Total Omzet", f"Rp {total_omzet:,.0f}")
    col2.metric("Total Komisi", f"Rp {total_komisi:,.0f}")
    col3.metric("Total Pesanan", f"{total_pesanan}")
    col4.metric("Jumlah Affiliator", f"{jumlah_affiliator}")

    # ======================== 1. PERFORMA AFFILIATOR ========================
    st.header("1. Performa Affiliator")

    top_omzet = df_bulan.nlargest(10, "Omzet Penjualan(Rp)")
    fig1 = px.bar(top_omzet, x="Nama Affiliate", y="Omzet Penjualan(Rp)", color="Bulan",
                  title="Top 10 Omzet Tertinggi")
    st.plotly_chart(fig1)

    top_komisi = df_bulan.nlargest(10, "Estimasi Komisi(Rp)")
    fig2 = px.bar(top_komisi, x="Nama Affiliate", y="Estimasi Komisi(Rp)", color="Bulan",
                  title="Top 10 Komisi Tertinggi")
    st.plotly_chart(fig2)

    top_pesanan = df_bulan.nlargest(10, "Pesanan")
    fig3 = px.bar(top_pesanan, x="Nama Affiliate", y="Pesanan", color="Bulan",
                  title="Top 10 Pesanan Terbanyak")
    st.plotly_chart(fig3)

    top_roi = df_bulan.nlargest(10, "ROI")
    fig4 = px.bar(top_roi, x="Nama Affiliate", y="ROI", color="Bulan",
                  title="Top 10 ROI Tertinggi")
    st.plotly_chart(fig4)

    # ======================== 2. EFEKTIVITAS PROMOSI ========================
    st.header("2. Efektivitas Promosi")

    df_bulan["CTR"] = df_bulan["Pesanan"] / df_bulan["Clicks"].replace(0, 1)

    top_clicks_pesanan = df_bulan.nlargest(10, "CTR")
    fig5 = px.scatter(top_clicks_pesanan, x="Clicks", y="Pesanan", size="CTR", color="Nama Affiliate",
                    title="Top 10 Efektif (Clicks vs Pesanan)", hover_data=["Bulan"])
    st.plotly_chart(fig5)

    top_baru_vs_lama = df_bulan.nlargest(10, "Pembeli Baru")
    fig6 = px.bar(top_baru_vs_lama, x="Nama Affiliate", y=["Pembeli Baru", "Total Pembeli"],
                barmode="group", title="Top 10 Pembeli Baru vs Lama")
    st.plotly_chart(fig6)

    produk_avg = df_bulan["Produk Terjual"].mean()
    st.write(f"📌 Rata-rata produk terjual per affiliator: **{produk_avg:.2f}**")

    # ======================== 3. ANALISIS PENJUALAN ========================
    st.header("3. Analisis Penjualan")

    bins = {
        ">50jt": df_bulan[df_bulan["Omzet Penjualan(Rp)"] > 50000000],
        "10-50jt": df_bulan[(df_bulan["Omzet Penjualan(Rp)"] >= 10000000) & (df_bulan["Omzet Penjualan(Rp)"] <= 50000000)],
        "<10jt": df_bulan[df_bulan["Omzet Penjualan(Rp)"] < 10000000]
    }

    for kategori, subset in bins.items():
        top5 = subset.nlargest(5, "Omzet Penjualan(Rp)")
        if not top5.empty:
            fig = px.bar(top5, 
                        x="Nama Affiliate", 
                        y="Omzet Penjualan(Rp)", 
                        color="Bulan",
                        title=f"Top 5 Affiliator dengan Omzet {kategori}",
                        text="Omzet Penjualan(Rp)")
            fig.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
            st.plotly_chart(fig)

    roi_trend = df_bulan.nlargest(10, "ROI")
    fig7 = px.line(roi_trend, x="Nama Affiliate", y="ROI", markers=True, color="Bulan",
                title="Top 10 ROI Per Affiliator")
    st.plotly_chart(fig7)

    # Tabel Ranking
    st.header("📌 Tabel Ranking Interaktif")
    kolom_sort = st.selectbox("Urutkan berdasarkan", 
        ["Omzet Penjualan(Rp)", "Estimasi Komisi(Rp)", "ROI"])
    ranking = df_bulan.sort_values(by=kolom_sort, ascending=False).reset_index(drop=True)
    ranking.index = ranking.index + 1
    st.dataframe(ranking[["Nama Affiliate", "Bulan", "Omzet Penjualan(Rp)", "Estimasi Komisi(Rp)", "ROI"]])

    # Ringkasan Statistik
    st.header("📌 Ringkasan Statistik")
    kolom_numerik = [
        "Omzet Penjualan(Rp)", "Estimasi Komisi(Rp)", "Clicks",
        "Pesanan", "Produk Terjual", "ROI", "Total Pembeli", "Pembeli Baru"
    ]
    stat_desc = df_bulan[kolom_numerik].describe().T.rename(columns={
        "count": "Jumlah Data", "mean": "Rata-rata", "std": "Standar Deviasi",
        "min": "Minimum", "25%": "Q1", "50%": "Median", "75%": "Q3", "max": "Maksimum"
    })
    st.dataframe(stat_desc)

# ================= CLUSTERING =================
elif mode == "Clustering":
    st.title("Clustering Affiliator DB Klik (KMeans)")

    # Pilihan bulan
    bulan_list = sorted(df["Bulan"].unique())
    bulan_pilihan = st.sidebar.multiselect("Pilih Bulan", bulan_list, default=[bulan_list[-1]])

    df_bulan = df[df["Bulan"].isin(bulan_pilihan)].copy()

    if df_bulan.empty:
        st.warning("❌ Tidak ada data untuk bulan yang dipilih!")
    else:
        # Kolom untuk clustering
        kolom_cluster = ["Omzet Penjualan(Rp)", "Estimasi Komisi(Rp)", "Pesanan", "ROI", "Clicks"]
        data_cluster = df_bulan[kolom_cluster].fillna(0)

        scaler = StandardScaler()
        data_scaled = scaler.fit_transform(data_cluster)

        # ================= ELBOW METHOD =================
        inertia = []
        silhouette_scores = []
        K = range(2, 8)
        for k in K:
            km = KMeans(n_clusters=k, random_state=42, n_init=10)
            preds = km.fit_predict(data_scaled)
            inertia.append(km.inertia_)
            from sklearn.metrics import silhouette_score
            if len(set(preds)) > 1:
                silhouette_scores.append(silhouette_score(data_scaled, preds))
            else:
                silhouette_scores.append(None)

        fig_elbow = px.line(x=list(K), y=inertia, markers=True,
                            title="Metode Elbow untuk Menentukan Jumlah Cluster",
                            labels={"x": "Jumlah Cluster (k)", "y": "Inertia"})
        st.plotly_chart(fig_elbow)

        fig_silhouette = px.line(x=list(K), y=silhouette_scores, markers=True,
                                 title="Silhouette Score untuk Evaluasi Cluster",
                                 labels={"x": "Jumlah Cluster (k)", "y": "Silhouette Score"})
        st.plotly_chart(fig_silhouette)

        # ================= KMEANS CLUSTERING =================
        k = st.sidebar.slider("Jumlah Cluster (k)", 2, 6, 3)
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        df_bulan["Cluster"] = kmeans.fit_predict(data_scaled)

        # Hitung silhouette untuk k terpilih
        from sklearn.metrics import silhouette_score
        silhouette_k = silhouette_score(data_scaled, df_bulan["Cluster"])
        st.info(f"Silhouette Score untuk k={k}: **{silhouette_k:.3f}**")

        # ================= LABEL BERDASARKAN CLUSTER =================
        cluster_labels = {
            0: "Micro Sellers",
            1: "Top Performer",
            2: "Potential Growers",
            3: "Others"
        }
        df_bulan["Cluster_Label"] = df_bulan["Cluster"].map(cluster_labels)
        df_bulan["Pembeli Lama"] = df_bulan["Total Pembeli"].fillna(0) - df_bulan["Pembeli Baru"].fillna(0)

        # ================= CEK AFFILIATOR =================
        st.subheader("🔍 Cek Cluster & Label Affiliator")
        nama_aff_list = sorted(df_bulan["Nama Affiliate"].dropna().unique())
        if nama_aff_list:
            nama_aff = st.selectbox("Pilih Nama Affiliate", nama_aff_list)
            hasil = df_bulan[df_bulan["Nama Affiliate"] == nama_aff][
                ["Nama Affiliate", "Bulan", "Omzet Penjualan(Rp)", "Estimasi Komisi(Rp)",
                 "Pesanan", "Clicks", "ROI", "Total Pembeli", "Pembeli Baru", "Pembeli Lama",
                 "Cluster", "Cluster_Label"]
            ]
            st.write(f"**Hasil Analisis untuk {nama_aff}:**")
            st.dataframe(hasil)
        else:
            st.warning("❌ Tidak ada data affiliator untuk bulan yang dipilih!")

        # ================= CLUSTER VISUALIZATION =================
        st.subheader("Visualisasi Cluster (Omzet vs Komisi)")
        fig_cluster = px.scatter(df_bulan,
                                 x="Omzet Penjualan(Rp)",
                                 y="Estimasi Komisi(Rp)",
                                 color=df_bulan["Cluster_Label"],
                                 hover_data=["Nama Affiliate", "Bulan", "Cluster"],
                                 title="Clustering Affiliator Berdasarkan Omzet & Komisi")
        st.plotly_chart(fig_cluster)

        # ================= DISTRIBUSI CLUSTER =================
        st.subheader("Distribusi Cluster")
        cluster_count = df_bulan["Cluster_Label"].value_counts().reset_index()
        cluster_count.columns = ["Cluster_Label", "Jumlah Affiliator"]
        st.dataframe(cluster_count)

        fig_pie = px.pie(cluster_count, names="Cluster_Label", values="Jumlah Affiliator",
                         title="Distribusi Affiliator Berdasarkan Cluster")
        st.plotly_chart(fig_pie)
