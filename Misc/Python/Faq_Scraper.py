from bs4 import BeautifulSoup
import requests
import os
import pandas as pd

def getFaq(lang, amount):
 
    r = requests.get("https://crm.superoffice.com/scripts/customer.fcgi?_sf=0&custSessionKey=&customerLang="+lang+"&noCookies=true&action=viewKbTopEntries&numEntries="+amount)
    data = r.text
    soup = BeautifulSoup(data, "lxml")
    desktop = os.environ["HOMEPATH"] + "\\desktop\\example\\"
   
    
    all_href = soup.find_all("a")
    all_links = []
    
    for href in all_href:    
        all_links.append(href.prettify(formatter=None).replace("/scripts","https://crm.superoffice.com/scripts"))
    
    
    
    names = []
    for i in all_links:
        startt = i.find('">') + 2
        endd =i.find("</a>")
        names.append(i[startt:endd])
    
    df = pd.DataFrame(all_links)
    df["FAQ"] = names
    df.columns =["Hyperlinks", "Faq"]
    
    df.to_excel(desktop+lang+ "Faqs.xlsx", index=False) 

# Language code & how many FAQ's to pull.
getFaq("no", "60")
