# -*- coding: utf-8 -*-

import logging
import json

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_model.ui import SimpleCard
from six import PY2


skill_name = "The Postmaster by Rabindranath Tagore"
help_text = ("I can tell you Rabindranath Tagore's famour short story, "
             "The Postmaster")
goodbye_message = "Thank you for using, The Postmaster by Rabindranath "\
                  "Tagore. If you like this skill, please write your "\
                  "feedback on Amazon website. Goodbye!"
welcome_message = "Hi, welcome to The Postmaster by Rabindranath Tagore."
continue_message = "To continue, say next"


sb = SkillBuilder()

POSITION = 0


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@sb.request_handler(can_handle_func=is_request_type("LaunchRequest"))
def launch_request_handler(handler_input):
    """Handler for Skill Launch."""
    # type: (HandlerInput) -> Response
    try:
        with open('story.txt', 'r', encoding='utf-8') as stream:
            data = stream.read().split('\n\n\n')
        length = len(data)
        speech = welcome_message + data[POSITION] + "." + continue_message
        handler_input.attributes_manager.session_attributes['data'] = data
        handler_input.attributes_manager.session_attributes['length'] = length
        handler_input.attributes_manager.session_attributes['POSITION'] = \
            (POSITION + 1)
    except Exception:
        speech = "Sorry, an error occured !!"

    print("Position is: {}"
          .format(handler_input.attributes_manager.session_attributes[
              'POSITION']))

    print("Handler input Attributes Manager is: {}"
          .format(handler_input.attributes_manager.session_attributes))

    handler_input.response_builder.speak(
        speech).ask(help_text)
    return handler_input.response_builder.response


@sb.request_handler(can_handle_func=is_intent_name("NextIntent"))
def next_intent_handler(handler_input):

    print("Handler input Attributes Manager is: {}"
          .format(handler_input.attributes_manager.session_attributes))

    if 'POSITION' in handler_input.attributes_manager.session_attributes and \
        'data' in handler_input.attributes_manager.session_attributes and \
            'length' in handler_input.attributes_manager.session_attributes:
        position = handler_input.attributes_manager\
            .session_attributes['POSITION']
        data = handler_input.attributes_manager.session_attributes['data']
        length = handler_input.attributes_manager.session_attributes['length']
        print("Position in Next is {}".format(position))
        print("length is: {}".format(length))
    else:
        speech = "The Postmaster by Rabindranath Tagore has not started yet."\
                 " To start the story, say, Launch The Postmaster by "\
                 "Rabindranath Tagore"

    if position != (length - 1):
        speech = data[position] + "." + continue_message
        handler_input.attributes_manager.session_attributes['POSITION'] = \
            (position + 1)
    else:
        speech = data[position] + "." + goodbye_message

    handler_input.response_builder.speak(
        speech).ask(help_text)
    return handler_input.response_builder.response


@sb.request_handler(can_handle_func=is_intent_name("AMAZON.HelpIntent"))
def help_intent_handler(handler_input):
    """Handler for Help Intent."""
    # type: (HandlerInput) -> Response
    handler_input.response_builder.speak(help_text).ask(help_text)
    return handler_input.response_builder.response


@sb.request_handler(
    can_handle_func=lambda handler_input:
        is_intent_name("AMAZON.CancelIntent")(handler_input) or
        is_intent_name("AMAZON.StopIntent")(handler_input))
def cancel_and_stop_intent_handler(handler_input):
    """Single handler for Cancel and Stop Intent."""
    # type: (HandlerInput) -> Response
    speech_text = goodbye_message

    return handler_input.response_builder.speak(speech_text).response


@sb.request_handler(can_handle_func=is_request_type("SessionEndedRequest"))
def session_ended_request_handler(handler_input):
    """Handler for Session End."""
    # type: (HandlerInput) -> Response
    return handler_input.response_builder.response


@sb.request_handler(can_handle_func=is_intent_name("AMAZON.FallbackIntent"))
def fallback_handler(handler_input):
    """AMAZON.FallbackIntent is only available in en-US locale.
    This handler will not be triggered except in that locale,
    so it is safe to deploy on any locale.
    """
    # type: (HandlerInput) -> Response
    speech = (
        "Sorry, {} can't help you with that. {}").format(skill_name,
                                                         help_text)
    reprompt = help_text
    handler_input.response_builder.speak(speech).ask(reprompt)
    return handler_input.response_builder.response


def convert_speech_to_text(ssml_speech):
    """convert ssml speech to text, by removing html tags."""
    # type: (str) -> str
    s = SSMLStripper()
    s.feed(ssml_speech)
    return s.get_data()


@sb.global_response_interceptor()
def add_card(handler_input, response):
    """Add a card by translating ssml text to card content."""
    # type: (HandlerInput, Response) -> None
    response.card = SimpleCard(
        title=skill_name,
        content=convert_speech_to_text(response.output_speech.ssml))


@sb.global_response_interceptor()
def log_response(handler_input, response):
    """Log response from alexa service."""
    # type: (HandlerInput, Response) -> None
    print("Alexa Response: {}\n".format(response))


@sb.global_request_interceptor()
def log_request(handler_input):
    """Log request to alexa service."""
    # type: (HandlerInput) -> None
    print("Alexa Request: {}\n".format(handler_input.request_envelope.request))


@sb.exception_handler(can_handle_func=lambda i, e: True)
def all_exception_handler(handler_input, exception):
    """Catch all exception handler, log exception and
    respond with custom message.
    """
    # type: (HandlerInput, Exception) -> None
    print("Encountered following exception: {}".format(exception))

    speech = "Sorry, there was some problem. Please try again!!"
    handler_input.response_builder.speak(speech).ask(speech)

    return handler_input.response_builder.response


# Convert SSML to Card text ############
# This is for automatic conversion of ssml to text content on simple card
# You can create your own simple cards for each response, if this is not
# what you want to use.


try:
    from HTMLParser import HTMLParser
except ImportError:
    from html.parser import HTMLParser


class SSMLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.full_str_list = []
        if not PY2:
            self.strict = False
            self.convert_charrefs = True

    def handle_data(self, d):
        self.full_str_list.append(d)

    def get_data(self):
        return ''.join(self.full_str_list)

################################################


# Handler to be provided in lambda console.
lambda_handler = sb.lambda_handler()
