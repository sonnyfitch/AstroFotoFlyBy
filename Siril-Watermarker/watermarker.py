"""
================================================================================
REVISION HISTORY:
v1.0.0 (Initial)  - Added core watermarking logic using Pillow library.
v1.1.0 (Update)   - Added Tkinter pop-up for dynamic target name input.
v1.2.0 (Fix)      - Implemented automatic dependency bootloader for PIL & sirilpy.
v1.3.0 (Fix)      - Replaced .filepath with get_cwd() to resolve FFit error layers.
v1.4.0 (Fix)      - Switched to explicit IPC command sending to resolve 'get_cwd' attribute error.
v1.5.0 (Fix)      - Rewrote using siril.cmd and direct Tkinter manual fallback file selection.
v1.6.0 (Update)   - Streamlined code execution loop directly to the working manual selector.
v1.7.0 (Update)   - Replaced single prompt with an expanded custom multi-field configuration GUI.
v1.8.0 (Update)   - Restructured into a clean 3-line layout including Location and Tech Specs.
================================================================================
"""

import os
import json
import cv2
import numpy as np
import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog

# Define where the local cache file will live on your disk
CACHE_FILE = os.path.join(os.path.dirname(__file__), "watermark_cache.json")

def load_cached_data():
    """Retrieves saved configurations from the local JSON storage file."""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_data_to_cache(name_data):
    """Writes the current working signature data directly to local disk."""
    try:
        with open(CACHE_FILE, "w") as f:
            json.dump({"saved_name": name_data}, f)
    except Exception as e:
        print(f"Error updating local configuration cache: {e}")

def clear_cache_file():
    """Removes the persistent local settings block from the workspace environment."""
    if os.path.exists(CACHE_FILE):
        try:
            os.remove(CACHE_FILE)
        except Exception as e:
            print(f"Error removing cached file asset: {e}")

def get_watermark_identity():
    """Manages the UI lifecycle for caching, resetting, and purging workspace metadata."""
    root = tk.Tk()
    root.withdraw() # Hide the main background window
    
    cache = load_cached_data()
    cached_name = cache.get("saved_name", "")
    
    # If a cache exists, ask to Save (Keep), Reset (Modify), or Clear
    if cached_name:
        choice_box = tk.Toplevel(root)
        choice_box.title("Watermark Profile Setup")
        choice_box.geometry("400x150")
        choice_box.attributes("-topmost", True)
        choice_box.resizable(False, False)
        
        lbl = tk.Label(
            choice_box, 
            text=f"Found existing profile:\n\"{cached_name}\"\n\nChoose an action:",
            justify="center",
            font=("Arial", 10),
            padx=10,
            pady=10
        )
        lbl.pack(pady=10)
        
        selection = {"action": "use"}
        
        def handle_action(act):
            selection["action"] = act
            choice_box.destroy()
            
        btn_frame = tk.Frame(choice_box)
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="Keep / Save", width=12, command=lambda: handle_action("use")).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Reset / Modify", width=12, command=lambda: handle_action("reset")).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Clear Profile", width=12, command=lambda: handle_action("clear")).grid(row=0, column=2, padx=5)
        
        choice_box.wait_window()
        
        if selection["action"] == "use":
            return cached_name
        elif selection["action"] == "clear":
            clear_cache_file()
            cached_name = ""
            # Fallthrough to ask for a new name definition below
            
    # Solicit fresh input if cache is blank or reset was requested
    user_input = simpledialog.askstring("Watermark Tool Initializer", "Enter signature text (e.g. © 2026 Stack-Horizon):")
    
    if user_input:
        should_cache = messagebox.askyesno("Cache Manager", "Would you like to preserve this profile context for future automation runs?")
        if should_cache:
            save_data_to_cache(user_input)
        return user_input
        
    return "© Default Watermark Context"

def apply_watermark(image_path, config):
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Could not load target image file asset at {image_path}")
        return False
        
    h, w, _ = img.shape
    margin_x = int(w * 0.02)
    margin_y = int(h * 0.03)

    if config.get("sig_file") and os.path.exists(config["sig_file"]):
        logo = cv2.imread(config["sig_file"], cv2.IMREAD_UNCHANGED)
        if logo is not None:
            logo_h, logo_w = logo.shape[0], logo.shape[1]
            target_w = int(w * 0.15)
            target_h = int(logo_h * (target_w / logo_w))
            logo = cv2.resize(logo, (target_w, target_h), interpolation=cv2.INTER_AREA)
            
            y1 = h - target_h - margin_y
            y2 = h - margin_y
            x1 = w - target_w - margin_x
            x2 = w - margin_x
            
            if logo.shape[2] == 4:
                alpha = logo[:, :, 3] / 255.0
                for c in range(3):
                    img[y1:y2, x1:x2, c] = (1.0 - alpha) * img[y1:y2, x1:x2, c] + alpha * logo[:, :, c]
            else:
                img[y1:y2, x1:x2] = logo[:, :, :3]
            
            cv2.imwrite(image_path, img)
            print(f"Graphic logo signature watermarked onto image asset: {image_path}")
            return True

    font_scale = max(0.5, w / 3200.0)
    thickness = max(1, int(w / 1600))
    font = cv2.FONT_HERSHEY_SIMPLEX
    
    text_lines = [config["line1"], config["line2"], config["line3"]]
    text_lines = [line for line in text_lines if line]

    current_y = h - margin_y
    for text in reversed(text_lines):
        text_size, _ = cv2.getTextSize(text, font, font_scale, thickness)
        text_w, text_h = text_size[0], text_size[1]
        line_spacing = int(text_h * 1.8)
        
        pos_x = w - text_w - margin_x
        
        cv2.putText(img, text, (pos_x + 2, current_y + 2), font, font_scale, (0, 0, 0), thickness + 1, cv2.LINE_AA)
        cv2.putText(img, text, (pos_x, current_y), font, font_scale, (255, 255, 255), thickness, cv2.LINE_AA)
        
        current_y -= line_spacing

    cv2.imwrite(image_path, img)
    print(f"Stitched multi-line text parameters to destination asset: {image_path}")
    return True

def main():
    print("Initializing Siril Automated Watermarker Engine...")
    config = get_watermark_configuration()
    if not config:
        print("Run execution halted.")
        return
        
    root = tk.Tk()
    root.withdraw()
    target_file = filedialog.askopenfilename(
        title="Select Astrophotography Target Image Frame Asset",
        filetypes=[("Image Files", "*.tif *.tiff *.jpg *.jpeg *.png")]
    )
    
    if target_file:
        apply_watermark(target_file, config)
