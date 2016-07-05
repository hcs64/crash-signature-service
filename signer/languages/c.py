import re

from signer.signature_tool_base import SignatureToolBase
from signer import settings, siglists


class CSignatureTool(SignatureToolBase):
    """This is the base class for signature generation tools that work on
    breakpad C/C++ stacks.  It provides a method to normalize signatures
    and then defines its own '_do_generate' method."""

    hang_prefixes = {
        -1: "hang",
        1: "chromehang"
    }

    def __init__(self, config, quit_check_callback=None):
        super(CSignatureTool, self).__init__(config, quit_check_callback)
        self.irrelevant_signature_re = re.compile(
            '|'.join(siglists.IRRELEVANT_SIGNATURE_RE)
        )
        self.prefix_signature_re = re.compile(
            '|'.join(siglists.PREFIX_SIGNATURE_RE)
        )
        self.signatures_with_line_numbers_re = re.compile(
            '|'.join(siglists.SIGNATURES_WITH_LINE_NUMBERS_RE)
        )
        self.trim_dll_signature_re = re.compile(
            '|'.join(siglists.TRIM_DLL_SIGNATURE_RE)
        )
        self.signature_sentinels = siglists.SIGNATURE_SENTINELS

        self.fixup_space = re.compile(r' (?=[\*&,])')
        self.fixup_comma = re.compile(r',(?! )')

    @staticmethod
    def _is_exception(
        exception_list,
        remaining_original_line,
        line_up_to_current_position
    ):
        for an_exception in exception_list:
            if remaining_original_line.startswith(an_exception):
                return True
            if line_up_to_current_position.endswith(an_exception):
                return True
        return False

    def _collapse(
        self,
        function_signature_str,
        open_string,
        replacement_open_string,
        close_string,
        replacement_close_string,
        exception_substring_list=(),
    ):
        """this method takes a string representing a C/C++ function signature
        and replaces anything between to possibly nested delimiters"""
        target_counter = 0
        collapsed_list = []
        exception_mode = False

        def append_if_not_in_collapse_mode(a_character):
            if not target_counter:
                collapsed_list.append(a_character)

        for index, a_character in enumerate(function_signature_str):
            if a_character == open_string:
                if self._is_exception(
                    exception_substring_list,
                    function_signature_str[index + 1:],
                    function_signature_str[:index]
                ):
                    exception_mode = True
                    append_if_not_in_collapse_mode(a_character)
                    continue
                append_if_not_in_collapse_mode(replacement_open_string)
                target_counter += 1
            elif a_character == close_string:
                if exception_mode:
                    append_if_not_in_collapse_mode(a_character)
                    exception_mode = False
                else:
                    target_counter -= 1
                    append_if_not_in_collapse_mode(replacement_close_string)
            else:
                append_if_not_in_collapse_mode(a_character)

        edited_function = ''.join(collapsed_list)
        return edited_function

    def normalize_signature(
        self,
        module=None,
        function=None,
        file=None,
        line=None,
        module_offset=None,
        offset=None,
        function_offset=None,
        normalized=None,
        **kwargs  # eat any extra kwargs passed in
    ):
        """ returns a structured conglomeration of the input parameters to
        serve as a signature.  The parameter names of this function reflect the
        exact names of the fields from the jsonMDSW frame output.  This allows
        this function to be invoked by passing a frame as **a_frame. Sometimes,
        a frame may already have a normalized version cached.  If that exists,
        return it instead.
        """
        if normalized is not None:
            return normalized
        if function:
            function = self._collapse(
                function,
                '<',
                '<',
                '>',
                'T>',
                ('name omitted', 'IPC::ParamTraits')
            )
            if settings.COLLAPSE_ARGUMENTS:
                function = self._collapse(
                    function,
                    '(',
                    '',
                    ')',
                    '',
                    ('anonymous namespace', 'operator')
                )

            if self.signatures_with_line_numbers_re.match(function):
                function = "%s:%s" % (function, line)
            # Remove spaces before all stars, ampersands, and commas
            function = self.fixup_space.sub('', function)
            # Ensure a space after commas
            function = self.fixup_comma.sub(', ', function)
            return function
        #if source is not None and source_line is not None:
        if file and line:
            filename = file.rstrip('/\\')
            if '\\' in filename:
                file = filename.rsplit('\\')[-1]
            else:
                file = filename.rsplit('/')[-1]
            return '%s#%s' % (file, line)
        if not module and not module_offset and offset:
            return "@%s" % offset
        if not module:
            module = ''  # might have been None
        return '%s@%s' % (module, module_offset)

    def _do_generate(self, source_list, crashed_thread):
        """
        each element of signatureList names a frame in the crash stack; and is:
          - a prefix of a relevant frame: Append this element to the signature
          - a relevant frame: Append this element and stop looking
          - irrelevant: Append this element only after seeing a prefix frame
        The signature is a ' | ' separated string of frame names.
        """
        signature_notes = []

        # shorten source_list to the first signatureSentinel
        sentinel_locations = []
        for a_sentinel in self.signature_sentinels:
            if type(a_sentinel) == tuple:
                a_sentinel, condition_fn = a_sentinel
                if not condition_fn(source_list):
                    continue
            try:
                sentinel_locations.append(source_list.index(a_sentinel))
            except ValueError:
                pass
        if sentinel_locations:
            source_list = source_list[min(sentinel_locations):]

        # Get all the relevant frame signatures.
        new_signature_list = []
        for a_signature in source_list:
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
                signature_notes.append("CSignatureTool: No signature could be "
                                       "created because we do not know which "
                                       "thread crashed")
                signature = "EMPTY: no crashing thread identified"
            else:
                signature_notes.append("CSignatureTool: No proper signature "
                                       "could be created because no good data "
                                       "for the crashing thread (%s) was found"
                                       % crashed_thread)
                try:
                    signature = source_list[0]
                except IndexError:
                    signature = "EMPTY: no frame data available"

        return signature, signature_notes
