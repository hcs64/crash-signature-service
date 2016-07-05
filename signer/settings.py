# The list of languages for which we can generate signatures.
SUPPORTED_LANGUAGES = (
    'c',
    'java',
)

# The default language to use if none is provided.
DEFAULT_LANGUAGE = 'c'

# The delimiter used to separate signature parts.
DELIMITER = ' | '

# The delimiter used by the Java Signature Tool to separate parts.
JAVA_DELIMITER = ': '

# Maximum length of a signature after it has been generated.
SIGNATURE_MAX_LENGTH = 255

# Whether or not to escape single quotes (with another single quote).
ESCAPE_SINGLE_QUOTE = True

# Whether or not to collapse arguments during C signatures normalization.
COLLAPSE_ARGUMENTS = False
