 # -*- coding: utf-8 -*-

import logging
import json

# DW: brauchen os für S3Adapter()
import os

import ask_sdk_core.utils as ask_utils

# DW: Hier habe ich den Sillbuilder in CustomSkillBuilder eingetauscht
# from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.skill_builder import CustomSkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_core.utils import get_supported_interfaces
from ask_sdk_model.interfaces.alexa.presentation.apl import RenderDocumentDirective, ExecuteCommandsDirective, SpeakItemCommand, AutoPageCommand, HighlightMode, UserEvent

# store and retrieve persistent data
from ask_sdk_s3.adapter import S3Adapter
s3_adapter = S3Adapter(bucket_name=os.environ["S3_PERSISTENCE_BUCKET"])

# DW: Import custom intent handler
# TODO: Nicht vergessen diese auch unten beim CustomSkillBuilder zu adden
# personality
from mood_choice import PersonalityIntentHandler

# handler for the objects
from bee import BienenIntentHandler
from globe import GlobusIntentHandler
from console import KonsoleIntentHandler
from pen import StiftIntentHandler
from book import BuchIntentHandler
from eu import EUIntentHandler
from telescope import FernrohrIntentHandler
from dolphin import DolphinIntentHandler
from teacher import TeacherIntentHandler
from rainbow import RainbowIntentHandler

# Helper functions
# utterances handler for choosen personality
from utterances import choose_utterance, UTTERANCES
from utils import load_apl_document

from ask_sdk_model import Response

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def _load_apl_document(file_path):
    with open(file_path) as f:
        return json.load(f)

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    
    template_mood_doc = "data/template_mood.json"
    mood_doc = "data/mood.json"
    
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Willkommen im Wimmelbild-Spiel. Du kannst dich entscheiden, ob ich gut oder schlecht gelaunt mit dir spiele. Wie soll ich heute gelaunt sein?"

        response_builder = handler_input.response_builder
        
        if get_supported_interfaces(
                handler_input).alexa_presentation_apl is not None:
            response_builder.add_directive(
                RenderDocumentDirective(
                    token="moodToken",
                    document=load_apl_document(self.template_mood_doc),
                    datasources=load_apl_document(self.mood_doc)
                ))
        
        return response_builder.speak(speak_output).response


class HelloWorldIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("HelloWorldIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Hello World!"

        if get_supported_interfaces(handler_input).alexa_presentation_apl is not None:
            return (
                handler_input.response_builder
                    .speak(speak_output)
                    # .ask("add a reprompt if you want to keep the session open for the user to respond")
                    .add_directive(
                        RenderDocumentDirective(
                            token="pagerToken",
                            document=_load_apl_document("document.json"),
                            datasources=_load_apl_document("default.json")
                        )
                    )
                    .response
            )
        else:
            return (
                handler_input.response_builder
                .speak("Nö.")
                .response
            )


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Du bist hier im Wimmelbild-Spiel und kannst mir ein Objekt auf dem Bild beschreiben."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class NoIntentHandler(AbstractRequestHandler):
    """Handler for No Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.NoIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        
        # Identify chosen modus.
        attributes_manager = handler_input.attributes_manager
        mood = attributes_manager.persistent_attributes["mood"]
        wrong_counter = attributes_manager.persistent_attributes["wrong_counter"]
        already_mentioned = attributes_manager.persistent_attributes["already_mentioned"]
        
        # TODO: Wimmelbild wieder zeigen
        wrong_counter += 1
        
        if wrong_counter <= 3:
            speak_output = choose_utterance(mood, "no_again")
        else:
            wrong_counter = 0
            already_mentioned.clear()
            speak_output = choose_utterance(mood, "no_stop")
            
        # update persistent memory with new wrong_counter and already_mentioned
        attributes = {"mood": mood, "wrong_counter": wrong_counter, "already_mentioned": already_mentioned}
        attributes_manager.persistent_attributes.update(attributes)
        attributes_manager.save_persistent_attributes()
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class YesIntentHandler(AbstractRequestHandler):
    """Handler for Yes Intent."""
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
        attributes = {"mood": mood, "wrong_counter": 0, "already_mentioned": already_mentioned.clear()}
        attributes_manager.persistent_attributes.update(attributes)
        attributes_manager.save_persistent_attributes()
        
        # TODO: Wimmelbild wieder zeigen
        # reset wrong proposal counter because new round
        speak_output = choose_utterance(mood, "yes")
        #auf neuen input warten
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # Identify chosen modus.
        attributes_manager = handler_input.attributes_manager
        mood = attributes_manager.persistent_attributes["mood"]
        
        speak_output = choose_utterance(mood, "bye")

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )

class FallbackIntentHandler(AbstractRequestHandler):
    """Single handler for Fallback Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In FallbackIntentHandler")
        
        # TODO: Wann wird das getriggert? Und soll immer getriggert werden, wenn sie keine Ahnung hat.
        
        # Identify chosen modus.
        attributes_manager = handler_input.attributes_manager
        mood = attributes_manager.persistent_attributes["mood"]
        
        speak_output = choose_utterance(mood, "no_clue")

        return handler_input.response_builder.speak(speech).ask(speech).response

class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        #speak_output = ""
        speak_output = "Es gab einen Fehler: {} in {}.".format(exception, __name__)

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


# sb = SkillBuilder()
sb = CustomSkillBuilder(persistence_adapter=s3_adapter)

# TODO: Hier CustomSkillBuilder anpassen!
# imported Intents:
sb.add_request_handler(PersonalityIntentHandler())
sb.add_request_handler(BienenIntentHandler())
sb.add_request_handler(GlobusIntentHandler())
sb.add_request_handler(KonsoleIntentHandler())
sb.add_request_handler(StiftIntentHandler())
sb.add_request_handler(BuchIntentHandler())
sb.add_request_handler(EUIntentHandler())
sb.add_request_handler(FernrohrIntentHandler())
sb.add_request_handler(DolphinIntentHandler())
sb.add_request_handler(TeacherIntentHandler())
sb.add_request_handler(RainbowIntentHandler())

# here all intents within this file: 
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(HelloWorldIntentHandler())
sb.add_request_handler(YesIntentHandler())
sb.add_request_handler(NoIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()