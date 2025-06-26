import pandas as pd

df = pd.read_csv('BHA_20250619_101.csv', skiprows=1)
print(df.columns.tolist())

frekuensi = df ['Card Type'].value_counts()
print("Frekuensi penggunaan Card Type:\n", frekuensi)

terbanyak = frekuensi.idxmax()
jumlah = frekuensi.max()


print(f"\nCard type yang paling banyak digunakan adalah: {terbanyak} (sebanyak {jumlah} kali)")





