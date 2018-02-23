# -*- coding: utf-8 -*-
# Description: Implements an Observable class that can be added
#              simply to another class.
#              https://en.wikipedia.org/wiki/Observer_pattern
# Author: Hywel Thomas

import logging_helper
from pprint import pformat
from .decorators import deprecated

logging = logging_helper.setup_logging()


class ObserverError(Exception):
    pass


class Observable(object):

    def __initialise_if_required(self):

        try:
            self.observers

        except AttributeError:
            # First observer, initialise the list
            self.observers = []
            self.notified_kwargs = {}

    def register_observer(self,
                          observer):
        logging.debug(u'Register: {o} to {n}'.format(o=observer.__class__,
                                                     n=self.__class__))
        self.__initialise_if_required()

        try:
            observer.notification

        except AttributeError:
            try:
                # TODO: Temporary check until notify deprecated (notify deprecation added 2018-01-30)
                observer.notify

            except AttributeError:
                raise ObserverError(u'{observer} does not have a notification method.'.format(observer=observer))

        self._initial_notification(observer)
        self.observers.append(observer)

    def unregister_observer(self,
                            observer):
        logging.debug(u'Unregister: {o} from {n}'.format(o=observer.__class__,
                                                         n=self.__class__))
        self.__initialise_if_required()
        self.observers.remove(observer)

    def _initial_notification(self,
                              observer):

        """ Override to perform a custom initial notify.

        If not overridden this will pass previous status of all params passed
        for this object.

        :return:
        """

        kwargs = self.notified_kwargs

        logging.debug(u'Initial Notify kwargs:\n'
                      u'{kwargs}'.format(kwargs=pformat(kwargs)))

        # TODO: Temporary try except until notify deprecated (notify deprecation added 2018-01-30)
        # Required for cases where Class does not inherit Observer!
        try:
            observer.notification(notifier=self,
                                  **kwargs)

        except AttributeError:
            observer.notify(notifier=self,
                            **kwargs)
            logging.warning(u'Observer does not inherit Observer class: {o}'.format(o=observer))

    def notify_observers(self,
                         **kwargs):
        self.__initialise_if_required()

        self.notified_kwargs.update(kwargs)

        logging.debug(u'Notify kwargs:\n'
                      u'{kwargs}'.format(kwargs=pformat(kwargs)))

        exceptions = []
        for observer in self.observers:
            try:
                try:
                    # TODO: Temporary try except until notify deprecated (notify deprecation added 2018-01-30)
                    # Required for cases where Class does not inherit Observer!
                    observer.notification(notifier=self,
                                          **kwargs)

                except AttributeError:
                    observer.notify(notifier=self,
                                    **kwargs)
                    logging.warning(u'Observer does not inherit Observer class: {o}'.format(o=observer))

            except Exception as err:
                exceptions.append(err)
                logging.exception(err)
                # Maybe remove the observer if an exception has occurred?

        if exceptions:
            raise exceptions[-1]


class Observer(object):

    NOTIFIER_KEY = u'notifier'

    # TODO: Deprecate in favour of notification (notify deprecation added 2018-01-30)
    #       (Better to have single case of confusing observer.notification
    #        hidden in notify_observers)
    @deprecated
    def notify(self,
               **kwargs):
        pass

    def notification(self,
                     **kwargs):
        # TODO: Remove this when notify is removed (notify deprecation added 2018-01-30)
        self.notify(**kwargs)


class ObservableMixIn(Observable):
    pass


class ObserverMixIn(Observer):
    pass


class ObservableObserverMixIn(ObservableMixIn,
                              ObserverMixIn):
    pass
