"""VirtuinBridge shall be used to launch Virtuin-based tests from Anduin."""

from __future__ import print_function
import json
import tempfile
import os
import urllib2
import base64
from . import virtuinglobalstubs as anduinFuncStubs

ANDUIN_GLOBAL_STUBS = dict()
for name in dir(anduinFuncStubs):
    if name.startswith('_'):
        continue
    attr = getattr(anduinFuncStubs, name, None)
    ANDUIN_GLOBAL_STUBS[name] = attr

try:
    from System.Diagnostics import Process
    __VIRT_ANDUIN_ENV__ = True
# pylint: disable=bare-except
except:
    __VIRT_ANDUIN_ENV__ = False
    from subprocess import Popen, PIPE

if __VIRT_ANDUIN_ENV__:
    def _runCommand(args, inputStr=None):
        """
        Runs child process using .NET Process.
        Args:
            args (list: str): Command arguments w/ first
            being executable.
            inputStr (str, None): Standard input to pass in.
        Returns:
            str: Standard output
            str: Standard error
            int: Process exit code
        """
        p = Process()
        have_stdin = inputStr is not None
        p.StartInfo.UseShellExecute = False
        p.StartInfo.RedirectStandardInput = have_stdin
        p.StartInfo.RedirectStandardOutput = True
        p.StartInfo.RedirectStandardError = True
        p.StartInfo.FileName = args[0]
        p.StartInfo.Arguments = " ".join(args[1:])
        p.Start()
        if have_stdin:
            p.StandardInput.Write(inputStr)
        p.WaitForExit()
        stdout = p.StandardOutput.ReadToEnd()
        stderr = p.StandardError.ReadToEnd()
        return stdout, stderr, p.ExitCode

else:
    def _runCommand(args, inputStr=None):
        """
        Runs child process using built-in subprocess.
        Args:
            args (list: str): Command arguments w/ first
            being executable.
            inputStr (str, None): Standard input to pass in.
        Returns:
            str: Standard output
            str: Standard error
            int: Process exit code
        """
        p = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate(inputStr)
        return stdout, stderr, p.returncode


def _net2dict(obj):
    """
    Converts .NET object public primitive attributes to python dict.
    .NET bool gets mapped to str due to IronPython compatibility issue.
    Function performs only shallow mapping (non-recursive).
    Args:
        obj (.Net object): .Net object
    Returns:
        dict: converted python dict
    """
    attrs = (name for name in dir(obj) if not name.startswith('_') and
             _isPrimitive(obj.__getattribute__(name)))
    objDict = dict()
    for attribute in attrs:
        val = obj.__getattribute__(attribute)
        # IronPython json uses incorrect boolean so change to string
        val = str(val) if isinstance(val, bool) else val
        objDict[attribute] = val
    return objDict

def _isPrimitive(var):
    """
    Determines if supplied var is a primitive.
    (int, float, bool, str)
    Args:
        var: variable to check
    Returns:
        bool: True if primitive, False otherwise
    """
    return isinstance(var, (int, float, bool, str))


def _getAnduinConfigs(anduinGlobals):
    """
    Extracts Anduin configs that are injected globally including
    slot, slot.Dut, station, and TestSpecs
    Args:
        None
    Returns:
        dict: Python dict with keys dut, station, and specs.
    """
    configs = dict(dut={}, station={}, specs={})
    if __VIRT_ANDUIN_ENV__:
        lclDut = _net2dict(anduinGlobals['slot'].Dut)
        configs['dut'].update(lclDut)
        lclStation = _net2dict(anduinGlobals['station'])
        kvKey = 'translateKeyValDictionary'
        stationConstants = anduinGlobals[kvKey](anduinGlobals['station'].Constants)
        lclStation.update(stationConstants)
        configs['station'].update(lclStation)
        for specName, specDict in anduinGlobals['TestSpecs'].iteritems():
            fullSpecDict = dict(lsl=None, usl=None, details='')
            fullSpecDict.update(specDict.copy())
            if "counts_in_result" in fullSpecDict:
                # IronPython json uses incorrect boolean so change to string
                fullSpecDict["counts"] = str(fullSpecDict["counts_in_result"])
            configs['specs'][specName] = fullSpecDict
    else:
        configs['dut'] = anduinGlobals.get('dut', {})
        configs['specs'] = anduinGlobals.get('specs', {})
        configs['station'] = anduinGlobals.get('station', {})
    return configs


def _processTestResult(result, anduinGlobals):
    rstType = result.get('type', '').lower()
    rstName = result.get('name', None)
    rstUnit = result.get('unit', None)
    rstValue = result.get('value', None)
    rstDisplay = result.get('display', False)
    if rstType == 'blob':
        value = rstValue if isinstance(rstValue, str) else base64.encodestring(rstValue)
        anduinGlobals['AddResultBlob'](rstName, rstUnit, value)
    elif rstType == 'text':
        anduinGlobals['AddResultText'](rstName, rstUnit, rstValue, rstDisplay)
    elif rstType == 'scalar':
        anduinGlobals['AddResultScalar'](rstName, rstUnit, rstValue, rstDisplay)
    elif rstType == 'list':
        anduinGlobals['AddResultList'](rstName, rstUnit, rstValue)
    elif rstType == 'file':
        if isinstance(rstValue, (str, unicode)):
            anduinGlobals['AddResultText'](rstName, 'Link', '{0}'.format(rstValue))
        elif isinstance(rstValue, dict):
            srcURL = rstValue.get('src')
            dstPath = rstValue.get('dst')
            dstFolder = os.path.dirname(dstPath)
            if not os.path.exists(dstFolder):
                os.makedirs(dstFolder)
            with open(dstPath, 'wb') as fp:
                fp.write(urllib2.urlopen(srcURL).read())
            anduinGlobals['AddResultText'](rstName, 'Link', str.format('{:s}', dstPath))
        else:
            raise Exception('result file value must be either string or dict.')
    elif rstType == 'flush':
        anduinGlobals['FlushMetrics']()
    elif rstType == 'channel':
        anduinGlobals['SetChannel'](rstValue)


def _processTestResults(results, anduinGlobals):
    error = None
    results = results if isinstance(results, list) else [results]
    for result in results:
        try:
            _processTestResult(result, anduinGlobals)
        # pylint: disable=broad-except
        except Exception as err:
            error = err
    return error


def getTestConfigs(testConfigs, anduinGlobals=None):
    """
    Combines injected Anduin globals with supplied test config.
    Anduin globals override test config.
    Args:
        testConfigs (dict): Test configs {dut:{}, specs:{}, station:{}}
    Returns:
        dict: Merged dict with keys dut, station, and specs.
    """
    lclAnduinGlobals = ANDUIN_GLOBAL_STUBS.copy()
    lclAnduinGlobals.update(anduinGlobals or {})
    anduinConfigs = _getAnduinConfigs(lclAnduinGlobals)
    totalConfigs = testConfigs.copy()
    totalConfigs['dut'] = totalConfigs.get('dut', dict())
    totalConfigs['specs'] = totalConfigs.get('specs', dict())
    totalConfigs['station'] = totalConfigs.get('station', dict())
    totalConfigs['dut'].update(anduinConfigs.get('dut', {}))
    totalConfigs['specs'].update(anduinConfigs.get('specs', {}))
    totalConfigs['station'].update(anduinConfigs.get('station', {}))
    return totalConfigs


def runVirtuinTest(testConfigs, anduinGlobals=None):
    """
    Runs Virtuin based test given supplied configs.
    Returns all results returned by test.
    Args:
        testConfigs (dict): Test configs {dut:{}, specs:{}, station:{}}
    Returns:
        str|None: Error message or None
        list: Results list of dict objects
    """
    lclAnduinGlobals = ANDUIN_GLOBAL_STUBS.copy()
    lclAnduinGlobals.update(anduinGlobals or {})
    # Create I/O files for Virtuin test
    tmpPath = testConfigs['station'].get("TEMP_PATH", None)
    testConfigPath = tempfile.mktemp(dir=tmpPath, suffix='.json')
    testResultsPath = tempfile.mktemp(dir=tmpPath, suffix='.json')
    print('[VB] Test input file: {0}'.format(testConfigPath))
    print('[VB] Test output file: {0}'.format(testResultsPath))
    errcode = 0
    stdout = ''
    stderr = ''
    # Write test configs to file
    with open(testConfigPath, 'w') as fp:
        json.dump(testConfigs, fp, skipkeys=True, ensure_ascii=True)
    # Run test and block until complete
    virtuinCore = os.environ.get('VirtuinCore', 'VirtuinCore')
    testCmd = [virtuinCore, testConfigPath, testResultsPath]
    stdout, stderr, errcode = _runCommand(args=testCmd, inputStr=None)
    results = None
    error = None
    if errcode != 0:
        results = None
        error = 'Failed to spawn test w/ code {0}.\nstdout: {1}.\nstderr: {2}.'.format(
            errcode, stdout, stderr)
    else:
        try:
            with open(testResultsPath, 'r') as fp:
                results = json.load(fp)
            error = _processTestResults(results, lclAnduinGlobals)
        # pylint: disable=broad-except
        except Exception as err:
            error = err
    if __VIRT_ANDUIN_ENV__:
        os.remove(testConfigPath)
        os.remove(testResultsPath)
    return error, results
