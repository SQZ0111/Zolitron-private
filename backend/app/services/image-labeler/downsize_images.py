# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Zolitron
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

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