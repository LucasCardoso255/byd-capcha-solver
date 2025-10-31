import cv2

# Caminhos
imagem_path = "resultado.png"
saida_path = "resultado_modificado.png"

# Carrega a imagem
img = cv2.imread(imagem_path)
if img is None:
    raise FileNotFoundError(f"Não foi possível abrir a imagem: {imagem_path}")

altura, largura, _ = img.shape

first_white_pixelY = None
last_white_pixelY = None
first_white_pixelX = None
last_white_pixelX = None
# Itera sobre todos os pixels
for y in range(int(altura * 0.8)):
    for x in range(largura):
        # Se o pixel for branco (BGR)
        if (img[y, x] == [255, 255, 255]).all():
            if first_white_pixelY is None:
                first_white_pixelY = y
            last_white_pixelY = y
            if first_white_pixelX is None:
                first_white_pixelX = x
            last_white_pixelX = x
            img[y, x] = [255, 0, 0]  # azul em BGR

# Pintar o MEIO de VERMELHO forte
if first_white_pixelY is not None and last_white_pixelY is not None:
	midY = (first_white_pixelY + last_white_pixelY) // 2
	midX = (first_white_pixelX + last_white_pixelX) // 2
	midX = int(midX * 0.96)
	img[midY, midX] = [0, 0, 255]  # vermelho em BGR

# Salva a imagem modificada
cv2.imwrite(saida_path, img)
print(f"Todos os pixels brancos foram transformados em azul e a imagem foi salva em '{saida_path}'")
