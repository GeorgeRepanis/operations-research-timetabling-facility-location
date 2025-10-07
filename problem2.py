import pandas as pd

# Επαναφορά δεδομένων
fixed_costs = [3500, 9000, 10000, 4000, 3000, 9000, 9000, 3000, 10000, 10000, 9000, 3500]
capacities = [300, 250, 180, 300, 180, 275, 300, 220, 270, 250, 230, 180]
demands = [120, 80, 75, 100, 110, 90, 60, 130, 150, 95, 120, 100]
open_facilities = [1, 4, 5, 7, 8]

assignments = [
    (1, 2, 35.0), (1, 3, 75.0), (1, 7, 60.0), (1, 8, 130.0),
    (4, 2, 45.0), (4, 5, 110.0), (4, 6, 50.0), (4, 10, 95.0),
    (5, 1, 10.0), (5, 4, 100.0),
    (7, 6, 110.0), (7, 9, 90.0), (7, 12, 100.0),
    (8, 9, 100.0), (8, 11, 120.0)
]

# Πίνακας κόστους (σε χιλ. €)
transport_cost_1000 = [
    [100, 80, 50, 50, 100, 120, 90, 60, 70, 65, 110, 100],
    [120, 90, 60, 70, 110, 140, 110, 80, 90, 85, 130, 130],
    [140, 110, 80, 80, 75, 130, 160, 125, 100, 80, 100, 150],
    [160, 125, 100, 90, 100, 150, 190, 150, 130, 90, 150, 150],
    [190, 200, 150, 80, float('inf'), float('inf'), float('inf'), float('inf'), float('inf'), float('inf'), float('inf'), float('inf')],
    [200, 180, 150, float('inf'), float('inf'), float('inf'), float('inf'), float('inf'), float('inf'), float('inf'), float('inf'), float('inf')],
    [120, 100, 80, 60, 70, 65, 110, 120, 90, 90, 75, 110],
    [130, 110, 90, 70, 65, 110, 120, 110, 80, 80, 75, 130],
    [140, 110, 90, 80, 75, 130, 160, 125, 100, 80, 100, 150],
    [160, 125, 100, 90, 100, 150, 190, 150, 130, 90, 150, 150],
    [190, 150, 130, float('inf'), float('inf'), float('inf'), float('inf'), float('inf'), float('inf'), float('inf'), float('inf'), float('inf')],
    [200, 180, 150, 80, 100, float('inf'), float('inf'), float('inf'), 50, 60, 100, 100]
]

# Ανάλυση αναθέσεων
records = []
for facility, center, tons in assignments:
    total_cost_euro = transport_cost_1000[facility-1][center-1] * 1000
    demand = demands[center-1]
    cost_per_ton = total_cost_euro / demand
    cost = cost_per_ton * tons
    records.append([facility, center, tons, cost_per_ton, cost])

df_transfers = pd.DataFrame(records, columns=[
    "Αποθήκη", "Κέντρο Πώλησης", "Ποσότητα (τόνοι)", "Κόστος ανά τόνο (€)", "Κόστος Μεταφοράς (€)"
])

# Ανάλυση παγίων
df_facilities = pd.DataFrame(
    [[i, fixed_costs[i-1]*1000] for i in open_facilities],
    columns=["Αποθήκη", "Πάγιο Κόστος (€)"]
)

# Σύνολα
sum_transport = df_transfers["Κόστος Μεταφοράς (€)"].sum()
sum_fixed = df_facilities["Πάγιο Κόστος (€)"].sum()
final_total = sum_transport + sum_fixed

# Εξαγωγή Excel
excel_path = "Analysis_Cost_Final.xlsx"
with pd.ExcelWriter(excel_path, engine="xlsxwriter") as writer:
    df_facilities.to_excel(writer, index=False, sheet_name="Πάγια Κόστη")
    df_transfers.to_excel(writer, index=False, sheet_name="Αναθέσεις & Κόστη")

    wb = writer.book
    ws1 = writer.sheets["Πάγια Κόστη"]
    ws2 = writer.sheets["Αναθέσεις & Κόστη"]

    bold = wb.add_format({'bold': True})
    euro_fmt = wb.add_format({'num_format': '#,##0.00 €'})
    ton_fmt = wb.add_format({'num_format': '#,##0.0'})

    ws1.set_column("A:A", 12)
    ws1.set_column("B:B", 20, euro_fmt)

    ws2.set_column("A:B", 18)
    ws2.set_column("C:C", 20, ton_fmt)
    ws2.set_column("D:E", 22, euro_fmt)

    # Συνοπτικά
    ws1.write("D2", "Σύνολο Πάγιου Κόστους:", bold)
    ws1.write("E2", sum_fixed, euro_fmt)

    ws2.write("G2", "Σύνολο Κόστους Μεταφοράς:", bold)
    ws2.write("H2", sum_transport, euro_fmt)
    ws2.write("G4", "Συνολικό Κόστος:", bold)
    ws2.write("H4", final_total, euro_fmt)

excel_path

import matplotlib.pyplot as plt
import networkx as nx

# Δημιουργία γράφου για ροές
G = nx.DiGraph()

# Κόμβοι αποθηκών και κέντρων
warehouses = sorted(set(i for i, _, _ in assignments))
centers = sorted(set(j for _, j, _ in assignments))

# Θέσεις κόμβων για καθαρή οριζόντια προβολή
for i, w in enumerate(warehouses):
    G.add_node(f"Α{w}", pos=(0, -i * 1.5))
for j, c in enumerate(centers):
    G.add_node(f"Κ{c}", pos=(6, -j * 1.0))

# Προσθήκη ακμών με ποσότητες (τόνοι)
for w, c, tons in assignments:
    G.add_edge(f"Α{w}", f"Κ{c}", weight=tons)

# Θέσεις και ετικέτες
pos = nx.get_node_attributes(G, "pos")
labels = nx.get_edge_attributes(G, "weight")

# Σχεδίαση διαγράμματος
plt.figure(figsize=(12, 8))
nx.draw_networkx_nodes(G, pos, node_color="lightblue", node_size=1400)
nx.draw_networkx_labels(G, pos, font_size=10)
nx.draw_networkx_edges(G, pos, arrows=True)
nx.draw_networkx_edge_labels(
    G,
    pos,
    edge_labels={(u, v): f"{w:.0f} τ." for (u, v), w in labels.items()},
    font_size=9
)

plt.title("Διάγραμμα Ροής: Από Αποθήκες προς Κέντρα Πώλησης (σε τόνους)", fontsize=14)
plt.axis("off")
plt.tight_layout()
plt.show()
