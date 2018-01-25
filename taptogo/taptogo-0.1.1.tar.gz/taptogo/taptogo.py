import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import Select

from bs4 import BeautifulSoup

class TapToGo(object):
    base_url = 'https://www.taptogo.net/'

    def __init__(self):
        self.driver = webdriver.PhantomJS()
        self.driver.get(self.base_url)

    def login(self, email, password):
        self.email = email
        self.driver.find_element_by_id('j_id0:tapwrapper:loginform:login-email').send_keys(email)
        self.driver.find_element_by_id('j_id0:tapwrapper:loginform:login-password').send_keys(password)
        
        with wait_for_page_load(self.driver):
            self.driver.find_element_by_id('j_id0:tapwrapper:loginform:login-submit').click()
        
        self.logged_in = True

        # Check for error message on failed login
        try:
            error_div = self.driver.find_element_by_css_selector('div.page-messages')
            if 'your login attempt has failed' in error_div.text.lower():
                self.logged_in = False
                return False
            else:
                return True
        except NoSuchElementException:
            return True
    
    def describe_tap_cards(self):
        if not self.logged_in:
            raise Exception('You must log in before describing cards')
        
        # This page is at /TAPMyCards, but for some reason it 
        # doesn't load correctly unless you click the link.
        self.driver.get(self.base_url)
        with wait_for_page_load(self.driver):
            self.driver.find_element_by_link_text('My TAP cards').click()

        cards_wrapper = self.driver.find_element_by_id('MyCards:tapwrapper:cardList').get_attribute('innerHTML')
        soup = BeautifulSoup(cards_wrapper, "html.parser")
        cards = []

        for div in soup.findAll('div'):
            if 'panel-card' in div.get('class', ''):
                card = {}
                for div in div.findAll('div'):
                    if 'panel-heading' in div.get('class', ''):
                        for h2 in div.findAll('h2'):
                            card['name'] = h2.text.split('-')[0].strip()
                    elif 'panel-collapse' in div.get('class', ''):
                        if 'card-' in div['id'] and '-panel' in div['id']:
                            card['id'] = div['id'].replace('card-', '').replace('-panel', '')
                            card['balance'] = float(div.findAll('div')[0].findAll('h4')[0].findAll('span')[0].text.replace('$', ''))

                            for link in div.findAll('a'):
                                link_text = link.text.lower().strip()
                                if link_text == 'add fare':
                                    card['reload_url'] = self.base_url + link['href']
                                elif link_text == 'view history':
                                    card['history_url'] = self.base_url + link['href']
                                elif link_text == 'report lost or stolen card':
                                    card['cancel_url'] = self.base_url + link['href']
                            
                            cards.append(card)
        self.cards = cards
        return cards
    
    def add_stored_value(self, amount, tap_card_id=None, reload_url=None,
                         card_dict=None, card_name=None, card_num=None,
                         card_exp_month=None, card_exp_year=None, card_cvv=None,
                         confirmation_email=None, card_address=None, card_state=None,
                         card_city=None, card_zip=None, card_country=None):
        if not card_dict and not card_num:
            raise AttributeError('card_dict or card_num are required.')
        
        if not tap_card_id and not reload_url:
            raise AttributeError('tap_card_id or reload_url are required.')

        if not card_dict:
            card_dict = {
                'name': card_name,
                'num': card_num,
                'exp_month': card_exp_month,
                'exp_year': card_exp_year,
                'cvv': card_cvv,
                'address': card_address,
                'city': card_city,
                'state': card_state,
                'zip': card_zip,
                'country': card_country
            }
        
        if not confirmation_email:
            confirmation_email = self.email
        
        if tap_card_id and not reload_url:
            for card in self.cards:
                if card['id'] == tap_card_id:
                    reload_url = card['reload_url']
        
        if not reload_url:
            raise AttributeError('Unknown card, use describe_cards or pass reload_url parameter')
        
        self.driver.get(reload_url)
        self.driver.find_element_by_link_text('Add Stored Value').click()
        self.driver.implicitly_wait(2)

        self.driver.find_element_by_id('ShoppingCart:tapwrapper:j_id98:farevalue').send_keys(str(amount))
        self.driver.find_element_by_id('ShoppingCart:tapwrapper:j_id98:j_id146').click()
        self.driver.implicitly_wait(2)

        self.driver.find_element_by_css_selector('.dropdown-toggle').click()
        self.driver.implicitly_wait(2)

        with wait_for_page_load(self.driver):
            self.driver.find_element_by_link_text('Edit and Checkout').click()
        
        with wait_for_page_load(self.driver):
            self.driver.find_elements_by_xpath("//input[@value='Complete Checkout']")[0].click()
        
        cart_amt = self.driver.find_element_by_css_selector('span.total_value').text
        if float(cart_amt) != float(amount):
            raise Exception("Cart amount doesn't match [{} != {}]".format(cart_amt, amount))
        
        self.driver.find_element_by_id('exact_cardholder_name').send_keys(card_dict['name'])
        self.driver.find_element_by_id('x_card_num').send_keys(card_dict['num'])
        self.driver.find_element_by_id('x_exp_date').send_keys(str(card_dict['exp_month']) + str(card_dict['exp_year']))
        self.driver.find_element_by_id('x_card_code').send_keys(card_dict['cvv'])
        
        try:
            self.driver.find_element_by_id('x_address').send(card_dict['address'])

            state_select = Select(self.driver.find_element_by_id('x_state'))
            state_select.select_by_visible_text(card_dict['state'])

            self.driver.find_element_by_id('x_city').send(card_dict['city'])
            self.driver.find_element_by_id('x_zip').send(card_dict['zip'])

            country_select = Select(self.driver.find_element_by_id('x_country'))
            country_select.select_by_visible_text(card_dict['country'])
        except AttributeError:
            # ignore errors caused by a stored address
            pass

        self.driver.find_element_by_id('cc_email').send_keys(confirmation_email)
        
        with wait_for_page_load(self.driver):
            self.driver.find_element_by_xpath("//input[@name='commit']").click()
        
        try:
            error_message = self.driver.find_element_by_css_selector('div.fieldErrorMessage').get_attribute('innerHTML')
            raise Exception(error_message)
        except NoSuchElementException:
            if 'Your Order Has Been Submitted' in client.page_source:
                return True
        return False

# http://www.obeythetestinggoat.com/how-to-get-selenium-to-wait-for-page-load-after-a-click.html
class wait_for_page_load(object):
    def __init__(self, browser):
        self.browser = browser

    def __enter__(self):
        self.old_page = self.browser.find_element_by_tag_name('html')

    def page_has_loaded(self):
        new_page = self.browser.find_element_by_tag_name('html')
        return new_page.id != self.old_page.id

    def __exit__(self, *_):
        self.wait_for(self.page_has_loaded)
    
    def wait_for(self, condition_function):
        start_time = time.time()
        while time.time() < start_time + 30:
            if condition_function():
                return True
            else:
                time.sleep(0.1)
        raise Exception(
            'Timeout waiting for {}'.format(condition_function.__name__)
        )