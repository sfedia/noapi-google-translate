import lxml.html
import os


def merge_files(source_folder, prefix_name):
    fls = [fl for fl in os.listdir(source_folder) if fl.startswith(prefix_name) and fl[len(prefix_name)] not in [".", "-"]]
    meta_list = {}
    for merged_file in fls:
        tree = lxml.html.parse(os.path.join(source_folder, merged_file))
        catch_elements = tree.xpath("//*[contains(@class, 'target-text')]")
        import ipdb; ipdb.set_trace();
        for n, elem in enumerate(catch_elements):
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
    
    print(f'Merged in {os.path.join(source_folder, f"{prefix_name}-merged.html")}')



if __name__ == "__main__":
    source_folder = input("Source folder: ").replace(" ", r"\ ")
    prefix_name = input("Prefix name: ").replace(" ", r"\ ")
    merge_files(source_folder, prefix_name)

