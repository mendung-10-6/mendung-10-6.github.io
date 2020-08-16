from os.path import isfile, join
from slugify import slugify
from jinja2 import Template
from glob import glob
import markdown2, os, pathlib

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

def writeContentToTemplate(filename, templateHtml, isContent=False, filenameOutput=None, props=None):
    with open("./site_templates/{}Template.html".format(filename + ("Content" if isContent else "")), "r") as f :
        contentHtml = f.read() 
        if props != None:
            contentHtml = Template(contentHtml).render(props)
        renderedResult = Template(templateHtml).render({"content": contentHtml})
        writeHTMLtoFILE(filename if filenameOutput == None else filenameOutput, renderedResult)

def main():
    print("[+] Running all sites creation sequence")

    baseFile = open("./site_templates/baseTemplate.html", "r")
    baseHtml = baseFile.read()

    print("[+] Creating index page")
    writeContentToTemplate("index", baseHtml)
        
    print("[+] Creating contact page")
    writeContentToTemplate("contact", baseHtml)
        
    print("[+] Creating notes page")
    with open("./data/notes.md", "r") as f:
        notesContent = f.read()
        notes = markdown2.markdown(notesContent, extras = [
            "footnotes", 
            "fenced-code-blocks", 
            "tables", 
            "markdown-in-html",
            "target-blank-links"
        ])
        writeContentToTemplate("notes", baseHtml, props={
            "notes": notes
        })

    print("[+] Creating about-us page")
    with open("./data/profiles.txt", "r") as f:
        profilesContent = f.read()
        profilesContent = profilesContent.split("===")
        
        print("[|] Found {} profile(s)".format(len(profilesContent)))

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

        writeContentToTemplate("aboutus", baseHtml, props={
            "profiles": profiles
        })
        
    print("[+] Creating news page")
    allNews = [f for f in os.listdir("./news") if isfile(join("./news", f))]
    allNews = [f.split(".md")[0] for f in allNews if f.split(".")[-1] == "md" and f != "format_news.md"]

    allNewsProps = []
    for news in allNews :
        print("[|] Working on '{}'".format(news))

        props = {
            "title": news,
            "slug": slugify(news)
        }
        allNewsProps.append(props)
        
        with open("./news/{}.md".format(news), "r") as newsFile:
            newsContent = newsFile.read()

            newsMd = newsContent.split("===\n")[1]
            newsMeta = newsContent.split("===\n")[0]
            newsHtml = markdown2.markdown(newsMd, extras = [
                "footnotes", 
                "fenced-code-blocks", 
                "tables", 
                "markdown-in-html",
                "target-blank-links"
            ])
            
            newsProps = {"content": newsHtml}
            for meta in newsMeta.split("\n"):
                if meta != "":
                    newsProps[meta.split(": ")[0]] = meta.split(": ")[1]

            writeContentToTemplate("news", baseHtml, isContent=True, filenameOutput=("news/" + slugify(news)), props=newsProps)

    writeContentToTemplate("news", baseHtml, props={
        "allNews": allNewsProps
    })
        
    print("[+] Creating writeup(s) page")
    print("[|] Downloading the writeups repo")
    os.system(str(pathlib.Path(__file__).parent.absolute()) + "/downloadAllWriteups.sh")

    allEvents = glob("./ctf-writeups-master/*/")
    allEventsSlug = []
    for event in allEvents:
        eventTitle = event.replace("./ctf-writeups-master/", "")[:-1]
        print("[|] Working on '{}'".format(eventTitle))

        allEventsSlug.append({
            "title": eventTitle,
            "slug": slugify(eventTitle)
        })
        
        md_filepaths = []
        for path, subdirs, files in os.walk(event):
            for name in files:
                if name.split(".")[-1] == "md" and str(name.split(".md")[0]).lower() != "readme":
                    md_filepaths.append(os.path.join(path, name))

        writeupMd = ""
        for path in md_filepaths:
            writeupMd += open(path, "r").read() + "\n"

        writeupHtml = markdown2.markdown(writeupMd, extras = [
            "footnotes", 
            "fenced-code-blocks", 
            "tables", 
            "markdown-in-html",
            "target-blank-links"
        ])

        writeContentToTemplate("writeup", baseHtml, isContent=True, filenameOutput=("writeups/" + slugify(eventTitle)), props={
            "content": writeupHtml
        })

    writeContentToTemplate("writeup", baseHtml, props={
        "writeups": allEventsSlug
    })

    print("[+] Sites creation sequence finished successfully")

if __name__ == "__main__" :
    main()