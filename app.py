import tkinter as tk
from tkinter import ttk, messagebox
import db
import sqlite3
from datetime import datetime

db.init_db()


# ---------- DB FUNKCE ----------

def add_sportoviste(nazev, typ, kapacita):
    conn = db.connect()
    cur = conn.cursor()
    cur.execute("INSERT INTO sportoviste VALUES (NULL, ?, ?, ?)",
                (nazev, typ, kapacita))
    conn.commit()
    conn.close()


def get_sportoviste():
    conn = db.connect()
    cur = conn.cursor()
    cur.execute("SELECT id, nazev FROM sportoviste")
    data = cur.fetchall()
    conn.close()
    return data


def check_collision(datum, od, do, sportoviste_id):
    conn = db.connect()
    cur = conn.cursor()

    cur.execute("""
    SELECT * FROM rezervace
    WHERE datum=? AND sportoviste_id=?
    AND NOT (cas_do <= ? OR cas_od >= ?)
    """, (datum, sportoviste_id, od, do))

    kolize = cur.fetchone()
    conn.close()
    return kolize is not None


def add_rezervace(datum, od, do, sportoviste_id):
    if check_collision(datum, od, do, sportoviste_id):
        messagebox.showerror("Chyba", "Kolize rezervace!")
        return

    conn = db.connect()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO rezervace VALUES (NULL, ?, ?, ?, ?)
    """, (datum, od, do, sportoviste_id))
    conn.commit()
    conn.close()
    load_today()


def delete_rezervace(rid):
    conn = db.connect()
    cur = conn.cursor()
    cur.execute("DELETE FROM rezervace WHERE id=?", (rid,))
    conn.commit()
    conn.close()
    load_today()


# ---------- GUI ----------

root = tk.Tk()
root.title("Správa sportoviště")
root.geometry("900x600")

# ---- Sportoviště frame ----

frame_s = ttk.LabelFrame(root, text="Přidat sportoviště")
frame_s.pack(fill="x", padx=10, pady=5)

tk.Label(frame_s, text="Název").grid(row=0, column=0)
tk.Label(frame_s, text="Typ").grid(row=0, column=2)
tk.Label(frame_s, text="Kapacita").grid(row=0, column=4)

nazev_e = tk.Entry(frame_s)
typ_e = tk.Entry(frame_s)
kap_e = tk.Entry(frame_s)

nazev_e.grid(row=0, column=1)
typ_e.grid(row=0, column=3)
kap_e.grid(row=0, column=5)


def gui_add_sport():
    if not kap_e.get().isdigit():
        messagebox.showerror("Chyba", "Kapacita musí být číslo")
        return
    add_sportoviste(nazev_e.get(), typ_e.get(), int(kap_e.get()))
    messagebox.showinfo("OK", "Sportoviště přidáno")


tk.Button(frame_s, text="Přidat", command=gui_add_sport).grid(row=0, column=6)

# ---- Rezervace frame ----

frame_r = ttk.LabelFrame(root, text="Nová rezervace")
frame_r.pack(fill="x", padx=10, pady=5)

tk.Label(frame_r, text="Datum YYYY-MM-DD").grid(row=0, column=0)
tk.Label(frame_r, text="Od HH:MM").grid(row=0, column=2)
tk.Label(frame_r, text="Do HH:MM").grid(row=0, column=4)

datum_e = tk.Entry(frame_r)
od_e = tk.Entry(frame_r)
do_e = tk.Entry(frame_r)

datum_e.grid(row=0, column=1)
od_e.grid(row=0, column=3)
do_e.grid(row=0, column=5)

sport_combo = ttk.Combobox(frame_r)
sport_combo.grid(row=0, column=6)


def refresh_combo():
    data = get_sportoviste()
    sport_combo["values"] = [f"{i} - {n}" for i, n in data]


refresh_combo()


def gui_add_rez():
    try:
        datetime.strptime(datum_e.get(), "%Y-%m-%d")
        datetime.strptime(od_e.get(), "%H:%M")
        datetime.strptime(do_e.get(), "%H:%M")
    except:
        messagebox.showerror("Chyba", "Špatný formát data/času")
        return

    if not sport_combo.get():
        return

    sid = sport_combo.get().split(" - ")[0]
    add_rezervace(datum_e.get(), od_e.get(), do_e.get(), sid)


tk.Button(frame_r, text="Rezervovat", command=gui_add_rez).grid(row=0, column=7)

# ---- Treeview denní přehled ----

frame_t = ttk.LabelFrame(root, text="Denní přehled")
frame_t.pack(fill="both", expand=True, padx=10, pady=5)

tree = ttk.Treeview(frame_t, columns=("id", "datum", "od", "do", "sport"), show="headings")
for c in ("id", "datum", "od", "do", "sport"):
    tree.heading(c, text=c)

tree.pack(fill="both", expand=True)


def load_today():
    today = datetime.now().strftime("%Y-%m-%d")

    conn = db.connect()
    cur = conn.cursor()
    cur.execute("""
    SELECT r.id, r.datum, r.cas_od, r.cas_do, s.nazev
    FROM rezervace r
    JOIN sportoviste s ON s.id = r.sportoviste_id
    WHERE datum=?
    """, (today,))

    for row in tree.get_children():
        tree.delete(row)

    for row in cur.fetchall():
        tree.insert("", "end", values=row)

    conn.close()


load_today()


def delete_selected():
    sel = tree.selection()
    if not sel:
        return
    rid = tree.item(sel[0])["values"][0]
    delete_rezervace(rid)


tk.Button(root, text="Smazat rezervaci", command=delete_selected).pack(pady=5)

root.mainloop()
