from PIL import Image

# 1. เปิดไฟล์ภาพที่ต้องการแปลง
img = Image.open('755_0.jpg')

# 2. บันทึกเป็นไฟล์ใหม่ในนามสกุล .png
img.save('a.png', 'PNG')

print("แปลงไฟล์สำเร็จ!")