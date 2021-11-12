import argparse
import os, sys

from system import SystemMain
import system

if __name__ == "__main__":
    py_ver = int(sys.version[0])
    if py_ver == 2:
        # python2 here has signal registration and obj inheritance issue.
        print('use python3 to execute, program exited.')
        sys.exit(0)

    parser = argparse.ArgumentParser(description='OPCUA Server')
    parser.add_argument('-d', '--daemonize', action='store_true', help='turn this process into a daemon')
    parser.add_argument('-l', '--log-level', default="warning", help='{debug | info | warning | error | critical}' )
    parser.add_argument('-lc', '--log-classes', default="", help="provides class names in form 'CLASS_NAME:LOG-LEVEL' as comma seperated list. i.e., MYDB:debug,MYTABLE:warn" )
    parser.add_argument('-re', '--reload-excel', action='store_true', help='reload excel and csv to INI config file')

    args = parser.parse_args()
    if args.daemonize:
        try:
            pid = os.fork()
            if pid > 0: # Parent process exit
                sys.exit(0)
            elif pid == 0:
                # set as session leader and de-couple from parent environment
                os.setsid()
                os.umask(0o002)
                #os.chdir('/')

                # redirect stdin, stdout and strerr to /dev/null
                sys.stdin  = open('/dev/null', 'r')
                sys.stdout = open('/dev/null', 'w')
                sys.stderr = open('/dev/null', 'w')

        except OSError as err:
            print(f"({err.errno}) {err.strerror}")
            sys.exit(1)
            
    system = SystemMain( args )
    system.loop()

    print('\n(PID {}) OPCUA Server terminated by interrupt, bye-bye.'.format(os.getpid()))

