from lxml import etree
import lxml.html
import os
import re
import shutil
import argparse


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
    parser = argparse.ArgumentParser(prog="html_simplifier.py")
    parser.add_argument("-p", "--prompt", action="store_true")
    parser.add_argument("--source-folder")
    parser.add_argument("--source-name")
    parser.add_argument("--dest-folder")
    parser.add_argument("--dest-name")

    args = parser.parse_args()

    if args.prompt:
        source_folder = input("Source folder: ")
        source_name = input("Source name: ")
        dest_folder = input("Destination folder: ")
        dest_name = input("Destination name: ")
    else:
        source_folder = args.source_folder
        source_name = args.source_name
        dest_folder = args.dest_folder
        dest_name = args.dest_name

    source_path = os.path.join(source_folder, source_name)
    dest_path = os.path.join(dest_folder, dest_name)
    copy_index(source_path, dest_path)
    simplify_html(dest_path)
    print(f"Simplified '{source_path}' -> '{dest_path}'")
