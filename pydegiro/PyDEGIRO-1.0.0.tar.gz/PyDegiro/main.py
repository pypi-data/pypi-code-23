import requests
import json
from PyDegiro.consts import *


class DegrioApi:
    """
    Default constructor, to set default values

    :param user: user login id
    :type user: str
    :param passwd: user login password
    :param session_id: user session id (default None)
    :type session_id: str
    :param account_no: user account id retrieved from server
    :type account_no: str
    """

    def __init__(self, user, passwd, session_id=None, account_no=None):
        print("[*] initializing")

        self.session_id = session_id
        self.user_name = user
        self.password = passwd
        self.account_no = account_no

        self.pa_url = None
        self.product_search_url = None
        self.product_types_url = None
        self.reporting_url = None
        self.trading_url = None
        self.vwd_quote_cast_service_url = None

        self.user_token = None
        self.client_info = None

        self.base_url = "https://trader.degiro.nl"

    """
    Login to the server
    """

    def login(self):
        print("[*] login " + self.user_name + " to server")

        url = self.base_url + '/login/secure/login'
        payload = {
            "username": self.user_name,
            "password": self.password,
            "isRedirectToMobile": False,
            "loginButtonUniversal": '',
            "queryParams": {"reason": "session_expired"}
        }

        session = requests.session()

        res = session.post(url, json.dumps(payload))
        # print(res.headers)
        if not res.cookies.get("JSESSIONID"):
            print("[x] login error")
        else:
            self.session_id = res.cookies.get('JSESSIONID')
            print("[+] logged in successfully !  Session ID: ", format(self.session_id))
            self.get_config(session)
            self.get_client_info(session)

        return session

    """
    Get important URL's from server
    
    :param session: user session returned by login()
    :type session: Session
    """

    def get_config(self, session):
        print("[*] fetch configs from server")

        config_url = self.base_url + '/login/secure/config'

        res = session.get(config_url)
        if res.status_code == requests.codes.ok:
            print("[+] configs fetch Ok")
            res_json = json.loads(res.content)
            self.pa_url = res_json['paUrl']
            self.product_search_url = res_json['productSearchUrl']
            self.product_types_url = res_json['productTypesUrl']
            self.reporting_url = res_json['reportingUrl']
            self.trading_url = res_json['tradingUrl']
            self.vwd_quote_cast_service_url = res_json['vwdQuotecastServiceUrl']
        else:
            print("[x] configs fetch error: ", format(res.status_code))

    """
    Get client info from server
    
    :param session: user session object
    :type session: Session
    """

    def get_client_info(self, session):

        print("[*] fetch client info from server")
        url = self.pa_url + 'client?sessionId=' + self.session_id
        res = session.get(url)

        if res.status_code == requests.codes.ok:
            print('[+] client info fetch success')
            res_json = json.loads(res.content)
            self.account_no = res_json['intAccount']
            self.user_token = res_json['id']
        else:
            print('[x] client info fetch error: {0}'.format(res.status_code))

    """
    Create vwd session on server
    Thanks to the postman client :)
    
    :param session: user session object
    :type session: Session
    """

    def request_vwd_session(self):
        print(self.user_token)
        url = "https://degiro.quotecast.vwdservices.com/CORS/request_session"
        query_string = {"version": "1.0.20170315", "userToken": self.user_token}
        payload = "{\"referrer\":\"https://trader.degiro.nl\"}"
        headers = {
            'content-type': "application/json",
            'origin': "https://trader.degiro.nl",
            'cache-control': "no-cache"
        }

        res = requests.request("POST", url, data=payload, headers=headers, params=query_string)
        return res.json()
    """
    Under Construction, do not un-comment
    
    def get_ask_bid_price(self, issue_id, times_checked = 0):
        vwd_session_id = self.request_vwd_session()

        def check_data(response):
            time = times_checked
            time += 1
            prices = {}

            print(len(response))

            print(response[0].get('m'))
            if len(response) == 1:
                if time <= 3:
                    self.get_ask_bid_price(issue_id, time)
                else:
                    print("all tries exceeded")

        vwd_session = vwd_session_id.get("sessionId")

        url = "https://degiro.quotecast.vwdservices.com/CORS/"
        urljoin(url, quote_plus(vwd_session))
        print(url)

        payload = "{\r\n        \"controlData\": \"req(350009261.BidPrice);req(350009261.AskPrice);
        req(350009261.LastPrice);req(350009261.LastTime);\"\r\n    }"
        headers = {
            'origin': "https://trader.degiro.nl",
            'content-type': "application/json",
            'cache-control': "no-cache"
        }

        response = requests.request("POST", url, data=payload, headers=headers)
        print(response.text)
        check_data(response.json())
    """

    """
    Get portfolio from server
    
    :param session: user session object
    :type session: Session
    """

    def get_portfolio(self, session):
        update_url = '{trading_url}v5/update/'.format(trading_url=self.trading_url)
        res = session.get(
            "{update_url}{account_id};""jsessionid={jsession_id}".format(
                update_url=update_url,
                account_id=self.account_no,
                jsession_id=self.session_id),
            params={'portfolio': 0, 'totalPortfolio': 0})
        if res.status_code == requests.codes.ok or res.status_code == 201:
            return res.json()
        else:
            return '{"Error":"Could not fetch portfolio", "StatusCode":{status_code}}'.format(
                status_code=res.status_code)

    """
    Get cash funds info from server
    
    :param session: user session object
    :type session: Session
    """

    def get_cash_funds(self, session):
        update_url = '{trading_url}v5/update/'.format(trading_url=self.trading_url)
        res = session.get(
            "{update_url}{account_id};""jsessionid={jsession_id}".format(
                update_url=update_url,
                account_id=self.account_no,
                jsession_id=self.session_id),
            params={'cashFunds': 0})
        if res.status_code == requests.codes.ok or res.status_code == 201:
            return res.json()
        else:
            return '{"Error":"Could not fetch/create cash funds", "StatusCode":{status_code}}'.format(
                status_code=res.status_code)

    """
    Get orders from server
    
    :param session: user session object
    :type session: Session
    """

    def get_orders(self, session):
        update_url = '{trading_url}v5/update/'.format(trading_url=self.trading_url)
        res = session.get(
            "{update_url}{account_id};""jsessionid={jsession_id}".format(
                update_url=update_url,
                account_id=self.account_no,
                jsession_id=self.session_id
            ),
            params={'orders': 0, 'historicalOrders': 0, 'transactions': 0}
        )

        if res.status_code == requests.codes.ok or res.status_code == 201:
            return res.json()
        else:
            return '{"Error":"Could not fetch/create orders", "StatusCode":{status_code}}'.format(
                status_code=res.status_code)

    """
    Search a product based on various criterion
    
    :param session: User login session
    :param type: Session
    :param search_text: Text to search
    :param type: str
    :param sort_column: Column to sort by
    :param type: str
    :param sort_type: sort type asc/desc
    :param type: str
    """

    def search_product(self, session, search_text, sort_column, sort_type, product_type=product_types.get("all"),
                       limit=7,
                       offset=0):
        payload = {
            'searchText': search_text,
            'productTypeId': product_type,
            'sortColumns': sort_column,
            'sortTypes': sort_type,
            'limit': limit,
            'offset': offset
        }

        search_url = '{search_url}v5/products/lookup?intAccount={account_id}&sessionId={session_id}&'.format(
            search_url=self.product_search_url,
            account_id=self.account_no,
            session_id=self.session_id)

        res = session.get(search_url, params=payload)
        if res.status_code == requests.codes.ok:
            return res.json()
        else:
            return '{"Error": "Error in searching product", "StatusCode":{status_code}}'.format(
                status_code=res.status_code)

    """
    Delete order
    
    :param session: user session
    :param type: Session
    :param order_id: order id to be deleted
    :param type: str
    """
    def delete_order(self, session, order_id):
        delete_url = '{trading_url}v5/order/{order_id};jsessionid={session_id}?intAccount={account_id}' \
                     '&sessionId={sessionid}'.format(
                        trading_url=self.trading_url,
                        order_id=order_id,
                        session_id=self.session_id,
                        account_id=self.account_no,
                        sessionid=self.session_id)
        res = session.delete(delete_url)
        if res.status_code == requests.codes.ok:
            return res.json()
        else:
            return '{"Error":"Unknown error", "StatusCode":{status_code}}'.format(status_code=res.status_code)

    """
    :param session
    :type Session
    
    :param order
    :type json
    """

    def check_order(self, session, order):
        check_url = '{trading_url}v5/checkOrder;jsessionid={session_id}?intAccount={account_id}&sessionId={sessionId}' \
            .format(
                trading_url=self.trading_url,
                session_id=self.session_id,
                account_id=self.account_no,
                sessionId=self.session_id
            )

        payload = json.dumps(order)
        headers = {'Content-Type': 'application/json;charset=UTF-8'}

        res = session.post(check_url, data=payload, headers=headers)
        return res.json()

    """
    Function needs to be tested !
    
    :param session
    :type Session
    
    :param order
    :type json
    
    :param confirmation_id
    :type String
    """

    def confirm_order(self, session, order, confirmation_id):
        confirm_url = '{trading_url}v5/order/{confirm_id};jsessionid={session_id}?intAccount={account_id}' \
                      '&sessionId={session_Id}'.format(
                        trading_url=self.trading_url,
                        confirm_id=confirmation_id,
                        session_id=self.session_id,
                        account_id=self.account_no,
                        session_Id=self.session_id
                        )
        payload = json.dumps(order)
        headers = {'Content-Type': 'application/json'}

        res = session.post(confirm_url, data=payload, headers=headers)
        return res.json()

    """
    Complete an order
    :param order
    :type json
    
    :param session
    :type Session
    
    :param order
    :type {buysell, orderType, productId, size, timeType, price, stopPrice}
    """

    def set_order(self, session, order):
        res = self.check_order(session, order)
        order_status = res.get("status")
        if order_status == 0:
            confirm_id = res.get("confirmationId")
            confirmation_res = self.confirm_order(session, order, str(confirm_id))
            return confirmation_res
        else:
            return res

    """
    Get multiple orders by ids
    
    :param session: user session
    :param type: Session
    :param product_ids: list of product ids
    :param type: list
    """
    def get_products_by_ids(self, session, product_ids):
        products_url = '{search_url}v5/products/info?intAccount={account_id}&sessionId={session_id}'.format(
            search_url=self.product_search_url,
            account_id=self.account_no,
            session_id=self.session_id)
        headers = {'Content-Type': 'application/json'}

        res = session.post(products_url, data=product_ids, headers=headers)
        return res.json()
