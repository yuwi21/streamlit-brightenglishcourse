import streamlit as st
import pandas as pd
import os
from datetime import date

st.set_page_config(page_title="Bright English Course", layout="wide")

# Fungsi simpan/baca file CSV
def simpan_data(df, filename):
    df.to_csv(filename, index=False)

def baca_data(filename, kolom):
    if os.path.exists(filename):
        return pd.read_csv(filename)
    else:
        return pd.DataFrame(columns=kolom)

# Nama file CSV
murid_file = "murid.csv"
absen_file = "absensi.csv"

# Load data dari file
df_murid = baca_data(murid_file, ["Nama", "Jenjang", "Kelas", "No WA"])
df_absensi = baca_data(absen_file, ["Nama", "Tanggal", "Hadir", "Bayar", "Catatan"])

st.title("📚 Bright English Course Management System")
menu = st.tabs(["➕ Tambah Murid", "📝 Absensi & Pembayaran", "📊 Rekap Data"])

# ➕ Tambah Murid
with menu[0]:
    st.header("📋 Form Tambah Data Murid")
    with st.form("form_murid", clear_on_submit=True):
        nama = st.text_input("Nama Lengkap")
        jenjang = st.selectbox("Jenjang Pendidikan", ["TK", "SD", "SMP", "SMA"])
        kelas = st.selectbox("Jenis Kelas", ["Privat", "Semi Privat", "Reguler"])
        no_wa = st.text_input("Nomor WhatsApp Orang Tua")
        submit = st.form_submit_button("Simpan Data")

        if submit:
            data_baru = pd.DataFrame([{
                "Nama": nama,
                "Jenjang": jenjang,
                "Kelas": kelas,
                "No WA": no_wa
            }])
            df_murid = pd.concat([df_murid, data_baru], ignore_index=True)
            simpan_data(df_murid, murid_file)
            st.success(f"✅ Data murid '{nama}' berhasil disimpan.")

    st.subheader("📚 Daftar Murid")
    if not df_murid.empty:
        st.dataframe(df_murid, use_container_width=True)
    else:
        st.info("Belum ada data murid.")

    st.subheader("🗑️ Hapus Data Murid")
    if not df_murid.empty:
        murid_hapus = st.selectbox("Pilih murid yang ingin dihapus", df_murid['Nama'].unique().tolist())
        if st.button("Hapus Murid"):
            df_murid = df_murid[df_murid['Nama'] != murid_hapus]
            simpan_data(df_murid, murid_file)
            st.success(f"✅ Data murid '{murid_hapus}' berhasil dihapus.")
    else:
        st.info("Tidak ada murid yang bisa dihapus.")

# 📝 Absensi & Pembayaran
with menu[1]:
    st.header("📝 Input Absensi dan Pembayaran")
    if not df_murid.empty:
        murid_list = df_murid['Nama'].tolist()
        nama_pilih = st.selectbox("Pilih Murid", murid_list)
        tanggal = st.date_input("Tanggal Pertemuan", value=date.today())
        hadir = st.checkbox("Murid Hadir", value=True)
        bayar = st.checkbox("Sudah Membayar", value=False)
        catatan = st.text_area("Catatan Tambahan", placeholder="(opsional)")
        simpan = st.button("Simpan Absensi")

        if simpan:
            data_baru = pd.DataFrame([{
                "Nama": nama_pilih,
                "Tanggal": tanggal,
                "Hadir": hadir,
                "Bayar": bayar,
                "Catatan": catatan
            }])
            df_absensi = pd.concat([df_absensi, data_baru], ignore_index=True)
            simpan_data(df_absensi, absen_file)
            st.success("✅ Absensi berhasil disimpan!")

        st.subheader("📅 Riwayat Absensi")
        st.dataframe(df_absensi, use_container_width=True)
    else:
        st.warning("⚠️ Tambahkan data murid terlebih dahulu.")

# 📊 Rekap Data
with menu[2]:
    st.header("📊 Rekapitulasi Pembayaran & Kehadiran")
    if not df_absensi.empty:
        df_absensi['Hadir'] = df_absensi['Hadir'].astype(bool)
        df_absensi['Bayar'] = df_absensi['Bayar'].astype(bool)
        rekap = df_absensi.groupby("Nama").agg(
            Total_Pertemuan=('Nama', 'count'),
            Total_Hadir=('Hadir', 'sum'),
            Sudah_Bayar=('Bayar', 'sum')
        ).reset_index()

        rekap['Reward'] = rekap['Sudah_Bayar'].apply(lambda x: '✅ Bonus Speaking' if x >= 10 else '-')
        st.dataframe(rekap, use_container_width=True)
        st.markdown("✅ *Murid yang sudah membayar 10x akan mendapatkan 1x kelas speaking gratis.*")
    else:
        st.info("📄 Belum ada data absensi untuk direkap.")
