import pyximport; pyximport.install()
from luaparser.utils import tests
from luaparser import asttokens
from luaparser.astnodes import *
import textwrap
from luaparser import ast

class VariablesTestCase(tests.TestCase):
    def test_global_var(self):
        tree = ast.parse(textwrap.dedent("""   
--- Local application model
--- @classmod Model
import "Overkiz.utilities"
import "Overkiz.Kizbox"
import "Overkiz.Subject"
import "Overkiz.TableStorage"
import "Overkiz.HomeAutomation.Local.storage"
import "Overkiz.HomeAutomation.Local.log"
import "Overkiz.HomeAutomation.Local.resync"

--- @field _devices string
--- @field protected _requestArgs TableStorage
--- @field public pairedMode boolean
--- @field public deviceNotifier
--- @field public events table
--- @field public driver table
--- @field public gateway table
--- @field public SUPPORTED_PROTOCOLS table
--- @return Model
local Model = class();

-- public constants
-- ----------------
Model.SUPPORTED_PROTOCOLS = {"io", "ovp", "enocean", "rts", "rtn"}

--- Constructor
--- @tparam string boxID box serial number
function Model:new(boxID)
  -- public fields
  -- -------------
  self.pairedMode     = false
  self.deviceNotifier = Subject() -- to notify new device.
  self.events         = {}
  self.driver         = {}
  self.gateway        = boxID

  -- private fields
  -- --------------
  self._devices = TableStorage.subStorage(storage, "devices")
  self._deviceSetup     = {}
end

-- private methods
-- ---------------
--- Update local storage and setup with the new label
--- @tparam string url device's url
--- @tparam string label new label
--- @return boolean true if cloudLink notified
local function updateLocalAndSetup(self, url, label)
  local notifCloud    = false
  local deviceSetup   = self._deviceSetup[url]
  local localDevice   = self._devices[url]

  if not deviceSetup and not localDevice then
    return -- nothing to merge
  elseif not localDevice then
    self._devices[url] = {label=label, synced=false}
    notifCloud = true -- need to notify cloud
    log:notice("Local device '"..url.."' created by driver.")
  else -- localDevice already exists.
    if deviceSetup then
      notifCloud = true
      if (label ~= nil) and (localDevice.label ~= label) and (not localDevice.fromCloud) then
        -- device coming from protocol, update label and send resync flag.
        localDevice.label = label
        self._devices[url] = localDevice -- write in storage
        log:notice("Local device '"..url.."' updated by driver.")
      else
        deviceSetup.label = localDevice.label
        log:notice("Device setup '"..url.."' updated by local.")
      end
    end
  end

  -- do not fire notif. if local device already synced (rest api locked):
  if (notifCloud) and (localDevice==nil or not localDevice.synced) then
    if self.events.deviceUpdatedEvent then
      self.events.deviceUpdatedEvent({deviceURL = url});
    end
    resync:update()
    self.deviceNotifier:notify(self._deviceSetup[url])
    log:notice("Device '"..url.."' has been updated. Sending resync flag.")
  end
  return notifCloud
end

--- Add local information to a high level device:
---   * label : Device name
---   * sync  : Is device synced with server
--- (return a copy of passed device)
--- @tparam self self instance (private)
--- @tparam table device device to enhance
--- @function enhanceDevice
--- @treturn table enhanced device
local function enhanceDevice(self, device)
  local localDevice = self._devices[device.deviceURL]
  if not localDevice then
    return device
  else
    local ret  = ovk.tableDeepCopy(device)
    ret.label  = localDevice.label
    ret.synced = localDevice.synced
    return ret
  end
end


-- public methods
-- --------------
--- Add or update a device definition (url + label) comming from the cloud
--- @tparam string url device's url
--- @tparam string label new label
--- @return boolean true if cloudLink notified
function Model:addOrUpdateDevFromCloud(url, label)
  local localDevice  = self._devices[url]
  if localDevice then -- update.
    localDevice.label = label
    self._devices[url] = localDevice
    log:notice("Local device '"..url.."' updated by cloud.")
  else -- create.
    if label then
      self._devices[url] = {label=label, synced=false, fromCloud=true}
    else
      self._devices[url] = {synced=false, fromCloud=true}
    end
    log:notice("Local device '"..url.."' created by cloud.")
  end
  return updateLocalAndSetup(self, url, label)
end

--- Add or update a device model (setup) comming from the protocol
--- @tparam string setup device's setup
--- @return boolean true if cloudLink notified
function Model:addOrUpdateDevFromProto(setup)
  local notifCloud = false
  local v, r = ovk.checkPath(setup, {deviceURL = "string"});
  if not v then
    log:error("Malformed setup argument. ("..tostring(r)..")");
    return
  end

  local newDevice = (self._deviceSetup[setup.deviceURL] == nil)
  local availableChanged = newDevice
  if not newDevice then
    if setup.available ~= nil and self._deviceSetup[setup.deviceURL].available ~= nil then
      availableChanged = (setup.available ~= self._deviceSetup[setup.deviceURL].available)
    end
  end

  self._deviceSetup[setup.deviceURL] = setup -- save device in model
  if newDevice then
    if self.events.deviceCreatedEvent then
      self.events.deviceCreatedEvent({deviceURL = setup.deviceURL})
    end
  end

  notifCloud = updateLocalAndSetup(self, setup.deviceURL, setup.label)
  -- events
  if availableChanged then
    if (setup.available) then
      if self.events.deviceAvailableEvent then
        self.events.deviceAvailableEvent({deviceURL = setup.deviceURL});
      end
    else
      if self.events.deviceAvailableEvent then
        self.events.deviceUnavailableEvent({deviceURL = setup.deviceURL});
      end
    end
  end
  return notifCloud
end

--- Delete a device from both storage and setup
--- @tparam string url device's url
--- @return boolean true if device deleted
function Model:deleteDevice(url)
  if not self._deviceSetup[url] then
    log:warning("Cannot delete inexistant device '"..url.."'.")
    self._devices[url] = nil -- erase storage in any case, to avoid desync device
    return false
  end
  if (self._devices[url] ~= nil) and (self._devices[url].synced) then
    log:notice("Device '"..url.."' deleted by cloud.")
  else
    log:notice("Device '"..url.."' deleted by local API.")
  end
  self._deviceSetup[url]  = nil
  self._devices[url]      = nil
  if self.events.deviceDeletedEvent then
    self.events.deviceDeletedEvent({deviceURL = url})
  end
  return true
end

--- Set a device as synced
--- @tparam string url device's url
--- @tparam boolean synced synced state
--- @return boolean true if device updated
function Model:setSynced(url, synced)
  local devFound = self._devices[url]
  if not devFound then
    log:warning("Trying to set as synced a inexistant device: '"..url.."'.")
    return false
  end
  if not devFound.synced then
    devFound.synced = synced
    self._devices[url] = devFound -- write in storage
    if self.events.deviceUpdatedEvent then
      self.events.deviceUpdatedEvent({deviceURL = url});
    end
    log:notice("Set device '"..url.."' as synced.")
  end
  return true
end

--- Get synced state for a device
--- @tparam string url device's url
--- @return boolean true if synced
function Model:isSynced(url)
  if not self._devices[url] then
    return false
  end
  return self._devices[url].synced
end

--- Get device label
--- @tparam string url device's url
--- @return string device's label
function Model:getLabel(url)
  return self._devices[url].label
end

--- Get device generic model
--- @tparam string url device's url
--- @return table generic model
function Model:getDevice(url)
  local device = self._deviceSetup[url]
  if device ~= nil then
    return enhanceDevice(self, device)
  else
    return nil
  end
end

--- Get all device generic model
--- @return table generic model list
function Model:getDevices()
  local devices = {}
  for url, device in pairs(self._deviceSetup) do
    devices[url] = enhanceDevice(self, device)
  end
  return devices
end

local model = Model(Kizbox.id());

--- Local application model
--- @classmod Model
import "Overkiz.utilities"
import "Overkiz.Kizbox"
import "Overkiz.Subject"
import "Overkiz.TableStorage"
import "Overkiz.HomeAutomation.Local.storage"
import "Overkiz.HomeAutomation.Local.log"
import "Overkiz.HomeAutomation.Local.resync"

--- @field _devices string
--- @field protected _requestArgs TableStorage
--- @field public pairedMode boolean
--- @field public deviceNotifier
--- @field public events table
--- @field public driver table
--- @field public gateway table
--- @field public SUPPORTED_PROTOCOLS table
--- @return Model
local Model = class();

-- public constants
-- ----------------
Model.SUPPORTED_PROTOCOLS = {"io", "ovp", "enocean", "rts", "rtn"}

--- Constructor
--- @tparam string boxID box serial number
function Model:new(boxID)
  -- public fields
  -- -------------
  self.pairedMode     = false
  self.deviceNotifier = Subject() -- to notify new device.
  self.events         = {}
  self.driver         = {}
  self.gateway        = boxID

  -- private fields
  -- --------------
  self._devices = TableStorage.subStorage(storage, "devices")
  self._deviceSetup     = {}
end

-- private methods
-- ---------------
--- Update local storage and setup with the new label
--- @tparam string url device's url
--- @tparam string label new label
--- @return boolean true if cloudLink notified
local function updateLocalAndSetup(self, url, label)
  local notifCloud    = false
  local deviceSetup   = self._deviceSetup[url]
  local localDevice   = self._devices[url]

  if not deviceSetup and not localDevice then
    return -- nothing to merge
  elseif not localDevice then
    self._devices[url] = {label=label, synced=false}
    notifCloud = true -- need to notify cloud
    log:notice("Local device '"..url.."' created by driver.")
  else -- localDevice already exists.
    if deviceSetup then
      notifCloud = true
      if (label ~= nil) and (localDevice.label ~= label) and (not localDevice.fromCloud) then
        -- device coming from protocol, update label and send resync flag.
        localDevice.label = label
        self._devices[url] = localDevice -- write in storage
        log:notice("Local device '"..url.."' updated by driver.")
      else
        deviceSetup.label = localDevice.label
        log:notice("Device setup '"..url.."' updated by local.")
      end
    end
  end

  -- do not fire notif. if local device already synced (rest api locked):
  if (notifCloud) and (localDevice==nil or not localDevice.synced) then
    if self.events.deviceUpdatedEvent then
      self.events.deviceUpdatedEvent({deviceURL = url});
    end
    resync:update()
    self.deviceNotifier:notify(self._deviceSetup[url])
    log:notice("Device '"..url.."' has been updated. Sending resync flag.")
  end
  return notifCloud
end

--- Add local information to a high level device:
---   * label : Device name
---   * sync  : Is device synced with server
--- (return a copy of passed device)
--- @tparam self self instance (private)
--- @tparam table device device to enhance
--- @function enhanceDevice
--- @treturn table enhanced device
local function enhanceDevice(self, device)
  local localDevice = self._devices[device.deviceURL]
  if not localDevice then
    return device
  else
    local ret  = ovk.tableDeepCopy(device)
    ret.label  = localDevice.label
    ret.synced = localDevice.synced
    return ret
  end
end


-- public methods
-- --------------
--- Add or update a device definition (url + label) comming from the cloud
--- @tparam string url device's url
--- @tparam string label new label
--- @return boolean true if cloudLink notified
function Model:addOrUpdateDevFromCloud(url, label)
  local localDevice  = self._devices[url]
  if localDevice then -- update.
    localDevice.label = label
    self._devices[url] = localDevice
    log:notice("Local device '"..url.."' updated by cloud.")
  else -- create.
    if label then
      self._devices[url] = {label=label, synced=false, fromCloud=true}
    else
      self._devices[url] = {synced=false, fromCloud=true}
    end
    log:notice("Local device '"..url.."' created by cloud.")
  end
  return updateLocalAndSetup(self, url, label)
end

--- Add or update a device model (setup) comming from the protocol
--- @tparam string setup device's setup
--- @return boolean true if cloudLink notified
function Model:addOrUpdateDevFromProto(setup)
  local notifCloud = false
  local v, r = ovk.checkPath(setup, {deviceURL = "string"});
  if not v then
    log:error("Malformed setup argument. ("..tostring(r)..")");
    return
  end

  local newDevice = (self._deviceSetup[setup.deviceURL] == nil)
  local availableChanged = newDevice
  if not newDevice then
    if setup.available ~= nil and self._deviceSetup[setup.deviceURL].available ~= nil then
      availableChanged = (setup.available ~= self._deviceSetup[setup.deviceURL].available)
    end
  end

  self._deviceSetup[setup.deviceURL] = setup -- save device in model
  if newDevice then
    if self.events.deviceCreatedEvent then
      self.events.deviceCreatedEvent({deviceURL = setup.deviceURL})
    end
  end

  notifCloud = updateLocalAndSetup(self, setup.deviceURL, setup.label)
  -- events
  if availableChanged then
    if (setup.available) then
      if self.events.deviceAvailableEvent then
        self.events.deviceAvailableEvent({deviceURL = setup.deviceURL});
      end
    else
      if self.events.deviceAvailableEvent then
        self.events.deviceUnavailableEvent({deviceURL = setup.deviceURL});
      end
    end
  end
  return notifCloud
end

--- Delete a device from both storage and setup
--- @tparam string url device's url
--- @return boolean true if device deleted
function Model:deleteDevice(url)
  if not self._deviceSetup[url] then
    log:warning("Cannot delete inexistant device '"..url.."'.")
    self._devices[url] = nil -- erase storage in any case, to avoid desync device
    return false
  end
  if (self._devices[url] ~= nil) and (self._devices[url].synced) then
    log:notice("Device '"..url.."' deleted by cloud.")
  else
    log:notice("Device '"..url.."' deleted by local API.")
  end
  self._deviceSetup[url]  = nil
  self._devices[url]      = nil
  if self.events.deviceDeletedEvent then
    self.events.deviceDeletedEvent({deviceURL = url})
  end
  return true
end

--- Set a device as synced
--- @tparam string url device's url
--- @tparam boolean synced synced state
--- @return boolean true if device updated
function Model:setSynced(url, synced)
  local devFound = self._devices[url]
  if not devFound then
    log:warning("Trying to set as synced a inexistant device: '"..url.."'.")
    return false
  end
  if not devFound.synced then
    devFound.synced = synced
    self._devices[url] = devFound -- write in storage
    if self.events.deviceUpdatedEvent then
      self.events.deviceUpdatedEvent({deviceURL = url});
    end
    log:notice("Set device '"..url.."' as synced.")
  end
  return true
end

--- Get synced state for a device
--- @tparam string url device's url
--- @return boolean true if synced
function Model:isSynced(url)
  if not self._devices[url] then
    return false
  end
  return self._devices[url].synced
end

--- Get device label
--- @tparam string url device's url
--- @return string device's label
function Model:getLabel(url)
  return self._devices[url].label
end

--- Get device generic model
--- @tparam string url device's url
--- @return table generic model
function Model:getDevice(url)
  local device = self._deviceSetup[url]
  if device ~= nil then
    return enhanceDevice(self, device)
  else
    return nil
  end
end

--- Get all device generic model
--- @return table generic model list
function Model:getDevices()
  local devices = {}
  for url, device in pairs(self._deviceSetup) do
    devices[url] = enhanceDevice(self, device)
  end
  return devices
end

local model = Model(Kizbox.id());

--- Local application model
--- @classmod Model
import "Overkiz.utilities"
import "Overkiz.Kizbox"
import "Overkiz.Subject"
import "Overkiz.TableStorage"
import "Overkiz.HomeAutomation.Local.storage"
import "Overkiz.HomeAutomation.Local.log"
import "Overkiz.HomeAutomation.Local.resync"

--- @field _devices string
--- @field protected _requestArgs TableStorage
--- @field public pairedMode boolean
--- @field public deviceNotifier
--- @field public events table
--- @field public driver table
--- @field public gateway table
--- @field public SUPPORTED_PROTOCOLS table
--- @return Model
local Model = class();

-- public constants
-- ----------------
Model.SUPPORTED_PROTOCOLS = {"io", "ovp", "enocean", "rts", "rtn"}

--- Constructor
--- @tparam string boxID box serial number
function Model:new(boxID)
  -- public fields
  -- -------------
  self.pairedMode     = false
  self.deviceNotifier = Subject() -- to notify new device.
  self.events         = {}
  self.driver         = {}
  self.gateway        = boxID

  -- private fields
  -- --------------
  self._devices = TableStorage.subStorage(storage, "devices")
  self._deviceSetup     = {}
end

-- private methods
-- ---------------
--- Update local storage and setup with the new label
--- @tparam string url device's url
--- @tparam string label new label
--- @return boolean true if cloudLink notified
local function updateLocalAndSetup(self, url, label)
  local notifCloud    = false
  local deviceSetup   = self._deviceSetup[url]
  local localDevice   = self._devices[url]

  if not deviceSetup and not localDevice then
    return -- nothing to merge
  elseif not localDevice then
    self._devices[url] = {label=label, synced=false}
    notifCloud = true -- need to notify cloud
    log:notice("Local device '"..url.."' created by driver.")
  else -- localDevice already exists.
    if deviceSetup then
      notifCloud = true
      if (label ~= nil) and (localDevice.label ~= label) and (not localDevice.fromCloud) then
        -- device coming from protocol, update label and send resync flag.
        localDevice.label = label
        self._devices[url] = localDevice -- write in storage
        log:notice("Local device '"..url.."' updated by driver.")
      else
        deviceSetup.label = localDevice.label
        log:notice("Device setup '"..url.."' updated by local.")
      end
    end
  end

  -- do not fire notif. if local device already synced (rest api locked):
  if (notifCloud) and (localDevice==nil or not localDevice.synced) then
    if self.events.deviceUpdatedEvent then
      self.events.deviceUpdatedEvent({deviceURL = url});
    end
    resync:update()
    self.deviceNotifier:notify(self._deviceSetup[url])
    log:notice("Device '"..url.."' has been updated. Sending resync flag.")
  end
  return notifCloud
end

--- Add local information to a high level device:
---   * label : Device name
---   * sync  : Is device synced with server
--- (return a copy of passed device)
--- @tparam self self instance (private)
--- @tparam table device device to enhance
--- @function enhanceDevice
--- @treturn table enhanced device
local function enhanceDevice(self, device)
  local localDevice = self._devices[device.deviceURL]
  if not localDevice then
    return device
  else
    local ret  = ovk.tableDeepCopy(device)
    ret.label  = localDevice.label
    ret.synced = localDevice.synced
    return ret
  end
end


-- public methods
-- --------------
--- Add or update a device definition (url + label) comming from the cloud
--- @tparam string url device's url
--- @tparam string label new label
--- @return boolean true if cloudLink notified
function Model:addOrUpdateDevFromCloud(url, label)
  local localDevice  = self._devices[url]
  if localDevice then -- update.
    localDevice.label = label
    self._devices[url] = localDevice
    log:notice("Local device '"..url.."' updated by cloud.")
  else -- create.
    if label then
      self._devices[url] = {label=label, synced=false, fromCloud=true}
    else
      self._devices[url] = {synced=false, fromCloud=true}
    end
    log:notice("Local device '"..url.."' created by cloud.")
  end
  return updateLocalAndSetup(self, url, label)
end

--- Add or update a device model (setup) comming from the protocol
--- @tparam string setup device's setup
--- @return boolean true if cloudLink notified
function Model:addOrUpdateDevFromProto(setup)
  local notifCloud = false
  local v, r = ovk.checkPath(setup, {deviceURL = "string"});
  if not v then
    log:error("Malformed setup argument. ("..tostring(r)..")");
    return
  end

  local newDevice = (self._deviceSetup[setup.deviceURL] == nil)
  local availableChanged = newDevice
  if not newDevice then
    if setup.available ~= nil and self._deviceSetup[setup.deviceURL].available ~= nil then
      availableChanged = (setup.available ~= self._deviceSetup[setup.deviceURL].available)
    end
  end

  self._deviceSetup[setup.deviceURL] = setup -- save device in model
  if newDevice then
    if self.events.deviceCreatedEvent then
      self.events.deviceCreatedEvent({deviceURL = setup.deviceURL})
    end
  end

  notifCloud = updateLocalAndSetup(self, setup.deviceURL, setup.label)
  -- events
  if availableChanged then
    if (setup.available) then
      if self.events.deviceAvailableEvent then
        self.events.deviceAvailableEvent({deviceURL = setup.deviceURL});
      end
    else
      if self.events.deviceAvailableEvent then
        self.events.deviceUnavailableEvent({deviceURL = setup.deviceURL});
      end
    end
  end
  return notifCloud
end

--- Delete a device from both storage and setup
--- @tparam string url device's url
--- @return boolean true if device deleted
function Model:deleteDevice(url)
  if not self._deviceSetup[url] then
    log:warning("Cannot delete inexistant device '"..url.."'.")
    self._devices[url] = nil -- erase storage in any case, to avoid desync device
    return false
  end
  if (self._devices[url] ~= nil) and (self._devices[url].synced) then
    log:notice("Device '"..url.."' deleted by cloud.")
  else
    log:notice("Device '"..url.."' deleted by local API.")
  end
  self._deviceSetup[url]  = nil
  self._devices[url]      = nil
  if self.events.deviceDeletedEvent then
    self.events.deviceDeletedEvent({deviceURL = url})
  end
  return true
end

--- Set a device as synced
--- @tparam string url device's url
--- @tparam boolean synced synced state
--- @return boolean true if device updated
function Model:setSynced(url, synced)
  local devFound = self._devices[url]
  if not devFound then
    log:warning("Trying to set as synced a inexistant device: '"..url.."'.")
    return false
  end
  if not devFound.synced then
    devFound.synced = synced
    self._devices[url] = devFound -- write in storage
    if self.events.deviceUpdatedEvent then
      self.events.deviceUpdatedEvent({deviceURL = url});
    end
    log:notice("Set device '"..url.."' as synced.")
  end
  return true
end

--- Get synced state for a device
--- @tparam string url device's url
--- @return boolean true if synced
function Model:isSynced(url)
  if not self._devices[url] then
    return false
  end
  return self._devices[url].synced
end

--- Get device label
--- @tparam string url device's url
--- @return string device's label
function Model:getLabel(url)
  return self._devices[url].label
end

--- Get device generic model
--- @tparam string url device's url
--- @return table generic model
function Model:getDevice(url)
  local device = self._deviceSetup[url]
  if device ~= nil then
    return enhanceDevice(self, device)
  else
    return nil
  end
end

--- Get all device generic model
--- @return table generic model list
function Model:getDevices()
  local devices = {}
  for url, device in pairs(self._deviceSetup) do
    devices[url] = enhanceDevice(self, device)
  end
  return devices
end

local model = Model(Kizbox.id());
--- Set a device as synced
--- @tparam string url device's url
--- @tparam boolean synced synced state
--- @return boolean true if device updated
function Model:setSynced(url, synced)
  local devFound = self._devices[url]
  if not devFound then
    log:warning("Trying to set as synced a inexistant device: '"..url.."'.")
    return false
  end
  if not devFound.synced then
    devFound.synced = synced
    self._devices[url] = devFound -- write in storage
    if self.events.deviceUpdatedEvent then
      self.events.deviceUpdatedEvent({deviceURL = url});
    end
    log:notice("Set device '"..url.."' as synced.")
  end
  return true
end

--- Get synced state for a device
--- @tparam string url device's url
--- @return boolean true if synced
function Model:isSynced(url)
  if not self._devices[url] then
    return false
  end
  return self._devices[url].synced
end

--- Get device label
--- @tparam string url device's url
--- @return string device's label
function Model:getLabel(url)
  return self._devices[url].label
end

--- Get device generic model
--- @tparam string url device's url
--- @return table generic model
function Model:getDevice(url)
  local device = self._deviceSetup[url]
  if device ~= nil then
    return enhanceDevice(self, device)
  else
    return nil
  end
end

--- Get all device generic model
--- @return table generic model list
function Model:getDevices()
  local devices = {}
  for url, device in pairs(self._deviceSetup) do
    devices[url] = enhanceDevice(self, device)
  end
  return devices
end

local model = Model(Kizbox.id());
--- Set a device as synced
--- @tparam string url device's url
--- @tparam boolean synced synced state
--- @return boolean true if device updated
function Model:setSynced(url, synced)
  local devFound = self._devices[url]
  if not devFound then
    log:warning("Trying to set as synced a inexistant device: '"..url.."'.")
    return false
  end
  if not devFound.synced then
    devFound.synced = synced
    self._devices[url] = devFound -- write in storage
    if self.events.deviceUpdatedEvent then
      self.events.deviceUpdatedEvent({deviceURL = url});
    end
    log:notice("Set device '"..url.."' as synced.")
  end
  return true
end

--- Get synced state for a device
--- @tparam string url device's url
--- @return boolean true if synced
function Model:isSynced(url)
  if not self._devices[url] then
    return false
  end
  return self._devices[url].synced
end

--- Get device label
--- @tparam string url device's url
--- @return string device's label
function Model:getLabel(url)
  return self._devices[url].label
end

--- Get device generic model
--- @tparam string url device's url
--- @return table generic model
function Model:getDevice(url)
  local device = self._deviceSetup[url]
  if device ~= nil then
    return enhanceDevice(self, device)
  else
    return nil
  end
end

--- Get all device generic model
--- @return table generic model list
function Model:getDevices()
  local devices = {}
  for url, device in pairs(self._deviceSetup) do
    devices[url] = enhanceDevice(self, device)
  end
  return devices
end

local model = Model(Kizbox.id());
--- Set a device as synced
--- @tparam string url device's url
--- @tparam boolean synced synced state
--- @return boolean true if device updated
function Model:setSynced(url, synced)
  local devFound = self._devices[url]
  if not devFound then
    log:warning("Trying to set as synced a inexistant device: '"..url.."'.")
    return false
  end
  if not devFound.synced then
    devFound.synced = synced
    self._devices[url] = devFound -- write in storage
    if self.events.deviceUpdatedEvent then
      self.events.deviceUpdatedEvent({deviceURL = url});
    end
    log:notice("Set device '"..url.."' as synced.")
  end
  return true
end

--- Get synced state for a device
--- @tparam string url device's url
--- @return boolean true if synced
function Model:isSynced(url)
  if not self._devices[url] then
    return false
  end
  return self._devices[url].synced
end

--- Get device label
--- @tparam string url device's url
--- @return string device's label
function Model:getLabel(url)
  return self._devices[url].label
end

--- Get device generic model
--- @tparam string url device's url
--- @return table generic model
function Model:getDevice(url)
  local device = self._deviceSetup[url]
  if device ~= nil then
    return enhanceDevice(self, device)
  else
    return nil
  end
end

--- Get all device generic model
--- @return table generic model list
function Model:getDevices()
  local devices = {}
  for url, device in pairs(self._deviceSetup) do
    devices[url] = enhanceDevice(self, device)
  end
  return devices
end

local model = Model(Kizbox.id());
--- Set a device as synced
--- @tparam string url device's url
--- @tparam boolean synced synced state
--- @return boolean true if device updated
function Model:setSynced(url, synced)
  local devFound = self._devices[url]
  if not devFound then
    log:warning("Trying to set as synced a inexistant device: '"..url.."'.")
    return false
  end
  if not devFound.synced then
    devFound.synced = synced
    self._devices[url] = devFound -- write in storage
    if self.events.deviceUpdatedEvent then
      self.events.deviceUpdatedEvent({deviceURL = url});
    end
    log:notice("Set device '"..url.."' as synced.")
  end
  return true
end

--- Get synced state for a device
--- @tparam string url device's url
--- @return boolean true if synced
function Model:isSynced(url)
  if not self._devices[url] then
    return false
  end
  return self._devices[url].synced
end

--- Get device label
--- @tparam string url device's url
--- @return string device's label
function Model:getLabel(url)
  return self._devices[url].label
end

--- Get device generic model
--- @tparam string url device's url
--- @return table generic model
function Model:getDevice(url)
  local device = self._deviceSetup[url]
  if device ~= nil then
    return enhanceDevice(self, device)
  else
    return nil
  end
end

--- Get all device generic model
--- @return table generic model list
function Model:getDevices()
  local devices = {}
  for url, device in pairs(self._deviceSetup) do
    devices[url] = enhanceDevice(self, device)
  end
  return devices
end

local model = Model(Kizbox.id());
--- Set a device as synced
--- @tparam string url device's url
--- @tparam boolean synced synced state
--- @return boolean true if device updated
function Model:setSynced(url, synced)
  local devFound = self._devices[url]
  if not devFound then
    log:warning("Trying to set as synced a inexistant device: '"..url.."'.")
    return false
  end
  if not devFound.synced then
    devFound.synced = synced
    self._devices[url] = devFound -- write in storage
    if self.events.deviceUpdatedEvent then
      self.events.deviceUpdatedEvent({deviceURL = url});
    end
    log:notice("Set device '"..url.."' as synced.")
  end
  return true
end

--- Get synced state for a device
--- @tparam string url device's url
--- @return boolean true if synced
function Model:isSynced(url)
  if not self._devices[url] then
    return false
  end
  return self._devices[url].synced
end

--- Get device label
--- @tparam string url device's url
--- @return string device's label
function Model:getLabel(url)
  return self._devices[url].label
end

--- Get device generic model
--- @tparam string url device's url
--- @return table generic model
function Model:getDevice(url)
  local device = self._deviceSetup[url]
  if device ~= nil then
    return enhanceDevice(self, device)
  else
    return nil
  end
end

--- Get all device generic model
--- @return table generic model list
function Model:getDevices()
  local devices = {}
  for url, device in pairs(self._deviceSetup) do
    devices[url] = enhanceDevice(self, device)
  end
  return devices
end

local model = Model(Kizbox.id());
--- Set a device as synced
--- @tparam string url device's url
--- @tparam boolean synced synced state
--- @return boolean true if device updated
function Model:setSynced(url, synced)
  local devFound = self._devices[url]
  if not devFound then
    log:warning("Trying to set as synced a inexistant device: '"..url.."'.")
    return false
  end
  if not devFound.synced then
    devFound.synced = synced
    self._devices[url] = devFound -- write in storage
    if self.events.deviceUpdatedEvent then
      self.events.deviceUpdatedEvent({deviceURL = url});
    end
    log:notice("Set device '"..url.."' as synced.")
  end
  return true
end

--- Get synced state for a device
--- @tparam string url device's url
--- @return boolean true if synced
function Model:isSynced(url)
  if not self._devices[url] then
    return false
  end
  return self._devices[url].synced
end

--- Get device label
--- @tparam string url device's url
--- @return string device's label
function Model:getLabel(url)
  return self._devices[url].label
end

--- Get device generic model
--- @tparam string url device's url
--- @return table generic model
function Model:getDevice(url)
  local device = self._deviceSetup[url]
  if device ~= nil then
    return enhanceDevice(self, device)
  else
    return nil
  end
end

--- Get all device generic model
--- @return table generic model list
function Model:getDevices()
  local devices = {}
  for url, device in pairs(self._deviceSetup) do
    devices[url] = enhanceDevice(self, device)
  end
  return devices
end

local model = Model(Kizbox.id());
--- Set a device as synced
--- @tparam string url device's url
--- @tparam boolean synced synced state
--- @return boolean true if device updated
function Model:setSynced(url, synced)
  local devFound = self._devices[url]
  if not devFound then
    log:warning("Trying to set as synced a inexistant device: '"..url.."'.")
    return false
  end
  if not devFound.synced then
    devFound.synced = synced
    self._devices[url] = devFound -- write in storage
    if self.events.deviceUpdatedEvent then
      self.events.deviceUpdatedEvent({deviceURL = url});
    end
    log:notice("Set device '"..url.."' as synced.")
  end
  return true
end

--- Get synced state for a device
--- @tparam string url device's url
--- @return boolean true if synced
function Model:isSynced(url)
  if not self._devices[url] then
    return false
  end
  return self._devices[url].synced
end

--- Get device label
--- @tparam string url device's url
--- @return string device's label
function Model:getLabel(url)
  return self._devices[url].label
end

--- Get device generic model
--- @tparam string url device's url
--- @return table generic model
function Model:getDevice(url)
  local device = self._deviceSetup[url]
  if device ~= nil then
    return enhanceDevice(self, device)
  else
    return nil
  end
end

--- Get all device generic model
--- @return table generic model list
function Model:getDevices()
  local devices = {}
  for url, device in pairs(self._deviceSetup) do
    devices[url] = enhanceDevice(self, device)
  end
  return devices
end

local model = Model(Kizbox.id());
--- Set a device as synced
--- @tparam string url device's url
--- @tparam boolean synced synced state
--- @return boolean true if device updated
function Model:setSynced(url, synced)
  local devFound = self._devices[url]
  if not devFound then
    log:warning("Trying to set as synced a inexistant device: '"..url.."'.")
    return false
  end
  if not devFound.synced then
    devFound.synced = synced
    self._devices[url] = devFound -- write in storage
    if self.events.deviceUpdatedEvent then
      self.events.deviceUpdatedEvent({deviceURL = url});
    end
    log:notice("Set device '"..url.."' as synced.")
  end
  return true
end

--- Get synced state for a device
--- @tparam string url device's url
--- @return boolean true if synced
function Model:isSynced(url)
  if not self._devices[url] then
    return false
  end
  return self._devices[url].synced
end

--- Get device label
--- @tparam string url device's url
--- @return string device's label
function Model:getLabel(url)
  return self._devices[url].label
end

--- Get device generic model
--- @tparam string url device's url
--- @return table generic model
function Model:getDevice(url)
  local device = self._deviceSetup[url]
  if device ~= nil then
    return enhanceDevice(self, device)
  else
    return nil
  end
end

--- Get all device generic model
--- @return table generic model list
function Model:getDevices()
  local devices = {}
  for url, device in pairs(self._deviceSetup) do
    devices[url] = enhanceDevice(self, device)
  end
  return devices
end

local model = Model(Kizbox.id());
--- Set a device as synced
--- @tparam string url device's url
--- @tparam boolean synced synced state
--- @return boolean true if device updated
function Model:setSynced(url, synced)
  local devFound = self._devices[url]
  if not devFound then
    log:warning("Trying to set as synced a inexistant device: '"..url.."'.")
    return false
  end
  if not devFound.synced then
    devFound.synced = synced
    self._devices[url] = devFound -- write in storage
    if self.events.deviceUpdatedEvent then
      self.events.deviceUpdatedEvent({deviceURL = url});
    end
    log:notice("Set device '"..url.."' as synced.")
  end
  return true
end

--- Get synced state for a device
--- @tparam string url device's url
--- @return boolean true if synced
function Model:isSynced(url)
  if not self._devices[url] then
    return false
  end
  return self._devices[url].synced
end

--- Get device label
--- @tparam string url device's url
--- @return string device's label
function Model:getLabel(url)
  return self._devices[url].label
end

--- Get device generic model
--- @tparam string url device's url
--- @return table generic model
function Model:getDevice(url)
  local device = self._deviceSetup[url]
  if device ~= nil then
    return enhanceDevice(self, device)
  else
    return nil
  end
end

--- Get all device generic model
--- @return table generic model list
function Model:getDevices()
  local devices = {}
  for url, device in pairs(self._deviceSetup) do
    devices[url] = enhanceDevice(self, device)
  end
  return devices
end

local model = Model(Kizbox.id());
--- Set a device as synced
--- @tparam string url device's url
--- @tparam boolean synced synced state
--- @return boolean true if device updated
function Model:setSynced(url, synced)
  local devFound = self._devices[url]
  if not devFound then
    log:warning("Trying to set as synced a inexistant device: '"..url.."'.")
    return false
  end
  if not devFound.synced then
    devFound.synced = synced
    self._devices[url] = devFound -- write in storage
    if self.events.deviceUpdatedEvent then
      self.events.deviceUpdatedEvent({deviceURL = url});
    end
    log:notice("Set device '"..url.."' as synced.")
  end
  return true
end

--- Get synced state for a device
--- @tparam string url device's url
--- @return boolean true if synced
function Model:isSynced(url)
  if not self._devices[url] then
    return false
  end
  return self._devices[url].synced
end

--- Get device label
--- @tparam string url device's url
--- @return string device's label
function Model:getLabel(url)
  return self._devices[url].label
end

--- Get device generic model
--- @tparam string url device's url
--- @return table generic model
function Model:getDevice(url)
  local device = self._deviceSetup[url]
  if device ~= nil then
    return enhanceDevice(self, device)
  else
    return nil
  end
end

--- Get all device generic model
--- @return table generic model list
function Model:getDevices()
  local devices = {}
  for url, device in pairs(self._deviceSetup) do
    devices[url] = enhanceDevice(self, device)
  end
  return devices
end

local model = Model(Kizbox.id());
--- Set a device as synced
--- @tparam string url device's url
--- @tparam boolean synced synced state
--- @return boolean true if device updated
function Model:setSynced(url, synced)
  local devFound = self._devices[url]
  if not devFound then
    log:warning("Trying to set as synced a inexistant device: '"..url.."'.")
    return false
  end
  if not devFound.synced then
    devFound.synced = synced
    self._devices[url] = devFound -- write in storage
    if self.events.deviceUpdatedEvent then
      self.events.deviceUpdatedEvent({deviceURL = url});
    end
    log:notice("Set device '"..url.."' as synced.")
  end
  return true
end

--- Get synced state for a device
--- @tparam string url device's url
--- @return boolean true if synced
function Model:isSynced(url)
  if not self._devices[url] then
    return false
  end
  return self._devices[url].synced
end

--- Get device label
--- @tparam string url device's url
--- @return string device's label
function Model:getLabel(url)
  return self._devices[url].label
end

--- Get device generic model
--- @tparam string url device's url
--- @return table generic model
function Model:getDevice(url)
  local device = self._deviceSetup[url]
  if device ~= nil then
    return enhanceDevice(self, device)
  else
    return nil
  end
end

--- Get all device generic model
--- @return table generic model list
function Model:getDevices()
  local devices = {}
  for url, device in pairs(self._deviceSetup) do
    devices[url] = enhanceDevice(self, device)
  end
  return devices
end

local model = Model(Kizbox.id());
--- Set a device as synced
--- @tparam string url device's url
--- @tparam boolean synced synced state
--- @return boolean true if device updated
function Model:setSynced(url, synced)
  local devFound = self._devices[url]
  if not devFound then
    log:warning("Trying to set as synced a inexistant device: '"..url.."'.")
    return false
  end
  if not devFound.synced then
    devFound.synced = synced
    self._devices[url] = devFound -- write in storage
    if self.events.deviceUpdatedEvent then
      self.events.deviceUpdatedEvent({deviceURL = url});
    end
    log:notice("Set device '"..url.."' as synced.")
  end
  return true
end

--- Get synced state for a device
--- @tparam string url device's url
--- @return boolean true if synced
function Model:isSynced(url)
  if not self._devices[url] then
    return false
  end
  return self._devices[url].synced
end

--- Get device label
--- @tparam string url device's url
--- @return string device's label
function Model:getLabel(url)
  return self._devices[url].label
end

--- Get device generic model
--- @tparam string url device's url
--- @return table generic model
function Model:getDevice(url)
  local device = self._deviceSetup[url]
  if device ~= nil then
    return enhanceDevice(self, device)
  else
    return nil
  end
end

--- Get all device generic model
--- @return table generic model list
function Model:getDevices()
  local devices = {}
  for url, device in pairs(self._deviceSetup) do
    devices[url] = enhanceDevice(self, device)
  end
  return devices
end

local model = Model(Kizbox.id());
--- Set a device as synced
--- @tparam string url device's url
--- @tparam boolean synced synced state
--- @return boolean true if device updated
function Model:setSynced(url, synced)
  local devFound = self._devices[url]
  if not devFound then
    log:warning("Trying to set as synced a inexistant device: '"..url.."'.")
    return false
  end
  if not devFound.synced then
    devFound.synced = synced
    self._devices[url] = devFound -- write in storage
    if self.events.deviceUpdatedEvent then
      self.events.deviceUpdatedEvent({deviceURL = url});
    end
    log:notice("Set device '"..url.."' as synced.")
  end
  return true
end

--- Get synced state for a device
--- @tparam string url device's url
--- @return boolean true if synced
function Model:isSynced(url)
  if not self._devices[url] then
    return false
  end
  return self._devices[url].synced
end

--- Get device label
--- @tparam string url device's url
--- @return string device's label
function Model:getLabel(url)
  return self._devices[url].label
end

--- Get device generic model
--- @tparam string url device's url
--- @return table generic model
function Model:getDevice(url)
  local device = self._deviceSetup[url]
  if device ~= nil then
    return enhanceDevice(self, device)
  else
    return nil
  end
end

--- Get all device generic model
--- @return table generic model list
function Model:getDevices()
  local devices = {}
  for url, device in pairs(self._deviceSetup) do
    devices[url] = enhanceDevice(self, device)
  end
  return devices
end

local model = Model(Kizbox.id());
--- Set a device as synced
--- @tparam string url device's url
--- @tparam boolean synced synced state
--- @return boolean true if device updated
function Model:setSynced(url, synced)
  local devFound = self._devices[url]
  if not devFound then
    log:warning("Trying to set as synced a inexistant device: '"..url.."'.")
    return false
  end
  if not devFound.synced then
    devFound.synced = synced
    self._devices[url] = devFound -- write in storage
    if self.events.deviceUpdatedEvent then
      self.events.deviceUpdatedEvent({deviceURL = url});
    end
    log:notice("Set device '"..url.."' as synced.")
  end
  return true
end

--- Get synced state for a device
--- @tparam string url device's url
--- @return boolean true if synced
function Model:isSynced(url)
  if not self._devices[url] then
    return false
  end
  return self._devices[url].synced
end

--- Get device label
--- @tparam string url device's url
--- @return string device's label
function Model:getLabel(url)
  return self._devices[url].label
end

--- Get device generic model
--- @tparam string url device's url
--- @return table generic model
function Model:getDevice(url)
  local device = self._deviceSetup[url]
  if device ~= nil then
    return enhanceDevice(self, device)
  else
    return nil
  end
end

--- Get all device generic model
--- @return table generic model list
function Model:getDevices()
  local devices = {}
  for url, device in pairs(self._deviceSetup) do
    devices[url] = enhanceDevice(self, device)
  end
  return devices
end

local model = Model(Kizbox.id());
--- Set a device as synced
--- @tparam string url device's url
--- @tparam boolean synced synced state
--- @return boolean true if device updated
function Model:setSynced(url, synced)
  local devFound = self._devices[url]
  if not devFound then
    log:warning("Trying to set as synced a inexistant device: '"..url.."'.")
    return false
  end
  if not devFound.synced then
    devFound.synced = synced
    self._devices[url] = devFound -- write in storage
    if self.events.deviceUpdatedEvent then
      self.events.deviceUpdatedEvent({deviceURL = url});
    end
    log:notice("Set device '"..url.."' as synced.")
  end
  return true
end

--- Get synced state for a device
--- @tparam string url device's url
--- @return boolean true if synced
function Model:isSynced(url)
  if not self._devices[url] then
    return false
  end
  return self._devices[url].synced
end

--- Get device label
--- @tparam string url device's url
--- @return string device's label
function Model:getLabel(url)
  return self._devices[url].label
end

--- Get device generic model
--- @tparam string url device's url
--- @return table generic model
function Model:getDevice(url)
  local device = self._deviceSetup[url]
  if device ~= nil then
    return enhanceDevice(self, device)
  else
    return nil
  end
end

--- Get all device generic model
--- @return table generic model list
function Model:getDevices()
  local devices = {}
  for url, device in pairs(self._deviceSetup) do
    devices[url] = enhanceDevice(self, device)
  end
  return devices
end

local model = Model(Kizbox.id());
--- Set a device as synced
--- @tparam string url device's url
--- @tparam boolean synced synced state
--- @return boolean true if device updated
function Model:setSynced(url, synced)
  local devFound = self._devices[url]
  if not devFound then
    log:warning("Trying to set as synced a inexistant device: '"..url.."'.")
    return false
  end
  if not devFound.synced then
    devFound.synced = synced
    self._devices[url] = devFound -- write in storage
    if self.events.deviceUpdatedEvent then
      self.events.deviceUpdatedEvent({deviceURL = url});
    end
    log:notice("Set device '"..url.."' as synced.")
  end
  return true
end

--- Get synced state for a device
--- @tparam string url device's url
--- @return boolean true if synced
function Model:isSynced(url)
  if not self._devices[url] then
    return false
  end
  return self._devices[url].synced
end

--- Get device label
--- @tparam string url device's url
--- @return string device's label
function Model:getLabel(url)
  return self._devices[url].label
end

--- Get device generic model
--- @tparam string url device's url
--- @return table generic model
function Model:getDevice(url)
  local device = self._deviceSetup[url]
  if device ~= nil then
    return enhanceDevice(self, device)
  else
    return nil
  end
end

--- Get all device generic model
--- @return table generic model list
function Model:getDevices()
  local devices = {}
  for url, device in pairs(self._deviceSetup) do
    devices[url] = enhanceDevice(self, device)
  end
  return devices
end

local model = Model(Kizbox.id());
--- Set a device as synced
--- @tparam string url device's url
--- @tparam boolean synced synced state
--- @return boolean true if device updated
function Model:setSynced(url, synced)
  local devFound = self._devices[url]
  if not devFound then
    log:warning("Trying to set as synced a inexistant device: '"..url.."'.")
    return false
  end
  if not devFound.synced then
    devFound.synced = synced
    self._devices[url] = devFound -- write in storage
    if self.events.deviceUpdatedEvent then
      self.events.deviceUpdatedEvent({deviceURL = url});
    end
    log:notice("Set device '"..url.."' as synced.")
  end
  return true
end

--- Get synced state for a device
--- @tparam string url device's url
--- @return boolean true if synced
function Model:isSynced(url)
  if not self._devices[url] then
    return false
  end
  return self._devices[url].synced
end

--- Get device label
--- @tparam string url device's url
--- @return string device's label
function Model:getLabel(url)
  return self._devices[url].label
end

--- Get device generic model
--- @tparam string url device's url
--- @return table generic model
function Model:getDevice(url)
  local device = self._deviceSetup[url]
  if device ~= nil then
    return enhanceDevice(self, device)
  else
    return nil
  end
end

--- Get all device generic model
--- @return table generic model list
function Model:getDevices()
  local devices = {}
  for url, device in pairs(self._deviceSetup) do
    devices[url] = enhanceDevice(self, device)
  end
  return devices
end

local model = Model(Kizbox.id());
--- Set a device as synced
--- @tparam string url device's url
--- @tparam boolean synced synced state
--- @return boolean true if device updated
function Model:setSynced(url, synced)
  local devFound = self._devices[url]
  if not devFound then
    log:warning("Trying to set as synced a inexistant device: '"..url.."'.")
    return false
  end
  if not devFound.synced then
    devFound.synced = synced
    self._devices[url] = devFound -- write in storage
    if self.events.deviceUpdatedEvent then
      self.events.deviceUpdatedEvent({deviceURL = url});
    end
    log:notice("Set device '"..url.."' as synced.")
  end
  return true
end

--- Get synced state for a device
--- @tparam string url device's url
--- @return boolean true if synced
function Model:isSynced(url)
  if not self._devices[url] then
    return false
  end
  return self._devices[url].synced
end

--- Get device label
--- @tparam string url device's url
--- @return string device's label
function Model:getLabel(url)
  return self._devices[url].label
end

--- Get device generic model
--- @tparam string url device's url
--- @return table generic model
function Model:getDevice(url)
  local device = self._deviceSetup[url]
  if device ~= nil then
    return enhanceDevice(self, device)
  else
    return nil
  end
end

--- Get all device generic model
--- @return table generic model list
function Model:getDevices()
  local devices = {}
  for url, device in pairs(self._deviceSetup) do
    devices[url] = enhanceDevice(self, device)
  end
  return devices
end

local model = Model(Kizbox.id());
--- Set a device as synced
--- @tparam string url device's url
--- @tparam boolean synced synced state
--- @return boolean true if device updated
function Model:setSynced(url, synced)
  local devFound = self._devices[url]
  if not devFound then
    log:warning("Trying to set as synced a inexistant device: '"..url.."'.")
    return false
  end
  if not devFound.synced then
    devFound.synced = synced
    self._devices[url] = devFound -- write in storage
    if self.events.deviceUpdatedEvent then
      self.events.deviceUpdatedEvent({deviceURL = url});
    end
    log:notice("Set device '"..url.."' as synced.")
  end
  return true
end

--- Get synced state for a device
--- @tparam string url device's url
--- @return boolean true if synced
function Model:isSynced(url)
  if not self._devices[url] then
    return false
  end
  return self._devices[url].synced
end

--- Get device label
--- @tparam string url device's url
--- @return string device's label
function Model:getLabel(url)
  return self._devices[url].label
end

--- Get device generic model
--- @tparam string url device's url
--- @return table generic model
function Model:getDevice(url)
  local device = self._deviceSetup[url]
  if device ~= nil then
    return enhanceDevice(self, device)
  else
    return nil
  end
end

--- Get all device generic model
--- @return table generic model list
function Model:getDevices()
  local devices = {}
  for url, device in pairs(self._deviceSetup) do
    devices[url] = enhanceDevice(self, device)
  end
  return devices
end

local model = Model(Kizbox.id());
--- Set a device as synced
--- @tparam string url device's url
--- @tparam boolean synced synced state
--- @return boolean true if device updated
function Model:setSynced(url, synced)
  local devFound = self._devices[url]
  if not devFound then
    log:warning("Trying to set as synced a inexistant device: '"..url.."'.")
    return false
  end
  if not devFound.synced then
    devFound.synced = synced
    self._devices[url] = devFound -- write in storage
    if self.events.deviceUpdatedEvent then
      self.events.deviceUpdatedEvent({deviceURL = url});
    end
    log:notice("Set device '"..url.."' as synced.")
  end
  return true
end

--- Get synced state for a device
--- @tparam string url device's url
--- @return boolean true if synced
function Model:isSynced(url)
  if not self._devices[url] then
    return false
  end
  return self._devices[url].synced
end

--- Get device label
--- @tparam string url device's url
--- @return string device's label
function Model:getLabel(url)
  return self._devices[url].label
end

--- Get device generic model
--- @tparam string url device's url
--- @return table generic model
function Model:getDevice(url)
  local device = self._deviceSetup[url]
  if device ~= nil then
    return enhanceDevice(self, device)
  else
    return nil
  end
end

--- Get all device generic model
--- @return table generic model list
function Model:getDevices()
  local devices = {}
  for url, device in pairs(self._deviceSetup) do
    devices[url] = enhanceDevice(self, device)
  end
  return devices
end

local model = Model(Kizbox.id());
--- Set a device as synced
--- @tparam string url device's url
--- @tparam boolean synced synced state
--- @return boolean true if device updated
function Model:setSynced(url, synced)
  local devFound = self._devices[url]
  if not devFound then
    log:warning("Trying to set as synced a inexistant device: '"..url.."'.")
    return false
  end
  if not devFound.synced then
    devFound.synced = synced
    self._devices[url] = devFound -- write in storage
    if self.events.deviceUpdatedEvent then
      self.events.deviceUpdatedEvent({deviceURL = url});
    end
    log:notice("Set device '"..url.."' as synced.")
  end
  return true
end

--- Get synced state for a device
--- @tparam string url device's url
--- @return boolean true if synced
function Model:isSynced(url)
  if not self._devices[url] then
    return false
  end
  return self._devices[url].synced
end

--- Get device label
--- @tparam string url device's url
--- @return string device's label
function Model:getLabel(url)
  return self._devices[url].label
end

--- Get device generic model
--- @tparam string url device's url
--- @return table generic model
function Model:getDevice(url)
  local device = self._deviceSetup[url]
  if device ~= nil then
    return enhanceDevice(self, device)
  else
    return nil
  end
end

--- Get all device generic model
--- @return table generic model list
function Model:getDevices()
  local devices = {}
  for url, device in pairs(self._deviceSetup) do
    devices[url] = enhanceDevice(self, device)
  end
  return devices
end

local model = Model(Kizbox.id());
--- Set a device as synced
--- @tparam string url device's url
--- @tparam boolean synced synced state
--- @return boolean true if device updated
function Model:setSynced(url, synced)
  local devFound = self._devices[url]
  if not devFound then
    log:warning("Trying to set as synced a inexistant device: '"..url.."'.")
    return false
  end
  if not devFound.synced then
    devFound.synced = synced
    self._devices[url] = devFound -- write in storage
    if self.events.deviceUpdatedEvent then
      self.events.deviceUpdatedEvent({deviceURL = url});
    end
    log:notice("Set device '"..url.."' as synced.")
  end
  return true
end

--- Get synced state for a device
--- @tparam string url device's url
--- @return boolean true if synced
function Model:isSynced(url)
  if not self._devices[url] then
    return false
  end
  return self._devices[url].synced
end

--- Get device label
--- @tparam string url device's url
--- @return string device's label
function Model:getLabel(url)
  return self._devices[url].label
end

--- Get device generic model
--- @tparam string url device's url
--- @return table generic model
function Model:getDevice(url)
  local device = self._deviceSetup[url]
  if device ~= nil then
    return enhanceDevice(self, device)
  else
    return nil
  end
end

--- Get all device generic model
--- @return table generic model list
function Model:getDevices()
  local devices = {}
  for url, device in pairs(self._deviceSetup) do
    devices[url] = enhanceDevice(self, device)
  end
  return devices
end

local model = Model(Kizbox.id());
--- Set a device as synced
--- @tparam string url device's url
--- @tparam boolean synced synced state
--- @return boolean true if device updated
function Model:setSynced(url, synced)
  local devFound = self._devices[url]
  if not devFound then
    log:warning("Trying to set as synced a inexistant device: '"..url.."'.")
    return false
  end
  if not devFound.synced then
    devFound.synced = synced
    self._devices[url] = devFound -- write in storage
    if self.events.deviceUpdatedEvent then
      self.events.deviceUpdatedEvent({deviceURL = url});
    end
    log:notice("Set device '"..url.."' as synced.")
  end
  return true
end

--- Get synced state for a device
--- @tparam string url device's url
--- @return boolean true if synced
function Model:isSynced(url)
  if not self._devices[url] then
    return false
  end
  return self._devices[url].synced
end

--- Get device label
--- @tparam string url device's url
--- @return string device's label
function Model:getLabel(url)
  return self._devices[url].label
end

--- Get device generic model
--- @tparam string url device's url
--- @return table generic model
function Model:getDevice(url)
  local device = self._deviceSetup[url]
  if device ~= nil then
    return enhanceDevice(self, device)
  else
    return nil
  end
end

--- Get all device generic model
--- @return table generic model list
function Model:getDevices()
  local devices = {}
  for url, device in pairs(self._deviceSetup) do
    devices[url] = enhanceDevice(self, device)
  end
  return devices
end

local model = Model(Kizbox.id());
--- Set a device as synced
--- @tparam string url device's url
--- @tparam boolean synced synced state
--- @return boolean true if device updated
function Model:setSynced(url, synced)
  local devFound = self._devices[url]
  if not devFound then
    log:warning("Trying to set as synced a inexistant device: '"..url.."'.")
    return false
  end
  if not devFound.synced then
    devFound.synced = synced
    self._devices[url] = devFound -- write in storage
    if self.events.deviceUpdatedEvent then
      self.events.deviceUpdatedEvent({deviceURL = url});
    end
    log:notice("Set device '"..url.."' as synced.")
  end
  return true
end

--- Get synced state for a device
--- @tparam string url device's url
--- @return boolean true if synced
function Model:isSynced(url)
  if not self._devices[url] then
    return false
  end
  return self._devices[url].synced
end

--- Get device label
--- @tparam string url device's url
--- @return string device's label
function Model:getLabel(url)
  return self._devices[url].label
end

--- Get device generic model
--- @tparam string url device's url
--- @return table generic model
function Model:getDevice(url)
  local device = self._deviceSetup[url]
  if device ~= nil then
    return enhanceDevice(self, device)
  else
    return nil
  end
end

--- Get all device generic model
--- @return table generic model list
function Model:getDevices()
  local devices = {}
  for url, device in pairs(self._deviceSetup) do
    devices[url] = enhanceDevice(self, device)
  end
  return devices
end

local model = Model(Kizbox.id());
--- Set a device as synced
--- @tparam string url device's url
--- @tparam boolean synced synced state
--- @return boolean true if device updated
function Model:setSynced(url, synced)
  local devFound = self._devices[url]
  if not devFound then
    log:warning("Trying to set as synced a inexistant device: '"..url.."'.")
    return false
  end
  if not devFound.synced then
    devFound.synced = synced
    self._devices[url] = devFound -- write in storage
    if self.events.deviceUpdatedEvent then
      self.events.deviceUpdatedEvent({deviceURL = url});
    end
    log:notice("Set device '"..url.."' as synced.")
  end
  return true
end

--- Get synced state for a device
--- @tparam string url device's url
--- @return boolean true if synced
function Model:isSynced(url)
  if not self._devices[url] then
    return false
  end
  return self._devices[url].synced
end

--- Get device label
--- @tparam string url device's url
--- @return string device's label
function Model:getLabel(url)
  return self._devices[url].label
end

--- Get device generic model
--- @tparam string url device's url
--- @return table generic model
function Model:getDevice(url)
  local device = self._deviceSetup[url]
  if device ~= nil then
    return enhanceDevice(self, device)
  else
    return nil
  end
end

--- Get all device generic model
--- @return table generic model list
function Model:getDevices()
  local devices = {}
  for url, device in pairs(self._deviceSetup) do
    devices[url] = enhanceDevice(self, device)
  end
  return devices
end

local model = Model(Kizbox.id());
--- Set a device as synced
--- @tparam string url device's url
--- @tparam boolean synced synced state
--- @return boolean true if device updated
function Model:setSynced(url, synced)
  local devFound = self._devices[url]
  if not devFound then
    log:warning("Trying to set as synced a inexistant device: '"..url.."'.")
    return false
  end
  if not devFound.synced then
    devFound.synced = synced
    self._devices[url] = devFound -- write in storage
    if self.events.deviceUpdatedEvent then
      self.events.deviceUpdatedEvent({deviceURL = url});
    end
    log:notice("Set device '"..url.."' as synced.")
  end
  return true
end

--- Get synced state for a device
--- @tparam string url device's url
--- @return boolean true if synced
function Model:isSynced(url)
  if not self._devices[url] then
    return false
  end
  return self._devices[url].synced
end

--- Get device label
--- @tparam string url device's url
--- @return string device's label
function Model:getLabel(url)
  return self._devices[url].label
end

--- Get device generic model
--- @tparam string url device's url
--- @return table generic model
function Model:getDevice(url)
  local device = self._deviceSetup[url]
  if device ~= nil then
    return enhanceDevice(self, device)
  else
    return nil
  end
end

--- Get all device generic model
--- @return table generic model list
function Model:getDevices()
  local devices = {}
  for url, device in pairs(self._deviceSetup) do
    devices[url] = enhanceDevice(self, device)
  end
  return devices
end

local model = Model(Kizbox.id());
--- Set a device as synced
--- @tparam string url device's url
--- @tparam boolean synced synced state
--- @return boolean true if device updated
function Model:setSynced(url, synced)
  local devFound = self._devices[url]
  if not devFound then
    log:warning("Trying to set as synced a inexistant device: '"..url.."'.")
    return false
  end
  if not devFound.synced then
    devFound.synced = synced
    self._devices[url] = devFound -- write in storage
    if self.events.deviceUpdatedEvent then
      self.events.deviceUpdatedEvent({deviceURL = url});
    end
    log:notice("Set device '"..url.."' as synced.")
  end
  return true
end

--- Get synced state for a device
--- @tparam string url device's url
--- @return boolean true if synced
function Model:isSynced(url)
  if not self._devices[url] then
    return false
  end
  return self._devices[url].synced
end

--- Get device label
--- @tparam string url device's url
--- @return string device's label
function Model:getLabel(url)
  return self._devices[url].label
end

--- Get device generic model
--- @tparam string url device's url
--- @return table generic model
function Model:getDevice(url)
  local device = self._deviceSetup[url]
  if device ~= nil then
    return enhanceDevice(self, device)
  else
    return nil
  end
end

--- Get all device generic model
--- @return table generic model list
function Model:getDevices()
  local devices = {}
  for url, device in pairs(self._deviceSetup) do
    devices[url] = enhanceDevice(self, device)
  end
  return devices
end

local model = Model(Kizbox.id());
--- Set a device as synced
--- @tparam string url device's url
--- @tparam boolean synced synced state
--- @return boolean true if device updated
function Model:setSynced(url, synced)
  local devFound = self._devices[url]
  if not devFound then
    log:warning("Trying to set as synced a inexistant device: '"..url.."'.")
    return false
  end
  if not devFound.synced then
    devFound.synced = synced
    self._devices[url] = devFound -- write in storage
    if self.events.deviceUpdatedEvent then
      self.events.deviceUpdatedEvent({deviceURL = url});
    end
    log:notice("Set device '"..url.."' as synced.")
  end
  return true
end

--- Get synced state for a device
--- @tparam string url device's url
--- @return boolean true if synced
function Model:isSynced(url)
  if not self._devices[url] then
    return false
  end
  return self._devices[url].synced
end

--- Get device label
--- @tparam string url device's url
--- @return string device's label
function Model:getLabel(url)
  return self._devices[url].label
end

--- Get device generic model
--- @tparam string url device's url
--- @return table generic model
function Model:getDevice(url)
  local device = self._deviceSetup[url]
  if device ~= nil then
    return enhanceDevice(self, device)
  else
    return nil
  end
end

--- Get all device generic model
--- @return table generic model list
function Model:getDevices()
  local devices = {}
  for url, device in pairs(self._deviceSetup) do
    devices[url] = enhanceDevice(self, device)
  end
  return devices
end

local model = Model(Kizbox.id());
--- Set a device as synced
--- @tparam string url device's url
--- @tparam boolean synced synced state
--- @return boolean true if device updated
function Model:setSynced(url, synced)
  local devFound = self._devices[url]
  if not devFound then
    log:warning("Trying to set as synced a inexistant device: '"..url.."'.")
    return false
  end
  if not devFound.synced then
    devFound.synced = synced
    self._devices[url] = devFound -- write in storage
    if self.events.deviceUpdatedEvent then
      self.events.deviceUpdatedEvent({deviceURL = url});
    end
    log:notice("Set device '"..url.."' as synced.")
  end
  return true
end

--- Get synced state for a device
--- @tparam string url device's url
--- @return boolean true if synced
function Model:isSynced(url)
  if not self._devices[url] then
    return false
  end
  return self._devices[url].synced
end

--- Get device label
--- @tparam string url device's url
--- @return string device's label
function Model:getLabel(url)
  return self._devices[url].label
end

--- Get device generic model
--- @tparam string url device's url
--- @return table generic model
function Model:getDevice(url)
  local device = self._deviceSetup[url]
  if device ~= nil then
    return enhanceDevice(self, device)
  else
    return nil
  end
end

--- Get all device generic model
--- @return table generic model list
function Model:getDevices()
  local devices = {}
  for url, device in pairs(self._deviceSetup) do
    devices[url] = enhanceDevice(self, device)
  end
  return devices
end

local model = Model(Kizbox.id());
--- Set a device as synced
--- @tparam string url device's url
--- @tparam boolean synced synced state
--- @return boolean true if device updated
function Model:setSynced(url, synced)
  local devFound = self._devices[url]
  if not devFound then
    log:warning("Trying to set as synced a inexistant device: '"..url.."'.")
    return false
  end
  if not devFound.synced then
    devFound.synced = synced
    self._devices[url] = devFound -- write in storage
    if self.events.deviceUpdatedEvent then
      self.events.deviceUpdatedEvent({deviceURL = url});
    end
    log:notice("Set device '"..url.."' as synced.")
  end
  return true
end

--- Get synced state for a device
--- @tparam string url device's url
--- @return boolean true if synced
function Model:isSynced(url)
  if not self._devices[url] then
    return false
  end
  return self._devices[url].synced
end

--- Get device label
--- @tparam string url device's url
--- @return string device's label
function Model:getLabel(url)
  return self._devices[url].label
end

--- Get device generic model
--- @tparam string url device's url
--- @return table generic model
function Model:getDevice(url)
  local device = self._deviceSetup[url]
  if device ~= nil then
    return enhanceDevice(self, device)
  else
    return nil
  end
end

--- Get all device generic model
--- @return table generic model list
function Model:getDevices()
  local devices = {}
  for url, device in pairs(self._deviceSetup) do
    devices[url] = enhanceDevice(self, device)
  end
  return devices
end

local model = Model(Kizbox.id());
--- Set a device as synced
--- @tparam string url device's url
--- @tparam boolean synced synced state
--- @return boolean true if device updated
function Model:setSynced(url, synced)
  local devFound = self._devices[url]
  if not devFound then
    log:warning("Trying to set as synced a inexistant device: '"..url.."'.")
    return false
  end
  if not devFound.synced then
    devFound.synced = synced
    self._devices[url] = devFound -- write in storage
    if self.events.deviceUpdatedEvent then
      self.events.deviceUpdatedEvent({deviceURL = url});
    end
    log:notice("Set device '"..url.."' as synced.")
  end
  return true
end

--- Get synced state for a device
--- @tparam string url device's url
--- @return boolean true if synced
function Model:isSynced(url)
  if not self._devices[url] then
    return false
  end
  return self._devices[url].synced
end

--- Get device label
--- @tparam string url device's url
--- @return string device's label
function Model:getLabel(url)
  return self._devices[url].label
end

--- Get device generic model
--- @tparam string url device's url
--- @return table generic model
function Model:getDevice(url)
  local device = self._deviceSetup[url]
  if device ~= nil then
    return enhanceDevice(self, device)
  else
    return nil
  end
end

--- Get all device generic model
--- @return table generic model list
function Model:getDevices()
  local devices = {}
  for url, device in pairs(self._deviceSetup) do
    devices[url] = enhanceDevice(self, device)
  end
  return devices
end

local model = Model(Kizbox.id());
--- Set a device as synced
--- @tparam string url device's url
--- @tparam boolean synced synced state
--- @return boolean true if device updated
function Model:setSynced(url, synced)
  local devFound = self._devices[url]
  if not devFound then
    log:warning("Trying to set as synced a inexistant device: '"..url.."'.")
    return false
  end
  if not devFound.synced then
    devFound.synced = synced
    self._devices[url] = devFound -- write in storage
    if self.events.deviceUpdatedEvent then
      self.events.deviceUpdatedEvent({deviceURL = url});
    end
    log:notice("Set device '"..url.."' as synced.")
  end
  return true
end

--- Get synced state for a device
--- @tparam string url device's url
--- @return boolean true if synced
function Model:isSynced(url)
  if not self._devices[url] then
    return false
  end
  return self._devices[url].synced
end

--- Get device label
--- @tparam string url device's url
--- @return string device's label
function Model:getLabel(url)
  return self._devices[url].label
end

--- Get device generic model
--- @tparam string url device's url
--- @return table generic model
function Model:getDevice(url)
  local device = self._deviceSetup[url]
  if device ~= nil then
    return enhanceDevice(self, device)
  else
    return nil
  end
end

--- Get all device generic model
--- @return table generic model list
function Model:getDevices()
  local devices = {}
  for url, device in pairs(self._deviceSetup) do
    devices[url] = enhanceDevice(self, device)
  end
  return devices
end

local model = Model(Kizbox.id());
--- Set a device as synced
--- @tparam string url device's url
--- @tparam boolean synced synced state
--- @return boolean true if device updated
function Model:setSynced(url, synced)
  local devFound = self._devices[url]
  if not devFound then
    log:warning("Trying to set as synced a inexistant device: '"..url.."'.")
    return false
  end
  if not devFound.synced then
    devFound.synced = synced
    self._devices[url] = devFound -- write in storage
    if self.events.deviceUpdatedEvent then
      self.events.deviceUpdatedEvent({deviceURL = url});
    end
    log:notice("Set device '"..url.."' as synced.")
  end
  return true
end

--- Get synced state for a device
--- @tparam string url device's url
--- @return boolean true if synced
function Model:isSynced(url)
  if not self._devices[url] then
    return false
  end
  return self._devices[url].synced
end

--- Get device label
--- @tparam string url device's url
--- @return string device's label
function Model:getLabel(url)
  return self._devices[url].label
end

--- Get device generic model
--- @tparam string url device's url
--- @return table generic model
function Model:getDevice(url)
  local device = self._deviceSetup[url]
  if device ~= nil then
    return enhanceDevice(self, device)
  else
    return nil
  end
end

--- Get all device generic model
--- @return table generic model list
function Model:getDevices()
  local devices = {}
  for url, device in pairs(self._deviceSetup) do
    devices[url] = enhanceDevice(self, device)
  end
  return devices
end

local model = Model(Kizbox.id());
--- Set a device as synced
--- @tparam string url device's url
--- @tparam boolean synced synced state
--- @return boolean true if device updated
function Model:setSynced(url, synced)
  local devFound = self._devices[url]
  if not devFound then
    log:warning("Trying to set as synced a inexistant device: '"..url.."'.")
    return false
  end
  if not devFound.synced then
    devFound.synced = synced
    self._devices[url] = devFound -- write in storage
    if self.events.deviceUpdatedEvent then
      self.events.deviceUpdatedEvent({deviceURL = url});
    end
    log:notice("Set device '"..url.."' as synced.")
  end
  return true
end

--- Get synced state for a device
--- @tparam string url device's url
--- @return boolean true if synced
function Model:isSynced(url)
  if not self._devices[url] then
    return false
  end
  return self._devices[url].synced
end

--- Get device label
--- @tparam string url device's url
--- @return string device's label
function Model:getLabel(url)
  return self._devices[url].label
end

--- Get device generic model
--- @tparam string url device's url
--- @return table generic model
function Model:getDevice(url)
  local device = self._deviceSetup[url]
  if device ~= nil then
    return enhanceDevice(self, device)
  else
    return nil
  end
end

--- Get all device generic model
--- @return table generic model list
function Model:getDevices()
  local devices = {}
  for url, device in pairs(self._deviceSetup) do
    devices[url] = enhanceDevice(self, device)
  end
  return devices
end

local model = Model(Kizbox.id());
--- Set a device as synced
--- @tparam string url device's url
--- @tparam boolean synced synced state
--- @return boolean true if device updated
function Model:setSynced(url, synced)
  local devFound = self._devices[url]
  if not devFound then
    log:warning("Trying to set as synced a inexistant device: '"..url.."'.")
    return false
  end
  if not devFound.synced then
    devFound.synced = synced
    self._devices[url] = devFound -- write in storage
    if self.events.deviceUpdatedEvent then
      self.events.deviceUpdatedEvent({deviceURL = url});
    end
    log:notice("Set device '"..url.."' as synced.")
  end
  return true
end

--- Get synced state for a device
--- @tparam string url device's url
--- @return boolean true if synced
function Model:isSynced(url)
  if not self._devices[url] then
    return false
  end
  return self._devices[url].synced
end

--- Get device label
--- @tparam string url device's url
--- @return string device's label
function Model:getLabel(url)
  return self._devices[url].label
end

--- Get device generic model
--- @tparam string url device's url
--- @return table generic model
function Model:getDevice(url)
  local device = self._deviceSetup[url]
  if device ~= nil then
    return enhanceDevice(self, device)
  else
    return nil
  end
end

--- Get all device generic model
--- @return table generic model list
function Model:getDevices()
  local devices = {}
  for url, device in pairs(self._deviceSetup) do
    devices[url] = enhanceDevice(self, device)
  end
  return devices
end

local model = Model(Kizbox.id());
--- Set a device as synced
--- @tparam string url device's url
--- @tparam boolean synced synced state
--- @return boolean true if device updated
function Model:setSynced(url, synced)
  local devFound = self._devices[url]
  if not devFound then
    log:warning("Trying to set as synced a inexistant device: '"..url.."'.")
    return false
  end
  if not devFound.synced then
    devFound.synced = synced
    self._devices[url] = devFound -- write in storage
    if self.events.deviceUpdatedEvent then
      self.events.deviceUpdatedEvent({deviceURL = url});
    end
    log:notice("Set device '"..url.."' as synced.")
  end
  return true
end

--- Get synced state for a device
--- @tparam string url device's url
--- @return boolean true if synced
function Model:isSynced(url)
  if not self._devices[url] then
    return false
  end
  return self._devices[url].synced
end

--- Get device label
--- @tparam string url device's url
--- @return string device's label
function Model:getLabel(url)
  return self._devices[url].label
end

--- Get device generic model
--- @tparam string url device's url
--- @return table generic model
function Model:getDevice(url)
  local device = self._deviceSetup[url]
  if device ~= nil then
    return enhanceDevice(self, device)
  else
    return nil
  end
end

--- Get all device generic model
--- @return table generic model list
function Model:getDevices()
  local devices = {}
  for url, device in pairs(self._deviceSetup) do
    devices[url] = enhanceDevice(self, device)
  end
  return devices
end

local model = Model(Kizbox.id());
--- Set a device as synced
--- @tparam string url device's url
--- @tparam boolean synced synced state
--- @return boolean true if device updated
function Model:setSynced(url, synced)
  local devFound = self._devices[url]
  if not devFound then
    log:warning("Trying to set as synced a inexistant device: '"..url.."'.")
    return false
  end
  if not devFound.synced then
    devFound.synced = synced
    self._devices[url] = devFound -- write in storage
    if self.events.deviceUpdatedEvent then
      self.events.deviceUpdatedEvent({deviceURL = url});
    end
    log:notice("Set device '"..url.."' as synced.")
  end
  return true
end

--- Get synced state for a device
--- @tparam string url device's url
--- @return boolean true if synced
function Model:isSynced(url)
  if not self._devices[url] then
    return false
  end
  return self._devices[url].synced
end

--- Get device label
--- @tparam string url device's url
--- @return string device's label
function Model:getLabel(url)
  return self._devices[url].label
end

--- Get device generic model
--- @tparam string url device's url
--- @return table generic model
function Model:getDevice(url)
  local device = self._deviceSetup[url]
  if device ~= nil then
    return enhanceDevice(self, device)
  else
    return nil
  end
end

--- Get all device generic model
--- @return table generic model list
function Model:getDevices()
  local devices = {}
  for url, device in pairs(self._deviceSetup) do
    devices[url] = enhanceDevice(self, device)
  end
  return devices
end

local model = Model(Kizbox.id());
--- Set a device as synced
--- @tparam string url device's url
--- @tparam boolean synced synced state
--- @return boolean true if device updated
function Model:setSynced(url, synced)
  local devFound = self._devices[url]
  if not devFound then
    log:warning("Trying to set as synced a inexistant device: '"..url.."'.")
    return false
  end
  if not devFound.synced then
    devFound.synced = synced
    self._devices[url] = devFound -- write in storage
    if self.events.deviceUpdatedEvent then
      self.events.deviceUpdatedEvent({deviceURL = url});
    end
    log:notice("Set device '"..url.."' as synced.")
  end
  return true
end

--- Get synced state for a device
--- @tparam string url device's url
--- @return boolean true if synced
function Model:isSynced(url)
  if not self._devices[url] then
    return false
  end
  return self._devices[url].synced
end

--- Get device label
--- @tparam string url device's url
--- @return string device's label
function Model:getLabel(url)
  return self._devices[url].label
end

--- Get device generic model
--- @tparam string url device's url
--- @return table generic model
function Model:getDevice(url)
  local device = self._deviceSetup[url]
  if device ~= nil then
    return enhanceDevice(self, device)
  else
    return nil
  end
end

--- Get all device generic model
--- @return table generic model list
function Model:getDevices()
  local devices = {}
  for url, device in pairs(self._deviceSetup) do
    devices[url] = enhanceDevice(self, device)
  end
  return devices
end

local model = Model(Kizbox.id());
--- Set a device as synced
--- @tparam string url device's url
--- @tparam boolean synced synced state
--- @return boolean true if device updated
function Model:setSynced(url, synced)
  local devFound = self._devices[url]
  if not devFound then
    log:warning("Trying to set as synced a inexistant device: '"..url.."'.")
    return false
  end
  if not devFound.synced then
    devFound.synced = synced
    self._devices[url] = devFound -- write in storage
    if self.events.deviceUpdatedEvent then
      self.events.deviceUpdatedEvent({deviceURL = url});
    end
    log:notice("Set device '"..url.."' as synced.")
  end
  return true
end

--- Get synced state for a device
--- @tparam string url device's url
--- @return boolean true if synced
function Model:isSynced(url)
  if not self._devices[url] then
    return false
  end
  return self._devices[url].synced
end

--- Get device label
--- @tparam string url device's url
--- @return string device's label
function Model:getLabel(url)
  return self._devices[url].label
end

--- Get device generic model
--- @tparam string url device's url
--- @return table generic model
function Model:getDevice(url)
  local device = self._deviceSetup[url]
  if device ~= nil then
    return enhanceDevice(self, device)
  else
    return nil
  end
end

--- Get all device generic model
--- @return table generic model list
function Model:getDevices()
  local devices = {}
  for url, device in pairs(self._deviceSetup) do
    devices[url] = enhanceDevice(self, device)
  end
  return devices
end

local model = Model(Kizbox.id());
--- Set a device as synced
--- @tparam string url device's url
--- @tparam boolean synced synced state
--- @return boolean true if device updated
function Model:setSynced(url, synced)
  local devFound = self._devices[url]
  if not devFound then
    log:warning("Trying to set as synced a inexistant device: '"..url.."'.")
    return false
  end
  if not devFound.synced then
    devFound.synced = synced
    self._devices[url] = devFound -- write in storage
    if self.events.deviceUpdatedEvent then
      self.events.deviceUpdatedEvent({deviceURL = url});
    end
    log:notice("Set device '"..url.."' as synced.")
  end
  return true
end

--- Get synced state for a device
--- @tparam string url device's url
--- @return boolean true if synced
function Model:isSynced(url)
  if not self._devices[url] then
    return false
  end
  return self._devices[url].synced
end

--- Get device label
--- @tparam string url device's url
--- @return string device's label
function Model:getLabel(url)
  return self._devices[url].label
end

--- Get device generic model
--- @tparam string url device's url
--- @return table generic model
function Model:getDevice(url)
  local device = self._deviceSetup[url]
  if device ~= nil then
    return enhanceDevice(self, device)
  else
    return nil
  end
end

--- Get all device generic model
--- @return table generic model list
function Model:getDevices()
  local devices = {}
  for url, device in pairs(self._deviceSetup) do
    devices[url] = enhanceDevice(self, device)
  end
  return devices
end

local model = Model(Kizbox.id());
--- Set a device as synced
--- @tparam string url device's url
--- @tparam boolean synced synced state
--- @return boolean true if device updated
function Model:setSynced(url, synced)
  local devFound = self._devices[url]
  if not devFound then
    log:warning("Trying to set as synced a inexistant device: '"..url.."'.")
    return false
  end
  if not devFound.synced then
    devFound.synced = synced
    self._devices[url] = devFound -- write in storage
    if self.events.deviceUpdatedEvent then
      self.events.deviceUpdatedEvent({deviceURL = url});
    end
    log:notice("Set device '"..url.."' as synced.")
  end
  return true
end

--- Get synced state for a device
--- @tparam string url device's url
--- @return boolean true if synced
function Model:isSynced(url)
  if not self._devices[url] then
    return false
  end
  return self._devices[url].synced
end

--- Get device label
--- @tparam string url device's url
--- @return string device's label
function Model:getLabel(url)
  return self._devices[url].label
end

--- Get device generic model
--- @tparam string url device's url
--- @return table generic model
function Model:getDevice(url)
  local device = self._deviceSetup[url]
  if device ~= nil then
    return enhanceDevice(self, device)
  else
    return nil
  end
end

--- Get all device generic model
--- @return table generic model list
function Model:getDevices()
  local devices = {}
  for url, device in pairs(self._deviceSetup) do
    devices[url] = enhanceDevice(self, device)
  end
  return devices
end

local model = Model(Kizbox.id());
--- Set a device as synced
--- @tparam string url device's url
--- @tparam boolean synced synced state
--- @return boolean true if device updated
function Model:setSynced(url, synced)
  local devFound = self._devices[url]
  if not devFound then
    log:warning("Trying to set as synced a inexistant device: '"..url.."'.")
    return false
  end
  if not devFound.synced then
    devFound.synced = synced
    self._devices[url] = devFound -- write in storage
    if self.events.deviceUpdatedEvent then
      self.events.deviceUpdatedEvent({deviceURL = url});
    end
    log:notice("Set device '"..url.."' as synced.")
  end
  return true
end

--- Get synced state for a device
--- @tparam string url device's url
--- @return boolean true if synced
function Model:isSynced(url)
  if not self._devices[url] then
    return false
  end
  return self._devices[url].synced
end

--- Get device label
--- @tparam string url device's url
--- @return string device's label
function Model:getLabel(url)
  return self._devices[url].label
end

--- Get device generic model
--- @tparam string url device's url
--- @return table generic model
function Model:getDevice(url)
  local device = self._deviceSetup[url]
  if device ~= nil then
    return enhanceDevice(self, device)
  else
    return nil
  end
end

--- Get all device generic model
--- @return table generic model list
function Model:getDevices()
  local devices = {}
  for url, device in pairs(self._deviceSetup) do
    devices[url] = enhanceDevice(self, device)
  end
  return devices
end

local model = Model(Kizbox.id());
--- Set a device as synced
--- @tparam string url device's url
--- @tparam boolean synced synced state
--- @return boolean true if device updated
function Model:setSynced(url, synced)
  local devFound = self._devices[url]
  if not devFound then
    log:warning("Trying to set as synced a inexistant device: '"..url.."'.")
    return false
  end
  if not devFound.synced then
    devFound.synced = synced
    self._devices[url] = devFound -- write in storage
    if self.events.deviceUpdatedEvent then
      self.events.deviceUpdatedEvent({deviceURL = url});
    end
    log:notice("Set device '"..url.."' as synced.")
  end
  return true
end

--- Get synced state for a device
--- @tparam string url device's url
--- @return boolean true if synced
function Model:isSynced(url)
  if not self._devices[url] then
    return false
  end
  return self._devices[url].synced
end

--- Get device label
--- @tparam string url device's url
--- @return string device's label
function Model:getLabel(url)
  return self._devices[url].label
end

--- Get device generic model
--- @tparam string url device's url
--- @return table generic model
function Model:getDevice(url)
  local device = self._deviceSetup[url]
  if device ~= nil then
    return enhanceDevice(self, device)
  else
    return nil
  end
end

--- Get all device generic model
--- @return table generic model list
function Model:getDevices()
  local devices = {}
  for url, device in pairs(self._deviceSetup) do
    devices[url] = enhanceDevice(self, device)
  end
  return devices
end

local model = Model(Kizbox.id());
--- Set a device as synced
--- @tparam string url device's url
--- @tparam boolean synced synced state
--- @return boolean true if device updated
function Model:setSynced(url, synced)
  local devFound = self._devices[url]
  if not devFound then
    log:warning("Trying to set as synced a inexistant device: '"..url.."'.")
    return false
  end
  if not devFound.synced then
    devFound.synced = synced
    self._devices[url] = devFound -- write in storage
    if self.events.deviceUpdatedEvent then
      self.events.deviceUpdatedEvent({deviceURL = url});
    end
    log:notice("Set device '"..url.."' as synced.")
  end
  return true
end

--- Get synced state for a device
--- @tparam string url device's url
--- @return boolean true if synced
function Model:isSynced(url)
  if not self._devices[url] then
    return false
  end
  return self._devices[url].synced
end

--- Get device label
--- @tparam string url device's url
--- @return string device's label
function Model:getLabel(url)
  return self._devices[url].label
end

--- Get device generic model
--- @tparam string url device's url
--- @return table generic model
function Model:getDevice(url)
  local device = self._deviceSetup[url]
  if device ~= nil then
    return enhanceDevice(self, device)
  else
    return nil
  end
end

--- Get all device generic model
--- @return table generic model list
function Model:getDevices()
  local devices = {}
  for url, device in pairs(self._deviceSetup) do
    devices[url] = enhanceDevice(self, device)
  end
  return devices
end

local model = Model(Kizbox.id());
--- Set a device as synced
--- @tparam string url device's url
--- @tparam boolean synced synced state
--- @return boolean true if device updated
function Model:setSynced(url, synced)
  local devFound = self._devices[url]
  if not devFound then
    log:warning("Trying to set as synced a inexistant device: '"..url.."'.")
    return false
  end
  if not devFound.synced then
    devFound.synced = synced
    self._devices[url] = devFound -- write in storage
    if self.events.deviceUpdatedEvent then
      self.events.deviceUpdatedEvent({deviceURL = url});
    end
    log:notice("Set device '"..url.."' as synced.")
  end
  return true
end

--- Get synced state for a device
--- @tparam string url device's url
--- @return boolean true if synced
function Model:isSynced(url)
  if not self._devices[url] then
    return false
  end
  return self._devices[url].synced
end

--- Get device label
--- @tparam string url device's url
--- @return string device's label
function Model:getLabel(url)
  return self._devices[url].label
end

--- Get device generic model
--- @tparam string url device's url
--- @return table generic model
function Model:getDevice(url)
  local device = self._deviceSetup[url]
  if device ~= nil then
    return enhanceDevice(self, device)
  else
    return nil
  end
end

--- Get all device generic model
--- @return table generic model list
function Model:getDevices()
  local devices = {}
  for url, device in pairs(self._deviceSetup) do
    devices[url] = enhanceDevice(self, device)
  end
  return devices
end

local model = Model(Kizbox.id());
--- Set a device as synced
--- @tparam string url device's url
--- @tparam boolean synced synced state
--- @return boolean true if device updated
function Model:setSynced(url, synced)
  local devFound = self._devices[url]
  if not devFound then
    log:warning("Trying to set as synced a inexistant device: '"..url.."'.")
    return false
  end
  if not devFound.synced then
    devFound.synced = synced
    self._devices[url] = devFound -- write in storage
    if self.events.deviceUpdatedEvent then
      self.events.deviceUpdatedEvent({deviceURL = url});
    end
    log:notice("Set device '"..url.."' as synced.")
  end
  return true
end

--- Get synced state for a device
--- @tparam string url device's url
--- @return boolean true if synced
function Model:isSynced(url)
  if not self._devices[url] then
    return false
  end
  return self._devices[url].synced
end

--- Get device label
--- @tparam string url device's url
--- @return string device's label
function Model:getLabel(url)
  return self._devices[url].label
end

--- Get device generic model
--- @tparam string url device's url
--- @return table generic model
function Model:getDevice(url)
  local device = self._deviceSetup[url]
  if device ~= nil then
    return enhanceDevice(self, device)
  else
    return nil
  end
end

--- Get all device generic model
--- @return table generic model list
function Model:getDevices()
  local devices = {}
  for url, device in pairs(self._deviceSetup) do
    devices[url] = enhanceDevice(self, device)
  end
  return devices
end

local model = Model(Kizbox.id());
--- Set a device as synced
--- @tparam string url device's url
--- @tparam boolean synced synced state
--- @return boolean true if device updated
function Model:setSynced(url, synced)
  local devFound = self._devices[url]
  if not devFound then
    log:warning("Trying to set as synced a inexistant device: '"..url.."'.")
    return false
  end
  if not devFound.synced then
    devFound.synced = synced
    self._devices[url] = devFound -- write in storage
    if self.events.deviceUpdatedEvent then
      self.events.deviceUpdatedEvent({deviceURL = url});
    end
    log:notice("Set device '"..url.."' as synced.")
  end
  return true
end

--- Get synced state for a device
--- @tparam string url device's url
--- @return boolean true if synced
function Model:isSynced(url)
  if not self._devices[url] then
    return false
  end
  return self._devices[url].synced
end

--- Get device label
--- @tparam string url device's url
--- @return string device's label
function Model:getLabel(url)
  return self._devices[url].label
end

--- Get device generic model
--- @tparam string url device's url
--- @return table generic model
function Model:getDevice(url)
  local device = self._deviceSetup[url]
  if device ~= nil then
    return enhanceDevice(self, device)
  else
    return nil
  end
end

--- Get all device generic model
--- @return table generic model list
function Model:getDevices()
  local devices = {}
  for url, device in pairs(self._deviceSetup) do
    devices[url] = enhanceDevice(self, device)
  end
  return devices
end

local model = Model(Kizbox.id());
--- Set a device as synced
--- @tparam string url device's url
--- @tparam boolean synced synced state
--- @return boolean true if device updated
function Model:setSynced(url, synced)
  local devFound = self._devices[url]
  if not devFound then
    log:warning("Trying to set as synced a inexistant device: '"..url.."'.")
    return false
  end
  if not devFound.synced then
    devFound.synced = synced
    self._devices[url] = devFound -- write in storage
    if self.events.deviceUpdatedEvent then
      self.events.deviceUpdatedEvent({deviceURL = url});
    end
    log:notice("Set device '"..url.."' as synced.")
  end
  return true
end

--- Get synced state for a device
--- @tparam string url device's url
--- @return boolean true if synced
function Model:isSynced(url)
  if not self._devices[url] then
    return false
  end
  return self._devices[url].synced
end

--- Get device label
--- @tparam string url device's url
--- @return string device's label
function Model:getLabel(url)
  return self._devices[url].label
end

--- Get device generic model
--- @tparam string url device's url
--- @return table generic model
function Model:getDevice(url)
  local device = self._deviceSetup[url]
  if device ~= nil then
    return enhanceDevice(self, device)
  else
    return nil
  end
end

--- Get all device generic model
--- @return table generic model list
function Model:getDevices()
  local devices = {}
  for url, device in pairs(self._deviceSetup) do
    devices[url] = enhanceDevice(self, device)
  end
  return devices
end

local model = Model(Kizbox.id());
--- Set a device as synced
--- @tparam string url device's url
--- @tparam boolean synced synced state
--- @return boolean true if device updated
function Model:setSynced(url, synced)
  local devFound = self._devices[url]
  if not devFound then
    log:warning("Trying to set as synced a inexistant device: '"..url.."'.")
    return false
  end
  if not devFound.synced then
    devFound.synced = synced
    self._devices[url] = devFound -- write in storage
    if self.events.deviceUpdatedEvent then
      self.events.deviceUpdatedEvent({deviceURL = url});
    end
    log:notice("Set device '"..url.."' as synced.")
  end
  return true
end

--- Get synced state for a device
--- @tparam string url device's url
--- @return boolean true if synced
function Model:isSynced(url)
  if not self._devices[url] then
    return false
  end
  return self._devices[url].synced
end

--- Get device label
--- @tparam string url device's url
--- @return string device's label
function Model:getLabel(url)
  return self._devices[url].label
end

--- Get device generic model
--- @tparam string url device's url
--- @return table generic model
function Model:getDevice(url)
  local device = self._deviceSetup[url]
  if device ~= nil then
    return enhanceDevice(self, device)
  else
    return nil
  end
end

--- Get all device generic model
--- @return table generic model list
function Model:getDevices()
  local devices = {}
  for url, device in pairs(self._deviceSetup) do
    devices[url] = enhanceDevice(self, device)
  end
  return devices
end

local model = Model(Kizbox.id());
--- Set a device as synced
--- @tparam string url device's url
--- @tparam boolean synced synced state
--- @return boolean true if device updated
function Model:setSynced(url, synced)
  local devFound = self._devices[url]
  if not devFound then
    log:warning("Trying to set as synced a inexistant device: '"..url.."'.")
    return false
  end
  if not devFound.synced then
    devFound.synced = synced
    self._devices[url] = devFound -- write in storage
    if self.events.deviceUpdatedEvent then
      self.events.deviceUpdatedEvent({deviceURL = url});
    end
    log:notice("Set device '"..url.."' as synced.")
  end
  return true
end

--- Get synced state for a device
--- @tparam string url device's url
--- @return boolean true if synced
function Model:isSynced(url)
  if not self._devices[url] then
    return false
  end
  return self._devices[url].synced
end

--- Get device label
--- @tparam string url device's url
--- @return string device's label
function Model:getLabel(url)
  return self._devices[url].label
end

--- Get device generic model
--- @tparam string url device's url
--- @return table generic model
function Model:getDevice(url)
  local device = self._deviceSetup[url]
  if device ~= nil then
    return enhanceDevice(self, device)
  else
    return nil
  end
end

--- Get all device generic model
--- @return table generic model list
function Model:getDevices()
  local devices = {}
  for url, device in pairs(self._deviceSetup) do
    devices[url] = enhanceDevice(self, device)
  end
  return devices
end

local model = Model(Kizbox.id());
--- Set a device as synced
--- @tparam string url device's url
--- @tparam boolean synced synced state
--- @return boolean true if device updated
function Model:setSynced(url, synced)
  local devFound = self._devices[url]
  if not devFound then
    log:warning("Trying to set as synced a inexistant device: '"..url.."'.")
    return false
  end
  if not devFound.synced then
    devFound.synced = synced
    self._devices[url] = devFound -- write in storage
    if self.events.deviceUpdatedEvent then
      self.events.deviceUpdatedEvent({deviceURL = url});
    end
    log:notice("Set device '"..url.."' as synced.")
  end
  return true
end

--- Get synced state for a device
--- @tparam string url device's url
--- @return boolean true if synced
function Model:isSynced(url)
  if not self._devices[url] then
    return false
  end
  return self._devices[url].synced
end

--- Get device label
--- @tparam string url device's url
--- @return string device's label
function Model:getLabel(url)
  return self._devices[url].label
end

--- Get device generic model
--- @tparam string url device's url
--- @return table generic model
function Model:getDevice(url)
  local device = self._deviceSetup[url]
  if device ~= nil then
    return enhanceDevice(self, device)
  else
    return nil
  end
end

--- Get all device generic model
--- @return table generic model list
function Model:getDevices()
  local devices = {}
  for url, device in pairs(self._deviceSetup) do
    devices[url] = enhanceDevice(self, device)
  end
  return devices
end

local model = Model(Kizbox.id());
--- Set a device as synced
--- @tparam string url device's url
--- @tparam boolean synced synced state
--- @return boolean true if device updated
function Model:setSynced(url, synced)
  local devFound = self._devices[url]
  if not devFound then
    log:warning("Trying to set as synced a inexistant device: '"..url.."'.")
    return false
  end
  if not devFound.synced then
    devFound.synced = synced
    self._devices[url] = devFound -- write in storage
    if self.events.deviceUpdatedEvent then
      self.events.deviceUpdatedEvent({deviceURL = url});
    end
    log:notice("Set device '"..url.."' as synced.")
  end
  return true
end

--- Get synced state for a device
--- @tparam string url device's url
--- @return boolean true if synced
function Model:isSynced(url)
  if not self._devices[url] then
    return false
  end
  return self._devices[url].synced
end

--- Get device label
--- @tparam string url device's url
--- @return string device's label
function Model:getLabel(url)
  return self._devices[url].label
end

--- Get device generic model
--- @tparam string url device's url
--- @return table generic model
function Model:getDevice(url)
  local device = self._deviceSetup[url]
  if device ~= nil then
    return enhanceDevice(self, device)
  else
    return nil
  end
end

--- Get all device generic model
--- @return table generic model list
function Model:getDevices()
  local devices = {}
  for url, device in pairs(self._deviceSetup) do
    devices[url] = enhanceDevice(self, device)
  end
  return devices
end

local model = Model(Kizbox.id());
--- Set a device as synced
--- @tparam string url device's url
--- @tparam boolean synced synced state
--- @return boolean true if device updated
function Model:setSynced(url, synced)
  local devFound = self._devices[url]
  if not devFound then
    log:warning("Trying to set as synced a inexistant device: '"..url.."'.")
    return false
  end
  if not devFound.synced then
    devFound.synced = synced
    self._devices[url] = devFound -- write in storage
    if self.events.deviceUpdatedEvent then
      self.events.deviceUpdatedEvent({deviceURL = url});
    end
    log:notice("Set device '"..url.."' as synced.")
  end
  return true
end

--- Get synced state for a device
--- @tparam string url device's url
--- @return boolean true if synced
function Model:isSynced(url)
  if not self._devices[url] then
    return false
  end
  return self._devices[url].synced
end

--- Get device label
--- @tparam string url device's url
--- @return string device's label
function Model:getLabel(url)
  return self._devices[url].label
end

--- Get device generic model
--- @tparam string url device's url
--- @return table generic model
function Model:getDevice(url)
  local device = self._deviceSetup[url]
  if device ~= nil then
    return enhanceDevice(self, device)
  else
    return nil
  end
end

--- Get all device generic model
--- @return table generic model list
function Model:getDevices()
  local devices = {}
  for url, device in pairs(self._deviceSetup) do
    devices[url] = enhanceDevice(self, device)
  end
  return devices
end

local model = Model(Kizbox.id());
--- Set a device as synced
--- @tparam string url device's url
--- @tparam boolean synced synced state
--- @return boolean true if device updated
function Model:setSynced(url, synced)
  local devFound = self._devices[url]
  if not devFound then
    log:warning("Trying to set as synced a inexistant device: '"..url.."'.")
    return false
  end
  if not devFound.synced then
    devFound.synced = synced
    self._devices[url] = devFound -- write in storage
    if self.events.deviceUpdatedEvent then
      self.events.deviceUpdatedEvent({deviceURL = url});
    end
    log:notice("Set device '"..url.."' as synced.")
  end
  return true
end

--- Get synced state for a device
--- @tparam string url device's url
--- @return boolean true if synced
function Model:isSynced(url)
  if not self._devices[url] then
    return false
  end
  return self._devices[url].synced
end

--- Get device label
--- @tparam string url device's url
--- @return string device's label
function Model:getLabel(url)
  return self._devices[url].label
end

--- Get device generic model
--- @tparam string url device's url
--- @return table generic model
function Model:getDevice(url)
  local device = self._deviceSetup[url]
  if device ~= nil then
    return enhanceDevice(self, device)
  else
    return nil
  end
end

--- Get all device generic model
--- @return table generic model list
function Model:getDevices()
  local devices = {}
  for url, device in pairs(self._deviceSetup) do
    devices[url] = enhanceDevice(self, device)
  end
  return devices
end

local model = Model(Kizbox.id());
--- Set a device as synced
--- @tparam string url device's url
--- @tparam boolean synced synced state
--- @return boolean true if device updated
function Model:setSynced(url, synced)
  local devFound = self._devices[url]
  if not devFound then
    log:warning("Trying to set as synced a inexistant device: '"..url.."'.")
    return false
  end
  if not devFound.synced then
    devFound.synced = synced
    self._devices[url] = devFound -- write in storage
    if self.events.deviceUpdatedEvent then
      self.events.deviceUpdatedEvent({deviceURL = url});
    end
    log:notice("Set device '"..url.."' as synced.")
  end
  return true
end

--- Get synced state for a device
--- @tparam string url device's url
--- @return boolean true if synced
function Model:isSynced(url)
  if not self._devices[url] then
    return false
  end
  return self._devices[url].synced
end

--- Get device label
--- @tparam string url device's url
--- @return string device's label
function Model:getLabel(url)
  return self._devices[url].label
end

--- Get device generic model
--- @tparam string url device's url
--- @return table generic model
function Model:getDevice(url)
  local device = self._deviceSetup[url]
  if device ~= nil then
    return enhanceDevice(self, device)
  else
    return nil
  end
end

--- Get all device generic model
--- @return table generic model list
function Model:getDevices()
  local devices = {}
  for url, device in pairs(self._deviceSetup) do
    devices[url] = enhanceDevice(self, device)
  end
  return devices
end

local model = Model(Kizbox.id());
--- Set a device as synced
--- @tparam string url device's url
--- @tparam boolean synced synced state
--- @return boolean true if device updated
function Model:setSynced(url, synced)
  local devFound = self._devices[url]
  if not devFound then
    log:warning("Trying to set as synced a inexistant device: '"..url.."'.")
    return false
  end
  if not devFound.synced then
    devFound.synced = synced
    self._devices[url] = devFound -- write in storage
    if self.events.deviceUpdatedEvent then
      self.events.deviceUpdatedEvent({deviceURL = url});
    end
    log:notice("Set device '"..url.."' as synced.")
  end
  return true
end

--- Get synced state for a device
--- @tparam string url device's url
--- @return boolean true if synced
function Model:isSynced(url)
  if not self._devices[url] then
    return false
  end
  return self._devices[url].synced
end

--- Get device label
--- @tparam string url device's url
--- @return string device's label
function Model:getLabel(url)
  return self._devices[url].label
end

--- Get device generic model
--- @tparam string url device's url
--- @return table generic model
function Model:getDevice(url)
  local device = self._deviceSetup[url]
  if device ~= nil then
    return enhanceDevice(self, device)
  else
    return nil
  end
end

--- Get all device generic model
--- @return table generic model list
function Model:getDevices()
  local devices = {}
  for url, device in pairs(self._deviceSetup) do
    devices[url] = enhanceDevice(self, device)
  end
  return devices
end

local model = Model(Kizbox.id());
--- Set a device as synced
--- @tparam string url device's url
--- @tparam boolean synced synced state
--- @return boolean true if device updated
function Model:setSynced(url, synced)
  local devFound = self._devices[url]
  if not devFound then
    log:warning("Trying to set as synced a inexistant device: '"..url.."'.")
    return false
  end
  if not devFound.synced then
    devFound.synced = synced
    self._devices[url] = devFound -- write in storage
    if self.events.deviceUpdatedEvent then
      self.events.deviceUpdatedEvent({deviceURL = url});
    end
    log:notice("Set device '"..url.."' as synced.")
  end
  return true
end

--- Get synced state for a device
--- @tparam string url device's url
--- @return boolean true if synced
function Model:isSynced(url)
  if not self._devices[url] then
    return false
  end
  return self._devices[url].synced
end

--- Get device label
--- @tparam string url device's url
--- @return string device's label
function Model:getLabel(url)
  return self._devices[url].label
end

--- Get device generic model
--- @tparam string url device's url
--- @return table generic model
function Model:getDevice(url)
  local device = self._deviceSetup[url]
  if device ~= nil then
    return enhanceDevice(self, device)
  else
    return nil
  end
end

--- Get all device generic model
--- @return table generic model list
function Model:getDevices()
  local devices = {}
  for url, device in pairs(self._deviceSetup) do
    devices[url] = enhanceDevice(self, device)
  end
  return devices
end

local model = Model(Kizbox.id());
--- Set a device as synced
--- @tparam string url device's url
--- @tparam boolean synced synced state
--- @return boolean true if device updated
function Model:setSynced(url, synced)
  local devFound = self._devices[url]
  if not devFound then
    log:warning("Trying to set as synced a inexistant device: '"..url.."'.")
    return false
  end
  if not devFound.synced then
    devFound.synced = synced
    self._devices[url] = devFound -- write in storage
    if self.events.deviceUpdatedEvent then
      self.events.deviceUpdatedEvent({deviceURL = url});
    end
    log:notice("Set device '"..url.."' as synced.")
  end
  return true
end

--- Get synced state for a device
--- @tparam string url device's url
--- @return boolean true if synced
function Model:isSynced(url)
  if not self._devices[url] then
    return false
  end
  return self._devices[url].synced
end

--- Get device label
--- @tparam string url device's url
--- @return string device's label
function Model:getLabel(url)
  return self._devices[url].label
end

--- Get device generic model
--- @tparam string url device's url
--- @return table generic model
function Model:getDevice(url)
  local device = self._deviceSetup[url]
  if device ~= nil then
    return enhanceDevice(self, device)
  else
    return nil
  end
end

--- Get all device generic model
--- @return table generic model list
function Model:getDevices()
  local devices = {}
  for url, device in pairs(self._deviceSetup) do
    devices[url] = enhanceDevice(self, device)
  end
  return devices
end

local model = Model(Kizbox.id());
--- Set a device as synced
--- @tparam string url device's url
--- @tparam boolean synced synced state
--- @return boolean true if device updated
function Model:setSynced(url, synced)
  local devFound = self._devices[url]
  if not devFound then
    log:warning("Trying to set as synced a inexistant device: '"..url.."'.")
    return false
  end
  if not devFound.synced then
    devFound.synced = synced
    self._devices[url] = devFound -- write in storage
    if self.events.deviceUpdatedEvent then
      self.events.deviceUpdatedEvent({deviceURL = url});
    end
    log:notice("Set device '"..url.."' as synced.")
  end
  return true
end

--- Get synced state for a device
--- @tparam string url device's url
--- @return boolean true if synced
function Model:isSynced(url)
  if not self._devices[url] then
    return false
  end
  return self._devices[url].synced
end

--- Get device label
--- @tparam string url device's url
--- @return string device's label
function Model:getLabel(url)
  return self._devices[url].label
end

--- Get device generic model
--- @tparam string url device's url
--- @return table generic model
function Model:getDevice(url)
  local device = self._deviceSetup[url]
  if device ~= nil then
    return enhanceDevice(self, device)
  else
    return nil
  end
end

--- Get all device generic model
--- @return table generic model list
function Model:getDevices()
  local devices = {}
  for url, device in pairs(self._deviceSetup) do
    devices[url] = enhanceDevice(self, device)
  end
  return devices
end

local model = Model(Kizbox.id());
--- Set a device as synced
--- @tparam string url device's url
--- @tparam boolean synced synced state
--- @return boolean true if device updated
function Model:setSynced(url, synced)
  local devFound = self._devices[url]
  if not devFound then
    log:warning("Trying to set as synced a inexistant device: '"..url.."'.")
    return false
  end
  if not devFound.synced then
    devFound.synced = synced
    self._devices[url] = devFound -- write in storage
    if self.events.deviceUpdatedEvent then
      self.events.deviceUpdatedEvent({deviceURL = url});
    end
    log:notice("Set device '"..url.."' as synced.")
  end
  return true
end

--- Get synced state for a device
--- @tparam string url device's url
--- @return boolean true if synced
function Model:isSynced(url)
  if not self._devices[url] then
    return false
  end
  return self._devices[url].synced
end

--- Get device label
--- @tparam string url device's url
--- @return string device's label
function Model:getLabel(url)
  return self._devices[url].label
end

--- Get device generic model
--- @tparam string url device's url
--- @return table generic model
function Model:getDevice(url)
  local device = self._deviceSetup[url]
  if device ~= nil then
    return enhanceDevice(self, device)
  else
    return nil
  end
end

--- Get all device generic model
--- @return table generic model list
function Model:getDevices()
  local devices = {}
  for url, device in pairs(self._deviceSetup) do
    devices[url] = enhanceDevice(self, device)
  end
  return devices
end

local model = Model(Kizbox.id());
--- Set a device as synced
--- @tparam string url device's url
--- @tparam boolean synced synced state
--- @return boolean true if device updated
function Model:setSynced(url, synced)
  local devFound = self._devices[url]
  if not devFound then
    log:warning("Trying to set as synced a inexistant device: '"..url.."'.")
    return false
  end
  if not devFound.synced then
    devFound.synced = synced
    self._devices[url] = devFound -- write in storage
    if self.events.deviceUpdatedEvent then
      self.events.deviceUpdatedEvent({deviceURL = url});
    end
    log:notice("Set device '"..url.."' as synced.")
  end
  return true
end

--- Get synced state for a device
--- @tparam string url device's url
--- @return boolean true if synced
function Model:isSynced(url)
  if not self._devices[url] then
    return false
  end
  return self._devices[url].synced
end

--- Get device label
--- @tparam string url device's url
--- @return string device's label
function Model:getLabel(url)
  return self._devices[url].label
end

--- Get device generic model
--- @tparam string url device's url
--- @return table generic model
function Model:getDevice(url)
  local device = self._deviceSetup[url]
  if device ~= nil then
    return enhanceDevice(self, device)
  else
    return nil
  end
end

--- Get all device generic model
--- @return table generic model list
function Model:getDevices()
  local devices = {}
  for url, device in pairs(self._deviceSetup) do
    devices[url] = enhanceDevice(self, device)
  end
  return devices
end

local model = Model(Kizbox.id());
--- Set a device as synced
--- @tparam string url device's url
--- @tparam boolean synced synced state
--- @return boolean true if device updated
function Model:setSynced(url, synced)
  local devFound = self._devices[url]
  if not devFound then
    log:warning("Trying to set as synced a inexistant device: '"..url.."'.")
    return false
  end
  if not devFound.synced then
    devFound.synced = synced
    self._devices[url] = devFound -- write in storage
    if self.events.deviceUpdatedEvent then
      self.events.deviceUpdatedEvent({deviceURL = url});
    end
    log:notice("Set device '"..url.."' as synced.")
  end
  return true
end

--- Get synced state for a device
--- @tparam string url device's url
--- @return boolean true if synced
function Model:isSynced(url)
  if not self._devices[url] then
    return false
  end
  return self._devices[url].synced
end

--- Get device label
--- @tparam string url device's url
--- @return string device's label
function Model:getLabel(url)
  return self._devices[url].label
end

--- Get device generic model
--- @tparam string url device's url
--- @return table generic model
function Model:getDevice(url)
  local device = self._deviceSetup[url]
  if device ~= nil then
    return enhanceDevice(self, device)
  else
    return nil
  end
end

--- Get all device generic model
--- @return table generic model list
function Model:getDevices()
  local devices = {}
  for url, device in pairs(self._deviceSetup) do
    devices[url] = enhanceDevice(self, device)
  end
  return devices
end

local model = Model(Kizbox.id());
--- Set a device as synced
--- @tparam string url device's url
--- @tparam boolean synced synced state
--- @return boolean true if device updated
function Model:setSynced(url, synced)
  local devFound = self._devices[url]
  if not devFound then
    log:warning("Trying to set as synced a inexistant device: '"..url.."'.")
    return false
  end
  if not devFound.synced then
    devFound.synced = synced
    self._devices[url] = devFound -- write in storage
    if self.events.deviceUpdatedEvent then
      self.events.deviceUpdatedEvent({deviceURL = url});
    end
    log:notice("Set device '"..url.."' as synced.")
  end
  return true
end

--- Get synced state for a device
--- @tparam string url device's url
--- @return boolean true if synced
function Model:isSynced(url)
  if not self._devices[url] then
    return false
  end
  return self._devices[url].synced
end

--- Get device label
--- @tparam string url device's url
--- @return string device's label
function Model:getLabel(url)
  return self._devices[url].label
end

--- Get device generic model
--- @tparam string url device's url
--- @return table generic model
function Model:getDevice(url)
  local device = self._deviceSetup[url]
  if device ~= nil then
    return enhanceDevice(self, device)
  else
    return nil
  end
end

--- Get all device generic model
--- @return table generic model list
function Model:getDevices()
  local devices = {}
  for url, device in pairs(self._deviceSetup) do
    devices[url] = enhanceDevice(self, device)
  end
  return devices
end

local model = Model(Kizbox.id());
--- Set a device as synced
--- @tparam string url device's url
--- @tparam boolean synced synced state
--- @return boolean true if device updated
function Model:setSynced(url, synced)
  local devFound = self._devices[url]
  if not devFound then
    log:warning("Trying to set as synced a inexistant device: '"..url.."'.")
    return false
  end
  if not devFound.synced then
    devFound.synced = synced
    self._devices[url] = devFound -- write in storage
    if self.events.deviceUpdatedEvent then
      self.events.deviceUpdatedEvent({deviceURL = url});
    end
    log:notice("Set device '"..url.."' as synced.")
  end
  return true
end

--- Get synced state for a device
--- @tparam string url device's url
--- @return boolean true if synced
function Model:isSynced(url)
  if not self._devices[url] then
    return false
  end
  return self._devices[url].synced
end

--- Get device label
--- @tparam string url device's url
--- @return string device's label
function Model:getLabel(url)
  return self._devices[url].label
end

--- Get device generic model
--- @tparam string url device's url
--- @return table generic model
function Model:getDevice(url)
  local device = self._deviceSetup[url]
  if device ~= nil then
    return enhanceDevice(self, device)
  else
    return nil
  end
end

--- Get all device generic model
--- @return table generic model list
function Model:getDevices()
  local devices = {}
  for url, device in pairs(self._deviceSetup) do
    devices[url] = enhanceDevice(self, device)
  end
  return devices
end

local model = Model(Kizbox.id());
--- Set a device as synced
--- @tparam string url device's url
--- @tparam boolean synced synced state
--- @return boolean true if device updated
function Model:setSynced(url, synced)
  local devFound = self._devices[url]
  if not devFound then
    log:warning("Trying to set as synced a inexistant device: '"..url.."'.")
    return false
  end
  if not devFound.synced then
    devFound.synced = synced
    self._devices[url] = devFound -- write in storage
    if self.events.deviceUpdatedEvent then
      self.events.deviceUpdatedEvent({deviceURL = url});
    end
    log:notice("Set device '"..url.."' as synced.")
  end
  return true
end

--- Get synced state for a device
--- @tparam string url device's url
--- @return boolean true if synced
function Model:isSynced(url)
  if not self._devices[url] then
    return false
  end
  return self._devices[url].synced
end

--- Get device label
--- @tparam string url device's url
--- @return string device's label
function Model:getLabel(url)
  return self._devices[url].label
end

--- Get device generic model
--- @tparam string url device's url
--- @return table generic model
function Model:getDevice(url)
  local device = self._deviceSetup[url]
  if device ~= nil then
    return enhanceDevice(self, device)
  else
    return nil
  end
end

--- Get all device generic model
--- @return table generic model list
function Model:getDevices()
  local devices = {}
  for url, device in pairs(self._deviceSetup) do
    devices[url] = enhanceDevice(self, device)
  end
  return devices
end

local model = Model(Kizbox.id());
--- Set a device as synced
--- @tparam string url device's url
--- @tparam boolean synced synced state
--- @return boolean true if device updated
function Model:setSynced(url, synced)
  local devFound = self._devices[url]
  if not devFound then
    log:warning("Trying to set as synced a inexistant device: '"..url.."'.")
    return false
  end
  if not devFound.synced then
    devFound.synced = synced
    self._devices[url] = devFound -- write in storage
    if self.events.deviceUpdatedEvent then
      self.events.deviceUpdatedEvent({deviceURL = url});
    end
    log:notice("Set device '"..url.."' as synced.")
  end
  return true
end

--- Get synced state for a device
--- @tparam string url device's url
--- @return boolean true if synced
function Model:isSynced(url)
  if not self._devices[url] then
    return false
  end
  return self._devices[url].synced
end

--- Get device label
--- @tparam string url device's url
--- @return string device's label
function Model:getLabel(url)
  return self._devices[url].label
end

--- Get device generic model
--- @tparam string url device's url
--- @return table generic model
function Model:getDevice(url)
  local device = self._deviceSetup[url]
  if device ~= nil then
    return enhanceDevice(self, device)
  else
    return nil
  end
end

--- Get all device generic model
--- @return table generic model list
function Model:getDevices()
  local devices = {}
  for url, device in pairs(self._deviceSetup) do
    devices[url] = enhanceDevice(self, device)
  end
  return devices
end

local model = Model(Kizbox.id());
--- Set a device as synced
--- @tparam string url device's url
--- @tparam boolean synced synced state
--- @return boolean true if device updated
function Model:setSynced(url, synced)
  local devFound = self._devices[url]
  if not devFound then
    log:warning("Trying to set as synced a inexistant device: '"..url.."'.")
    return false
  end
  if not devFound.synced then
    devFound.synced = synced
    self._devices[url] = devFound -- write in storage
    if self.events.deviceUpdatedEvent then
      self.events.deviceUpdatedEvent({deviceURL = url});
    end
    log:notice("Set device '"..url.."' as synced.")
  end
  return true
end

--- Get synced state for a device
--- @tparam string url device's url
--- @return boolean true if synced
function Model:isSynced(url)
  if not self._devices[url] then
    return false
  end
  return self._devices[url].synced
end

--- Get device label
--- @tparam string url device's url
--- @return string device's label
function Model:getLabel(url)
  return self._devices[url].label
end

--- Get device generic model
--- @tparam string url device's url
--- @return table generic model
function Model:getDevice(url)
  local device = self._deviceSetup[url]
  if device ~= nil then
    return enhanceDevice(self, device)
  else
    return nil
  end
end

--- Get all device generic model
--- @return table generic model list
function Model:getDevices()
  local devices = {}
  for url, device in pairs(self._deviceSetup) do
    devices[url] = enhanceDevice(self, device)
  end
  return devices
end

local model = Model(Kizbox.id());
--- Set a device as synced
--- @tparam string url device's url
--- @tparam boolean synced synced state
--- @return boolean true if device updated
function Model:setSynced(url, synced)
  local devFound = self._devices[url]
  if not devFound then
    log:warning("Trying to set as synced a inexistant device: '"..url.."'.")
    return false
  end
  if not devFound.synced then
    devFound.synced = synced
    self._devices[url] = devFound -- write in storage
    if self.events.deviceUpdatedEvent then
      self.events.deviceUpdatedEvent({deviceURL = url});
    end
    log:notice("Set device '"..url.."' as synced.")
  end
  return true
end

--- Get synced state for a device
--- @tparam string url device's url
--- @return boolean true if synced
function Model:isSynced(url)
  if not self._devices[url] then
    return false
  end
  return self._devices[url].synced
end

--- Get device label
--- @tparam string url device's url
--- @return string device's label
function Model:getLabel(url)
  return self._devices[url].label
end

--- Get device generic model
--- @tparam string url device's url
--- @return table generic model
function Model:getDevice(url)
  local device = self._deviceSetup[url]
  if device ~= nil then
    return enhanceDevice(self, device)
  else
    return nil
  end
end

--- Get all device generic model
--- @return table generic model list
function Model:getDevices()
  local devices = {}
  for url, device in pairs(self._deviceSetup) do
    devices[url] = enhanceDevice(self, device)
  end
  return devices
end

local model = Model(Kizbox.id());
--- Set a device as synced
--- @tparam string url device's url
--- @tparam boolean synced synced state
--- @return boolean true if device updated
function Model:setSynced(url, synced)
  local devFound = self._devices[url]
  if not devFound then
    log:warning("Trying to set as synced a inexistant device: '"..url.."'.")
    return false
  end
  if not devFound.synced then
    devFound.synced = synced
    self._devices[url] = devFound -- write in storage
    if self.events.deviceUpdatedEvent then
      self.events.deviceUpdatedEvent({deviceURL = url});
    end
    log:notice("Set device '"..url.."' as synced.")
  end
  return true
end

--- Get synced state for a device
--- @tparam string url device's url
--- @return boolean true if synced
function Model:isSynced(url)
  if not self._devices[url] then
    return false
  end
  return self._devices[url].synced
end

--- Get device label
--- @tparam string url device's url
--- @return string device's label
function Model:getLabel(url)
  return self._devices[url].label
end

--- Get device generic model
--- @tparam string url device's url
--- @return table generic model
function Model:getDevice(url)
  local device = self._deviceSetup[url]
  if device ~= nil then
    return enhanceDevice(self, device)
  else
    return nil
  end
end

--- Get all device generic model
--- @return table generic model list
function Model:getDevices()
  local devices = {}
  for url, device in pairs(self._deviceSetup) do
    devices[url] = enhanceDevice(self, device)
  end
  return devices
end

local model = Model(Kizbox.id());
--- Set a device as synced
--- @tparam string url device's url
--- @tparam boolean synced synced state
--- @return boolean true if device updated
function Model:setSynced(url, synced)
  local devFound = self._devices[url]
  if not devFound then
    log:warning("Trying to set as synced a inexistant device: '"..url.."'.")
    return false
  end
  if not devFound.synced then
    devFound.synced = synced
    self._devices[url] = devFound -- write in storage
    if self.events.deviceUpdatedEvent then
      self.events.deviceUpdatedEvent({deviceURL = url});
    end
    log:notice("Set device '"..url.."' as synced.")
  end
  return true
end

return model;

            """))
        print(ast.toPrettyStr(tree))

