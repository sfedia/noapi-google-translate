from lxml import etree
import lxml.html
import os
import re
import shutil


def subject_path(subject_name):
    return os.path.join(
        "Программы RU HTML",
        subject_name
    )

def copy_index(subject_name):
    shutil.copy(
        os.path.join(subject_path(subject_name), "index.html"),
        os.path.join(subject_path(subject_name), "modified.html")
    )

def simplify_html(subject_name):
    tree = lxml.html.parse(
        os.path.join(subject_path(subject_name), "modified.html")
    )
    n = 0
    for p_tag in tree.xpath('body/p'):
        t = ''.join(p_tag.itertext())
        for child in p_tag.xpath("*"):
            p_tag.remove(child)
        new_text = etree.SubElement(p_tag, "span")
        new_text.text = t
        new_text.set("class", "target-text")

    for td_tag in tree.xpath('//td'):
        t = '<p class="target-text">' + '<br>'.join(td_tag.itertext()) + '</p>'
        for child in td_tag.xpath("*"):
            td_tag.remove(child)
        td_tag.append(lxml.html.fragment_fromstring(t))

    tree.write(
        os.path.join(subject_path(subject_name), "modified.html"),
        pretty_print=True,
        encoding='utf-8',
        method='html'
    )
    print(n)

if __name__ == "__main__":
    subject = "Введение в компьютерную лингвистику"
    copy_index(subject)
    simplify_html(subject)
    print()
