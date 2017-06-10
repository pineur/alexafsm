from collections import namedtuple

from alexafsm.session_attributes import SessionAttributes


PLAIN_TEXT = 'PlainText'

class Response(namedtuple('Response', ['speech', 'card', 'card_content', 'reprompt', 'should_end',
                                       'image', 'session_attributes', 'output_speech_type'])):
    """Pythonic representation of the response to be sent to Alexa"""
    def __new__(cls, speech: str, reprompt: str, card: str = None, should_end: bool = False,
                card_content: str = None, image: str = None,
                session_attributes: SessionAttributes = SessionAttributes(), output_speech_type: str = PLAIN_TEXT):
        if not card_content:
            card_content = speech
        return super(Response, cls) \
            .__new__(cls, speech=speech, card=card, reprompt=reprompt, should_end=should_end,
                     card_content=card_content.strip(), image=image,
                     session_attributes=session_attributes)

    def to_json(self):
        """Build entire Alexa response as a JSON-serializable dictionary"""
        card = None

        text_type = 'text' if self.output_speech_type == PLAIN_TEXT else 'ssml'

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
                text_type: self.speech
            },
            'card': card,
            'reprompt': {
                'outputSpeech': {
                    'type': self.output_speech_type,
                    text_type: self.reprompt
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


def end(skill_name: str) -> Response:
    return Response(
        speech=f"Thank you for using {skill_name}",
        reprompt="",
        should_end=True)


NOT_UNDERSTOOD = Response(
    speech="I did not understand your response, please say it differently.",
    reprompt="Please respond in a different way."
)
