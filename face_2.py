import cv2
import face_recognition as fr
import numpy as np
import mediapipe as mp
import os
from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk
import imutils
import mysql.connector
import time
import io

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="facerecognition_db"
)
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    username VARCHAR(100) UNIQUE,
    face_encoding LONGBLOB
)''')
conn.commit()

cursor.execute('''CREATE TABLE IF NOT EXISTS access_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    access_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
)''')
conn.commit()
known_users = {}

def load_encodings():
    global known_users
    cursor.execute("SELECT username, face_encoding FROM users")
    for username, enc in cursor.fetchall():
        known_users[username] = np.frombuffer(enc, dtype=np.float64)

load_encodings()

mpDraw = mp.solutions.drawing_utils
FacemeshObject = mp.solutions.face_mesh
FaceMesh = FacemeshObject.FaceMesh(max_num_faces=1)
FACE_CONNECTIONS = FacemeshObject.FACEMESH_TESSELATION
FaceObject = mp.solutions.face_detection
Detector = FaceObject.FaceDetection(min_detection_confidence=0.5, model_selection=1)
ConfigDraw = mpDraw.DrawingSpec(thickness=1, circle_radius=1, color=(200, 200, 200))

parpadeo = False
conteo = 0
muestra = 0
step = 0
modo = "registro"
offsety = 30
offsetx = 20
cap = None
info = []
Reconocido = False
RegName = ""
RegUser = ""
current_timer = 3
found_user = ""
face_captured = False

def countdown():
    global current_timer, pantalla2
    if modo == "registro" and not face_captured:
        if current_timer > 0:
            current_timer -= 1
            pantalla2.after(1000, countdown)

def Log_Biometric():
    global pantalla2, conteo, parpadeo, img_info, step, cap, lblVideo, muestra, modo, Reconocido, current_timer, found_user, face_captured

    if cap is not None and cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("No se pudo capturar la cámara.")
            return

        frame = imutils.resize(frame, width=1280)
        frameBGR = frame.copy()
        frameRGB = cv2.cvtColor(frameBGR, cv2.COLOR_BGR2RGB)
        frameToShow = frameRGB.copy()

        detections = Detector.process(frameRGB)
        results_mesh = FaceMesh.process(frameRGB)
        if results_mesh.multi_face_landmarks:
            for faceLms in results_mesh.multi_face_landmarks:
                mpDraw.draw_landmarks(
                    image=frameToShow,
                    landmark_list=faceLms,
                    connections=FACE_CONNECTIONS,
                    landmark_drawing_spec=ConfigDraw,
                    connection_drawing_spec=ConfigDraw
                )

        if detections.detections:
            ih, iw, _ = frameBGR.shape
            for detection in detections.detections:
                bbox = detection.location_data.relative_bounding_box
                x = int(bbox.xmin * iw)
                y = int(bbox.ymin * ih)
                w = int(bbox.width * iw)
                h = int(bbox.height * ih)
                face_crop = frameBGR[y:y + h, x:x + w]

                if modo == "registro" and not face_captured:
                    cv2.putText(frameToShow, f"Captura en: {current_timer}", (50, 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 255), 4)

                    if current_timer == 0:
                        try:
                            face_enc = fr.face_encodings(frameRGB)[0]

                            for enc in known_users.values():
                                match = fr.compare_faces([enc], face_enc, tolerance=0.5)[0]
                                if match:
                                    cursor.execute("DELETE FROM users WHERE username = %s", (RegUser,))
                                    conn.commit()
                                    inputNameReg.delete(0, END)
                                    inputUsersReg.delete(0, END)
                                    cap.release()
                                    pantalla2.destroy()
                                    messagebox.showerror("Error", "¡Este rostro ya está registrado!")
                                    return

                            encoding_bytes = face_enc.tobytes()
                            cursor.execute("INSERT INTO users (name, username, face_encoding) VALUES (%s, %s, %s)",
                                           (RegName, RegUser, encoding_bytes))
                            conn.commit()
                            known_users[RegUser] = face_enc  

                            face_captured = True
                            cap.release()
                            pantalla2.destroy()
                            messagebox.showinfo("Registro", "Rostro registrado con éxito.")
                            return
                        except:
                            pass

                elif modo == "login" and not Reconocido:
                    try:
                        face_enc = fr.face_encodings(frameRGB)[0]
                        start_time = time.time()
                        rostro_no_encontrado = True
                        for user, known_enc in known_users.items():
                            if time.time() - start_time > 2:
                                print("Tiempo límite alcanzado")
                                break
                            match = fr.compare_faces([known_enc], face_enc, tolerance=0.5)[0]
                            if match:
                                Reconocido = True
                                found_user = user
                                rostro_no_encontrado = False

                                cursor.execute("SELECT id FROM users WHERE username = %s", (user,))
                                user_id_result = cursor.fetchone()
                                if user_id_result:
                                    user_id = user_id_result[0]
                                    cursor.execute("INSERT INTO access_logs (user_id) VALUES (%s)", (user_id,))
                                    conn.commit()

                                cap.release()
                                pantalla2.destroy()
                                Bienvenida(user)
                                return

                        if rostro_no_encontrado:
                            cap.release()
                            pantalla2.destroy()
                            messagebox.showinfo("No registrado", "Usted no se encuentra registrado, por favor complete el registro para iniciar sesión.")
                            return
                    except:
                        pass

        im = Image.fromarray(frameToShow)
        img = ImageTk.PhotoImage(image=im)
        lblVideo.configure(image=img)
        lblVideo.image = img
        lblVideo.after(30, Log_Biometric)
    else:
        if cap:
            cap.release()

def Bienvenida(user: str):
    ventana = Toplevel(pantalla)
    ventana.title("Bienvenido")
    ventana.geometry("600x500")
    Label(ventana, text=f"¡Bienvenido {user}!", font=("Arial", 20)).pack(pady=10)
    Label(ventana, text="Este sistema mejora la seguridad de la Institución Universitaria de Barranquilla.",
          wraplength=500, justify="center").pack(pady=10)
    
    print(f"Usuario {user} autenticado - TORNIQUETE DESBLOQUEADO (puede girar)")
    
    ventana.after(3000, lambda: cerrar_ventana(ventana, user))

def cerrar_ventana(ventana, user):
    ventana.destroy()
    print(f"Usuario {user} ha pasado - TORNIQUETE BLOQUEADO")

def Sign():
    global RegName, RegUser, inputNameReg, inputUsersReg, cap, lblVideo, pantalla2, muestra, modo, current_timer, face_captured

    RegName, RegUser = inputNameReg.get(), inputUsersReg.get()

    if len(RegName) == 0 or len(RegUser) == 0:
        messagebox.showwarning("Faltan datos", "Complete todos los campos.")
    else:
        cursor.execute("SELECT username FROM users WHERE username = %s", (RegUser,))
        if cursor.fetchone():
            messagebox.showwarning("Ya existe", "Usuario ya registrado.")
        else:
            pantalla2 = Toplevel(pantalla)
            pantalla2.title("CAPTURA BIOMÉTRICA")
            pantalla2.geometry("1280x720")

            lblVideo = Label(pantalla2)
            lblVideo.place(x=0, y=0)

            cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            cap.set(3, 1280)
            cap.set(4, 720)

            muestra = 0
            current_timer = 5
            face_captured = False
            modo = "registro"
            countdown()
            Log_Biometric()

def Log():
    global cap, lblVideo, pantalla2, modo, Reconocido, current_timer, found_user

    Reconocido = False
    found_user = ""
    pantalla2 = Toplevel(pantalla)
    pantalla2.title("LOGIN BIOMÉTRICO")
    pantalla2.geometry("1280x720")

    lblVideo = Label(pantalla2)
    lblVideo.place(x=0, y=0)

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(3, 1280)
    cap.set(4, 720)

    modo = "login"
    current_timer = 5
    Log_Biometric()

pantalla = Tk()
pantalla.title("FACE RECOGNITION SYSTEM")
pantalla.geometry("1280x720")

imagenF = PhotoImage(file=r"C:\xampp\htdocs\xampp\Reconocimiento_Facial_IUB\SetUp\Inicio.png")
background = Label(image=imagenF, text="Inicio")
background.place(x=0, y=0, relheight=1, relwidth=1)

inputNameReg = Entry(pantalla)
inputNameReg.place(x=150, y=360)

inputUsersReg = Entry(pantalla)
inputUsersReg.place(x=150, y=470)

imagenBR = PhotoImage(file=r"C:\xampp\htdocs\xampp\Reconocimiento_Facial_IUB\SetUp\BtSign.png")
BtReg = Button(pantalla, image=imagenBR, height="52", width="411", command=Sign)
BtReg.place(x=150, y=535)

imagenBL = PhotoImage(file=r"C:\xampp\htdocs\xampp\Reconocimiento_Facial_IUB\SetUp\BtLogin.png")
BtSign = Button(pantalla, image=imagenBL, height="51", width="395", command=Log)
BtSign.place(x=730, y=535)

pantalla.mainloop()
