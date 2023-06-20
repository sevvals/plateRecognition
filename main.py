from ultralytics import YOLO
import pytesseract
import cv2

model = YOLO('best.pt')

#Tesseract OCR
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'

cap = cv2.VideoCapture(r'C:\Users\PC\Downloads\SharpVision-main\SharpVision-main\VIDEO-2023-06-20-20-23-19_Trim_Trim.mp4')

plate_list = []

while cap.isOpened():
    ret, frame = cap.read()

    if not ret:
        break

    results = model.predict(frame, show=True, stream=True)
    for r in results:
        boxes = r.boxes.xyxy

        if len(boxes) > 0:
            for box in boxes:
                x1, y1, x2, y2 = map(int, box)

                # Plaka bölgesini kesme
                cropped = frame[y1:y2, x1:x2]

                if cropped.shape[0] < 10 or cropped.shape[1] < 10:
                    continue

                gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)

                blur = cv2.GaussianBlur(gray, (3, 3), 0)
                # thresh = cv2.threshold(blur, 128, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

                crop_img_text = pytesseract.image_to_string(blur, lang='eng')
                crop_img_text = crop_img_text.strip()
                print("text:", crop_img_text)

                if len(crop_img_text.replace(" ", "")) >= 7 and len(crop_img_text.replace(" ", "")) <= 8:
                    # Aynı plakanın birden fazla kez eklenmesini engelleme
                    if crop_img_text not in plate_list:
                        plate_list.append(crop_img_text)

    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

plate_list = [plate for plate in plate_list if plate]

print("Plaka Listesi:", plate_list)
