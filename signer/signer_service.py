import importlib
import json

import falcon

from signer import settings


class SignerService(object):
    """The application responsible for returning generated crash signatures.
    """

    def get_signature(self, lang, frames, crashed_thread):
        package_name = 'signer.languages.{}'.format(lang)
        module = importlib.import_module(package_name)
        app = module.SignatureTool()
        return app.generate(frames, crashed_thread)

    def on_post(self, req, resp):
        lang = req.get_param('lang') or settings.DEFAULT_LANGUAGE
        crashed_thread = req.get_param('crashed_thread')

        if lang not in settings.SUPPORTED_LANGUAGES:
            raise falcon.HTTPBadRequest(
                'Unsupported lang',
                'The language `{}` is not supported.'.format(lang)
            )

        try:
            content = req.context['content']
        except KeyError:
            raise falcon.HTTPBadRequest(
                'Missing frames',
                'A list of frames must be submitted in the request body.'
            )

        frames = content.get('frames')
        if not frames:
            raise falcon.HTTPBadRequest(
                'Missing frames',
                'A list of frames must be submitted in the request body.'
            )

        signature, notes = self.get_signature(lang, frames, crashed_thread)

        resp.body = json.dumps({
            'signature': signature,
            'notes': notes,
            'language': lang,
        })
