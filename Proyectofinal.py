import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from tkcalendar import Calendar
from datetime import datetime
import os

class Cita:
    def _init_(self, fecha, nombre, telefono, motivo):
        self.fecha = fecha
        self.nombre = nombre
        self.telefono = telefono
        self.motivo = motivo

    def _str_(self):
        return f"Fecha: {self.fecha}, Nombre: {self.nombre}, Teléfono: {self.telefono}, Motivo: {self.motivo}"

class CitaManager:
    def _init_(self):
        self.citas = {}

    def cargar_citas(self, fecha):
        filename = f"{fecha.strftime('%d-%m-%Y')}.txt"  
        if os.path.exists(filename):
            with open(filename, 'r') as file:
                lines = file.readlines()
                self.citas[fecha] = [Cita(*line.strip().split(',')) for line in lines]
        else:
            self.citas[fecha] = []

    def guardar_citas(self, fecha):
        filename = f"{fecha.strftime('%d-%m-%Y')}.txt"
        with open(filename, 'w') as file:
            for cita in self.citas.get(fecha, []):
                file.write(f"{cita.fecha},{cita.nombre},{cita.telefono},{cita.motivo}\n")

    def agregar_cita(self, cita):
        fecha = cita.fecha
        if fecha not in self.citas:
            self.citas[fecha] = []

        self.citas[fecha].append(cita)

    def editar_cita(self, fecha, indice, nueva_cita):
        if fecha in self.citas and 0 <= indice < len(self.citas[fecha]):
            self.citas[fecha][indice] = nueva_cita
            return True
        return False

    def eliminar_cita(self, fecha, indice):
        if fecha in self.citas and 0 <= indice < len(self.citas[fecha]):
            del self.citas[fecha][indice]
            return True
        return False

class CitaGUI(ttk.Frame):
    def _init_(self, master, cita_manager):
        super()._init_(master)
        self.master = master
        self.cita_manager = cita_manager
        self.current_date = None

        self.calendar = Calendar(self, font="Arial 14", selectmode="day", date_pattern="dd/MM/yyyy")
        self.calendar.pack(padx=20, pady=20)

        self.nombre_label = ttk.Label(self, text="Nombre y Apellido:")
        self.nombre_label.pack(pady=(10,0), padx=20, anchor='w')

        self.nombre_entry = ttk.Entry(self)
        self.nombre_entry.pack(pady=0, padx=20)

        self.telefono_label = ttk.Label(self, text="Número telefónico:")
        self.telefono_label.pack(pady=(10,0), padx=20, anchor='w')

        self.telefono_entry = ttk.Entry(self)
        self.telefono_entry.pack(pady=0, padx=20)

        self.motivo_label = ttk.Label(self, text="Motivo de su cita:")
        self.motivo_label.pack(pady=(10,0), padx=20, anchor='w')

        self.motivo_entry = ttk.Entry(self)
        self.motivo_entry.pack(pady=(0,20), padx=20)

        self.guardar_button = ttk.Button(self, text="Guardar Cita", command=self.guardar_cita)
        self.guardar_button.pack(pady=(0,20))

        self.visualizar_button = ttk.Button(self, text="Visualizar Citas", command=self.visualizar_citas)
        self.visualizar_button.pack(pady=10)

        self.calendar.bind("<<CalendarSelected>>", self.seleccionar_fecha)

    def seleccionar_fecha(self, event):
        self.current_date = self.calendar.get_date()

    def guardar_cita(self):
        if self.current_date is None:
            messagebox.showerror("Error", "Selecciona una fecha primero.")
            return

        fecha = datetime.strptime(self.current_date, "%d/%m/%Y").date()
        nombre = self.nombre_entry.get()
        telefono = self.telefono_entry.get()
        motivo = self.motivo_entry.get()

        if nombre and telefono and motivo:
            cita = Cita(fecha, nombre, telefono, motivo)
            self.cita_manager.agregar_cita(cita)
            self.cita_manager.guardar_citas(fecha)
            messagebox.showinfo("Éxito", "Cita guardada con éxito.")
        else:
            messagebox.showerror("Error", "Completa todos los campos.")

    def visualizar_citas(self):
        if self.current_date is None:
            messagebox.showerror("Error", "Selecciona una fecha primero.")
            return

        fecha = datetime.strptime(self.current_date, "%d/%m/%Y").date()
        if fecha in self.cita_manager.citas:
            citas = self.cita_manager.citas[fecha]

            visualizar_gui = VisualizarCitasGUI(self.master, citas, fecha, self.cita_manager, self.actualizar)
        else:
            messagebox.showinfo("Citas", "No hay citas para esta fecha.")

    def actualizar(self):
        self.visualizar_citas()

class VisualizarCitasGUI(tk.Toplevel):
    def _init_(self, master, citas, fecha, cita_manager, callback):
        super()._init_(master)
        self.title("Visualizar Citas")
        self.citas = citas
        self.fecha = fecha
        self.cita_manager = cita_manager
        self.checkboxes = []
        self.callback = callback

        self.visualizar()

        editar_button = ttk.Button(self, text="Editar Citas", command=self.editar_citas)
        editar_button.pack(pady=(10,0))

        eliminar_button = ttk.Button(self, text="Eliminar Citas", command=self.eliminar_citas)
        eliminar_button.pack()

    def visualizar(self):
        for widget in self.winfo_children():
            widget.destroy()

        for i, cita in enumerate(self.citas):
            var = tk.BooleanVar(self, value=False)
            self.checkboxes.append(var)
            cita_str = f"{i+1} - {cita}"
            checkbox = ttk.Checkbutton(self, text=cita_str, variable=var)
            checkbox.pack(anchor='w')

    def editar_citas(self):
        for i, var in enumerate(self.checkboxes):
            if var.get():
                cita = self.citas[i]
                editar_gui = EditarCitaGUI(self.master, cita, self.fecha, i, self.cita_manager, self.callback)

    def eliminar_citas(self):
        citas_seleccionadas = [i for i, var in enumerate(self.checkboxes) if var.get()]
        citas_seleccionadas.reverse()  
        for i in citas_seleccionadas:
            self.cita_manager.eliminar_cita(self.fecha, i)
            self.cita_manager.guardar_citas(self.fecha)
            messagebox.showinfo("Éxito", "Cita(s) eliminada(s) con éxito.")
        self.callback()

class EditarCitaGUI(tk.Toplevel):
    def _init_(self, master, cita, fecha, indice, cita_manager, callback):
        super()._init_(master)
        self.title("Editar Cita")
        self.cita = cita
        self.fecha = fecha
        self.indice = indice
        self.cita_manager = cita_manager
        self.callback = callback

        self.fecha_label = ttk.Label(self, text="Fecha (dd/mm/yyyy):")
        self.fecha_label.pack(pady=(10,0), padx=20, anchor='w')

        self.fecha_entry = ttk.Entry(self)
        self.fecha_entry.insert(0, cita.fecha.strftime("%d/%m/%Y"))
        self.fecha_entry.pack(pady=0, padx=20)

        self.nombre_label = ttk.Label(self, text="Nombre y Apellido:")
        self.nombre_label.pack(pady=(10,0), padx=20, anchor='w')

        self.nombre_entry = ttk.Entry(self)
        self.nombre_entry.insert(0, cita.nombre)
        self.nombre_entry.pack(pady=0, padx=20)

        self.telefono_label = ttk.Label(self, text="Número telefónico:")
        self.telefono_label.pack(pady=(10,0), padx=20, anchor='w')

        self.telefono_entry = ttk.Entry(self)
        self.telefono_entry.insert(0, cita.telefono)
        self.telefono_entry.pack(pady=0, padx=20)

        self.motivo_label = ttk.Label(self, text="Motivo de su cita:")
        self.motivo_label.pack(pady=(10,0), padx=20, anchor='w')

        self.motivo_entry = ttk.Entry(self)
        self.motivo_entry.insert(0, cita.motivo)
        self.motivo_entry.pack(pady=(0,20), padx=20)

        self.guardar_button = ttk.Button(self, text="Guardar Cambios", command=self.guardar_cambios)
        self.guardar_button.pack(pady=(0,20))

    def guardar_cambios(self):
        fecha = self.fecha_entry.get()
        nombre = self.nombre_entry.get()
        telefono = self.telefono_entry.get()
        motivo = self.motivo_entry.get()

        try:
            fecha = datetime.strptime(fecha, "%d/%m/%Y").date()
        except ValueError:
            messagebox.showerror("Error", "Formato de fecha incorrecto (dd/mm/yyyy).")
            return

        if nombre and telefono and motivo:
            nueva_cita = Cita(fecha, nombre, telefono, motivo)
            if self.cita_manager.editar_cita(self.fecha, self.indice, nueva_cita):
                self.cita_manager.guardar_citas(fecha)
                messagebox.showinfo("Éxito", "Cambios guardados con éxito.")
                self.callback()
                self.destroy()
            else:
                messagebox.showerror("Error", "No se pudo editar la cita.")
        else:
            messagebox.showerror("Error", "Completa todos los campos.")

if _name_ == "_main_":
    root = tk.Tk()
    root.title("Registro de Citas Médicas")

    cita_manager = CitaManager()

    app = CitaGUI(root, cita_manager)
    app.pack()

    root.mainloop()
