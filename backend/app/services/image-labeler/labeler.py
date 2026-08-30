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

import ollama
import os
import json

open('results.txt', 'w').close()

image_folder = "processed_images"

files = os.listdir(image_folder)

for filename in files:
    if filename.endswith((".jpg", ".png", ".jpeg")):
        print(f"--- Analyzing {filename} ---")
        
        path = os.path.join(image_folder, filename)
        
        response = ollama.chat(
            model='qwen2.5vl:3b',
            messages=[{
                'role': 'user',
                'content': 'Given image is {640,320} pixels, given is a street image, is there any overgrown vegetation? Return a JSON with "weeds_found" (boolean) and "bbox" [ymin, xmin, ymax, xmax].',
                'images': [path]
            }]
        )
        qwen_data = response['message']['content']
        clean_json = qwen_data.replace("```json", "").replace("```", "").strip()
        data = json.loads(clean_json)
        with open('results.txt', 'a') as f:
            f.write(f"Image: {filename}\n")
            f.write(f"Weeds: {data['weeds_found']}\n")
            f.write(f"BBox: {data['bbox']}\n")
            f.write("_____\n")
        print(data)