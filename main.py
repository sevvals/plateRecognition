from ultralytics import YOLO
import pytesseract
import cv2
from PIL import Image, ImageTk
import tkinter as tk

class Arayuz:
    def __init__(self, master):
        self.master = master
        master.title("Plaka Okuma Uygulaması")

        self.upper_frame = tk.Frame(master, width=900, height=700)
        self.upper_frame.pack(fill=tk.BOTH, expand=True)

        self.video_label = tk.Label(self.upper_frame, width=800, height=500)
        self.video_label.pack(side=tk.LEFT)

        self.right_frame = tk.Frame(master)
        self.right_frame.pack(side=tk.LEFT, padx=20)

        self.search_frame = tk.LabelFrame(self.right_frame, text="Arama", padx=10, pady=10)
        self.search_frame.pack(pady=10)

        self.search_entry = tk.Entry(self.search_frame, width=20)
        self.search_entry.pack()

        self.search_entry.bind('<Return>', self.arama)

        self.sonuc_label = tk.Label(self.right_frame, text="", padx=10, pady=10)
        self.sonuc_label.pack()

        self.plaka_label = tk.Label(self.right_frame, text="Plaka Listesi", padx=10, pady=10)
        self.plaka_label.pack()

        self.plaka_listesi = tk.Listbox(self.right_frame, width=30, height=15)
        self.plaka_listesi.pack()

        self.boşluk_frame = tk.Frame(self.right_frame, height=50)
        self.boşluk_frame.pack()

        self.plate_list = []
        self.plate_timestamps = []
        self.oynat()


    def oynat(self):
        model = YOLO('best.pt')

        #Tesseract OCR
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'

        cap = cv2.VideoCapture(r'C:\Users\PC\PycharmProjects\pythonProject9\VIDEO-2023-06-20-20-23-19_Trim_Trim.mp4')

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

                            #ocr
                            crop_img_text = pytesseract.image_to_string(blur, lang='eng')
                            crop_img_text = crop_img_text.strip()

                            #plaka kontrol
                            if len(crop_img_text.replace(" ", "")) >= 7 and len(crop_img_text.replace(" ", "")) <= 8:
                                if crop_img_text.isalnum() or " " in crop_img_text:

                                    if crop_img_text not in self.plate_list:
                                        self.plate_list.append(crop_img_text)
                                        self.plate_timestamps.append(cap.get(cv2.CAP_PROP_POS_MSEC) / 1000)

                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame)
                img = img.resize((640, 480), Image.ANTIALIAS)
                imgtk = ImageTk.PhotoImage(image=img)
                self.video_label.configure(image=imgtk)
                self.video_label.image = imgtk

                #listeyi güncelle
                self.plaka_listesi.delete(0, tk.END)
                for plaka in self.plate_list:
                    self.plaka_listesi.insert(tk.END, plaka)

                self.master.after(1, video_goster)

        video_goster()

    def arama(self, event):
        aranan_plaka = self.search_entry.get()
        if aranan_plaka:
            self.plaka_listesi.selection_clear(0, tk.END)

            for i in range(self.plaka_listesi.size()):
                plaka = self.plaka_listesi.get(i)
                if plaka.lower() == aranan_plaka.lower():
                    self.plaka_listesi.selection_set(i)  #aranan plakayı seç
                    timestamp = self.plate_timestamps[i] if i < len(self.plate_timestamps) else ""
                    self.sonuc_label.config(text=f"Aranan plaka: {plaka} - Okunduğu dakika: {timestamp}")
                    break
            else:
                self.sonuc_label.config(text="Plaka bulunamadı")


root = tk.Tk()
arayuz = Arayuz(root)
root.mainloop()
