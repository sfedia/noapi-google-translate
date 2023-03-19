import lxml.html
import os
import argparse


def is_thread_file(filename, prefix_name):
    return filename.startswith(prefix_name) and filename[len(prefix_name)].isdigit()


def merge_files(source_folder, prefix_name):
    fls = [fl for fl in os.listdir(source_folder) if is_thread_file(fl, prefix_name)]
    meta_list = {}
    for merged_file in fls:
        tree = lxml.html.parse(os.path.join(source_folder, merged_file))
        catch_elements = tree.xpath("//*[contains(@class, 'target-text')]")
        for n, elem in enumerate(catch_elements):
            while elem.getchildren():
                elem.remove(elem.getchildren()[0])
            if n not in meta_list:
                meta_list[n] = elem
            elif "target-text" in meta_list[n].classes and "target-text-modified" in elem.classes:
                meta_list[n] = elem

    num_total = len(meta_list)
    num_translated = len([meta_list[n] for n in meta_list if "target-text-modified" in meta_list[n].classes])
    print(f"{num_translated} / {num_total} = {num_translated / num_total * 100}%")
    for i in range(num_total):
        catch_elements[i].text = meta_list[i].text
        catch_elements[i].classes = meta_list[i].classes

    tree.write(
        os.path.join(source_folder, f"{prefix_name}-merged.html"),
        pretty_print=True,
        encoding='utf-8',
        method='html'
    )
    
    print(f"Merged into '{os.path.join(source_folder, f'{prefix_name}-merged.html')}'")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="merge_translations.py")
    parser.add_argument("-p", "--prompt", action="store_true")
    parser.add_argument("--source-folder")
    parser.add_argument("--prefix-name")
    args = parser.parse_args()

    if args.prompt:
        source_folder = input("Source folder: ")
        prefix_name = input("Prefix name: ")
    else:
        source_folder = args.source_folder
        prefix_name = args.prefix_name

    merge_files(source_folder, prefix_name)
