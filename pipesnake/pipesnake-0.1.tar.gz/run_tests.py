# -*- coding: utf-8 -*-

import nose


def main():
    return not nose.run(defaultTest='', argv=['', '--processes=1', '--verbose', '--process-timeout=90'])


if __name__ == '__main__':
    main()
