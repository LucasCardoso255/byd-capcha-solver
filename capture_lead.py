from colorama import Fore
from utils import Condition, get_element, get_elements, wait_loading_to_disappear, click_when_ready,DRIVER
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys

lead_data = []
USERNAME_GLOBAL = None

def capture_leads():
    LEADBUTTON = get_element(Condition.CLICKABLE, By.XPATH, '/html/body/div[1]/div[2]/div/div/div/div[1]/div[1]/div/div/div[2]/div[1]/div')
    LEADBUTTON.click()
    print(f'{Fore.YELLOW}Acessando página de leads...')
    verify_lead()

# função de busca de leads pendentes
def verify_lead():

    increase_page_size()

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

def increase_page_size():
    PAGE_SIZE_DROPDOWN = get_element(Condition.CLICKABLE, By.XPATH, '/html/body/div[1]/div[1]/div[1]/div/div/div[2]/div[1]/div[2]/div[3]/div/span[2]/div/div[1]/input')
    PAGE_SIZE_DROPDOWN.click()
    print(f'{Fore.YELLOW}Aumentando tamanho da página para 100 itens...')

    OPTION_100 = get_element(Condition.CLICKABLE, By.XPATH, '/html/body/div[3]/div[1]/div[1]/ul/li[4]')
    OPTION_100.click()

def get_data(coluna3: WebElement):
    
    wait_loading_to_disappear()

    a = get_element(Condition.CLICKABLE, By.TAG_NAME, 'a', element=coluna3)

    if a.is_displayed():
        a.click()
        print(f'{Fore.YELLOW}Lendo dados do lead...')
        append_data()
        append_vendor()

    else:
        print(f'{Fore.RED}Elemento "a" não encontrado')

# pegando os dados do lead e dando append na lista
def append_data():

    try:
        elemento_nome = get_element(Condition.PRESENCE, By.CSS_SELECTOR, '.use-name span')
        nome = elemento_nome.text
        print(f'{Fore.BLUE}Nome do lead encontrado: {nome}')

        elemento_email = get_element(Condition.PRESENCE, By.CSS_SELECTOR, '.base-info-content span:nth-of-type(2)' )
        email = elemento_email.text
        print(f'{Fore.BLUE}Email do lead encontrado: {email}')
        
        elemento_produto = get_element(Condition.PRESENCE, By.CSS_SELECTOR, 'div.info-content:nth-child(2) > div:nth-child(3) > span:nth-child(2)')
        produto = elemento_produto.text
        print(f'{Fore.BLUE}Produto de interesse encontrado: {produto}')

        elemento_observacoes = get_element(Condition.PRESENCE, By.CSS_SELECTOR, 'div.info-content:nth-child(2)')
        spans = elemento_observacoes.find_elements(By.TAG_NAME, "span")
        observacoes = [s.text for s in spans]
        print(f'{Fore.BLUE}Observações preenchidas: {observacoes}')

        lead_data.append({
            "nome": nome,
            "email": email,
            "produto": produto,
            "observacoes": observacoes
        })
        print(f'{Fore.GREEN}Dados do lead capturados com sucesso')

    except Exception as e:
        print(f"Erro ao capturar o lead: {e}")

def append_vendor():
    ASSIGNMENT_BUTTON = get_element(
        Condition.CLICKABLE,
        By.XPATH,
        "//button[span[text()=' Lead Assignment ']]"
    )

    ASSIGNMENT_BUTTON.click()
    print(f'{Fore.YELLOW}Atribuindo vendedor...')

    wait_loading_to_disappear()
    input_wrapper = click_when_ready(By.XPATH, "/html/body/div[6]/div/div[2]/div/div[2]/div[1]/div/form/div/div/div[1]/div/div") # caixa de pesquisa de vendedor

    input_name = input_wrapper.find_element(By.TAG_NAME, "input")
    input_name.send_keys(USERNAME_GLOBAL)
    print(f'{Fore.YELLOW}Procurando vendedor: {USERNAME_GLOBAL}...')
    BUTTONS = get_elements(By.TAG_NAME, "button")
    
    queryButtons = [btn for btn in BUTTONS if btn.text.strip().lower() == "query"]
    
    if not queryButtons:
        print(f'{Fore.RED}Botão de consulta não encontrado')
        return
    else:
        print(f'{Fore.GREEN}{len(queryButtons)} botões de consulta encontrados:')
        print(f'{Fore.GREEN}{[btn for btn in queryButtons]}')

    QUERY_BUTTON = queryButtons[-1]  # seleciona o último botão "Query"
    QUERY_BUTTON.click()
    print(f'{Fore.YELLOW}Clicando no botão de consulta...')


    assign_vendor_tbody = get_element(Condition.PRESENCE, By.XPATH, "//table[contains(@class, 'el-table__body')]//tbody")
    VENDOR_SELECT_BUTTON = assign_vendor_tbody.get_elements(By.CSS_SELECTOR, 'input.el-radio__original')
    
    click_when_ready(VENDOR_SELECT_BUTTON)
    
    tabs_sequence = Keys.TAB * 11
    input_name.send_keys(tabs_sequence + Keys.SPACE)

    FINISH_ASSIGN = get_element(Condition.CLICKABLE,By.XPATH, '/html/body/div[12]/div/div[3]/div/button[2]')
    FINISH_ASSIGN.click()
        # tabs: 8
        # e depois: 4

