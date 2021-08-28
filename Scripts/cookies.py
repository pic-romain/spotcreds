import pickle
from selenium import webdriver

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import urllib.parse as urlparse
import urllib.parse as urllibparse
from urllib.parse import parse_qs
import json

SPOTIFY_API_BASE_URL = 'https://api.spotify.com'
API_VERSION = "v1"
SPOTIFY_API_URL = f"{SPOTIFY_API_BASE_URL}/{API_VERSION}"


# spotify endpoints
SPOTIFY_AUTH_BASE_URL = "https://accounts.spotify.com/{}"
SPOTIFY_AUTH_URL = SPOTIFY_AUTH_BASE_URL.format('authorize')
SPOTIFY_TOKEN_URL = SPOTIFY_AUTH_BASE_URL.format('api/token')

# client keys
REDIRECT_URI = "https://twitter.com/SpotCredits"#f"{CLIENT_SIDE_URL}:{PORT}/callback/"
SCOPE = "ugc-image-upload playlist-modify-public playlist-modify-private"

CLIENT = json.load(open('conf_spotify.json', 'r'))
CLIENT_ID = CLIENT['id']
CLIENT_SECRET = CLIENT['secret']
auth_query_parameters = {
    "response_type": "code",
    "redirect_uri": REDIRECT_URI,
    "scope": SCOPE,
    "client_id": CLIENT_ID
}
URL_ARGS = "&".join([f"{key}={urllibparse.quote(val)}" for key, val in auth_query_parameters.items()])
AUTH_URL = f"{SPOTIFY_AUTH_URL}/?{URL_ARGS}"

spotify_account = json.load(open('conf_spotify_account.json', 'r'))
ACCOUNT_ID = spotify_account["id"]
ACCOUNT_PASSWORD =  spotify_account["password"]

def save_cookie(driver, path):
    with open(path, 'wb') as filehandler:
        print(driver.get_cookies())
        pickle.dump(driver.get_cookies(), filehandler)

def load_cookie(driver, path):
     with open(path, 'rb') as cookiesfile:
         cookies = pickle.load(cookiesfile)
         for cookie in cookies:
             driver.add_cookie(cookie)

opts = webdriver.FirefoxOptions()
opts.add_argument("--headless")
driver = webdriver.Firefox(options=opts)
driver.get(AUTH_URL)


try:
        driver.find_element_by_id("login-username").send_keys(ACCOUNT_ID)
        driver.find_element_by_id ("login-password").send_keys(ACCOUNT_PASSWORD)
        driver.find_element_by_id("login-button").click()
except NoSuchElementException:
    # print(driver.page_source)
    print("Not the right page")

try:
    auth_button= WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'auth-accept')))
    print("Page is ready!")
    auth_button.click()
except TimeoutException:
    print("Loading took too much time!")
    
    url_code = driver.current_url
    parsed_url = urlparse.urlparse(url_code)

driver.get("https://accounts.spotify.com/404")
save_cookie(driver,path="data/cookies.txt")
driver.close()
