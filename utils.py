import enum
import math
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.options import Options
from colorama import Fore, init
import capture_lead as cl

class Condition(enum.Enum):
    CLICKABLE = "clickable"
    PRESENCE = "presence"
    NO_WAIT = "no_wait"

DRIVER_PATH = r"D:\.bundas\captcha2\byd-capcha-solver\Driver\webdriver.exe"
options = Options()
options.binary_location = r"C:\Program Files\Mozilla Firefox\firefox.exe"
DRIVER = webdriver.Firefox(service=Service(DRIVER_PATH), options=options)
    
# espera por {cond} e pega o elemento
def get_element(cond, by, value, timeout=30, element=DRIVER):
    try:
        TIMEOUT=timeout
        if cond == Condition.CLICKABLE:
            return WebDriverWait(element, TIMEOUT).until(EC.element_to_be_clickable((by, value)))
        elif cond == Condition.PRESENCE:
            return WebDriverWait(element, TIMEOUT).until(EC.presence_of_element_located((by, value)))
        elif cond == Condition.NO_WAIT:
            return element.find_element(by, value)
    except Exception as e:
        print(f"{Fore.RED}Erro ao localizar o elemento: {value} - {str(e)}")
        raise e
    
# aguarda o carregamento dos elementos antes de pegar
def get_elements(by, value, timeout=30, element=DRIVER):
    try:
        TIMEOUT=timeout
        return WebDriverWait(element, TIMEOUT).until(EC.presence_of_all_elements_located((by, value)))
        
    except Exception as e:
        print(f"{Fore.RED}Erro ao localizar o elemento: {value} - {str(e)}")
        raise e

# aguarda o loading desparecer antes de prosseguir
def wait_loading_to_disappear():
    try:
        WebDriverWait(DRIVER, timeout=30).until(
            EC.invisibility_of_element_located((By.CLASS_NAME, "el-loading-mask"))
        )
    except:
        pass  # se não desaparecer em timeout, continua

# função caso o loading tenha animação de fade
def click_when_ready(by, value, timeout=30):
    '''
    Se puder evitar usar essa função, é melhor.
    Pois não fica muito facil de entender qual elemento está buscando, ao usar ela.
    (sem falar que eu fiz essa função para um caso especifico do modal de busca de vendedor, as outras funções substituem essa facilmente)
    '''
    try:
        # aguarda invisibilidade de qualquer loading overlay
        WebDriverWait(DRIVER, timeout).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, ".el-loading-mask"))
        )
        # espera o botão ficar clicável
        button = WebDriverWait(DRIVER, timeout).until(
            EC.element_to_be_clickable((by, value))
        )
        sleep(1.2)  # tempo de espera
        button.click()
        return button
    except Exception as e:
        print(f"{Fore.RED}Erro ao clicar no botão {value}: {e}")
        raise e