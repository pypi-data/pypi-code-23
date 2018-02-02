import gym
import argparse
import logging
import os
from time import sleep, time
from bonsai_ai import Simulator, Brain, Config
import sys

# log = logging.getLogger(__name__)
log = logging.getLogger('gym_simulator')


class GymSimulator(Simulator):
    """ GymSimulator class

        End users should subclass GymSimulator to interface OpenAI Gym
        environments to the Bonsai platform. A minimal subclass must
        implement `gym_to_state()` and `action_to_gym()`, as well as
        specify the `simulator_name` and `environment_name`.

        To start the simulation for training, call `run_gym()`.
    """
    simulator_name = None    # name of the simulation in the inkling file
    environment_name = None  # name of the OpenAI Gym environment

    def __init__(self, brain):
        """ initialize the GymSimulator with a bonsai.Config,
            the class variables will be used to setup the environment
            and simulator name as specified in inkling
        """
        super(GymSimulator, self).__init__(brain, self.simulator_name)

        # create the gym environment
        self._env = gym.make(self.environment_name)

        # parse optional command line arguments
        cli_args = self._parse_arguments()
        if cli_args is None:
            return

        # optional parameters for controlling the simulation
        self._headless = cli_args.headless
        self._episode_length = 0    # no limit

        # book keeping for rate status
        self._log_interval = 10.0  # seconds
        self._gym_total_reward = 0
        self._iteration_count = 0
        self._episode_count = 0
        self._last_status = time()
        self._last_iterations = 0

    # convert openai gym observation to our state schema
    def gym_to_state(self, observation):
        """Convert a gym observation into an Inkling state

        Example:
            state = {'position': observation[0],
                     'velocity': observation[1],
                     'angle':    observation[2],
                     'rotation': observation[3]}
            return state

        :param observation: gym observation, see specific gym
            environment for details.
        :return A dictionary matching the Inkling state schema.
        """
        return None

    # convert our action schema into openai gym action
    def action_to_gym(self, action):
        """Convert an Inkling action schema into a gym action.

        Example:
            return action['command']

        :param action: A dictionary as defined in the Inkling schema.
        :return A gym action as defined in the gym environment
        """
        return action['command']

    def episode_start(self, parameters):
        """ called at the start of each new episode
        """
        self._episode_count += 1

        # initial observation
        observation = self._env.reset()
        state = self.gym_to_state(observation)
        return state

    def simulate(self, action):
        """ step the simulation, optionally rendering the results
        """
        # simulate
        self._iteration_count += 1
        gym_action = self.action_to_gym(action)
        observation, reward, done, info = self._env.step(gym_action)

        # for logging
        self._gym_total_reward += reward

        # render if not headless
        if not self._headless:
            if 'human' in self._env.metadata['render.modes']:
                self._env.render()

        # reset if we finished this episode
        if done:
            # log how this episode went
            log.info("Episode %s reward is %s",
                     self._episode_count, self._gym_total_reward)
            self._last_status = time()
            self._gym_total_reward = 0.0

            # reset the openai-gym env
            self._env.reset()

        # print a periodic status of iterations and episodes
        self._periodic_status_update()

        # convert state and return to the server
        state = self.gym_to_state(observation)
        return state, reward, done

    def standby(self, reason):
        """ report standby messages from the server
        """
        log.info('standby: %s', reason)
        sleep(1)
        return True

    def run_gym(self):
        """ runs the simulation until cancelled or finished
        """
        # update brain to make sure we're in sync
        self.brain.update()

        # train
        while self.run():
            continue

        # success
        log.info('Finished running %s', self.name)

    def _periodic_status_update(self):
        """ print a periodic status update showing iterations/sec
        """
        if time() - self._last_status > self._log_interval:
            ips = ((self._iteration_count - self._last_iterations) /
                   self._log_interval)
            log.info("Episode %s is still running, reward so far is %s",
                     self._episode_count, self._gym_total_reward)
            self._last_status = time()
            self._last_iterations = self._iteration_count

    def _parse_arguments(self):
        """ parses command line arguments and returns them as a list
        """
        headless_help = (
            "The simulator can be run with or without the graphical "
            "environment. By default the graphical environment is shown. "
            "Using --headless will run the simulator without graphical "
            "output. This may be set as BONSAI_HEADLESS in the environment.")
        parser = argparse.ArgumentParser()
        parser.add_argument('--headless',
                            help=headless_help,
                            action='store_true',
                            default=os.environ.get('BONSAI_HEADLESS', False))
        try:
            args, unknown = parser.parse_known_args()
        except SystemExit:
            # --help specified by user. Continue, so as to print rest of help
            # from (brain_server_connection).
            print('')
            return None
        return args
