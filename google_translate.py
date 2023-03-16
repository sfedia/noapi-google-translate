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


class GlobalCounter:
    def __init__(self, total):
        self.total = total
        self.translated = 0

    @property
    def percentage(self):
        return self.translated / self.total * 100


def translate_chain(driver, input_box, paragraphs, debug_mode):
    prev = None
    for par in paragraphs:
        if debug_mode:
            print(f"Current paragraph: '{par}'")
        if not par or par == " " or re.search(r'^[\d ]+$', par):
            prev = par
            yield par
            continue
        input_box.send_keys(par)
        selected_span = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, '[aria-live="polite"] div div span')
            )
        )
        t = 0
        while t < 5 and prev == selected_span.get_attribute('innerText'):
            time.sleep(0.1)
            if debug_mode:
                print('t =', t)
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


  
def start_translator(source, min_element, max_element, destination, headless, debug_mode, source_lang, dest_lang):
    global global_counter
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument('--log-level=3')
    if headless:
        options.add_argument('--headless')

    driver = webdriver.Chrome(executable_path="chromedriver",
                              chrome_options=options)
    driver.set_window_size(1920,1080)

    driver.get('https://translate.google.com/?sl={}&tl={}'.format(source_lang, dest_lang))
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
    for result in translate_chain(driver, input_box, paragraphs, debug_mode):
        target_elements[i + min_element].text = result
        target_elements[i + min_element].tail = ""
        while target_elements[i + min_element].getchildren():
            target_elements[i + min_element].remove(target_elements[i + min_element].getchildren()[0])
        target_elements[i + min_element].classes.remove('target-text')
        target_elements[i + min_element].classes.add('target-text-modified')
        if debug_mode:
            print("Result:", result)
        global_counter.translated += 1
        if not i % 5:
            tree.write(
                destination,
                pretty_print=True,
                encoding='utf-8',
                method='html'
            )
            if debug_mode:
                print("Saving on i = ", i + min_element)
            print(f"Progress: {round(global_counter.percentage, 2)}%")
        i += 1
    tree.write(
        destination,
        pretty_print=True,
        encoding='utf-8',
        method='html'
    )



def start_parallelized_translator(
        source_path, dest_path, paragraphs_count, workers_count = 4, debug_mode = False, source_language = "ru", dest_language = "de"):
    step = round(paragraphs_count / workers_count)
    i = 0
    pairs = []
    while i < paragraphs_count:
        pairs.append([i, i + step])
        i += step

    print(f"Made slices for threads: {pairs}")
    threads = {}
    for i in range(workers_count):
        threads[i] = threading.Thread(
            target=start_translator, 
            args = (
                source_path, pairs[i][0], pairs[i][1], dest_path.replace("X", str(i + 1)),
                True, debug_mode, source_language, dest_language
            )
        )
    for i in range(workers_count):
        threads[i].start()
    for i in range(workers_count):
        threads[i].join()


if __name__ == "__main__":
    source_language_code = input("Source language (ru by default): ").strip()
    if not source_language_code:
        source_language_code = "ru"
    dest_language_code = input("Destination language (de by default): ").strip()
    if not dest_language_code:
        dest_language_code = "de"
    source_folder = input("Source folder: ")
    source_name = input("Source name: ")
    source_path = os.path.join(source_folder, source_name)
    paragraphs_count = len([par for par in provide_paragraphs(source_path)])
    print(f"Number of elements in the file: {paragraphs_count}")
    threaded = input("Use threaded translation? [y] ") != "n"
    if not threaded:
        from_page = int(input("From page: "))
        to_page = int(input("To page: "))
    dest_folder = input("Destination folder: ")
    dest_name = input("Destination name (should contain X for index substitution): ")
    dest_path = os.path.join(dest_folder, dest_name)
    headless = input("Headless? [y] ") != "n"
    debug_mode = input("Debug mode? [n] ") == "y"
    global_counter = GlobalCounter(paragraphs_count)
    if threaded:
        workers_count = input("Number of workers? (4 by default)").strip()
        if workers_count.isdigit():
            workers_count = int(workers_count)
        else:
            workers_count = 4
        start_parallelized_translator(
            source_path, dest_path, paragraphs_count, workers_count=workers_count, 
            debug_mode=False, source_language=source_language_code, dest_language=dest_language_code
        )
    else:
        start_translator(source_path, from_page, to_page, dest_path, headless, debug_mode, source_language_code, dest_language_code)
