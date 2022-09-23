import time
import ask_sdk_core.utils as ask_utils
import random as random

from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import get_supported_interfaces
from ask_sdk_model.interfaces.alexa.presentation.apl import RenderDocumentDirective # Needed for APL
from utils import load_apl_document, create_presigned_url # APL helper functions
from utterances import choose_utterance, UTTERANCES

from bye import CancelOrStopIntentHandler


class YesIntentHandler(AbstractRequestHandler):
    """
    Handler for Yes Intent. Called after Alexa correctly 
    guesses object described by user.
    """
    
    # Documents for rendering visual response
    template_apl = load_apl_document("jsondata/alexas_turn.json")
    data_apl = load_apl_document("jsondata/data_apl_template.json")
    images = load_apl_document("images.json")
    
    # Set background image in APL template
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
        
        # Setting up statistics, get statistics values from attributes_manager
        statistics = attributes_manager.persistent_attributes["statistics"]
        statistics["alexa"]["correct_obj"] += 1
        statistics["alexa"]["selected_obj"] += 1
        
        # Calculate time for Alexa and save in statistics
        alexas_start_timestamp = statistics["alexa"]["start_timestamp"] 
        alexas_end_time = time.monotonic()
        delta_time = alexas_end_time - alexas_start_timestamp
        statistics["alexa"]["duration_in_sec"] += delta_time
        statistics["alexa"]["start_timestamp"] = time.monotonic()
        
        # Calculate time for User and save in statistics
        user_start_timestamp = time.monotonic()
        statistics["user"]["start_timestamp"] = user_start_timestamp
        
        # Afer the YesIntent was triggered Alexas gets her turn
        alexas_objects = ["globus", "europa", "fff", "konsole", "saturn", "boot", "biene", "fernrohr", "stift", "mathe"] 
        alexas_already_mentioned_objects = statistics["alexa"]["already_mentioned"]
        remaining_objects = list(set(alexas_objects).difference(set(alexas_already_mentioned_objects)))
        
        # check if Alexa has objects left:
        if bool(remaining_objects) == True:
            # has objects left
            act_object = random.choice(remaining_objects)
            # storing the already mentioned objects from alexa in statistics
            statistics["alexa"]["already_mentioned"].append(act_object)
            
            # utterances are in the same file, so we have to distinct between which utterances should be used:
            # for now when Alexa describe an object the prefix "alexa_" is used
            act_obj_utterance = "alexa_" + act_object
            speak_output = choose_utterance(mood, "yes") + choose_utterance(mood, act_obj_utterance)
            
            # Reset values for a new round
            already_mentioned.clear()
            attributes = {
                "mood": mood, 
                "wrong_counter": 0, 
                "already_mentioned": already_mentioned,
                "act_object": act_object,
                "statistics": statistics
            }
            # Update attributes_manager with values and statistics
            attributes_manager.persistent_attributes.update(attributes)
            attributes_manager.save_persistent_attributes()
            
            response_builder = handler_input.response_builder
            
            # Activate APL 
            if get_supported_interfaces(
                    handler_input).alexa_presentation_apl is not None:
                response_builder.add_directive(
                    RenderDocumentDirective(
                        token="WimmelbildToken",
                        document = self.template_apl,
                        datasources = self.data_apl
                    ))
            
            # Give Response
            return response_builder.speak(speak_output).response
        
        # Alexa has no objects left
        else:
            self.template_apl = load_apl_document("statistik_apl.json")
            self.data_apl = load_apl_document("data_statistik_apl.json")
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
            speak_output = choose_utterance(mood, "bye_no_more_objects") + f""" Insgesamt hast du {user_correct_obj} Objekte richtig erraten und 
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
            
                