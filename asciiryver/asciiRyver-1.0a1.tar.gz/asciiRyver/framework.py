import requests
from requests.auth import HTTPBasicAuth
import logging
import json




class Builder(object):

  newMessages = []
  CurrentMessages = []
  CurrentUsers = {}
  CurrentUser = 'Not Logged In'
  CurrentChat = "No Room Selected"
  myJid = ''
  _builtForum = {}
  _builtUsers = {}
  _builtTopics = {}

  def __init__(self, params):
    self.username = params.get('email')
    self.password = params.get('password')
    self.org = params.get('org')
    self.jsondata = params.get('data')
    self.socketaddr = self.jsondata['d']['services']['chat']
    self.sessionid = self.jsondata['d']['sessionId']
    logging.debug(self.username)
    self.pullInfo()
    logging.debug(Builder._builtForum)

  def pullInfo(self):
      self.ryverData = requests.get('https://'+self.org+'.ryver.com/api/1/odata.svc/Ryver.Info()',
                               auth=(self.username, self.password))
      self.ryverInfo = self.ryverData.json()
      self.user_build = self.createUserDict(self.ryverInfo)
      self.forum_build = self.createForumDict(self.ryverInfo)
      Builder._builtUsers = self.user_build
      Builder._builtForum = self.forum_build


  def createUserDict(self, info):
      Builder.CurrentUser = info['d']['me']['username']
      Builder.myJid = info['d']['me']['jid']
      self.users = {}
      self.templist = info['d']['users']
      for i in self.templist:
          self._username = i['descriptor']
          self.users[self._username] = ['user', i['jid'], i['id']]

      return self.users


  def createForumDict(self, info):
      self.forums = {}
      self.frmlist = info['d']['forums']
      for i in self.frmlist:
          self.description = i['descriptor']
          self.forums[self.description] = ['forum', i['jid'], i['id']]
      self.wkgplist = info['d']['teams']
      for i in self.wkgplist:
          self.description = i['descriptor']
          self.forums[self.description] = ['wkgp', i['jid'], i['id']]
      return self.forums

  def changeRoom(self, identifier, width):
      Builder.CurrentMessages = []
      Builder.CurrentUsers = {}
      Builder.CurrentChat = identifier
      self._id = Builder._builtForum[identifier][2]
      self._width = width
      if Builder._builtForum[identifier][0] == 'forum':
        self._frmchatHistory(type='forum')
      elif Builder._builtForum[identifier][0] == 'wkgp':
        self._frmchatHistory(type='wkgp')

  def changeDm(self, identifier, width):
      Builder.CurrentMessages = []
      Builder.CurrentUsers = {}
      Builder.CurrentChat = identifier
      self._id = Builder._builtUsers[identifier][2]
      self._width = width
      self._frmchatHistory(type='user')

  def _frmchatHistory(self, type):
      self._type = type
      if self._type == 'forum':
        self._chatHistory = requests.get('https://'+self.org+'.ryver.com/api/1/odata.svc/forums('
                                        +str(self._id)+')/Chat.History()?%24format=json&%24top=25&%24orderby=when'
                                                      '%20desc&%24inlinecount=allpages',
                                        auth=(self.username, self.password))
      elif self._type == 'wkgp':
          self._chatHistory = requests.get('https://' + self.org + '.ryver.com/api/1/odata.svc/workrooms('
                                           + str(self._id) + ')/Chat.History()?%24format=json&%24top=25&%24orderby=when'
                                                             '%20desc&%24inlinecount=allpages',
                                           auth=(self.username, self.password))
      elif self._type == 'user':
          self._chatHistory = requests.get('https://' + self.org + '.ryver.com/api/1/odata.svc/users('
                                           + str(self._id) + ')/Chat.History()?%24format=json&%24top=25&%24orderby=when'
                                                             '%20desc&%24inlinecount=allpages',
                                           auth=(self.username, self.password))
      self._chatInfo = self._chatHistory.json()
      self.temp = self._chatInfo['d']['results']
      for i in range(len(self.temp)-1, -1, -1):
          self._postTime = self.temp[i]['when']
          self._postTime = self._postTime.split('.', 1)[0]
          self._postTime = self._postTime.split('T', 1)[1]
          self._poster = self.temp[i]['from']['__descriptor']
          self._postMessage = self.temp[i]['body']
          self._originalMessage = '['+self._postTime+'] '+self._poster+': '+self._postMessage
          self._slicedMsg = self._chatSlicer(self._originalMessage, self._width)
          for x in self._slicedMsg:
              Builder.CurrentMessages.append(x)
      if self._type == 'forum' or self._type == 'wkgp':
          self._frmcurrentChatUsers()


  def _frmcurrentChatUsers(self):
      self._userList = requests.get('https://'+self.org+'.ryver.com/api/1/odata.svc/forums('
                                    +str(self._id)+')/members', auth=(self.username, self.password))
      self._userInfo = self._userList.json()
      self.temp = self._userInfo['d']['results']
      for i in range(0, len(self.temp)):
         for usernames in Builder._builtUsers.keys():
             if self.temp[i]['extras']['displayName'] == usernames:
                 Builder.CurrentUsers[usernames] = Builder._builtUsers[usernames]

  def _topicListPuller(self, identifier):
      Builder._builtTopics = {}
      self._id = Builder._builtForum[identifier][2]
      if Builder._builtForum[identifier][0] == 'forum':
        self._topicLists(type='forum')
      elif Builder._builtForum[identifier][0] == 'wkgp':
        self._topicLists(type='wkgp')

  def _topicLists(self, type):
      self._type = type
      if self._type == 'forum':
          self._topics = requests.get('https://'+self.org+'.ryver.com/api/1/odata.svc/forums('+str(self._id)+')/Post.Stream()'
                                      '?%24format=json&%24top=10&%24orderby=modifyDate&%24inlinecount=allpages',
                                      auth=(self.username, self.password))
      elif self._type == 'wkgp':
          self._topics = requests.get('https://' + self.org + '.ryver.com/api/1/odata.svc/workrooms('+str(self._id)+')/Post.Stream()'
                                      '?%24format=json&%24top=10&%24orderby=modifyDate&%24inlinecount=allpages',
                                      auth=(self.username, self.password))
      self._topicInfo = self._topics.json()
      logging.debug(self._topicInfo)
      self._topicInfo = self._topicInfo['d']['results']
      for i in range(len(self._topicInfo) -1, -1, -1):
          self._title = self._topicInfo[i]['subject']
          self._topicId = self._topicInfo[i]['id']
          Builder._builtTopics[self._title] = self._topicId

  def _createTopic(self, channel, subject, body):
      if Builder._builtForum[channel][0] == 'forum':
          self._inType = 'Entity.Forum'
      elif Builder._builtForum[channel][0] == 'wkgp':
          self._inType = 'Entity.Workroom'
      self._channelId = Builder._builtForum[channel][2]
      self.headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
      self._payload = {
          "subject": subject,
          "body": body,
          "outAssociations": {
              "results": [
                  {
                      "inId": self._channelId,
                      "inType": self._inType,
                      "inSecured": True,
                      "inName": channel
                  }
              ]
          },
          "recordType": "note"
      }
      self._createRequests = requests.post('https://'+self.org+'.ryver.com/api/1/odata.svc/posts',
                                           auth=HTTPBasicAuth(self.username, self.password), data=json.dumps(self._payload),
                                           headers=self.headers)
      return self._createRequests


  def _chatSlicer(self, msg, width):
      self._sliced = []
      self._width = width
      self._originMsg = msg
      self._workedMsg = msg
      while len(self._workedMsg) > self._width:
          sectionOne = self._workedMsg[:self._width]
          sectionTwo = self._workedMsg[self._width:]
          #logging.debug(sectionOne)
          try:
              sectionOne = sectionOne.rsplit(' ', 1)
              logging.debug(sectionOne)
              sectionTwo = sectionOne[1] + sectionTwo
              sectionOne.pop()
              self._sliced.append(sectionOne[0])
              self._workedMsg = sectionTwo
          except IndexError:
              logging.debug(
                  "No white space found, appending entire line. This usually occurs when someone pastes an image.")
              # Append it anyways
              self._sliced.append(self._originMsg)
              return self._sliced
              #break
      self._sliced.append(self._workedMsg)
      return self._sliced




