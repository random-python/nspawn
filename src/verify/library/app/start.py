
"""
http://www.torek.net/torek/python/util.html
"""

import errno, os, signal, stat, sys, time, traceback


def sigdie(sig):
    """Attempt to die from a signal.
    """
    signal.signal(sig, signal.SIG_DFL)
    os.kill(os.getpid(), sig)
    # We should not get here, but if we do, this exit() status
    # is as close as we can get to what happens when we die from
    # a signal.
    return 128 + sig


def _split_err(err):
    """Split exc_info() (if any) into one of two "signal based"
    errors, or generic non-signal error.  Returns a trio
    (pipe_err, intr_err, regular_err) with at most one being
    non-None.
    """
    if err is None:
        return None, None, None
    if isinstance(err[1], IOError) and err[1].errno == errno.EPIPE:
        return err, None, None
    if isinstance(err[1], KeyboardInterrupt):
        return None, err, None
    return None, None, err


def _open_tracedump_file(path):
    """Open a trace-dump file (a la kernel core dump file).

    Reject symlinks (if we have that option, at least).  Only
    write regular files that have just one link.
    """
    nofollow = getattr(os, 'O_NOFOLLOW', 0)
    if nofollow == 0:
        # We don't have O_NOFOLLOW.  Racy test for symlink...
        try:
            stbuf = os.lstat(path)
            if stat.S_ISLNK(stbuf.st_mode):
                # EMLINK seems odd, but is what FreeBSD gives
                # with real O_NOFOLLOW.
                raise OSError(errno.EMLINK, 'too many links: %r' % path)
        except OSError as err:
            if err.errno != errno.ENOENT:
                raise
    fd = -1
    close_fd = True
    try:
        fd = os.open(path, os.O_CREAT | os.O_WRONLY | os.O_APPEND | nofollow, 0o0600)
        stbuf = os.fstat(fd)
        if not stat.S_ISREG(stbuf.st_mode):
            raise IOError(errno.EINVAL, 'not a regular file: %r' % path)
        if stbuf.st_nlink > 1:
            raise IOError(errno.EMLINK, 'too many links (%d): %r' %
                (stbuf.st_nlink, path))
        close_fd = False
        return fd
    finally:
        if close_fd and fd >= 0:
            os.close(fd)


def _print_tb(prefix, err, stream):
    """Print given traceback to stream, with optional prefix
    (if not None) and omitting one frame.  (See _show_err().)
    """
    if prefix:
        stream.write(prefix)
    traceback.print_exception(err[0], err[1], err[2].tb_next, None, stream)


def _show_err(err, to_user, to_file, progname, prefix=None):
    """Show info / dump traceback from exc_info() error, but leave
    out the first frame, which is start() itself, and do nothing if
    err is None.  Show this to user (stderr) if so directed, or if
    not doing that, optionally, show into a "core dump".
    """
    if err is None:
        return
    if to_user:
        _print_tb(prefix, err, sys.stderr)
        return
    if not to_file:
        return
    path = '%s.core' % progname  # or use .trace, or ... ?
    fd = -1
    sys.stderr.write('internal error detected')
    try:
        fd = _open_tracedump_file(path)
        stream = os.fdopen(fd, 'w')
        stream.write('pid %d: %s\n' % (os.getpid(), time.ctime()))
        _print_tb(prefix, err, stream)
        stream.write('------------------------------\n')
        stream.close()
        fd = -1
        sys.stderr.write(', trace in %r\n' % path)
    except (OSError, IOError) as err2:
        sys.stderr.write('\nunable to save stack trace: %s\n'
            'set PYTHON_DEBUG=1 in environment'
            ' to print stack trace to stderr\n' % err2)
    finally:
        if fd >= 0:
            os.close(fd)


def start(func, interrupt_trace=None, exc_trace=None):
    """
    Invoke a program, catch various exits, and catch broken-pipe.

    If interrupt_trace is True, a KeyboardInterrupt will show a
    stack trace.  If False, KeyboardInterrupt will not.  If None
    (the default), KeyboardInterrupt will be set from environment
    PYTHON_SIGINT (anything Pythonically true, i.e., any non-empty
    string, will evaluate as True).

    If exc_trace is True, any other exception will show a stack
    trace.  If False, the stack trace will be sent to a file
    instead, except for SIGPIPE cases (where it is simply
    discarded).  If None (the default), it is set from
    PYTHON_DEBUG, similar to KeyboardInterrupt handling.

    In any case, signals (specifically SIGINT and SIGPIPE) that
    were caught and translated into an exception, are translated
    back to a signal-style exit, so as to make this a well behaved
    Unix utility.
    """

    if sys.argv:
        progname = os.path.basename(sys.argv[0])
        if progname.endswith('.py') and len(progname) > 3:
            progname = progname[:-3]
    else:
        progname = 'python-script'

    if interrupt_trace is None:
        interrupt_trace = os.environ.get('PYTHON_SIGINT', False)
    if exc_trace is None:
        exc_trace = os.environ.get('PYTHON_DEBUG', False)

    ret, err1, err2 = None, None, None

    try:
        ret = func()
    except SystemExit as err:
        ret = err.code
    except:
        err1 = sys.exc_info()
    finally:
        # This may also cause broken pipe or get interrupted (or
        # do all kinds of things if sys.stdout has been wrapped).
        try:
            sys.stdout.flush()
        except SystemExit as err:
            ret = err.code  # should we keep any earlier SystemExit val?
        except:
            err2 = sys.exc_info()

    pipe1, intr1, err1 = _split_err(err1)
    pipe2, intr2, err2 = _split_err(err2)

    _show_err(intr1, interrupt_trace, False, progname)
    _show_err(pipe1, exc_trace, False, progname)
    _show_err(err1, exc_trace, True, progname)

    _show_err(intr2, interrupt_trace, False, progname)

    # These have no traceback so say something first.
    prefix = 'In final sys.stdout.flush():\n'
    _show_err(pipe2, exc_trace, False, progname, prefix)
    _show_err(err2, exc_trace, True, progname, prefix)

    if intr1 or intr2:
        ret = sigdie(signal.SIGINT)
    if pipe1 or pipe2:
        ret = sigdie(signal.SIGPIPE)
    sys.exit(ret)
