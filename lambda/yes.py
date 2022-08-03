import time

import ask_sdk_core.utils as ask_utils
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import get_supported_interfaces

import random as random

# APL
from ask_sdk_model.interfaces.alexa.presentation.apl import RenderDocumentDirective

# Helper functions
from utils import load_apl_document, create_presigned_url
from utterances import choose_utterance, UTTERANCES


class YesIntentHandler(AbstractRequestHandler):
    """Handler for Yes Intent."""
    
    # Documents for rendering visual response
    template_apl = load_apl_document("jsondata/alexas_turn.json")
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
        
        ### DW: STATISTICS ###
        # Correkt Objekts
        statistics = attributes_manager.persistent_attributes["statistics"]
        statistics["alexa"]["correct_obj"] += 1
        # Alexas Time berechnen und in statistics ablegen
        alexas_start_timestamp = statistics["alexa"]["start_timestamp"] 
        alexas_end_time = time.monotonic()
        delta_time = alexas_end_time - alexas_start_timestamp
        statistics["alexa"]["duration_in_sec"] += delta_time
        statistics["alexa"]["start_timestamp"] = time.monotonic()
        # USER Time starten und ablegen
        user_start_timestamp = time.monotonic()
        statistics["user"]["start_timestamp"] = user_start_timestamp
        ###
        
        # DW: Afer the YesIntent was triggered Alexas gets her turn
        # for now simply random choice without storing the already mentioned objects
        # TODO: storing the already mentioned objects
        alexas_objects = ["globus", "europa", "fff", "konsole", "saturn", "boot", "biene", "fernrohr", "stift", "mathe"]
        act_object = random.choice(alexas_objects)
        # utterances are in the same file, so we have to distinct between which utterances should be used:
        # for now when Alexa describe an object the prefix "alexa_" is used
        act_obj_utterance = "alexa_" + act_object
        speak_output = choose_utterance(mood, "yes") + choose_utterance(mood, act_obj_utterance)
        
        # reset wrong_counter and already_mentioned because new round
        # update persistent memory with new wrong_counter and already_mentioned
        # and act_object and statistics
        already_mentioned.clear()
        attributes = {
            "mood": mood, 
            "wrong_counter": 0, 
            "already_mentioned": already_mentioned,  # Könnte man hier nicht einfach leere Liste?
            "act_object": act_object,
            "statistics": statistics
        }
        attributes_manager.persistent_attributes.update(attributes)
        attributes_manager.save_persistent_attributes()
        
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