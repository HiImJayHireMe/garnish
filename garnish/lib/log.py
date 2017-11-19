# coding=utf-8
import datetime
import logging
from logging import handlers

from naga import valmap, mapv

from garnish.lib.utils import relative_url

log_file = relative_url('data/run.log')


class LoggerFormatter(logging.Formatter):
    def __init__(self,
                 fmt='[+] %(asctime)s [PID:%(process)s] |%(levelname)s| %(module)s: ~|~%(message)s',
                 datefmt='[%02d/%s/%04d:%02d:%02d:%02d]'):
        super(LoggerFormatter, self).__init__(fmt=fmt, datefmt=datefmt)

    def formatTime(self, record, datefmt=None):
        return self.time()

    def time(self):
        """Return now() in Apache Common Log Format (no timezone)."""
        now = datetime.datetime.now()
        monthnames = ['jan', 'feb', 'mar', 'apr', 'may', 'jun',
                      'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
        month = monthnames[now.month - 1].capitalize()
        return ('[%02d/%s/%04d:%02d:%02d:%02d]' %
                (now.day, month, now.year, now.hour, now.minute, now.second))

    def format(self, record, sep='~|~'):
        fmt = super(LoggerFormatter, self).format(record)
        if len(fmt) > 2001:
            fmt = ''.join([fmt[:1000],
                           '\n\t... \n\t<snip>\n\t...\n',
                           fmt[-1000:]])

        vals, rst = fmt.split(sep)
        stuff = mapv(lambda s: s.strip(), vals.split())
        name = stuff[-1].upper()
        fst = stuff[:-1]
        otherstuff, lvl = ' '.join(fst[:-1]), fst[-1]
        fst_str = '{}{:-<12}>'.format(otherstuff, lvl)
        tofmt = ' '.join([fst_str, name]), rst
        res = '{:.<80}{}'.format(*tofmt)
        return res


loggers = {}


class DatabaseFormatter(logging.Formatter):
    def __init__(self):
        """
asctime	    %(asctime)s	Human-readable time when the LogRecord was created. By default this is of the form ���2003-07-08 16:49:45,896��� (the numbers after the comma are millisecond portion of the time).
created	    %(created)f	Time when the LogRecord was created (as returned by time.time()).
exc_info	You shouldn���t need to format this yourself.	Exception tuple (�� la sys.exc_info) or, if no exception has occurred, None.
filename	%(filename)s	Filename portion of pathname.
funcName	%(funcName)s	Name of function containing the logging call.
levelname	%(levelname)s	Text logging level for the message ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL').
levelno	    %(levelno)s	Numeric logging level for the message (DEBUG, INFO, WARNING, ERROR, CRITICAL).
lineno	    %(lineno)d	Source line number where the logging call was issued (if available).
module	    %(module)s	Module (name portion of filename).
msecs	    %(msecs)d	Millisecond portion of the time when the LogRecord was created.
message	    %(message)s	The logged message, computed as msg % args. This is set when Formatter.format() is invoked.
name	    %(name)s	Name of the logger used to log the call.
pathname	%(pathname)s	Full pathname of the source file where the logging call was issued (if available).
process	    %(process)d	Process ID (if available).
processName	%(processName)s	Process name (if available).
thread	    %(thread)d	Thread ID (if available).
threadName	%(threadName)s	Thread name (if available).
        """
        self.fmtd = dict(
            date='created',
            module='module',
            fname='filename',
            level='levelname',
            levelno='levelno',
            lineno='lineno',
            pathname='pathname',
            process='process',
            thread_='thread',
            threadname='threadName',
            funcname='funcName',
            message='message'
        )
        super(DatabaseFormatter, self).__init__()

    def format(self, record):
        recordd = valmap(lambda v: getattr(record, v), self.fmtd)
        recordd['date'] = datetime.datetime.fromtimestamp(float(recordd['date']))
        return recordd


def get_logger(log_file=log_file):
    global loggers
    if loggers:
        return loggers['logger']
    else:
        logger = logging.getLogger()

        fhandler = handlers.RotatingFileHandler(log_file, maxBytes=(1024 * 1000 * 10), backupCount=10)
        shandler = logging.StreamHandler()

        fmter = LoggerFormatter()

        fhandler.setFormatter(fmter)
        shandler.setFormatter(fmter)

        logger.addHandler(fhandler)
        logger.addHandler(shandler)

        logger.setLevel(logging.DEBUG)

    loggers['logger'] = logger

    return get_logger()


logger = get_logger(relative_url('data/run.log'))

if __name__ == '__main__':
    logger.info("test!")
