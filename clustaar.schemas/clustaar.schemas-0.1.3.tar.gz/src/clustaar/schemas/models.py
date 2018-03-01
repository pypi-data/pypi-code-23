"""Model classes"""


def model(name, attr_names):
    """Generate a new class with a constructor taking attr_names as parameters.

    Args:
        name (str): class name
        attr_names (str|list): attribute names
    """
    if isinstance(attr_names, str):
        attr_names = attr_names.split(" ")

    def constructor(self, **kwargs):
        for attr_name in attr_names:
            setattr(self, attr_name, kwargs.get(attr_name))

    return type(name, (object,), {
        "__init__": constructor
    })


# Bot actions
AskLocationAction = model("AskLocationAction", "message callback_action")
StepTarget = model("StepTarget", "step_id name")
StoryTarget = model("StoryTarget", "story_id name")
GoToAction = model("GoToAction", "target")
LegacyReplyToMessageAction = model("LegacyReplyToMessageAction", "message")
OpenURLAction = model("OpenURLAction", "url")
ShareAction = model("ShareAction", "")
SendImageAction = model("SendImageAction", "image_url")
SendTextAction = model("SendTextAction", "alternatives")
SendEmailAction = model("SendEmailAction", "content subject recipient")
WaitAction = model("WaitAction", "duration")
PauseBotAction = model("PauseBotAction", "")
CloseIntercomConversationAction = model("CloseIntercomConversationAction", "")
AssignIntercomConversationAction = model("AssignIntercomConversationAction", "")
SendQuickRepliesAction = model("SendQuickRepliesAction", "buttons message")
QuickReply = model("QuickReply", "title action")
Button = model("Button", "title action")
Card = model("Card", "title subtitle buttons image_url url")
SendCardsAction = model("SendCardsAction", "cards")
StoreSessionValueAction = model("StoreSessionValueAction", "key value")

# Webhook
Step = model("Step", "actions name id user_data")
Coordinates = model("Coordinates", "lat long")
Interlocutor = model("Interlocutor", "id location")
ConversationSession = model("ConversationSession", "values")
StepReached = model("StepReached", "step session interlocutor channel")
StepReachedResponse = model("StepReachedResponse", "actions session")
WebhookRequest = model("WebhookRequest", "event bot_id timestamp topic")
