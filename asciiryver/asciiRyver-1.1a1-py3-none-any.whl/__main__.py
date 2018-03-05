from asciimatics.screen import Screen
from asciimatics.widgets import Text, TextBox, Divider, Widget, Frame, Layout, Label, MultiColumnListBox, Button, PopUpDialog
from asciimatics.scene import Scene
from asciimatics.exceptions import ResizeScreenError, NextScene, StopApplication
from asciiRyver.framework import Builder
from asciiRyver.client import Client
import sys
import logging
import requests
import threading
import time

class Model(object):
    def __init__(self):
        self.running = object
        self.activeClient = object
        self._signal = threading.Event()
        self._messageQueue = []

class NewTopic(Frame):
    def __init__(self, screen, builder, model, colors):
        super(NewTopic, self).__init__(screen,
                                       screen.height * 2 // 3,
                                       screen.width * 2 // 3,
                                       title="New Topic")
        self.palette = colors
        self.model = model
        self._builder = builder
        self.layout = Layout([100], fill_frame=True)
        self.add_layout(self.layout)
        self.layout.add_widget(Text("Channel:", 'channel'))
        self.layout.add_widget(Text("Subject:", 'subject'))
        self.layout.add_widget(Text("Body:", 'body'))
        self.button_bar = Layout([1, 1, 1, 1])
        self.add_layout(self.button_bar)
        self.button_bar.add_widget(Button("OK", on_click=self._ok), 1)
        self.button_bar.add_widget(Button("Cancel", on_click=self._cancel), 2)
        self.fix()

    def _ok(self):
        self.save()
        self._topicCreate = self.model.running._createTopic(self.data['channel'],
                                                            self.data['subject'],
                                                            self.data['body'])
        logging.debug(self._topicCreate)
        if self._topicCreate.status_code == 201:
            raise NextScene("TopicPanel")
        else:
            self._scene.add_effect(PopUpDialog(self.screen, "Topic Creation Failed!", "X", on_close=None))

    def _cancel(self):
        raise NextScene('TopicPanel')

class TopicPanel(Frame):
    def __init__(self, screen, builder, model, colors):
        super(TopicPanel, self).__init__(screen,
                                         screen.height * 2 // 3,
                                         screen.width * 2 // 3,
                                         on_load=self.reload,
                                         title="Topics")
        self.palette = colors
        self.model = model
        self._builder = builder
        self.layout = Layout([45, 5, 45], fill_frame=True)
        self.add_layout(self.layout)
        self._Channels = [([x], i) for i, x in enumerate(self._builder._builtForum.keys())]
        self._Channelslist = MultiColumnListBox(Widget.FILL_FRAME, [0], self._Channels, on_select=self._retrieveTopics)
        self.layout.add_widget(self._Channelslist, 0)
        #self.layout.add_widget(VertDivider(), 1)
        self._Topics = [([x], i) for i, x in enumerate(self._builder._builtTopics.keys())]
        self._TopicsList = MultiColumnListBox(Widget.FILL_FRAME, [0], self._Topics, on_select=self._joinTopic)
        self.layout.add_widget(self._TopicsList, 2)
        self.divideBox = Layout([100])
        self.add_layout(self.divideBox)
        self.divideBox.add_widget(Divider())
        self.buttonBox = Layout([50, 50])
        self.add_layout(self.buttonBox)
        self.buttonBox.add_widget(Button('Create New', on_click=self._newTopic), 0)
        self.buttonBox.add_widget(Button('Back', on_click=self._goBack), 1)
        self.fix()

    def _goBack(self):
        raise NextScene('Main')

    def _newTopic(self):
        raise NextScene('NewTopic')

    def _joinTopic(self):
        self._topicName = self._TopicsList.options[self._TopicsList.value][0][0]
        self._builder.CurrentChat = self._topicName
        self._builder.CurrentMessages = []
        raise NextScene("Main")

    def _retrieveTopics(self):
        self._channel = self._Channelslist.options[self._Channelslist.value][0][0]
        logging.debug("Fetching topics for "+self._channel)
        self.model.running._topicListPuller(self._channel)
        self.reload()


    def reload(self):
        self._Channelslist.options = [([x], i) for i, x in enumerate(self._builder._builtForum.keys())]
        self._TopicsList.options = [([x], i) for i, x in enumerate(self._builder._builtTopics.keys())]



class LoginView(Frame):

    def __init__(self, screen, builder, model, client, colors):
        super(LoginView, self).__init__(screen,
                                        screen.height * 2 // 3,
                                        screen.width * 2 // 3,
                                        title="Login")
        self.palette = colors
        self.model = model
        self._builder = builder
        self._client = client
        self.layout = Layout([100], fill_frame=True)
        self.add_layout(self.layout)
        self.layout.add_widget(Text("Email:", "email"))
        self.layout.add_widget(Text("Password:", "password", hide_char='*'))
        self.layout.add_widget(Text("Ryver Organization:", "organization"))
        self.button_bar = Layout([1, 1, 1, 1])
        self.add_layout(self.button_bar)
        self.button_bar.add_widget(Button("OK", on_click=self._ok), 0)
        self.button_bar.add_widget(Button("Cancel", on_click=self._cancel), 3)
        self.fix()

    def _ok(self):
        self.save()
        self.loginRequest = requests.post('https://'+self.data['organization']+'.ryver.com/api/1/odata.svc/User.Login()',
                                          auth=(self.data['email'], self.data['password']))
        if self.loginRequest.status_code == 200:
            # Success
            self.response = self.loginRequest.json()
            self.payload = {'email': self.data['email'], 'password': self.data['password'],
                       'org': self.data['organization'], 'data': self.response}
            self._builder(self.payload)
            self.model.running = self._builder(self.payload)
            self.newClient = self._client(self.payload, self.model)
            self.newClient.run(self.payload)
            self.model.activeClient = self.newClient
            raise NextScene("Main")
        else:
            self._scene.add_effect(PopUpDialog(self.screen, "Login Failed!", "X", on_close=None))

    def _cancel(self):
        raise NextScene("Main")


class myTest(Frame):

    def __init__(self, screen, builder, model, colors):
        super(myTest, self).__init__(screen,
                                     int(screen.height * 3 // 3),
                                     int(screen.width * 3 // 3),
                                     on_load=self.reload,
                                     title='asciiRyver')


        self.palette = colors
        self._model = model
        self._screen = screen
        self._builder = builder
        # Header
        self.layout = Layout([1, 1, 1, 1, 1, 1])
        self.add_layout(self.layout)
        # Current User
        self._currentUser = Label(self._builder.CurrentUser)
        self.layout.add_widget(self._currentUser, 0)
        # Current Chat
        self._currentChat = Label(self._builder.CurrentChat)
        self.layout.add_widget(self._currentChat, 1)
        # Buttons
        self.layout.add_widget(Button('Topics', on_click=self._topic), 3)
        self.layout.add_widget(Button('Login', on_click=self._login), 4)
        self.layout.add_widget(Button('Exit', on_click=self._exit), 5)

        # Top Divider
        self.divideBox1 = Layout([100])
        self.add_layout(self.divideBox1)
        self.divideBox1.add_widget(Divider())

        # Main Chat Section
        self.mainBody = Layout([12, 2, 72, 2, 12], fill_frame=True)
        self.add_layout(self.mainBody)
        # Forum Column
        self._Forums = [([x], i) for i, x in enumerate(self._builder._builtForum.keys())]
        self._Forumslist = MultiColumnListBox(Widget.FILL_FRAME, [0], self._Forums, on_select=self._changeRoom)
        self.mainBody.add_widget(self._Forumslist, 0)
        # Testing Vert Divider
        #self.mainBody.add_widget(VertDivider(), 1)
        # Messages Column
        self._Messages = [([x], i) for i, x in enumerate(self._builder.CurrentMessages)]
        self._Messageslist = MultiColumnListBox(Widget.FILL_FRAME, [0], self._Messages)
        self.mainBody.add_widget(self._Messageslist, 2)
        # Testing Vert Divider
        #self.mainBody.add_widget(VertDivider(), 3)
        # Users Column
        self._Users = [([x], i) for i, x in enumerate(self._builder._builtUsers.keys())]
        self._Userslist = MultiColumnListBox(Widget.FILL_FRAME, [0], self._Users, on_select=self._changeUser)
        self.mainBody.add_widget(self._Userslist, 4)

        # Bottom Divider
        self.divideBox2 = Layout([100])
        self.add_layout(self.divideBox2)
        self.divideBox2.add_widget(Divider())

        # User Send Box
        self.sendBox = Layout([93, 7])
        self.add_layout(self.sendBox)
        self._MsgBox = TextBox(1, label='> ', name='userMsg')
        self.sendBox.add_widget(self._MsgBox, 0)
        self.sendBox.add_widget(Button('Send', on_click=self._sendMsg), 1)
        self.fix()

    def _login(self):
        raise NextScene("LoginForm")

    def _topic(self):
        raise NextScene("TopicPanel")

    def _sendMsg(self):
        self.save()
        self.to = self._builder.CurrentChat
        # Check if we are in a topic
        if self.to in self._builder._builtTopics.keys():
            self._id = self._builder._builtTopics[self.to]
            self._model.activeClient._send_topic(self._id, self.data['userMsg'][0])
        # Check if we are in a forum/workgroup
        elif self.to in self._builder._builtForum.keys():
            self.toJid = self._builder._builtForum[self.to][1]
            self._model.activeClient._on_send(self.toJid, self.data['userMsg'][0])
        # Check if we are DM'ing
        elif self.to in self._builder._builtUsers.keys():
            self.toJid = self._builder._builtUsers[self.to][1]
            self._model.activeClient._on_send(self.toJid, self.data['userMsg'][0])
        self._MsgBox.value = None
        self._MsgBox.focus()


    def _changeRoom(self):
        self._newRoom = self._Forumslist.options[self._Forumslist.value][0][0]
        logging.debug("Changing rooms to: "+self._newRoom)
        self._textBoxWidth = self._Messageslist._get_width(0)
        self._model.running.changeRoom(self._newRoom, self._textBoxWidth)
        self._Messageslist.options = [([x], i) for i, x in enumerate(self._builder.CurrentMessages)]
        self._Userslist.options = [([x], i) for i, x in enumerate(self._builder.CurrentUsers)]
        self._currentChat.text = self._builder.CurrentChat

    def _changeUser(self):
        self._newUser = self._Userslist.options[self._Userslist.value][0][0]
        self._textBoxWidth = self._Messageslist._get_width(0)
        self._model.running.changeDm(self._newUser, self._textBoxWidth)
        self._Messageslist.options = [([x], i) for i, x in enumerate(self._builder.CurrentMessages)]
        self._currentChat.text = self._builder.CurrentChat

    def _chatFeeder(self):
        while True:
            time.sleep(0.1)
            self._model._signal.wait()
            for i in self._model._messageQueue:
                self._textBoxWidth = self._Messageslist._get_width(0)
                self._sliced = self._model.running._chatSlicer(i, self._textBoxWidth)
                for i in self._sliced:
                    self._num = len(self._Messageslist.options)
                    self._Messageslist.options.append(([i], self._num))
                    self._Messageslist.start_line = len(self._Messageslist.options)
                    self._Messageslist._line = len(self._Messageslist.options) - 1
                    self._screen.force_update()
                try:
                    self._model._messageQueue.pop()
                except IndexError:
                    #logging.debug(self._model._messageQueue)
                    pass
            self._model._signal.clear()


    def reload(self):
        self._Forumslist.options = [([x], i) for i, x in enumerate(self._builder._builtForum.keys())]
        self._Userslist.options = [([x], i) for i, x in enumerate(self._builder.CurrentUsers.keys())]
        self._Messageslist.options = [([x], i) for i, x in enumerate(self._builder.CurrentMessages)]
        self._currentUser.text = self._builder.CurrentUser
        self._currentChat.text = self._builder.CurrentChat
        self.t1 = threading.Thread(target=self._chatFeeder)
        self.t1.daemon = True
        self.t1.start()

    @staticmethod
    def _exit():
        raise StopApplication('User requested to quit.')


def run(screen, scene):
    colorScheme = {
            'borders': (Screen.COLOUR_BLACK, Screen.A_NORMAL, Screen.COLOUR_WHITE),
            'background': (Screen.COLOUR_BLACK, Screen.A_NORMAL, Screen.COLOUR_WHITE),
            'label': (Screen.COLOUR_BLACK, Screen.A_NORMAL, Screen.COLOUR_WHITE),
            'button': (Screen.COLOUR_BLACK, Screen.A_NORMAL, Screen.COLOUR_WHITE),
            'focus_button': (Screen.COLOUR_WHITE, Screen.A_NORMAL, Screen.COLOUR_BLACK),
            'field': (Screen.COLOUR_BLACK, Screen.A_NORMAL, Screen.COLOUR_WHITE),
            'focus_field': (Screen.COLOUR_BLACK, Screen.A_NORMAL, Screen.COLOUR_WHITE),
            'edit_text': (Screen.COLOUR_BLACK, Screen.A_NORMAL, Screen.COLOUR_WHITE),
            'title': (Screen.COLOUR_BLACK, Screen.A_NORMAL, Screen.COLOUR_WHITE),
            'focus_edit_text': (Screen.COLOUR_BLACK, Screen.A_NORMAL, Screen.COLOUR_WHITE),
            'selected_focus_field': (Screen.COLOUR_WHITE, Screen.A_NORMAL, Screen.COLOUR_BLACK),
            'scroll': (Screen.COLOUR_BLACK, Screen.A_NORMAL, Screen.COLOUR_WHITE),
            'control': (Screen.COLOUR_BLACK, Screen.A_NORMAL, Screen.COLOUR_WHITE),
            'disabled': (Screen.COLOUR_BLACK, Screen.A_NORMAL, Screen.COLOUR_WHITE),
            'selected_control': (Screen.COLOUR_BLACK, Screen.A_NORMAL, Screen.COLOUR_WHITE),
            'selected_focus_control': (Screen.COLOUR_BLACK, Screen.A_NORMAL, Screen.COLOUR_WHITE),
            'focus_control': (Screen.COLOUR_BLACK, Screen.A_NORMAL, Screen.COLOUR_WHITE),
            'invalid': (Screen.COLOUR_BLACK, Screen.A_NORMAL, Screen.COLOUR_WHITE),
            'selected_field': (Screen.COLOUR_BLACK, Screen.A_NORMAL, Screen.COLOUR_WHITE),
            'shadow': (0, None, 0)
        }
    logging.basicConfig(filename='ascii.log', level=logging.DEBUG)
    scenes = [
        Scene([myTest(screen, Builder, runtimeData, colorScheme)], -1, name="Main"),
        Scene([LoginView(screen, Builder, runtimeData, client, colorScheme)], -1, name="LoginForm"),
        Scene([TopicPanel(screen, Builder, runtimeData, colorScheme)], -1, name="TopicPanel"),
        Scene([NewTopic(screen, Builder, runtimeData, colorScheme)], -1, name="NewTopic")
    ]

    screen.play(scenes, stop_on_resize=True, start_scene=scene)

def main():
    global runtimeData
    global client
    runtimeData = Model()
    client = Client
    last_scene = None
    while True:
        try:
            Screen.wrapper(run, arguments=[last_scene])
            sys.exit(0)
        except ResizeScreenError as e:
            last_scene = e.scene

if __name__ == '__main__':
    main()


