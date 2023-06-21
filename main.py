from ultralytics import YOLO
import pytesseract
import cv2
from PIL import Image, ImageTk
import tkinter as tk
import re

class Arayuz:
    def __init__(self, master):
        self.master = master
        master.title("Plaka Okuma Uygulaması")
        master.geometry("1000x500")

        self.video_frame = tk.Frame(master, width=700, height=500)
        self.video_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.video_label = tk.Label(self.video_frame)
        self.video_label.pack()

        self.left_frame = tk.Frame(master, width=300, height=500)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.search_frame = tk.LabelFrame(self.left_frame, text="Arama", padx=10, pady=10)
        self.search_frame.pack(pady=10)

        self.search_entry = tk.Entry(self.search_frame, width=20)
        self.search_entry.pack()

        self.search_entry.bind('<Return>', self.arama)

        self.plaka_label = tk.Label(self.left_frame, text="Plaka Listesi", padx=10, pady=10)
        self.plaka_label.pack()

        self.sonuc_label = tk.Label(self.left_frame, text="", padx=10, pady=10, anchor='w')
        self.sonuc_label.pack()

        self.plaka_listesi_frame = tk.Frame(self.left_frame)
        self.plaka_listesi_frame.pack(fill=tk.BOTH, expand=True)

        self.scrollbar = tk.Scrollbar(self.plaka_listesi_frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.plaka_listesi = tk.Listbox(self.plaka_listesi_frame, width=30, height=15, yscrollcommand=self.scrollbar.set)
        self.plaka_listesi.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar.config(command=self.plaka_listesi.yview)

        self.plate_list = []
        self.plate_timestamps = []
        self.oynat()

    def oynat(self):
        model = YOLO('best.pt')

        #tesseract OCR
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'

        cap = cv2.VideoCapture(r'C:\Users\PC\PycharmProjects\pythonProject9\carsvideo.mp4')

        def video_goster():
            ret, frame = cap.read()

            if ret:
                results = model.predict(frame, show=False, stream=True)
                for r in results:
                    boxes = r.boxes.xyxy

                    if len(boxes) > 0:
                        for box in boxes:
                            x1, y1, x2, y2 = map(int, box)

                            cropped = frame[y1:y2, x1:x2]

                            if cropped.shape[0] < 10 or cropped.shape[1] < 10:
                                continue

                            gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)

                            blur = cv2.GaussianBlur(gray, (3, 3), 0)

                            _, thresh = cv2.threshold(blur, 127, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

                            crop_img_text = pytesseract.image_to_string(thresh, config='--psm 7')

                            crop_img_text = crop_img_text.strip()

                            #plaka kontrolu yap
                            clean_plaka = re.sub(r'[^a-zA-Z0-9]', '', crop_img_text)  #harf-rakam
                            if len(clean_plaka) >= 7 and len(clean_plaka) <= 8:
                                if clean_plaka.isalnum() and clean_plaka[0].isdigit():
                                    if clean_plaka not in self.plate_list:
                                        self.plate_list.append(clean_plaka)
                                        self.plate_timestamps.append(cap.get(cv2.CAP_PROP_POS_MSEC) / 1000)

                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame)
                img = img.resize((640, 480), Image.ANTIALIAS)
                imgtk = ImageTk.PhotoImage(image=img)
                self.video_label.configure(image=imgtk)
                self.video_label.image = imgtk

                #plaka listesi guncelle
                self.plaka_listesi.delete(0, tk.END)
                for plaka in self.plate_list:
                    if len(plaka) == 7:
                        formatted_plaka = f"{plaka[:2]} {plaka[2:4]} {plaka[4:]}"
                    elif len(plaka) == 8:
                        formatted_plaka = f"{plaka[:2]} {plaka[2:5]} {plaka[5:]}"
                    else:
                        formatted_plaka = plaka
                    self.plaka_listesi.insert(tk.END, formatted_plaka)

                if self.plaka_listesi.size() > 0:
                    self.plaka_listesi.select_set(0)
                    self.plaka_listesi.event_generate("<<ListboxSelect>>")

            self.master.after(1, video_goster)

        video_goster()

    def arama(self, event):
        aranan_plaka = self.search_entry.get()
        if aranan_plaka:
            self.plaka_listesi.selection_clear(0, tk.END)

            aranan_plaka = re.sub(r'[^a-zA-Z0-9]', '', aranan_plaka)

            for i in range(self.plaka_listesi.size()):
                plaka = re.sub(r'\s', '', self.plaka_listesi.get(i))  #bosluk
                if plaka.lower() == aranan_plaka.lower():
                    self.plaka_listesi.selection_set(i)
                    timestamp = self.plate_timestamps[i] if i < len(self.plate_timestamps) else ""
                    formatted_plaka = f"{plaka[:2]} {plaka[2:4]} {plaka[4:]}"  #plaka formatı
                    self.sonuc_label.config(text=f"{formatted_plaka} - Okunduğu dakika: {timestamp:.2f}")
                    self.sonuc_label.pack(after=self.plaka_label, anchor='w')
                    break
            else:
                self.sonuc_label.config(text="Plaka bulunamadı")


root = tk.Tk()
arayuz = Arayuz(root)
root.mainloop()
