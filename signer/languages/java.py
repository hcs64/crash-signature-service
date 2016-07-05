import re

from signer.signature_tool_base import SignatureToolBase
from signer import settings


class JavaSignatureTool(SignatureToolBase):
    """This is the signature generation class for Java signatures."""

    java_line_number_killer = re.compile(r'\.java\:\d+\)$')
    java_hex_addr_killer = re.compile(r'@[0-9a-f]{8}')

    @staticmethod
    def join_ignore_empty(delimiter, list_of_strings):
        return delimiter.join(x for x in list_of_strings if x)

    def _do_generate(self, source, crashed_thread):
        signature_notes = []
        try:
            source_list = [x.strip() for x in source.splitlines()]
        except AttributeError:
            signature_notes.append(
                'JavaSignatureTool: stack trace not in expected format'
            )
            return (
                "EMPTY: Java stack trace not in expected format",
                signature_notes
            )
        try:
            java_exception_class, description = source_list[0].split(':', 1)
            java_exception_class = java_exception_class.strip()
            # relace all hex addresses in the description by the string <addr>
            description = self.java_hex_addr_killer.sub(
                r'@<addr>',
                description
            ).strip()
        except ValueError:
            java_exception_class = source_list[0]
            description = ''
            signature_notes.append(
                'JavaSignatureTool: stack trace line 1 is '
                'not in the expected format'
            )
        try:
            java_method = re.sub(
                self.java_line_number_killer,
                '.java)',
                source_list[1]
            )
            if not java_method:
                signature_notes.append(
                    'JavaSignatureTool: stack trace line 2 is empty'
                )
        except IndexError:
            signature_notes.append(
                'JavaSignatureTool: stack trace line 2 is missing'
            )
            java_method = ''

        # an error in an earlier version of this code resulted in the colon
        # being left out of the division between the description and the
        # java_method if the description didn't end with "<addr>".  This code
        # perpetuates that error while correcting the "<addr>" placement
        # when it is not at the end of the description.  See Bug 865142 for
        # a discussion of the issues.
        if description.endswith('<addr>'):
            # at which time the colon placement error is to be corrected
            # just use the following line as the replacement for this entire
            # if/else block
            signature = self.join_ignore_empty(
                settings.DELIMITER,
                (java_exception_class, description, java_method)
            )
        else:
            description_java_method_phrase = self.join_ignore_empty(
                ' ',
                (description, java_method)
            )
            signature = self.join_ignore_empty(
                settings.DELIMITER,
                (java_exception_class, description_java_method_phrase)
            )

        if len(signature) > self.max_len:
            signature = settings.DELIMITER.join(
                (java_exception_class, java_method)
            )
            signature_notes.append(
                'JavaSignatureTool: dropped Java exception '
                'description due to length'
            )

        return signature, signature_notes
