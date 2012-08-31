
import sys
import argparse
import logging


from PyQt4.QtGui import QApplication, QIcon

from gui import MainWindow






def main():

    app = QApplication(sys.argv)


    args = app.arguments()

    args = map(str, args)

    config = parse_args(args[1:])

    if config['verbose'] > 0:
        logging.basicConfig(level=logging.DEBUG)

    win = MainWindow(config)

    win.setFixedSize(600, 400)
    win.setWindowTitle('BrytonOffline')
    win.setWindowIcon(QIcon('img/bryton_logo.jpg'))
    win.show()

    return app.exec_()



def parse_args(args):

    p = argparse.ArgumentParser(description='BrytonOffline')

    p.add_argument('--server-host', nargs='?', default='localhost',
                help='''Hostname/ip of the internal server. The default is "localhost". Only usefull if you are
                running BrytonBridge on a virtual machine.''')

    s = p.add_argument_group('strava')
    s.add_argument('--strava-email', nargs='?', help='''Your strava.com email''')
    s.add_argument('--strava-password', nargs='?', help='''Your strava.com password''')
    s.add_argument('--strava-auth-token', nargs='?', help='''A valid strava.com authentication token''')

    s = p.add_argument_group('brytonsport')
    s.add_argument('--bryton-email', nargs='?', help='''Your brytonsport.com email''')
    s.add_argument('--bryton-password', nargs='?', help='''Your brytonsport.com password''')
    s.add_argument('--bryton-session-id', nargs='?', help='''A valid brytonsport.com session id''')


    p.add_argument('--verbose', '-v', action='count', help='Enable debugging messages')

    return vars(p.parse_args(args))


if __name__ == '__main__':

    sys.exit(main())
