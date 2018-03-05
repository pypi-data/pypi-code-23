from slacker import Slacker

class SlackUtils:
    '''
    @param api_token: the Slack API Token
    '''
    def __init__(self, api_token):
        self.slack = Slacker(api_token)


    '''
    Sends a multi-line message to a given channel if the message is not blank.
    If only one line needs to be sent, it should be put in a list by itself.

    @param channel: the channel to send the message to (ex: #general)
    @param message: a list of message lines
    '''
    def send_slack_message(self, channel, message):
        msg = ""

        for line in message:
            msg += "{0}{1}".format(line, "\n")

        if msg != "":
            self.slack.chat.post_message(channel, msg)


    '''
    Uploads a file.

    @param file_path: the full path to the file to be uploaded
    @param channels: an optional list of channels to upload the file to, 
                     defaults to None (global upload)
    @return: information about the file that was uploaded in JSON format
    '''
    def upload_file(self, file_path, channels = None):
        uploaded_file = self.slack.files.upload(file_path, channels)
        return uploaded_file.body
