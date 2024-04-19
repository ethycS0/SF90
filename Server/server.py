from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import pickle
import requests
from bs4 import BeautifulSoup
import whois
import re
import ipaddress
from datetime import date
import json
import time
import socket

hostName = "0.0.0.0"
serverPort = 8000

class MyServer(BaseHTTPRequestHandler):
        def do_GET(self):
            parsed_url = urlparse(self.path)
            query_params = parse_qs(parsed_url.query)

            url = query_params.get('url', [''])[0]

            print('Received URL parameter:', url)
            url_param = query_params.get('url', [''])[0]

            loaded_model = pickle.load(open("Server/models/full.pkl", "rb"))
            obj = FeaturesFinder(url)
            Features = obj.getFeaturesList()
            print(Features)
            start_time = time.time()
            url = Features.pop(0)
            y_predicted = loaded_model.predict([Features])
            print("Prediction processing finished --- %s seconds ---" % (time.time() - start_time))
            print("URL is: ", y_predicted)
            if y_predicted == 1:
                response_data = {'safety': '1', 'url_param': url_param}
            elif y_predicted == 0:
                response_data = {'safety': '0', 'url_param': url_param}
            elif y_predicted == -1:
                response_data = {'safety': '-1', 'url_param': url_param}
        
            response_json = json.dumps(response_data)
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(bytes(response_json, 'utf-8'))

class FeaturesFinder:
    features = []
    def __init__(self,url):
        self.features = []
        self.url = url
        self.domain = ""
        self.whois_response = ""
        self.urlparse = ""
        self.response = ""
        self.soup = ""
        self.start_time = time.time()

        try:
            self.response = requests.get(url)
            self.soup = BeautifulSoup(self.response.text, 'html.parser')
        except:
            pass

        try:
            self.urlparse = urlparse(url)
            self.domain = self.urlparse.netloc
        except:
            pass

        try:
            self.whois_response = whois.query(self.domain)
        except:
            pass

        self.features.append(self.url)
        self.features.append(self.UsingIp())
        self.features.append(self.longUrl())
        self.features.append(self.shortUrl())
        self.features.append(self.symbol())
        self.features.append(self.redirecting())
        self.features.append(self.prefixSuffix())
        self.features.append(self.SubDomains())
        self.features.append(self.https())
        self.features.append(self.DomainRegLen())
        self.features.append(self.Favicon())
        self.features.append(self.NonStdPort())
        self.features.append(self.RequestURL())
        self.features.append(self.AnchorURL())
        self.features.append(self.LinksInScriptTags())
        self.features.append(self.ServerFormHandler())
        self.features.append(self.InfoEmail())
        self.features.append(self.AbnormalURL())
        self.features.append(self.WebsiteForwarding())
        self.features.append(self.StatusBarCust())
        self.features.append(self.DisableRightClick())
        self.features.append(self.UsingPopupWindow())
        self.features.append(self.IframeRedirection())
        self.features.append(self.AgeofDomain())
        self.features.append(self.DNSRecording())
        self.features.append(self.PageRank())
        self.features.append(self.GoogleIndex())
        self.features.append(self.LinksPointingToPage())


    def UsingIp(self):
        try:
            ipaddress.ip_address(self.domain)
            return -1
        except:
            return 1

    def longUrl(self):
        if len(self.url) < 54:
            return 1
        if len(self.url) >= 54 and len(self.url) <= 75:
            return 0
        return -1

    def shortUrl(self):
        match = re.search('bit\.ly|goo\.gl|shorte\.st|go2l\.ink|x\.co|ow\.ly|t\.co|tinyurl|tr\.im|is\.gd|cli\.gs|'
                    'yfrog\.com|migre\.me|ff\.im|tiny\.cc|url4\.eu|twit\.ac|su\.pr|twurl\.nl|snipurl\.com|'
                    'short\.to|BudURL\.com|ping\.fm|post\.ly|Just\.as|bkite\.com|snipr\.com|fic\.kr|loopt\.us|'
                    'doiop\.com|short\.ie|kl\.am|wp\.me|rubyurl\.com|om\.ly|to\.ly|bit\.do|t\.co|lnkd\.in|'
                    'db\.tt|qr\.ae|adf\.ly|goo\.gl|bitly\.com|cur\.lv|tinyurl\.com|ow\.ly|bit\.ly|ity\.im|'
                    'q\.gs|is\.gd|po\.st|bc\.vc|twitthis\.com|u\.to|j\.mp|buzurl\.com|cutt\.us|u\.bb|yourls\.org|'
                    'x\.co|prettylinkpro\.com|scrnch\.me|filoops\.info|vzturl\.com|qr\.net|1url\.com|tweez\.me|v\.gd|tr\.im|link\.zip\.net', self.domain)
        if match:
            return -1
        return 1

    def symbol(self):
        if re.findall("@",self.url):
            return -1
        return 1
    
    def redirecting(self):
        if self.url.count('//') > 1 or (self.url.find('//') != 5 and self.url.find('//') != 6):
            return -1
        else:
            return 1

    def prefixSuffix(self):
        try:
            match = re.findall('\-', self.domain)
            if match:
                return -1
            return 1
        except:
            return -1
    
    def SubDomains(self):
        dot_count = len(re.findall("\.", self.domain))
        if dot_count == 1:
            return 1
        elif dot_count == 2:
            return 0
        return -1

    def https(self):
        try:
            response = requests.head(self.url, allow_redirects=True, timeout=5)
            final_url = response.url

            if final_url.startswith('https://'):
                return 1
            else:
                return -1
        except:
            return -1


    def DomainRegLen(self):
        try:
            expiration_date = self.whois_response.expiration_date
            creation_date = self.whois_response.creation_date
            try:
                if(len(expiration_date)):
                    expiration_date = expiration_date[0]
            except:
                pass
            try:
                if(len(creation_date)):
                    creation_date = creation_date[0]
            except:
                pass

            age = (expiration_date.year-creation_date.year)*12+ (expiration_date.month-creation_date.month)
            if age >=12:
                return 1
            return -1
        except:
            return -1

    def Favicon(self):
        try:
            for head in self.soup.find_all('head'):
                for head.link in self.soup.find_all('link', href=True):
                    dots = [x.start(0) for x in re.finditer('\.', head.link['href'])]
                    if self.url in head.link['href'] or len(dots) == 1 or self.domain in head.link['href']:
                        return 1
            return -1
        except:
            return -1

    def NonStdPort(self):
        try:
            port = self.domain.split(":")
            if len(port)>1:
                return -1
            return 1
        except:
            return -1

    def RequestURL(self):
        try:
            success = 0
            i=0
            for img in self.soup.find_all('img', src=True):
                dots = [x.start(0) for x in re.finditer('\.', img['src'])]
                if self.url in img['src'] or self.domain in img['src'] or len(dots) == 1:
                    success = success + 1
                i = i+1

            for audio in self.soup.find_all('audio', src=True):
                dots = [x.start(0) for x in re.finditer('\.', audio['src'])]
                if self.url in audio['src'] or self.domain in audio['src'] or len(dots) == 1:
                    success = success + 1
                i = i+1

            for embed in self.soup.find_all('embed', src=True):
                dots = [x.start(0) for x in re.finditer('\.', embed['src'])]
                if self.url in embed['src'] or self.domain in embed['src'] or len(dots) == 1:
                    success = success + 1
                i = i+1

            for iframe in self.soup.find_all('iframe', src=True):
                dots = [x.start(0) for x in re.finditer('\.', iframe['src'])]
                if self.url in iframe['src'] or self.domain in iframe['src'] or len(dots) == 1:
                    success = success + 1
                i = i+1

            try:
                percentage = 1-success/float(i) * 100
                if percentage < 22.0:
                    return 1
                elif((percentage >= 22.0) and (percentage < 61.0)):
                    return 0
                else:
                    return -1
            except:
                return 0
        except:
            return -1
    
    def AnchorURL(self):
        try:
            i,unsafe = 0,0
            for a in self.soup.find_all('a', href=True):
                if "#" in a['href'] or "javascript" in a['href'].lower() or "mailto" in a['href'].lower() or not (self.url in a['href'] or not self.domain in a['href']):
                    unsafe = unsafe + 1
                i = i + 1

            try:
                percentage = unsafe / float(i) * 100
                if percentage < 31.0:
                    return 1
                elif ((percentage >= 31.0) and (percentage < 67.0)):
                    return 0
                else:
                    return -1
            except:
                return -1

        except:
            return -1

    def LinksInScriptTags(self):
        try:
            i,success = 0,0
        
            for link in self.soup.find_all('link', href=True):
                dots = [x.start(0) for x in re.finditer('\.', link['href'])]
                if self.url in link['href'] or self.domain in link['href'] or len(dots) == 1:
                    success = success + 1
                i = i+1

            for script in self.soup.find_all('script', src=True):
                dots = [x.start(0) for x in re.finditer('\.', script['src'])]
                if self.url in script['src'] or self.domain in script['src'] or len(dots) == 1:
                    success = success + 1
                i = i+1

            try:
                percentage = success / float(i) * 100
                if percentage < 17.0:
                    return 1
                elif((percentage >= 17.0) and (percentage < 81.0)):
                    return 0
                else:
                    return -1
            except:
                return 0
        except:
            return -1

    def ServerFormHandler(self):
        try:
            if len(self.soup.find_all('form', action=True))==0:
                return 1
            else :
                for form in self.soup.find_all('form', action=True):
                    if form['action'] == "" or form['action'] == "about:blank":
                        return -1
                    elif self.url in form['action'] or self.domain in form['action'] or "https" not in form['action'] or 'http' not in form['action']:
                        return 1
                    else:
                        return 0
        except:
            return -1

    def InfoEmail(self):
        try:
            if "mailto:" in self.response.text:
                return -1
            else:
                return 1
        except:
            return -1

    def AbnormalURL(self):
        try:
            if self.whois_response.name in self.domain:
                return 1
            else:
                return -1
        except:
            return -1

    def WebsiteForwarding(self):
        try:
            if len(self.response.history) <= 1:
                return 1
            elif len(self.response.history) <= 4:
                return 0
            else:
                return -1
        except:
             return -1

    def StatusBarCust(self):
        try:
            if re.findall("<script>.+onmouseover.+</script>", self.response.text):
                return -1
            else:
                return 1
        except:
             return -1

    def DisableRightClick(self):
        try:
            if re.findall(r"event.button ?== ?2", self.response.text):
                return -1
            else:
                return 1
        except:
             return -1

    def UsingPopupWindow(self):
        try:
            if re.findall(r"alert\(", self.response.text):
                return -1
            else:
                return 1
        except:
             return -1

    def IframeRedirection(self):
        try:
            if re.findall(r"[<iframe>|<frameBorder>]", self.response.text):
                return -1
            else:
                return 1
        except:
             return -1

    def AgeofDomain(self):
        try:
            creation_date = self.whois_response.creation_date
            try:
                if(len(creation_date)):
                    creation_date = creation_date[0]
            except:
                pass

            today  = date.today()
            age = (today.year-creation_date.year)*12+(today.month-creation_date.month)
            if age >=6:
                return 1
            return -1
        except:
            return -1
 
    def DNSRecording(self):
        try:
            creation_date = self.whois_response.creation_date
            try:
                if(len(creation_date)):
                    creation_date = creation_date[0]
            except:
                pass

            today  = date.today()
            age = (today.year-creation_date.year)*12+(today.month-creation_date.month)
            if age >=6:
                return 1
            return -1
        except:
            return -1

    def PageRank(self):
        try:
            for i in search(self.domain, sleep_interval=5, num_results=5):
                parsed = urlparse(i)
                parseddom = parsed.netloc
                if parseddom == self.domain:
                    return 1
            else:
                return -1
        except:
            return -1

    def GoogleIndex(self):
        try:
            for i in search(self.domain, sleep_interval=3, num_results=3):
                parsed = urlparse(i)
                parseddom = parsed.netloc
                if parseddom == self.domain:
                    return 1
            else:
                return -1
        except:
            return -1

    def LinksPointingToPage(self):
        try:
            number_of_links = len(re.findall(r"<a href=", self.response.text))
            if number_of_links == 0:
                return 1
            elif number_of_links <= 2:
                return 0
            else:
                return -1
        except:
            return -1

    def getFeaturesList(self):

        print("Prediction processing finished --- %s seconds ---" % (time.time() - self.start_time))
        return self.features
        # try:
        #     responsel = requests.get(self.url, timeout=20)
        #     return self.features

        # except RequestException as e:
        #     print(f"Error extracting features from {self.url}: {e}")

# server usage
webServer = HTTPServer((hostName, serverPort), MyServer)
print("Server started http://%s:%s" % (hostName, serverPort))
webServer.serve_forever()

# Feature Testing
# for item in suspicious_links:
#     url = item
#     loaded_model = pickle.load(open("Server/models/full.pkl", "rb"))
#     obj = FeaturesFinder(url)
#     Features = obj.getFeaturesList()
#     print(Features)

#     start_time = time.time()
#     url = Features.pop(0)
#     y_predicted = loaded_model.predict([Features])
#     print("Prediction processing finished --- %s seconds ---" % (time.time() - start_time))
#     print("URL is: ", y_predicted)
# if y_predicted == 1:
#     response_data = {'safety': '1', 'url_param': url_param}
# elif y_predicted == 0:
#     response_data = {'safety': '0', 'url_param': url_param}
# elif y_predicted == -1:
#     response_data = {'safety': '-1', 'url_param': url_param}