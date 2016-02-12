from PIL import Image
import pytesseract

img = Image.open('./test.png')
test = pytesseract.image_to_string(img)
print(test)
