from datetime import datetime
from os.path import isfile, join
from jinja2 import Template
from pytz import timezone
import markdown2, os

def convertMDtoHTML(md_text):
    html_text = markdown2.markdown(md_text, extras=[
        "footnotes", 
        "fenced-code-blocks", 
        "tables", 
        "markdown-in-html",
        "target-blank-links"
    ])
    return html_text

def writeHTMLtoFILE(filename, content):
    indexFile = open("./{}.html".format(filename), "w+")
    indexFile.write(content)
    indexFile.close()

def writeContentToTemplate(filename, templateHtml, props=None):
    with open("./site_templates/{}Template.html".format(filename), "r") as f :
        contentHtml = f.read() 
        if props != None:
            contentHtml = Template(contentHtml).render(props)
        renderedResult = Template(templateHtml).render({"content": contentHtml})
        writeHTMLtoFILE(filename, renderedResult)

def main():
    print("[+] Running all sites creation sequence")

    baseFile = open("./site_templates/baseTemplate.html", "r")
    baseHtml = baseFile.read()

    print("[+] Creating index page")
    writeContentToTemplate("index", baseHtml)
        
    print("[+] Creating contact page")
    writeContentToTemplate("contact", baseHtml)
        
    print("[+] Creating notes page")
    writeContentToTemplate("notes", baseHtml)

    print("[+] Creating about-us page")
    with open("./data/profiles.txt", "r") as f:
        profilesContent = f.read()
        profilesContent = profilesContent.split("===")

        profiles = []
        for profile in profilesContent:
            props = {}
            props["contacts"] = {}

            for line in profile.split("\n"):
                if line != "":
                    if line.split(":")[0] != "contact":
                        props[line.split(": ")[0]] = line.split(": ")[1]
                    else :
                        props["contacts"][line.split(":")[1]] = line.split(": ")[1]

            profiles.append(props)

        writeContentToTemplate("aboutus", baseHtml, {
            "profiles": profiles
        })
        
    print("[+] Creating news page")
    writeContentToTemplate("news", baseHtml)
        
    print("[+] Creating writeup page")
    writeContentToTemplate("writeup", baseHtml)

if __name__ == "__main__" :
    main()