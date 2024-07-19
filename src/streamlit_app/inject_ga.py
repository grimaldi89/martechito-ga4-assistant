from bs4 import BeautifulSoup
import pathlib
import shutil
import streamlit as st
import logging
import os
from dotenv import load_dotenv
logging.basicConfig(level=logging.INFO)
load_dotenv()
GTM_CONTAINER_ID = os.getenv("GTM_CONTAINER_ID")

GTM_ID="google_tag_manager"
GTM_SCRIPT_HEAD = f"""
<!-- Google Tag Manager -->
<script>(function(w,d,s,l,i){{w[l]=w[l]||[];w[l].push({{'gtm.start':
new Date().getTime(),event:'gtm.js'}});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
}})(window,document,'script','dataLayer','{GTM_CONTAINER_ID}');</script>
<!-- End Google Tag Manager -->
"""
GTM_SCRIPT_BODY = f"""
<!-- Google Tag Manager (noscript) -->
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id={GTM_CONTAINER_ID}"
height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
<!-- End Google Tag Manager (noscript) -->
"""



def inject_gtm():
    
    index_path = pathlib.Path(st.__file__).parent / "static" / "index.html"
    soup = BeautifulSoup(index_path.read_text(), features="html.parser")
    if not soup.find(id=GTM_ID): 
        bck_index = index_path.with_suffix('.bck')
        if bck_index.exists():
            shutil.copy(bck_index, index_path)  
        else:
            shutil.copy(index_path, bck_index)  
        html = str(soup)
        new_html = html.replace('<head>', '<head>\n' + GTM_SCRIPT_HEAD).replace('<body>', '<body>\n' + GTM_SCRIPT_BODY)
       
        index_path.write_text(new_html)


inject_gtm()
logging.info("Google Tag Manager injected!")
