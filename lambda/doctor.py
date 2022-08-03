import ask_sdk_core.utils as ask_utils
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import get_supported_interfaces

# APL
from ask_sdk_model.interfaces.alexa.presentation.apl import RenderDocumentDirective

# Helper functions
from utils import load_apl_document, create_presigned_url
from utterances import choose_utterance, UTTERANCES

class DoktorIntentHandler(AbstractRequestHandler):
    """Handler for Doktor Intent."""
    
    # DW: object name
    object_name = "doctor"
    global object_german
    object_german = "die Doktorin"
    
    # Documents for rendering visual response
    template_apl = load_apl_document("jsondata/main_apl_template.json")
    data_apl = load_apl_document("jsondata/data_apl_template.json")
    images = load_apl_document("images.json")
    
    data_apl["templateData"]["properties"]["backgroundImage"]["sources"][0]["url"] = images[object_name]["image"]
    
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("DoktorIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        
        # Identify chosen mood.
        attributes_manager = handler_input.attributes_manager
        mood = attributes_manager.persistent_attributes["mood"]
        
        ######## DW: TODO for all objects:
        # copy and paste this and change the object name above
        # and delete old speak_output statement 
        already_mentioned = attributes_manager.persistent_attributes["already_mentioned"]
        wrong_counter = attributes_manager.persistent_attributes["wrong_counter"]
        
        # if object_name not in already_mentioned
        if self.object_name not in already_mentioned:
            # update bee into already_mentioned in persistent attributes
            already_mentioned.append(self.object_name)
            
            speak_output = choose_utterance(mood, self.object_name)
        
        # if object was already_mentioned 
        else:
            wrong_counter += 1
            # check wrong_counter
            if wrong_counter <= 3:
                speak_output = choose_utterance(mood, "already_mentioned").format(object_german)
            else:
                wrong_counter = 0
                already_mentioned.clear()
                speak_output = choose_utterance(mood, "no_stop")
                
        # get statistics
        statistics = attributes_manager.persistent_attributes["statistics"]
               
        # update persistent memory with new wrong_counter and already_mentioned
        attributes = {
            "mood": mood, 
            "wrong_counter": wrong_counter, 
            "already_mentioned": already_mentioned,
            "statistics": statistics
        }
        attributes_manager.persistent_attributes.update(attributes)
        attributes_manager.save_persistent_attributes()
        ######## end copy and paste

        response_builder = handler_input.response_builder
        
        if get_supported_interfaces(
                handler_input).alexa_presentation_apl is not None:
            response_builder.add_directive(
                RenderDocumentDirective(
                    token="doctorToken",
                    document = self.template_apl,
                    datasources = self.data_apl
                ))
        
        return response_builder.speak(speak_output).response