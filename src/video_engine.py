import os
import cv2
import numpy as np
from astropy.io import fits

def unwrap_path(item):
    """Bulletproof un-nester that continuously pulls out the first element until it hits a string."""
    while isinstance(item, (list, tuple, set)):
        if len(item) > 0:
            item = list(item)[0]  # FIXED: Force pull the absolute first index out of the sequence array
        else:
            return None
    return item

def load_and_normalize_image(file_path):
    """Intelligently processes standard consumer formats or memory-mapped FITS layers."""
    file_path = unwrap_path(file_path)
    
    if not file_path or not isinstance(file_path, str):
        print(" ❌ Error: Resolved file path is empty or invalid.")
        return None

    ext = os.path.splitext(file_path).lower()
    
    if ext not in ['.fit', '.fits']:
        print(f" [LOG] Reading consumer matrix via OpenCV: {os.path.basename(file_path)[:20]}...")
        return cv2.imread(file_path)

    try:
        print(f" [LOG] Opening memory-mapped FITS stream: {os.path.basename(file_path)[:20]}...")
        with fits.open(file_path, mode='readonly', memmap=True, ignore_missing_end=True) as hdul:
            data_layer = None
            for hdu in hdul:
                if hdu.data is not None:
                    data_layer = hdu.data
                    break
            
            if data_layer is None:
                return None

            shape = data_layer.shape
            
            if len(shape) == 3:
                c_dim, h_dim, w_dim = shape
                img_data = np.zeros((h_dim, w_dim, 3), dtype=np.float32)
                channels_to_fetch = min(c_dim, 3)
                for c in range(channels_to_fetch):
                    np.copyto(img_data[:, :, c], data_layer[c, :, :].astype(np.float32))
                img_float = cv2.cvtColor(img_data, cv2.COLOR_RGB2BGR)
                del img_data
            else:
                h_dim, w_dim = shape
                img_float = np.zeros((h_dim, w_dim), dtype=np.float32)
                np.copyto(img_float, data_layer.astype(np.float32))

            sample_data = img_float[::16, ::16]
            min_val = np.percentile(sample_data, 1.0)
            max_val = np.percentile(sample_data, 99.0)
            del sample_data
            
            if max_val - min_val > 0:
                img_float = np.clip((img_float - min_val) / (max_val - min_val), 0.0, 1.0)
            else:
                img_float = np.clip(img_float / (np.max(img_float) if np.max(img_float) > 0 else 1.0), 0.0, 1.0)

            img_8bit = (img_float * 255.0).astype(np.uint8)
            del img_float
            
            if len(img_8bit.shape) == 2:
                img_8bit = cv2.cvtColor(img_8bit, cv2.COLOR_GRAY2BGR)
                
            return img_8bit
    except Exception as e:
        print(f" ❌ Error compiling FITS asset matrix: {e}")
        return None

def render_spaceflight(selected_pair):
    """Executes frame transformation layouts and exports an MP4 movie container."""
    print(f"\n[Step 3] Loading image assets into background processing buffers...")
    
    starless_src = unwrap_path(selected_pair['starless'])
    starmask_src = unwrap_path(selected_pair['starmask'])
    out_dir = unwrap_path(selected_pair['output_dir'])

    bg_img = load_and_normalize_image(starless_src)
    stars_img = load_and_normalize_image(starmask_src)

    if bg_img is None or stars_img is None:
        print("❌ Error: Could not parse target data files.")
        return

    if bg_img.shape != stars_img.shape:
        stars_img = cv2.resize(stars_img, (bg_img.shape, bg_img.shape))

    height, width, _ = bg_img.shape
    fps = 30
    total_frames = fps * 10
    
    output_path = os.path.join(out_dir, f"spaceflight_{selected_pair['folder']}.mp4")

    render_w, render_h = width, height
    if width > 1920:
        render_w = 1920
        render_h = int(height * (1920 / width))
        print(f" [LOG] Scaling layout bounds down to HD standard ({render_w}x{render_h}) for safe processing limits...")
        bg_img = cv2.resize(bg_img, (render_w, render_h))
        stars_img = cv2.resize(stars_img, (render_w, render_h))

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter(output_path, fourcc, fps, (render_w, render_h))

    print(f"\n[Step 4] Starting Flight Frame Render Loop ({total_frames} total frames)...")
    bg_max_zoom = 1.06       
    stars_max_zoom = 1.65    

    for frame_idx in range(total_frames):
        t = frame_idx / (total_frames - 1)

        M_bg = cv2.getRotationMatrix2D((render_w / 2, render_h / 2), 0, 1.0 + (bg_max_zoom - 1.0) * t)
        frame_bg = cv2.warpAffine(bg_img, M_bg, (render_w, render_h), flags=cv2.INTER_LINEAR)

        M_stars = cv2.getRotationMatrix2D((render_w / 2, render_h / 2), 0, 1.0 + (stars_max_zoom - 1.0) * t)
        frame_stars = cv2.warpAffine(stars_img, M_stars, (render_w, render_h), flags=cv2.INTER_LINEAR)

        if t > 0.6:
            frame_stars = cv2.convertScaleAbs(frame_stars, alpha=1.0 - ((t - 0.6) * 0.5), beta=0)

        video_writer.write(cv2.add(frame_bg, frame_stars))

        if frame_idx % 15 == 0:
            print(f"   -> Rendering Frame {frame_idx}/{total_frames} ({int(t * 100)}% Complete)")

    video_writer.release()
    print(f"\n🚀 Success! Your 3D Space Flight Video is saved here:\n  ➡️ {output_path}")
