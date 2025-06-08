
import tkinter as tk
from tkinter import ttk, messagebox
import random

class HammingSECDED:
    def __init__(self, data_bits):
        self.data_bits = data_bits

    def encode(self, data: str):
        m = list(map(int, data))
        m.reverse()
        r = 0
        while (2 ** r) < (len(m) + r + 1):
            r += 1
        total_bits = len(m) + r
        hamming = []
        j = 0
        for i in range(1, total_bits + 1):
            if i == 2 ** j:
                hamming.append(0)
                j += 1
            else:
                hamming.append(m.pop(0))
        for i in range(r):
            pos = 2 ** i
            val = 0
            for j in range(1, total_bits + 1):
                if j & pos and j != pos:
                    val ^= hamming[j - 1]
            hamming[pos - 1] = val
        overall_parity = sum(hamming) % 2
        hamming.reverse()
        hamming.append(overall_parity)
        return ''.join(map(str, hamming))

    def detect_and_correct(self, encoded: str):
        bits = list(map(int, encoded))
        bits.reverse()
        r = 0
        while (2 ** r) < (len(bits) - r):
            r += 1
        total_bits = len(bits) - 1
        syndrome = 0
        for i in range(r):
            pos = 2 ** i
            val = 0
            for j in range(1, total_bits + 1):
                if j & pos:
                    val ^= bits[j - 1]
            if val:
                syndrome += pos
        overall_parity = sum(bits[:-1]) % 2
        if syndrome == 0 and overall_parity == bits[-1]:
            return ''.join(map(str, bits[::-1])), "Hata yok", -1
        elif syndrome != 0 and overall_parity != bits[-1]:
            bits[syndrome - 1] ^= 1
            return ''.join(map(str, bits[::-1])), f"{syndrome}. bit düzeltildi", syndrome - 1
        elif syndrome == 0 and overall_parity != bits[-1]:
            return ''.join(map(str, bits[::-1])), "Çift hata tespit edildi (düzeltilemez)", -1
        else:
            return ''.join(map(str, bits[::-1])), "Kod çözümlenemedi", -1

    def inject_error(self, encoded: str, bit_index: int):
        if 0 <= bit_index < len(encoded):
            lst = list(encoded)
            lst[bit_index] = '1' if lst[bit_index] == '0' else '0'
            return ''.join(lst)
        return encoded

class HammingSimulatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🔐 Hamming SEC-DED Kodlayıcı")
        self.root.configure(bg="#f0f4f7")
        self.create_widgets()

    def create_widgets(self):
        style = ttk.Style()
        style.configure("TButton", font=("Arial", 10, "bold"), padding=6)
        style.configure("TLabel", font=("Arial", 10))

        header = tk.Label(self.root, text="🔧 Hamming SEC-DED Kod Simülatörü", bg="#3f51b5", fg="white", font=("Arial", 14, "bold"))
        header.pack(fill="x", pady=10)

        frame = ttk.Frame(self.root, padding=10)
        frame.pack()

        ttk.Label(frame, text="Veri Uzunluğu (bit):").grid(column=0, row=0, sticky="w")
        self.bit_length = ttk.Combobox(frame, values=["8", "16", "32"], state="readonly")
        self.bit_length.grid(column=1, row=0)
        self.bit_length.set("8")

        ttk.Label(frame, text="Veri (binary):").grid(column=0, row=1, sticky="w")
        self.data_entry = ttk.Entry(frame, width=40)
        self.data_entry.grid(column=1, row=1)

        ttk.Label(frame, text="Hata oluşturulacak bit numarası:").grid(column=0, row=2, sticky="w")
        self.error_index_entry = ttk.Entry(frame, width=10)
        self.error_index_entry.grid(column=1, row=2)

        ttk.Button(frame, text="Kodla", command=self.encode_data).grid(column=0, row=3, pady=5)
        ttk.Button(frame, text="Hata Ekle", command=self.add_error).grid(column=1, row=3, pady=5)
        ttk.Button(frame, text="Düzelt", command=self.correct_data).grid(column=2, row=3, pady=5)
        ttk.Button(frame, text="Yardım", command=self.show_help).grid(column=3, row=3, pady=5)

        self.output = tk.Text(frame, width=75, height=10)
        self.output.grid(column=0, row=4, columnspan=4, pady=5)

        self.canvas = tk.Canvas(frame, width=750, height=120, bg="white")
        self.canvas.grid(column=0, row=5, columnspan=4, pady=10)

        self.info = tk.Label(frame, text="Veriyi girin, kodlayın, ardından hata ekleyip düzeltmeyi deneyin.", foreground="gray")
        self.info.grid(column=0, row=6, columnspan=4, pady=5)

        self.encoded = ""
        self.last_error_bit = -1

    def draw_bits(self, bits: str, title: str, highlight_index=-1):
        self.canvas.delete("all")
        self.canvas.create_text(10, 10, anchor="nw", text=title, font=("Arial", 10, "bold"))
        box_size = 20
        spacing = 5
        start_x = 10
        start_y = 30

        for i, bit in enumerate(bits):
            x = start_x + (box_size + spacing) * (i % 32)
            y = start_y + (box_size + spacing) * (i // 32)
            color = "green" if bit == "0" else "red"
            #if i == highlight_index:
             #   color = "orange"
            pos_from_right = len(bits) - 1 - i
            is_parity = (pos_from_right & (pos_from_right - 1)) == 0 
            if i == len(bits) - 1:
                label = "P"
                   
            elif is_parity:
                label = "P"
            else:
                label = "D"
            self.canvas.create_text(x + box_size / 2, y + box_size + 10, text=label, font=("Arial", 8), fill="black")
            self.canvas.create_rectangle(x, y, x + box_size, y + box_size, fill=color)
            self.canvas.create_text(x + box_size / 2, y + box_size / 2, text=bit, fill="white")

        if highlight_index != -1:
            self.animate_flash(highlight_index, bits)

    def animate_flash(self, index, bits):
        def flash(count):
            if count == 0:
                return
            fill = "yellow" if count % 2 == 0 else "orange"
            box_size = 20
            spacing = 5
            x = 10 + (box_size + spacing) * (index % 32)
            y = 30 + (box_size + spacing) * (index // 32)
            self.canvas.create_rectangle(x, y, x + box_size, y + box_size, fill=fill)
            self.canvas.create_text(x + box_size / 2, y + box_size / 2, text=bits[index], fill="black")
            self.root.after(300, lambda: flash(count - 1))
        flash(6)

    def encode_data(self):
        bits = int(self.bit_length.get())
        data = self.data_entry.get().strip()
        if len(data) != bits or any(c not in '01' for c in data):
            messagebox.showerror("Hata", f"Lütfen {bits} bitlik bir binary veri giriniz.")
            return
        coder = HammingSECDED(bits)
        encoded = coder.encode(data)
        self.encoded = encoded
        self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, f"Hamming Kodlu Veri:\n{encoded}\n")
        self.draw_bits(encoded, "Kodlanmış Veri")

    def add_error(self):
        #if not self.encoded:
        #    messagebox.showwarning("Uyarı", "Önce veriyi kodlayınız.")
        #    return
        #bit = random.randint(0, len(self.encoded) - 1)
        try:
            bit = int(self.error_index_entry.get())  # Kullanıcının yazdığı bit numarası
        except ValueError:
            messagebox.showerror("Hata", "Lütfen geçerli bir bit numarası giriniz.")
            return

        if not (0 <= bit < len(self.encoded)):
            messagebox.showerror("Hata", f"Lütfen 0 ile {len(self.encoded) - 1} arasında bir değer giriniz.")
            return
        görünen_bit = len(self.encoded) - 1 - bit
        coder = HammingSECDED(int(self.bit_length.get()))
        self.encoded = coder.inject_error(self.encoded, görünen_bit)
        self.output.insert(tk.END, f"\n{bit}. bitten hata eklendi:\n{self.encoded}\n")
        #self.output.insert(tk.END, f"\n{bit}. bitten hata eklendi:\n{self.encoded}\n")
        self.draw_bits(self.encoded, "Hatalı Veri", highlight_index=görünen_bit)
        self.last_error_bit = bit

    def correct_data(self):
        if not self.encoded:
            messagebox.showwarning("Uyarı", "Önce veriyi kodlayınız.")
            return
        coder = HammingSECDED(int(self.bit_length.get()))
        corrected, info, error_bit = coder.detect_and_correct(self.encoded)
        if error_bit != -1:
            normal_index = len(self.encoded) - 1 - error_bit
            info = "düzeltildi"
        #if error_bit != -1:
        #    bit = len(self.encoded) - 1 - error_bit
            
        self.encoded = corrected    
        self.output.insert(tk.END, "\nHata Kontrolü:\n" + corrected + "\nSonuç: " + info + "\n")
        self.draw_bits(corrected, "Düzeltilmiş Veri", highlight_index=(len(corrected) - 1 - error_bit))
        #self.draw_bits(corrected, "Düzeltilmiş Veri", highlight_index=error_bit)
        

    def show_help(self):
        messagebox.showinfo("Yardım", "1. Bit uzunluğunu seçin (8, 16, 32).\n2. Binary veriyi girin.\n3. 'Kodla' ile Hamming kodunu üretin.\n4. 'Hata Ekle' ile istediğiniz bitte hata oluşturun.\n5. 'Düzelt' ile hatayı tespit edip düzeltin.\n\nNot: Görsel panelde bitler renkli olarak gösterilir.")

if __name__ == "__main__":
    root = tk.Tk()
    app = HammingSimulatorApp(root)
    root.mainloop()
