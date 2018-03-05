from IndicoWp.controller import Controller


if __name__ == '__main__':

    try:
        controller = Controller()
        controller.post_observed_events()
    finally:
        controller.close()
