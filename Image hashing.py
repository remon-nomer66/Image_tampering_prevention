import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import hashlib
import pickle

def hash_pixel(prev_hash, pixel_data):
    hasher = hashlib.sha256()
    hasher.update(prev_hash.encode('utf-8'))
    hasher.update(str(pixel_data).encode('utf-8'))
    return hasher.hexdigest()

def generate_and_save_image_hash(image_path, binary_path):
    img = Image.open(image_path).convert('RGB')  # Alpha値を無視してRGBに変換
    pixels = img.load()
    width, height = img.size
    
    pixel_info_list = []
    prev_hash = hashlib.sha256(b'initial value').hexdigest()
    
    for y in range(height):
        for x in range(width):
            pixel_data = pixels[x, y]
            current_hash = hash_pixel(prev_hash, pixel_data)
            prev_hash = current_hash
            pixel_info_list.append((pixel_data, current_hash))
    
    with open(binary_path, 'wb') as binary_file:
        pickle.dump((pixel_info_list, width, height), binary_file)

def restore_and_check_image(binary_path):
    with open(binary_path, 'rb') as binary_file:
        pixel_info_list, width, height = pickle.load(binary_file)
    
    img = Image.new('RGB', (width, height))  # 復元する画像もRGBモードで作成
    pixels = img.load()
    
    tampered = False
    prev_hash = hashlib.sha256(b'initial value').hexdigest()
    for i, (pixel_data, saved_hash) in enumerate(pixel_info_list):
        x = i % width
        y = i // width
        current_hash = hash_pixel(prev_hash, pixel_data)
        if current_hash != saved_hash:
            tampered = True
            break
        prev_hash = current_hash
        pixels[x, y] = pixel_data  # Alpha値を無視したRGBデータのみを使用
    
    return img, tampered

def save_image():
    image_path = filedialog.askopenfilename()
    if image_path:
        binary_path = filedialog.asksaveasfilename(defaultextension=".bin")
        if binary_path:
            generate_and_save_image_hash(image_path, binary_path)
            messagebox.showinfo("Success", "Image data has been saved in binary format.")

def load_and_verify_image():
    binary_path = filedialog.askopenfilename(filetypes=[("Binary files", "*.bin")])
    if binary_path:
        img, tampered = restore_and_check_image(binary_path)
        if tampered:
            messagebox.showwarning("Warning", "Image data may have been tampered with!")
        else:
            messagebox.showinfo("Success", "Image restored successfully with no tampering detected.")
        save_path = filedialog.asksaveasfilename(defaultextension=".png")
        if save_path:
            img.save(save_path)

root = tk.Tk()
root.title("Image Hash and Restore GUI")

save_button = tk.Button(root, text="Save Image in Binary Format", command=save_image)
save_button.pack()

load_button = tk.Button(root, text="Load and Verify Image from Binary", command=load_and_verify_image)
load_button.pack()

root.mainloop()