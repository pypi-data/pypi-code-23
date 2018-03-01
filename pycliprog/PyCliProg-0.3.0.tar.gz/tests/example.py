#! /usr/bin/env python3


from pycliprog import Prog, ExitFailure


class TestProg(Prog):
    def main(self):
        if self.args.fail:
            self.logger.warning('Raising exception...')
            raise ExitFailure('Something went wrong!')
        self.logger.info('Reporting status...')
        print('Everything is operational!')

    def add_args(self):
        self.parser.add_argument('-f', '--fail',
                                 action='store_true',
                                 help='fail')


if __name__ == '__main__':
    TestProg().start()
