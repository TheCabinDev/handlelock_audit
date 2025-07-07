import pandas as pd
import warnings
warnings.filterwarnings('ignore')

print("INVESTIGASI FORMAT WAKTU: Mengapa parsing gagal?")
print("=" * 60)

# Analisis file 103
print("\n ANALISIS DETAIL FORMAT WAKTU: Tugu_30062025_103.csv")
print("-" * 50)

df_103 = pd.read_csv('Tugu_30062025_103.csv', skiprows=1)

# Cek sample data di baris yang bermasalah
print("Sample 20 baris pertama untuk melihat format waktu:")
for i, time_val in enumerate(df_103['Time'].head(20)):
    print(f"Baris {i+1}: '{time_val}' (tipe: {type(time_val)})")

print("\nSample 10 baris di tengah:")
middle_start = len(df_103) // 2
for i, time_val in enumerate(df_103['Time'].iloc[middle_start:middle_start+10]):
    print(f"Baris {middle_start+i+1}: '{time_val}' (tipe: {type(time_val)})")

print("\nSample 10 baris terakhir:")
for i, time_val in enumerate(df_103['Time'].tail(10)):
    print(f"Baris {len(df_103)-10+i+1}: '{time_val}' (tipe: {type(time_val)})")

# Cek baris yang bisa diparsing vs tidak bisa
print("\n Testing parsing manual:")
format_target = "%d/%m/%Y %H.%M.%S"

berhasil = []
gagal = []

for idx, time_val in enumerate(df_103['Time']):
    try:
        parsed = pd.to_datetime(time_val, format=format_target, errors='raise')
        berhasil.append((idx, time_val, parsed))
    except:
        gagal.append((idx, time_val))

print(f"Berhasil parsing: {len(berhasil)} baris")
print(f"Gagal parsing: {len(gagal)} baris")

if len(berhasil) > 0:
    print("\nContoh yang berhasil diparsing:")
    for i, (idx, original, parsed) in enumerate(berhasil[:5]):
        print(f"  Baris {idx+1}: '{original}' → {parsed}")

if len(gagal) > 0:
    print("\nContoh yang gagal diparsing:")
    for i, (idx, original) in enumerate(gagal[:10]):
        print(f"  Baris {idx+1}: '{original}' (len: {len(str(original))})")

print("\n" + "=" * 60)

# Analisis file 207
print("\n ANALISIS DETAIL FORMAT WAKTU: Tugu_30062025_207.csv")
print("-" * 50)

df_207 = pd.read_csv('Tugu_30062025_207.csv', skiprows=1)

print("Sample 10 baris pertama untuk melihat format waktu:")
for i, time_val in enumerate(df_207['Time'].head(10)):
    print(f"Baris {i+1}: '{time_val}' (tipe: {type(time_val)})")

# Test parsing untuk file 207
berhasil_207 = []
gagal_207 = []

for idx, time_val in enumerate(df_207['Time']):
    try:
        parsed = pd.to_datetime(time_val, format=format_target, errors='raise')
        berhasil_207.append((idx, time_val, parsed))
    except:
        gagal_207.append((idx, time_val))

print(f"\nBerhasil parsing: {len(berhasil_207)} baris")
print(f"Gagal parsing: {len(gagal_207)} baris")

if len(berhasil_207) > 0:
    print("\nContoh yang berhasil diparsing:")
    for i, (idx, original, parsed) in enumerate(berhasil_207[:5]):
        print(f"  Baris {idx+1}: '{original}' → {parsed}")

if len(gagal_207) > 0:
    print("\nContoh yang gagal diparsing:")
    for i, (idx, original) in enumerate(gagal_207[:10]):
        print(f"  Baris {idx+1}: '{original}' (len: {len(str(original))})")
