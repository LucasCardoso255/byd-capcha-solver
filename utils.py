import enum
import math
import os
import unicodedata
from time import sleep, time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.remote.webelement import WebElement
from colorama import Fore, init
import capture_lead as cl
from selenium.common.exceptions import TimeoutException


class Condition(enum.Enum):
    CLICKABLE = "clickable"
    PRESENCE = "presence"
    NO_WAIT = "no_wait"

DRIVER_PATH = '/home/lydia-server/Documentos/crawler-byd/byd-capcha-solver/Driver/geckodriver'
DRIVER_PATH = os.path.abspath(DRIVER_PATH)
options = Options()
options.binary_location = "/usr/bin/firefox"
options.add_argument("--headless") # Adicione esta linha
DRIVER = webdriver.Firefox(service=Service(DRIVER_PATH), options=options)
    
# espera por {cond} e pega o elemento
def get_element(cond, by, value, timeout=90, element=DRIVER):
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
def get_elements(by, value, timeout=90, element=DRIVER):
    try:
        TIMEOUT=timeout
        return WebDriverWait(element, TIMEOUT).until(EC.presence_of_all_elements_located((by, value)))
        
    except Exception as e:
        print(f"{Fore.RED}Erro ao localizar o elemento: {value} - {str(e)}")
        raise e

# aguarda o loading desparecer antes de prosseguir
def wait_loading_to_disappear():
    try:
        WebDriverWait(DRIVER, timeout=90).until(
            EC.invisibility_of_element_located((By.CLASS_NAME, "el-loading-mask"))
        )
    except:
        pass  # se não desaparecer em timeout, continua

# função caso o loading tenha animação de fade
def click_when_ready(by, value, timeout=90):
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
    

def get_last_element_by_content(by, value, content, first=False):
    ELEMENTS = get_elements(by, value)
    filtered_elements = [el for el in ELEMENTS if content in el.text]
    if not filtered_elements:
        raise Exception(f"Nenhum elemento encontrado com o conteúdo: {content}")
    if first == True:
        return filtered_elements[0] # gambiarra
    return filtered_elements[-1]

def wait_until_clickable(element, timeout=20, check_interval=0.3):
    """
    Espera até que o elemento esteja visível, habilitado e sem nada obstruindo o clique.
    Usa document.elementsFromPoint() para checar se há algo na frente.
    """

    print(f"{Fore.YELLOW}Aguardando o elemento <{element.tag_name}> ficar clicável...")
    end_time = time() + timeout

    while time() < end_time:
        try:
            # Centraliza o elemento na tela
            DRIVER.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", element
            )

            # Pega as coordenadas do centro do elemento
            rect = DRIVER.execute_script("""
                const r = arguments[0].getBoundingClientRect();
                return {x: r.x + r.width/2, y: r.y + r.height/2};
            """, element)

            x, y = rect["x"], rect["y"]

            # Pega os elementos visuais na posição do centro
            front_elements = DRIVER.execute_script("""
                return document.elementsFromPoint(arguments[0], arguments[1])
                    .map(e => e.outerHTML.slice(0, 80));
            """, x, y)

            # O primeiro da lista deve ser o próprio elemento ou um filho dele
            is_top = DRIVER.execute_script("""
                const el = arguments[0];
                const r = el.getBoundingClientRect();
                const topEl = document.elementFromPoint(r.x + r.width/2, r.y + r.height/2);
                return el === topEl || el.contains(topEl);
            """, element)

            if is_top:
                print(f"{Fore.GREEN}Elemento <{element.tag_name}> está clicável!")
                return element
            else:
                # Opcional: depuração (quem está na frente)
                front_top = front_elements[0] if front_elements else "desconhecido"
                print(f"{Fore.RED}Ainda obstruído por: {front_top}")
                sleep(check_interval)

        except Exception as e:
            # Pode ocorrer se o elemento mudar de posição, ser recriado etc.
            print(f"{Fore.RED}Esperando elemento válido... ({e.__class__.__name__})")
            sleep(check_interval)

    raise TimeoutException(
        f"O elemento <{element.tag_name}> permaneceu obstruído após {timeout}s."
    )

def refresh_page():
    print(f"{Fore.YELLOW}Atualizando a página...")
    DRIVER.refresh()
    wait_page_ready()

def wait_page_ready():
    WebDriverWait(DRIVER, 30).until(lambda driver: driver.execute_script("return document.readyState") == "complete")

def normalize_text(text: str) -> str:
    """
        Função para normalizar o ' : ' desse site chines safado que usa caracteres fora do padrão.  
    """
    return text.replace("：", ":").strip() 