import json
import re


class Expandable(object):

    SEARCH_PAT = re.compile("(<[^<>]+>)")

    def __init__(self, text):
        self.text = text

    def expand(self):
        utterances = []
        queue = [self.text]
        while len(queue) > 0:
            utterance = queue.pop()
            match = self.SEARCH_PAT.search(utterance)
            if match is None:
                utterances.append(utterance)
            else:
                alt_group = match.groups()[0]
                alternates = alt_group.strip('<>').split('|')
                for alternate in alternates:
                    queue.append(utterance.replace(alt_group, alternate, 1))
        return {u.strip() for u in utterances}


class LanguageModelIntentSlot(object):

    def __init__(self, name, slot_type, samples=None):
        self.name = name
        self.type = slot_type
        self.samples = samples if samples else []

    def to_json(self):
        o = {"name": self.name,
             "type": self.type}
        if self.samples:
            samples = set()
            for sample in self.samples:
                if isinstance(sample, Expandable):
                    samples = samples.union(sample.expand())
                else:
                    samples.add(sample)
            o["samples"] = list(samples)
        return o


class LanguageModelIntent(object):

    def __init__(self, name):
        self.name = name
        self.samples = []
        self.slots = {}

    def add_slot(self, name, slot_type):
        slot = LanguageModelIntentSlot(name=name, slot_type=slot_type)
        self.slots[name] = slot
        return slot

    def to_json(self):
        o = {"name": self.name}
        if self.samples:
            samples = set()
            for sample in self.samples:
                if isinstance(sample, Expandable):
                    samples = samples.union(sample.expand())
                else:
                    samples.add(sample)
            o["samples"] = list(samples)
        if self.slots:
            o["slots"] = [slot.to_json() for slot in self.slots.values()]
        return o


class LanguageModelSlotTypeValue(object):

    def __init__(self, value, id=None, synonyms=None):
        self.value = value
        self.id = id
        self.synonyms = synonyms

    def to_json(self):
        o = {"id": self.id, "name": {"value": self.value}}
        if self.synonyms:
            o["name"]["synonyms"] = self.synonyms
        return o


class LanguageModelSlotType(object):

    def __init__(self, name):
        self.name = name
        self.values = []

    def add_value(self, value):
        v = LanguageModelSlotTypeValue(value=value)
        self.values.append(v)
        return v

    def add_values(self, values):
        self.values.extend([LanguageModelSlotTypeValue(v) for v in values])

    def to_json(self):
        return {"name": self.name, "values": [v.to_json() for v in self.values]}


class LanguageModel(object):

    def __init__(self, invocation_name):
        self.invocationName = invocation_name
        self.types = {}
        self.intents = {}

    def add_intent(self, name):
        intent = LanguageModelIntent(name=name)
        self.intents[name] = intent
        return intent

    def add_slot_type(self, name):
        slot_type = LanguageModelSlotType(name=name)
        self.types[name] = slot_type
        return slot_type

    def to_json(self):
        o = {"invocationName": self.invocationName}
        if self.intents:
            o["intents"] = [i.to_json() for i in self.intents.values()]
        if self.types:
            o["types"] = [t.to_json() for t in self.types.values()]
        return o


class PromptVariation(object):

    PLAIN = "PlainText"
    SSML = "SSML"
    AUTO = None

    def __init__(self, value, text_type=None):
        self.value = value
        if text_type == None:
            if '<' in value:
                self.type = PromptVariation.SSML
            else:
                self.type = PromptVariation.PLAIN
        else:
            self.type = text_type

    def to_json(self):
        return {"type": self.type,
                "value": self.value}


class Prompt(object):

    def __init__(self, id_string):
        self.id = id_string
        self.variations = []

    def add_variation(self, value, text_type=PromptVariation.AUTO):
        self.variations.append(PromptVariation(value=value, text_type=text_type))

    def to_json(self):
        if not self.variations:
            raise ValueError("At least one utterance must be provided for each Prompt.")
        return {"id": self.id,
                "variations": [v.to_json() for v in self.variations]}


class DialogIntentSlot(object):

    ELICIT = "elicit"
    CONFIRMATION = "confirmation"

    def __init__(self, name, slot_type, elicitation_required=True, confirmation_required=False):
        self.name = name
        self.type = slot_type
        self.elicitationRequired = elicitation_required
        self.confirmationRequired = confirmation_required
        self.prompts = {}

    def add_prompt(self, prompt_id, prompt_type="elicit"):
        self.prompts[prompt_type] = prompt_id

    def to_json(self):
        if self.confirmationRequired and "confirmation" not in self.prompts:
            raise ValueError("Dialog Slot Requires Confirmation but has No Confirmation Prompt.")
        if self.elicitationRequired and "elicit" not in self.prompts:
            raise ValueError("Dialog Slot Requires Elicitation but has not Elicitation Prompt.")
        return {"name": self.name,
                "type": self.type,
                "elicitationRequired": self.elicitationRequired,
                "confirmationRequired": self.confirmationRequired,
                "prompts": self.prompts}


class DialogIntent(object):

    def __init__(self, name, confirmation_required=False):
        self.name = name
        self.confirmationRequired = confirmation_required
        self.prompts = {}
        self.slots = {}

    def add_slot(self, name, slot_type, elicitation_required=True, confirmation_required=False):
        slot = DialogIntentSlot(name=name,
                                slot_type=slot_type,
                                elicitation_required=elicitation_required,
                                confirmation_required=confirmation_required)
        self.slots[name] = slot
        return slot

    def add_prompt(self, prompt_id):
        self.prompts["confirmation"] = prompt_id

    def to_json(self):
        if self.confirmationRequired and "confirmation" not in self.prompts:
            raise ValueError("Dialog Intent Requires Confirmation but has No Confirmation Prompt.")
        return {"name": self.name,
                "confirmationRequired": self.confirmationRequired,
                "prompts": self.prompts,
                "slots": [s.to_json() for s in self.slots.values()]}


class Dialog(object):

    def __init__(self):
        self.intents = {}

    def add_intent(self, name, confirmation_required=False):
        i = DialogIntent(name=name, confirmation_required=confirmation_required)
        self.intents[name] = i
        return i

    def to_json(self):
        return [i.to_json() for i in self.intents.values()]


class InteractionModel(object):

    def __init__(self):
        self.languageModel = None
        self.dialog = None
        self.prompts = {}

    def add_language_model(self, invocation_name):
        self.languageModel = LanguageModel(invocation_name=invocation_name)
        return self.languageModel

    def add_prompt(self, id_string):
        p = Prompt(id_string=id_string)
        self.prompts[id_string] = p
        return p

    def add_dialog_intent(self, name, confirmation_required=False):
        if not self.dialog:
            self.dialog = Dialog()
        return self.dialog.add_intent(name=name, confirmation_required=confirmation_required)

    def to_json(self):
        o = {}
        if self.languageModel:
            o["languageModel"] = self.languageModel.to_json()
        if self.prompts:
            o["prompts"] = [p.to_json() for p in self.prompts.values()]
        if self.dialog:
            o["dialog"] = self.dialog.to_json()
        return {"interactionModel": o}

    def save(self, filename):
        with open(filename, 'wt') as modelfile:
            json.dump(self.to_json(), modelfile, indent=2)
