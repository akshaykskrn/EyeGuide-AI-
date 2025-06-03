import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import cv2
from ultralytics import YOLO
import numpy as np
import queue
import pyttsx3
import pytesseract
import pyautogui
import keyboard
import requests
import os
import subprocess
import sys
from datetime import datetime
import psutil
import pyperclip
import win32gui
import win32con
import win32process
from PIL import Image, ImageTk
import re

# For Azure integration if enabled
try:
    from azure.cognitiveservices.vision.computervision import ComputerVisionClient
    from msrest.authentication import CognitiveServicesCredentials
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False

# Configure pytesseract path if on Windows
if sys.platform == 'win32':
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# -------------- CONFIGURATION -----------------
AZURE_ENDPOINT = "https://eyeguideai2025.cognitiveservices.azure.com/"
AZURE_KEY = "CSiHUHZYTZKcj8iTiwyKmzic5eljvaQ1slyANS24QsSzVpojIJIdJQQJ99BDACYeBjFXJ3w3AAAFACOG1o1R"
SOS_PHONE_NUMBER = "8073320798"  # Include country code for international numbers

# WhatsApp configuration
WHATSAPP_POTENTIAL_PATHS = [
    r"C:\Users\%USERNAME%\AppData\Local\WhatsApp\WhatsApp.exe",
    r"C:\Program Files\WindowsApps\5319275A.WhatsAppDesktop_2.2323.4.0_x64__cv1g1gvanyjgm\WhatsApp.exe",
    r"C:\Program Files\WhatsApp\WhatsApp.exe",
    r"C:\Program Files\WindowsApps\WhatsAppDesktop_*\WhatsApp.exe",
    r"C:\Program Files (x86)\WhatsApp\WhatsApp.exe",
    r"C:\Users\%USERNAME%\AppData\Local\Programs\WhatsApp\WhatsApp.exe",
]

# UI Colors & Fonts
BG_COLOR = "#121212"
FG_COLOR = "#f5f6fa"
ACCENT_COLOR = "#00cec9"
FONT_NAME = "Segoe UI"
CAM_WIDTH = 640
CAM_HEIGHT = 480

LOG_FILE = "eyeguide_ai_enhanced_log.txt"

# Camera calibration coefficient for distance (adjust experimentally)
DISTANCE_COEFF = 6800 

# YOLO confidence threshold
YOLO_CONF_THRESHOLD = 0.4

# Object detection interval (seconds)
OBJECT_DETECTION_INTERVAL = 3.0  # Changed from 5 to 3 seconds per requirements

# ---------------- Utility Functions ---------------------

def log_event(msg: str):
    """Logs event to file and UI queue"""
    timestamped = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n"
    try:
        with open(LOG_FILE, "a") as f:
            f.write(timestamped)
    except Exception:
        pass
    AppUI.log_queue.put(timestamped)

# TTS Queue + worker
tts_queue = queue.Queue()
speech_priority_queue = queue.PriorityQueue()  # For prioritized speech handling

def tts_worker():
    """Worker thread to handle text-to-speech queue"""
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    while True:
        text = tts_queue.get()
        if text is None:
            break
        try:
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            log_event(f"TTS error: {e}")
        tts_queue.task_done()

def speak(text: str, priority=10):
    """Add text to speech queue with optional priority"""
    if not text.strip():
        return
        
    # Only queue if not already queued (avoid duplicates)
    if tts_queue.qsize() < 5:  # Prevent queue overflow
        tts_queue.put(text)

def get_live_location():
    """Attempt to get current location via IP"""
    try:
        resp = requests.get("http://ip-api.com/json/", timeout=5)
        data = resp.json()
        if data.get('status') == 'success':
            return round(data['lat'], 6), round(data['lon'], 6)
    except Exception as e:
        log_event(f"Location fetch failed: {e}")
    return None

def format_sos_msg():
    """Format emergency SOS message with location if available"""
    base = "EMERGENCY ALERT! This is an automated SOS message from EyeGuide AI application. Please help!"
    loc = get_live_location()
    if loc:
        url = f"https://www.google.com/maps?q={loc[0]},{loc[1]}"
        return f"{base} My approximate location: {url}"
    return f"{base} Location could not be determined."

def approximate_distance_by_height(bbox_height, frame_height, coeff=DISTANCE_COEFF):
    """Calculate approximate distance based on bounding box height"""
    if bbox_height <= 0:
        return float('inf')
    return round(coeff / bbox_height, 2)

def is_process_running(proc_name):
    """Check if a process is running by name (case insensitive)"""
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] and proc_name.lower() in proc.info['name'].lower():
            return True
    return False

def get_whatsapp_window():
    """Find WhatsApp window handle more reliably with better matching"""
    result = []
    
    def callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            # Match both "WhatsApp" and "WhatsApp Desktop"
            if 'WhatsApp' in title:
                result.append((hwnd, title))
                
    win32gui.EnumWindows(callback, None)
    
    # Sort results - prioritize main window over chat window
    if result:
        # First try to find main application window
        for hwnd, title in result:
            if title.lower() == 'whatsapp' or 'whatsapp desktop' in title.lower():
                return hwnd
                
        # Otherwise return first window found
        return result[0][0]
    return None

def find_whatsapp_executable():
    """Search for WhatsApp Desktop executable in common locations with wildcards"""
    # Expand environment variables in paths
    expanded_paths = []
    for path in WHATSAPP_POTENTIAL_PATHS:
        expanded = os.path.expandvars(path)
        if '*' in expanded:
            # Handle wildcards in paths
            base_dir = os.path.dirname(expanded.split('*')[0])
            pattern = os.path.basename(expanded.replace('*', '.*'))
            if os.path.exists(base_dir):
                # Use regex to find matching directories
                for item in os.listdir(base_dir):
                    if re.match(pattern, item) and os.path.isdir(os.path.join(base_dir, item)):
                        potential_exe = os.path.join(base_dir, item, "WhatsApp.exe")
                        if os.path.exists(potential_exe):
                            expanded_paths.append(potential_exe)
        else:
            expanded_paths.append(expanded)
    
    # Try all paths
    for path in expanded_paths:
        if os.path.exists(path):
            log_event(f"Found WhatsApp executable at: {path}")
            return path
            
    # If we can't find it directly, look for running processes
    if is_process_running("WhatsApp.exe"):
        for proc in psutil.process_iter(['name', 'exe']):
            if proc.info['name'] and 'whatsapp' in proc.info['name'].lower():
                if proc.info.get('exe'):
                    log_event(f"Found running WhatsApp at: {proc.info['exe']}")
                    return proc.info['exe']
                    
    return None

def launch_whatsapp():
    """Launch WhatsApp Desktop application with robust error handling"""
    if sys.platform != 'win32':
        log_event("WhatsApp automation only supported on Windows in this script.")
        return False

    # Check if already running
    if is_process_running("WhatsApp.exe"):
        log_event("WhatsApp is already running.")
        return True
        
    # Find executable
    whatsapp_path = find_whatsapp_executable()
    
    if not whatsapp_path:
        log_event("Could not find WhatsApp Desktop executable. Please check installation.")
        return False
        
    try:
        log_event(f"Launching WhatsApp from: {whatsapp_path}")
        subprocess.Popen([whatsapp_path])
        
        # Wait for process to start
        start_time = time.time()
        while time.time() - start_time < 30:  # 30 second timeout
            if is_process_running("WhatsApp.exe"):
                time.sleep(3)  # Give UI more time to initialize
                return True
            time.sleep(1)
            
        log_event("Timeout waiting for WhatsApp to start")
        return False
    except Exception as e:
        log_event(f"Error launching WhatsApp: {e}")
        return False

# ----------- Main App Class --------------

class AppUI:
    log_queue = queue.Queue()

    def __init__(self, root):
        self.root = root
        self.root.title("EyeGuide AI")
        self.root.config(bg=BG_COLOR)
        self.root.geometry("1000x750")
        self.root.minsize(900, 650)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.azure_client = None
        if AZURE_AVAILABLE:
            self.load_azure_client()

        self.yolo_model = None
        self.load_yolo_model()

        self.cap = None
        self.current_mode = None

        self.tts_thread = threading.Thread(target=tts_worker, daemon=True)
        self.tts_thread.start()

        self.setup_ui()

        self.update_log_text()

        self.running = False
        self.obj_thread = None
        self.text_running = False
        self.sos_mode_active = False
        self.sos_key_thread = None

        self.fps_calc_time = time.time()
        self.frame_count = 0
        self.fps = 0

        self.last_spoken_objects = {}  # Dictionary to track last spoken objects with distances
        self.object_announcement_batch = []  # For batching object announcements
        
        self.whatsapp_status = "Not Started"
        self.whatsapp_hwnd = None

    def load_azure_client(self):
        """Initialize Azure Computer Vision client if credentials available"""
        if not AZURE_AVAILABLE:
            log_event("Azure SDK not available. Install with: pip install azure-cognitiveservices-vision-computervision")
            return
            
        try:
            self.azure_client = ComputerVisionClient(
                AZURE_ENDPOINT, CognitiveServicesCredentials(AZURE_KEY)
            )
            log_event("Azure client initialized successfully.")
        except Exception as e:
            log_event(f"Azure client init failed: {e}")
            messagebox.showerror("Azure Error",
                                 "Failed to initialize Azure Cognitive Services client.")

    def load_yolo_model(self):
        """Load YOLOv8 model for object detection"""
        try:
            self.yolo_model = YOLO('yolov8n.pt')
            log_event("YOLOv8 model loaded successfully.")
        except Exception as e:
            log_event(f"YOLO model load failed: {e}")
            messagebox.showerror("YOLO Error",
                                 "Failed to load YOLO model. Ensure 'yolov8n.pt' is in the directory.")

    def setup_ui(self):
        """Initialize the user interface"""
        title = tk.Label(self.root, text="EyeGuide AI", font=(FONT_NAME, 28, 'bold'),
                         fg=ACCENT_COLOR, bg=BG_COLOR)
        title.pack(pady=15)

        main_frame = tk.Frame(self.root, bg=BG_COLOR)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        left_menu = tk.Frame(main_frame, bg=BG_COLOR)
        left_menu.pack(side="left", fill="y", padx=(0,20), pady=10)

        btn_style = {'font': (FONT_NAME, 14), 'width': 28, 'height': 2, 'bg': ACCENT_COLOR,
                     'fg': FG_COLOR, 'activebackground': '#008080', 'bd':0, 'cursor':'hand2'}

        self.btn_obj_detect = tk.Button(left_menu, text="Object Detection",
                                       command=self.start_object_detection, **btn_style)
        self.btn_obj_detect.pack(pady=15)

        self.btn_text_recog = tk.Button(left_menu, text="Text Recognition and Reading",
                                       command=self.start_text_recognition, **btn_style)
        self.btn_text_recog.pack(pady=15)

        self.btn_sos = tk.Button(left_menu, text="Emergency SOS Mode",
                                 command=self.start_sos_mode, **btn_style)
        self.btn_sos.pack(pady=15)

        self.btn_stop = tk.Button(left_menu, text="Stop Current Mode",
                                  command=self.stop_current_mode, bg='#e84393', fg='white',
                                  font=(FONT_NAME, 14), width=28, height=2, state='disabled', bd=0,
                                  activebackground='#d63031', cursor='hand2')
        self.btn_stop.pack(pady=25)

        self.btn_exit = tk.Button(left_menu, text="Exit Application",
                                  command=self.on_close, bg='#d63031', fg='white',
                                  font=(FONT_NAME, 14), width=28, height=2, bd=0,
                                  activebackground='#b23b3b', cursor='hand2')
        self.btn_exit.pack(side="bottom", pady=20)

        right_frame = tk.Frame(main_frame, bg=BG_COLOR)
        right_frame.pack(side="right", expand=True, fill="both")

        # Video Display
        self.video_label = tk.Label(right_frame, bg='black', width=CAM_WIDTH, height=CAM_HEIGHT)
        self.video_label.pack(padx=10, pady=10)

        # Status Frame
        status_frame = tk.Frame(right_frame, bg=BG_COLOR)
        status_frame.pack(fill='x', padx=10, pady=5)
        
        status_label = tk.Label(status_frame, text="Status:", bg=BG_COLOR, fg=ACCENT_COLOR,
                               font=(FONT_NAME, 10, 'bold'))
        status_label.pack(side='left', padx=(0,5))
        
        self.status_text = tk.Label(status_frame, text="Idle", bg=BG_COLOR, fg=FG_COLOR,
                                  font=(FONT_NAME, 10))
        self.status_text.pack(side='left')

        # Logs Label
        log_lbl = tk.Label(right_frame, text="Application Logs:", fg=ACCENT_COLOR,
                           bg=BG_COLOR, font=(FONT_NAME, 12, 'bold'))
        log_lbl.pack(anchor='w', padx=10)

        # ScrollText for logs
        self.log_text = scrolledtext.ScrolledText(right_frame, bg="#222222", fg=FG_COLOR,
                                                  font=(FONT_NAME, 10), height=12, state='disabled')
        self.log_text.pack(fill='both', expand=True, padx=10, pady=(0,10))

    def update_log_text(self):
        """Update the log text widget with new log entries"""
        while not self.log_queue.empty():
            line = self.log_queue.get()
            self.log_text.configure(state='normal')
            self.log_text.insert(tk.END, line)
            self.log_text.see(tk.END)
            self.log_text.configure(state='disabled')
        self.root.after(200, self.update_log_text)

    def update_status(self, text):
        """Update the status text in the UI"""
        self.status_text.config(text=text)
        self.root.update_idletasks()

    # --- Object Detection ---

    def start_object_detection(self):
        """Start advanced object detection mode"""
        self.stop_current_mode()
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW if sys.platform=='win32' else 0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_HEIGHT)
        if not self.cap.isOpened():
            messagebox.showerror("Camera Error", "Unable to open webcam.")
            return
        self.current_mode = 'object'
        self.running = True
        self.btn_stop.config(state='normal')
        speak("Starting advanced object detection.")
        log_event("Advanced Object Detection started.")
        self.update_status("Running Object Detection")
        self.last_spoken_objects = {}
        self.object_announcement_batch = []
        self.frame_count = 0
        self.fps_calc_time = time.time()
        self.obj_thread = threading.Thread(target=self.object_detection_loop, daemon=True)
        self.obj_thread.start()

    def object_detection_loop(self):
        """Main loop for object detection and voice announcements"""
        detect_interval = OBJECT_DETECTION_INTERVAL  # Changed from 5 to 3 seconds per requirements
        last_detection_time = 0
        detection_in_progress = False
        
        while self.running and self.current_mode == 'object':
            ret, frame = self.cap.read()
            if not ret:
                log_event("Failed to capture frame from webcam.")
                time.sleep(0.1)
                continue

            current_time = time.time()
            display_frame = frame.copy()

            # Update FPS calc
            self.frame_count += 1
            elapsed = current_time - self.fps_calc_time
            if elapsed > 1.0:
                self.fps = self.frame_count / elapsed
                self.frame_count = 0
                self.fps_calc_time = current_time
                
            # Show FPS on display
            cv2.putText(display_frame, f"FPS: {self.fps:.1f}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

            # Run detection on interval
            if current_time - last_detection_time >= detect_interval and not detection_in_progress:
                detection_in_progress = True
                
                # Run detection
                results = self.yolo_model(frame)[0]
                
                # Process results
                current_objects = {}  # {label: distance}
                self.object_announcement_batch = []  # Clear batch
                
                for det in results.boxes.data.tolist() if results.boxes.data is not None else []:
                    x1, y1, x2, y2, conf, cls = det
                    if conf < YOLO_CONF_THRESHOLD:
                        continue

                    x1, y1, x2, y2 = map(int, (x1, y1, x2, y2))
                    conf = round(conf, 2)
                    label = self.yolo_model.names[int(cls)]

                    bbox_height = y2 - y1
                    distance = approximate_distance_by_height(bbox_height, CAM_HEIGHT)
                    
                    # Store for announcement
                    current_objects[label] = distance

                    # Draw on display frame
                    text = f"{label} {conf*100:.0f}% Dist: {distance}cm"
                    cv2.rectangle(display_frame, (x1, y1), (x2, y2), (0, 255, 128), 2)
                    cv2.putText(display_frame, text, (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (25, 255, 25), 2)

                # Process announcements - only announce changes or new objects
                if current_objects:
                    for obj, dist in current_objects.items():
                        # If object is new or distance changed significantly
                        if obj not in self.last_spoken_objects or \
                           abs(self.last_spoken_objects.get(obj, 0) - dist) > 50:
                            self.object_announcement_batch.append(f"{obj} at {dist} centimeters")
                    
                    # Speak the batched announcements
                    if self.object_announcement_batch:
                        if len(self.object_announcement_batch) > 3:
                            # If too many objects, use summary style
                            obj_count = len(self.object_announcement_batch)
                            speak(f"Detected {obj_count} objects. Including {', '.join(self.object_announcement_batch[:3])}")
                        else:
                            # Otherwise announce all objects
                            speak("Detected " + ", ".join(self.object_announcement_batch))
                            
                        # Log detections
                        log_event(f"Detected objects: {', '.join(self.object_announcement_batch)}")
                
                # Update tracking
                self.last_spoken_objects = current_objects
                
                # Reset for next interval
                last_detection_time = current_time
                detection_in_progress = False

            # Convert for tkinter display
            rgb_img = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(rgb_img)
            imgtk = ImageTk.PhotoImage(img_pil)
            try:
                self.video_label.imgtk = imgtk
                self.video_label.configure(image=imgtk)
            except tk.TclError:
                break

            time.sleep(0.03)  # Limit FPS for smoother operation

        self.clear_video()

    # --- Text Recognition ---

    def start_text_recognition(self):
        """Start text recognition mode"""
        self.stop_current_mode()
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW if sys.platform=='win32' else 0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_HEIGHT)
        if not self.cap.isOpened():
            messagebox.showerror("Camera Error", "Unable to open webcam.")
            return

        self.current_mode = 'text'
        self.text_running = True
        self.btn_stop.config(state='normal')
        log_event("Text Recognition started.")
        self.update_status("Running Text Recognition")
        speak("Starting text recognition mode.")
        self.latest_text_spoken = ""
        self.open_text_recognition_window()

    def open_text_recognition_window(self):
        """Open text recognition UI window"""
        self.text_win = tk.Toplevel(self.root)
        self.text_win.title("EyeGuide AI - Text Recognition")
        self.text_win.geometry("700x600")
        self.text_win.configure(bg=BG_COLOR)

        label = tk.Label(self.text_win,
                         text="Text Recognition Mode\nPress 'Capture Text' to read text aloud.\nClose window or Stop mode to exit.",
                         fg=ACCENT_COLOR, bg=BG_COLOR, font=(FONT_NAME, 14))
        label.pack(pady=15)

        btn_capture = tk.Button(self.text_win, text="Capture Text",
                                command=self.capture_text, font=(FONT_NAME, 14),
                                bg=ACCENT_COLOR, fg=FG_COLOR, bd=0, activebackground="#009688")
        btn_capture.pack(pady=10)

        btn_close = tk.Button(self.text_win, text="Stop Text Recognition",
                              command=self.stop_current_mode, font=(FONT_NAME, 14),
                              bg="#e74c3c", fg=FG_COLOR, bd=0, activebackground="#d63031")
        btn_close.pack(pady=10)

        self.text_video_label = tk.Label(self.text_win, bg="black", width=CAM_WIDTH, height=CAM_HEIGHT)
        self.text_video_label.pack(padx=10, pady=10)

        self.text_thread = threading.Thread(target=self.text_preview_loop, daemon=True)
        self.text_thread.start()

        self.text_win.protocol("WM_DELETE_WINDOW", self.stop_current_mode)

    def text_preview_loop(self):
        """Display video preview for text recognition"""
        while self.text_running and self.current_mode == 'text':
            ret, frame = self.cap.read()
            if not ret:
                time.sleep(0.1)
                continue

            instructions = "Press 'Capture Text' button to capture & read text aloud."
            cv2.putText(frame, instructions, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (50, 255, 255), 2)

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(rgb)
            imgtk = ImageTk.PhotoImage(img_pil)
            try:
                self.text_video_label.imgtk = imgtk
                self.text_video_label.configure(image=imgtk)
            except tk.TclError:
                break

            time.sleep(0.03)

    def capture_text(self):
        """Capture and process text from image"""
        if not self.cap or not self.cap.isOpened():
            messagebox.showerror("Camera Error", "Webcam not available.")
            return
        ret, frame = self.cap.read()
        if not ret:
            messagebox.showerror("Camera Error", "Failed to capture frame.")
            return

        log_event("Capturing text for OCR.")
        speak("Capturing text, please hold still.")

        detected_text = ""
        
        # Try Azure OCR if available
        if AZURE_AVAILABLE and self.azure_client:
            try:
                temp_path = "temp_text_capture.png"
                cv2.imwrite(temp_path, frame)
                
                with open(temp_path, "rb") as img_stream:
                    read_response = self.azure_client.read_in_stream(img_stream, raw=True)
                op_loc = read_response.headers["Operation-Location"]
                op_id = op_loc.split("/")[-1]
                
                while True:
                    result = self.azure_client.get_read_result(op_id)
                    if result.status.lower() not in ['notstarted', 'running']:
                        break
                    time.sleep(1)

                if result.status == 'succeeded':
                    for page in result.analyze_result.read_results:
                        for line in page.lines:
                            detected_text += line.text + " "
                
                try:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                except Exception:
                    pass
                    
            except Exception as e:
                log_event(f"Azure OCR failed: {e}")
                detected_text = ""

        # Fallback to Tesseract if Azure failed or not available
        if not detected_text.strip():
            try:
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                detected_text = pytesseract.image_to_string(gray)
            except Exception as e:
                log_event(f"Tesseract OCR failed: {e}")
                detected_text = ""

        if detected_text.strip():
            log_event(f"OCR detected text: {detected_text[:100]}...")
            pyperclip.copy(detected_text)  # Copy to clipboard
            
            # Clean up the text
            clean_text = detected_text.strip()
            
            # Make sure not to repeat the same text
            if clean_text != self.latest_text_spoken:
                speak(f"Detected text: {clean_text}")
                self.latest_text_spoken = clean_text
                
                # Show in UI
                self.show_text_window(clean_text)
        else:
            speak("No text detected. Please try again.")
            log_event("No text detected in captured image.")

    def show_text_window(self, text):
        """Display captured text in window"""
        text_win = tk.Toplevel(self.root)
        text_win.title("Captured Text")
        text_win.geometry("600x400")
        text_win.configure(bg=BG_COLOR)
        
        tk.Label(text_win, text="Captured Text (copied to clipboard):", 
                bg=BG_COLOR, fg=ACCENT_COLOR, font=(FONT_NAME, 14, 'bold')).pack(pady=10)
        
        text_area = scrolledtext.ScrolledText(text_win, font=(FONT_NAME, 12), height=15, width=60)
        text_area.pack(padx=20, pady=10, fill='both', expand=True)
        text_area.insert('1.0', text)
        
        tk.Button(text_win, text="Close", font=(FONT_NAME, 12),
                command=text_win.destroy, bg=ACCENT_COLOR, fg=FG_COLOR).pack(pady=15)

    # --- SOS Mode ---

    def start_sos_mode(self):
        """Start emergency SOS mode"""
        self.stop_current_mode()
        self.current_mode = 'sos'
        self.sos_mode_active = True
        self.btn_stop.config(state='normal')
        log_event("Emergency SOS mode activated. Press SPACE to send SOS.")
        speak("Emergency SOS mode activated. Press space bar to send SOS message.")
        self.update_status("SOS Mode Active")
        
        # Start SOS key listener thread
        self.sos_key_thread = threading.Thread(target=self.sos_key_listener, daemon=True)
        self.sos_key_thread.start()
        
        # Show SOS instructions window
        self.show_sos_instructions()

    def sos_key_listener(self):
        """Listen for spacebar press to trigger SOS"""
        while self.sos_mode_active and self.current_mode == 'sos':
            if keyboard.is_pressed('space'):
                self.send_sos_alert()
                # Wait to prevent multiple triggers from one press
                time.sleep(2)
            time.sleep(0.1)

    def show_sos_instructions(self):
        """Show SOS mode instructions window"""
        self.sos_win = tk.Toplevel(self.root)
        self.sos_win.title("EyeGuide AI - Emergency SOS Mode")
        self.sos_win.geometry("600x400")
        self.sos_win.configure(bg="#ff4757")  # Emergency red background
        
        frame = tk.Frame(self.sos_win, bg="#ff4757", padx=20, pady=20)
        frame.pack(fill='both', expand=True)
        
        title = tk.Label(frame, text="EMERGENCY SOS MODE", font=(FONT_NAME, 24, 'bold'),
                         fg='white', bg="#ff4757")
        title.pack(pady=15)
        
        instructions = (
            "Press SPACE BAR to send emergency SOS\n\n"
            f"SOS will be sent to: {SOS_PHONE_NUMBER}\n\n"
            "The message will include your approximate location if available.\n\n"
            "Close this window or click 'Stop SOS Mode' to deactivate."
        )
        
        tk.Label(frame, text=instructions, font=(FONT_NAME, 14),
                 fg='white', bg="#ff4757", justify='center').pack(pady=20)
        
        tk.Button(frame, text="Stop SOS Mode", font=(FONT_NAME, 14, 'bold'),
                  command=self.stop_current_mode, bg='white', fg='#ff4757',
                  activebackground='#f1f2f6', activeforeground='#ff4757').pack(pady=20)
        
        self.sos_win.protocol("WM_DELETE_WINDOW", self.stop_current_mode)

    def send_sos_alert(self):
        """Send SOS alert message via WhatsApp"""
        speak("Sending SOS alert, please wait.", priority=1)
        log_event("SOS alert triggered")
        
        try:
            # Format SOS message with location
            sos_msg = format_sos_msg()
            
            # Try to send via WhatsApp Desktop
            self.send_whatsapp_sos(sos_msg)
            
        except Exception as e:
            log_event(f"Error sending SOS: {e}")
            speak("Error sending SOS. Please try again or use manual emergency call.", priority=1)

    def send_whatsapp_sos(self, message):
        """Send SOS via WhatsApp using GUI automation"""
        if sys.platform != 'win32':
            speak("WhatsApp SOS not supported on this platform.")
            return False
            
        try:
            self.whatsapp_status = "Starting"
            log_event("Attempting to send WhatsApp SOS")
            
            # Launch WhatsApp if not already running
            if not launch_whatsapp():
                speak("Could not start WhatsApp. Please send emergency message manually.")
                return False
                
            self.whatsapp_status = "Finding window"
            
            # Find WhatsApp window
            self.whatsapp_hwnd = get_whatsapp_window()
            if not self.whatsapp_hwnd:
                log_event("Could not find WhatsApp window.")
                speak("WhatsApp window not found. Please send emergency message manually.")
                return False
                
            # Bring window to front
            win32gui.ShowWindow(self.whatsapp_hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(self.whatsapp_hwnd)
            time.sleep(1)
            
            self.whatsapp_status = "Sending"
            
            # Click new chat button (position may need adjustment)
            pyautogui.hotkey('ctrl', 'n')
            time.sleep(1)
            
            # Type phone number
            pyautogui.write(SOS_PHONE_NUMBER)
            time.sleep(1)
            pyautogui.press('enter')
            time.sleep(2)
            
            # Type and send message
            pyautogui.write(message)
            time.sleep(0.5)
            pyautogui.press('enter')
            
            self.whatsapp_status = "Sent"
            log_event("WhatsApp SOS message sent successfully")
            speak("Emergency SOS sent via WhatsApp")
            return True
            
        except Exception as e:
            log_event(f"WhatsApp SOS error: {e}")
            speak("Error sending WhatsApp SOS. Please call emergency services manually.")
            return False

    # --- Utility Methods ---

    def clear_video(self):
        """Clear the video display"""
        blank = np.zeros((CAM_HEIGHT, CAM_WIDTH, 3), dtype=np.uint8)
        blank.fill(0)  # Black image
        img_pil = Image.fromarray(blank)
        img_tk = ImageTk.PhotoImage(image=img_pil)
        self.video_label.imgtk = img_tk
        self.video_label.config(image=img_tk)
        self.root.update_idletasks()

    def stop_current_mode(self):
        """Stop the current active mode"""
        if self.current_mode == 'object':
            self.running = False
            if self.obj_thread:
                self.obj_thread.join(timeout=0.5)
                
        elif self.current_mode == 'text':
            self.text_running = False
            if hasattr(self, 'text_win') and self.text_win:
                try:
                    self.text_win.destroy()
                except tk.TclError:
                    pass
                    
        elif self.current_mode == 'sos':
            self.sos_mode_active = False
            if self.sos_key_thread:
                self.sos_key_thread.join(timeout=0.5)
            if hasattr(self, 'sos_win') and self.sos_win:
                try:
                    self.sos_win.destroy()
                except tk.TclError:
                    pass

        # Release camera
        if self.cap and self.cap.isOpened():
            self.cap.release()
            
        self.clear_video()
        self.current_mode = None
        self.btn_stop.config(state='disabled')
        self.update_status("Idle")
        log_event("Stopped all active modes.")

    def on_close(self):
        """Clean up resources and close application"""
        self.stop_current_mode()
        self.running = False
        self.text_running = False
        self.sos_mode_active = False
        
        # Stop TTS engine
        tts_queue.put(None)
        if self.tts_thread:
            self.tts_thread.join(timeout=0.5)
            
        # Release camera if still open
        if self.cap and self.cap.isOpened():
            self.cap.release()
            
        log_event("Application shutting down.")
        self.root.destroy()

# --- Main Entry Point ---

def main():
    """Main application entry point"""
    try:
        # Check for required packages
        missing_packages = []
        required_packages = {
            'opencv-python': cv2,
            'ultralytics': YOLO,
            'numpy': np,
            'pyttsx3': pyttsx3,
            'pytesseract': pytesseract,
            'pyautogui': pyautogui,
            'keyboard': keyboard,
            'requests': requests,
            'psutil': psutil,
            'pyperclip': pyperclip
        }
        
        for pkg_name, module in required_packages.items():
            if module is None:
                missing_packages.append(pkg_name)
                
        if missing_packages:
            print(f"Missing required packages: {', '.join(missing_packages)}")
            print("Please install them using pip install <package_name>")
            return
            
        # Start application
        root = tk.Tk()
        app = AppUI(root)
        
        # Center window on screen
        root.update_idletasks()
        width = root.winfo_width()
        height = root.winfo_height()
        x = (root.winfo_screenwidth() // 2) - (width // 2)
        y = (root.winfo_screenheight() // 2) - (height // 2)
        root.geometry(f'{width}x{height}+{x}+{y}')
        
        # Set application icon if available
        try:
            root.iconbitmap("eyeguide_icon.ico")
        except tk.TclError:
            pass
            
        # Download YOLO model if needed
        if not os.path.exists('yolov8n.pt'):
            log_event("YOLO model not found. Attempting to download...")
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", "ultralytics"], 
                              stdout=subprocess.PIPE, check=True)
                # YOLO will download the model on first use
            except Exception as e:
                log_event(f"Failed to download YOLO model: {e}")
                
        speak("EyeGuide AI Enhanced started. Please select a mode.")
        log_event("Application started successfully.")
        
        root.mainloop()
        
    except Exception as e:
        print(f"Application error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()