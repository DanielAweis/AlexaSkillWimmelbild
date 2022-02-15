import ask_sdk_core.utils as ask_utils
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import get_supported_interfaces

# APL
from ask_sdk_model.interfaces.alexa.presentation.apl import RenderDocumentDirective

# Helper functions
from utils import load_apl_document, create_presigned_url
from utterances import choose_utterance, UTTERANCES


class YesIntentHandler(AbstractRequestHandler):
    """Handler for Yes Intent."""
    
    # Documents for rendering visual response
    template_apl = load_apl_document("jsondata/main_apl_template.json")
    data_apl = load_apl_document("jsondata/data_apl_template.json")
    images = load_apl_document("images.json")
    
    data_apl["templateData"]["properties"]["backgroundImage"]["sources"][0]["url"] = images["wimmelbild"]["image"]
    
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.YesIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        
        # Identify chosen modus.
        attributes_manager = handler_input.attributes_manager
        mood = attributes_manager.persistent_attributes["mood"]
        already_mentioned = attributes_manager.persistent_attributes["already_mentioned"]
        
        # reset wrong_counter and already_mentioned because new round
        # update persistent memory with new wrong_counter and already_mentioned
        already_mentioned.clear()
        attributes = {
            "mood": mood, 
            "wrong_counter": 0, 
            "already_mentioned": already_mentioned
            
        }
        attributes_manager.persistent_attributes.update(attributes)
        attributes_manager.save_persistent_attributes()
        
        # reset wrong proposal counter because new round
        speak_output = choose_utterance(mood, "yes")
        #auf neuen input warten
        response_builder = handler_input.response_builder
        
        if get_supported_interfaces(
                handler_input).alexa_presentation_apl is not None:
            response_builder.add_directive(
                RenderDocumentDirective(
                    token="WimmelbildToken",
                    document = self.template_apl,
                    datasources = self.data_apl
                ))
        
        return response_builder.speak(speak_output).response