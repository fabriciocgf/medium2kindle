from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import bs4
import time
import os
import requests
import re
import pypandoc
from subprocess import Popen
from dotenv import load_dotenv
load_dotenv('.env')

def parseArticle(soup):
    sec = soup.find_all("article")
    doc = ""
    tags = sec[0].find_all(['h1','h2','h3','h4','ol','ul','blockquote','figure','p', 'pre', 'hr'])
    doc += ("---\n")
    doc += ("title: "+ '"' +sec[0].find_all('h1')[0].get_text()+ '"' +"\n")
    doc += ("author: Fabricio Gomes\n")
    doc += ("...\n")
    aux = 0
    for i in tags:
        if (i.name == "h1"):
            if aux > 0:
                doc+=("# " + i.getText() + "\n")
            if aux < 1:
                aux+=1

        elif (i.name == "h2"):
            doc+=("## " + i.getText() + "\n")

        elif (i.name == "h3"):
            doc+=("## " + i.getText() + "\n")

        elif (i.name == "h4"):
            doc+=("### " + i.getText() + "\n")

        elif (i.name == "h5"):
            doc+=("#### " + i.getText() + "\n")

        elif (i.name == "h6"):
            doc+=("##### " + i.getText() + "\n")

        elif (i.name == "p"):
            for e in i.contents:
                if(type(e) == bs4.element.NavigableString):
                    doc+=str(e)
                elif (type(e) == bs4.element.Tag and e.name == "a"):
                    doc+="["+ e.getText() +"]("+ e['href'] +")"
                elif ((type(e) == bs4.element.Tag) and (e.name == "b" or e.name == "strong")):
                        temptext = str(e.getText())
                        temptext = temptext.strip()
                        doc+="**"+ temptext +"** "
                elif ((type(e) == bs4.element.Tag) and (e.name == "i" or e.name == "em")):
                    temptext = str(e.getText())
                    temptext = temptext.strip()
                    doc+="*"+ temptext +"* "
                elif (e.name == "span"):
                    temptext = str(e.getText())
                    temptext = temptext.strip()
                    doc+= temptext
            doc+=("\n\n")

        elif (i.name == "blockquote"):
            doc+=(">" + i.getText() + "\n\n")

        elif (i.name == "figure"):
            im = i.find("img")
            cap = i.find("figcaption")
            if (im is not None):
                if(cap!= None and cap.find("a")!= None):
                    im['src'] = re.sub('\/\d+\/', '/400/',im['src'])
                    doc+=("[!["+ cap.getText() +"](" +im['src'] +")]("+ cap.find("a")['href'] +")" + "\n\n")
                else:
                    s = ("![](" +im['src'] +")\n\n")
                    s = re.sub('\/\d+\/', '/400/',s)
                    doc += s

        elif (i.name == "ol"):
            lilist = i.find_all('li')
            for t in range(len(lilist)):
                doc+='\n' +str(t+1) +". "
                for e in lilist[t].contents:
                    if(type(e) == bs4.element.NavigableString):
                        doc+=str(e)
                    elif (type(e) == bs4.element.Tag and e.name == "a"):
                        doc+="["+ e.getText() +"]("+ e['href'] +")"
                    elif ((type(e) == bs4.element.Tag) and (e.name == "b" or e.name == "strong")):
                        temptext = str(e.getText())
                        temptext = temptext.strip()
                        doc+="**"+ temptext +"** "
                    elif ((type(e) == bs4.element.Tag) and (e.name == "i" or e.name == "em")):
                        temptext = str(e.getText())
                        temptext = temptext.strip()
                        doc+="*"+ temptext +"* "
                doc+= "\n"
            doc+="\n"

        elif (i.name == "ul"):
            if (i['class'] == []):
                lilist = i.find_all('li')
                for t in range(len(lilist)):
                    doc+="\n- "
                    for e in lilist[t].contents:
                        if(type(e) == bs4.element.NavigableString):
                            doc+=str(e)
                        elif (type(e) == bs4.element.Tag and e.name == "a"):
                            doc+="["+ e.getText() +"]("+ e['href'] +")"
                        elif ((type(e) == bs4.element.Tag) and (e.name == "b" or e.name == "strong")):
                            temptext = str(e.getText())
                            temptext = temptext.strip()
                            doc+="**"+ temptext +"** "
                        elif ((type(e) == bs4.element.Tag) and (e.name == "i" or e.name == "em")):
                            temptext = str(e.getText())
                            temptext = temptext.strip()
                            doc+="*"+ temptext +"* "
                doc+= "\n\n"

        elif (i.name == "pre"):
            doc+="\n"
            doc+="```\n"
            for e in i.contents:
                for x in e.contents:
                    if (type(x) == bs4.element.NavigableString):
                        doc += str(x)+"\n"
                    elif (type(x) == bs4.element.Tag and x.name == "a"):
                        doc += x.getText()+"\n"
            doc+= "``` \n"

        elif (i.name == "hr"):
            doc+="\n---\n"
    return doc

def getAndSaveArticle(site):
    #driver = webdriver.PhantomJS()
    #driver.set_window_size(1120, 550)
    #options = webdriver.FirefoxOptions()
    #options.headless = True
    #driver = webdriver.Firefox(executable_path="geckodriver.exe", options=options)
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--incognito')
    options.add_argument('--headless')
    options.add_argument("--use-gl=swiftshader")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome("chromedriver", options=options)
    driver.get(site)
    driver.execute_script("window.scrollTo(0, 5000);")
    driver.implicitly_wait(10)
    #WebDriverWait(driver, 50).until(EC.presence_of_element_located((By.ID, 'root')))
    page_source = driver.page_source
    soup = bs4.BeautifulSoup(page_source, features="html.parser")
    fn = soup.title.string
    forb = '<>:/\|?*, \'!"'
    fn = ''.join(c for c in fn if c not in forb)
    FILENAME = "./" + "Articles" + "/" + fn[0:52] + ".md"
    with open(FILENAME, "w", encoding="utf8") as file:
        file.write(parseArticle(soup))
    driver.close()
    return FILENAME

def convert_epub(file):
    output = pypandoc.convert_file(source_file=file, format='md', to='epub',outputfile=file[:-2]+"epub", extra_args=["-M2GB", "+RTS", "-K64m", "-RTS", '--toc'], encoding='utf-8')
    #os.remove(file)
    return file[:-2]+"epub"

def convert_mobi(file):
    cwd = os.getcwd()
    file = (cwd + file[1:]).replace('/','\\')
    file_mobi = file[:-5] + ".mobi"
    p = Popen('ebook-convert' +' '+ '"'+file+'"' +' '+ '"'+file_mobi+'"', shell=True)
    p.wait()
    return file_mobi, file

def send2kindle(file):
    sender = os.getenv("SENDER")
    receiver = os.getenv("RECEIVER")
    senderName = os.getenv("SENDER_NAME")
    server = os.getenv("SERVER")
    user = os.getenv("USER")
    password = os.getenv("PASSWORD")
    enc = os.getenv("ENCRIPT")
    port = os.getenv("PORT")
    p = Popen('calibre-smtp'+' '+ sender +' '+ receiver +' '+ senderName +' -r '+ server +' -u '+ user +' -a '+ '"' + file + '"' +' -p '+ password +' -e '+ enc +' --port '+ port +'"',shell=True)
    p.wait()
