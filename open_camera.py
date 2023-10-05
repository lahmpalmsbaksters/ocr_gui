import cv2
import os
import time
import urllib3
from urllib3 import encode_multipart_formdata
import requests
import tkinter as tk
import threading
from PIL import Image, ImageTk


# def show_video():
#     camera_url = 'rtsp://admin:islabac123@10.10.2.112/Streaming/Channels/0101'
#     # Change the argument to a video file path or camera URL if needed
#     cap = cv2.VideoCapture(camera_url)

#     while True:
#         ret, frame = cap.read()

#         if not ret:
#             break

#         # Convert the OpenCV BGR frame to RGB format
#         frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

#         # Convert the frame to a format suitable for displaying in Tkinter
#         img = Image.fromarray(frame_rgb)
#         img = ImageTk.PhotoImage(image=img)

#         # Update the video label widget with the new frame
#         video_label.config(image=img)
#         video_label.image = img

#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break

#     cap.release()
#     cv2.destroyAllWindows()


def update_gui(text_list):
    text_widget.config(state=tk.NORMAL)
    text_widget.delete(1.0, tk.END)  # Clear previous text
    # text_widget.insert(tk.END, response_text)
    for text in text_list:
        # text_widget.insert(tk.END, text + '\n')  # Add each text and a newline
        text_width = len(text)
        spaces = (text_widget.winfo_width() - text_width) // 2
        centered_text = ' ' * spaces + text + '\n'
        text_widget.insert(tk.END, centered_text)
    text_widget.tag_configure("center", justify="center")
    text_widget.tag_add("center", "1.0", "end")
    text_widget.config(state=tk.DISABLED)


def process_api_request():
    # Replace 'your_camera_url' with the URL of your IP camera stream
    camera_url = 'rtsp://admin:islabac123@10.10.2.112/Streaming/Channels/0101'
    api_endpoint = 'http://18.141.185.135:5000/ocr_file'
    http = urllib3.PoolManager()

    # Create a VideoCapture object
    # cap = cv2.VideoCapture(camera_url)

    cap = cv2.VideoCapture(0)
    # Check if the camera is opened successfully
    if not cap.isOpened():
        print("Error: Could not open camera.")
    else:
        capture_interval = 10  # 5 minutes in seconds
        last_capture_time = time.time()

        # Create a folder to store captured images
        output_folder = "captured_images"
        if not os.path.exists(output_folder):
            os.mkdir(output_folder)

        while True:
            # Read a frame from the camera
            ret, frame = cap.read()

            if not ret:
                print("Error: Could not read frame.")
                break

            # Display the frame
            # cv2.imshow('IP Camera Feed', frame)

            # Capture an image every 5 minutes
            current_time = time.time()
            if current_time - last_capture_time >= capture_interval:
                image_filename = os.path.join(
                    output_folder, f"captured_image_{int(current_time)}.jpg")
                cv2.imwrite(image_filename, frame)
                print(f"Image captured: {image_filename}")
                last_capture_time = current_time
                file_paths = [os.path.join(output_folder, filename) for filename in os.listdir(
                    output_folder) if os.path.isfile(os.path.join(output_folder, filename))]
                # Iterate through the file paths
                for file_path in file_paths:
                    filename = os.path.basename(file_path)
                    form_data = {'files': ('file.jpg', open(file_path, 'rb'))}
                    response = requests.post(api_endpoint, files=form_data)

                    print(response.json())

                    # use this response to show on GUI
                    text_list = []
                    if response.json()['result']:
                        api_response = response.json()['result']
                        for text in api_response:
                            print(text['result'])
                            text_list.append(str(text['result']))
                    else:
                        text_list.append('Not found')
                    # Convert the response to a string
                    # response_text = str(api_response)
                    update_gui(text_list)
                    # time.sleep(5)  # Sleep for 5 seconds before updating again

                    try:
                        os.remove(file_path)
                        print(
                            f"File {file_path} has been successfully deleted.")
                    except OSError as e:
                        print(f"Error deleting {file_path}: {e}")

            # Exit the loop when 'q' key is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break


# Create the main window
root = tk.Tk()
root.title("API Response GUI")

# # Create a frame for the video feed
# video_frame = tk.Frame(root)
# video_frame.pack(side=tk.LEFT, padx=10, pady=10)

# # Create a label to display the video frames
# video_label = tk.Label(video_frame)
# video_label.pack()

# Create a frame for the API result
result_frame = tk.Frame(root)
result_frame.pack(side=tk.LEFT)

# Create a text widget to display the API response
text_widget = tk.Text(root, wrap=tk.WORD, height=15, width=60)
text_widget.pack()

# Start the API request and GUI update process in a separate thread
api_thread = threading.Thread(target=process_api_request)
api_thread.daemon = True
api_thread.start()

# Release the VideoCapture and close OpenCV windows
# cap.release()
# cv2.destroyAllWindows()

# Start the Tkinter main loop
Font_tuple = ("Comic Sans MS", 20, "bold")

# Parsed the specifications to the
# Text widget using .configure( ) method.
text_widget.configure(font=Font_tuple)
root.mainloop()
