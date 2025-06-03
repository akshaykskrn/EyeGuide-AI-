# EyeGuide AI Enhanced

## Description
EyeGuide AI Enhanced is an assistive technology application designed to help visually impaired users navigate their environment and interact with text through advanced computer vision techniques. The application combines real-time object detection, text recognition, and emergency assistance features in an accessible interface.

## Features

### 1. Advanced Object Detection
- Real-time detection and identification of objects in the user's environment
- Distance estimation for detected objects
- Voice announcements of objects and their approximate distances
- Continuous monitoring with configurable detection intervals

### 2. Text Recognition and Reading
- Captures text from the camera view
- Uses OCR (Optical Character Recognition) to extract text from images
- Reads detected text aloud using text-to-speech
- Automatically copies recognized text to clipboard
- Supports both local (Tesseract) and cloud-based (Azure) text recognition

### 3. Emergency SOS Mode
- Quick WhatsApp emergency messaging with a simple space bar press
- Automatically includes location information in emergency messages
- Configurable emergency contact number
- Visual and audio confirmation of SOS activation

## System Requirements

### Hardware
- Webcam (built-in or external)
- Microphone and speakers for voice feedback
- Windows computer (preferred for full functionality)

### Software Dependencies
- Python 3.7 or higher
- OpenCV (computer vision)
- Ultralytics YOLO (object detection)
- PyTesseract (text recognition)
- pyttsx3 (text-to-speech)
- Other Python packages: numpy, pyautogui, keyboard, requests, psutil, pyperclip, win32gui (on Windows)

## Installation

1. Clone or download this repository:
```bash
git clone https://github.com/yourusername/eyeguide-ai-enhanced.git
cd eyeguide-ai-enhanced
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Install Tesseract OCR:
   - **Windows**: Download and install from [Tesseract GitHub releases](https://github.com/UB-Mannheim/tesseract/wiki)
   - **macOS**: `brew install tesseract`
   - **Linux**: `sudo apt-get install tesseract-ocr`

4. (Optional) Set up Azure Computer Vision:
   - Create an Azure account and a Computer Vision resource
   - Install the Azure SDK: `pip install azure-cognitiveservices-vision-computervision`
   - Update the `AZURE_ENDPOINT` and `AZURE_KEY` variables in the code with your credentials

5. For WhatsApp integration (Windows only):
   - Install WhatsApp Desktop application

## Usage

1. Run the application:
```bash
python eyeguide_ai_enhanced.py
```

2. Application Modes:

   - **Advanced Object Detection**:
     - Press the "Advanced Object Detection" button
     - The application will identify objects in view and announce them with distances
     - Detection results will also be visually displayed on screen

   - **Text Recognition and Reading**:
     - Press the "Text Recognition and Reading" button
     - Point camera at text you want to read
     - Press "Capture Text" button to scan and read text aloud
     - Recognized text will be displayed and copied to clipboard

   - **Emergency SOS Mode**:
     - Press the "Emergency SOS Mode" button
     - In emergency situations, press the SPACE bar
     - The application will send an SOS message with your location via WhatsApp

3. To stop any active mode, press the "Stop Current Mode" button

## Configuration

You can configure the following settings in the code:

- `SOS_PHONE_NUMBER`: Emergency contact number (include country code)
- `OBJECT_DETECTION_INTERVAL`: Time between object detection announcements (seconds)
- `YOLO_CONF_THRESHOLD`: Confidence threshold for object detection (0.0-1.0)
- `DISTANCE_COEFF`: Calibration coefficient for distance estimation

## Accessibility Features

- High-contrast user interface
- Text-to-speech announcements
- Simple keyboard shortcuts
- Automatic copying of recognized text to clipboard

## Troubleshooting

### Camera Issues
- Ensure your webcam is properly connected
- Check if other applications are using the camera
- Try restarting the application

### Text Recognition Problems
- Ensure adequate lighting for better text recognition
- Hold the camera steady when capturing text
- For Windows users, verify Tesseract is correctly installed and the path is set

### WhatsApp Integration
- Ensure WhatsApp Desktop is installed
- The application may need to be run with administrator privileges
- Allow the application through Windows security/firewall if prompted

## Log Files

The application creates a log file (`eyeguide_ai_enhanced_log.txt`) that records all operations and can be helpful for troubleshooting.

## License

[Akshay]

## Disclaimer

This application is intended as an assistive technology and should not be solely relied upon in emergency situations. Always have backup safety measures in place.

## Contributing

Contributions to improve EyeGuide AI Enhanced are welcome. Please feel free to submit a pull request or open an issue to discuss proposed changes or report bugs.