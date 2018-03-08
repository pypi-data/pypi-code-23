from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
import time
from .pipelines import SaveToFilePipeline, SaveToMongoPipeline
from .entities import Follower,Following
from .settings import settings
from collections import deque

class Extractor(object):
    __prev_size, __size = None,None
    __driver = None
    __user = None
    __tweets = None
    __nFollowers = None
    __nFollowing = None
    __time = None
    __cantU = None
    __idUser = None
    __saveFile = None
    __userAuth = None
    __passAuth = None
    __users = None 
    __timeExtract = None

    def __init__(self, user =settings.USER_AUTH, passwd = settings.PASS_AUTH,  cantU = settings.TOTAL_USERS_EXTRACT, timeExt = settings.TOTAL_EXTRACT_TIME):
        self.__saveFile = SaveToFilePipeline() if(settings.SAVE_MODE == "Disk") else SaveToMongoPipeline()
        self.__userAuth = user
        self.__passAuth = passwd
        self.__cantU = cantU
        self.__timeExtract = timeExt

    def __getData(self, user):
        ''' Obtiene la info del usuario que le llega '''
        self.__driver.get("https://twitter.com/{}".format(user))
        idi = self.__driver.find_elements_by_xpath("//div[@data-user-id][@data-screen-name='{}']".format(user))
        try:
            self.__idUser = idi[0].get_attribute("data-user-id")
        except:
            raise 
        time.sleep(self.__timeExtract)
        self.__driver.get("https://twitter.com/{}/followers".format(user))
        elementos = self.__driver.find_elements_by_class_name("ProfileNav-value")
        try:
            self.__nFollowing = int(elementos[1].get_attribute("data-count"))
        except:
            self.__nFollowing = 0
        try:
            self.__nFollowers = int(elementos[2].get_attribute("data-count"))
        except:
            self.__nFollowers = 0
        time.sleep(self.__timeExtract)
    
    def __move(self, b):
        ''' Logra desplazar la ventana hacia abajo para cargar mas usuarios '''
        count = 0
        while self.__prev_size < b and count < 2:
            print(count)
            wait = WebDriverWait(self.__driver, 10)
            height = self.__driver.execute_script("var h=document.body.scrollHeight; window.scrollTo(0, h); return h;")
            time.sleep(self.__timeExtract)
            try:
                a = wait.until(lambda drv: drv.execute_script("return document.documentElement.scrollHeight;") > height)
                break
            except:
                count +=1
                continue
        return count==2

    def __openConnection(self):
        ''' Abre una conexcion con Twitter '''
        self.__driver = webdriver.Firefox()
        #self.__driver = webdriver.PhantomJS("phantomjs")
        self.__driver.get("https://twitter.com/login")
        time.sleep(self.__timeExtract)
        self.__prev_size, self.__size = 0,0
        username = self.__driver.find_element_by_xpath("//div[contains(@class,'clearfix field')]/input[contains(@name,'username')]")
        password = self.__driver.find_element_by_xpath("//div[contains(@class,'clearfix field')]/input[contains(@name,'password')]")
        username.send_keys(self.__userAuth)
        password.send_keys(self.__passAuth)
        self.__driver.find_element_by_xpath("//button[contains(., 'Log in')]").submit()
        time.sleep(self.__timeExtract)
        
    def __closeConnection(self):
        ''' Cierra la conexion con Twitter '''
        self.__driver.close()

    def __getFollowers(self, user):
        ''' Extrae los followers del usuario que le llega '''
        self.__driver.get("https://twitter.com/{}/followers".format(user))
        followers =  self.__driver.find_elements_by_class_name("ProfileCard")
        self.__size = self.__nFollowers
        self.__prev_size=0
        lista = []
        print()
        print("followers size: {}, prev: {}, size: {}".format(len(followers), self.__prev_size, self.__size) )
        while self.__prev_size < self.__nFollowers:
            if(self.__cantU!=-1 and self.__prev_size >= self.__cantU): break
            for follower in followers[self.__prev_size:]:
                self.__prev_size+=1
                follow = Follower(self.__idUser, self.__user, follower.get_attribute("data-user-id"), follower.get_attribute("data-screen-name"))
                self.__saveFile.process_item(follow)
                lista.append(follow.nameFollower)
                #print("Screen-name: ", follower.get_attribute("data-screen-name"))
                #print("user id: ", follower.get_attribute("data-user-id"))
                #print("fullname: ", follower.find_element_by_class_name("fullname").text.encode('utf-8'))
            if(self.__move(self.__nFollowers)): break
            time.sleep(self.__timeExtract)
            followers =  self.__driver.find_elements_by_class_name("ProfileCard")
            self.__size = len(followers)
            print("followers size: {}, prev: {}, size: {}".format(len(followers), self.__prev_size, self.__size) )
        return lista
    
    def __getFollowing(self, user):
        ''' Extrae los followings del usuario que le llega '''
        self.__driver.get("https://twitter.com/{}/following".format(user))
        followings =  self.__driver.find_elements_by_class_name("ProfileCard")
        self.__size = len(followings)
        self.__prev_size = 0
        lista = []
        print("following size: {}, prev: {}, size: {}".format(len(followings), self.__prev_size, self.__size) )
        while self.__prev_size < self.__nFollowing:
            if(self.__cantU!=-1 and self.__prev_size >= self.__cantU): break
            for following in followings[self.__prev_size:]:
                self.__prev_size+=1
                follow = Following(self.__idUser, self.__user, following.get_attribute("data-user-id"), following.get_attribute("data-screen-name"))
                self.__saveFile.process_item(follow)
                lista.append(follow.nameFollowing)
                #print("Screen-name: ", following.get_attribute("data-screen-name"))
                #print("user id: ", following.get_attribute("data-user-id"))
                #print("fullname: ", following.find_element_by_class_name("fullname").text.encode('utf-8'))
            if(self.__move(self.__nFollowing)): break
            time.sleep(self.__timeExtract)
            followings =  self.__driver.find_elements_by_class_name("ProfileCard")
            self.__size = len(followings)
            print("following size: {}, prev: {}, size: {}".format(len(followings), self.__prev_size, self.__size) )
        return lista

    def getFollowers(self, user):
        ''' Transaccion de extraccion de los Followers '''
        lista = []
        self.__openConnection()
        try:
            self.__getData(user)
        except:
            print("Usuario no encontrado")
        lista=self.__getFollowers(user)
        self.__closeConnection()
        return lista
        
    def getFollowing(self, user):
        ''' Transaccion de extraccion de los Following '''
        lista = []
        self.__openConnection()
        try:
            self.__getData(user)
        except:
            print("Usuario no encontrado")
        lista=self.__getFollowing(user)
        self.__closeConnection()
        return lista
        
    def getFollowersAndFollowing(self, user):
        ''' Transaccion de extraccion de los (1)Followers y (2)Following '''
        lista = []
        self.__openConnection()
        try:
            self.__getData(user)
        except:
            print("Usuario no encontrado")
        lista=self.__getFollowers(user)
        lista+=self.__getFollowing(user)
        self.__closeConnection()
        return lista

    def getFollowingAndFollowers(self, user):
        ''' Transaccion de extraccion de los (1)Following y (2)Followers '''
        lista = []
        self.__openConnection()
        try:
            self.__getData(user)
        except:
            print("Usuario no encontrado")
        lista=self.__getFollowing(user)
        lista+=self.__getFollowers(user)
        self.__closeConnection()
        return lista
