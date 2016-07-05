import re

from signer.signature_tool_base import SignatureToolBase
from signer import settings, siglists


class CSignatureTool(SignatureToolBase):
    """This is the class for signature generation tools that work on
    breakpad C/C++ stacks. """

    def __init__(self):
        super(CSignatureTool, self).__init__()

        self.irrelevant_signature_re = re.compile(
            '|'.join(siglists.IRRELEVANT_SIGNATURE_RE)
        )
        self.prefix_signature_re = re.compile(
            '|'.join(siglists.PREFIX_SIGNATURE_RE)
        )
        self.trim_dll_signature_re = re.compile(
            '|'.join(siglists.TRIM_DLL_SIGNATURE_RE)
        )
        self.signature_sentinels = siglists.SIGNATURE_SENTINELS

        self.fixup_space = re.compile(r' (?=[\*&,])')
        self.fixup_comma = re.compile(r',(?! )')

    def _do_generate(self, frames, crashed_thread):
        """
        each element of frames names a frame in the crash stack; and is:
          - a prefix of a relevant frame: Append this element to the signature
          - a relevant frame: Append this element and stop looking
          - irrelevant: Append this element only after seeing a prefix frame
        The signature is a ' | ' separated string of frame names.
        """
        signature_notes = []

        # shorten frames to the first signatureSentinel
        sentinel_locations = []
        for a_sentinel in self.signature_sentinels:
            if type(a_sentinel) == tuple:
                a_sentinel, condition_fn = a_sentinel
                if not condition_fn(frames):
                    continue
            try:
                sentinel_locations.append(frames.index(a_sentinel))
            except ValueError:
                pass
        if sentinel_locations:
            frames = frames[min(sentinel_locations):]

        # Get all the relevant frame signatures.
        new_signature_list = []
        for a_signature in frames:
            # If the signature matches the irrelevant signatures regex,
            # skip to the next frame.
            if self.irrelevant_signature_re.match(a_signature):
                continue

            # If the signature matches the trim dll signatures regex,
            # rewrite it to remove all but the module name.
            if self.trim_dll_signature_re.match(a_signature):
                a_signature = a_signature.split('@')[0]

                # If this trimmed DLL signature is the same as the previous
                # frame's, we do not want to add it.
                if (
                    new_signature_list and
                    a_signature == new_signature_list[-1]
                ):
                    continue

            new_signature_list.append(a_signature)

            # If the signature does not match the prefix signatures regex,
            # then it is the last one we add to the list.
            if not self.prefix_signature_re.match(a_signature):
                break

        signature = settings.DELIMITER.join(new_signature_list)

        # Handle empty signatures to explain why we failed generating them.
        if signature == '' or signature is None:
            if crashed_thread is None:
                signature_notes.append(
                    'CSignatureTool: No signature could be created because '
                    'we do not know which thread crashed'
                )
                signature = 'EMPTY: no crashing thread identified'
            else:
                signature_notes.append(
                    'CSignatureTool: No proper signature could be created '
                    'because no good data for the crashing thread ({}) was '
                    'found'.format(crashed_thread)
                )
                try:
                    signature = frames[0]
                except IndexError:
                    signature = 'EMPTY: no frame data available'

        return signature, signature_notes

# An alias used to import at runtime.
SignatureTool = CSignatureTool
