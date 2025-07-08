import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import warnings

# Mengurangi warning yang tidak penting
warnings.filterwarnings('ignore', category=UserWarning, message='Could not infer format')
warnings.filterwarnings('ignore', category=UserWarning, message='The argument \'infer_datetime_format\'')

folder_path = "./data_tugu"

csv_files = [
    f for f in os.listdir(folder_path)
    if f.lower().endswith('.csv')
    and 'tugu' in f.lower()
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

    format_waktu = [
        "%d/%m/%Y %H.%M.%S",    # 30/06/2025 12.55.00 (format Tugu)
        "%d-%b-%y %H:%M:%S",    # 25-Jun-25 14:02:00
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

        df['time'] = pd.to_datetime(df[time_col], dayfirst=True, errors='coerce')
        
        jumlah_error = df['time'].isna().sum()
        if jumlah_error > 0:
            print(f"⚠️  {jumlah_error} baris dengan format waktu tidak valid di file {file}")
           
            df = df.dropna(subset=['time'])

    dataframes.append(df)

if not dataframes:
    print("❌ Tidak ada file valid ditemukan.")
    exit()

df = pd.concat(dataframes, ignore_index=True)

df = df.drop_duplicates(subset=['holder', 'time', 'card_no.', 'card_type'], keep='first').reset_index(drop=True)

# Ubah nama kolom time menjadi waktu_tempel_kartu
df = df.rename(columns={'time': 'waktu_tempel_kartu'})

# Standardisasi nama holder
df['holder'] = df['holder'].astype(str).str.strip().str.lower().str.title()

# Simpan data dengan sumber_file untuk export per file nanti
df_with_source = df.copy()

# Hapus kolom yang tidak diinginkan dari data final
columns_to_drop = ['sumber_file']
df = df.drop(columns=[col for col in columns_to_drop if col in df.columns])

df_cleaned = df.copy()


print("\n Statistik:")
print("Jumlah baris setelah cleaning:", len(df_cleaned))
print("Total log:", len(df_cleaned))
print("Jumlah kartu unik:", df_cleaned['card_no.'].nunique() if 'card_no.' in df_cleaned.columns else "Kolom card_no. tidak ditemukan")
print("Holder terbanyak:")
print(df_cleaned['holder'].value_counts().head(5))

df_cleaned['jam_temp'] = df_cleaned['waktu_tempel_kartu'].dt.hour

akses_dinihari = df_cleaned[df_cleaned['jam_temp'] < 6]
print("Log aktivitas antara jam 00:00 - 06:00:", len(akses_dinihari))
print(df_cleaned['card_type'].value_counts())


df_cleaned = df_cleaned.drop(columns=['jam_temp'])
print(df_cleaned['card_type'].value_counts())

card_usage = (
    df_cleaned.groupby(['card_no.', 'holder', 'card_type'])
    .size()
    .reset_index(name='Jumlah Penggunaan')
    .sort_values('Jumlah Penggunaan', ascending=False)
)

df_temp = df_cleaned.copy()
df_temp['jam_temp'] = df_temp['waktu_tempel_kartu'].dt.hour

summary_info = {
    'Total Log': [len(df_cleaned)],
    'Jumlah Kartu Unik': [df_cleaned['card_no.'].nunique()],
    'Jumlah Holder Unik': [df_cleaned['holder'].nunique()],
    'Log Dini Hari (00-06)': [len(akses_dinihari)]
}

# ==================== Export per sheet berdasarkan file sumber (per kamar) ====================
print("\nMembuat laporan per kamar...")
per_file_writer = pd.ExcelWriter("File-TuguCabin.xlsx", engine="xlsxwriter")

for sumber_file, df_per_file in df_with_source.groupby("sumber_file"):
    # Hapus kolom sumber_file dari setiap group
    df_per_file_clean = df_per_file.drop(columns=['sumber_file']).reset_index(drop=True)
    
    # Buat nama sheet dari nama file (maksimal 31 karakter untuk Excel)
    sheet_name = sumber_file.replace(".csv", "").replace("Tugu_30062025_", "Kamar_")[:31]
    
    # Export ke sheet
    df_per_file_clean.to_excel(per_file_writer, sheet_name=sheet_name, index=False)
    print(f"✅ Sheet '{sheet_name}' dibuat dengan {len(df_per_file_clean)} baris data")

per_file_writer.close()
print("📁 File 'File-TuguCabin.xlsx' berhasil dibuat!")
