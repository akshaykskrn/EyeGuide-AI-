import threading
import time
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib
matplotlib.use('Agg')  # Use Agg backend for non-interactive environments
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk
from collections import Counter
import io
import os

# Add these functions to the AppUI class:

def initialize_confusion_matrix(self):
    """Initialize confusion matrix tracking data"""
    # Define common objects expected to be detected
    self.common_objects = [
        'person', 'bicycle', 'car', 'motorcycle', 'bus', 'truck', 
        'chair', 'couch', 'bed', 'dining table', 'laptop', 'cell phone', 'book'
    ]
    
    # Create empty confusion matrix
    self.confusion_data = {
        'ground_truth': [],  # Will be filled with ground truth labels
        'predictions': []    # Will be filled with predicted labels
    }
    
    # Frame for buttons to manually label "ground truth"
    self.last_detected_objects = []
    self.current_ground_truth = None
    
    # Initialize log of detections for analysis
    self.detection_log = []
    
    log_event("Confusion matrix tracking initialized")

def open_confusion_matrix_window(self):
    """Open window to display and manage confusion matrix"""
    if hasattr(self, 'cm_window') and self.cm_window is not None:
        try:
            self.cm_window.destroy()
        except tk.TclError:
            pass
    
    self.cm_window = tk.Toplevel(self.root)
    self.cm_window.title("EyeGuide AI - Detection Analysis")
    self.cm_window.geometry("900x700")
    self.cm_window.configure(bg=BG_COLOR)
    
    # Frame for content
    main_frame = tk.Frame(self.cm_window, bg=BG_COLOR)
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Add title and explanation
    title = tk.Label(main_frame, text="Object Detection Performance Analysis", 
                   font=(FONT_NAME, 18, 'bold'), fg=ACCENT_COLOR, bg=BG_COLOR)
    title.pack(pady=(0, 15))
    
    description = tk.Label(main_frame, text=(
        "This tool helps analyze the performance of object detection. "
        "You can either record ground truth vs predictions manually or generate a simulated confusion matrix."
    ), font=(FONT_NAME, 10), fg=FG_COLOR, bg=BG_COLOR, wraplength=800, justify='center')
    description.pack(pady=(0, 20))
    
    # Buttons frame
    btn_frame = tk.Frame(main_frame, bg=BG_COLOR)
    btn_frame.pack(pady=10)
    
    btn_style = {'font': (FONT_NAME, 12), 'width': 25, 'height': 1, 
                'bg': ACCENT_COLOR, 'fg': FG_COLOR, 'bd': 0, 'padx': 10, 'pady': 5}
    
    record_btn = tk.Button(btn_frame, text="Record Ground Truth", 
                         command=self.show_ground_truth_panel, **btn_style)
    record_btn.grid(row=0, column=0, padx=10, pady=10)
    
    generate_btn = tk.Button(btn_frame, text="Generate Simulated Matrix", 
                           command=self.generate_simulated_matrix, **btn_style)
    generate_btn.grid(row=0, column=1, padx=10, pady=10)
    
    clear_btn = tk.Button(btn_frame, text="Clear Recorded Data", 
                        command=self.clear_confusion_data, **btn_style)
    clear_btn.grid(row=1, column=0, padx=10, pady=10)
    
    view_btn = tk.Button(btn_frame, text="View Current Matrix", 
                       command=self.show_current_matrix, **btn_style)
    view_btn.grid(row=1, column=1, padx=10, pady=10)
    
    # Frame for detection statistics
    stats_frame = tk.LabelFrame(main_frame, text="Detection Statistics", 
                             bg=BG_COLOR, fg=ACCENT_COLOR, font=(FONT_NAME, 12, 'bold'),
                             padx=15, pady=15)
    stats_frame.pack(fill="both", expand=True, pady=20)
    
    # Statistical metrics
    self.stats_labels = {
        'total': tk.StringVar(value="Total Detections: 0"),
        'accuracy': tk.StringVar(value="Accuracy: N/A"),
        'common': tk.StringVar(value="Most Common Object: N/A"),
        'misclassified': tk.StringVar(value="Most Misclassified: N/A")
    }
    
    for i, (key, var) in enumerate(self.stats_labels.items()):
        lbl = tk.Label(stats_frame, textvariable=var, bg=BG_COLOR, fg=FG_COLOR, 
                     font=(FONT_NAME, 11), anchor='w')
        lbl.pack(anchor='w', pady=5)
    
    # Frame for the confusion matrix image
    self.cm_image_frame = tk.Frame(main_frame, bg=BG_COLOR)
    self.cm_image_frame.pack(fill="both", expand=True, pady=10)
    
    self.cm_image_label = tk.Label(self.cm_image_frame, bg=BG_COLOR)
    self.cm_image_label.pack(fill="both", expand=True)
    
    self.update_confusion_stats()

def show_ground_truth_panel(self):
    """Show panel for recording ground truth vs detected objects"""
    if hasattr(self, 'gt_window') and self.gt_window is not None:
        try:
            self.gt_window.destroy()
        except tk.TclError:
            pass
    
    self.gt_window = tk.Toplevel(self.root)
    self.gt_window.title("Record Ground Truth")
    self.gt_window.geometry("600x500")
    self.gt_window.configure(bg=BG_COLOR)
    
    # Instructions
    instructions = tk.Label(self.gt_window, 
                          text="Select the ACTUAL object in view, then click 'Record'",
                          font=(FONT_NAME, 12, 'bold'), fg=ACCENT_COLOR, bg=BG_COLOR)
    instructions.pack(pady=15)
    
    # Object selection frame
    sel_frame = tk.Frame(self.gt_window, bg=BG_COLOR)
    sel_frame.pack(pady=10)
    
    # Ground truth selection
    gt_label = tk.Label(sel_frame, text="Actual Object (Ground Truth):", 
                      bg=BG_COLOR, fg=FG_COLOR, font=(FONT_NAME, 11))
    gt_label.grid(row=0, column=0, padx=10, pady=10, sticky='w')
    
    self.gt_var = tk.StringVar(value=self.common_objects[0])
    gt_combo = ttk.Combobox(sel_frame, textvariable=self.gt_var, 
                          values=self.common_objects, width=20)
    gt_combo.grid(row=0, column=1, padx=10, pady=10)
    
    # Current detection label
    detect_label = tk.Label(sel_frame, text="Currently Detected:", 
                          bg=BG_COLOR, fg=FG_COLOR, font=(FONT_NAME, 11))
    detect_label.grid(row=1, column=0, padx=10, pady=10, sticky='w')
    
    self.detect_var = tk.StringVar(value="None")
    detect_text = tk.Label(sel_frame, textvariable=self.detect_var, 
                         bg='#222222', fg=ACCENT_COLOR, font=(FONT_NAME, 11),
                         width=25, padx=5, pady=5)
    detect_text.grid(row=1, column=1, padx=10, pady=10)
    
    # Record button
    record_btn = tk.Button(self.gt_window, text="Record This Pair", 
                         command=self.record_confusion_pair,
                         bg=ACCENT_COLOR, fg=FG_COLOR, font=(FONT_NAME, 12),
                         width=20, bd=0)
    record_btn.pack(pady=20)
    
    # Display recent records
    records_frame = tk.LabelFrame(self.gt_window, text="Recent Records", 
                               bg=BG_COLOR, fg=ACCENT_COLOR, font=(FONT_NAME, 11),
                               padx=10, pady=10)
    records_frame.pack(fill="both", expand=True, padx=20, pady=10)
    
    self.records_text = tk.Text(records_frame, bg="#222222", fg=FG_COLOR, 
                              font=(FONT_NAME, 10), height=10, wrap="word")
    self.records_text.pack(fill="both", expand=True)
    
    # Start a thread to update detected objects
    if self.current_mode == 'object' and self.running:
        self.gt_update_thread = threading.Thread(target=self.update_detection_for_gt, daemon=True)
        self.gt_update_thread.start()
    else:
        tk.messagebox.showwarning("Warning", 
                               "Object detection is not running. Start object detection first.")

def update_detection_for_gt(self):
    """Update the currently detected objects for ground truth comparison"""
    while hasattr(self, 'gt_window') and self.gt_window.winfo_exists():
        if self.current_mode == 'object' and self.running and hasattr(self, 'last_spoken_objects'):
            if self.last_spoken_objects:
                # Get the first object (most prominent)
                detected = list(self.last_spoken_objects.keys())
                if detected:
                    self.last_detected_objects = detected
                    self.detect_var.set(detected[0])
            else:
                self.detect_var.set("None detected")
        time.sleep(0.5)

def record_confusion_pair(self):
    """Record a ground truth vs prediction pair"""
    ground_truth = self.gt_var.get()
    prediction = self.detect_var.get()
    
    if prediction == "None" or prediction == "None detected":
        tk.messagebox.showinfo("No Detection", 
                            "No object currently detected. Please try when an object is visible.")
        return
    
    # Add to confusion data
    self.confusion_data['ground_truth'].append(ground_truth)
    self.confusion_data['predictions'].append(prediction)
    
    # Add to records display
    record = f"Ground Truth: {ground_truth} | Predicted: {prediction}\n"
    self.records_text.insert("1.0", record)
    
    # Log event
    log_event(f"Recorded confusion pair: GT={ground_truth}, Pred={prediction}")
    
    # Update stats
    self.update_confusion_stats()

def clear_confusion_data(self):
    """Clear all recorded confusion matrix data"""
    if tk.messagebox.askyesno("Clear Data", 
                           "Are you sure you want to clear all recorded detection data?"):
        self.confusion_data = {'ground_truth': [], 'predictions': []}
        self.detection_log = []
        self.update_confusion_stats()
        log_event("Cleared confusion matrix data")

def generate_simulated_matrix(self):
    """Generate a simulated confusion matrix for demonstration"""
    # Select subset of objects to use
    objects = self.common_objects[:8]  # Use first 8 objects for cleaner visualization
    
    # Generate random confusion data with bias toward correct classification
    n_samples = 100
    np.random.seed(42)  # For reproducibility
    
    # Generate ground truth labels
    ground_truth = np.random.choice(objects, n_samples)
    
    # Generate predictions with 70% accuracy
    predictions = []
    for gt in ground_truth:
        if np.random.random() < 0.7:  # 70% correct
            predictions.append(gt)
        else:  # 30% incorrect
            other_objects = [obj for obj in objects if obj != gt]
            predictions.append(np.random.choice(other_objects))
    
    # Store in our confusion data
    self.confusion_data = {
        'ground_truth': ground_truth.tolist(),
        'predictions': predictions
    }
    
    # Update stats and show matrix
    self.update_confusion_stats()
    self.show_current_matrix()
    log_event("Generated simulated confusion matrix data")

def update_confusion_stats(self):
    """Update statistics based on current confusion data"""
    if not self.confusion_data['ground_truth']:
        for var in self.stats_labels.values():
            var.set(var.get().split(':')[0] + ': N/A')
        return
    
    # Total number of detections
    total = len(self.confusion_data['ground_truth'])
    self.stats_labels['total'].set(f"Total Detections: {total}")
    
    # Calculate accuracy
    correct = sum(gt == pred for gt, pred in 
                 zip(self.confusion_data['ground_truth'], self.confusion_data['predictions']))
    accuracy = correct / total if total > 0 else 0
    self.stats_labels['accuracy'].set(f"Accuracy: {accuracy:.2%}")
    
    # Most common object
    if self.confusion_data['ground_truth']:
        common_counter = Counter(self.confusion_data['ground_truth'])
        most_common = common_counter.most_common(1)[0]
        self.stats_labels['common'].set(f"Most Common Object: {most_common[0]} ({most_common[1]} occurrences)")
    
    # Most misclassified object
    misclassified = {}
    for gt, pred in zip(self.confusion_data['ground_truth'], self.confusion_data['predictions']):
        if gt != pred:
            misclassified[gt] = misclassified.get(gt, 0) + 1
    
    if misclassified:
        most_misclassified = max(misclassified.items(), key=lambda x: x[1])
        self.stats_labels['misclassified'].set(
            f"Most Misclassified: {most_misclassified[0]} ({most_misclassified[1]} times)"
        )
    else:
        self.stats_labels['misclassified'].set("Most Misclassified: None")

def show_current_matrix(self):
    """Create and display the confusion matrix visualization"""
    if not self.confusion_data['ground_truth']:
        tk.messagebox.showinfo("No Data", 
                            "No confusion matrix data available. Record some data first.")
        return
    
    # Get unique labels from both ground truth and predictions
    labels = sorted(set(self.confusion_data['ground_truth'] + self.confusion_data['predictions']))
    
    # If too many labels, limit to the most common ones
    if len(labels) > 10:
        combined = self.confusion_data['ground_truth'] + self.confusion_data['predictions']
        counter = Counter(combined)
        labels = [item[0] for item in counter.most_common(10)]
    
    # Create the confusion matrix
    n_labels = len(labels)
    cm = np.zeros((n_labels, n_labels), dtype=int)
    
    # Fill the confusion matrix
    label_to_idx = {label: i for i, label in enumerate(labels)}
    for gt, pred in zip(self.confusion_data['ground_truth'], self.confusion_data['predictions']):
        if gt in labels and pred in labels:
            i = label_to_idx[gt]
            j = label_to_idx[pred]
            cm[i, j] += 1
    
    # Create the figure for the confusion matrix
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
               xticklabels=labels, yticklabels=labels)
    plt.ylabel('Ground Truth')
    plt.xlabel('Predicted')
    plt.title('Object Detection Confusion Matrix')
    
    # Save figure to buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    
    # Convert to PIL Image and then to ImageTk
    img = ImageTk.PhotoImage(Image.open(buf))
    self.cm_image_label.configure(image=img)
    self.cm_image_label.image = img
    
    plt.close()  # Close the figure to free memory

def add_confusion_matrix_button(self):
    """Add confusion matrix button to the UI"""
    if not hasattr(self, 'btn_confusion_matrix'):
        self.initialize_confusion_matrix()
        
        # Add button to left menu
        left_menu = None
        for child in self.root.winfo_children():
            if isinstance(child, tk.Frame):
                for subchild in child.winfo_children():
                    if isinstance(subchild, tk.Frame) and subchild.winfo_ismapped():
                        # This is likely the left menu frame
                        left_menu = subchild
                        break
        
        if left_menu:
            # Place above the Exit button
            btn_style = {'font': (FONT_NAME, 14), 'width': 28, 'height': 2, 
                       'bg': ACCENT_COLOR, 'fg': FG_COLOR, 'activebackground': '#008080', 
                       'bd': 0, 'cursor': 'hand2'}
            
            self.btn_confusion_matrix = tk.Button(
                left_menu,
                text="Detection Analytics",
                command=self.open_confusion_matrix_window,
                **btn_style
            )
            
            # Insert before the Exit button (which is the last button)
            self.btn_confusion_matrix.pack(side="bottom", pady=20, before=left_menu.winfo_children()[-1])
            
            log_event("Added confusion matrix analysis button to UI")

# Add this function to AppUI.__init__ to add the confusion matrix functionality
# self.add_confusion_matrix_button()

# Add this to the start_object_detection method:
# self.initialize_confusion_matrix()