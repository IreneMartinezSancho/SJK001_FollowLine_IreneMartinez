# CONTROLADOR PD - Irene Martínez

import WebGUI
import HAL
import Frequency
import cv2

# Parámetros del controlador PD
linearVelocity = 7
Kp = 0.01
Kd = 0.05

# Guardamos el error anterior para calcular la derivada
error_anterior = None

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

        # Calculamos cuánto ha cambiado el error respecto a la iteración anterior
        # En la primera iteración no tenemos un error anterior, por lo que la derivada es 0
        if error_anterior is None:
            derivada = 0
        else:
            derivada = err - error_anterior

        # Controlador proporcional-derivativo (PD)
        # La parte P corrige según lo lejos que estamos de la línea
        P = Kp * err

        # La parte D tiene en cuenta cuánto está cambiando el error
        # para intentar reducir los bandazos y las oscilaciones
        D = Kd * derivada

        # Sumamos las dos partes para calcular el giro del coche
        HAL.setW(P + D)

        # Guardamos el error actual para utilizarlo en la siguiente iteración
        error_anterior = err

    else:
        # Si perdemos la línea, reiniciamos el error anterior
        # para evitar una corrección derivativa brusca al recuperarla
        error_anterior = None

    # Mostramos la máscara para comprobar qué partes detecta como rojas
    WebGUI.showImage(red_mask)
