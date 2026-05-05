
requirements:
download Ollama
download the qwen2.5vl:3b from Ollama
do pip install for ollama
(run the script and check if thats all you need to download)

running the code:
insert photos into images folder.
run downsize_images.py ,this scales them down and cuts a bit of the top of the image (the sky) to make the llm run faster.
run labeler.py ,this then prints out the info about the photo and saves it in the results.txt file.