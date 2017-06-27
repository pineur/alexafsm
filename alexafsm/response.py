from collections import namedtuple

from alexafsm.session_attributes import SessionAttributes


PLAIN_TEXT = 'PlainText'
SSML = 'SSML'


def _format_text(text_to_format, text_type):
    if text_type == PLAIN_TEXT:
        return text_to_format
    elif text_type == SSML:
        return '<speak>' + text_to_format + '</speak>'

    raise ValueError(f'text_type {text_type} is not {PLAIN_TEXT} or {SSML}')


class Response(namedtuple('Response', ['speech', 'card', 'card_content', 'reprompt', 'should_end',
                                       'image', 'session_attributes', 'output_speech_type'])):
    """Pythonic representation of the response to be sent to Alexa"""
    def __new__(cls, speech: str, reprompt: str, card: str = None, should_end: bool = False,
                card_content: str = None, image: str = None,
                session_attributes: SessionAttributes = SessionAttributes(), output_speech_type: str = SSML):
        if not card_content:
            card_content = speech
        return super(Response, cls) \
            .__new__(cls, speech=speech, card=card, reprompt=reprompt, should_end=should_end,
                     card_content=card_content.strip(), image=image,
                     session_attributes=session_attributes, output_speech_type=output_speech_type)

    def to_json(self):
        """Build entire Alexa response as a JSON-serializable dictionary"""
        card = None

        text_type_key = 'text' if self.output_speech_type == PLAIN_TEXT else SSML.lower()

        if self.card:
            if self.image:
                card = {
                    'type': 'Standard',
                    'image': {
                        'largeImageUrl': self.image
                    },
                    'title': self.card,
                    'text': self.card_content
                }
            else:
                card = {
                    'type': 'Simple',
                    'title': self.card,
                    'content': self.card_content
                }

        resp = {
            'outputSpeech': {
                'type': self.output_speech_type,
                text_type_key: _format_text(self.speech, self.output_speech_type)
            },
            'card': card,
            'reprompt': {
                'outputSpeech': {
                    'type': self.output_speech_type,
                    text_type_key: _format_text(self.reprompt, self.output_speech_type)
                }
            },
            'shouldEndSession': self.should_end
        }

        if not resp['card']:
            del resp['card']

        return {
            'version': '1.0',
            'sessionAttributes': self.session_attributes,
            'response': resp
        }


def end(skill_name: str, speech: str = None) -> Response:
    if speech is None:
        speech = f"Thank you for using {skill_name}"

    return Response(
        speech=speech,
        reprompt="",
        should_end=True)


NOT_UNDERSTOOD = "I did not understand your response."
