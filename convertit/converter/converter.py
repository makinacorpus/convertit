import os
import sys
from logging import INFO, Formatter, StreamHandler, getLogger
from tempfile import NamedTemporaryFile, gettempdir
from time import sleep

import uno
import unohelper
from com.sun.star.connection import NoConnectException
from com.sun.star.document.UpdateDocMode import QUIET_UPDATE
from convertit.converter.utils import uno_props

logger = getLogger(__name__)
logger.setLevel(INFO)

formatter = Formatter('[%(asctime)s][%(levelname)s] %(message)s')

stream_handler = StreamHandler()
stream_handler.setLevel(INFO)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


class Converter:
    """
    This convertor takes as optionnal parameters a host and port of a soffice server. It can be
    used to convert any LibreOffice document to a pdf.

    If you are working with the Linux operating system, you must install libreoffice and give the
    virtual environment access to the global site packages.

    If you are working with the MacOS operating system, you must install libreoffice and use the
    python it installs.
    """
    def __init__(self, server='127.0.0.1', port='2002'):
        connection = ("socket,host=%s,port=%s,tcpNoDelay=1;urp;StarOffice.ComponentContext" %
                      (server, port))

        # Do the LibreOffice component dance
        self.context = uno.getComponentContext()
        self.svcmgr = self.context.ServiceManager
        resolver = self.svcmgr.createInstanceWithContext("com.sun.star.bridge.UnoUrlResolver",
                                                         self.context)

        # Test for an existing connection
        unocontext = None
        while not unocontext:
            try:
                unocontext = resolver.resolve("uno:%s" % connection)
            except NoConnectException:
                logger.error('No soffice instance is running.')
                sleep(1)

        if not unocontext:
            sys.exit(1)

        # And some more LibreOffice magic
        unosvcmgr = unocontext.ServiceManager
        self.desktop = unosvcmgr.createInstanceWithContext("com.sun.star.frame.Desktop", unocontext)
        self.cwd = unohelper.systemPathToFileUrl(os.getcwd())

    def convert(self, inputfn):
        """
        This method takes a LibreOffice document as a byte object as parameter and returns the
        associated pdf file as a byte object.
        """
        document = None

        # Load inputfile
        inputprops = uno_props(Hidden=True, ReadOnly=True, UpdateDocMode=QUIET_UPDATE)

        if isinstance(inputfn, bytes):
            inputStream = self.svcmgr.createInstanceWithContext(
                "com.sun.star.io.SequenceInputStream", self.context)
            inputStream.initialize((uno.ByteSequence(inputfn),))
            inputprops += uno_props(InputStream=inputStream)
            inputurl = 'private:stream'
        else:
            inputfn_type = type(inputfn)
            logger.error('Incorrect type for the input parameter: %s unrecognized' % inputfn_type)
            sys.exit(1)

        document = self.desktop.loadComponentFromURL(inputurl, "_blank", 0, inputprops)
        if not document:
            logger.error('Could not open the document.')
            sys.exit(1)

        outputprops = uno_props(FilterName='writer_pdf_Export', Overwrite=True)

        outputf = NamedTemporaryFile()
        outputurl = unohelper.absolutize(gettempdir(), unohelper.systemPathToFileUrl(outputf.name))

        document.storeToURL(outputurl, outputprops)
        document.dispose()
        document.close(True)

        with open(outputf.name, 'rb') as read_file:
            pdf_content = read_file.read()
        if not pdf_content:
            logger.error('soffice error please check.')
            sys.exit(1)
        return pdf_content
