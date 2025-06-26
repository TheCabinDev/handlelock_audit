from rich.table import Table

def show_table(console):
    table = Table(title="Daftar Produk")
    table.add_column("Produk", style="cyan")
    table.add_column("Harga", justify="right", style="green")
    table.add_row("Laptop", "Rp 10.000.000")
    table.add_row("Mouse", "Rp 150.000")
    console.print(table)
