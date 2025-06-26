import csv

produk = [
    ["Nama", "Harga"],
    ["Laptop", "10000000"],
    ["Mouse", "150000"]
]

with open("produk.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(produk)
