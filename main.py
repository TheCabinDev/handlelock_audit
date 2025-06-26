from rich.console import Console
from panels import show_panel
from tables import show_table

console = Console()

console.print("[bold green]Selamat datang di program Python dengan Rich![/bold green] 🎉")
console.print("Ini [red]teks merah[/red], ini [blue]biru[/blue], dan ini [bold yellow]kuning tebal[/bold yellow]")


show_panel(console)
show_table(console)

# main.py
import requests
from rich.console import Console
from rich.table import Table

console = Console()

# Panggil API
url = "https://jsonplaceholder.typicode.com/users"
response = requests.get(url)

# Cek apakah berhasil
if response.status_code == 200:
    data = response.json()  # ubah ke dict/list Python

    # Buat tabel
    table = Table(title="Daftar Pengguna dari Internet")
    table.add_column("Nama", style="cyan")
    table.add_column("Email", style="magenta")
    table.add_column("Kota", style="green")

    for user in data:
        table.add_row(user["name"], user["email"], user["address"]["city"])

    console.print(table)
else:
    console.print(f"[red]Gagal mengambil data: {response.status_code}[/red]")

