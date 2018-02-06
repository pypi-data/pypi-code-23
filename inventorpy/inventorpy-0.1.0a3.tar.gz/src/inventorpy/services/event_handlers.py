from inventorpy.domain.ports import IssueViewBuilder
from inventorpy.domain import emails


class IssueAssignedHandler:
    def __init__(self, view_builder: IssueViewBuilder,
                 sender: emails.EmailSender):
        self.view_builder = view_builder
        self.sender = sender

    def handle(self, event):
        data = self.view_builder.fetch(event.issue_id)
        data.update(**event._asdict())
        request = emails.MailRequest(
            emails.IssueAssignedToMe,
            emails.default_from_addr,
            emails.EmailAddress(event.assigned_to),
        )
        self.sender.send(request, data)
