from signer import settings


class SignatureToolBase(object):
    """this is the base class for signature generation objects.  It defines the
    basic interface and provides truncation and quoting service.  Any derived
    classes should implement the '_do_generate' function.  If different
    truncation or quoting techniques are desired, then derived classes may
    override the 'generate' function."""

    def generate(self, source_list, crashed_thread=None):
        signature, signature_notes = self._do_generate(
            source_list,
            crashed_thread
        )
        if settings.ESCAPE_SINGLE_QUOTE:
            signature = signature.replace("'", "''")

        if len(signature) > settings.SIGNATURE_MAX_LENGTH:
            signature = "%s..." % signature[:settings.SIGNATURE_MAX_LENGTH - 3]
            signature_notes.append(
                'SignatureTool: signature truncated due to length'
            )

        return signature, signature_notes

    def _do_generate(self, source_list, crashed_thread):
        raise NotImplementedError
