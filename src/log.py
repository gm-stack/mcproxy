import logging

class ConsoleHandler(logging.StreamHandler):
    """
    A handler class which writes logging records, appropriately formatted,
    to a console.
    """

    def emit(self, record):
        """
        Emit a record.

        If a formatter is specified, it is used to format the record.
        The record is then written to the stream with a trailing newline.  If
        exception information is present, it is formatted using
        traceback.print_exception and appended to the stream.  If the stream
        has an 'encoding' attribute, it is used to determine how to do the
        output to the stream.
        """
        try:
            msg = self.format(record)
            stream = self.stream
            fs = "%s\n"
            stream.write


logging.config.dictConfig({
    'version': 1,
    'formatters': {
        },
    'handlers': {
        'console': {
            'class': logging.StreamHandler,
            'formatter': 'brief',
            'level': 'INFO',
        },
        'file': {
            'class': logging.handlers.RotatingFileHandler
        },
        
    },
})