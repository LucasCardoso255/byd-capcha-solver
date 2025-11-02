import cv2
import numpy as np
import base64

def get_x_y(img):
    altura, largura, _ = img.shape

    
    minY = maxY = minX = maxX = None
    found_white = False
    
    # itera sobre todos os pixels
    for y in range(int(altura)):
        found_line = False
        for x in range(largura):
            # se o pixel for branco
            if (img[y, x] == [255, 255, 255]).all():
                # marca que encontrou branco
                found_white = True
                found_line = True
                
                # atualiza limites
                if minY is None or y < minY: minY = y
                if maxY is None or y > maxY: maxY = y
                if minX is None or x < minX: minX = x
                if maxX is None or x > maxX: maxX = x
                
                 # pintar de AZUL os pixels brancos encontrados
                img[y, x] = [255, 0, 0]  # azul em BGR
        # se não encontrou branco na linha atual, mas já encontrou antes, acabou o bloco
        if not found_line and found_white:
            break
                
                
    # # teste
    # if minX is not None and maxX is not None and minY is not None and maxY is not None:
    #     cv2.rectangle(img, (minX, minY), (maxX, maxY), (0, 255, 0), 1)

    # pintar o MEIO de VERMELHO
    if minY is not None and maxY is not None:
        midY = (minY + maxY) // 2
        midX = (minX + maxX) // 2
        testX = minX
        img[midY, testX] = [0, 0, 255] 
        return testX, midY
    return None, None
        

def base64_to_matrix(base64_str):
    img_data = base64.b64decode(base64_str)
    np_arr = np.frombuffer(img_data, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    return img
   

def get_base64(image_src):
        base64 = image_src.split(",")[1]
        return base64

def get_image_x_y(image_src, debug=False):
    img = base64_to_matrix(get_base64(image_src))
    x, y = get_x_y(img)
    # salva a imagem pra debuggar
    if debug:
        cv2.imwrite("saida.png", img)
    print("Resultado:", x, y)
    _, largura, _ = img.shape
    return x, largura