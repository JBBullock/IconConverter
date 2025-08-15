import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import os
import io

# --- SETTINGS ---
PREVIEW_SIZE = (400, 400)
DEFAULT_COLORS = 32
DEFAULT_QUALITY = 50
MAX_COLORS = 256
MIN_COLORS = 4
ICON_SIZES = [16, 32, 48, 256]  # standard ICO sizes

# --- GLOBALS ---
original_img = None
preview_img = None
color_slider = None
quality_slider = None
orig_label = None
comp_label = None
status_label = None

# --- FUNCTIONS ---
def select_file():
    global original_img
    file_path = filedialog.askopenfilename(
        filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif")]
    )
    if not file_path:
        return
    original_img = Image.open(file_path).convert("RGB")
    show_preview()

def show_preview(*args):
    global preview_img
    if original_img is None:
        return

    colors = color_slider.get()
    quality = quality_slider.get()

    # Reduce colors and convert back to RGB for JPEG preview
    compressed_copy = original_img.convert("P", palette=Image.ADAPTIVE, colors=colors).convert("RGB")

    # Apply JPEG compression in memory for preview
    buffer = io.BytesIO()
    compressed_copy.save(buffer, format="JPEG", quality=quality)
    buffer.seek(0)
    compressed_copy = Image.open(buffer)

    preview_img = compressed_copy

    # Generate preview thumbnails
    orig_preview = original_img.resize(PREVIEW_SIZE)
    comp_preview = compressed_copy.resize(PREVIEW_SIZE)

    orig_tk = ImageTk.PhotoImage(orig_preview)
    comp_tk = ImageTk.PhotoImage(comp_preview)

    orig_label.config(image=orig_tk)
    orig_label.image = orig_tk
    comp_label.config(image=comp_tk)
    comp_label.image = comp_tk

    # Show file sizes
    orig_size = get_image_size_bytes(original_img)
    comp_size = len(buffer.getvalue())
    status_label.config(text=f"Original: {orig_size/1024:.1f} KB | Compressed: {comp_size/1024:.1f} KB")

def get_image_size_bytes(img):
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=95)
    return len(buffer.getvalue())

def save_image():
    if preview_img is None:
        return
    save_path = filedialog.asksaveasfilename(
        defaultextension=".jpg",
        filetypes=[("JPEG files", "*.jpg"), ("All files", "*.*")]
    )
    if not save_path:
        return
    preview_img.convert("RGB").save(save_path, quality=quality_slider.get())
    status_label.config(text=f"Saved: {os.path.basename(save_path)}")

def save_as_ico():
    if preview_img is None:
        return
    save_path = filedialog.asksaveasfilename(
        defaultextension=".ico",
        filetypes=[("Icon files", "*.ico"), ("All files", "*.*")]
    )
    if not save_path:
        return

    # Make sure image is square for ICO
    w, h = preview_img.size
    size = max(w, h)
    square_img = Image.new("RGB", (size, size), (0, 0, 0))  # black background
    square_img.paste(preview_img, ((size - w)//2, (size - h)//2))

    # Generate multiple sizes
    icons = [square_img.resize((s, s), Image.LANCZOS) for s in ICON_SIZES]

    # Save as ICO with multiple sizes
    icons[0].save(save_path, format="ICO", sizes=[(s, s) for s in ICON_SIZES])
    status_label.config(text=f"Saved ICO: {os.path.basename(save_path)}")

def main():
    global color_slider, quality_slider, orig_label, comp_label, status_label

    root = tk.Tk()
    root.title("Lossy Image Compressor + ICO")
    root.geometry("1000x750")

    tk.Button(root, text="📂 Select Image", command=select_file).pack(pady=10)

    slider_frame = tk.Frame(root)
    slider_frame.pack(pady=10)

    tk.Label(slider_frame, text="🎨 Colors:").grid(row=0, column=0, sticky="w")
    color_slider = tk.Scale(slider_frame, from_=MIN_COLORS, to=MAX_COLORS, orient="horizontal", command=show_preview)
    color_slider.set(DEFAULT_COLORS)
    color_slider.grid(row=0, column=1, padx=10)

    tk.Label(slider_frame, text="🖼 Quality:").grid(row=1, column=0, sticky="w")
    quality_slider = tk.Scale(slider_frame, from_=1, to=100, orient="horizontal", command=show_preview)
    quality_slider.set(DEFAULT_QUALITY)
    quality_slider.grid(row=1, column=1, padx=10)

    frame = tk.Frame(root)
    frame.pack(pady=10)

    orig_label = tk.Label(frame)
    orig_label.grid(row=0, column=0, padx=20)
    comp_label = tk.Label(frame)
    comp_label.grid(row=0, column=1, padx=20)

    # Save buttons
    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=10)

    tk.Button(btn_frame, text="💾 Save JPEG", command=save_image).grid(row=0, column=0, padx=10)
    tk.Button(btn_frame, text="🖼 Save ICO", command=save_as_ico).grid(row=0, column=1, padx=10)

    status_label = tk.Label(root, text="")
    status_label.pack(pady=6)

    root.mainloop()

if __name__ == "__main__":
    main()
