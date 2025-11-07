import json
import os
import requests
from colorama import Fore
from utils import Condition, get_element, get_elements, wait_loading_to_disappear, click_when_ready,DRIVER, get_last_element_by_content, wait_until_clickable, refresh_page
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

USERNAME_GLOBAL = None

def capture_leads():
    
    LEADBUTTON = get_element(Condition.CLICKABLE, By.XPATH, '/html/body/div[1]/div[2]/div/div/div/div[1]/div[1]/div/div/div[2]/div[1]/div')
    LEADBUTTON.click()
    
    print(f'{Fore.YELLOW}Acessando página de leads...')
    
    while verify_lead() == True: # essa função faz tudo, atribui vendedor, pega os dados do lead e etc
        refresh_page()

def json_write_data(body):
    os.makedirs("json", exist_ok=True)
    caminho_arquivo = os.path.join("json", "leads.json")

    # Se o arquivo existir, lê os dados anteriores
    if os.path.exists(caminho_arquivo):
        with open(caminho_arquivo, "r", encoding="utf-8") as f:
            try:
                dados = json.load(f)
            except json.JSONDecodeError:
                dados = []  # se estiver vazio ou corrompido
    else:
        dados = []

    # adiciona o novo dado
    dados.append(body)

    # grava tudo de volta
    with open(caminho_arquivo, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

    print(f"{Fore.GREEN}Arquivo salvo em: {caminho_arquivo}")

# função de busca de leads pendentes
def verify_lead():

    # increase_page_size()
    red_leads_filter()

    # achando o tbody da lista de leads
    TBODY = get_element(Condition.PRESENCE, By.XPATH, '/html/body/div[1]/div[1]/div[1]/div/div/div[2]/div[1]/div[2]/div[2]/div[4]/div[2]/table/tbody') 
    print(f'{Fore.GREEN}TBODY encontrado')

    # achando cada linha do tbody
    linhas = get_elements(By.TAG_NAME, 'tr', element=TBODY)

    for linha in linhas:
        colunas = get_elements(By.TAG_NAME, 'td', element=linha) # retorna um array com todas as colunas (td)
        coluna2 = colunas[1] # pegando a segunda coluna da tr
        span = get_elements(By.TAG_NAME, 'span', element=coluna2)[0]
        
        if 'redCircle' in span.get_attribute("class").split():
            coluna3 = colunas[2] # pegando a terceira coluna, que contém o link com os dados do lead
            print(f'{Fore.BLUE}Lead pendente de captura encontrado')
            get_data(coluna3)
            return True
    return False

# def increase_page_size():
#     PAGE_SIZE_DROPDOWN = get_element(Condition.CLICKABLE, By.XPATH, '/html/body/div[1]/div[1]/div[1]/div/div/div[2]/div[1]/div[2]/div[3]/div/span[2]/div/div[1]/input')
#     PAGE_SIZE_DROPDOWN.click()
#     print(f'{Fore.YELLOW}Aumentando tamanho da página para 100 itens...')

#     OPTION_100 = get_element(Condition.CLICKABLE, By.XPATH, '/html/body/div[3]/div[1]/div[1]/ul/li[4]')
#     OPTION_100.click()

def get_data(coluna3: WebElement):
    
    wait_loading_to_disappear()

    a = get_element(Condition.CLICKABLE, By.TAG_NAME, 'a', element=coluna3)

    if a.is_displayed():
        url_lead = a.text
        a.click()
        print(f'{Fore.YELLOW}Lendo dados do lead...')
        body = append_data(url_lead)
        append_vendor()
        contact_assign()
        json_write_data(body)
        post_data_to_api(body)

    else:
        print(f'{Fore.RED}Elemento "a" não encontrado')

# pegando os dados do lead e dando append na lista
def append_data(url_lead):
    try:
        elemento_nome = get_element(Condition.PRESENCE, By.CSS_SELECTOR, '.use-name span')
        name = elemento_nome.text
        print(f'{Fore.BLUE}Nome do lead encontrado: {name}')

        phone_element = get_element(Condition.PRESENCE, By.CSS_SELECTOR, 'div.use-base-info-item:nth-child(2) > div:nth-child(2) > span:nth-child(2)' )
        phone = int(phone_element.text)
        print(f'{Fore.BLUE}Telefone do lead encontrado: {phone}')

        elemento_email = get_element(Condition.PRESENCE, By.CSS_SELECTOR, '.base-info-content span:nth-of-type(2)' )
        email = elemento_email.text
        print(f'{Fore.BLUE}Email do lead encontrado: {email}')
                
        elemento_produto = get_element(Condition.PRESENCE, By.CSS_SELECTOR, 'div.info-content:nth-child(2) > div:nth-child(3) > span:nth-child(2)')
        produto = elemento_produto.text
        print(f'{Fore.BLUE}Produto de interesse encontrado: {produto}')

        mall_element = get_element(Condition.PRESENCE, By.CSS_SELECTOR, '#pane-baseInfo > div:nth-child(1) > div:nth-child(1) > div:nth-child(6) > div:nth-child(2) > div:nth-child(1)')
        mall = mall_element.text
        print(f'{Fore.BLUE}Shopping encontrado: {mall}')

        createdat_element = get_element(Condition.PRESENCE, By.CSS_SELECTOR, 'div.content-info-item:nth-child(21) > div:nth-child(2) > div:nth-child(1)')
        created_at = createdat_element.text
        print(f'{Fore.BLUE}Data de criação encontrada: {created_at}')

        leadtype_element = get_element(Condition.PRESENCE, By.CSS_SELECTOR, '#pane-baseInfo > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(2) > div:nth-child(1)')
        leadtype = leadtype_element.text
        print(f'{Fore.BLUE}Tipo de lead encontrado: {leadtype}')

        suborigin_element = get_element(Condition.PRESENCE, By.CSS_SELECTOR, '#pane-baseInfo > div:nth-child(1) > div:nth-child(1) > div:nth-child(3) > div:nth-child(2) > div:nth-child(1)')
        suborigin = suborigin_element.text
        print(f'{Fore.BLUE}Suborigem encontrada: {suborigin}')

        elemento_observacoes = get_element(Condition.PRESENCE, By.CSS_SELECTOR, 'div.info-content:nth-child(2)')
        spans = elemento_observacoes.find_elements(By.TAG_NAME, "span")
        # normaliza o texto das observacoes
        observacoes = ", ".join(
            s.text.strip() for s in spans if s.text.strip()
        )

        print(f'{Fore.BLUE}Observações normalizadas: {observacoes}')

        # Vamos pegar pelo JSON recebido futuramente porem por enquanto Hard-Coded
        if USERNAME_GLOBAL == "KaremM.Teresina":
            camp_id = 41747
        elif USERNAME_GLOBAL == "Brena.Morais":
            camp_id = 41746
        else:
            camp_id = 0
            
        body = {
            "name": name,
            "phone": str(phone),
            "email": email,
            "productid": produto,
            "mall": mall,
            "createdAt": created_at,
            "urllead": url_lead,
            "leadtype": leadtype,
            "suborigin": suborigin,
            "details": observacoes,
            "source": 201,
            "CampaignId": camp_id,
            "people_mail": ""
        }
        
        print(f'{Fore.GREEN}Dados do lead capturados com sucesso!')
        print(f'{Fore.YELLOW}Dados do lead: {body}')
        
        return body

    except Exception as e:
        print(f"Erro ao capturar o lead: {e}")
        raise e

def post_data_to_api(lead):
    API_URL = "https://api.lydia.com.br/lead"
    CONTENT_TYPE = "application/json"
    AUTHORIZATION = "Bearer 0458d5361721652a0b8182c8f2eeecab126e942f"
    headers = {
    "Content-Type": CONTENT_TYPE,
    "Authorization": AUTHORIZATION
    }
      
    try:
        response = requests.post(API_URL, headers=headers, json=lead)
        if response.status_code == 201 or response.status_code == 200:
            print(f"{Fore.GREEN}Lead enviado com sucesso: {lead['name']}")
        else:
            print(f"{Fore.RED}Falha ao enviar lead: {lead['name']}. Status Code: {response.status_code}, Response: {response.text}")
    except Exception as e:
        print(f"{Fore.RED}Erro ao enviar lead: {lead['name']}. Erro: {str(e)}")


def append_vendor():
    ASSIGNMENT_BUTTON = get_element(Condition.CLICKABLE,By.XPATH,"//button[span[text()=' Lead Assignment ']]")

    ASSIGNMENT_BUTTON.click()
    print(f'{Fore.YELLOW}Atribuindo vendedor...')

    wait_loading_to_disappear()
    
    input_wrapper = click_when_ready(By.XPATH, "/html/body/div[6]/div/div[2]/div/div[2]/div[1]/div/form/div/div/div[1]/div/div") # caixa de pesquisa de vendedor

    input_name = input_wrapper.find_element(By.TAG_NAME, "input")
    input_name.send_keys(USERNAME_GLOBAL)
    print(f'{Fore.YELLOW}Procurando vendedor: {USERNAME_GLOBAL}...')

    QUERY_BUTTON = get_last_element_by_content(By.TAG_NAME, "button", "Query")
    QUERY_BUTTON.click()
    print(f'{Fore.YELLOW}Carregando consulta...')

    wait_loading_to_disappear()
    tBody = get_element(Condition.PRESENCE, By.XPATH, "/html/body/div[6]/div/div[2]/div/div[2]/div[2]/div[2]/div[4]/div[2]/table/tbody")
    first_row = get_elements(By.TAG_NAME, "tr", element=tBody)[0]
    first_col = get_elements(By.TAG_NAME, "td", element=first_row)[0]
    radio_label = get_elements(By.TAG_NAME, "label", element=first_col)[0]
    wait_until_clickable(radio_label)
    radio_label.click()
    print(f'{Fore.YELLOW}Vendedor selecionado.')

    CONFIRM_BUTTON = get_last_element_by_content(By.TAG_NAME, "button", "Assignment")
    CONFIRM_BUTTON.click()
    print(f'{Fore.GREEN}Vendedor atribuído com sucesso.')

def contact_assign():
    print(f'{Fore.BLUE}Iniciando atribuição de vendedor.')

    fu_record = get_element(Condition.CLICKABLE, By.XPATH, '//*[@id="tab-followRecords"]')
    wait_until_clickable(fu_record)
    fu_record.click()

    ADD_TRACK = get_last_element_by_content(By.TAG_NAME, 'button', 'Add Track')
    ActionChains(DRIVER).move_to_element(ADD_TRACK).click_and_hold().perform()
    ActionChains(DRIVER).release().perform()
    
    ZAP = get_element(Condition.CLICKABLE, By.XPATH, '/html/body/ul/li[4]')
    wait_until_clickable(ZAP)
    ZAP.click()
    
    EVENT_TIME = get_element(Condition.CLICKABLE, By.CSS_SELECTOR, "input.el-input__inner[placeholder='Event Time']")
    EVENT_TIME.click()

    EVENT_TIME_OK_BUTTON = get_element(Condition.CLICKABLE, By.XPATH, "//button[span[normalize-space()='OK']]")
    EVENT_TIME_OK_BUTTON.click()

    CONTACT_TEXT = get_element(Condition.PRESENCE, By.CSS_SELECTOR, "textarea.el-textarea__inner[placeholder='Content']")
    CONTACT_TEXT.click()
    CONTACT_TEXT.send_keys("Contato Realizado.")

    print(f'{Fore.BLUE}Atribuindo atendimento...')
    SAVE_BUTTON = get_last_element_by_content(By.TAG_NAME, 'button', 'Save')
    SAVE_BUTTON.click()
    print(f'{Fore.GREEN}Lead atendido com sucesso')

def red_leads_filter():
    MORE_BUTTON = get_element(Condition.CLICKABLE, By.XPATH, '/html/body/div[1]/div[1]/div[1]/div/div/div[2]/div[1]/div[1]/div/button/span')
    wait_until_clickable(MORE_BUTTON)
    MORE_BUTTON.click()

    STATUS_BUTTON = get_element(Condition.CLICKABLE, By.XPATH, '/html/body/div[1]/div[1]/div[1]/div/div/div[2]/div[1]/div[1]/div/form/div/div/div[21]/div/div/div[1]/input')
    STATUS_BUTTON.click()
    
    # espera o item "To be assigned" ficar clicável dentro do dropdown visível
    RED_FILTER_BUTTON = get_element(Condition.CLICKABLE,By.XPATH,"//div[contains(@class, 'el-select-dropdown') and not(contains(@style,'display: none'))]""//li[span[normalize-space(text())='To be assigned']]")

    wait_until_clickable(RED_FILTER_BUTTON)
    RED_FILTER_BUTTON.click()

    SEARCH_FILTERS = get_element(Condition.CLICKABLE,By.XPATH, '/html/body/div[1]/div[1]/div[1]/div/div/div[2]/div[1]/div[1]/div/form/div/div/div[32]/button[1]')
    SEARCH_FILTERS.click()