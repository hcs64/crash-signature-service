import falcon

from signer import middleware, signer_service


app = falcon.API(middleware=[
    middleware.RequireJSON(),
    middleware.JSONTranslator(),
])
app.add_route('/sign', signer_service.SignerService())
