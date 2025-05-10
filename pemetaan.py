import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from statistics import mode

st.set_page_config(page_title="Pemetaan Siswa & Orang Tua", layout="wide")

# Header yang lebih menarik
st.title("📊 Pemetaan Siswa & Orang Tua")
st.markdown("""
Aplikasi ini digunakan untuk memetakan **domisili**, **kondisi ekonomi**, dan **jumlah siswa** berdasarkan data Excel yang diunggah.  
Silakan unggah file Excel terlebih dahulu menggunakan form di bawah ini.
""")

# Menambahkan logo di sidebar
st.sidebar.image("https://www.birufms.com/assets/img/logo-support.gif", width=150)
st.sidebar.header("🔧 Pengaturan")
st.sidebar.markdown("Sesuaikan tampilan dan analisis data Anda di sini.")

uploaded_file = st.file_uploader("📁 Unggah data Excel siswa", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df.columns = df.columns.str.upper().str.strip()
    st.success("✅ File berhasil dimuat. Kolom yang terdeteksi:")
    st.write(df.columns.tolist())

    if 'PENGHASILAN' in df.columns:
        df['PENGHASILAN'] = pd.to_numeric(df['PENGHASILAN'], errors='coerce')

    st.subheader("🔍 Cuplikan Data")
    st.dataframe(df.head())

    if 'TAHUN' in df.columns:
        tahun_terpilih = st.selectbox("📅 Pilih Tahun", sorted(df['TAHUN'].dropna().unique()))
        df = df[df['TAHUN'] == tahun_terpilih]

    # Filter Kota di sidebar
    kota_terpilih = None
    if 'KOTA' in df.columns:
        kota_terpilih = st.sidebar.multiselect("📍 Pilih Kota", sorted(df['KOTA'].dropna().unique()))
        if kota_terpilih:
            df = df[df['KOTA'].isin(kota_terpilih)]

    # Filter Jenjang di sidebar
    jenjang_terpilih = None
    if 'JENJANG' in df.columns:
        jenjang_terpilih = st.sidebar.multiselect("🏫 Pilih Jenjang", sorted(df['JENJANG'].dropna().unique()))
        if jenjang_terpilih:
            df = df[df['JENJANG'].isin(jenjang_terpilih)]

    # Filter Kelas di sidebar
    kelas_terpilih = None
    if 'KELAS' in df.columns:
        kelas_terpilih = st.sidebar.multiselect("🎓 Pilih Kelas", sorted(df['KELAS'].dropna().unique()))
        if kelas_terpilih:
            df = df[df['KELAS'].isin(kelas_terpilih)]

    if st.sidebar.checkbox("Tampilkan Data Lengkap"):
        st.subheader("📊 Data Lengkap")
        st.dataframe(df)

    if 'KOTA' in df.columns:
        st.subheader("📍 Sebaran Siswa per Kota")
        kota_count = df['KOTA'].value_counts().reset_index()
        kota_count.columns = ['KOTA', 'JUMLAH']
        fig_kota = px.bar(kota_count, x='KOTA', y='JUMLAH', text='JUMLAH', 
                          title='Sebaran Siswa Berdasarkan Kota', 
                          color='JUMLAH', 
                          color_continuous_scale=px.colors.sequential.Viridis)
        fig_kota.update_traces(textposition='outside')
        st.plotly_chart(fig_kota, use_container_width=True)

    if 'PENGHASILAN' in df.columns:
        st.subheader("💰 Statistik Ekonomi Orang Tua")

        # Kategorisasi penghasilan
        df['PENGHASILAN_KAT'] = pd.cut(df['PENGHASILAN'],
            bins=[0, 1_000_000, 3_000_000, 5_000_000, 10_000_000, float('inf')],
            labels=["<1jt", "1-3jt", "3-5jt", "5-10jt", ">10jt"]
        )
        penghasilan_count = df['PENGHASILAN_KAT'].value_counts().sort_index().reset_index()
        penghasilan_count.columns = ['Kategori', 'Jumlah']

        # Pie chart
        fig_pie = px.pie(penghasilan_count, values='Jumlah', names='Kategori',
                         title='Distribusi Kategori Penghasilan', hole=0.4,
                         color_discrete_sequence=px.colors.sequential.RdBu)
        fig_pie.update_traces(textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)

        # Statistik deskriptif
        mean_val = df['PENGHASILAN'].mean()
        median_val = df['PENGHASILAN'].median()
        try:
            mode_val = mode(df['PENGHASILAN'].dropna())
        except:
            mode_val = "Tidak unik"
        std_val = df['PENGHASILAN'].std()

        st.markdown("📊 **Statistik Deskriptif Penghasilan**")
        st.write(f"- Rata-rata (Mean): Rp {mean_val:,.0f}")
        st.write(f"- Median: Rp {median_val:,.0f}")
        st.write(f"- Modus: {mode_val if isinstance(mode_val, str) else f'Rp {mode_val:,.0f}'}")
        st.write(f"- Standar Deviasi: Rp {std_val:,.0f}")

        # Bar chart penghasilan
        stat_labels = ['Mean', 'Median','Modus', 'Standar Deviasi']
        stat_values = [mean_val, median_val, mode_val if isinstance(mode_val, (int, float)) else 0, std_val]
        
        fig_stat = go.Figure(data=[
            go.Bar(name='Statistik', x=stat_labels, y=stat_values, marker_color='indigo')
        ])
        fig_stat.update_layout(title='Statistik Deskriptif Penghasilan', yaxis_title='Nilai (Rp)', xaxis_title='Statistik')
        st.plotly_chart(fig_stat, use_container_width=True)

    if 'JENJANG' in df.columns and not jenjang_terpilih:
        st.subheader("🏫 Jumlah Siswa per Jenjang")
        jenjang_count = df['JENJANG'].value_counts().reset_index()
        jenjang_count.columns = ['Jenjang', 'Jumlah']
        fig_jenjang = px.bar(jenjang_count, x='Jenjang', y='Jumlah', text='Jumlah', title='Jumlah Siswa per Jenjang', color='Jumlah', color_continuous_scale=px.colors.sequential.Plasma)
        fig_jenjang.update_traces(textposition='outside')
        st.plotly_chart(fig_jenjang, use_container_width=True)

    if 'KELAS' in df.columns and not kelas_terpilih:
        st.subheader("🏫 Jumlah Siswa per Kelas")
        kelas_count = df['KELAS'].value_counts().reset_index()
        kelas_count.columns = ['Kelas', 'Jumlah']
        fig_kelas = px.bar(kelas_count, x='Kelas', y='Jumlah', text='Jumlah', title='Jumlah Siswa per Kelas', color='Jumlah', color_continuous_scale=px.colors.sequential.Cividis)
        fig_kelas.update_traces(textposition='outside')
        st.plotly_chart(fig_kelas, use_container_width=True)

    # Analisis tambahan dari sidebar
    if st.sidebar.checkbox("Tampilkan Grafik Penghasilan per Kota"):
        if 'KOTA' in df.columns and 'PENGHASILAN' in df.columns:
            st.subheader("📈 Grafik Penghasilan per Kota")
            penghasilan_per_kota = df.groupby('KOTA')['PENGHASILAN'].mean().reset_index()
            fig_penghasilan_kota = px.bar(penghasilan_per_kota, x='KOTA', y='PENGHASILAN', 
                                           title='Rata-rata Penghasilan per Kota', 
                                           color='PENGHASILAN', 
                                           color_continuous_scale=px.colors.sequential.Plasma)
            st.plotly_chart(fig_penghasilan_kota, use_container_width=True)
        else:
            st.warning("Data penghasilan atau kota tidak tersedia.")

    if st.sidebar.checkbox("Tampilkan Distribusi Penghasilan"):
        if 'PENGHASILAN' in df.columns:
            st.subheader("📉 Distribusi Penghasilan")
            fig_dist = px.histogram(df, x='PENGHASILAN', nbins=30, 
                                     title='Distribusi Penghasilan Orang Tua', 
                                     color_discrete_sequence=['lightblue'])
            st.plotly_chart(fig_dist, use_container_width=True)
        else:
            st.warning("Data penghasilan tidak tersedia.")

    if st.sidebar.checkbox("Tampilkan Rata-rata Penghasilan per Kategori"):
        if 'PENGHASILAN_KAT' in df.columns:
            st.subheader("📊 Rata-rata Penghasilan per Kategori")
            rata_rata_kategori = df.groupby('PENGHASILAN_KAT')['PENGHASILAN'].mean().reset_index()
            fig_rata_rata = px.bar(rata_rata_kategori, x='PENGHASILAN_KAT', y='PENGHASILAN', 
                                    title='Rata-rata Penghasilan per Kategori', 
                                    color='PENGHASILAN', 
                                    color_continuous_scale=px.colors.sequential.YlGn)
            st.plotly_chart(fig_rata_rata, use_container_width=True)
        else:
            st.warning("Data kategori penghasilan tidak tersedia.")

    # Kesimpulan otomatis
    st.subheader("📋 Kesimpulan")
    if 'PENGHASILAN' in df.columns:
        if mean_val > 7_500_000:
            st.success("🎉 Rata-rata penghasilan orang tua tergolong tinggi.")
        elif mean_val < 2_000_000:
            st.error("⚠️ Rata-rata penghasilan orang tua tergolong rendah.")
        else:
            st.info("ℹ️ Rata-rata penghasilan orang tua berada pada kategori menengah.")
        st.markdown("""
        - Distribusi penghasilan menunjukkan bagaimana kondisi ekonomi orang tua siswa.
        - Sebaran siswa berdasarkan kota dan jenjang pendidikan dapat membantu perencanaan pendidikan yang lebih tepat sasaran.
        - Gunakan filter di sidebar untuk menyesuaikan data dan mendapatkan analisis yang lebih sesuai kebutuhan.
        """)
    else:
        st.info("Data penghasilan tidak tersedia untuk kesimpulan.")

    st.markdown("---")
    st.markdown("🔗 **Sumber Data**: Pastikan data yang diunggah akurat dan terbaru untuk hasil yang optimal.")
    st.markdown("📞 **Hubungi Kami**: Jika Anda memiliki pertanyaan atau masukan, silakan hubungi tim pengembang.")

else:
    st.info("📂 Silakan unggah file Excel terlebih dahulu.")
