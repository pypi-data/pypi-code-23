import websocket
import threading
import json
import logging
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime
from asciiRyver.framework import Builder



class Client(object):


  def __init__(self, params, model):
    self.params = params
    self._model = model


  def _on_send(self, jid, msg):
      self.data = {'type': 'chat',
                   'text': msg,
                   'to': jid}
      self.ws.send(json.dumps(self.data))
      return

  def _send_topic(self, id, msg):
      self.data = {'comment': msg,
                   'post': {
                       'id': str(id)
                   }}
      self.headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
      self._sender = requests.post('https://'+self.org+'.ryver.com/api/1/odata.svc/postComments',
                                   auth=HTTPBasicAuth(self.username, self.password), data=json.dumps(self.data),
                                   headers=self.headers)



  def on_message(self, ws, message):
    self._message = json.loads(message)
    if self._message['type'] == 'chat':
        self._chatHandler()
    elif self._message['type'] == 'event':
        self._eventHandler()
    else:
      #logging.debug(message)
      pass


  def on_error(self, ws, error):
    logging.debug(error)

  def on_close(self, ws):
    logging.debug("Connection closed!")

  def on_open(self, ws):
      self.info = {'type': 'auth',
             'authorization': 'Session '+self.sessionid, 'agent': 'Ryver',
              'resource': 'Contatta-1516859178732'}
      self.ws.send(json.dumps(self.info))
      logging.debug('Connection established!')

  def run(self, params):
      self.username = params.get('email')
      self.password = params.get('password')
      self.org = params.get('org')
      self.jsondata = params.get('data')
      self.socketaddr = self.jsondata['d']['services']['chat']
      self.sessionid = self.jsondata['d']['sessionId']
      self.ws = websocket.WebSocketApp(self.socketaddr, on_message=self.on_message, on_error=self.on_error,
                                       on_close=self.on_close)
      self.ws.on_open = self.on_open
      self.t1 = threading.Thread(target=self.ws.run_forever)
      self.t1.daemon = True
      self.t1.start()

  def _postHandler(self):
      self._currentChat = Builder.CurrentChat
      # See if current chat is in the Topics Dictionary
      if self._currentChat in Builder._builtTopics.keys():
        self._postID = self._message['data']['created'][0]['postId']
        self._msgID = self._message['data']['created'][0]['id']
        if Builder._builtTopics[self._currentChat] == self._postID:
           self._postComment = requests.get('https://'+self.org+'.ryver.com/api/1/odata.svc/postComments('
                                            +str(self._msgID)+')?%24expand=createUser', auth=(self.username, self.password))

           self._commentInfo = self._postComment.json()
           self._text = self._commentInfo['d']['results']['comment']
           self._postUser = self._commentInfo['d']['results']['createUser']['username']
           self._time = datetime.now().strftime("%H:%M:%S")
           self._constructMsg = '[' + self._time + '] ' + self._postUser + ': ' + self._text
           self._model._messageQueue.append(self._constructMsg)
           self._model._signal.set()
           # Add Formatting


  def _chatHandler(self):
      # DM Alerting needs reworking.
      self._myJid = Builder.myJid
      self._currentChat = Builder.CurrentChat
      if self._currentChat in Builder._builtForum.keys():
          # It's a forum/workgroup
          self._currentChatJid = Builder._builtForum[self._currentChat][1]
          if self._message['to'] == self._currentChatJid:
              self._messageFormatter()
          # Received a DM while not directly chatting in a forum/workgroup
          elif self._message['to'] == self._myJid:
              self._messageFormatter(dm=True)
      elif self._currentChat in Builder._builtUsers.keys():
          # We are DM'ing a user
          self._currentUserJid = Builder._builtUsers[self._currentChat][1]
          if self._message['from'] == self._currentUserJid or self._message['to'] == self._currentUserJid:
              self._messageFormatter()
          # We received a DM from a user other than the one we are chatting with
          elif self._message['from'] != self._currentUserJid and self._message['to'] == self._myJid:
              self._messageFormatter(dm=True)
      elif self._currentChat in Builder._builtTopics.keys():
          # We are in a Topic, but we still should know about DM's
          if self._message['to'] == self._myJid:
              self._messageFormatter(dm=True)
      else:
          pass



  def _messageFormatter(self, dm=False):
      try:
        self._text = self._message['text']
      except KeyError:
        self._text = ''
      self._fromJid = self._message['from']
      for self.i in Builder._builtUsers.keys():
          if Builder._builtUsers[self.i][1] == self._fromJid:
              self._fromUser = self.i
      self._time = datetime.now().strftime("%H:%M:%S")
      if dm:
          self._constructMsg = '*DM* [' + self._time + '] ' + self._fromUser + ': ' + self._text
      else:
          self._constructMsg = '['+self._time+'] '+self._fromUser+': '+self._text
      self._model._messageQueue.append(self._constructMsg)
      self._model._signal.set()

  def _eventHandler(self):
      if self._message['topic'] == "/api/activityfeed/postComments/changed":
          self._postHandler()
      else:
          pass
          #More to be added
          #Presence Change?

