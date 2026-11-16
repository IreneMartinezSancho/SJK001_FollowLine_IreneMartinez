#CONTROLADOR P - Irene Martínez

import WebGUI
import HAL
import Frequency
import cv2

# Parámetros del controlador P
linearVelocity = 6
Kp = 0.01

while True:
    #Controla la frecuencia de ejecución del programa
    Frequency.tick()

    #Establecemos la velocidad lineal del coche y obtenemos la imagen de la cámara
    HAL.setV(linearVelocity)
    img = HAL.getImage()
    WebGUI.showImage(img)

    #Convertimos la imagen de BGR a HSV para poder detectar el color rojo    
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Creamos una máscara para quedarnos únicamente con los píxeles rojos
    # En HSV, el tono rojo está cerca de 0. Utilizamos el rango de 0 a 30
    # y unos valores mínimos de saturación y brillo de 125
    # La máscara pone en blanco (255) los píxeles que detecta como rojos
    # y en negro (0) el resto de la imagen    
    red_mask = cv2.inRange(hsv, (0,125,125),(30,255,255))
    
    # Calculamos los momentos de la máscara para obtener el centroide
    # de la zona roja que hemos detectado
    M = cv2.moments(red_mask)

    if M["m00"] != 0:  
        # Si hay píxeles rojos, calculamos el centroide de la máscara
        # cX es la posición horizontal del centroide, que es la que nos interesa
        # cY es la posición vertical, pero no la utilizamos para controlar el coche
        cX = M["m10"] / M["m00"]    
        cY = M["m01"] / M["m00"]
    else:
        # Si no detectamos rojo, ponemos las coordenadas a cero
        cX, cY = 0, 0

    if cX > 0:
        # Calculamos el error entre el centro de la imagen (320)
        # y la posición horizontal de la línea roja
        err = 320 - cX
        # Controlador proporcional (P)
        # Multiplicamos el error por Kp = 0.01 para calcular cuánto debe girar
        # Cuanto más lejos esté la línea del centro, mayor será la corrección
        HAL.setW(Kp * err)

    # Mostramos la máscara para comprobar qué partes detecta como rojas
    WebGUI.showImage(red_mask)
    
