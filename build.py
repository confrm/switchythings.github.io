#!/usr/bin/env python3

import glob
import os
import shutil
import toml

from pathlib import Path
from string import Template


def main():

    """ Create the output folder """
    if os.path.exists("build"):
        files = glob.glob('./build/*')
        for f in files:
            if os.path.isdir(f):
                shutil.rmtree(f)
            else:
                os.remove(f)
    else:
        os.mkdir("build")

    """ Copy in fixed assets """
    fixed_assets = ["favicon.ico", "robots.txt", "CNAME", "assets"]
    for asset in fixed_assets:
        if (os.path.isdir(asset)):
            shutil.copytree(asset, os.path.join("build", asset), False, None)
        else:
            shutil.copy(asset, os.path.join("build", asset))

    """ Find all the simple pages """
    # The array notation removes the "pages" dir from the generated path
    page_list = list(Path("./pages").rglob("*.[hH][tT][mM][lL]"))
    page_list_relative = [*map(lambda x: Path(*x.parts[1:]), page_list)]

    """ Get template items """
    with open("top.template", "r") as top_template_file:
        top_template = top_template_file.read()
    with open("bottom.template", "r") as bottom_template_file:
        bottom_template = bottom_template_file.read()

    """ Build templated pages """
    for page in page_list_relative:
        # Check to see if dirs need to be created
        path = "build"
        for element in page.parts:
            path = os.path.join(path, element)
            if not path.endswith(".html"):
                if os.path.exists(path) is False:
                    os.mkdir(path)
        with open(os.path.join("pages", page), "r") as file:
            content = file.read()
        with open(path, "w") as file:
            file.write(top_template)
            file.write(content)
            file.write(bottom_template)

    """ Find all the templated pages """
    template_page_list = list(Path("./pages").rglob("*.[tT][oO][mM][lL]"))
    template_page_list_relative = [*map(lambda x: Path(*x.parts[1:]), template_page_list)]

    for page in template_page_list_relative:
        path = "build"
        for element in page.parts:
            path = os.path.join(path, element)
            if not path.lower().endswith(".toml"):
                if os.path.exists(path) is False:
                    os.mkdir(path)
        with open(os.path.join("pages", page), "r") as file:
            template_content = toml.loads(file.read())
            if template_content['template']['name'] == "product":
                create_product(template_content, path, (top_template, bottom_template))

def build_product_spec(specifications, title, content):

    spec_table_header = "<table class=\"table table-striped\"><tbody>"
    spec_table_footer = "</table>"

    specifications += f"<h3 class=\"h5\">{title}</h3>"
    specifications += spec_table_header
    for spec in content:
        specifications += f"<tr><td class=\"text-muted w-50\">{spec}</td><td>{content[spec]}</td></tr>"
    specifications += spec_table_footer

    return specifications

def create_product(content, path, wrapper):

    path = os.path.splitext(path)[0]+".html"

    with open("product.template", "r") as file:
        template_string = file.read()
    template = Template(template_string)

    specifications = build_product_spec("", "Base", content['specifications'])
    options_list = ""

    description = f"<p>{content['product']['description']}</p>"
    for option in content['options']:
        option_content = content['options'][option]
        options_list += f"<li>{option_content['title']} (${option_content['price']})</li>\n"
        description += f"<strong>{option_content['title']}</strong><p>{option_content['description']}</p>" 
        if "specifications" in option_content.keys():
            specifications = build_product_spec(specifications, option_content['title'], option_content['specifications'])

    file = open(path, "w")
    file.write(wrapper[0])
    file.write(template.substitute(
        title = content['product']['title'],
        sku = content['product']['sku'],
        price = content['product']['price'],
        description = description,
        specifications = specifications,
        options = options_list
    ))
    file.write(wrapper[1])
    file.close()

    print(content)

if __name__ == "__main__":
    main()