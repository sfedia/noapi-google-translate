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
from html_translator import subject_path


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


def provide_paragraphs(subject_name):
    tree = lxml.html.parse(
        os.path.join(subject_path(subject_name), "modified.html")
    )
    text_elements = tree.xpath("//*[@class='target-text']")
    for elem in text_elements:
        yield format_text('\n'.join(elem.itertext()))


  
if __name__ == '__main__':

    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument('--log-level=3')

    driver = webdriver.Chrome(executable_path="chromedriver",
                              chrome_options=options)
    driver.set_window_size(1920,1080)

    driver.get('https://translate.google.com/?sl=ru&tl=de')
    input_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "textarea[aria-label='Source text']")
        )
    )

    subject_name = "Введение в компьютерную лингвистику"
    tree = lxml.html.parse(
        os.path.join(subject_path(subject_name), "modified.html")
    )
    
    paragraphs = [par for par in provide_paragraphs(subject_name)]
    target_elements = tree.xpath("//*[@class='target-text']")
    tree.write(
        os.path.join(subject_path(subject_name), "modified.html"),
        pretty_print=True,
        encoding='utf-8',
        method='html'
    )
    i = 0
    for result in translate_chain(driver, input_box, paragraphs):
        target_elements[i].text = result
        target_elements[i].classes.remove('target-text')
        target_elements[i].classes.add('target-text-modified')
        print("Result:", result)
        if not i % 5:
            tree.write(
                os.path.join(subject_path(subject_name), "modified.html"),
                pretty_print=True,
                encoding='utf-8',
                method='html'
            )
            print("Saving on i = ", i)
        i += 1
    tree.write(
        os.path.join(subject_path(subject_name), "modified.html"),
        pretty_print=True,
        encoding='utf-8',
        method='html'
    )
    

