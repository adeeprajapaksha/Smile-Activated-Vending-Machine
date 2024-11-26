import cv2
import imutils
import pygetwindow as gw
import threading
import time
import numpy as np
from keras.preprocessing.image import img_to_array
from keras.models import load_model
import argparse
from motor_python import activate_motor

cv2.ocl.setUseOpenCL(True)  # Enable OpenCL backend

def capture_photo(frame, smile_percentages, rects):
    frame_with_overlay = frame.copy()

    for i, (fX, fY, fW, fH) in enumerate(rects):
        label = f'Smile: {smile_percentages[i]:.2f}%'
        color = (0, 255, 0) if smile_percentages[i] > 50 else (0, 0, 255)
        cv2.putText(frame_with_overlay, label, (fX, fY - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 2)
        cv2.rectangle(frame_with_overlay, (fX, fY), (fX + fW, fY + fH), color, 2)

    timestamp = time.strftime('%Y%m%d%H%M%S')
    filename = f'C:/xampp/htdocs/bocpost/imgs/smile_{timestamp}.jpg'
    cv2.imwrite(filename, frame_with_overlay)
    print(f'[INFO] Photo captured with overlay: {filename}')

def reset_game():
    global game_active, motor_activated, countdown_start_time, capture_flag, smile_percentages_list, delay_start_time, photo_counter
    #game_active = False
    countdown_start_time = None
    capture_flag = False
    motor_activated = True
    smile_percentages_list.clear()
    delay_start_time = time.time()
    photo_counter = 0
    #time.sleep(10)

global photo_counter
global countdown_counter
photo_counter = 0
countdown_counter = 0

ap = argparse.ArgumentParser()
ap.add_argument('-c', '--cascade', required=True, help='path to where the face cascade resides')
ap.add_argument('-m', '--model', required=True, help='path to the pre-trained smile detector CNN')
ap.add_argument('-v', '--video', help='path to the (optional) video file')
args = vars(ap.parse_args())

detector = cv2.CascadeClassifier(args['cascade'])
model = load_model(args['model'])

if not args.get('video', False):
    print('[INFO] starting video capture...')
    camera = cv2.VideoCapture(0)
else:
    camera = cv2.VideoCapture(args['video'])

desired_fps = 30
camera.set(cv2.CAP_PROP_FPS, desired_fps)
desired_width = 1280
desired_height = 720
camera.set(cv2.CAP_PROP_FRAME_WIDTH, desired_width)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, desired_height)
camera.set(cv2.CAP_PROP_FPS, desired_fps)

game_active = False
countdown_start_time = None
capture_flag = False
smile_percentages_list = []
delay_start_time = None
motor_activated = True


smoothing_factor = 0.9
countdown_seconds = 40
pause_seconds = 10
smile_duration = 3
min_faces_to_start_game = 2

intro = cv2.VideoCapture('static/123.mp4')

window_name = "window"

def generate_frames():
    global motor_activated
    global game_active, countdown_start_time, capture_flag, smile_percentages_list, delay_start_time, photo_counter
    game_active = False
    motor_activated = True
    frame_counter = 0
    game_pause = False
    game_status = ''
    won = cv2.imread('static/screen2.jpg')
    lose = cv2.imread('static/screen1.jpg')

    # Create a window without a border
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    # Find the window by name
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    
    #h 1920
    #w 1080

    # TEST
    # pause_countdown_start_time = time.time()
    # game_active = True
    # game_pause = True
    # game_status = 'WON'

    while True :
        (grabbed, frame) = camera.read()

        if args.get('video') and not grabbed:
            break
      

          # Specify desired height for portrait mode
        desired_height = 800

        # Resize the frame maintaining aspect ratio
        frame = imutils.resize(frame, height=desired_height)        
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame_clone = frame.copy()

        rects = detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30),
                                           flags=cv2.CASCADE_SCALE_IMAGE)
        
        if game_active: 
            if not game_pause :
                countdown_elapsed_time = time.time() - countdown_start_time
                remaining_seconds = max(countdown_seconds - countdown_elapsed_time, 0)
                countdown_counter = 1
                print(f"Countdown: {int(remaining_seconds)} seconds")

              
                if remaining_seconds > 0 and motor_activated:
                    smile_percentages = []
                    for (fX, fY, fW, fH) in rects:
                        roi = gray[fY:fY + fH, fX:fX + fW]
                        roi = cv2.resize(roi, (28, 28))
                        roi = roi.astype('float') / 255.0
                        roi = img_to_array(roi)
                        roi = np.expand_dims(roi, axis=0)

                        smile_percentage = model.predict(roi)[0][1] * 100
                        smile_percentages.append(smile_percentage)

                        smile_percentages_list = [smoothing_factor * percentage +
                                                (1 - smoothing_factor) * smoothed_percentage
                                                for percentage, smoothed_percentage in
                                                zip(smile_percentages, smile_percentages_list)]

                        smoothed_smile_percentage = (
                            smoothing_factor * smile_percentage +
                            (1 - smoothing_factor) * (smile_percentages_list[-1] if smile_percentages_list else smile_percentage)
                        )

                        label = f'Smile: {smoothed_smile_percentage:.2f}%'
                        color = (0, 255, 0) if smoothed_smile_percentage > 50 else (0, 0, 255)
                        cv2.putText(frame_clone, label, (fX, fY - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 2)
                        cv2.rectangle(frame_clone, (fX, fY), (fX + fW, fY + fH), color, 2)

                    if all(percentage > 80 for percentage in smile_percentages):
                        if not capture_flag:
                            capture_flag = True
                            capture_time = time.time()

                    if capture_flag and motor_activated:
                        if len(rects) >= 2 and all(percentage > 80 for percentage in smile_percentages[:2]):
                            elapsed_capture_time = time.time() - capture_time
                            if elapsed_capture_time >= smile_duration:
                                capture_photo(frame, smile_percentages, rects)
                                photo_counter += 1
                                pause_countdown_start_time = time.time()
                                game_pause = True
                                game_status = 'WON'
                                reset_game()
                                


                                
                    cv2.putText(frame_clone, f"Countdown: {int(remaining_seconds)} seconds", (10, 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

                else:
                    # loss
                    pause_countdown_start_time = time.time()
                    game_pause = True
                    game_status = 'LOSS'

                
                cv2.imshow(window_name, frame_clone)
                cv2.resizeWindow(window_name,1080,960)
                cv2.namedWindow(window_name, cv2.WINDOW_GUI_NORMAL)

                print(f'Total photos captured: {photo_counter}')

                if photo_counter > 0:
                    # win
                    pause_countdown_start_time = time.time()
                    game_pause = True
                    game_status = 'WON'
            else:
                pause_countdown_elapsed_time = time.time() - pause_countdown_start_time    
                pause_remaining_seconds = max(pause_seconds - pause_countdown_elapsed_time, 0)
                print(f"PAUSE: {int(pause_remaining_seconds)} seconds")
                if pause_remaining_seconds == 0:
                    game_active = False
                    game_pause  = False
                else:
                    if game_status == 'WON' and motor_activated:                        
                        cv2.imshow(window_name, won)
                        cv2.resizeWindow(window_name,1080,1920)
                        cv2.namedWindow(window_name, cv2.WINDOW_GUI_NORMAL)                        
                        activate_motor(1)
                        print("Motor activated!")
                        motor_activated = False
                        
                    elif game_status == 'LOSS' and motor_activated:   
                        cv2.imshow(window_name, lose)
                        cv2.resizeWindow(window_name,1080,1920)
                        cv2.namedWindow(window_name, cv2.WINDOW_GUI_NORMAL)

        if len(rects) >= min_faces_to_start_game and not game_active:
            print("Game started! Maintain a smile for 3 seconds within the countdown.")
            game_active = True
            motor_activated = True
            countdown_start_time = time.time()
            smile_percentages_list.clear()
        else:
            if not game_active:
                smile_percentages_list.clear()
                (introGrabbed, introFrm) = intro.read()
                frame_counter += 1
                
                if frame_counter == intro.get(cv2.CAP_PROP_FRAME_COUNT):
                    frame_counter = 0 #Or whatever as long as it is the same as next line
                    intro.set(cv2.CAP_PROP_POS_FRAMES, 0)

                
                if introGrabbed:
                    introFrame = imutils.resize(introFrm , width=1080)
            
                cv2.imshow(window_name, introFrame)
                cv2.resizeWindow(window_name,1080,1920)
                cv2.namedWindow(window_name, cv2.WINDOW_GUI_NORMAL)

            
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break



    camera.release()
    cv2.destroyAllWindows()

generate_frames()
