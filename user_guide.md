# EyeGuide AI Enhanced: User Guide

This guide provides detailed instructions on how to effectively use the EyeGuide AI Enhanced application and get the most out of its features.

## Table of Contents
1. [Getting Started](#getting-started)
2. [Application Interface](#application-interface)
3. [Advanced Object Detection](#advanced-object-detection)
4. [Text Recognition and Reading](#text-recognition-and-reading)
5. [Emergency SOS Mode](#emergency-sos-mode)
6. [Customization](#customization)
7. [Tips and Best Practices](#tips-and-best-practices)
8. [Keyboard Shortcuts](#keyboard-shortcuts)
9. [FAQ](#faq)

## Getting Started

After installing EyeGuide AI Enhanced (see INSTALLATION_GUIDE.md), follow these steps to start using the application:

1. Launch the application by running `python eyeguide_ai_enhanced.py` in your terminal/command prompt
2. When the application starts, you'll see the main interface with three main modes to choose from
3. Ensure your webcam is properly connected and accessible
4. Check that your speakers or headphones are working correctly

## Application Interface

The EyeGuide AI Enhanced interface is designed to be straightforward and accessible:

![Main Interface Description](https://via.placeholder.com/800x600/121212/00cec9?text=EyeGuide+AI+Interface)

- **Left Side:** Mode selection buttons
  - Advanced Object Detection
  - Text Recognition and Reading
  - Emergency SOS Mode
  - Stop Current Mode
  - Exit Application

- **Right Side:** 
  - Video display from camera
  - Status indicator
  - Application logs

## Advanced Object Detection

This mode identifies objects in your environment and provides voice feedback about what's around you.

### How to Use:

1. Click the "Advanced Object Detection" button
2. The application will activate your camera and begin detecting objects
3. When objects are detected, the application will:
   - Display the objects with bounding boxes on screen
   - Announce the objects and their approximate distances through voice
   - Update the information every 3 seconds
   - Focus on announcing new objects or significant changes in distance

### Tips for Object Detection:

- Good lighting improves detection accuracy
- The detection range works best for objects 1-5 meters away
- The application can detect common objects like people, furniture, appliances, etc.
- Detection works best when objects are fully visible and not obscured
- If there are too many objects, the application will prioritize announcing the closest ones

## Text Recognition and Reading

This mode allows you to capture and read text from documents, books, signs, labels, and screens.

### How to Use:

1. Click the "Text Recognition and Reading" button
2. A new window will open with camera preview
3. Position the camera to frame the text you want to read
4. Click the "Capture Text" button
5. The application will:
   - Process the image to find text
   - Read the detected text aloud
   - Display the text in a window
   - Copy the text to your clipboard for use in other applications

### Tips for Text Recognition:

- Hold the camera steady when capturing text
- Ensure the text is well-lit and has good contrast
- Position the camera so text is straight and fully visible
- For multicolumn documents, capture one column at a time
- Larger text tends to be recognized more accurately
- If using Azure OCR, recognition quality will be higher but requires internet connection

## Emergency SOS Mode

This mode allows you to quickly send emergency messages with your location to a predefined contact.

### How to Use:

1. Click the "Emergency SOS Mode" button
2. The application will activate SOS mode and display instructions
3. In case of emergency, press the SPACE BAR
4. The application will:
   - Determine your approximate location
   - Generate an SOS message with location link
   - Automatically open WhatsApp Desktop
   - Send the message to your emergency contact
   - Provide voice confirmation when completed

### Setting Up Emergency Contact:

Before using SOS mode, make sure to set up your emergency contact:

1. Open `eyeguide_ai_enhanced.py` in a text editor
2. Find the line: `SOS_PHONE_NUMBER = "8073320798"`
3. Replace with your emergency contact's number (include country code)
4. Save the file and restart the application

### Important Notes on SOS Mode:

- Test the SOS feature before relying on it in an emergency
- The WhatsApp automation works best on Windows
- Make sure WhatsApp Desktop is installed and you're logged in
- Location accuracy depends on your internet connection
- The application must have permission to control other applications

## Customization

You can customize various aspects of EyeGuide AI Enhanced by modifying the following settings in the code:

### Appearance:

```python
# UI Colors & Fonts
BG_COLOR = "#121212"         # Background color
FG_COLOR = "#f5f6fa"         # Text color
ACCENT_COLOR = "#00cec9"     # Button color
FONT_NAME = "Segoe UI"       # Font
```

### Performance Settings:

```python
# Camera settings
CAM_WIDTH = 640             # Camera preview width
CAM_HEIGHT = 480            # Camera preview height

# Detection settings
YOLO_CONF_THRESHOLD = 0.4   # Confidence threshold (0-1)
OBJECT_DETECTION_INTERVAL = 3.0  # Seconds between detections
```

### Text-to-Speech Configuration:

```python
# In the tts_worker function
engine.setProperty('rate', 150)  # Speech speed (words per minute)
```

## Tips and Best Practices

### For Best Performance:

1. **Lighting Matters**: Ensure adequate lighting for both object detection and text recognition
2. **Camera Positioning**: Mount or position the camera at eye level for most natural detection
3. **Regular Updates**: Keep Python packages updated for improved performance
4. **Background Noise**: Use headphones in noisy environments to hear announcements better
5. **Battery Life**: When using on a laptop, consider connecting to power for extended sessions

### For Visually Impaired Users:

1. **Screen Reader Compatibility**: The application works well with most screen readers
2. **Voice Rate**: Adjust the speech rate in the code to match your listening preference
3. **Keyboard Navigation**: Use the Tab key to navigate between buttons
4. **Practice Mode**: Spend time in a familiar environment to learn how the object detection describes your surroundings

### For Caregivers and Assistants:

1. **Initial Setup**: Help with installation and configuration of emergency contact
2. **Environment Mapping**: Walk through familiar environments to help the user understand how objects are described
3. **Regular Testing**: Periodically test the SOS function (without actually sending messages)

## Keyboard Shortcuts

The application supports these keyboard shortcuts:

- **SPACE BAR**: Trigger SOS message (when in SOS mode)
- **ESC**: Stop current mode (alternative to clicking "Stop Current Mode")
- **CTRL+Q**: Exit application

## FAQ

### Q: How accurate is the distance estimation?
**A:** The distance estimation is approximate, with accuracy of about ±15% at 1-3 meters. It is based on the object's apparent size in the frame and works best for known objects of standard sizes.

### Q: Does the application require internet access?
**A:** Basic object detection and text recognition work offline. The Azure OCR (if enabled) and location services for SOS require internet connectivity.

### Q: Can I use the application on a tablet or mobile device?
**A:** The current version is designed for desktop/laptop computers. A mobile version would require adaptation of the code.

### Q: How can I improve text recognition accuracy?
**A:** Enable Azure OCR for better accuracy, ensure good lighting, hold the camera steady, and position text to fill most of the frame.

### Q: The application is not detecting some objects correctly. Why?
**A:** The object detection model (YOLOv8) can detect common objects but may struggle with unusual or partially visible items. Good lighting and positioning can help.

### Q: Can I customize which objects are announced?
**A:** Yes, but it requires modifying the code. Look for the `object_detection_loop` function to add filters for specific object classes.

### Q: Why does the SOS feature only work with WhatsApp?
**A:** The current implementation uses WhatsApp Desktop due to its widespread availability. Future versions could support other messaging platforms.

### Q: Is my data private when using this application?
**A:** Yes. The application processes most data locally on your computer. If using Azure OCR, the images are sent to Microsoft's servers for processing according to their privacy policy.

### Q: How can I report bugs or suggest improvements?
**A:** Please create an issue on the GitHub repository or contact the developer directly.

---

For additional help or feedback, please contact the development team or visit the project's GitHub page.