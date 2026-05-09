import os
from PIL import Image

image_folder = "images"
output_folder = "processed_images"

files = os.listdir(image_folder)

count = 0
for filename in files:
	if filename.endswith((".jpg", ".png", ".jpeg")):
		extension = os.path.splitext(filename)[1]
		input_path = os.path.join(image_folder, filename)
		output_path = os.path.join(output_folder, f"I_{count}{extension}")
		count += 1
		try:
			with Image.open(input_path) as img:
						#Resize to 640x480
						#4:3 ration quite common with the mapillary images
						img_resized = img.resize((640, 480), Image.Resampling.LANCZOS)
						#Crop the top third
						left = 0
						top = 160
						right = 640
						bottom = 480
						top_third = img_resized.crop((left, top, right, bottom))
						top_third.save(output_path)
		except Exception as e:
			print(f"Error processing {filename}: {e}")

print("Processing complete. Check the processed_images folder.")