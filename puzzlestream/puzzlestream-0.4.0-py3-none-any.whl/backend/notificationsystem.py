# -*- coding: utf-8 -*-
"""Notification system module.

Usage:
- Add reation methods that are executed when a new notification arrives
  using addReactionMethod; The message is directly passed to each and
  every method.
- Throw a new notification using newNotification; the message is passed to the
  reactionMethods.
- If needed, remove methods again using removeReactionMethod.
"""

reactionMethods = []


def addReactionMethod(method):
    """Add method to reaction methods executed when on notification."""
    reactionMethods.append(method)


def removeReactionMethod(method):
    """Remove method from reactionMethods."""
    i = reactionMethods.index(method)
    del reactionMethods[i]


def newNotification(message):
    """Throw new notification."""
    for m in reactionMethods:
        m(message)
