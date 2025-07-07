import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import warnings

# Mengurangi warning yang tidak penting
warnings.filterwarnings('ignore', category=UserWarning, message='Could not infer format')
warnings.filterwarnings('ignore', category=UserWarning, message='The argument \'infer_datetime_format\'')

folder_path = "."

csv_files = [
    f for f in os.listdir(folder_path)
    if f.lower().endswith('.csv')
    and 'purwo' in f.lower()
    and not f.startswith('akses_cleaned')
]

dataframes = []

for file in csv_files:
    df = pd.read_csv(os.path.join(folder_path, file), skiprows=1)
    df["sumber_file"] = file

    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_', regex=False)

    possible_time_cols = [col for col in df.columns if 'time' in col and col != 'time_issued' and col != 'time_modified']
    if not possible_time_cols:
        print(f"❌ Lewatkan file {file}: kolom waktu tidak ditemukan.")
        continue

    time_col = possible_time_cols[0]
    print(f"📅 Memproses kolom waktu '{time_col}' di file {file}")

    # Coba berbagai format waktu yang umum digunakan
    format_waktu = [
        "%d-%b-%y %H:%M:%S",    # 25-Jun-25 14:02:00 (format yang ada di file)
        "%d-%b-%Y %H:%M:%S",    # 25-Jun-2025 14:02:00
        "%d/%m/%Y %H:%M:%S",    # 01/01/2023 12:30:45
        "%Y-%m-%d %H:%M:%S",    # 2023-01-01 12:30:45
        "%d-%m-%Y %H:%M:%S",    # 01-01-2023 12:30:45
        "%d/%m/%y %H:%M:%S",    # 01/01/23 12:30:45
        "%d-%b-%y %H:%M",       # 25-Jun-25 14:02 (tanpa detik)
        "%d-%b-%Y %H:%M"        # 25-Jun-2025 14:02 (tanpa detik)
    ]
    
    berhasil_parsing = False
    for fmt in format_waktu:
        try:
            df['time'] = pd.to_datetime(df[time_col], format=fmt, errors='raise')
            print(f"✅ Berhasil parsing waktu dengan format: {fmt}")
            berhasil_parsing = True
            break
        except ValueError:
            continue
        except Exception as e:
            continue
    
    if not berhasil_parsing:
        print(f"⚠️  Format waktu di file {file} tidak standar, menggunakan parser otomatis...")
        # Gunakan parser yang lebih modern tanpa infer_datetime_format yang deprecated
        df['time'] = pd.to_datetime(df[time_col], dayfirst=True, errors='coerce')
        
        # Cek apakah ada nilai NaT (Not a Time) setelah parsing
        jumlah_error = df['time'].isna().sum()
        if jumlah_error > 0:
            print(f"⚠️  {jumlah_error} baris dengan format waktu tidak valid di file {file}")
            # Hapus baris dengan waktu yang tidak valid
            df = df.dropna(subset=['time'])

    dataframes.append(df)

if not dataframes:
    print("❌ Tidak ada file valid ditemukan.")
    exit()

df = pd.concat(dataframes, ignore_index=True)

duplikat = df[df.duplicated(subset=['holder', 'time', 'card_no.'], keep='first')]
duplikat.to_csv('duplikat.csv', index=False)

df = df.drop_duplicates(subset=['holder', 'time', 'card_no.', 'card_type'], keep='first').reset_index(drop=True)

df['tanggal'] = df['time'].dt.date
df['jam'] = df['time'].dt.hour
df['holder'] = df['holder'].astype(str).str.strip().str.lower().str.title()
df['waktu_singkat'] = df['time'].dt.strftime('%Y-%m-%d %H:%M:%S')

df_cleaned = df.copy()


print("\n Statistik:")
print("Jumlah baris setelah cleaning:", len(df_cleaned))
print("Total log:", len(df_cleaned))
print("Jumlah kartu unik:", df_cleaned['card_no.'].nunique() if 'card_no.' in df_cleaned.columns else "Kolom card_no. tidak ditemukan")
print("Holder terbanyak:")
print(df_cleaned['holder'].value_counts().head(5))

akses_jam = df_cleaned['jam'].value_counts().sort_index()
if not akses_jam.empty:
    akses_jam.plot(kind='bar', title='Akses Pintu per Jam')
    plt.xlabel('Jam')
    plt.ylabel('Jumlah Akses')
    plt.tight_layout()
    plt.savefig('akses_per_jam.png')
    plt.show()

df_cleaned['holder'].value_counts().head(10).plot(kind='barh', title='Top 10 Holder')
plt.xlabel('Jumlah Akses')
plt.tight_layout()
plt.savefig('top_holder.png')
plt.show()

akses_dinihari = df_cleaned[df_cleaned['jam'] < 6]
print("Log aktivitas antara jam 00:00 - 06:00:", len(akses_dinihari))
print(df_cleaned['card_type'].value_counts())

card_usage = (
    df_cleaned.groupby(['card_no.', 'holder', 'card_type'])
    .size()
    .reset_index(name='Jumlah Penggunaan')
    .sort_values('Jumlah Penggunaan', ascending=False)
)

df_cleaned.to_csv('akses_cleaned.csv', index=False)
df_cleaned.to_excel('akses_cleaned.xlsx', index=False)

akses_per_tanggal = df_cleaned['tanggal'].value_counts().sort_index()
plt.figure(figsize=(12, 5))
akses_per_tanggal.plot(kind='line', marker='o', title='Akses Pintu per Tanggal')
plt.xlabel('Tanggal')
plt.ylabel('Jumlah Akses')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('akses_per_tanggal.png')
plt.show()

pivot_heatmap = df_cleaned.pivot_table(index='jam', columns='tanggal', values='holder', aggfunc='count')
plt.figure(figsize=(12, 7))
sns.heatmap(pivot_heatmap, cmap='YlGnBu', linewidths=0.5)
plt.title("Heatmap Akses: Jam vs Tanggal")
plt.xlabel("Tanggal")
plt.ylabel("Jam")
plt.tight_layout()
plt.savefig('heatmap_jam_vs_tanggal.png')
plt.show()

plt.figure(figsize=(6, 6))
df_cleaned['card_type'].value_counts().plot(kind='pie', autopct='%1.1f%%', startangle=140)
plt.title('Distribusi Jenis Kartu')
plt.ylabel('')
plt.tight_layout()
plt.savefig('distribusi_card_type.png')
plt.show()

summary_writer = pd.ExcelWriter('laporan_ringkasan_akses.xlsx', engine='xlsxwriter')

summary_info = {
    'Total Log': [len(df_cleaned)],
    'Jumlah Kartu Unik': [df_cleaned['card_no.'].nunique()],
    'Jumlah Holder Unik': [df_cleaned['holder'].nunique()],
    'Log Dini Hari (00-06)': [len(akses_dinihari)]
}
pd.DataFrame(summary_info).to_excel(summary_writer, sheet_name='Ringkasan Umum', index=False)

df_cleaned['jam'].value_counts().sort_index().reset_index().rename(
    columns={'index': 'Jam', 'jam': 'Jumlah Akses'}
).to_excel(summary_writer, sheet_name='Akses per Jam', index=False)

akses_per_tanggal.reset_index().rename(columns={'index': 'Tanggal', 'tanggal': 'Jumlah Akses'}).to_excel(
    summary_writer, sheet_name='Akses per Tanggal', index=False
)

df_cleaned['holder'].value_counts().head(10).reset_index().rename(
    columns={'index': 'Holder', 'holder': 'Jumlah Akses'}
).to_excel(summary_writer, sheet_name='Top 10 Holder', index=False)

card_usage.to_excel(summary_writer, sheet_name='Penggunaan Kartu', index=False)
akses_dinihari.to_excel(summary_writer, sheet_name='Log Dini Hari', index=False)

summary_writer.close()

# ==================== Export per sheet berdasarkan file sumber ====================
per_file_writer = pd.ExcelWriter("akses_cleaned_per_file.xlsx", engine="xlsxwriter")
for sumber_file, df_per_file in df_cleaned.groupby("sumber_file"):
    sheet_name = sumber_file.replace(".csv", "")[:31]
    df_per_file.to_excel(per_file_writer, sheet_name=sheet_name, index=False)
per_file_writer.close()
