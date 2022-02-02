import ask_sdk_core.utils as ask_utils
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import get_supported_interfaces

# APL
from ask_sdk_model.interfaces.alexa.presentation.apl import RenderDocumentDirective

# Helper functions
from utils import load_apl_document, create_presigned_url
from utterances import choose_utterance, UTTERANCES


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    
    # Documents for rendering visual response
    template_apl = load_apl_document("jsondata/main_apl_template.json")
    data_apl = load_apl_document("jsondata/data_apl_template.json")
    images = load_apl_document("jsondata/images.json")
    
    #TODO: upload bye bye image 
    
    data_apl["templateData"]["properties"]["backgroundImage"]["sources"][0]["url"] = create_presigned_url(images["bye"]["image"]) 
    
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # Identify chosen modus.
        attributes_manager = handler_input.attributes_manager
        mood = attributes_manager.persistent_attributes["mood"]
        
        speak_output = choose_utterance(mood, "bye")

        response_builder = handler_input.response_builder
        response_builder.set_should_end_session(True)
        
        if get_supported_interfaces(
                handler_input).alexa_presentation_apl is not None:
            response_builder.add_directive(
                RenderDocumentDirective(
                    token="byeToken",
                    document = self.template_apl,
                    datasources = self.data_apl
                ))
        
        return response_builder.speak(speak_output).response