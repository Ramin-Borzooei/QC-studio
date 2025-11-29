import customtkinter as ctk
import tkinter as tk
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# تنظیمات ظاهری
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

# ============================================================
# 1. ENHANCED POCKET DATABASE (Mechanical + Chemical)
# ============================================================
INTERNAL_DB = {
    "AISI 4140 (1.7225)": {
        "mech": {"min_uts": 850, "min_yield": 650, "min_elong": 12},
        "chem": {"C": (0.38, 0.43), "Mn": (0.75, 1.00), "Cr": (0.80, 1.10), "Mo": (0.15, 0.25)}
    },
    "AISI 316 (1.4401)": {
        "mech": {"min_uts": 515, "min_yield": 205, "min_elong": 40},
        "chem": {"C": (0.0, 0.08), "Mn": (0.0, 2.00), "Cr": (16.0, 18.0), "Ni": (10.0, 14.0)}
    },
    "A105 Carbon Steel": {
        "mech": {"min_uts": 485, "min_yield": 250, "min_elong": 22},
        "chem": {"C": (0.0, 0.35), "Mn": (0.60, 1.05), "Si": (0.10, 0.35)}
    }
}

# ============================================================
# 2. SUB-VIEWS FOR LAB MODULE (زیر ماژول‌های آزمایشگاه)
# ============================================================

class TensileView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # Control Panel
        ctrl = ctk.CTkFrame(self)
        ctrl.pack(side="left", fill="y", padx=10, pady=10)
        
        ctk.CTkLabel(ctrl, text="⚙️ Tensile Settings", font=("Arial", 16, "bold")).pack(pady=10)
        self.entry_d = ctk.CTkEntry(ctrl, placeholder_text="Diameter (mm)")
        self.entry_d.pack(pady=5)
        self.entry_l0 = ctk.CTkEntry(ctrl, placeholder_text="Gauge Length (mm)")
        self.entry_l0.pack(pady=5)
        
        ctk.CTkButton(ctrl, text="Generate Demo Data", command=self.sim_data, fg_color="gray").pack(pady=10)
        ctk.CTkButton(ctrl, text="Calculate & Plot", command=self.plot_tensile).pack(pady=5)
        
        self.res_lbl = ctk.CTkLabel(ctrl, text="Results:\n---", justify="left")
        self.res_lbl.pack(pady=20, anchor="w", padx=5)

        # Plot Area
        self.plot_frame = ctk.CTkFrame(self)
        self.plot_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        self.df = None

    def sim_data(self):
        # تولید داده مصنوعی برای تست
        strain = np.linspace(0, 0.2, 100)
        stress = 800 * strain * (strain < 0.05) + (800 * 0.05 + 200 * (strain - 0.05)**0.5) * (strain >= 0.05)
        noise = np.random.normal(0, 5, 100)
        force = stress * (np.pi * (5)**2) + noise
        disp = strain * 50
        self.df = pd.DataFrame({'Force_N': force, 'Disp_mm': disp})
        self.res_lbl.configure(text="Data Loaded (Simulated) ✅")

    def plot_tensile(self):
        if self.df is None: self.sim_data()
        
        try:
            d = float(self.entry_d.get() or 10)
            l0 = float(self.entry_l0.get() or 50)
            area = np.pi * (d/2)**2
            
            stress = self.df['Force_N'] / area
            strain = (self.df['Disp_mm'] / l0) * 100
            
            uts = stress.max()
            elong = strain.max()
            
            self.res_lbl.configure(text=f"Results:\nUTS: {uts:.1f} MPa\nElongation: {elong:.1f} %")

            # Plotting
            for widget in self.plot_frame.winfo_children(): widget.destroy()
            
            fig = plt.Figure(figsize=(5, 4), dpi=100)
            ax = fig.add_subplot(111)
            ax.plot(strain, stress, color='#3B82F6', linewidth=2)
            ax.set_title("Stress-Strain Curve")
            ax.set_xlabel("Strain (%)")
            ax.set_ylabel("Stress (MPa)")
            ax.grid(True, linestyle='--', alpha=0.6)

            canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)

        except Exception as e:
             self.res_lbl.configure(text=f"Error: {e}")


class HardnessView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        ctk.CTkLabel(self, text="💎 Hardness Converter & Averaging", font=("Arial", 20, "bold")).pack(pady=20)
        
        input_frame = ctk.CTkFrame(self)
        input_frame.pack(pady=10)
        
        self.entry_vals = ctk.CTkEntry(input_frame, placeholder_text="e.g: 45, 46, 44.5 (HRC)", width=300)
        self.entry_vals.pack(side="left", padx=10)
        ctk.CTkButton(input_frame, text="Calculate", command=self.calc).pack(side="left")
        
        self.res_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.res_frame.pack(pady=20)
        
        self.lbl_avg = ctk.CTkLabel(self.res_frame, text="Average HRC: --", font=("Arial", 24))
        self.lbl_avg.pack(pady=10)
        self.lbl_conv = ctk.CTkLabel(self.res_frame, text="Approx HB: --", font=("Arial", 24), text_color="#F59E0B")
        self.lbl_conv.pack(pady=10)

    def calc(self):
        try:
            raw = self.entry_vals.get().split(',')
            vals = [float(x.strip()) for x in raw if x.strip()]
            if not vals: return
            
            avg = sum(vals) / len(vals)
            # فرمول تقریبی تبدیل HRC به HB (تجربی)
            hb = 10 * avg if avg < 20 else (12 * avg) - 50 # فقط یک فرمول نمایشی ساده
            
            self.lbl_avg.configure(text=f"Average HRC: {avg:.1f}")
            self.lbl_conv.configure(text=f"Approx HB: {int(hb)} (Estimated)")
        except:
            self.lbl_avg.configure(text="Error in input format")


class QuantometryView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        ctk.CTkLabel(self, text="🔬 Quantometry Compliance Check", font=("Arial", 20)).pack(pady=10)
        
        # Select Standard
        self.combo_std = ctk.CTkOptionMenu(self, values=list(INTERNAL_DB.keys()), command=self.update_fields)
        self.combo_std.pack(pady=10)
        
        # Dynamic Input Container
        self.fields_frame = ctk.CTkFrame(self)
        self.fields_frame.pack(pady=10, padx=20, fill="x")
        
        self.inputs = {}
        self.update_fields(self.combo_std.get())
        
        ctk.CTkButton(self, text="Check Compliance", command=self.check_comp, fg_color="#10B981").pack(pady=20)
        self.lbl_res = ctk.CTkLabel(self, text="", font=("Consolas", 16))
        self.lbl_res.pack()

    def update_fields(self, alloy_name):
        for w in self.fields_frame.winfo_children(): w.destroy()
        self.inputs = {}
        elements = INTERNAL_DB[alloy_name]["chem"]
        
        # ساخت گرید ورودی‌ها
        row = 0
        for idx, el in enumerate(elements):
            ctk.CTkLabel(self.fields_frame, text=f"{el} %:").grid(row=row, column=0, padx=10, pady=5)
            ent = ctk.CTkEntry(self.fields_frame, width=100)
            ent.grid(row=row, column=1, padx=10, pady=5)
            # نمایش رنج مجاز به عنوان راهنما
            rng = elements[el]
            ctk.CTkLabel(self.fields_frame, text=f"({rng[0]} - {rng[1]})", text_color="gray").grid(row=row, column=2, padx=5)
            
            self.inputs[el] = ent
            row += 1

    def check_comp(self):
        alloy = self.combo_std.get()
        limits = INTERNAL_DB[alloy]["chem"]
        report = []
        overall_pass = True
        
        for el, entry in self.inputs.items():
            try:
                val = float(entry.get())
                mn, mx = limits[el]
                if mn <= val <= mx:
                    report.append(f"{el}: {val} ✅")
                else:
                    report.append(f"{el}: {val} ❌ (Range: {mn}-{mx})")
                    overall_pass = False
            except:
                pass # Skip empty
        
        final_txt = "PASSED ✅" if overall_pass else "FAILED ❌"
        self.lbl_res.configure(text=f"Result: {final_txt}\n" + "\n".join(report))


class CorrosionView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        ctk.CTkLabel(self, text="⚡ Corrosion Analysis (Tafel Plot)", font=("Arial", 20)).pack(pady=10)
        
        btn = ctk.CTkButton(self, text="Plot Simulated Tafel Curve", command=self.plot_tafel)
        btn.pack(pady=10)
        
        self.plot_area = ctk.CTkFrame(self)
        self.plot_area.pack(fill="both", expand=True, padx=20, pady=10)

    def plot_tafel(self):
        # داده‌های شبیه‌سازی شده تافل
        current = np.logspace(-8, -2, 100)
        potential = 0.2 + 0.1 * np.log10(current) + 0.05 * np.log10(current)**2 # منحنی ساختگی
        
        for w in self.plot_area.winfo_children(): w.destroy()
        
        fig = plt.Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111)
        ax.semilogx(current, potential, 'r-', label='Tafel Curve')
        ax.set_xlabel("Current Density (A/cm²)")
        ax.set_ylabel("Potential (V vs SCE)")
        ax.set_title("Polarization Curve")
        ax.grid(True, which="both", alpha=0.4)
        ax.legend()
        
        canvas = FigureCanvasTkAgg(fig, master=self.plot_area)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

class CompressionView(ctk.CTkFrame):
     def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        ctk.CTkLabel(self, text="🔽 Compression Test Check", font=("Arial", 20)).pack(pady=40)
        ctk.CTkLabel(self, text="(Structure similar to Tensile - Ready for logic)", text_color="gray").pack()


# ============================================================
# 3. MAIN LAB CONTAINER (With Left Sidebar)
# ============================================================

class QCFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # --- Header ---
        header = ctk.CTkFrame(self, height=50, fg_color="#1F2937")
        header.pack(fill="x", side="top")
        ctk.CTkButton(header, text="🏠 Home", width=60, command=lambda: controller.show_frame("HomeFrame")).pack(side="left", padx=10, pady=5)
        ctk.CTkLabel(header, text="Lab & Material Center", font=("Arial", 18, "bold")).pack(side="left", padx=10)

        # --- Main Layout (Sidebar + Content) ---
        body = ctk.CTkFrame(self)
        body.pack(fill="both", expand=True)
        
        # Sidebar (Left Menu)
        self.sidebar = ctk.CTkFrame(body, width=200, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        
        # Content Area (Right)
        self.content_area = ctk.CTkFrame(body, fg_color="#2B2B2B") # Dark gray background for content
        self.content_area.pack(side="right", fill="both", expand=True)

        # Sidebar Buttons
        self.add_menu_item("🔗 Tensile Test", TensileView)
        self.add_menu_item("🔽 Compression", CompressionView)
        self.add_menu_item("💎 Hardness", HardnessView)
        self.add_menu_item("🔬 Quantometry", QuantometryView)
        self.add_menu_item("⚡ Corrosion Plots", CorrosionView)
        
        # Default View
        self.current_view = None
        self.show_view(TensileView)

    def add_menu_item(self, text, view_class):
        btn = ctk.CTkButton(self.sidebar, text=text, 
                            fg_color="transparent", hover_color="#4B5563", anchor="w", 
                            height=40,
                            command=lambda: self.show_view(view_class))
        btn.pack(fill="x", padx=5, pady=2)

    def show_view(self, view_class):
        if self.current_view:
            self.current_view.pack_forget()
        
        # Create new instance of the view
        self.current_view = view_class(self.content_area)
        self.current_view.pack(fill="both", expand=True, padx=10, pady=10)


# ============================================================
# OTHER FRAMES (Simplified for context)
# ============================================================
class HomeFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        # Logo Section
        ctk.CTkLabel(self, text="Materials QC Studio", font=("Impact", 60), text_color="#60A5FA").pack(pady=(60, 10))
        
        # Navigation Grid
        grid = ctk.CTkFrame(self, fg_color="transparent")
        grid.pack(expand=True)
        
        btn_config = {"width": 250, "height": 150, "font": ("Arial", 20, "bold"), "corner_radius": 15}
        
        ctk.CTkButton(grid, text="🧪 Lab Center", fg_color="#2cc985", **btn_config, 
                      command=lambda: controller.show_frame("QCFrame")).grid(row=0, column=0, padx=20, pady=20)
        
        ctk.CTkButton(grid, text="🔥 Risk (API 571)", fg_color="#F59E0B", **btn_config,
                      command=lambda: print("Risk Module")).grid(row=0, column=1, padx=20, pady=20)
        
        ctk.CTkButton(grid, text="🕵️ Diagnosis", fg_color="#3B82F6", **btn_config,
                      command=lambda: print("Diagnosis Module")).grid(row=1, column=0, padx=20, pady=20)


class MaterialsQCApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Materials QC Studio v3.0")
        self.geometry("1100x800")

        container = ctk.CTkFrame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (HomeFrame, QCFrame):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("HomeFrame")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

if __name__ == "__main__":
    app = MaterialsQCApp()
    app.mainloop()
