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
    
    def __init__(self):
        self.template_apl = load_apl_document("statistik_apl.json")
        self.data_apl = load_apl_document("data_statistik_apl.json")
    
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
        user_selected_obj = statistics["user"]["selected_obj"]
        user_av_time = user_time / user_selected_obj
        user_minutes, user_seconds = divmod(user_av_time, 60)
        
        
        # ALEXA
        alexa_correct_obj = statistics["alexa"]["correct_obj"]
        alexa_time = statistics["alexa"]["duration_in_sec"]
        alexa_selected_obj = statistics["alexa"]["selected_obj"]
        alexa_av_time = alexa_time / alexa_selected_obj
        alexa_minutes, alexa_seconds = divmod(alexa_av_time, 60)
        ##################
        
        # APL
        if mood == "good_mood":
            self.template_apl["mainTemplate"]["items"][0]["items"][0]["backgroundImageSource"] = "https://i.imgur.com/f7oEcLF.png"
        else:
            self.template_apl["mainTemplate"]["items"][0]["items"][0]["backgroundImageSource"] = "https://i.imgur.com/mD1KJMu.jpeg"
            
        self.data_apl["statData"]["sources"][0]["correctCountAlexa"] = alexa_correct_obj
        self.data_apl["statData"]["sources"][0]["correctCountUser"] = user_correct_obj
        self.data_apl["statData"]["sources"][0]["AvTimeAlexa"] = f"{alexa_minutes:0.0f}:{alexa_seconds:0.0f} min"
        self.data_apl["statData"]["sources"][0]["AvTimeUser"] = f"{user_minutes:0.0f}:{user_seconds:0.0f} min"
        
        # TODO: Mehr Äusserungen mit f string in json 
        speak_output = choose_utterance(mood, "bye") + f""" Insgesamt hast du {user_correct_obj} Objekte richtig erraten und 
        hast pro objekt im Durchschnitt {user_minutes:0.0f} Minuten und {user_seconds:0.0f} Sekunden gebraucht. Und ich habe {alexa_correct_obj} richtig erraten 
        und habe im Durchschnitt {alexa_minutes:0.0f} Minuten und {alexa_seconds:0.0f} Sekunden gebraucht."""

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