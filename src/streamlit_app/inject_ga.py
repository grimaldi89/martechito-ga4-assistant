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
'https://www.tagging.martechito.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
}})(window,document,'script','dataLayer','GTM-K228GN4F');</script>
<!-- End Google Tag Manager -->
"""
GTM_SCRIPT_BODY = f"""
<!-- Google Tag Manager (noscript) -->
<noscript><iframe src="https://www.tagging.martechito.com/ns.html?id=GTM-K228GN4F"
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

def modify_tag_content(tag_name, new_content):
    index_path = pathlib.Path(st.__file__).parent / "static" / "index.html"
    logging.info(f'editing {index_path}')
    soup = BeautifulSoup(index_path.read_text(), features="html.parser")
    
    target_tag = soup.find(tag_name)  # find the target tag

    if target_tag:  # if target tag exists
        target_tag.string = new_content  # modify the tag content
    else:  # if target tag doesn't exist, create a new one
        target_tag = soup.new_tag(tag_name)
        target_tag.string = new_content
        try:
            if tag_name in ['title', 'script', 'noscript'] and soup.head:
                soup.head.append(target_tag)
            elif soup.body:
                soup.body.append(target_tag)
        except AttributeError as e:
            print(f"Error when trying to append {tag_name} tag: {e}")
            return

    # Save the changes
    bck_index = index_path.with_suffix('.bck')
    if not bck_index.exists():
        shutil.copy(index_path, bck_index)  # keep a backup
    index_path.write_text(str(soup))

modify_tag_content('title', 'Martechito - GA4 AI Assistant')
modify_tag_content('noscript', 'Martechito is a GA4 AI Assistant that helps you to find answers to your questions about GA4')