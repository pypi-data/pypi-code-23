class Message:
    
    def __init__(self, id: str, recipients: List[str], sender: str, size: str, subject: str, type: str, source: str, created_at: str):
        """create Message object.

        Arguments:
            id {str}               -- message ID.
            recipients {List[str]} -- List of recipients.
            sender {str}           -- sender like "<user@example.com>"
            size {str}             -- message sourse size
            subject {str}          -- message subject.
            type {str}             -- text type like text/plain, text/html
            source {str}           -- message row sourse.
            created_at {str}       -- the time when this message recieved.
        """
        self.id         = id
        self.recipients = recipients
        self.sender     = sender
        self.size       = size
        self.subject    = subject
        self.type       = type
        self.source     = source
        self.created_at = created_at
