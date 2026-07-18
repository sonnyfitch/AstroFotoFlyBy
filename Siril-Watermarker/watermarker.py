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
v1.9.6 (Stable)   - Protected source assets by generating isolated alternative path targets dynamically.
================================================================================
"""

import os
import json
import cv2
import numpy as np
import tkinter as tk
from tkinter import messagebox, filedialog

CACHE_FILE = os.path.join(os.path.dirname(__file__), "watermark_cache.json")

def load_cached_data():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_data_to_cache(data_dict):
    try:
        with open(CACHE_FILE, "w") as f:
            json.dump(data_dict, f)
    except Exception as e:
        print(f"Error saving configurations: {e}")

def clear_cache_file():
    if os.path.exists(CACHE_FILE):
        try:
            os.remove(CACHE_FILE)
        except Exception as e:
            print(f"Error clearing cache file: {e}")

def get_watermark_configuration():
    root = tk.Tk()
    root.withdraw()
    
    cache = load_cached_data()
    
    if cache:
        choice_box = tk.Toplevel(root)
        choice_box.title("Watermark Profile Setup")
        choice_box.geometry("440x160")
        choice_box.attributes("-topmost", True)
        choice_box.resizable(False, False)
        
        lbl_text = "Found existing profile specifications.\nChoose workspace behavior:"
        if cache.get("sig_file"):
            lbl_text += f"\nLogo Asset: {os.path.basename(cache['sig_file'])}"
        else:
            lbl_text += f"\nSignature Text: \"{cache.get('line1', '')}\""
            
        lbl = tk.Label(choice_box, text=lbl_text, justify="center", font=("Arial", 10))
        lbl.pack(pady=15)
        
        selection = {"action": "use"}
        def handle_action(act):
            selection["action"] = act
            choice_box.destroy()
            
        btn_frame = tk.Frame(choice_box)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Keep / Save", width=12, command=lambda: handle_action("use")).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Reset / Modify", width=12, command=lambda: handle_action("reset")).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Clear Profile", width=12, command=lambda: handle_action("clear")).grid(row=0, column=2, padx=5)
        
        choice_box.wait_window()
        
        if selection["action"] == "use":
            return cache
        elif selection["action"] == "clear":
            clear_cache_file()
            cache = {}

    input_window = tk.Toplevel(root)
    input_window.title("Configure Watermark Details (v1.9.6)")
    input_window.geometry("540x240")
    input_window.attributes("-topmost", True)
    input_window.resizable(False, False)

    result = {"cancelled": True}

    tk.Label(input_window, text="Signature Image File (Optional):").grid(row=0, column=0, sticky="w", padx=10, pady=5)
    file_path_var = tk.StringVar(value=cache.get("sig_file", ""))
    file_entry = tk.Entry(input_window, textvariable=file_path_var, width=42)
    file_entry.grid(row=0, column=1, padx=5, pady=5)
    
    def browse_sig_image():
        fp = filedialog.askopenfilename(
            title="Select Logo/Signature File", 
            filetypes=[("All Files", "*.*"), ("PNG Files", "*.png")]
        )
        if fp:
            file_path_var.set(fp)
    tk.Button(input_window, text="Browse...", command=browse_sig_image).grid(row=0, column=2, padx=5, pady=5)

    tk.Label(input_window, text="Line 1: Name / Copyright Text:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
    line1_var = tk.StringVar(value=cache.get("line1", "© 2026 Stack-Horizon"))
    tk.Entry(input_window, textvariable=line1_var, width=54).grid(row=1, column=1, columnspan=2, sticky="w", padx=5, pady=5)

    tk.Label(input_window, text="Line 2: Target Location / Date:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
    line2_var = tk.StringVar(value=cache.get("line2", "Ventura, CA, USA"))
    tk.Entry(input_window, textvariable=line2_var, width=54).grid(row=2, column=1, columnspan=2, sticky="w", padx=5, pady=5)

    tk.Label(input_window, text="Line 3: Tech Specs / Equipment:").grid(row=3, column=0, sticky="w", padx=10, pady=5)
    line3_var = tk.StringVar(value=cache.get("line3", "Siril Stacked Integration"))
    tk.Entry(input_window, textvariable=line3_var, width=54).grid(row=3, column=1, columnspan=2, sticky="w", padx=5, pady=5)

    def submit_form():
        result["cancelled"] = False
        result["sig_file"] = file_path_var.get().strip()
        result["line1"] = line1_var.get().strip()
        result["line2"] = line2_var.get().strip()
        result["line3"] = line3_var.get().strip()
        input_window.destroy()

    btn_submit_frame = tk.Frame(input_window)
    btn_submit_frame.grid(row=4, column=0, columnspan=3, pady=15)
    tk.Button(btn_submit_frame, text="Confirm & Run", width=16, command=submit_form).pack(side="left", padx=10)
    tk.Button(btn_submit_frame, text="Cancel", width=12, command=input_window.destroy).pack(side="left", padx=10)

    input_window.wait_window()
    
    if result["cancelled"]:
        return None
        
    should_cache = messagebox.askyesno("Cache Manager", "Would you like to preserve this profile context for future automation runs?")
    if should_cache:
        save_data_to_cache({
            "sig_file": result["sig_file"],
            "line1": result["line1"],
            "line2": result["line2"],
            "line3": result["line3"]
        })
        
    return result

def apply_watermark(image_path, config):
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Could not load target image file asset at {image_path}")
        return False, None
        
    h, w, _ = img.shape
    margin_x = int(w * 0.02)
    margin_y = int(h * 0.03)

    # Automatically generate a safe new file output path to preserve the original stack
    base_dir, base_file = os.path.split(image_path)
    filename, ext = os.path.splitext(base_file)
    output_path = os.path.join(base_dir, f"{filename}.watermarked{ext}")

    if config.get("sig_file") and os.path.exists(config["sig_file"]):
        logo = cv2.imread(config["sig_file"], cv2.IMREAD_UNCHANGED)
        if logo is not None:
            logo_h, logo_w = logo.shape, logo.shape
            target_w = int(w * 0.15)
            target_h = int(logo_h * (target_w / logo_w))
            logo = cv2.resize(logo, (target_w, target_h), interpolation=cv2.INTER_AREA)
            
            y1 = h - target_h - margin_y
            y2 = h - margin_y
            x1 = w - target_w - margin_x
            x2 = w - margin_x
            
            if len(logo.shape) > 2 and logo.shape == 4:
                alpha = logo[:, :, 3] / 255.0
                for c in range(3):
                    img[y1:y2, x1:x2, c] = (1.0 - alpha) * img[y1:y2, x1:x2, c] + alpha * logo[:, :, c]
            else:
                img[y1:y2, x1:x2] = logo[:, :, :3]
            
            cv2.imwrite(output_path, img)
            print(f"Logo watermarked onto alternative output file target: {output_path}")
            return True, output_path

    font_scale = max(0.5, w / 3200.0)
    thickness = max(1, int(w / 1600))
    font = cv2.FONT_HERSHEY_SIMPLEX
    
    text_lines = [config["line1"], config["line2"], config["line3"]]
    text_lines = [line for line in text_lines if line]

    current_y = h - margin_y
    for text in reversed(text_lines):
        text_size, _ = cv2.getTextSize(text, font, font_scale, thickness)
        text_w, text_h = text_size, text_size
        line_spacing = int(text_h * 1.8)
        
        pos_x = w - text_w - margin_x
        
        cv2.putText(img, text, (pos_x + 2, current_y + 2), font, font_scale, (0, 0, 0), thickness + 1, cv2.LINE_AA)
        cv2.putText(img, text, (pos_x, current_y), font, font_scale, (255, 255, 255), thickness, cv2.LINE_AA)
        
        current_y -= line_spacing

    cv2.imwrite(output_path, img)
    print(f"Stitched multi-line text parameters to alternative output target: {output_path}")
    return True, output_path

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
        filetypes=[("All Files", "*.*"), ("Image Files", "*.tif *.tiff *.jpg *.jpeg *.png")]
    )
    
    if target_file:
        success, final_output = apply_watermark(target_file, config)
        
        # Force Siril command canvas to reload the alternative watermarked file layout
        if success and final_output:
            print(f"siril load \"{final_output}\"")

if __name__ == "__main__":
    main()
