import ask_sdk_core.utils as ask_utils
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import get_supported_interfaces

# APL
from ask_sdk_model.interfaces.alexa.presentation.apl import RenderDocumentDirective

# Helper functions
from utils import load_apl_document
from utterances import choose_utterance, UTTERANCES

class EUIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    
    # Documents for rendering visual response
    template_doc = "data/template.json"
    data = "data/bee.json"
    
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("EUIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        
        # Identify chosen modus.
        attributes_manager = handler_input.attributes_manager
        mood = attributes_manager.persistent_attributes["mood"]
        
        speak_output = choose_utterance(mood, "eu")

        response_builder = handler_input.response_builder
        
        if get_supported_interfaces(
                handler_input).alexa_presentation_apl is not None:
            response_builder.add_directive(
                RenderDocumentDirective(
                    token="EUToken",
                    document=load_apl_document(self.template_doc),
                    datasources=load_apl_document(self.data)
                ))
        
        return response_builder.speak(speak_output).response