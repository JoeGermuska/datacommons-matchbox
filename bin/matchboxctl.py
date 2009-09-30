#!/usr/bin/env python

"""
    script to start and stop the matchbox processes
"""

from optparse import OptionParser
import os
import signal
import subprocess
import sys

def pid_exists(pid):
    ''' based on example from http://mail.python.org/pipermail/python-list/2002-May/144522.html '''
    try:
        os.kill(pid, 0)
        return True
    except OSError, err:
        return err.errno == os.errno.EPERM

def check_pidfile(fname):
    if os.path.exists(fname):
        pid = int(open(fname).read())
        exists = pid_exists(pid)
        if not exists:
            os.remove(fname)
            return None
        else:
            return pid
    else:
        return None

def controlled_launch(args, progname, logdir, wait=False):
    if check_pidfile(progname+'.pid'):
        print progname, 'is already running'
    else:
        err = open(os.path.join(logdir, progname+'.err'), 'w')
        out = open(os.path.join(logdir, progname+'.out'), 'w')
        proc = subprocess.Popen(args, stdout=out, stderr=err)
        print progname, 'started with pid', proc.pid
        open(progname+'.pid', 'w').write(str(proc.pid))
        if wait:
            proc.wait()

def kill_pidfile(pidfile):
    pid = check_pidfile(pidfile)
    if pid:
        print 'killing %s (pid=%s)...' % (pidfile[0:-4], pid)
        os.kill(pid, signal.SIGTERM)
        os.remove(pidfile)

def start(options):
    if options.mongo:
        args = ['mongod', '--dbpath', options.mongo]
        if options.quiet:
            args.append('--quiet')
        controlled_launch(args, 'mongo', options.logdir)

    if options.sphinx:
        args = ['searchd', '--config', options.sphinx]
        controlled_launch(args, 'sphinx', options.logdir)

def stop(options):
    if options.mongo:
        kill_pidfile('mongo.pid')
    if options.sphinx:
        kill_pidfile('sphinx.pid')

def status(options):
    m_pid = check_pidfile('mongo.pid')
    if m_pid:
        print 'mongodb is running (pid=%s)' % m_pid
    else:
        print 'mongodb is not running'
    s_pid = check_pidfile('sphinx.pid')
    if s_pid:
        print 'sphinx is running (pid=%s)' % s_pid
    else:
        print 'sphinx is not running'

def reindex(options):
    args = ['indexer', '--config', options.sphinx, '--all']
    if options.rotate:
        args.append('--rotate')
    controlled_launch(args, 'indexer', options.logdir, wait=True)
    kill_pidfile('indexer.pid')

def main():
    parser = OptionParser()
    parser.add_option('--mongo', dest='mongo', default='data/mongo', 
                      metavar='MONGO_DBPATH',
                      help='set path to mongo database [./data/mongo]')
    parser.add_option('--nomongo', action='store_false', dest='mongo',
                      help='do not start mongo instance')
    parser.add_option('--sphinx', dest='sphinx', default='etc/sphinx.conf',
                      metavar='SPHINX_CONF',
                      help='set path to sphinx.conf [./sphinx.conf]')
    parser.add_option('--nosphinx', action='store_false', dest='sphinx',
                      help='do not start sphinx instance')
    parser.add_option('--rotate', dest='rotate', action='store_true',
                      help='rotate sphinx indexes on running instance (only used with reindex)')
    parser.add_option('--logdir', dest='logdir', default='log',
                      help='set log directory [./log/]')
    parser.add_option('-q', '--quiet', dest='quiet', action='store_true',
                      help='run mongo in quiet mode')
    options, args = parser.parse_args()

    cmd = args[0] if len(args) else None
    if cmd == 'start':
        start(options)
    elif cmd == 'stop':
        stop(options)
    elif cmd == 'restart':
        stop(options)
        start(options)
    elif cmd == 'status':
        status(options)
    elif cmd == 'reindex':
        reindex(options)

    else:
        print 'Usage: ./script start|stop|restart|status|reindex [args]'


if __name__ == '__main__':
    main()
