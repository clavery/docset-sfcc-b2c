#!/usr/bin/env python
# coding: utf-8

from pyquery import PyQuery as pq
import sqlite3
import os
import os.path
import shutil
import markdown
from markdown.extensions.tables import TableExtension
from markdown.extensions.fenced_code import FencedCodeExtension
from markdown.extensions.codehilite import CodeHiliteExtension
from lxml import etree as ET
from io import StringIO
from jinja2 import Template
import requests

PLIST = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
<key>CFBundleIdentifier</key>
<string>sfcc</string>
<key>CFBundleName</key>
<string>SFCC B2C Script API/OCAPI</string>
<key>DocSetPlatformFamily</key>
<string>sfcc</string>
<key>isDashDocset</key>
<true/>
</dict>
</plist>"""


# Init dirs

assert os.path.exists("./docs/scriptapi"), "Follow the instructions in the README.md to download the source docs"

if os.path.exists("./SFCC_API.docset/Contents/"):
    shutil.rmtree("./SFCC_API.docset/Contents/")

if not os.path.exists('./SFCC_API.docset/Contents/Resources/Documents/'):
    os.makedirs('./SFCC_API.docset/Contents/Resources/Documents/')

shutil.copy('./code.css', './SFCC_API.docset/Contents/Resources/Documents/code.css')

with open('./SFCC_API.docset/Contents/Info.plist', 'w') as f:
    f.write(PLIST)

conn = sqlite3.connect('./SFCC_API.docset/Contents/Resources/docSet.dsidx')
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT);")
c.execute("CREATE UNIQUE INDEX IF NOT EXISTS anchor ON searchIndex (name, type, path);")
conn.commit()

# Script API

if os.path.exists("./SFCC_API.docset/Contents/Resources/Documents/api"):
    shutil.rmtree("./SFCC_API.docset/Contents/Resources/Documents/api")
shutil.copytree("./docs/scriptapi/html/api", "./SFCC_API.docset/Contents/Resources/Documents/api")

with open("./SFCC_API.docset/Contents/Resources/Documents/api/classList.html", "r") as f:
    d = pq(f.read())

for link in d('.classesName a'):
    title = link.attrib["title"]
    name = link.text
    path = link.attrib["href"]

    print("scriptapi", name, title)

    c.execute("INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES ('%s', 'Class', '%s');" %
              (name, "api/%s" % path))

conn.commit()

# Job Step API

if os.path.exists("./SFCC_API.docset/Contents/Resources/Documents/jobstepapi/"):
    shutil.rmtree("./SFCC_API.docset/Contents/Resources/Documents/jobstepapi/")
shutil.copytree("./docs/jobstepapi/html/api/", "./SFCC_API.docset/Contents/Resources/Documents/jobstepapi")

with open("./SFCC_API.docset/Contents/Resources/Documents/jobstepapi/jobStepList.html", "r") as f:
    d = pq(f.read())


for link in d('.classesName a'):
    name = link.find("span").text
    path = link.attrib["href"]

    print("jobstep", name)

    c.execute("INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES ('%s', 'Builtin', '%s');" %
              (name, "jobstepapi/%s" % path))

conn.commit()

# Pipelet API

if os.path.exists("./SFCC_API.docset/Contents/Resources/Documents/pipelet/"):
    shutil.rmtree("./SFCC_API.docset/Contents/Resources/Documents/pipelet/")
shutil.copytree("./docs/pipeletapi/html/api/", "./SFCC_API.docset/Contents/Resources/Documents/pipelet")

with open("./SFCC_API.docset/Contents/Resources/Documents/pipelet/pipeletList.html", "r") as f:
    d = pq(f.read())

for link in d('.classesName a'):
    name = link.find("span").text
    path = link.attrib["href"]

    print("pipelet", name)

    c.execute("INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES ('%s', 'Procedure', '%s');" %
              (name, "pipelet/%s" % path))

conn.commit()

# Remove JS files
if os.path.exists("./SFCC_API.docset/Contents/Resources/Documents/api/js/dwapi.js"):
    os.remove("./SFCC_API.docset/Contents/Resources/Documents/api/js/dwapi.js")
if os.path.exists("./SFCC_API.docset/Contents/Resources/Documents/jobstepapi/js/dwapi.js"):
    os.remove("./SFCC_API.docset/Contents/Resources/Documents/jobstepapi/js/dwapi.js")
if os.path.exists("./SFCC_API.docset/Contents/Resources/Documents/pipelet/js/dwapi.js"):
    os.remove("./SFCC_API.docset/Contents/Resources/Documents/pipelet/js/dwapi.js")

# Samples/Guides

with open('./guidetemplate.html', 'r') as f:
    template_src = f.read()
template = Template(template_src)

if not os.path.exists('./SFCC_API.docset/Contents/Resources/Documents/guides/'):
    os.makedirs('./SFCC_API.docset/Contents/Resources/Documents/guides/')

for f in os.listdir('./guides/'):
    name, ext = os.path.splitext(f)
    title = name + " (Guide)"
    print("guide", name)
    c.execute("INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES ('%s', 'Guide', '%s');" %
              (title, "guides/%s" % (name+".html")))

    with open('./guides/' + f, 'r') as f:
        doc_output = markdown.markdown(f.read(), extensions=[TableExtension(), FencedCodeExtension(), CodeHiliteExtension()])

    with open(os.path.join('./SFCC_API.docset/Contents/Resources/Documents/guides/', name+".html"), 'w') as f:
        output = template.render(body=doc_output)
        f.write(output)

conn.commit()

# ISML Tags

if not os.path.exists('./SFCC_API.docset/Contents/Resources/Documents/isml/'):
    os.makedirs('./SFCC_API.docset/Contents/Resources/Documents/isml/')

for f in os.listdir('./isml/'):
    name, ext = os.path.splitext(f)
    title = name + " (ISML Tag)"
    print("isml", name)
    c.execute("INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES ('%s', 'Tag', '%s');" %
              (title, "isml/%s" % (name+".html")))

    shutil.copy('./isml/' + f, './SFCC_API.docset/Contents/Resources/Documents/isml/' + f)

conn.commit()


# Schemas

with open('./schematemplate.html', 'r') as f:
    template_src = f.read()
template = Template(template_src)

if not os.path.exists('./SFCC_API.docset/Contents/Resources/Documents/schemas/'):
    os.makedirs('./SFCC_API.docset/Contents/Resources/Documents/schemas/')
for f in os.listdir('./docs/xsd/'):
    name, ext = os.path.splitext(f)
    if ext != ".xsd":
        continue
    print("schema", name)
    c.execute("INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES ('%s', 'Protocol', '%s');" %
              (f, "schemas/%s" % (name+".html")))

    with open('./docs/xsd/' + f, 'r') as f:
        md = """
```xml
%s
```
        """ % f.read()
        doc_output = markdown.markdown(md, extensions=[TableExtension(), FencedCodeExtension(), CodeHiliteExtension()])

    with open(os.path.join('./SFCC_API.docset/Contents/Resources/Documents/schemas/', name+".html"), 'w') as f:
        output = template.render(body=doc_output, name=name)
        f.write(output)

conn.commit()

# Quota

if os.path.exists("./SFCC_API.docset/Contents/Resources/Documents/quota/"):
    shutil.rmtree("./SFCC_API.docset/Contents/Resources/Documents/quota/")
shutil.copytree("./docs/quota/html/", "./SFCC_API.docset/Contents/Resources/Documents/quota")

c.execute("INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES ('Quotas', 'Setting', 'quota/index.html');")
c.execute("INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES ('API Quotas', 'Setting', 'quota/API_Quotas.html');")
c.execute("INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES ('Object Quotas', 'Setting', 'quota/Object_Quotas.html');")
conn.commit()

# ## OCAPI

if os.path.exists("./SFCC_API.docset/Contents/Resources/Documents/ocapi"):
    shutil.rmtree("./SFCC_API.docset/Contents/Resources/Documents/ocapi")
shutil.copytree("./ocapi", "./SFCC_API.docset/Contents/Resources/Documents/ocapi")


# list contents of directory
LINKS = []
for root, dirs, files in os.walk("./SFCC_API.docset/Contents/Resources/Documents/ocapi/data/Documents"):
    for file in files:
        if file.endswith(".html"):
            entry_type = "Type"
            entry_name = "DATADOC " + os.path.splitext(file)[0]
            entry_folder = "data/Documents/"
            c.execute("INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES ('%s', '%s', '%s');" %
                      (entry_name, entry_type, "ocapi/%s%s" % (entry_folder, file)))
for root, dirs, files in os.walk("./SFCC_API.docset/Contents/Resources/Documents/ocapi/data/Resources"):
    for file in files:
        if file.endswith(".html"):
            entry_type = "Resource"
            entry_name = "DATAAPI " + os.path.splitext(file)[0]
            entry_folder = "data/Resources/"
            c.execute("INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES ('%s', '%s', '%s');" %
                      (entry_name, entry_type, "ocapi/%s%s" % (entry_folder, file)))
for root, dirs, files in os.walk("./SFCC_API.docset/Contents/Resources/Documents/ocapi/shop/Documents"):
    for file in files:
        if file.endswith(".html"):
            entry_type = "Type"
            entry_name = "SHOPDOC " + os.path.splitext(file)[0]
            entry_folder = "shop/Documents/"
            c.execute("INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES ('%s', '%s', '%s');" %
                      (entry_name, entry_type, "ocapi/%s%s" % (entry_folder, file)))
for root, dirs, files in os.walk("./SFCC_API.docset/Contents/Resources/Documents/ocapi/shop/Resources"):
    for file in files:
        if file.endswith(".html"):
            entry_type = "Resource"
            entry_name = "SHOPAPI " + os.path.splitext(file)[0]
            entry_folder = "shop/Resources/"
            c.execute("INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES ('%s', '%s', '%s');" %
                      (entry_name, entry_type, "ocapi/%s%s" % (entry_folder, file)))

for f in os.listdir("./SFCC_API.docset/Contents/Resources/Documents/ocapi/"):
    if f.endswith(".html"):
        entry_type = "Guide"
        entry_name = "OCAPI " + os.path.splitext(f)[0]
        c.execute("INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES ('%s', '%s', '%s');" %
                  (entry_name, entry_type, "ocapi/%s" % (f)))

conn.commit()
conn.close()











