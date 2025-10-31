import cv2
import numpy as np
import base64

def get_x_y(img):
    altura, largura, _ = img.shape

    
    first_white_pixelY = None
    last_white_pixelY = None
    first_white_pixelX = None
    last_white_pixelX = None
    # Itera sobre todos os pixels
    for y in range(int(altura * 0.6)):
        for x in range(largura):
            # Se o pixel for branco (BGR)
            if (img[y, x] == [255, 255, 255]).all():
                if first_white_pixelY is None:
                    first_white_pixelY = y
                last_white_pixelY = y
                if first_white_pixelX is None:
                    first_white_pixelX = x
                last_white_pixelX = x
                img[y, x] = [255, 0, 0]

    # Pintar o MEIO de VERMELHO forte
    if first_white_pixelY is not None and last_white_pixelY is not None:
        midY = (first_white_pixelY + last_white_pixelY) // 2
        midX = (first_white_pixelX + last_white_pixelX) // 2
        midX = int(midX)
        img[midY, midX] = [0, 0, 255]  # vermelho em BGR
        return midX, midY
    return None, None
        

def base64_to_matrix(base64_str):
    img_data = base64.b64decode(base64_str)
    np_arr = np.frombuffer(img_data, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    return img
   

def get_base64(image_src):
        base64 = image_src.split(",", 1)[1]
        return base64

def get_image_x(image_src):
    img = base64_to_matrix(get_base64(image_src))
    x, y = get_x_y(img)
    # Salva a imagem modificada
    cv2.imwrite("saida.png", img)
    print("Resultado:", x, y)
    return x
