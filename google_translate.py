from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import os
import lxml.html
import re
import threading


def translate_chain(driver, input_box, paragraphs):
    prev = None
    for par in paragraphs:
        print(f"Current paragraph: '{par}'")
        if not par or par == " " or re.search(r'^[\d ]+$', par):
            prev = par
            yield par
            continue
        input_box.send_keys(par)
        selected_span = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, '[aria-live="polite"] div div span')# span span')
            )
        )
        t = 0
        while t < 5 and prev == selected_span.get_attribute('innerText'):
            time.sleep(0.1)
            print('t=', t)
            t += 0.1
        prev = selected_span.get_attribute("innerText")
        input_box.send_keys(len(input_box.get_attribute("value")) * Keys.BACKSPACE)
        yield prev


def format_text(text):
    return re.sub(r'\s{2,}', " ", text)


def provide_paragraphs(source):
    tree = lxml.html.parse(
        source
    )
    text_elements = tree.xpath("//*[@class='target-text']")
    for elem in text_elements:
        yield format_text('\n'.join(elem.itertext()))


  
def start_translator(source, min_element, max_element, destination, headless):
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument('--log-level=3')
    if headless:
        options.add_argument('--headless')

    driver = webdriver.Chrome(executable_path="chromedriver",
                              chrome_options=options)
    driver.set_window_size(1920,1080)

    driver.get('https://translate.google.com/?sl=ru&tl=de')
    turn_off_input_method_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, '[aria-label="Turn off Input Method"]')
        )
    )
    turn_off_input_method_button.click()
    input_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "textarea[aria-label='Source text']")
        )
    )

    tree = lxml.html.parse(source)
    
    paragraphs = [par for par in provide_paragraphs(source)]
    paragraphs = paragraphs[min_element:max_element]
    target_elements = tree.xpath("//*[@class='target-text']")
    tree.write(
        destination,
        pretty_print=True,
        encoding='utf-8',
        method='html'
    )
    i = 0
    for result in translate_chain(driver, input_box, paragraphs):
        target_elements[i + min_element].text = result
        target_elements[i + min_element].tail = ""
        while target_elements[i + min_element].getchildren():
            target_elements[i + min_element].remove(target_elements[i + min_element].getchildren()[0])
        target_elements[i + min_element].classes.remove('target-text')
        target_elements[i + min_element].classes.add('target-text-modified')
        print("Result:", result)
        if not i % 5:
            tree.write(
                destination,
                pretty_print=True,
                encoding='utf-8',
                method='html'
            )
            print("Saving on i = ", i + min_element)
        i += 1
    tree.write(
        destination,
        pretty_print=True,
        encoding='utf-8',
        method='html'
    )



def start_parallelized_translator(source_path, dest_path, paragraphs_count, worker_count = 4):
    step = round(paragraphs_count / worker_count)
    i = 0
    pairs = []
    while i < paragraphs_count:
        pairs.append([i, i + step])
        i += step

    print(pairs)
    threads = {}
    for i in range(worker_count):
        threads[i] = threading.Thread(
            target=start_translator, 
            args = (source_path, pairs[i][0], pairs[i][1], dest_path.replace("X", str(i + 1)), True)
        )
    for i in range(worker_count):
        threads[i].start()
    for i in range(worker_count):
        threads[i].join()


if __name__ == "__main__":
    source_folder = input("Source folder: ")
    source_name = input("Source name: ")
    source_path = os.path.join(source_folder, source_name)
    paragraphs_count = len([par for par in provide_paragraphs(source_path)])
    print(f"Number of elements in the file: {paragraphs_count}")
    auto = input("Auto? [y] ") != "n"
    if not auto:
        from_page = int(input("From page: "))
        to_page = int(input("To page: "))
    dest_folder = input("Destination folder: ")
    dest_name = input("Destination name: ")
    dest_path = os.path.join(dest_folder, dest_name)
    headless = input("Headless? [y] ") != "n"
    if auto:
        start_parallelized_translator(source_path, dest_path, paragraphs_count)
    else:
        start_translator(source_path, from_page, to_page, dest_path, headless)
