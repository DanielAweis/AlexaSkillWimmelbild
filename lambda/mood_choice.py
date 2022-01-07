import ask_sdk_core.utils as ask_utils
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import get_supported_interfaces

# APL
from ask_sdk_model.interfaces.alexa.presentation.apl import (
    UserEvent, RenderDocumentDirective)

# Helper functions
from utils import load_apl_document
from utterances import choose_utterance, UTTERANCES

class PersonalityIntentHandler(AbstractRequestHandler):
    """Handler for Personality Intent."""
    
    # Documents for rendering visual response
    template_doc = "data/template.json"
    wimmel_doc = "data/wimmelbild.json"
    
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        # Check if a button was pressed
        request = handler_input.request_envelope.request
        if isinstance(request, UserEvent):
            # Check arguments for right values
            return len(request.arguments) > 0 and request.arguments[0] == "mood"
        return ask_utils.is_intent_name("PersonalityIntent")(handler_input)
        
        
    def handle(self, handler_input):
        request = handler_input.request_envelope.request
        # First case: button was pressed.
        if isinstance(request, UserEvent):
            mood = request.arguments[1]
        # Second case: Modus was uttered
        else:
            slots = handler_input.request_envelope.request.intent.slots
            mood = slots["mood"].resolutions.resolutions_per_authority[0].values[0].value.id
        
        # Save mood to persistent memory 
        attributes_manager = handler_input.attributes_manager
        actual_mood = {"mood": mood} # seen key 
        attributes_manager.persistent_attributes.update(actual_mood)
        attributes_manager.save_persistent_attributes()
        
        speak_output = choose_utterance(mood, "start")
        
        response_builder = handler_input.response_builder
        
        if get_supported_interfaces(
                handler_input).alexa_presentation_apl is not None:
            response_builder.add_directive(
                RenderDocumentDirective(
                    token="WimmelbildToken",
                    document=load_apl_document(self.template_doc),
                    datasources=load_apl_document(self.wimmel_doc)
                ))
        
        return response_builder.speak(speak_output).response