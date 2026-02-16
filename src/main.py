import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageDraw, ImageFont
import time
import os
import re

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class QueensSolver:
    def __init__(self, grid_warna):
        self.grid_warna = grid_warna
        self.n = len(grid_warna)
        self.solusi = None
        self.jumlah_percobaan = 0
        
    def generate_permutasi(self, elemen):
        if len(elemen) <= 1:
            yield elemen
        else:
            for permutasi in self.generate_permutasi(elemen[1:]):
                for i in range(len(elemen)):
                    yield permutasi[:i] + [elemen[0]] + permutasi[i:]
                    
    def cek_validasi(self, posisi_queens):
        self.jumlah_percobaan += 1
        warna_terpakai = []
        
        # Constraint Warna
        for baris in range(self.n):
            kolom = posisi_queens[baris]
            warna = self.grid_warna[baris][kolom]
            
            if warna in warna_terpakai:
                return False
            warna_terpakai.append(warna)
        
        # Constraint Neighbor
        for i in range(self.n):
            for j in range(i + 1, self.n):
                r1, c1 = i, posisi_queens[i]
                r2, c2 = j, posisi_queens[j]
                
                dr = abs(r1 - r2)
                dc = abs(c1 - c2)
                
                if dr <=1 and dc <= 1:
                    return False
                
        # Constraint Horizantal dan Vertikal
        for i in range(self.n):
            for j in range(i + 1, self.n):
                if posisi_queens[i] == posisi_queens[j]:
                    return False
                
        return True
                
    def cari_solusi(self):
        angka_kolom = list(range(self.n))
        generator = self.generate_permutasi(angka_kolom)
        
        for kemungkinan in generator:
            is_valid = self.cek_validasi(kemungkinan)
            if is_valid:
                yield kemungkinan, True, True
                return
            else:
                yield kemungkinan, False, False
                
        yield None, False, True
        
class QueensApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Tucil 1 IF2211 - Queens Linkedin Solver")
        self.geometry("900x600")
        
        self.grid_data = []
        self.tombol_grid = {}
        self.solver = None
        self.generator_solusi = None
        self.start_time = 0
        self.is_running = False
        self.input_filename = None
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)    
        self.setup_sidebar()
        self.setup_board_area()
        
    def setup_sidebar(self):
        frame_kiri = ctk.CTkFrame(self, width=200, corner_radius=0)
        frame_kiri.grid(row=0, column=0, sticky="nsew")
        
        label_judul = ctk.CTkLabel(frame_kiri, text="Queens Linkedin Solver\nBrute Force", font=("Roboto Medium", 20))
        label_judul.pack(pady=20, padx=5)
        
        self.btn_load = ctk.CTkButton(frame_kiri, text="Pilih File .txt", command=self.load_file, font=("Roboto", 16))
        self.btn_load.pack(pady=10, padx=20)
        self.btn_start = ctk.CTkButton(frame_kiri, text="Mulai Cari Solusi", command=self.start_solusi, state="disabled", font=("Roboto", 16))
        self.btn_start.pack(pady=10, padx=20)
        self.label_status = ctk.CTkLabel(frame_kiri, text="Menunggu file", font=("Roboto", 14))
        self.label_status.pack(pady=(20, 5))
        self.label_iterasi = ctk.CTkLabel(frame_kiri, text="Iterasi: 0", font=("Roboto", 14))
        self.label_iterasi.pack(pady=5)
        self.label_waktu = ctk.CTkLabel(frame_kiri, text="Waktu: 0 ms", font=("Roboto", 14))
        self.label_waktu.pack(pady=5)
        
    def setup_board_area(self):
        self.frame_kanan = ctk.CTkFrame(self)
        self.frame_kanan.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if not file_path:
            return
        
        self.input_filename = os.path.basename(file_path)
        
        with open(file_path, 'r') as f:
            lines = f.readlines()
            
        self.grid_data = [list(line.strip()) for line in lines if line.strip()]
        self.n = len(self.grid_data)
        
        for line in self.grid_data:
            if len(line) != self.n:
                messagebox.showerror("Error", "File tidak valid: Grid harus persegi (NxN).")
                return
            
        self.gambar_papan()
        self.label_status.configure(text=f"File berhasil dimuat ({self.n}x{self.n})")
        self.btn_start.configure(state="normal")

            
    def get_warna_region(self, huruf):
        warna_map = {
            'A': '#FFB5BA',
            'B': '#B5F0D5',
            'C': '#A8D8FF',
            'D': '#FFED99',
            'E': '#D9B3FF',
            'F': '#FFB380',
            'G': '#B8E994',
            'H': '#87E0D9',
            'I': '#FFA8CC',
            'J': '#C2A3FF',
            'K': '#FFDAA8',
            'L': '#FF9999',
            'M': '#99E6D9',
            'N': '#B3D9FF',
            'O': '#FFE5B4',
            'P': '#E6B3D6',
            'Q': '#D4FF99',
            'R': '#FFC2E0',
            'S': '#FFFAAA',
            'T': '#FFCC99',
            'U': '#C4E6E6',
            'V': '#D9D9D9',
            'W': '#A8E6CF',
            'X': '#B3B3FF',
            'Y': '#F5C2F5',
            'Z': '#99FFEB',
        }
        return warna_map.get(huruf.upper(), '#E8E8E8')

    def gambar_papan(self):
        for widget in self.frame_kanan.winfo_children():
            widget.destroy()
            
        self.tombol_grid = {}
        
        for i in range(self.n):
            self.frame_kanan.grid_rowconfigure(i, weight=1)
            self.frame_kanan.grid_columnconfigure(i, weight=1)
            
        for r in range(self.n):
            for c in range(self.n):
                huruf_region = self.grid_data[r][c]
                warna_bg = self.get_warna_region(huruf_region)
                
                kotak = ctk.CTkButton(self.frame_kanan, text=huruf_region, fg_color=warna_bg, text_color=warna_bg, hover=False, corner_radius=0, font=("Arial", 24, "bold"), border_width=0.5, border_color="black")
                kotak.grid(row=r, column=c, sticky="nsew")
                self.tombol_grid[(r, c)] = kotak
                
    def start_solusi(self):
        if not self.grid_data:
            return 
        
        self.solver = QueensSolver(self.grid_data)
        self.generator_solusi = self.solver.cari_solusi()
        
        self.is_running = True
        self.start_time = time.time()
        self.btn_start.configure(state="disabled")
        self.btn_load.configure(state="disabled")
        self.label_status.configure(text="Mencari solusi..", text_color="#75BAFE")
        
        self.update_logika()
        
    def update_logika(self):
        if not self.is_running:
            return
        
        try:
            steps_per_frame = 100
            data_terakhir = None
            found = False
            finished = False
            
            for _ in range(steps_per_frame):
                data_terakhir, found, finished = next(self.generator_solusi)
                if finished:
                    break
            
            waktu_berjalan = (time.time() - self.start_time) * 1000
            self.label_iterasi.configure(text=f"Iterasi: {self.solver.jumlah_percobaan}")
            self.label_waktu.configure(text=f"Waktu: {waktu_berjalan:.2f} ms")
            
            if data_terakhir:
                self.visualisasi_queens(data_terakhir)
                
            if finished:
                self.is_running = False
                self.btn_load.configure(state="normal")
                self.btn_start.configure(state="normal")
                
                if found:
                    self.label_status.configure(text="Solusi ditemukan!", text_color="green")
                    messagebox.showinfo("Sukses", f"Solusi ditemukan dalam {self.solver.jumlah_percobaan} iterasi dan {waktu_berjalan:.2f} ms.")
                    
                    simpan = messagebox.askyesno("Simpan Solusi", "Apakah Anda ingin menyimpan solusi?")
                    if simpan:
                        self.simpan_solusi(data_terakhir, waktu_berjalan)
                else:
                    self.label_status.configure(text="Tidak ada solusi.", text_color="red")
                    messagebox.showinfo("Info", "Algoritma selesai, tidak ada solusi valid.")
            else:
                self.after(1, self.update_logika)
                
        except StopIteration:
            pass
    
    def simpan_solusi(self, posisi_queens, waktu_ms):
        test_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "test")
        os.makedirs(test_folder, exist_ok=True)
        
        nomor = "1" 
        if self.input_filename:
            nums = re.findall(r'\d+', self.input_filename)
            if nums:
                nomor = nums[0]
        
        filepath_txt = os.path.join(test_folder, f"output{nomor}.txt")
        
        with open(filepath_txt, 'w') as f:
            for r in range(self.n):
                for c in range(self.n):
                    ada_queen = (c == posisi_queens[r])
                    if ada_queen:
                        f.write("#")
                    else:
                        huruf = self.grid_data[r][c]
                        f.write(huruf)
                f.write("\n")
            
        self.simpan_solusi_gambar(posisi_queens, nomor)
        
        messagebox.showinfo("Sukses", f"Solusi berhasil disimpan:\n- {filepath_txt}\n- {os.path.join(test_folder, f'output{nomor}.png')}")
            
    def simpan_solusi_gambar(self, posisi_final, nomor):
        if not posisi_final:
            return

        test_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "test")
        os.makedirs(test_folder, exist_ok=True)
        
        cell_size = 100
        img_size = self.n * cell_size
        
        image = Image.new("RGB", (img_size, img_size), "white")
        draw = ImageDraw.Draw(image)
        font_queen = ImageFont.truetype("seguisym.ttf", size=int(cell_size * 0.6))

        for r in range(self.n):
            for c in range(self.n):
                x0 = c * cell_size
                y0 = r * cell_size
                x1 = x0 + cell_size
                y1 = y0 + cell_size
                
                huruf = self.grid_data[r][c]
                warna_hex = self.get_warna_region(huruf)
                
                draw.rectangle([x0, y0, x1, y1], fill=warna_hex, outline="black", width=1)

                if posisi_final[r] == c:
                    center_x = x0 + (cell_size / 2)
                    center_y = y0 + (cell_size / 2)
                    draw.text((center_x, center_y), "♛", fill="black", font=font_queen, anchor="mm")

        filepath = os.path.join(test_folder, f"output{nomor}.png")
        image.save(filepath)
    
    def visualisasi_queens(self, posisi_queens):
        for (r, c), tombol in self.tombol_grid.items():
            tombol.configure(text="")
        
        for r, c in enumerate(posisi_queens):
            tombol = self.tombol_grid[(r, c)]
            tombol.configure(text="♛", text_color="black", font=("Segoe UI Symbol", 36, "bold"))
            
if __name__ == "__main__":
    app = QueensApp()
    app.mainloop()