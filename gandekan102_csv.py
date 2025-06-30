import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Baca file CSV
df = pd.read_csv('Gandekan_20250619_102.xlsx - Sheet1.csv', skiprows=1)

# 2. Normalisasi nama kolom
df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_', regex=False)

# 3. Filter hanya baris yang flag-nya kosong (log valid)
df = df[df['flag'].isnull()]

# 4. Hapus data duplikat dan reset index
df = df.drop_duplicates()
df = df.reset_index(drop=True)

# 5. Ubah kolom 'time' ke format datetime
df['time'] = pd.to_datetime(df['time'], dayfirst=True, errors='coerce')

# 6. Tambah kolom baru: tanggal (YYYY-MM-DD) dan jam (0-23)
df['tanggal'] = df['time'].dt.date
df['jam'] = df['time'].dt.hour

# 7. Normalisasi penulisan nama holder (huruf kecil semua lalu kapital di awal kata)
df['holder'] = df['holder'].str.strip().str.lower()
df['holder'] = df['holder'].str.title()

# 8. Statistik dasar
print("Jumlah baris setelah cleaning:", len(df))
print("Total log:", len(df))
print("Jumlah kartu unik:", len(df['card_no.'].unique()))
print("Holder terbanyak:")
print(df['holder'].value_counts().head(5))

# 9. Visualisasi: jumlah akses per jam (bar chart)
akses_jam = df['jam'].value_counts().sort_index()
akses_jam.plot(kind='bar', title='Akses Pintu per Jam')
plt.xlabel('Jam')
plt.ylabel('Jumlah Akses')
plt.tight_layout()
plt.savefig('akses_per_jam.png')
plt.show()

# 10. Visualisasi: 10 holder dengan akses terbanyak (horizontal bar chart)
df['holder'].value_counts().head(10).plot(kind='barh', title='Top 10 Holder')
plt.xlabel('Jumlah Akses')
plt.tight_layout()
plt.savefig('top_holder.png')
plt.show()

# 11. Analisis aktivitas dini hari (antara jam 00:00–05:59)
akses_dinihari = df[df['jam'] < 6]
print("Log aktivitas antara jam 00:00 - 06:00:", len(akses_dinihari))

# 12. Statistik jenis kartu
print(df['card_type'].value_counts())

# 13. Buat tabel ringkasan penggunaan kartu berdasarkan nomor kartu, pemilik, dan tipe kartu
card_usage = (
    df.groupby(['card_no.', 'holder', 'card_type'])
    .size()
    .reset_index(name='jumlah_penggunaan')
    .sort_values('jumlah_penggunaan', ascending=False)
)

# 14. Buat kolom 'waktu singkat' untuk identifikasi duplikat berdasarkan waktu per detik
df['waktu_singkat'] = df['time'].dt.strftime('%Y-%m-%d %H:%M:%S')

# 15. Hapus duplikat berdasarkan holder + waktu singkat
df_cleaned = df.drop_duplicates(subset=['holder', 'waktu_singkat'], keep='first')

# 16. Simpan data hasil cleaning ke file
df_cleaned.to_csv('akses_cleaned102.csv', index=False)
df_cleaned.to_excel('akses_cleaned102.xlsx', index=False)


# ====================
# Visualisasi Lanjutan
# ====================

# Akses per Tanggal (Line Chart)
akses_per_tanggal = df_cleaned['tanggal'].value_counts().sort_index()
plt.figure(figsize=(12, 5))
akses_per_tanggal.plot(kind='line', marker='o', title='Akses Pintu per Tanggal')
plt.xlabel('Tanggal')
plt.ylabel('Jumlah Akses')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('akses_per_tanggal.png')
plt.show()

# Heatmap : Jam, Tanggal
pivot_heatmap = df_cleaned.pivot_table(index='jam', columns='tanggal', values='holder', aggfunc='count')
plt.figure(figsize=(12, 7))
sns.heatmap(pivot_heatmap, cmap='YlGnBu', linewidths=0.5)
plt.title("Heatmap Akses per Jam dan Tanggal")
plt.xlabel("Tanggal")
plt.ylabel("Jam")
plt.tight_layout()
plt.savefig('heatmap_jam_vs_tanggal.png')
plt.show()

# Pie Chart Distribusi Jenis Kartu
plt.figure(figsize=(6, 6))
df_cleaned['card_type'].value_counts().plot(kind='pie', autopct='%1.1f%%', startangle=140)
plt.title("Distribusi Jenis Kartu")
plt.tight_layout()
plt.savefig('distribusi_jenis_kartu.png')
plt.show()




