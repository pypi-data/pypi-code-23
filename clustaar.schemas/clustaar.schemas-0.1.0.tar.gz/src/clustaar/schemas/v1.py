import re
from lupin import Schema, fields as f, validators as v, Mapper, bind
from .constants import *
from .models import *


#
# Targets
#
STEP_TARGET = Schema({
    "id": f.String(binding="step_id"),
    "type": f.Constant(value="step", read_only=True),
    "name": f.String(optional=True)
})

STORY_TARGET = Schema({
    "id": f.String(binding="story_id"),
    "type": f.Constant(value="story", read_only=True),
    "name": f.String(optional=True)
})

ACTIONS_BLOCK_TARGET = Schema({
    "id": f.String(binding="actions_block_id"),
    "type": f.Constant(value="actions_block", read_only=True),
    "name": f.String(optional=True)
})


#
# Button actions
#
GO_TO_ACTION = Schema({
    "type": f.Constant(value="go_to_action", read_only=True),
    "target": f.PolymorphicObject(on="type", schemas={
        "step": STEP_TARGET,
        "story": STORY_TARGET
    })
})

LEGACY_REPLY_TO_MESSAGE_ACTION = Schema({
    "type": f.Constant(value="legacy_reply_to_message_action", read_only=True),
    "message": f.String(validators=[v.Length(min=1, max=SEND_TEXT_ACTION_MESSAGE_MAX_LENGTH)])
})

OPEN_URL_ACTION = Schema({
    "type": f.Constant(value="open_url_action", read_only=True),
    "url": f.String(validators=[v.Length(min=1, max=EXTERNAL_URL_MAX_LENGTH),
                                v.URL()])
})

SHARE_ACTION = Schema({
    "type": f.Constant(value="share_action", read_only=True)
})

BUTTON_ACTIONS_SCHEMAS = {
    "go_to_action": GO_TO_ACTION,
    "legacy_reply_to_message_action": LEGACY_REPLY_TO_MESSAGE_ACTION,
    "open_url_action": OPEN_URL_ACTION,
    "share_action": SHARE_ACTION
}

#
# Bot actions
#
ASK_LOCATION_ACTION = Schema({
    "type": f.Constant(value="ask_location_action", read_only=True),
    "message": f.String(validators=[v.Length(min=1, max=SEND_TEXT_ACTION_MESSAGE_MAX_LENGTH)]),
    "action": f.Object(schema=GO_TO_ACTION, binding="callback_action")
})

SEND_IMAGE_ACTION = Schema({
    "type": f.Constant(value="send_image_action", read_only=True),
    "url": f.String(binding="image_url", validators=[
        v.Length(max=EXTERNAL_URL_MAX_LENGTH),
        v.URL(schemes={"https", "http"})
    ])
})

SEND_TEXT_ACTION = Schema({
    "type": f.Constant(value="send_text_action", read_only=True),
    "alternatives": f.List(f.String(validators=[v.Length(min=1, max=SEND_TEXT_ACTION_MESSAGE_MAX_LENGTH)]),
                           validators=[v.Length(min=1, max=SEND_TEXT_ACTION_MAX_MESSAGES_COUNT)])
})

SEND_EMAIL_ACTION = Schema({
    "type": f.Constant(value="send_email_action", read_only=True),
    "recipient": f.String(validators=[v.Length(max=SEND_EMAIL_ACTION_RECIPIENT_MAX_LENGTH)]),
    "subject": f.String(validators=[v.Length(max=SEND_EMAIL_ACTION_SUBJECT_MAX_LENGTH)]),
    "content": f.String(validators=[v.Length(max=SEND_EMAIL_ACTION_CONTENT_MAX_LENGTH)])
})

WAIT_ACTION = Schema({
    "type": f.Constant(value="wait_action", read_only=True),
    "duration": f.Number(validators=[v.Between(min=WAIT_ACTION_MIN_DURATION, max=WAIT_ACTION_MAX_DURATION)],
                         default=WAIT_ACTION_DEFAULT_DURATION)
})

PAUSE_BOT_ACTION = Schema({
    "type": f.Constant(value="pause_bot_action", read_only=True)
})

CLOSE_INTERCOM_CONVERSATION_ACTION = Schema({
    "type": f.Constant(value="close_intercom_conversation_action", read_only=True)
})

ASSIGN_INTERCOM_CONVERSATION_ACTION = Schema({
    "type": f.Constant(value="assign_intercom_conversation_action", read_only=True)
})

QUICK_REPLY = Schema({
    "title": f.String(validators=[v.Length(min=1, max=QUICK_REPLY_TITLE_MAX_LENGTH)]),
    "action": f.Object(GO_TO_ACTION),
    "type": f.Constant(value="quick_reply", read_only=True)
})

SEND_QUICK_REPLIES_ACTION = Schema({
    "type": f.Constant(value="send_quick_replies_action", read_only=True),
    "message": f.String(validators=[v.Length(min=1, max=SEND_TEXT_ACTION_MESSAGE_MAX_LENGTH)]),
    "buttons": f.List(f.Object(QUICK_REPLY),
                      validators=[v.Length(min=1, max=SEND_QUICK_REPLIES_ACTION_MAX_BUTTONS_COUNT)])
})

BUTTON = Schema({
    "type": f.Constant(value="button", read_only=True),
    "title": f.String(validators=[v.Length(min=1, max=BUTTON_TITLE_MAX_LENGTH)]),
    "action": f.PolymorphicObject(on="type", schemas=BUTTON_ACTIONS_SCHEMAS)
})

CARD = Schema({
    "type": f.Constant(value="card", read_only=True),
    "title": f.String(validators=[v.Length(min=1, max=CARD_TITLE_MAX_LENGTH)]),
    "subtitle": f.String(optional=True, validators=[v.Length(max=CARD_SUBTITLE_MAX_LENGTH)]),
    "imageURL": f.String(optional=True, binding="image_url", validators=[
        v.Length(max=EXTERNAL_URL_MAX_LENGTH),
        v.URL(schemes={"http", "https"})
    ]),
    "url": f.String(optional=True, validators=[
        v.Length(max=EXTERNAL_URL_MAX_LENGTH)
    ]),
    "buttons": f.List(f.Object(BUTTON),
                      optional=True,
                      validators=[v.Length(max=CARD_MAX_BUTTONS_COUNT)])
})

SEND_CARDS_ACTIONS = Schema({
    "type": f.Constant(value="send_cards_action", read_only=True),
    "cards": f.List(f.Object(CARD),
                    validators=[v.Length(min=1, max=SEND_CARDS_ACTION_MAX_CARDS_COUNT)])
})

STORE_SESSION_VALUE_ACTION = Schema({
    "type": f.Constant(value="store_session_value_action", read_only=True),
    "key": f.String(validators=[v.Length(min=1, max=STORE_SESSION_VALUE_ACTION_KEY_MAX_LENGTH),
                                v.Match(re.compile(r"^[\w\d_]+$"))]),
    "value": f.String(validators=[v.Length(min=1, max=STORE_SESSION_VALUE_ACTION_VALUE_MAX_LENGTH)])
})

ACTION_SCHEMAS = {
    "pause_bot_action": PAUSE_BOT_ACTION,
    "wait_action": WAIT_ACTION,
    "send_email_action": SEND_EMAIL_ACTION,
    "send_text_action": SEND_TEXT_ACTION,
    "send_image_action": SEND_IMAGE_ACTION,
    "close_intercom_conversation_action": CLOSE_INTERCOM_CONVERSATION_ACTION,
    "assign_intercom_conversation_action": ASSIGN_INTERCOM_CONVERSATION_ACTION,
    "send_cards_action": SEND_CARDS_ACTIONS,
    "send_quick_replies_action": SEND_QUICK_REPLIES_ACTION,
    "store_session_value_action": STORE_SESSION_VALUE_ACTION,
    "ask_location_action": ASK_LOCATION_ACTION
}

COORDINATES = Schema({
    "lat": f.Number(),
    "long": f.Number()
})

#
# Webhook
#

WEBHOOK_INTERLOCUTOR = Schema({
    "id": f.String(),
    "location": f.Object(COORDINATES)
})

WEBHOOK_CONVERSATION_SESSION = Schema({
    "values": f.Dict()
})

WEBHOOK_STEP = Schema({
    "id": f.String(),
    "name": f.String(),
    "userData": f.String(binding="user_data"),
    "actions": f.PolymorphicList(on="type", schemas=ACTION_SCHEMAS)
})

WEBHOOK_STEP_REACHED = Schema({
    "type": f.Constant("step_reached_event", read_only=True),
    "channel": f.String(),
    "interlocutor": f.Object(schema=WEBHOOK_INTERLOCUTOR),
    "session": f.Object(schema=WEBHOOK_CONVERSATION_SESSION),
    "step": f.Object(schema=WEBHOOK_STEP)
})

WEBHOOK_STEP_REACHED_RESPONSE = Schema({
    "actions": f.PolymorphicList(on="type", schemas=ACTION_SCHEMAS),
    "session": f.Object(schema=WEBHOOK_CONVERSATION_SESSION, optional=True),
})

WEBHOOK_REQUEST = Schema({
    "topic": f.String(),
    "botID": f.String(binding="bot_id"),
    "timestamp": f.Int(),
    "data": f.PolymorphicObject(binding="event", on="type", schemas={
        "step_reached_event": WEBHOOK_STEP_REACHED
    })
})


def get_mapper(factory=bind):
    """Load mapper v1

    Returns:
        Mapper
    """
    mapper = Mapper()
    mappings = {
        AskLocationAction: ASK_LOCATION_ACTION,
        StepTarget: STEP_TARGET,
        StoryTarget: STORY_TARGET,
        GoToAction: GO_TO_ACTION,
        LegacyReplyToMessageAction: LEGACY_REPLY_TO_MESSAGE_ACTION,
        OpenURLAction: OPEN_URL_ACTION,
        ShareAction: SHARE_ACTION,
        SendImageAction: SEND_IMAGE_ACTION,
        SendTextAction: SEND_TEXT_ACTION,
        SendEmailAction: SEND_EMAIL_ACTION,
        WaitAction: WAIT_ACTION,
        PauseBotAction: PAUSE_BOT_ACTION,
        CloseIntercomConversationAction: CLOSE_INTERCOM_CONVERSATION_ACTION,
        AssignIntercomConversationAction: ASSIGN_INTERCOM_CONVERSATION_ACTION,
        QuickReply: QUICK_REPLY,
        SendQuickRepliesAction: SEND_QUICK_REPLIES_ACTION,
        Button: BUTTON,
        Card: CARD,
        SendCardsAction: SEND_CARDS_ACTIONS,
        StoreSessionValueAction: STORE_SESSION_VALUE_ACTION,
        Step: WEBHOOK_STEP,
        Interlocutor: WEBHOOK_INTERLOCUTOR,
        ConversationSession: WEBHOOK_CONVERSATION_SESSION,
        StepReached: WEBHOOK_STEP_REACHED,
        WebhookRequest: WEBHOOK_REQUEST,
        Coordinates: COORDINATES,
        StepReachedResponse: WEBHOOK_STEP_REACHED_RESPONSE
    }

    for cls, schema in mappings.items():
        mapper.register(cls, schema, factory=factory)

    return mapper
