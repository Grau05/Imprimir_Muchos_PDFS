"""
Imprimir PDFs por lote (Windows)
Requiere SumatraPDF instalado (sumatrapdfreader.org) o junto a este script.
Opciones: impresora, color/blanco y negro, dúplex, papel, orientación,
escala, copias, rango de páginas y acceso a preferencias del driver
(donde se define la calidad de impresión).
"""
import os
import subprocess
import sys
import threading
import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)

COLOR = {"Predeterminado de la impresora": "", "A color": "color", "Blanco y negro": "monochrome"}
DUPLEX = {"Predeterminado de la impresora": "", "Una cara": "simplex",
          "Dos caras (borde largo)": "duplexlong", "Dos caras (borde corto)": "duplexshort"}
PAPEL = {"Predeterminado de la impresora": "", "Carta": "paper=letter",
         "Oficio": "paper=legal", "A4": "paper=a4"}
ORIENT = {"Automática": "", "Vertical": "portrait", "Horizontal": "landscape"}
ESCALA = {"Ajustar a la página": "fit", "Reducir si es grande": "shrink", "Tamaño real": "noscale"}


def buscar_sumatra():
    base = os.path.dirname(os.path.abspath(sys.argv[0]))
    candidatos = [
        os.path.join(base, "SumatraPDF.exe"),
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "SumatraPDF", "SumatraPDF.exe"),
        r"C:\Program Files\SumatraPDF\SumatraPDF.exe",
        r"C:\Program Files (x86)\SumatraPDF\SumatraPDF.exe",
    ]
    return next((c for c in candidatos if os.path.exists(c)), None)


def listar_impresoras():
    try:
        out = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "Get-Printer | Select-Object -ExpandProperty Name"],
            capture_output=True, text=True, creationflags=NO_WINDOW, timeout=20,
        ).stdout
        return [l.strip() for l in out.splitlines() if l.strip()]
    except Exception:
        return []


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Imprimir PDFs por lote")
        self.geometry("680x640")
        self.sumatra = buscar_sumatra()
        self.carpeta = tk.StringVar()
        self.impresora = tk.StringVar()
        self.copias = tk.IntVar(value=1)
        self.color = tk.StringVar(value="Predeterminado de la impresora")
        self.duplex = tk.StringVar(value="Predeterminado de la impresora")
        self.papel = tk.StringVar(value="Predeterminado de la impresora")
        self.orient = tk.StringVar(value="Automática")
        self.escala = tk.StringVar(value="Ajustar a la página")
        self.rango = tk.StringVar()
        self.incluir_sub = tk.BooleanVar(value=False)
        self.pdfs = []
        self.imprimiendo = False
        self.crear_ui()

    def combo(self, parent, texto, var, opciones, fila, col):
        ttk.Label(parent, text=texto).grid(row=fila, column=col, sticky="w", padx=5, pady=3)
        ttk.Combobox(parent, textvariable=var, values=list(opciones), state="readonly",
                     width=28).grid(row=fila, column=col + 1, sticky="w", padx=5, pady=3)

    def crear_ui(self):
        p = {"padx": 10, "pady": 4}
        f = ttk.Frame(self); f.pack(fill="x", **p)
        ttk.Entry(f, textvariable=self.carpeta).pack(side="left", fill="x", expand=True)
        ttk.Button(f, text="Carpeta…", command=self.elegir_carpeta).pack(side="left", padx=5)

        f = ttk.Frame(self); f.pack(fill="x", **p)
        ttk.Label(f, text="Impresora:").pack(side="left")
        impresoras = listar_impresoras()
        ttk.Combobox(f, textvariable=self.impresora, values=impresoras,
                     state="readonly").pack(side="left", fill="x", expand=True, padx=5)
        ttk.Button(f, text="Preferencias / calidad…",
                   command=self.abrir_preferencias).pack(side="left")
        if impresoras:
            hp = [i for i in impresoras if "hp" in i.lower()]
            self.impresora.set(hp[0] if hp else impresoras[0])

        g = ttk.LabelFrame(self, text="Opciones de impresión"); g.pack(fill="x", **p)
        self.combo(g, "Color:", self.color, COLOR, 0, 0)
        self.combo(g, "Dúplex:", self.duplex, DUPLEX, 0, 2)
        self.combo(g, "Papel:", self.papel, PAPEL, 1, 0)
        self.combo(g, "Orientación:", self.orient, ORIENT, 1, 2)
        self.combo(g, "Escala:", self.escala, ESCALA, 2, 0)
        ttk.Label(g, text="Copias:").grid(row=2, column=2, sticky="w", padx=5)
        ttk.Spinbox(g, from_=1, to=99, width=5, textvariable=self.copias).grid(
            row=2, column=3, sticky="w", padx=5)
        ttk.Label(g, text="Páginas (ej. 1-3,5):").grid(row=3, column=0, sticky="w", padx=5, pady=3)
        ttk.Entry(g, textvariable=self.rango, width=30).grid(row=3, column=1, sticky="w", padx=5)
        ttk.Checkbutton(g, text="Incluir subcarpetas", variable=self.incluir_sub,
                        command=self.cargar_pdfs).grid(row=3, column=2, columnspan=2, sticky="w", padx=5)

        self.lista = tk.Listbox(self, selectmode="extended")
        self.lista.pack(fill="both", expand=True, **p)

        self.estado = ttk.Label(self, text="Elige una carpeta con PDFs.")
        self.estado.pack(anchor="w", **p)
        self.barra = ttk.Progressbar(self, mode="determinate")
        self.barra.pack(fill="x", **p)

        f = ttk.Frame(self); f.pack(fill="x", **p)
        ttk.Button(f, text="Imprimir todos", command=lambda: self.imprimir(False)).pack(side="left")
        ttk.Button(f, text="Imprimir seleccionados",
                   command=lambda: self.imprimir(True)).pack(side="left", padx=5)

        if not self.sumatra:
            self.estado.config(text="No se encontró SumatraPDF. Instálalo desde sumatrapdfreader.org")

    def abrir_preferencias(self):
        if not self.impresora.get():
            return
        subprocess.Popen(["rundll32", "printui.dll,PrintUIEntry", "/e", "/n", self.impresora.get()])

    def elegir_carpeta(self):
        c = filedialog.askdirectory()
        if c:
            self.carpeta.set(c)
            self.cargar_pdfs()

    def cargar_pdfs(self):
        c = self.carpeta.get()
        if not c or not os.path.isdir(c):
            return
        self.pdfs = []
        if self.incluir_sub.get():
            for raiz, _, archivos in os.walk(c):
                self.pdfs += [os.path.join(raiz, a) for a in archivos if a.lower().endswith(".pdf")]
        else:
            self.pdfs = [os.path.join(c, a) for a in os.listdir(c) if a.lower().endswith(".pdf")]
        self.pdfs.sort()
        self.lista.delete(0, "end")
        for pdf in self.pdfs:
            self.lista.insert("end", os.path.relpath(pdf, c))
        self.estado.config(text=f"{len(self.pdfs)} PDF encontrados.")

    def ajustes(self):
        partes = [COLOR[self.color.get()], DUPLEX[self.duplex.get()], PAPEL[self.papel.get()],
                  ORIENT[self.orient.get()], ESCALA[self.escala.get()]]
        if self.copias.get() > 1:
            partes.append(f"{self.copias.get()}x")
        if self.rango.get().strip():
            partes.append(self.rango.get().strip().replace(" ", ""))
        return ",".join(x for x in partes if x)

    def imprimir(self, solo_sel):
        if self.imprimiendo:
            return
        if not self.sumatra:
            messagebox.showerror("Falta SumatraPDF",
                                 "Instala SumatraPDF desde sumatrapdfreader.org y vuelve a abrir el programa.")
            return
        if not self.impresora.get():
            messagebox.showerror("Impresora", "Elige una impresora.")
            return
        archivos = [self.pdfs[i] for i in self.lista.curselection()] if solo_sel else list(self.pdfs)
        if not archivos:
            messagebox.showinfo("Nada que imprimir", "No hay PDFs para imprimir.")
            return
        if not messagebox.askyesno("Confirmar", f"¿Imprimir {len(archivos)} archivo(s)?"):
            return
        self.imprimiendo = True
        self.barra.config(maximum=len(archivos), value=0)
        threading.Thread(target=self.trabajo, args=(archivos, self.ajustes()), daemon=True).start()

    def trabajo(self, archivos, ajustes):
        fallos = []
        for n, ruta in enumerate(archivos, 1):
            self.after(0, lambda n=n, r=ruta: self.estado.config(
                text=f"Imprimiendo {n}/{len(archivos)}: {os.path.basename(r)}"))
            cmd = [self.sumatra, "-print-to", self.impresora.get(), "-silent"]
            if ajustes:
                cmd += ["-print-settings", ajustes]
            cmd.append(ruta)
            try:
                r = subprocess.run(cmd, creationflags=NO_WINDOW, timeout=180)
                if r.returncode != 0:
                    raise RuntimeError(f"código {r.returncode}")
            except Exception as e:
                fallos.append(f"{os.path.basename(ruta)}: {e}")
            self.after(0, lambda n=n: self.barra.config(value=n))
            time.sleep(1)
        self.after(0, lambda: self.terminar(len(archivos), fallos))

    def terminar(self, total, fallos):
        self.imprimiendo = False
        self.estado.config(text=f"Listo: {total - len(fallos)} enviados, {len(fallos)} con error.")
        if fallos:
            messagebox.showwarning("Algunos fallaron", "\n".join(fallos[:15]))
        else:
            messagebox.showinfo("Listo", "Todos los PDF se enviaron a la impresora.")


if __name__ == "__main__":
    App().mainloop()