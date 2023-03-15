from lxml import etree
import lxml.html
import os
import re
import shutil


def copy_index(source_path, dest_path):
    shutil.copy(source_path, dest_path)


def simplify_html(dest_path):
    tree = lxml.html.parse(dest_path)
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
        dest_path,
        pretty_print=True,
        encoding='utf-8',
        method='html'
    )


if __name__ == "__main__":
    source_folder = input("Source folder: ").replace(" ", r"\ ")
    source_name = input("Source name: ").replace(" ", r"\ ")
    source_path = os.path.join(source_folder, source_name)
    dest_folder = input("Destination folder: ").replace(" ", r"\ ")
    dest_name = input("Destination name: ").replace(" ", r"\ ")
    dest_path = os.path.join(dest_folder, dest_name)
    copy_index(source_path, dest_path)
    simplify_html(dest_path)
    print(f"Simplified '{source_path}' -> '{dest_path}'")
