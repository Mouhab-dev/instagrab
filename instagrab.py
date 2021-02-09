from logging import raiseExceptions
from typing import MutableMapping
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.errorhandler import ErrorHandler
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, InvalidArgumentException, JavascriptException, NoSuchElementException, TimeoutException
from urllib.error import URLError
import time
# library to download photo from url
import urllib.request

# Configure Webdriver to use Brave Browser
options = Options()
# options.binary_location = 'C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe' 
options.binary_location = 'C:\Program Files\Google\Chrome\Application\chrome.exe' # Put your chrome/brave browser path here
driver_path = 'C:/Program Files (x86)/chromedriver.exe' # Put chromedriver path here
options.add_argument('--disable-gpu')

options.add_argument("--headless") # Comment to disable running in background
# Instagram blocks the headless mode so we have to change the user_agent of the browser
user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36' # change
options.add_argument(f'user-agent={user_agent}')

drvr = webdriver.Chrome(options = options, executable_path = driver_path)

LOGIN_USERNAME = '' # Enter your email or login username here
LOGIN_PASSWORD = '' # Enter your password here
logged_in = False
username_obtained = False
target_username = ''
total_posts = 0
fin_no_of_posts = 0
req_no_of_posts = 0 # By default download all posts


def insta_login(reload_url):

    if reload_url[-1] != '/':
        reload_url = reload_url + '/'
    
    if drvr.current_url == reload_url:
        return True

    print(drvr.current_url)
    
    global logged_in

    while not logged_in:
        try:
            # Check Form Login
            WebDriverWait(drvr, 7).until(EC.presence_of_element_located((By.ID, "loginForm")))
        except TimeoutException or NoSuchElementException:
            print("Login Form Not Found, Continuing ...")
            return True

        # Code To Prompt The user to enter his Credentials
        # TODO

        # Login Process
        try:
            username = drvr.find_element_by_xpath('//*[@id="loginForm"]/div/div[1]/div/label/input')
            username.send_keys(LOGIN_USERNAME)
            password = drvr.find_element_by_xpath('//*[@id="loginForm"]/div/div[2]/div/label/input')
            password.send_keys(LOGIN_PASSWORD)
            password.send_keys(Keys.RETURN)
            print("Logging in ...")
            try:
                WebDriverWait(drvr,3).until(EC.presence_of_element_located((By.ID,'slfErrorAlert')))
                print("Invalid Username and/or password!")
                return False
            except TimeoutException:
                try:
                    # Save login info form
                    WebDriverWait(drvr, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR,'div.olLwo')))
                    print('[*] You have successfully logged in')
                    logged_in = True
                    drvr.get(reload_url)
                    return  True
                except TimeoutException:
                    print("An fatal error has occured !!!")
                    return False
        except:
            print("unable to locate login fields")


def insta_login_popup():
    global logged_in
    try:
        username = WebDriverWait(drvr, 20).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="loginForm"]/div[1]/div[1]/div/label/input')))
        username.send_keys(LOGIN_USERNAME)
        password = WebDriverWait(drvr, 20).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="loginForm"]/div[1]/div[2]/div/label/input')))
        password.send_keys(LOGIN_PASSWORD)
        password.send_keys(Keys.RETURN)
        print("Logging in POP-UP Window...")

        try:
            WebDriverWait(drvr,3).until(EC.presence_of_element_located((By.ID,'slfErrorAlert')))
            print("Invalid Username and/or password!")
            return False
        except TimeoutException:
            try:
                # Check for save login info form
                WebDriverWait(drvr, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR,'div.olLwo')))
                print('[*] You have successfully logged in')
                logged_in = True
                return  True
            except TimeoutException:
                print("An fatal error has occured !!!")
                return False

    except TimeoutException or NoSuchElementException:
        return False


def get_username():
    global username_obtained
    # Find Username
    try:
        username = WebDriverWait(drvr, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.ZIAjV"))).text
        username_obtained = True
    except TimeoutException or NoSuchElementException:
        print("Problem Finding username, Default username was set.")
        username = "Instagram"
    return username


def number_of_photos_url():
    number_of_photos=0
    try:
        number_of_photos = len(WebDriverWait(drvr, 5).until(EC.visibility_of_all_elements_located((By.CLASS_NAME, "Yi5aA"))))
    except TimeoutException:
        number_of_photos = 0

    try:
        photo_link = WebDriverWait(drvr, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.c-Yi7"))).get_attribute('href')[28:].strip('/')
        if number_of_photos == 0:
            number_of_photos = 1
    except TimeoutException or NoSuchElementException:
        print("Cannot Determine Number of Photos")
        print("Cannot Determine photo link")
        number_of_photos = 0
        photo_link = None

    return number_of_photos, photo_link


def check_private_wrong_empty_acc():
    try:
        WebDriverWait(drvr, 2).until(EC.presence_of_element_located((By.XPATH,'//*[@id="react-root"]/section/main/div/div/article/div/div/h2')))
        print("[!] Sorry, This Account is Private.")
        return True
    except TimeoutException:
        # it means that he didn't find the <h2> tag, so probably the account is public
        try:
            WebDriverWait(drvr, 1).until(EC.presence_of_element_located((By.XPATH,'//*[@id="react-root"]/section/main/div/h2')))
            print("[!] Sorry, this page isn't available.")
            return True
        except TimeoutException:
            # it means that he didn't find the <h2> tag, so probably the page is available
            try:
                WebDriverWait(drvr, 1).until(EC.presence_of_element_located((By.XPATH,'//*[@id="react-root"]/section/main/div/div[2]/article/div[1]/div/div[2]/h1')))
                print("[!] Sorry, this account has no posts yet.")
                return True
            except TimeoutException:
                # it means that he didn't find the <h1> tag, so probably the account is valid and not private and have posts
                return False
            except:
                print("An error has occured!!")
                return False


def download_image(url):
    # open photo link
    drvr.get(url)
    
    # Check for login
    insta_login(url)

    # Get username, no.of photos and the link url to name the photos.
    username = get_username()
    number_of_photos, photo_link = number_of_photos_url()

    print("Number of Photos Found: ", number_of_photos)
        
    if number_of_photos == 0:
        # Check if account is private, wrong or empty
        check_private_wrong_empty_acc()

    img_index = 0
    while (img_index < number_of_photos):
        print(f'Downloading {img_index+1} of {number_of_photos} .......')
        li_index = ['2','3','3','3','3','3','3','3','3','3']
        image_src = None
        video_src = None
        # Try to get the url of the image
        try:
            # Single image in one post
            image_src = WebDriverWait(drvr, 3).until(
                EC.visibility_of_element_located((By.XPATH,'//*[@id="react-root"]/section/main/div/div[1]/article/div[2]/div/div/div[1]/img'))).get_attribute('src')
        except TimeoutException:
            try:
                # One photo with mention
                image_src = WebDriverWait(drvr, 0.25).until(
                    EC.visibility_of_element_located((By.XPATH,'//*[@id="react-root"]/section/main/div/div[1]/article/div[2]/div/div/div[1]/div[1]/img'))).get_attribute('src')
            except TimeoutException:
                try:
                    # Search for Single Video
                    video_src = WebDriverWait(drvr, 0.25).until(
                    EC.visibility_of_element_located((By.XPATH,'//*[@id="react-root"]/section/main/div/div[1]/article/div[2]/div/div/div[1]/div/div/video'))).get_attribute('src')
                    print("Video was Found")
                    print(video_src)
                except TimeoutException:
                    try:
                        # Multiple images in one post
                        image_src = WebDriverWait(drvr, 0.25).until(
                            EC.visibility_of_element_located((By.XPATH,'//*[@id="react-root"]/section/main/div/div[1]/article/div[2]/div/div[1]/div[2]/div/div/div/ul/li['+li_index[img_index]+']/div/div/div/div[1]/img'))).get_attribute('src')
                    except TimeoutException:
                        try:
                            # Multiple images but with a mention layer on top of the photo
                            image_src = WebDriverWait(drvr, 0.25).until(
                            EC.visibility_of_element_located((By.XPATH,'//*[@id="react-root"]/section/main/div/div[1]/article/div[2]/div/div[1]/div[2]/div/div/div/ul/li['+li_index[img_index]+']/div/div/div/div[1]/div[1]/img'))).get_attribute('src')
                        except TimeoutException:
                            try:
                                # Video in Multiple images or videos
                                video_src = WebDriverWait(drvr, 0.25).until(
                                EC.visibility_of_element_located((By.XPATH,'//*[@id="react-root"]/section/main/div/div[1]/article/div[2]/div/div[1]/div[2]/div/div/div/ul/li['+li_index[img_index]+']/div/div/div/div[1]/div/div/video'))).get_attribute('src')
                                print("Video was Found")
                                print(video_src)
                            except TimeoutException:
                                # if image url not found
                                print("Failed to obtain image url and video")

        # Download Image
        if image_src != None:
            save_image(image_src,username,photo_link,img_index)

        # Download Video
        if video_src != None:
            save_video(video_src,username,photo_link,img_index)

        if number_of_photos > 1:
            # Click next button
            try:
                next_btn = drvr.find_element_by_class_name("coreSpriteRightChevron")
                next_btn.click()
            except NoSuchElementException:
                # if we can't find next button anymore
                print("All photos in this post has been downloaded successfully.")

        # Increase img_index to download the next image
        img_index += 1


def save_image(image_src,username,photo_link,img_index):
    # Download Image
    try:
        r = urllib.request.urlopen(image_src)
        with open('(' + username + ')' + '_' + str(photo_link) + '_' + '(' + str(img_index + 1) + ')' + ".jpg", "wb") as f:
            f.write(r.read())
    except KeyboardInterrupt:
        drvr.quit()
        exit(1)
    except:
        print("[!] An error has happened while downloading photo.")


def save_video(video_src,username,photo_link,img_index):
    # Download Video
    try:
        r = urllib.request.urlopen(video_src)
        with open('(' + username + ')' + '_' + str(photo_link) + '_' + '(' + str(img_index + 1) + ')' + ".mp4", "wb") as f:
            f.write(r.read())
    except KeyboardInterrupt:
        drvr.quit()
        exit(1)
    except URLError:
        print(f"Couldnot download video, Unkown URL Type: {video_src}")
    except :
        print("[!] An error has happened while downloading video.")


def download_posts():
    global target_username, fin_no_of_posts, req_no_of_posts

    if not username_obtained:
        target_username = get_username()
    
    number_of_photos, photo_link = number_of_photos_url()

    print("---------------------------------------------------------------") 
    print(f'Photo Link: {photo_link} with Number of Photos : {number_of_photos}')
    
    img_index = 0
    while ((img_index < number_of_photos) and (img_index <= 9) and (fin_no_of_posts < req_no_of_posts)):
        print(f'Downloading {img_index+1} of {number_of_photos} .......')
        image_src = None
        video_src = None
        li_index = ['2','3','3','3','3','3','3','3','3','3']
        # Try to get the url of the image
        try:
            # Single image in one post
            image_src = WebDriverWait(drvr, 3).until(
                EC.visibility_of_element_located((By.XPATH,'/html/body/div[5]/div[2]/div/article/div[2]/div/div/div[1]/img'))).get_attribute('src')
        except TimeoutException:
            try:
                # Single image with mention
                if number_of_photos == 1:
                    image_src = WebDriverWait(drvr, 1).until(
                        EC.visibility_of_element_located((By.XPATH,'/html/body/div[5]/div[2]/div/article/div[2]/div/div/div[1]/div[1]/img'))).get_attribute('src')
                else:
                    raise TimeoutException
            except TimeoutException:
                try: 
                    # Single Video Only
                    if number_of_photos == 1:
                        video_src = WebDriverWait(drvr, 1).until(
                        EC.visibility_of_element_located((By.XPATH,'/html/body/div[5]/div[2]/div/article/div[2]/div/div/div[1]/div/div/video'))).get_attribute('src')
                        print("Video was Found")
                        print(video_src)
                    else:
                        raise TimeoutException
                except TimeoutException:
                    try:
                        # Multiple images in one post
                        image_src = WebDriverWait(drvr, 1).until(
                            EC.visibility_of_element_located((By.XPATH,'/html/body/div[5]/div[2]/div/article/div[2]/div/div[1]/div[2]/div/div/div/ul/li['+li_index[img_index]+']/div/div/div/div[1]/img'))).get_attribute('src')
                    except TimeoutException:
                        try:
                            # Multiple images but with a mention layer on top of the photo
                            image_src = WebDriverWait(drvr, 0.25).until(
                                EC.visibility_of_element_located((By.XPATH,'/html/body/div[5]/div[2]/div/article/div[2]/div/div[1]/div[2]/div/div/div/ul/li['+li_index[img_index]+']/div/div/div/div[1]/div[1]/img'))).get_attribute('src')
                        except TimeoutException:
                            try:
                                # Search for Video not image
                                video_src = WebDriverWait(drvr, 0.25).until(
                                EC.visibility_of_element_located((By.XPATH,'/html/body/div[5]/div[2]/div/article/div[2]/div/div[1]/div[2]/div/div/div/ul/li['+li_index[img_index]+']/div/div/div/div[1]/div/div/video'))).get_attribute('src')
                                print("Video was Found")
                                print(video_src)
                            except TimeoutException:
                                # if image url not found
                                print("Failed to obtain image url or video")

        # Download Image
        if image_src != None:
            save_image(image_src,target_username,photo_link,img_index)
            if number_of_photos == 1:
                print('All photos on this post has been downloaded successfully.')
                fin_no_of_posts += 1
                print(f'Finished posts: {fin_no_of_posts} of {req_no_of_posts}')

        if video_src != None:
            save_video(video_src,target_username,photo_link,img_index)
            if number_of_photos == 1:
                print('All photos on this post has been downloaded successfully.')
                fin_no_of_posts += 1 
                print(f'Finished posts: {fin_no_of_posts} of {req_no_of_posts}')

        if number_of_photos > 1:
            # Click next image button in the same post
            try:
                next_btn = drvr.find_element_by_class_name("coreSpriteRightChevron")
                next_btn.click()
            except NoSuchElementException:
                # if we can't find next image button anymore
                print("All photos on this post has been downloaded successfully.")
                fin_no_of_posts += 1
                print(f'Finished posts: {fin_no_of_posts} of {req_no_of_posts}')

        # Increase img_index to download the next image
        img_index += 1

    if fin_no_of_posts == req_no_of_posts:
        print("[~] InstaGrab has finished dowloading all specified posts.")
        return True
    
    try:
        # Move to next post
        drvr.find_element_by_class_name("coreSpriteRightPaginationArrow").click()
        download_posts()
    except NoSuchElementException:
        print("[~] InstaGrab has finished dowloading all posts.")
        return True

def get_t_posts():
    try:
        f_t_posts = str(WebDriverWait(drvr, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR,'span.g47SY'))).text).replace(',','')
        return int(f_t_posts)
    except TimeoutException:
        print("Cannot find total number of posts")
        return None

def download_user(USERNAME):
    global logged_in, total_posts, req_no_of_posts

    url = 'https://www.instagram.com/' + USERNAME + '/'

    drvr.get(url)

    # Check for login form and login in
    if not insta_login(url):
        return False

    # Check if account is private or not
    if check_private_wrong_empty_acc():
        return False

    if logged_in:
        total_posts = get_t_posts()
        print("Total posts this user has: ", total_posts)

        answer=''
        while answer not in ("yes", "no", 'y', 'n'):
            answer = input("Do you want to download all posts? Enter Yes/(Y) or No/(N): ").lower()
            if answer == "yes" or answer == 'y':
                req_no_of_posts = total_posts
                print("Downloading all posts ...")
            elif answer == "no" or answer == 'n':
                posts_range = 0
                while posts_range not in range(1, total_posts + 1):
                    try:
                        posts_range = int(input(f"Please, Specify your range of posts (1 - {total_posts}): "))
                        req_no_of_posts = posts_range
                        if posts_range not in range (1, total_posts + 1):
                            raise ValueError
                    except ValueError:
                        print(f"Value Error, Please a valid number in range (1 - {total_posts})")
                    except KeyboardInterrupt:
                        print("Terminating InstaGrab Process ...")
                        return False

    # Javascript code to click on the first photo
    try:
        drvr.execute_script(
            '''
            document.getElementsByClassName('KL4Bh')[0].click()
            '''
        )
    except JavascriptException:
        print("Couldn't click on the first image")
    except :
        print("[!] Unknown error has occured, Terminating Process ...")
        return False

    if not logged_in:
        # to optimize: try to find this xpath first /html/body/div[5]/div[2]/div/article or check browser's url
        if drvr.current_url == url:
            if not insta_login_popup():
                return False
            else:
                download_user(prompted_username)
        else:
            download_posts()
    else:
        download_posts()


if __name__ == "__main__":
    # prompt user for credentials (GUI OR CLI interactive)
    time.sleep(1)
    print("Welcome to InstaGrab v1.0 By Mouhab-dev")
    print("")
    print("Please Choose one of the two following options:")
    print("")
    print("     1) Download Posts for a given User")
    print("     2) Download Only One Post")
    print("")

    choice = 0
    while choice not in range(1,3) :
        try:
            choice = int(input("Your Choice: "))
            if choice not in range (1,3):
                raise ValueError
        except ValueError:
            print("Value Error, Please enter either 1 or 2")
        except KeyboardInterrupt:
            print("Terminating InstaGrab Process ...")
            break

    # 1st Choice
    if choice == 1 :
        try:
            prompted_username = ''
            while prompted_username == '' :
                prompted_username = input("Please Enter The Target Username: ")
            download_user(prompted_username)
        except KeyboardInterrupt:
            print("Terminating InstaGrab Process ...")

    # 2nd Choice
    elif choice == 2:
        Valid_URL = False
        while not Valid_URL:
            try:
                prompted_url = input("Please Enter The Post URL: ")
                download_image(prompted_url)
                Valid_URL = True
            except InvalidArgumentException:
                print("Please enter a valid URL")
            except KeyboardInterrupt:
                print("Terminating InstaGrab Process ...")

    drvr.quit()
    exit(0)