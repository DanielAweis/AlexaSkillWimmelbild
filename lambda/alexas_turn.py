# DW: this handels the Event after Alexa described an object

import ask_sdk_core.utils as ask_utils
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import get_supported_interfaces

# APL
from ask_sdk_model.interfaces.alexa.presentation.apl import (
    UserEvent, RenderDocumentDirective)

# Helper functions
from utils import load_apl_document, create_presigned_url
from utterances import choose_utterance, UTTERANCES

class AlexasTurnIntentHandler(AbstractRequestHandler):
    """Handler for AlexasTurn."""
    
    # Documents for rendering visual response
    template_apl = load_apl_document("jsondata/main_apl_template.json")
    data_apl = load_apl_document("jsondata/data_apl_template.json")
    images = load_apl_document("images.json")
    
    data_apl["templateData"]["properties"]["backgroundImage"]["sources"][0]["url"] = images["wimmelbild"]["image"]
    
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        # Check if a button was pressed
        request = handler_input.request_envelope.request
        if isinstance(request, UserEvent):
            # Check arguments for right values
            return len(request.arguments) > 0 and request.arguments[0] == "alexas_turn"
        return ask_utils.is_intent_name("AlexasTurnIntent")(handler_input)
        
    def handle(self, handler_input):
        request = handler_input.request_envelope.request
        # First case: button was pressed.
        if isinstance(request, UserEvent):
            alexas_turn = request.arguments[1]
        # Second case: Modus was uttered
        else:
            slots = handler_input.request_envelope.request.intent.slots
            alexas_turn = slots["alexas_turn"].resolutions.resolutions_per_authority[0].values[0].value.id
        
        # Identify chosen mood.
        attributes_manager = handler_input.attributes_manager
        mood = attributes_manager.persistent_attributes["mood"]
        already_mentioned = attributes_manager.persistent_attributes["already_mentioned"]
        wrong_counter = attributes_manager.persistent_attributes["wrong_counter"]
        
        # get actual described object
        act_object = attributes_manager.persistent_attributes["act_object"]
        
        # TODO: Die Äusserungen im json erweitern und hier wieder auswählen für mehr Varianz.
        if act_object == alexas_turn:
            speak_output = "Yay, du hast es richtig erraten. Jetzt bist du wieder dran. Beschreib mir ein neues Objekt auf dem Bild!"
        else: 
            speak_output = "Mhhh, das meinte ich nicht. Versuch es nochmal!"

        response_builder = handler_input.response_builder
        
        if get_supported_interfaces(
                handler_input).alexa_presentation_apl is not None:
            response_builder.add_directive(
                RenderDocumentDirective(
                    token="beeToken",
                    document = self.template_apl,
                    datasources = self.data_apl
                ))
        
        return response_builder.speak(speak_output).response