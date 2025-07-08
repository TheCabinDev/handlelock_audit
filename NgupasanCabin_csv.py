import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import warnings

# Mengurangi warning yang tidak penting
warnings.filterwarnings('ignore', category=UserWarning, message='Could not infer format')
warnings.filterwarnings('ignore', category=UserWarning, message='The argument \'infer_datetime_format\'')

folder_path = "./data_ngupasan"

csv_files = [
    f for f in os.listdir(folder_path)
    if f.lower().endswith('.csv')
    and 'ngupasan' in f.lower()
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
        "%d/%m/%Y %H.%M.%S",    # 30/06/2025 12.55.00
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

# ==================== Filter berdasarkan kolom flag ====================
# Hapus baris dengan flag tertentu yang tidak diinginkan
flag_to_remove = ['latch bold record', 'latch bolt record', 'exit double locked', 'double locked record']

print(f"\n🔍 Filtering data berdasarkan kolom flag...")
print(f"Total baris sebelum filter: {len(df)}")

if 'flag' in df.columns:
    # Cek berapa baris yang akan dihapus
    mask_remove = df['flag'].str.lower().str.strip().isin([f.lower() for f in flag_to_remove])
    baris_dihapus = mask_remove.sum()
    
    if baris_dihapus > 0:
        print(f"Menghapus {baris_dihapus} baris dengan flag:")
        for flag in flag_to_remove:
            count = df['flag'].str.lower().str.strip().eq(flag.lower()).sum()
            if count > 0:
                print(f"  - '{flag}': {count} baris")
        
        # Filter out baris yang tidak diinginkan
        df = df[~mask_remove].reset_index(drop=True)
        print(f"Total baris setelah filter: {len(df)}")
    else:
        print("Tidak ada baris dengan flag yang perlu dihapus")
else:
    print("⚠️  Kolom 'flag' tidak ditemukan, skip filtering")

# ==================== Cleaning kolom kosong/NaN ====================
print(f"\n Cleaning data kosong/NaN...")
print(f"Total baris sebelum cleaning NaN: {len(df)}")

# Hapus baris yang memiliki nilai NaN/kosong di kolom penting
kolom_penting = ['holder', 'card_no.', 'card_type']
for kolom in kolom_penting:
    if kolom in df.columns:
        sebelum = len(df)
        # Hapus baris dengan nilai kosong, NaN, atau string 'nan'/'null'
        df = df[df[kolom].notna() & 
                (df[kolom].astype(str).str.strip() != '') & 
                (df[kolom].astype(str).str.lower() != 'nan') &
                (df[kolom].astype(str).str.lower() != 'null')].reset_index(drop=True)
        sesudah = len(df)
        if sebelum != sesudah:
            print(f"  - Kolom '{kolom}': {sebelum - sesudah} baris dengan nilai kosong dihapus")

print(f"Total baris setelah cleaning NaN: {len(df)}")

# duplikat = df[df.duplicated(subset=['holder', 'time', 'card_no.'], keep='first')]
# duplikat.to_csv('duplikat.csv', index=False)

df = df.drop_duplicates(subset=['holder', 'time', 'card_no.', 'card_type', 'id_no.'], keep='first').reset_index(drop=True)

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
per_file_writer = pd.ExcelWriter("File-NgupasanCabin.xlsx", engine="xlsxwriter")

for sumber_file, df_per_file in df_with_source.groupby("sumber_file"):
    # Hapus kolom sumber_file dari setiap group
    df_per_file_clean = df_per_file.drop(columns=['sumber_file']).reset_index(drop=True)
    
    # Buat nama sheet dari nama file (maksimal 31 karakter untuk Excel)
    sheet_name = sumber_file.replace(".csv", "").replace("Ngupasan_", "Kamar_")[:31]
    
    # Export ke sheet
    df_per_file_clean.to_excel(per_file_writer, sheet_name=sheet_name, index=False)
    print(f"✅ Sheet '{sheet_name}' dibuat dengan {len(df_per_file_clean)} baris data")

per_file_writer.close()
print("📁 File 'File-NgupasanCabin.xlsx' berhasil dibuat!")
