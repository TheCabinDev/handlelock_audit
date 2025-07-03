import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv('Gandekan_20250619_304.xlsx - Sheet1.csv', skiprows=1)

df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_', regex=False)

df = df[df['flag'].isnull()]

df = df.drop_duplicates().reset_index(drop=True)

df['time'] = pd.to_datetime(df['time'], dayfirst=True, errors='coerce')
df['tanggal'] = df['time'].dt.date
df['jam'] = df['time'].dt.hour

df['holder'] = df['holder'].str.strip().str.lower().str.title()

df['waktu_singkat'] = df['time'].dt.strftime('%Y-%m-%d %H:%M:%S')

df_cleaned = df.drop_duplicates(subset=['holder', 'waktu_singkat'], keep='first')

print("Jumlah baris setelah cleaning", len(df_cleaned))
print("Total log:", len(df_cleaned))
print("Jumlah kartu unik:", len(df_cleaned['card_no.'].unique()))
print("Holder terbanyak:")
print(df_cleaned['holder'].value_counts().head(5))

akses_jam = df_cleaned['jam'].value_counts().sort_index()
akses_jam.plot(kind='bar', title='Akses Pintu per Jam')
plt.xlabel('Jam')
plt.ylabel('Jumlah Akses')
plt.tight_layout()
plt.savefig('akses_per_jam304.png')
plt.show()

df_cleaned['holder'].value_counts().head(10).plot(kind='barh', title='Top 10 Holder')
plt.xlabel('Jumlah Akses')
plt.tight_layout()
plt.savefig('top_holder304.png')
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

df_cleaned.to_csv('akses_cleaned304.csv', index=False)
df_cleaned.to_excel('akses_cleaned304.xlsx', index=False)

# ====================
# Visualisasi Lanjutan
# ====================


akses_per_tanggal = df_cleaned['tanggal'].value_counts().sort_index()
plt.figure(figsize=(12, 5))
akses_per_tanggal.plot(kind='line', marker='o', title='Akses Pintu per Tanggal')
plt.xlabel('Tanggal')
plt.ylabel('Jumlah Akses')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('akses_per_tanggal304.png')
plt.show()

pivot_heatmap = df_cleaned.pivot_table(index='jam', columns='tanggal', values='holder', aggfunc='count')
plt.figure(figsize=(12, 7))
sns.heatmap(pivot_heatmap, cmap='YlGnBu', linewidths=0.5)
plt.title("Heatmap Akses: Jam vs Tanggal")
plt.xlabel("Tanggal")
plt.ylabel("Jam")
plt.tight_layout()
plt.savefig('heatmap_jam_vs_tanggal304.png')
plt.show()

plt.figure(figsize=(6, 6))
df_cleaned['card_type'].value_counts().plot(kind='pie', autopct='%1.1f%%', startangle=140)
plt.title('Distribusi Jenis Kartu')
plt.ylabel('')
plt.tight_layout()
plt.savefig('distribusi_card_type304.png')
plt.show()


# =======================
# EXPORT LAPORAN EXCEL
# =======================

summary_writer = pd.ExcelWriter('laporan_ringkasan_akses304.xlsx', engine='xlsxwriter')

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