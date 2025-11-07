import capture_lead as cl
import utils
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from colorama import Fore, init
import image
import json

# colorama
init(autoreset=True)
# parser = argparse.ArgumentParser(description="Script para dar bypass em CAPTCHA.")
# parser.add_argument("--driver-path", required=True, help="Caminho do driver do navegador.")

# args = parser.parse_args()


json_path = r'/home/lydia-server/Documentos/crawler-byd/byd-captcha karem/json/login.json'

# abre e carrega os dados
with open(json_path, "r", encoding="utf-8") as f:
    login_data = json.load(f)

USERNAME = login_data["username"]
cl.USERNAME_GLOBAL = USERNAME
PASSWORD = login_data["password"]

LOGIN="https://uscrm.byd.com/login"

print(f"{Fore.YELLOW}Iniciando o navegador...")



utils.DRIVER.maximize_window()
utils.DRIVER.get(LOGIN)
print(f"{Fore.GREEN}Navegador iniciado e página Inicial Carregada!")

def login(username, password):
    print(f"{Fore.YELLOW}Iniciando o processo de login...")
    
    username_field = utils.get_element(utils.Condition.PRESENCE, By.XPATH, "//*[@id='msp']/div[1]/div/div/div[1]/div[2]/div/div[2]/form/div[2]/div/div/input")

    password_field = utils.get_element(utils.Condition.PRESENCE, By.XPATH, "//*[@id='msp']/div[1]/div/div/div[1]/div[2]/div/div[2]/form/div[4]/div/div/input")

    username_field.click()
    username_field.send_keys(username)
    password_field.click()
    password_field.send_keys(password)

    accept_cookies = utils.get_element(utils.Condition.CLICKABLE, By.XPATH, "/html/body/div/div[1]/div/div/div[1]/div[6]/div[1]/div/div[2]/button[3]")
    accept_cookies.click()
    
    read_politics = utils.get_element(utils.Condition.CLICKABLE, By.XPATH, "/html/body/div/div[1]/div/div/div[1]/div[2]/div/div[2]/form/div[5]/div/label/label")
    read_politics.click()
 
    login_button = utils.get_element(utils.Condition.CLICKABLE, By.XPATH, "//*[@id='msp']/div[1]/div/div/div[1]/div[2]/div/div[2]/form/div[5]/div/button")
    login_button.click()
    print(f"{Fore.GREEN}Credenciais enviadas.")
    
    
def get_image():
    print(f"{Fore.YELLOW}Capturando imagem do CAPTCHA...")
    captcha_image = utils.get_element(utils.Condition.PRESENCE, By.XPATH, "/html/body/div/div[1]/div/div/div[1]/div[4]/div/div[2]/div/div[1]/div/img")
    image_src = captcha_image.get_attribute("src")
    print(f"{Fore.GREEN}Imagem do CAPTCHA capturada.")
    return image_src, captcha_image

def resolve_captcha(x_pixel, image_width, image_element):
    """
    Move o slider do CAPTCHA até a posição x_pixel dentro da imagem.
    
    x_pixel: coordenada horizontal dentro da imagem (em pixels)
    image_element: elemento Selenium da imagem do CAPTCHA
    """
    print(f"{Fore.YELLOW}Iniciando a resolução do CAPTCHA...")

    # slider
    slider = utils.get_element(
        utils.Condition.CLICKABLE,
        By.XPATH,
        "/html/body/div/div[1]/div/div/div[1]/div[4]/div/div[2]/div/div[2]/div/div"
    )
    
    slider_width = slider.size['width']
    print(f"{Fore.MAGENTA}Largura do slider: {Fore.RED}{slider_width}{Fore.MAGENTA} pixels")
 
 
 
    real_width = image_element.size['width']
    print(f"{Fore.MAGENTA}Largura da imagem: {Fore.RED}{image_width}{Fore.MAGENTA} pixels")
    print(f"{Fore.MAGENTA}Largura mostrada na tela: {Fore.RED}{real_width}{Fore.MAGENTA} pixels")

    # calcula a proporção entre a largura real e a largura mostrada
    scale_factor = real_width / image_width
    print(f"{Fore.MAGENTA}Fator de escala: {Fore.RED}{scale_factor}{Fore.MAGENTA}")
    # ajusta a coordenada x_pixel de acordo com a escala
    print(f"{Fore.BLUE}Coordenada X original do CAPTCHA: {Fore.RED}{x_pixel}{Fore.BLUE} pixels")
    x_pixel = int(x_pixel * scale_factor)
    print(f"{Fore.BLUE}Coordenada X ajustada do CAPTCHA: {Fore.RED}{x_pixel}{Fore.BLUE} pixels")

    offset_x = x_pixel - (slider_width // 2)  # centraliza o clique no meio do slider
    print(f"{Fore.MAGENTA}Calculando deslocamento do slider: {Fore.RED}{offset_x}{Fore.MAGENTA} pixels")
    
    # movimenta o slider
    action = ActionChains(utils.DRIVER)
    action.click_and_hold(slider).perform()
    sleep(0.2)
    # action.move_to_element(image_element).perform()
    # sleep(0.2)
    action.move_by_offset(offset_x, 0).perform()
    action.release().perform()
    
    print(f"Slider movido aproximadamente {Fore.RED}{offset_x}{Fore.RESET} pixels para a direita.")

login(USERNAME, PASSWORD)
image_src, image_element = get_image()
x, width = image.get_image_x_y(image_src, debug=True)
if x is None:
    exit(1)
print(f"{Fore.CYAN}Coordenada X da peça do CAPTCHA: {x}")
resolve_captcha(x, width, image_element)

print(f'{Fore.GREEN}Captcha solucionado!')
cl.capture_leads()