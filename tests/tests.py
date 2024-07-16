import unittest
import requests

gcp = "https://chatbot-ga4-n4ttrget4a-uc.a.run.app"
local = "http://localhost:8080"
url_global = local

class TestBlueprint(unittest.TestCase):
    """
    A class that contains unit tests for the Blueprint functionality.
    """

    def test_vectorizer(self):
        """
        Test the vectorizer endpoint.

        This method sends a POST request to the vectorizer endpoint and checks if the response status code is 200.
        """
        url = url_global
        path = "vectorizer"
        full_url = f"{url}/{path}"
        data = {
            "bucket":"markdown-file",
            "name":"attribution.txt"
        }
        response = requests.post(full_url, json=data)
        status_code = response.status_code
        self.assertEqual(status_code, 200, f"Erro: {status_code}")
        print("Vectorizer passou!")
        
    def test_url_extractor(self):
        """
        Test the URL extractor endpoint.

        This method sends a GET request to the URL extractor endpoint and checks if the response status code is 200.
        """
        url = url_global
        path = "url_extractor"
        full_url = f"{url}/{path}"
        response = requests.get(full_url)
        status_code = response.status_code
        self.assertEqual(status_code, 200, f"Erro: {status_code}")
        print("URL Extractor passou!")
        
    
    

if __name__ == '__main__':
        unittest.main()
  
