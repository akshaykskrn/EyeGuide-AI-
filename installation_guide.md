# EyeGuide AI Enhanced: Installation Guide

This document provides detailed step-by-step instructions for installing and setting up the EyeGuide AI Enhanced application on various operating systems.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Windows Installation](#windows-installation)
3. [macOS Installation](#macos-installation)
4. [Linux Installation](#linux-installation)
5. [Azure Setup (Optional)](#azure-setup-optional)
6. [Troubleshooting](#troubleshooting)

## Prerequisites

Before installing EyeGuide AI Enhanced, ensure your system meets these requirements:

- **Hardware:**
  - Webcam (built-in or external USB)
  - Microphone and speakers/headphones
  - At least 4GB RAM (8GB recommended)
  - At least 2GB free disk space

- **Software:**
  - Python 3.7 or newer
  - Git (for cloning the repository)
  - WhatsApp Desktop (for SOS feature on Windows)

## Windows Installation

1. **Install Python:**
   - Download the latest Python installer from [python.org](https://www.python.org/downloads/windows/)
   - During installation, make sure to check "Add Python to PATH"
   - Verify installation by opening Command Prompt and typing:
     ```
     python --version
     ```

2. **Install Git:**
   - Download and install Git from [git-scm.com](https://git-scm.com/download/win)
   - Use default settings during installation

3. **Install Tesseract OCR:**
   - Download the Tesseract installer from [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
   - Run the installer and use the default installation path (`C:\Program Files\Tesseract-OCR\`)
   - Add Tesseract to your PATH environment variable:
     - Search for "Environment Variables" in Windows search
     - Under System Variables, find "Path" and click Edit
     - Add `C:\Program Files\Tesseract-OCR\` as a new entry
     - Click OK to save

4. **Install WhatsApp Desktop (for SOS feature):**
   - Download from [WhatsApp Desktop](https://www.whatsapp.com/download)
   - Complete the installation and sign in to your account

5. **Clone the Repository:**
   - Open Command Prompt
   - Navigate to your desired installation directory:
     ```
     cd C:\Users\YourUsername\Documents
     ```
   - Clone the repository:
     ```
     git clone https://github.com/yourusername/eyeguide-ai-enhanced.git
     cd eyeguide-ai-enhanced
     ```

6. **Create a Virtual Environment (recommended):**
   ```
   python -m venv venv
   venv\Scripts\activate
   ```

7. **Install Required Python Packages:**
   ```
   pip install -r requirements.txt
   ```

8. **Download YOLOv8 Model:**
   - The model will be downloaded automatically on first run, or you can manually download it:
   ```
   python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
   ```

9. **Run the Application:**
   ```
   python eyeguide_ai_enhanced.py
   ```

## macOS Installation

1. **Install Homebrew (if not already installed):**
   ```
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. **Install Python:**
   ```
   brew install python
   ```

3. **Install Git:**
   ```
   brew install git
   ```

4. **Install Tesseract:**
   ```
   brew install tesseract
   ```

5. **Clone the Repository:**
   ```
   cd ~/Documents
   git clone https://github.com/yourusername/eyeguide-ai-enhanced.git
   cd eyeguide-ai-enhanced
   ```

6. **Create a Virtual Environment (recommended):**
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```

7. **Install Required Python Packages:**
   ```
   pip install -r requirements.txt
   ```
   
   > **Note:** The WhatsApp SOS feature is primarily designed for Windows. On macOS, this feature will have limited functionality.

8. **Run the Application:**
   ```
   python eyeguide_ai_enhanced.py
   ```

## Linux Installation

These instructions are for Ubuntu/Debian-based distributions. Adjust package manager commands for other distributions.

1. **Update Package Lists:**
   ```
   sudo apt update
   ```

2. **Install Python and Required System Packages:**
   ```
   sudo apt install python3 python3-pip python3-venv git
   sudo apt install python3-tk python3-dev
   sudo apt install libgl1-mesa-glx # For OpenCV
   ```

3. **Install Tesseract OCR:**
   ```
   sudo apt install tesseract-ocr
   ```

4. **Clone the Repository:**
   ```
   cd ~/Documents
   git clone https://github.com/yourusername/eyeguide-ai-enhanced.git
   cd eyeguide-ai-enhanced
   ```

5. **Create a Virtual Environment (recommended):**
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```

6. **Install Required Python Packages:**
   ```
   pip install -r requirements.txt
   ```
   
   > **Note:** On Linux, the WhatsApp SOS feature will have limited functionality, as it's primarily designed for Windows.

7. **Run the Application:**
   ```
   python eyeguide_ai_enhanced.py
   ```

## Azure Setup (Optional)

For enhanced text recognition, you can set up Azure Computer Vision:

1. **Create an Azure Account:**
   - Sign up at [azure.microsoft.com](https://azure.microsoft.com/free/)

2. **Create a Computer Vision Resource:**
   - Go to the Azure Portal
   - Click "Create a resource"
   - Search for "Computer Vision"
   - Click "Create"
   - Fill in the required information
   - Select your pricing tier (F0 Free tier is available)
   - Complete the creation process

3. **Get Your API Key and Endpoint:**
   - Go to your Computer Vision resource
   - Under "Resource Management", select "Keys and Endpoint"
   - Copy Key 1 and the Endpoint URL

4. **Update the Application:**
   - Open `eyeguide_ai_enhanced.py` in a text editor
   - Find the following lines:
     ```python
     AZURE_ENDPOINT = "https://eyeguideai2025.cognitiveservices.azure.com/"
     AZURE_KEY = "CSiHUHZYTZKcj8iTiwyKmzic5eljvaQ1slyANS24QsSzVpojIJIdJQQJ99BDACYeBjFXJ3w3AAAFACOG1o1R"
     ```
   - Replace with your actual endpoint and key
   - Save the file

5. **Install Azure SDK:**
   ```
   pip install azure-cognitiveservices-vision-computervision msrest
   ```

## Troubleshooting

### Camera Issues
- **Problem**: Application fails to access webcam
  - **Solution**: Check if another application is using the camera
  - **Solution**: Ensure proper permissions are granted
  - **Solution**: Try specifying a different camera index:
    ```python
    # Change this line in eyeguide_ai_enhanced.py:
    self.cap = cv2.VideoCapture(1)  # Try 1 instead of 0
    ```

### Tesseract OCR Issues
- **Problem**: Application can't find Tesseract
  - **Windows Solution**: Verify the path in the code matches your installation:
    ```python
    # Update this line in eyeguide_ai_enhanced.py:
    pytesseract.pytesseract.tesseract_cmd = r'C:\Path\To\Tesseract-OCR\tesseract.exe'
    ```
  - **Linux/macOS Solution**: Ensure tesseract is in your PATH:
    ```bash
    which tesseract
    ```

### YOLO Model Issues
- **Problem**: Error loading YOLO model
  - **Solution**: Manually download the model:
    ```
    # Create a models directory if it doesn't exist
    mkdir -p models
    
    # Download YOLOv8n model
    wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt -O yolov8n.pt
    ```

### Python Dependency Issues
- **Problem**: Missing dependencies or version conflicts
  - **Solution**: Try installing packages individually:
    ```
    pip install opencv-python ultralytics numpy pyttsx3 pytesseract pyautogui keyboard
    pip install requests psutil pyperclip pillow
    pip install pywin32  # Windows only
    ```

### WhatsApp Automation Issues
- **Problem**: WhatsApp automation not working
  - **Solution**: Update the WhatsApp path in code to match your installation
  - **Solution**: Run the application as Administrator
  - **Solution**: Make sure WhatsApp Desktop is installed (not WhatsApp Web)

For any other issues, please check the log file (`eyeguide_ai_enhanced_log.txt`) for detailed error messages.