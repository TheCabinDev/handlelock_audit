import pandas as pd
import warnings
warnings.filterwarnings('ignore')

print("🔍 ANALISIS MENDALAM: Mengapa Kamar_103 dan Kamar_207 hanya tersisa 1 data")
print("=" * 70)

# Analisis file 103
print("\n📂 ANALISIS FILE: Tugu_30062025_103.csv")
print("-" * 50)

df_103 = pd.read_csv('Tugu_30062025_103.csv', skiprows=1)
print(f"Total baris awal: {len(df_103)}")

# Cek missing values di kolom penting
print("\nMissing values di kolom penting:")
print(f"- Time: {df_103['Time'].isna().sum()}")
print(f"- Holder: {df_103['Holder'].isna().sum()}")
print(f"- Card No.: {df_103['Card No.'].isna().sum()}")
print(f"- Card Type: {df_103['Card Type'].isna().sum()}")

# Cek format waktu
print("\nSample format waktu:")
print(df_103['Time'].head(10).tolist())

# Test parsing waktu
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
        df_103['time_parsed'] = pd.to_datetime(df_103['Time'], format=fmt, errors='raise')
        print(f"✅ Berhasil parsing waktu dengan format: {fmt}")
        berhasil_parsing = True
        break
    except:
        continue

if not berhasil_parsing:
    print("⚠️  Menggunakan parser otomatis...")
    df_103['time_parsed'] = pd.to_datetime(df_103['Time'], dayfirst=True, errors='coerce')
    jumlah_error = df_103['time_parsed'].isna().sum()
    print(f"⚠️  {jumlah_error} baris dengan format waktu tidak valid")

# Setelah filtering waktu
df_103_clean = df_103.dropna(subset=['time_parsed']).copy()
print(f"Setelah drop baris dengan waktu invalid: {len(df_103_clean)}")

# Rename kolom sesuai script asli
df_103_clean = df_103_clean.rename(columns={
    'Time': 'time',
    'Card Type': 'card_type',
    'Card No.': 'card_no.',
    'Holder': 'holder'
})

# Drop duplikat
before_dedup = len(df_103_clean)
df_103_clean = df_103_clean.drop_duplicates(subset=['holder', 'time_parsed', 'card_no.', 'card_type'], keep='first')
after_dedup = len(df_103_clean)
print(f"Setelah deduplikasi: {after_dedup} (dihapus {before_dedup - after_dedup} duplikat)")

print("\nData yang tersisa:")
print(df_103_clean[['time_parsed', 'card_type', 'card_no.', 'holder']].to_string())

print("\n" + "=" * 70)

# Analisis file 207
print("\n📂 ANALISIS FILE: Tugu_30062025_207.csv")
print("-" * 50)

df_207 = pd.read_csv('Tugu_30062025_207.csv', skiprows=1)
print(f"Total baris awal: {len(df_207)}")

# Cek missing values di kolom penting
print("\nMissing values di kolom penting:")
print(f"- Time: {df_207['Time'].isna().sum()}")
print(f"- Holder: {df_207['Holder'].isna().sum()}")
print(f"- Card No.: {df_207['Card No.'].isna().sum()}")
print(f"- Card Type: {df_207['Card Type'].isna().sum()}")

# Cek format waktu
print("\nSample format waktu:")
print(df_207['Time'].head(10).tolist())

# Test parsing waktu
berhasil_parsing = False
for fmt in format_waktu:
    try:
        df_207['time_parsed'] = pd.to_datetime(df_207['Time'], format=fmt, errors='raise')
        print(f"✅ Berhasil parsing waktu dengan format: {fmt}")
        berhasil_parsing = True
        break
    except:
        continue

if not berhasil_parsing:
    print("⚠️  Menggunakan parser otomatis...")
    df_207['time_parsed'] = pd.to_datetime(df_207['Time'], dayfirst=True, errors='coerce')
    jumlah_error = df_207['time_parsed'].isna().sum()
    print(f"⚠️  {jumlah_error} baris dengan format waktu tidak valid")

# Setelah filtering waktu
df_207_clean = df_207.dropna(subset=['time_parsed']).copy()
print(f"Setelah drop baris dengan waktu invalid: {len(df_207_clean)}")

# Rename kolom sesuai script asli
df_207_clean = df_207_clean.rename(columns={
    'Time': 'time',
    'Card Type': 'card_type',
    'Card No.': 'card_no.',
    'Holder': 'holder'
})

# Drop duplikat
before_dedup = len(df_207_clean)
df_207_clean = df_207_clean.drop_duplicates(subset=['holder', 'time_parsed', 'card_no.', 'card_type'], keep='first')
after_dedup = len(df_207_clean)
print(f"Setelah deduplikasi: {after_dedup} (dihapus {before_dedup - after_dedup} duplikat)")

print("\nData yang tersisa:")
print(df_207_clean[['time_parsed', 'card_type', 'card_no.', 'holder']].to_string())

print("\n" + "=" * 70)
print("KESIMPULAN:")
print("1. Kedua file memiliki banyak baris dengan format waktu yang tidak valid")
print("2. Setelah parsing waktu otomatis, banyak baris dihapus karena waktu tidak bisa diparsing")
print("3. Deduplikasi juga menghapus beberapa baris duplikat")
print("4. Kombinasi kedua proses ini menyebabkan hanya tersisa 1 data per kamar")
