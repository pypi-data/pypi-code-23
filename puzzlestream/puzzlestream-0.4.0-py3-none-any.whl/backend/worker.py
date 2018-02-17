# -*- coding: utf-8 -*-
"""Background worker module.

contains PSWorker
"""

import importlib as imp
import multiprocessing as mp
import os
import random
import string
import sys
import traceback
from time import sleep, time

import numpy as np
import psutil
from puzzlestream.backend.signal import PSSignal


class PSWorker:
    """Background worker class.

    Every Puzzle Stream module has exactly one worker that does all the heavy
    lifting in a background process without blocking the UI.
    """

    def __init__(self, workerRegistrationFunction, startTimerFunction):
        """Worker init.

        Args:
            workerRegistrationFunction (method): Method to enqueue the worker.
            startTimerFunction (method): Method to start the polling timer.
        """
        self.__process, self.__conn = None, None
        self.__finished = PSSignal()
        self.__newStdout = PSSignal()
        self.__progressUpdate = PSSignal()
        self.__name, self.__path, self.__libs = None, None, None
        self.__workerRegistration = workerRegistrationFunction
        self.__startTimer = startTimerFunction
        self.__id = None
        self.__queue = mp.Queue()

    def __getstate__(self):
        return (self.__name, self.__path, self.__libs)

    def __setstate__(self, state):
        self.__name, self.__path, self.__libs = state

    @property
    def finished(self):
        """Signal that is emitted when the worker has finished (PSSignal)."""
        return self.__finished

    @property
    def newStdout(self):
        """Signal that is emitted when there is new output (PSSignal)."""
        return self.__newStdout

    @property
    def progressUpdate(self):
        """Signal that is emitted when progress has changed (PSSignal)."""
        return self.__progressUpdate

    def setName(self, name):
        """Set the name of the worker."""
        self.__name = name

    def setPath(self, path):
        """Set the worker file path."""
        self.__path = path

    def setLibs(self, libs):
        """Pass libs to be made available inside the background process."""
        self.__libs = libs

    def enqueue(self, streamSection, currentID, lastID):
        """Enqueue worker to be executed whenever there is a free slot."""
        self.__streamSection = streamSection
        self.__id, self.__lastID = currentID, lastID
        self.__workerRegistration(self.__id, self)
        self.__startTimer()

    def run(self):
        """Run worker in background process."""
        self.__process = mp.Process(
            target=self._calculate,
            args=(self.__queue, self.__streamSection,
                  self.__id, self.__lastID)
        )

        self.__startTimer()
        self.__process.start()

        while not self.__process.is_alive():
            sleep(0.01)

    def __importModule(self):
        """Import and return module that holds the code to be executed."""
        for lib in self.__libs:
            if lib not in sys.path:
                sys.path.append(lib)
        spec = imp.util.spec_from_file_location(self.__name, self.__path)
        mod = imp.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def poll(self):
        """Poll worker and see if there is new output or if it has finished."""
        if not self.__queue.empty():
            result = self.__queue.get()

            if isinstance(result, str):
                self.newStdout.emit(result)
            elif isinstance(result, float):
                self.progressUpdate.emit(result)
            else:
                self.finish(result)

    def finish(self, result):
        """Run some finalising procedure when the worker has finished."""
        self.__process.join()
        self.__workerRegistration(self.__id, self)
        self.__process = None
        self.finished.emit(*result)

    def _calculate(self, queue, streamSec, currentID, lastID):
        """Actual background task, run in seperate process.

        Args:
            queue (mp.Queue): Queue to pass data to the main process.
            streamSec (PSStreamSection): Current stream section.
            currentID, lastID (int): Current and previous module IDs.
        """
        self.__curStdout, self.__lastOutSendTime = "", time()

        def sendPrint(*args, sep=" ", end="\n"):
            sep = str(sep)

            # acquire some output in 10 ms interval and pass it to the main
            # process as one block
            for a in args:
                self.__curStdout += str(a) + sep
            self.__curStdout += end

            if time() > self.__lastOutSendTime + 0.01:
                queue.put(self.__curStdout)
                self.__curStdout, self.__lastOutSendTime = "", time()

        def progressUpdate(finished, total=None):
            if total is None and isinstance(finished, float):
                if finished < 0:
                    finished = 0
                elif finished > 1:
                    finished = 1
                queue.put(finished)
            else:
                finished = finished / total
                progressUpdate(finished)

        np.random.seed(int.from_bytes(os.urandom(4), "big"))

        runtime, savetime, testResults = 0, 0, {}

        try:
            mod = self.__importModule()
            os.chdir(os.path.dirname(mod.__file__))

            mod.print = sendPrint
            mod.progressUpdate = progressUpdate

            inp = streamSec.data

            t0 = time()
            out = mod.main(inp)
            runtime = time() - t0
            log = out.changelog

            t0 = time()
            inp.update(out)
            streamSec.updateData(lastID, inp, log, clean=True)
            savetime = time() - t0

            success, output = True, ""

            if "testFunctions" in dir(mod):
                if isinstance(mod.testFunctions, list):
                    for func in mod.testFunctions:
                        result = getattr(mod, func)(out)

                        if isinstance(result, bool):
                            testResults[func] = result

            del out

        except Exception as e:
            message = traceback.format_exc()
            success, log, output = False, [], message

        times = [runtime, savetime]

        queue.put(self.__curStdout)
        queue.put([success, streamSec.changelog, output, times, testResults])

    def pause(self):
        """Pause the current process."""
        if self.__process is not None:
            p = psutil.Process(self.__process.pid)
            p.suspend()
        else:
            return False
        return True

    def resume(self):
        """Resume the current process."""
        if self.__process is not None:
            p = psutil.Process(self.__process.pid)
            p.resume()
        else:
            return False
        return True

    def stop(self):
        """Terminate the current process."""
        if self.__process is not None:
            self.__process.terminate()
        else:
            return False
        return True
