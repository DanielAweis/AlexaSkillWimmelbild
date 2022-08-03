import time

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
    template_apl = load_apl_document("statistik_apl.json")
    data_apl = load_apl_document("data_statistik_apl.json")
    
    
    data_apl["statData"]["sources"][0]["correctCountAlexa"] = 42
    # data_apl["statData"]["sources"][0]["correctCountUser"] = ANZAHL_OBJEKTE
    # data_apl["statData"]["sources"][0]["AvTimeAlexa"] = ZEIT_ALEXA
    # data_apl["statData"]["sources"][0]["AvTimeUser"] = ZEIT_USER
    
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # Identify chosen modus.
        attributes_manager = handler_input.attributes_manager
        mood = attributes_manager.persistent_attributes["mood"]
        
        ### STATISTICS ###
        statistics = attributes_manager.persistent_attributes["statistics"]
        
        # USER
        user_correct_obj = statistics["user"]["correct_obj"]
        user_time = statistics["user"]["duration_in_sec"]
        user_minutes, user_seconds = divmod(user_time, 60)
        
        # ALEXA
        alexa_correct_obj = statistics["alexa"]["correct_obj"]
        alexa_time = statistics["alexa"]["duration_in_sec"]
        alexa_minutes, alexa_seconds = divmod(alexa_time, 60)
        ##################
        
        # TODO: durchschnittliche zeit berechnen
        # TODO: Mehr Äusserungen mit f string in json 
        # TODO: einbauen der Werte in den Bye-Screen
        speak_output = choose_utterance(mood, "bye") + f" Insgesamt hast du {user_correct_obj} Objekte richtig erraten und hast {user_minutes:0.0f} Minuten und {user_seconds:0.0f} Sekunden gebraucht. Und ich habe {alexa_correct_obj} richtig erraten und habe {alexa_minutes:0.0f} Minuten und {alexa_seconds:0.0f} Sekunden gebraucht."

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