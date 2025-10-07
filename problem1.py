import pandas as pd
from pulp import LpProblem, LpVariable, lpSum, LpMinimize
import os

# Δεδομένα
days = ["Δευτέρα", "Τρίτη", "Τετάρτη", "Πέμπτη", "Παρασκευή"]
slots = ["08:00–10:00", "10:15–12:15", "14:00–16:00", "16:15–18:15"]
subjects = {
    "Αγγλικά": {"καθηγητής": "Γεωμανίδης", "τμήματα": [1, 2], "ώρες": 1},
    "Βιολογία": {"καθηγητής": "Ινσουλίνα", "τμήματα": [1, 2], "ώρες": 3},
    "Ιστορία-Γεωγραφία": {"καθηγητής": "Χαρτούλα", "τμήματα": [1, 2], "ώρες": 2},
    "Μαθηματικά1": {"καθηγητής": "Αντιπαραγωγος", "τμήματα": [1], "ώρες": 4},
    "Μαθηματικά2": {"καθηγητής": "Λαθοπράξης", "τμήματα": [2], "ώρες": 4},
    "Φυσική": {"καθηγητής": "Κιρκοφίδου", "τμήματα": [1, 2], "ώρες": 3},
    "Φιλοσοφία": {"καθηγητής": "Πλατιζών", "τμήματα": [1, 2], "ώρες": 1},
    "Φυσική Αγωγή1": {"καθηγητής": "Μπρατσάκης", "τμήματα": [1], "ώρες": 1},
    "Φυσική Αγωγή2": {"καθηγητής": "Τρεχαλητούλα", "τμήματα": [2], "ώρες": 1},
}
times = [(d, s) for d in days for s in slots]

# Μεταβλητές
prob = LpProblem("School_Scheduling", LpMinimize)
x = LpVariable.dicts("x", ((t, subj, d, s) for t in [1, 2] for subj in subjects
                         if t in subjects[subj]["τμήματα"]
                         for (d, s) in times), cat='Binary')

# Αντικειμενική συνάρτηση
prob += 0

# Περιορισμοί
for t in [1, 2]:
    for subj in subjects:
        if t in subjects[subj]["τμήματα"]:
            prob += lpSum(x[t, subj, d, s] for (d, s) in times) == subjects[subj]["ώρες"]

for t in [1, 2]:
    for d, s in times:
        prob += lpSum(x[t, subj, d, s] for subj in subjects if t in subjects[subj]["τμήματα"]) <= 1

for t in [1, 2]:
    for subj in subjects:
        if t in subjects[subj]["τμήματα"]:
            for d in days:
                prob += lpSum(x[t, subj, d, s] for s in slots) <= 1

for (subj, info) in subjects.items():
    teacher = info["καθηγητής"]
    if teacher == "Λαθοπράξης":
        for s in ["08:00–10:00", "10:15–12:15"]:
            prob += x.get((2, subj, "Δευτέρα", s), 0) == 0
    if teacher == "Ινσουλίνα":
        for s in slots:
            prob += x.get((1, subj, "Τετάρτη", s), 0) == 0
            prob += x.get((2, subj, "Τετάρτη", s), 0) == 0

for subj in ["Φυσική Αγωγή1", "Φυσική Αγωγή2"]:
    for (d, s) in times:
        if not (d == "Πέμπτη" and s == "14:00–16:00"):
            prob += x.get((1 if "1" in subj else 2, subj, d, s), 0) == 0

for t in [1, 2]:
    for subj in subjects:
        if t in subjects[subj]["τμήματα"]:
            prob += x.get((t, subj, "Δευτέρα", "08:00–10:00"), 0) == 0

# Επίλυση
prob.solve()

# Δημιουργία πινάκων προγράμματος
def generate_schedule(t):
    schedule = pd.DataFrame(index=slots, columns=days)
    for (tt, subj, d, s), var in x.items():
        if tt == t and var.varValue == 1:
            schedule.loc[s, d] = subj.replace("1", "").replace("2", "")
    schedule.reset_index(inplace=True)
    schedule.rename(columns={"index": "Ώρα"}, inplace=True)
    return schedule

df1 = generate_schedule(1)
df2 = generate_schedule(2)

# Αποθήκευση Excel με δύο φύλλα
output_path = os.path.join(os.getcwd(), "programma_teliko_final_output.xlsx")
with pd.ExcelWriter(output_path, engine="xlsxwriter") as writer:
    df1.to_excel(writer, sheet_name="Τμήμα 1", index=False)
    df2.to_excel(writer, sheet_name="Τμήμα 2", index=False)

print("✅ Το πρόγραμμα αποθηκεύτηκε επιτυχώς στο:")
print(output_path)
