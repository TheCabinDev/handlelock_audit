import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('Gandekan_20250619_101.xlsx - Sheet1.csv', skiprows=1)
print(df.columns.tolist())

df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_', regex=False)
print("Kolom setelah normalisasi:", df.columns.tolist())

df = df[df['flag'].isnull()]

df = df.drop_duplicates()
df = df.reset_index(drop=True)

print("Jumlah baris setelah cleaning", len(df))
df.head()

df['time'] = pd.to_datetime(df['time'], dayfirst=True, errors='coerce')

df['tanggal'] = df['time'].dt.date
df['jam'] = df['time'].dt.hour
akses_per_jam = df.groupby('jam').size()
akses_per_tanggal = df.groupby('tanggal').size()

print("Total log:", len(df))
print("Jumlah kartu unik:", len(df['card_no.'].unique()))
print("Holder terbanyak:")
print(df['holder'].value_counts().head(5))

df['time'] = pd.to_datetime(df['time'], dayfirst=True, errors='coerce')
df['tanggal'] = df['time'].dt.date
df['jam'] = df['time'].dt.hour
akses_jam = df['jam'].value_counts().sort_index()
akses_jam.plot(kind='bar', title='Akses Pintu Per Jam')
akses_jam.plot(kind='bar', title='Akses Pintu per Jam')
plt.xlabel('Jam')
plt.ylabel('Jumlah Akses')
plt.tight_layout()
plt.savefig('akses_per_jam.png')  # Simpan grafik ke file
plt.show()  # Tampilkan grafik


# df['time'] = pd.to_datetime(df['time'], dayfirst=True, errors='coerce')
# df['jam'] = df['time'].dt.hour
# akses_jam = df['jam'].value_counts().sort_index()

# akses_jam.plot(kind='bar', title='Akses Pintu per Jam')

akses_dinihari = df[(df['time'].dt.hour < 6)]
print("log aktivitas antara jam 00:00 - 06:00:", len(akses_dinihari))

print(df['card_type'].value_counts())

card_usage = (
    df.groupby(['card_no.', 'holder', 'card_type'])
    .size()
    .reset_index(name='jumlah_penggunaan')
    .sort_values('jumlah_penggunaan', ascending=False)
)
card_usage

df['waktu_singkat'] = df['time'].dt.strftime('%Y-%m-%d %H:%M:%S')

df_cleaned = df.drop_duplicates(subset=['holder', 'waktu_singkat'], keep='first')

df_cleaned.to_csv('akses_cleaned.csv', index=False)

df_cleaned.to_excel('akses_cleaned.xlsx', index=False)


df_cleaned.to_excel("akses_cleaned.xlsx", index=False)
