import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set(style="whitegrid")

file_path = "Gandekan_20250619_104.xlsx - Sheet1.csv"
df = pd.read_csv(file_path)

df_cleaned = df[1:].copy()
df_cleaned.columns = df.iloc[0]
df_cleaned.reset_index(drop=True, inplace=True)

df_cleaned.columns = [
    "event_id", "time", "flag", "card_type", "card_no", "holder", "id_no", "issuer", "time_issued", "modifier", "time_modified"
]

df_cleaned = df_cleaned[df_cleaned['flag'].isnull()]
df_cleaned = df_cleaned.drop_duplicates()
df_cleaned = df_cleaned.reset_index(drop=True)


df_cleaned["time"] = pd.to_datetime(df_cleaned["time"], errors="coerce")

df_cleaned["hour"] = df_cleaned["time"].dt.hour
df_cleaned["date"] = df_cleaned["time"].dt.date

print("\nJumlah data:", len(df_cleaned))
print("\nJumah unik flag:\n", df_cleaned["flag"].value_counts())
print("\nWaktu paling awal", df_cleaned["time"].min())
print("Waktu paling akhir:", df_cleaned["time"].max())

plt.figure(figsize=(10, 5))
df_cleaned["hour"].value_counts().sort_index().plot(kind="bar", color="skyblue")
plt.title("Distribusi Event Per Jam")
plt.xlabel("Jam (0-23)")
plt.ylabel("Jumlah Event")
plt.tight_layout()
plt.show()

flag_counts = df_cleaned["flag"].value_counts()
if not flag_counts.empty:
    plt.figure(figsize=(8, 5))
    flag_counts.plot(kind="barh", color="salmon")
    plt.title("Distribusi Tipe Event (Flag)")
    plt.xlabel("Jumlah")
    plt.ylabel("Jenis Flag")
    plt.tight_layout()
    plt.show()
else:
    print("⚠️ Tidak ada data flag untuk ditampilkan.")


df_cleaned.to_csv("akses_cleaned104.csv", index=False)
df_cleaned.to_excel("akses_cleaned104.xlsx", index=False)
