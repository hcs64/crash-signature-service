import mock

from signer.signature_tool_base import SignatureToolBase


class TestSignatureToolBase(object):
    @mock.patch('signer.signature_tool_base.settings')
    def test_generate_quote_escaping(self, m_settings):
        m_settings.ESCAPE_SINGLE_QUOTE = True

        # Create a fake class that implements the _do_generate method.
        class FakeTool(SignatureToolBase):
            def _do_generate(self, *args, **kwargs):
                return (
                    "some | signature | with | 'quotes'",
                    [],
                )

        inst = FakeTool()
        signature, signature_notes = inst.generate([])

        assert signature == "some | signature | with | ''quotes''"

    @mock.patch('signer.signature_tool_base.settings')
    def test_generate_signature_length(self, m_settings):
        m_settings.SIGNATURE_MAX_LENGTH = 255

        # Create a fake class that implements the _do_generate method.
        class FakeTool(SignatureToolBase):
            def _do_generate(self, *args, **kwargs):
                return (
                    'a' * 500,
                    [],
                )

        inst = FakeTool()
        signature, signature_notes = inst.generate([])

        assert signature == '{}...'.format('a' * (255 - 3))
        assert (
            'SignatureTool: signature truncated due to length' in
            signature_notes
        )
