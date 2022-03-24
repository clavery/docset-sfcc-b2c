#!/usr/bin/env python
# coding: utf-8

from pyquery import PyQuery as pq
import sqlite3
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

# ## OCAPI

V = "current"
OCAPI_PREFIX = '/DOC3/topic/com.demandware.dochelp/OCAPI/%s/' % V
OCAPI_INDICIES = [
    'https://documentation.b2c.commercecloud.salesforce.com/DOC3/topic/com.demandware.dochelp/OCAPI/%s/shop/Resources/index.html' % V,
    'https://documentation.b2c.commercecloud.salesforce.com/DOC3/topic/com.demandware.dochelp/OCAPI/%s/data/Resources/index.html' % V,
    'https://documentation.b2c.commercecloud.salesforce.com/DOC3/topic/com.demandware.dochelp/OCAPI/%s/usage/APIUsage.html?cp=0_12_2' % V,
    'https://documentation.b2c.commercecloud.salesforce.com/DOC3/topic/com.demandware.dochelp/OCAPI/%s/shop/Documents/index.html' % V,
    'https://documentation.b2c.commercecloud.salesforce.com/DOC3/topic/com.demandware.dochelp/OCAPI/%s/data/Documents/index.html' % V
]

NS = "{http://www.w3.org/1999/xhtml}"
NSMAP = {
    "X" : "http://www.w3.org/1999/xhtml"
}
from urllib.parse import urlparse
LINKS = set()
for page in OCAPI_INDICIES:
    r = requests.get(page)
    content = r.content.decode('utf-8').replace('self == top', 'self == "blah"').encode('utf-8')
    parser = ET.HTMLParser()
    content = ET.fromstring(content, parser)
    parsed_url = urlparse(page)
    dirname = os.path.normpath(os.path.dirname(parsed_url.path))
    if OCAPI_PREFIX not in dirname:
        continue

    for link in content.xpath("//a", namespaces=NSMAP):
        if 'href' not in link.attrib:
            continue
        href = link.attrib['href']
        if href.startswith("https://www"):
            continue
        normalized = os.path.normpath(os.path.join(dirname, href))
        full_link = urlparse(f"{parsed_url.scheme}://{parsed_url.netloc}{normalized}")
        full_link = f"{full_link.scheme}://{full_link.netloc}{full_link.path}"
        if OCAPI_PREFIX not in full_link:
            continue
        if full_link.endswith('.html') and "DOC3" in full_link:
            LINKS.add(full_link)
            
resp = requests.get('https://documentation.b2c.commercecloud.salesforce.com/DOC3/topic/com.demandware.dochelp/css/commonltr.css')
css = f"""<style>
{resp.content.decode('utf-8')}
.help_breadcrumbs {{ display: none !important; }}
.copyright_table td {{ display: none; }}
copyright_table td:nth-child(4) {{ display: table-cell; }}
</style>"""

if os.path.exists("./SFCC_API.docset/Contents/Resources/Documents/ocapi"):
    shutil.rmtree("./SFCC_API.docset/Contents/Resources/Documents/ocapi")
    
if not os.path.exists('./SFCC_API.docset/Contents/Resources/Documents/ocapi/'):
    os.makedirs('./SFCC_API.docset/Contents/Resources/Documents/ocapi/shop/Documents')
    os.makedirs('./SFCC_API.docset/Contents/Resources/Documents/ocapi/data/Documents')
    os.makedirs('./SFCC_API.docset/Contents/Resources/Documents/ocapi/shop/Resources')
    os.makedirs('./SFCC_API.docset/Contents/Resources/Documents/ocapi/data/Resources')


for link in LINKS:
    r = requests.get(link)
    r.raise_for_status()
    content = r.content.decode('utf-8').replace('self == top', 'self == "blah"')
    content = content.replace("</head>", css)
    parser = ET.HTMLParser()
    content_html = ET.fromstring(content.encode("utf-8"), parser)
    title = content_html.xpath('//title')[0].text
    if "(" in title:
        title = title[:title.index('(') - 1]

    # replace DWAPI/scriptapi/html with Documents for relative paths to script APIs
    content = content.replace('DWAPI/scriptapi/html', 'Documents')

    name, ext = os.path.splitext(os.path.basename(link))
    if "shop/Resources" in link:
        entry_type = "Resource"
        entry_name = "SHOPAPI " + name
        entry_folder = "shop/Resources/"
    elif "shop/Documents" in link:
        entry_type = "Type"
        entry_name = "SHOPDOC "  + name
        entry_folder = "shop/Documents/"
    elif "data/Resources" in link:
        entry_type = "Resource"
        entry_name = "DATAAPI " + name
        entry_folder = "data/Resources/"
    elif "data/Documents" in link:
        entry_type = "Type"
        entry_name = "DATADOC "  + name
        entry_folder = "data/Documents/"
    else:
        entry_type = "Guide"
        entry_name = title
        entry_folder = ""

    print(entry_type, entry_name)

    c.execute("INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES ('%s', '%s', '%s');" % 
              (entry_name, entry_type, "ocapi/%s%s" % (entry_folder, name+".html")))
    with open(os.path.join('./SFCC_API.docset/Contents/Resources/Documents/ocapi/%s' % entry_folder, name+".html"), 'w') as f:
        f.write(content)

conn.commit()
conn.close()











