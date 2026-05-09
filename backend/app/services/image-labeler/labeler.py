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