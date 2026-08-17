import cv2
import mediapipe as mp
import pyautogui
import math
import time
import ctypes
import os


# PYAUTOGUI
pyautogui.PAUSE = 0  
pyautogui.FAILSAFE = False 
wScr, hScr = pyautogui.size()

# MEDIAPIPE & KAMERA
wCam, hCam = 640, 480
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.75, min_tracking_confidence=0.75)
mp_drawing = mp.solutions.drawing_utils

# SETTING JENDELA "ALWAYS ON TOP" & TRANSPARAN
window_name = "Air Touchpad PiP"
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)
cv2.resizeWindow(window_name, 320, 240) 

TINGKAT_TRANSPARANSI = 160 
try:
    hwnd = ctypes.windll.user32.FindWindowW(None, window_name)
    if hwnd:
        GWL_EXSTYLE = -20
        WS_EX_LAYERED = 0x00080000
        LWA_ALPHA = 0x00000002
        ex_style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, ex_style | WS_EX_LAYERED)
        ctypes.windll.user32.SetLayeredWindowAttributes(hwnd, 0, TINGKAT_TRANSPARANSI, LWA_ALPHA)
except Exception as e:
    print(f"Gagal mengatur transparansi: {e}")

# VAR KONTROL & STABILISASI
frameR = 40     
plocX, plocY = 0, 0 
clocX, clocY = 0, 0 

# Var State Inti
is_left_clicked = False
is_right_clicked = False
is_dragging = False
left_click_start = 0
prev_y_scroll = 0 
CLICK_THRESHOLD = 22 

is_paused = False
pause_start = 0
osk_start = 0
media_prev_y = 0
media_prev_x = 0
prev_task_y = 0
task_view_triggered = False

def map_koordinat(val, in_min, in_max, out_min, out_max):
    return (val - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def get_fingers(lm):
    """Fungsi pembantu untuk mendeteksi jari terbuka (Telunjuk, Tengah, Manis, Kelingking)"""
    f = []
    for tip in [8, 12, 16, 20]:
        f.append(1 if lm[tip].y < lm[tip - 2].y else 0)
    return f

while cap.isOpened():
    success, frame = cap.read()
    if not success: break

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    left_lm = None
    right_lm = None
    l_fingers = []
    r_fingers = []
    zoom_lock_active = False
    
    box_color = (255, 0, 255) 
    alert_text = "Air Touchpad Pro"

    # pemisah tngan kiri dan kanan
    if results.multi_hand_landmarks and results.multi_handedness:
        for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            label = results.multi_handedness[idx].classification[0].label
            
            if label == 'Left':
                left_lm = hand_landmarks.landmark
                l_fingers = get_fingers(left_lm)
            elif label == 'Right':
                right_lm = hand_landmarks.landmark
                r_fingers = get_fingers(right_lm)

    # MODE JEDA
    if left_lm and right_lm and l_fingers == [0,0,0,0] and r_fingers == [0,0,0,0]:
        if time.time() - pause_start > 1.5:
            is_paused = not is_paused
            pause_start = time.time() + 1.0
    elif not (l_fingers == [0,0,0,0] and r_fingers == [0,0,0,0]):
        pause_start = time.time()

    if is_paused:
        cv2.putText(frame, "SISTEM JEDA (PAUSED)", (wCam//2 - 120, hCam//2), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 3)
        cv2.imshow(window_name, frame)
        if cv2.waitKey(1) & 0xFF == ord('q'): break
        continue

    # PROSES TANGAN KIRI (KURSOR, OSK, ZOOM LOCK)
    if left_lm:
        x_index_l = int(left_lm[8].x * wCam)
        y_index_l = int(left_lm[8].y * hCam)

        # Warning System
        margin_warning = 20 
        if (x_index_l < frameR + margin_warning or x_index_l > wCam - frameR - margin_warning or 
            y_index_l < frameR + margin_warning or y_index_l > hCam - frameR - margin_warning):
            box_color = (0, 0, 255) 
            alert_text = "AWAS: KELUAR BATAS!"

        # ON-SCREEN KEYBOARD
        if l_fingers == [1, 0, 0, 1]:
            cv2.putText(frame, "MEMANGGIL KEYBOARD...", (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            if time.time() - osk_start > 2.0:
                os.popen("osk")
                osk_start = time.time() + 3.0
        else:
            osk_start = time.time()

        # kunci mode zoom
        if l_fingers == [1, 1, 0, 0]:
            zoom_lock_active = True
            cv2.putText(frame, "ZOOM MODE LOCKED", (50, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

        # eksekusi kursor
        if l_fingers != [0,0,0,0]:
            x_terbatas = max(frameR, min(x_index_l, wCam - frameR))
            y_terbatas = max(frameR, min(y_index_l, hCam - frameR))
            x3 = map_koordinat(x_terbatas, frameR, wCam - frameR, 0, wScr)
            y3 = map_koordinat(y_terbatas, frameR, hCam - frameR, 0, hScr)
            
            diff_x = x3 - plocX
            diff_y = y3 - plocY
            
            # kecepatan dinamis
            speed = math.hypot(diff_x, diff_y)
            if speed > 40: current_smooth = 2     
            elif speed < 10: current_smooth = 8   
            else: current_smooth = 5             
            
            if abs(diff_x) > 0.5 or abs(diff_y) > 0.5:
                clocX = plocX + diff_x / current_smooth
                clocY = plocY + diff_y / current_smooth
                pyautogui.moveTo(int(clocX), int(clocY))
                plocX, plocY = clocX, clocY

            cv2.circle(frame, (x_index_l, y_index_l), 8, (255, 0, 255), cv2.FILLED)

    # PROSES TANGAN KANAN (MEDIA, KLIK, SCROLL, TASK VIEW)
    if right_lm:
        x_thumb_r = int(right_lm[4].x * wCam)
        y_thumb_r = int(right_lm[4].y * hCam)
        x_index_r = int(right_lm[8].x * wCam)
        y_index_r = int(right_lm[8].y * hCam)
        x_mid_r = int(right_lm[12].x * wCam)
        y_mid_r = int(right_lm[12].y * hCam)

        # kiri mengepal + knan gerakk
        if left_lm and l_fingers == [0,0,0,0]:
            cv2.putText(frame, "MEDIA MODE AKTIF", (50, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            
            # volume control
            if r_fingers == [1,0,0,0]:
                if media_prev_y == 0: media_prev_y = y_index_r
                dy = y_index_r - media_prev_y
                if dy < -15:
                    pyautogui.press('volumeup')
                    media_prev_y = y_index_r
                elif dy > 15:
                    pyautogui.press('volumedown')
                    media_prev_y = y_index_r
            
            # next/prev track
            elif r_fingers == [1,1,0,0]:
                if media_prev_x == 0: media_prev_x = x_index_r
                dx = x_index_r - media_prev_x
                if dx > 40:
                    pyautogui.press('nexttrack')
                    media_prev_x = x_index_r
                    time.sleep(0.2)
                elif dx < -40:
                    pyautogui.press('prevtrack')
                    media_prev_x = x_index_r
                    time.sleep(0.2)
            else:
                media_prev_y, media_prev_x = 0, 0
                
        # klik, scroll, task view)
        else:
            jarak_kiri_r = math.hypot(x_index_r - x_thumb_r, y_index_r - y_thumb_r)
            jarak_kanan_r = math.hypot(x_mid_r - x_thumb_r, y_mid_r - y_thumb_r)

            # klik & drag
            if r_fingers not in [[1,1,1,1], [1,1,1,0]]:
                if jarak_kiri_r < CLICK_THRESHOLD:
                    cv2.circle(frame, (x_index_r, y_index_r), 12, (0, 255, 0), cv2.FILLED) 
                    if not is_left_clicked:
                        left_click_start = time.time()
                        is_left_clicked = True
                    else:
                        if time.time() - left_click_start > 0.4 and not is_dragging:
                            pyautogui.mouseDown()
                            is_dragging = True
                            cv2.putText(frame, "DRAGGING", (50, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                else:
                    if is_left_clicked:
                        if is_dragging:
                            pyautogui.mouseUp()
                            is_dragging = False
                        else:
                            pyautogui.click()
                        is_left_clicked = False

                # klik kanan
                if jarak_kanan_r < CLICK_THRESHOLD and not is_left_clicked:
                    cv2.circle(frame, (x_mid_r, y_mid_r), 12, (255, 0, 0), cv2.FILLED) 
                    if not is_right_clicked:
                        is_right_clicked = True
                        pyautogui.rightClick()
                else:
                    is_right_clicked = False

            # TASK VIEW
            if r_fingers == [1, 1, 1, 0]:
                cv2.putText(frame, "TASK VIEW READY", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 100, 100), 2)
                if prev_task_y == 0: prev_task_y = y_index_r
                if y_index_r - prev_task_y < -40 and not task_view_triggered:
                    pyautogui.hotkey('win', 'tab')
                    task_view_triggered = True
            else:
                task_view_triggered = False
                prev_task_y = y_index_r

            # Zoom
            if r_fingers == [1, 1, 1, 1] and jarak_kiri_r > 40 and jarak_kanan_r > 40:
                rata_y_r = (y_index_r + y_mid_r) / 2
                if prev_y_scroll == 0: prev_y_scroll = rata_y_r
                delta_y = rata_y_r - prev_y_scroll

                if abs(delta_y) > 1:
                    scroll_power = int(delta_y * 14) 
                    if zoom_lock_active:
                        cv2.putText(frame, "ZOOM ACTION", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
                        pyautogui.keyDown('ctrl'); pyautogui.scroll(scroll_power); pyautogui.keyUp('ctrl')
                    else:
                        cv2.putText(frame, "SCROLL MODE", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
                        pyautogui.scroll(scroll_power)
                    prev_y_scroll = rata_y_r
            else:
                prev_y_scroll = 0
                try: pyautogui.keyUp('ctrl') 
                except: pass

    # KOTAK BATAS
    cv2.rectangle(frame, (frameR, frameR), (wCam - frameR, hCam - frameR), box_color, 2)
    cv2.putText(frame, alert_text, (frameR, frameR - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, box_color, 2)

    cv2.imshow(window_name, frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()