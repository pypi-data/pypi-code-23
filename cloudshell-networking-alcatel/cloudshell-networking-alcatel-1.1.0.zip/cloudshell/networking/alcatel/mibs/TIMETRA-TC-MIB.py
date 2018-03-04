#
# PySNMP MIB module TIMETRA-TC-MIB (http://pysnmp.sf.net)
# ASN.1 source file://C:\MIBS\text_mibs\aos\TIMETRA-TC-MIB
# Produced by pysmi-0.0.6 at Wed May 31 13:16:58 2017
# On host ? platform ? version ? by user ?
# Using Python version 2.7.9 (default, Dec 10 2014, 12:24:55) [MSC v.1500 32 bit (Intel)]
#
( Integer, ObjectIdentifier, OctetString, ) = mibBuilder.importSymbols("ASN1", "Integer", "ObjectIdentifier", "OctetString")
( NamedValues, ) = mibBuilder.importSymbols("ASN1-ENUMERATION", "NamedValues")
( ConstraintsUnion, SingleValueConstraint, ConstraintsIntersection, ValueSizeConstraint, ValueRangeConstraint, ) = mibBuilder.importSymbols("ASN1-REFINEMENT", "ConstraintsUnion", "SingleValueConstraint", "ConstraintsIntersection", "ValueSizeConstraint", "ValueRangeConstraint")
( NotificationGroup, ModuleCompliance, ) = mibBuilder.importSymbols("SNMPv2-CONF", "NotificationGroup", "ModuleCompliance")
( Integer32, MibScalar, MibTable, MibTableRow, MibTableColumn, NotificationType, MibIdentifier, IpAddress, TimeTicks, Counter64, Unsigned32, ModuleIdentity, Gauge32, iso, ObjectIdentity, Bits, Counter32, ) = mibBuilder.importSymbols("SNMPv2-SMI", "Integer32", "MibScalar", "MibTable", "MibTableRow", "MibTableColumn", "NotificationType", "MibIdentifier", "IpAddress", "TimeTicks", "Counter64", "Unsigned32", "ModuleIdentity", "Gauge32", "iso", "ObjectIdentity", "Bits", "Counter32")
( DisplayString, TextualConvention, ) = mibBuilder.importSymbols("SNMPv2-TC", "DisplayString", "TextualConvention")
( timetraModules, ) = mibBuilder.importSymbols("TIMETRA-GLOBAL-MIB", "timetraModules")
timetraTCMIBModule = ModuleIdentity((1, 3, 6, 1, 4, 1, 6527, 1, 1, 2)).setRevisions(("1911-02-01 00:00", "1909-02-28 00:00", "1908-07-01 00:00", "1908-01-01 00:00", "1907-01-01 00:00", "1906-03-23 00:00", "1905-08-31 00:00", "1905-01-24 00:00", "1904-01-15 00:00", "1903-08-15 00:00", "1903-01-20 00:00", "1901-05-29 00:00",))
class InterfaceIndex(Integer32, TextualConvention):
    displayHint = 'd'

class TmnxPortID(Unsigned32, TextualConvention):
    pass

class TmnxEncapVal(Unsigned32, TextualConvention):
    pass

class QTag(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ValueRangeConstraint(1,4094)

class QTagOrZero(Unsigned32, TextualConvention):
    subtypeSpec = Unsigned32.subtypeSpec+ValueRangeConstraint(0,4094)

class QTagFullRange(Unsigned32, TextualConvention):
    subtypeSpec = Unsigned32.subtypeSpec+ValueRangeConstraint(0,4095)

class QTagFullRangeOrNone(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(-1,-1),ValueRangeConstraint(0,4095),)
class TmnxStrSapId(DisplayString, TextualConvention):
    subtypeSpec = DisplayString.subtypeSpec+ValueSizeConstraint(0,32)

class IpAddressPrefixLength(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ValueRangeConstraint(0,32)

class TmnxActionType(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2,)
    namedValues = NamedValues(("doAction", 1), ("notApplicable", 2),)

class TmnxAdminState(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2, 3,)
    namedValues = NamedValues(("noop", 1), ("inService", 2), ("outOfService", 3),)

class TmnxOperState(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2, 3, 4,)
    namedValues = NamedValues(("unknown", 1), ("inService", 2), ("outOfService", 3), ("transition", 4),)

class TmnxStatus(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2,)
    namedValues = NamedValues(("create", 1), ("delete", 2),)

class TmnxEnabledDisabled(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2,)
    namedValues = NamedValues(("enabled", 1), ("disabled", 2),)

class TmnxEnabledDisabledOrInherit(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2, 3,)
    namedValues = NamedValues(("enabled", 1), ("disabled", 2), ("inherit", 3),)

class TNamedItem(DisplayString, TextualConvention):
    subtypeSpec = DisplayString.subtypeSpec+ValueSizeConstraint(1,32)

class TNamedItemOrEmpty(DisplayString, TextualConvention):
    subtypeSpec = DisplayString.subtypeSpec+ConstraintsUnion(ValueSizeConstraint(0,0),ValueSizeConstraint(1,32),)
class TLNamedItem(DisplayString, TextualConvention):
    subtypeSpec = DisplayString.subtypeSpec+ValueSizeConstraint(1,64)

class TLNamedItemOrEmpty(DisplayString, TextualConvention):
    subtypeSpec = DisplayString.subtypeSpec+ConstraintsUnion(ValueSizeConstraint(0,0),ValueSizeConstraint(1,64),)
class TItemDescription(DisplayString, TextualConvention):
    subtypeSpec = DisplayString.subtypeSpec+ValueSizeConstraint(0,80)

class TItemLongDescription(DisplayString, TextualConvention):
    subtypeSpec = DisplayString.subtypeSpec+ValueSizeConstraint(0,160)

class TmnxVRtrID(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ValueRangeConstraint(1,10240)

class TmnxVRtrIDOrZero(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ValueRangeConstraint(0,10240)

class TmnxBgpAutonomousSystem(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ValueRangeConstraint(0,65535)

class TmnxBgpLocalPreference(Unsigned32, TextualConvention):
    pass

class TmnxBgpPreference(Unsigned32, TextualConvention):
    subtypeSpec = Unsigned32.subtypeSpec+ValueRangeConstraint(0,255)

class TmnxCustId(Unsigned32, TextualConvention):
    subtypeSpec = Unsigned32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(0,0),ValueRangeConstraint(1,2147483647),)
class BgpPeeringStatus(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12,)
    namedValues = NamedValues(("notApplicable", 0), ("installed", 1), ("notInstalled", 2), ("noEnhancedSubmgt", 3), ("wrongAntiSpoof", 4), ("parentItfDown", 5), ("hostInactive", 6), ("noDualHomingSupport", 7), ("invalidRadiusAttr", 8), ("noDynamicPeerGroup", 9), ("duplicatePeer", 10), ("maxPeersReached", 11), ("genError", 12),)

class TmnxServId(Unsigned32, TextualConvention):
    subtypeSpec = Unsigned32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(0,0),ValueRangeConstraint(1,2147483647),ValueRangeConstraint(2147483648,2147483648),ValueRangeConstraint(2147483649,2147483649),ValueRangeConstraint(2147483650,2147483650),)
class ServiceAdminStatus(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2,)
    namedValues = NamedValues(("up", 1), ("down", 2),)

class ServiceOperStatus(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2,)
    namedValues = NamedValues(("up", 1), ("down", 2),)

class TPolicyID(Unsigned32, TextualConvention):
    subtypeSpec = Unsigned32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(0,65535),ValueRangeConstraint(65536,65536),ValueRangeConstraint(65537,65537),)
class TTmplPolicyID(Unsigned32, TextualConvention):
    subtypeSpec = Unsigned32.subtypeSpec+ValueRangeConstraint(1,65535)

class TSapIngressPolicyID(TPolicyID, TextualConvention):
    pass

class TSapEgressPolicyID(TPolicyID, TextualConvention):
    subtypeSpec = TPolicyID.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(1,65535),ValueRangeConstraint(65536,65536),ValueRangeConstraint(65537,65537),)
class TSdpIngressPolicyID(TPolicyID, TextualConvention):
    pass

class TSdpEgressPolicyID(TPolicyID, TextualConvention):
    pass

class TQosQGrpInstanceIDorZero(Unsigned32, TextualConvention):
    subtypeSpec = Unsigned32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(0,0),ValueRangeConstraint(1,65535),)
class TmnxBsxTransitIpPolicyId(Unsigned32, TextualConvention):
    subtypeSpec = Unsigned32.subtypeSpec+ValueRangeConstraint(1,65535)

class TmnxBsxTransitIpPolicyIdOrZero(Unsigned32, TextualConvention):
    subtypeSpec = Unsigned32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(0,0),ValueRangeConstraint(1,65535),)
class TmnxBsxTransPrefPolicyId(Unsigned32, TextualConvention):
    subtypeSpec = Unsigned32.subtypeSpec+ValueRangeConstraint(1,65535)

class TmnxBsxTransPrefPolicyIdOrZero(Unsigned32, TextualConvention):
    subtypeSpec = Unsigned32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(0,0),ValueRangeConstraint(1,65535),)
class TmnxBsxAarpId(Unsigned32, TextualConvention):
    subtypeSpec = Unsigned32.subtypeSpec+ValueRangeConstraint(1,65535)

class TmnxBsxAarpIdOrZero(Unsigned32, TextualConvention):
    subtypeSpec = Unsigned32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(0,0),ValueRangeConstraint(1,65535),)
class TmnxBsxAarpServiceRefType(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(0, 1, 2, 3,)
    namedValues = NamedValues(("none", 0), ("dualHomed", 1), ("shuntSubscriberSide", 2), ("shuntNetworkSide", 3),)

class TSapEgrEncapGrpQosPolicyIdOrZero(Unsigned32, TextualConvention):
    subtypeSpec = Unsigned32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(0,0),ValueRangeConstraint(1,65535),)
class TSapEgrEncapGroupType(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1,)
    namedValues = NamedValues(("isid", 1),)

class TSapEgrEncapGroupActionType(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2,)
    namedValues = NamedValues(("create", 1), ("destroy", 2),)

class TPerPacketOffset(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ValueRangeConstraint(-32,31)

class TPerPacketOffsetOvr(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(-128,-128),ValueRangeConstraint(-32,31),)
class TIngressHsmdaPerPacketOffset(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ValueRangeConstraint(-32,31)

class TEgressQPerPacketOffset(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ValueRangeConstraint(-64,32)

class TIngHsmdaPerPacketOffsetOvr(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(-128,-128),ValueRangeConstraint(-32,31),)
class TEgressHsmdaPerPacketOffset(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ValueRangeConstraint(-32,31)

class THsmdaCounterIdOrZero(Unsigned32, TextualConvention):
    subtypeSpec = Unsigned32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(0,0),ValueRangeConstraint(1,8),)
class THsmdaCounterIdOrZeroOrAll(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(-1,-1),ValueRangeConstraint(0,0),ValueRangeConstraint(1,8),)
class TEgrHsmdaPerPacketOffsetOvr(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(-128,-128),ValueRangeConstraint(-32,31),)
class TIngressHsmdaCounterId(Unsigned32, TextualConvention):
    subtypeSpec = Unsigned32.subtypeSpec+ValueRangeConstraint(1,8)

class TIngressHsmdaCounterIdOrZero(Unsigned32, TextualConvention):
    subtypeSpec = Unsigned32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(0,0),ValueRangeConstraint(1,8),)
class TEgressHsmdaCounterId(Unsigned32, TextualConvention):
    subtypeSpec = Unsigned32.subtypeSpec+ValueRangeConstraint(1,8)

class TEgressHsmdaCounterIdOrZero(Unsigned32, TextualConvention):
    subtypeSpec = Unsigned32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(0,0),ValueRangeConstraint(1,8),)
class TEgrRateModType(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2, 3,)
    namedValues = NamedValues(("none", 1), ("aggRateLimit", 2), ("namedScheduler", 3),)

class TPolicyStatementNameOrEmpty(TNamedItemOrEmpty, TextualConvention):
    pass

class TmnxVcType(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2, 3, 4, 5, 9, 10, 11, 17, 18, 19, 20, 21, 23, 25, 4096,)
    namedValues = NamedValues(("frDlciMartini", 1), ("atmSdu", 2), ("atmCell", 3), ("ethernetVlan", 4), ("ethernet", 5), ("atmVccCell", 9), ("atmVpcCell", 10), ("ipipe", 11), ("satopE1", 17), ("satopT1", 18), ("satopE3", 19), ("satopT3", 20), ("cesopsn", 21), ("cesopsnCas", 23), ("frDlci", 25), ("mirrorDest", 4096),)

class TmnxVcId(Unsigned32, TextualConvention):
    subtypeSpec = Unsigned32.subtypeSpec+ValueRangeConstraint(1,4294967295)

class TmnxVcIdOrNone(Unsigned32, TextualConvention):
    subtypeSpec = Unsigned32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(0,0),ValueRangeConstraint(1,4294967295),)
class Dot1PPriority(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(-1,-1),ValueRangeConstraint(0,7),)
class Dot1PPriorityMask(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ValueRangeConstraint(0,7)

class ServiceAccessPoint(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(-1,-1),ValueRangeConstraint(0,255),)
class TLspExpValue(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(-1,-1),ValueRangeConstraint(0,7),)
class TIpProtocol(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(-2,-2),ValueRangeConstraint(-1,-1),ValueRangeConstraint(0,255),)
class TIpOption(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ValueRangeConstraint(0,255)

class TTcpUdpPort(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(0,0),ValueRangeConstraint(1,65535),)
class TOperator(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(0, 1, 2, 3, 4,)
    namedValues = NamedValues(("none", 0), ("eq", 1), ("range", 2), ("lt", 3), ("gt", 4),)

class TTcpUdpPortOperator(TOperator, TextualConvention):
    pass

class TFrameType(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(0, 1, 2, 3, 5,)
    namedValues = NamedValues(("e802dot3", 0), ("e802dot2LLC", 1), ("e802dot2SNAP", 2), ("ethernetII", 3), ("atm", 5),)

class TQueueId(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(0,0),ValueRangeConstraint(1,32),)
class TQueueIdOrAll(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(-1,-1),ValueRangeConstraint(0,0),ValueRangeConstraint(1,32),)
class TIngressQueueId(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(0,0),ValueRangeConstraint(1,32),)
class TIngressMeterId(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(0,0),ValueRangeConstraint(1,32),)
class TSapIngressMeterId(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(0,0),ValueRangeConstraint(1,32),)
class TNetworkIngressMeterId(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(0,0),ValueRangeConstraint(1,16),)
class TEgressQueueId(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(0,0),ValueRangeConstraint(1,8),)
class TIngressHsmdaQueueId(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(0,0),ValueRangeConstraint(1,8),)
class TEgressHsmdaQueueId(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(0,0),ValueRangeConstraint(1,8),)
class THsmdaSchedulerPolicyGroupId(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(0,0),ValueRangeConstraint(1,2),)
class THsmdaPolicyIncludeQueues(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2,)
    namedValues = NamedValues(("q1to2", 1), ("q1to3", 2),)

class THsmdaPolicyScheduleClass(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ValueRangeConstraint(1,3)

class TDSCPName(TNamedItem, TextualConvention):
    pass

class TDSCPNameOrEmpty(TNamedItemOrEmpty, TextualConvention):
    pass

class TDSCPValue(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ValueRangeConstraint(0,63)

class TDSCPValueOrNone(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(-1,-1),ValueRangeConstraint(0,63),)
class TDSCPFilterActionValue(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(-1,-1),ValueRangeConstraint(0,255),)
class TFCName(TNamedItem, TextualConvention):
    pass

class TFCNameOrEmpty(TNamedItemOrEmpty, TextualConvention):
    pass

class TFCSet(Bits, TextualConvention):
    namedValues = NamedValues(("be", 0), ("l2", 1), ("af", 2), ("l1", 3), ("h2", 4), ("ef", 5), ("h1", 6), ("nc", 7),)

class TFCType(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(0, 1, 2, 3, 4, 5, 6, 7,)
    namedValues = NamedValues(("be", 0), ("l2", 1), ("af", 2), ("l1", 3), ("h2", 4), ("ef", 5), ("h1", 6), ("nc", 7),)

class TmnxTunnelType(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2, 3, 4, 5, 6, 7,)
    namedValues = NamedValues(("sdp", 1), ("ldp", 2), ("rsvp", 3), ("gre", 4), ("bypass", 5), ("invalid", 6), ("bgp", 7),)

class TmnxTunnelID(Unsigned32, TextualConvention):
    pass

class TmnxBgpRouteTarget(OctetString, TextualConvention):
    subtypeSpec = OctetString.subtypeSpec+ValueSizeConstraint(1,32)

class TmnxVPNRouteDistinguisher(OctetString, TextualConvention):
    subtypeSpec = OctetString.subtypeSpec+ValueSizeConstraint(8,8)
    fixedLength = 8

class SdpBindId(OctetString, TextualConvention):
    subtypeSpec = OctetString.subtypeSpec+ValueSizeConstraint(8,8)
    fixedLength = 8

class TmnxVRtrMplsLspID(Unsigned32, TextualConvention):
    subtypeSpec = Unsigned32.subtypeSpec+ValueRangeConstraint(0,65535)

class TPortSchedulerPIR(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(-1,-1),ValueRangeConstraint(1,100000000),)
class TPortSchedulerPIRRate(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(-1,-1),ValueRangeConstraint(1,400000000),)
class TPortSchedulerCIR(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(-1,-1),ValueRangeConstraint(0,400000000),)
class TWeight(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ValueRangeConstraint(0,100)

class TNonZeroWeight(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ValueRangeConstraint(1,100)

class TPolicerWeight(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ValueRangeConstraint(1,100)

class THsmdaWeight(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ValueRangeConstraint(1,100)

class THsmdaWrrWeight(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ValueRangeConstraint(1,32)

class THsmdaWeightClass(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2, 4, 8,)
    namedValues = NamedValues(("class1", 1), ("class2", 2), ("class4", 4), ("class8", 8),)

class THsmdaWeightOverride(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(-2,-2),ValueRangeConstraint(1,100),)
class THsmdaWrrWeightOverride(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(-2,-2),ValueRangeConstraint(1,32),)
class TCIRRate(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(-1,-1),ValueRangeConstraint(0,100000000),)
class THPolCIRRate(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(-1,-1),ValueRangeConstraint(0,20000000),)
class TRateType(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2,)
    namedValues = NamedValues(("kbps", 1), ("percent", 2),)

class TBWRateType(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2, 3,)
    namedValues = NamedValues(("kbps", 1), ("percentPortLimit", 2), ("percentLocalLimit", 3),)

class TPolicerRateType(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2,)
    namedValues = NamedValues(("kbps", 1), ("percentLocalLimit", 2),)

class TCIRRateOverride(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(-2,-2),ValueRangeConstraint(-1,-1),ValueRangeConstraint(0,100000000),)
class THPolCIRRateOverride(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(-2,-2),ValueRangeConstraint(-1,-1),ValueRangeConstraint(0,20000000),)
class TCIRPercentOverride(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(-2,-2),ValueRangeConstraint(0,10000),)
class THsmdaCIRKRate(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(-1,-1),ValueRangeConstraint(0,100000000),)
class THsmdaCIRKRateOverride(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(-2,-2),ValueRangeConstraint(-1,-1),ValueRangeConstraint(0,100000000),)
class THsmdaCIRMRate(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(-1,-1),ValueRangeConstraint(0,100000),)
class THsmdaCIRMRateOverride(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(-2,-2),ValueRangeConstraint(-1,-1),ValueRangeConstraint(0,100000),)
class TPIRRate(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(-1,-1),ValueRangeConstraint(1,100000000),)
class THPolVirtualSchePIRRate(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(-1,-1),ValueRangeConstraint(1,800000000),)
class THPolVirtualScheCIRRate(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(-1,-1),ValueRangeConstraint(0,800000000),)
class TAdvCfgRate(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ValueRangeConstraint(0,100000000)

class TMaxDecRate(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(0,0),ValueRangeConstraint(1,100000000),)
class THPolPIRRate(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(-1,-1),ValueRangeConstraint(1,20000000),)
class TSecondaryShaper10GPIRRate(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(-1,-1),ValueRangeConstraint(1,10000),)
class TExpSecondaryShaperPIRRate(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(-1,-1),ValueRangeConstraint(1,10000000),)
class TExpSecondaryShaperClassRate(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(-1,-1),ValueRangeConstraint(1,10000000),)
class TPIRRateOverride(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(-2,-2),ValueRangeConstraint(-1,-1),ValueRangeConstraint(1,100000000),)
class THPolPIRRateOverride(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(-2,-2),ValueRangeConstraint(-1,-1),ValueRangeConstraint(1,20000000),)
class TPIRPercentOverride(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(-2,-2),ValueRangeConstraint(1,10000),)
class TPIRRateOrZero(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(-1,-1),ValueRangeConstraint(0,100000000),)
class THsmdaPIRKRate(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(-1,-1),ValueRangeConstraint(1,100000000),)
class THsmdaPIRKRateOverride(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(-2,-2),ValueRangeConstraint(-1,-1),ValueRangeConstraint(1,100000000),)
class THsmdaPIRMRate(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(-1,-1),ValueRangeConstraint(1,100000),)
class THsmdaPIRMRateOverride(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(-2,-2),ValueRangeConstraint(-1,-1),ValueRangeConstraint(1,100000),)
class TmnxDHCP6MsgType(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,)
    namedValues = NamedValues(("dhcp6MsgTypeSolicit", 1), ("dhcp6MsgTypeAdvertise", 2), ("dhcp6MsgTypeRequest", 3), ("dhcp6MsgTypeConfirm", 4), ("dhcp6MsgTypeRenew", 5), ("dhcp6MsgTypeRebind", 6), ("dhcp6MsgTypeReply", 7), ("dhcp6MsgTypeRelease", 8), ("dhcp6MsgTypeDecline", 9), ("dhcp6MsgTypeReconfigure", 10), ("dhcp6MsgTypeInfoRequest", 11), ("dhcp6MsgTypeRelayForw", 12), ("dhcp6MsgTypeRelayReply", 13), ("dhcp6MsgTypeMaxValue", 14),)

class TmnxOspfInstance(Unsigned32, TextualConvention):
    subtypeSpec = Unsigned32.subtypeSpec+ValueRangeConstraint(0,31)

class TmnxBGPFamilyType(Bits, TextualConvention):
    namedValues = NamedValues(("ipv4Unicast", 0), ("ipv4Multicast", 1), ("ipv4UastMcast", 2), ("ipv4MplsLabel", 3), ("ipv4Vpn", 4), ("ipv6Unicast", 5), ("ipv6Multicast", 6), ("ipv6UcastMcast", 7), ("ipv6MplsLabel", 8), ("ipv6Vpn", 9), ("l2Vpn", 10), ("ipv4Mvpn", 11), ("msPw", 12), ("ipv4Flow", 13), ("mdtSafi", 14), ("routeTarget", 15), ("mcastVpnIpv4", 16),)

class TmnxIgmpGroupFilterMode(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2,)
    namedValues = NamedValues(("include", 1), ("exclude", 2),)

class TmnxIgmpGroupType(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2,)
    namedValues = NamedValues(("static", 1), ("dynamic", 2),)

class TmnxIgmpVersion(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2, 3,)
    namedValues = NamedValues(("version1", 1), ("version2", 2), ("version3", 3),)

class TmnxMldGroupFilterMode(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2,)
    namedValues = NamedValues(("include", 1), ("exclude", 2),)

class TmnxMldGroupType(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2,)
    namedValues = NamedValues(("static", 1), ("dynamic", 2),)

class TmnxMldVersion(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2,)
    namedValues = NamedValues(("version1", 1), ("version2", 2),)

class TmnxManagedRouteStatus(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,)
    namedValues = NamedValues(("installed", 0), ("notYetInstalled", 1), ("wrongAntiSpoofType", 2), ("outOfMemory", 3), ("shadowed", 4), ("routeTableFull", 5), ("parentInterfaceDown", 6), ("hostInactive", 7), ("enhancedSubMgmtRequired", 8), ("deprecated1", 9), ("l2AwNotSupported", 10),)

class TmnxAncpString(DisplayString, TextualConvention):
    subtypeSpec = DisplayString.subtypeSpec+ValueSizeConstraint(1,63)

class TmnxAncpStringOrZero(DisplayString, TextualConvention):
    subtypeSpec = DisplayString.subtypeSpec+ValueSizeConstraint(0,63)

class TmnxMulticastAddrFamily(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(0, 1,)
    namedValues = NamedValues(("ipv4Multicast", 0), ("ipv6Multicast", 1),)

class TmnxAsciiSpecification(DisplayString, TextualConvention):
    subtypeSpec = DisplayString.subtypeSpec+ValueSizeConstraint(0,255)

class TmnxMacSpecification(DisplayString, TextualConvention):
    subtypeSpec = DisplayString.subtypeSpec+ValueSizeConstraint(0,17)

class TmnxBinarySpecification(DisplayString, TextualConvention):
    subtypeSpec = DisplayString.subtypeSpec+ValueSizeConstraint(0,255)

class TmnxDefSubIdSource(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2, 3,)
    namedValues = NamedValues(("useSapId", 1), ("useString", 2), ("useAutoId", 3),)

class TmnxSubIdentString(DisplayString, TextualConvention):
    subtypeSpec = DisplayString.subtypeSpec+ValueSizeConstraint(1,32)

class TmnxSubIdentStringOrEmpty(DisplayString, TextualConvention):
    subtypeSpec = DisplayString.subtypeSpec+ValueSizeConstraint(0,32)

class TmnxSubRadServAlgorithm(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2, 3,)
    namedValues = NamedValues(("direct", 1), ("roundRobin", 2), ("hashBased", 3),)

class TmnxSubRadiusAttrType(Unsigned32, TextualConvention):
    subtypeSpec = Unsigned32.subtypeSpec+ValueRangeConstraint(0,255)

class TmnxSubRadiusVendorId(Unsigned32, TextualConvention):
    subtypeSpec = Unsigned32.subtypeSpec+ValueRangeConstraint(0,16777215)

class TmnxRadiusPendingReqLimit(Unsigned32, TextualConvention):
    subtypeSpec = Unsigned32.subtypeSpec+ValueRangeConstraint(1,4096)

class TmnxRadiusServerOperState(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2, 3, 4, 5,)
    namedValues = NamedValues(("unknown", 1), ("inService", 2), ("outOfService", 3), ("transition", 4), ("overloaded", 5),)

class TmnxSubProfileString(DisplayString, TextualConvention):
    subtypeSpec = DisplayString.subtypeSpec+ValueSizeConstraint(1,16)

class TmnxSubProfileStringOrEmpty(DisplayString, TextualConvention):
    subtypeSpec = DisplayString.subtypeSpec+ValueSizeConstraint(0,16)

class TmnxSlaProfileString(DisplayString, TextualConvention):
    subtypeSpec = DisplayString.subtypeSpec+ValueSizeConstraint(1,16)

class TmnxSlaProfileStringOrEmpty(DisplayString, TextualConvention):
    subtypeSpec = DisplayString.subtypeSpec+ValueSizeConstraint(0,16)

class TmnxAppProfileString(DisplayString, TextualConvention):
    subtypeSpec = DisplayString.subtypeSpec+ValueSizeConstraint(1,16)

class TmnxAppProfileStringOrEmpty(DisplayString, TextualConvention):
    subtypeSpec = DisplayString.subtypeSpec+ValueSizeConstraint(0,16)

class TmnxSubMgtIntDestIdOrEmpty(DisplayString, TextualConvention):
    subtypeSpec = DisplayString.subtypeSpec+ValueSizeConstraint(0,32)

class TmnxSubMgtIntDestId(TmnxSubMgtIntDestIdOrEmpty, TextualConvention):
    subtypeSpec = TmnxSubMgtIntDestIdOrEmpty.subtypeSpec+ValueSizeConstraint(1,32)

class TmnxDefInterDestIdSource(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2, 3,)
    namedValues = NamedValues(("useString", 1), ("useTopQTag", 2), ("useVpi", 3),)

class TmnxSubNasPortSuffixType(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(0, 1, 2,)
    namedValues = NamedValues(("none", 0), ("circuitId", 1), ("remoteId", 2),)

class TmnxSubNasPortPrefixType(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(0, 1,)
    namedValues = NamedValues(("none", 0), ("userString", 1),)

class TmnxSubNasPortTypeType(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2,)
    namedValues = NamedValues(("standard", 1), ("config", 2),)

class TmnxSubMgtOrgStrOrZero(DisplayString, TextualConvention):
    subtypeSpec = DisplayString.subtypeSpec+ValueSizeConstraint(0,32)

class TmnxSubMgtOrgString(TmnxSubMgtOrgStrOrZero, TextualConvention):
    subtypeSpec = TmnxSubMgtOrgStrOrZero.subtypeSpec+ValueSizeConstraint(1,32)

class TmnxFilterProfileStringOrEmpty(DisplayString, TextualConvention):
    subtypeSpec = DisplayString.subtypeSpec+ValueSizeConstraint(0,16)

class TmnxAccessLoopEncapDataLink(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(0, 1,)
    namedValues = NamedValues(("aal5", 0), ("ethernet", 1),)

class TmnxAccessLoopEncaps1(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(0, 1, 2,)
    namedValues = NamedValues(("notAvailable", 0), ("untaggedEthernet", 1), ("singleTaggedEthernet", 2),)

class TmnxAccessLoopEncaps2(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(0, 1, 2, 3, 4, 5, 6, 7, 8,)
    namedValues = NamedValues(("notAvailable", 0), ("pppoaLlc", 1), ("pppoaNull", 2), ("ipoaLlc", 3), ("ipoaNull", 4), ("ethernetOverAal5LlcFcs", 5), ("ethernetOverAal5LlcNoFcs", 6), ("ethernetOverAal5NullFcs", 7), ("ethernetOverAal5NullNoFcs", 8),)

class TmnxSubAleOffsetMode(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(0, 1,)
    namedValues = NamedValues(("none", 0), ("auto", 1),)

class TmnxSubAleOffset(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24,)
    namedValues = NamedValues(("none", 0), ("pppoaLlc", 1), ("pppoaNull", 2), ("pppoeoaLlc", 3), ("pppoeoaLlcFcs", 4), ("pppoeoaLlcTagged", 5), ("pppoeoaLlcTaggedFcs", 6), ("pppoeoaNull", 7), ("pppoeoaNullFcs", 8), ("pppoeoaNullTagged", 9), ("pppoeoaNullTaggedFcs", 10), ("ipoaLlc", 11), ("ipoaNull", 12), ("ipoeoaLlc", 13), ("ipoeoaLlcFcs", 14), ("ipoeoaLlcTagged", 15), ("ipoeoaLlcTaggedFcs", 16), ("ipoeoaNull", 17), ("ipoeoaNullFcs", 18), ("ipoeoaNullTagged", 19), ("ipoeoaNullTaggedFcs", 20), ("pppoe", 21), ("pppoeTagged", 22), ("ipoe", 23), ("ipoeTagged", 24),)

class TmnxDhcpOptionType(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2, 3, 4, 5,)
    namedValues = NamedValues(("ipv4", 1), ("ascii", 2), ("hex", 3), ("ipv6", 4), ("domain", 5),)

class TmnxPppoeUserName(DisplayString, TextualConvention):
    subtypeSpec = DisplayString.subtypeSpec+ValueSizeConstraint(1,128)

class TmnxPppoeUserNameOrEmpty(DisplayString, TextualConvention):
    subtypeSpec = DisplayString.subtypeSpec+ValueSizeConstraint(0,128)

class TCpmProtPolicyID(Unsigned32, TextualConvention):
    subtypeSpec = Unsigned32.subtypeSpec+ValueRangeConstraint(0,255)

class TCpmProtPolicyIDOrDefault(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(-1,-1),ValueRangeConstraint(1,255),)
class TMlpppQoSProfileId(Unsigned32, TextualConvention):
    subtypeSpec = Unsigned32.subtypeSpec+ValueRangeConstraint(0,65535)

class TMcFrQoSProfileId(Unsigned32, TextualConvention):
    subtypeSpec = Unsigned32.subtypeSpec+ValueRangeConstraint(0,65535)

class TmnxPppoeSessionId(Unsigned32, TextualConvention):
    subtypeSpec = Unsigned32.subtypeSpec+ValueRangeConstraint(0,65535)

class TmnxPppoePadoDelay(Unsigned32, TextualConvention):
    subtypeSpec = Unsigned32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(0,0),ValueRangeConstraint(1,30),)
class TmnxPppoeSessionInfoOrigin(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(0, 1, 2, 3, 4, 5, 6, 7,)
    namedValues = NamedValues(("none", 0), ("default", 1), ("radius", 2), ("localUserDb", 3), ("dhcp", 4), ("midSessionChange", 5), ("tags", 6), ("l2tp", 7),)

class TmnxPppoeSessionType(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2, 3, 4,)
    namedValues = NamedValues(("local", 1), ("localWholesale", 2), ("localRetail", 3), ("l2tp", 4),)

class TmnxPppNcpProtocol(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2,)
    namedValues = NamedValues(("ipcp", 1), ("ipv6cp", 2),)

class TmnxMlpppEpClass(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(0, 1, 2, 3, 4, 5,)
    namedValues = NamedValues(("null", 0), ("local", 1), ("ipv4Address", 2), ("macAddress", 3), ("magicNumber", 4), ("directoryNumber", 5),)

class TNetworkPolicyID(TPolicyID, TextualConvention):
    subtypeSpec = TPolicyID.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(1,65535),ValueRangeConstraint(65536,65536),ValueRangeConstraint(65537,65537),)
class TItemScope(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2,)
    namedValues = NamedValues(("exclusive", 1), ("template", 2),)

class TItemMatch(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2, 3,)
    namedValues = NamedValues(("off", 1), ("false", 2), ("true", 3),)

class TPriority(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2,)
    namedValues = NamedValues(("low", 1), ("high", 2),)

class TPriorityOrDefault(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2, 3,)
    namedValues = NamedValues(("low", 1), ("high", 2), ("default", 3),)

class TProfileUseDEOrNone(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(0, 1, 2, 3,)
    namedValues = NamedValues(("none", 0), ("in", 1), ("out", 2), ("de", 3),)

class TPriorityOrUndefined(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(0, 1, 2,)
    namedValues = NamedValues(("undefined", 0), ("low", 1), ("high", 2),)

class TProfile(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2,)
    namedValues = NamedValues(("in", 1), ("out", 2),)

class TProfileOrDei(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2, 13,)
    namedValues = NamedValues(("in", 1), ("out", 2), ("use-dei", 13),)

class TDEProfile(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2, 3,)
    namedValues = NamedValues(("in", 1), ("out", 2), ("de", 3),)

class TDEProfileOrDei(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2, 3, 13,)
    namedValues = NamedValues(("in", 1), ("out", 2), ("de", 3), ("use-dei", 13),)

class TProfileOrNone(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(0, 1, 2,)
    namedValues = NamedValues(("none", 0), ("in", 1), ("out", 2),)

class TAdaptationRule(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2, 3,)
    namedValues = NamedValues(("max", 1), ("min", 2), ("closest", 3),)

class TAdaptationRuleOverride(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(0, 1, 2, 3,)
    namedValues = NamedValues(("noOverride", 0), ("max", 1), ("min", 2), ("closest", 3),)

class TRemarkType(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2, 3,)
    namedValues = NamedValues(("none", 1), ("dscp", 2), ("precedence", 3),)

class TPrecValue(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ValueRangeConstraint(0,7)

class TPrecValueOrNone(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(-1,-1),ValueRangeConstraint(0,7),)
class TBurstSize(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(-1,-1),ValueRangeConstraint(0,131072),)
class TBurstSizeOverride(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(-2,-2),ValueRangeConstraint(-1,-1),ValueRangeConstraint(0,131072),)
class TBurstPercent(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ValueRangeConstraint(0,100)

class TBurstHundredthsOfPercent(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ValueRangeConstraint(0,10000)

class TBurstPercentOrDefault(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(-1,-1),ValueRangeConstraint(0,100),)
class TBurstPercentOrDefaultOverride(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(-2,-2),ValueRangeConstraint(-1,-1),ValueRangeConstraint(0,100),)
class TRatePercent(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ValueRangeConstraint(0,100)

class TPIRRatePercent(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ValueRangeConstraint(1,100)

class TLevel(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ValueRangeConstraint(1,8)

class TLevelOrDefault(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(0,0),ValueRangeConstraint(1,8),)
class TQWeight(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(0,0),ValueRangeConstraint(1,100),)
class TMeterMode(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2,)
    namedValues = NamedValues(("priority", 1), ("profile", 2),)

class TPlcyMode(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(0, 1, 2, 3,)
    namedValues = NamedValues(("none", 0), ("roundRobin", 1), ("weightedRoundRobin", 2), ("weightedDeficitRoundRobin", 3),)

class TPlcyQuanta(Integer32, TextualConvention):
    pass

class TQueueMode(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2,)
    namedValues = NamedValues(("priority", 1), ("profile", 2),)

class TEntryIndicator(Unsigned32, TextualConvention):
    subtypeSpec = Unsigned32.subtypeSpec+ValueRangeConstraint(0,65535)

class TEntryId(TEntryIndicator, TextualConvention):
    subtypeSpec = TEntryIndicator.subtypeSpec+ValueRangeConstraint(1,65535)

class TMatchCriteria(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2, 3, 4, 5, 6,)
    namedValues = NamedValues(("ip", 1), ("mac", 2), ("none", 3), ("dscp", 4), ("dot1p", 5), ("prec", 6),)

class TmnxMdaQos(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(0, 1, 2, 3,)
    namedValues = NamedValues(("unknown", 0), ("mda", 1), ("hsmda1", 2), ("hsmda2", 3),)

class TAtmTdpDescrType(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(0, 1, 2, 3,)
    namedValues = NamedValues(("clp0And1pcr", 0), ("clp0And1pcrPlusClp0And1scr", 1), ("clp0And1pcrPlusClp0scr", 2), ("clp0And1pcrPlusClp0scrTag", 3),)

class TDEValue(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(-1,-1),ValueRangeConstraint(0,1),)
class TQGroupType(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(0, 1,)
    namedValues = NamedValues(("port", 0), ("vpls", 1),)

class TQosOverrideType(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2, 3, 4, 5,)
    namedValues = NamedValues(("queue", 1), ("policer", 2), ("aggRateLimit", 3), ("arbiter", 4), ("scheduler", 5),)

class TmnxIPsecTunnelTemplateId(Unsigned32, TextualConvention):
    subtypeSpec = Unsigned32.subtypeSpec+ValueRangeConstraint(1,2048)

class TmnxIPsecTunnelTemplateIdOrZero(Unsigned32, TextualConvention):
    subtypeSpec = Unsigned32.subtypeSpec+ValueRangeConstraint(0,2048)

class TmnxIpSecIsaOperFlags(Bits, TextualConvention):
    namedValues = NamedValues(("adminDown", 0), ("noActive", 1), ("noResources", 2),)

class TmnxIkePolicyAuthMethod(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2, 3, 4, 5,)
    namedValues = NamedValues(("psk", 1), ("hybridX509XAuth", 2), ("plainX509XAuth", 3), ("plainPskXAuth", 4), ("cert", 5),)

class TmnxIkePolicyOwnAuthMethod(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(0, 1, 5,)
    namedValues = NamedValues(("symmetric", 0), ("psk", 1), ("cert", 5),)

class TmnxRsvpDSTEClassType(Unsigned32, TextualConvention):
    subtypeSpec = Unsigned32.subtypeSpec+ValueRangeConstraint(0,7)

class TmnxAccPlcyQICounters(Bits, TextualConvention):
    namedValues = NamedValues(("hpo", 0), ("lpo", 1), ("ucp", 2), ("hoo", 3), ("loo", 4), ("uco", 5), ("apo", 6), ("aoo", 7), ("hpd", 8), ("lpd", 9), ("hod", 10), ("lod", 11), ("ipf", 12), ("opf", 13), ("iof", 14), ("oof", 15),)

class TmnxAccPlcyQECounters(Bits, TextualConvention):
    namedValues = NamedValues(("ipf", 0), ("ipd", 1), ("opf", 2), ("opd", 3), ("iof", 4), ("iod", 5), ("oof", 6), ("ood", 7),)

class TmnxAccPlcyOICounters(Bits, TextualConvention):
    namedValues = NamedValues(("apo", 0), ("aoo", 1), ("hpd", 2), ("lpd", 3), ("hod", 4), ("lod", 5), ("ipf", 6), ("opf", 7), ("iof", 8), ("oof", 9),)

class TmnxAccPlcyOECounters(Bits, TextualConvention):
    namedValues = NamedValues(("ipf", 0), ("ipd", 1), ("opf", 2), ("opd", 3), ("iof", 4), ("iod", 5), ("oof", 6), ("ood", 7),)

class TmnxAccPlcyAACounters(Bits, TextualConvention):
    namedValues = NamedValues(("any", 0), ("sfa", 1), ("nfa", 2), ("sfd", 3), ("nfd", 4), ("saf", 5), ("naf", 6), ("spa", 7), ("npa", 8), ("sba", 9), ("nba", 10), ("spd", 11), ("npd", 12), ("sbd", 13), ("nbd", 14), ("sdf", 15), ("mdf", 16), ("ldf", 17), ("tfd", 18), ("tfc", 19), ("sbm", 20), ("spm", 21), ("smt", 22), ("nbm", 23), ("npm", 24), ("nmt", 25),)

class TmnxVdoGrpIdIndex(Unsigned32, TextualConvention):
    subtypeSpec = Unsigned32.subtypeSpec+ValueRangeConstraint(1,4)

class TmnxVdoGrpId(Unsigned32, TextualConvention):
    subtypeSpec = Unsigned32.subtypeSpec+ValueRangeConstraint(0,4)

class TmnxVdoGrpIdOrInherit(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(-1,-1),ValueRangeConstraint(0,4),)
class TmnxVdoFccServerMode(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(0, 1, 2, 3,)
    namedValues = NamedValues(("none", 0), ("burst", 1), ("dent", 2), ("hybrid", 3),)

class TmnxVdoPortNumber(Unsigned32, TextualConvention):
    subtypeSpec = Unsigned32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(1024,5999),ValueRangeConstraint(6251,65535),)
class TmnxVdoIfName(TNamedItem, TextualConvention):
    pass

class TmnxTimeInSec(Unsigned32, TextualConvention):
    subtypeSpec = Unsigned32.subtypeSpec+ValueRangeConstraint(0,86400)

class TmnxMobProfName(TNamedItem, TextualConvention):
    pass

class TmnxMobProfNameOrEmpty(TNamedItemOrEmpty, TextualConvention):
    pass

class TmnxMobProfIpTtl(Unsigned32, TextualConvention):
    subtypeSpec = Unsigned32.subtypeSpec+ValueRangeConstraint(1,255)

class TmnxMobDiaTransTimer(Unsigned32, TextualConvention):
    subtypeSpec = Unsigned32.subtypeSpec+ValueRangeConstraint(1,180)

class TmnxMobDiaRetryCount(Unsigned32, TextualConvention):
    subtypeSpec = Unsigned32.subtypeSpec+ValueRangeConstraint(0,8)

class TmnxMobDiaPeerHost(DisplayString, TextualConvention):
    subtypeSpec = DisplayString.subtypeSpec+ValueSizeConstraint(0,80)

class TmnxMobGwId(Unsigned32, TextualConvention):
    subtypeSpec = Unsigned32.subtypeSpec+ValueRangeConstraint(1,8)

class TmnxMobNode(DisplayString, TextualConvention):
    subtypeSpec = DisplayString.subtypeSpec+ValueSizeConstraint(0,30)

class TmnxMobBufferLimit(Unsigned32, TextualConvention):
    subtypeSpec = Unsigned32.subtypeSpec+ValueRangeConstraint(1000,12000)

class TmnxMobQueueLimit(Unsigned32, TextualConvention):
    subtypeSpec = Unsigned32.subtypeSpec+ValueRangeConstraint(1000,12000)

class TmnxMobRtrAdvtInterval(Unsigned32, TextualConvention):
    subtypeSpec = Unsigned32.subtypeSpec+ValueRangeConstraint(1,60)

class TmnxMobRtrAdvtLifeTime(Unsigned32, TextualConvention):
    subtypeSpec = Unsigned32.subtypeSpec+ValueRangeConstraint(1,24)

class TmnxMobAddrScheme(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2,)
    namedValues = NamedValues(("stateful", 1), ("stateless", 2),)

class TmnxMobQciValue(Unsigned32, TextualConvention):
    subtypeSpec = Unsigned32.subtypeSpec+ValueRangeConstraint(1,9)

class TmnxMobQciValueOrZero(Unsigned32, TextualConvention):
    subtypeSpec = Unsigned32.subtypeSpec+ValueRangeConstraint(0,9)

class TmnxMobArpValue(Unsigned32, TextualConvention):
    subtypeSpec = Unsigned32.subtypeSpec+ValueRangeConstraint(1,15)

class TmnxMobArpValueOrZero(Unsigned32, TextualConvention):
    subtypeSpec = Unsigned32.subtypeSpec+ValueRangeConstraint(0,15)

class TmnxMobApn(DisplayString, TextualConvention):
    subtypeSpec = DisplayString.subtypeSpec+ValueSizeConstraint(1,80)

class TmnxMobApnOrZero(DisplayString, TextualConvention):
    subtypeSpec = DisplayString.subtypeSpec+ValueSizeConstraint(0,80)

class TmnxMobImsi(OctetString, TextualConvention):
    subtypeSpec = OctetString.subtypeSpec+ValueSizeConstraint(8,8)
    fixedLength = 8

class TmnxMobMsisdn(DisplayString, TextualConvention):
    subtypeSpec = DisplayString.subtypeSpec+ValueSizeConstraint(0,15)

class TmnxMobImei(DisplayString, TextualConvention):
    subtypeSpec = DisplayString.subtypeSpec+ConstraintsUnion(ValueSizeConstraint(0,0),ValueSizeConstraint(16,16),)
class TmnxMobNai(DisplayString, TextualConvention):
    subtypeSpec = DisplayString.subtypeSpec+ValueSizeConstraint(0,72)

class TmnxMobMcc(DisplayString, TextualConvention):
    subtypeSpec = DisplayString.subtypeSpec+ValueSizeConstraint(3,3)
    fixedLength = 3

class TmnxMobMnc(DisplayString, TextualConvention):
    subtypeSpec = DisplayString.subtypeSpec+ConstraintsUnion(ValueSizeConstraint(2,2),ValueSizeConstraint(3,3),)
class TmnxMobMccOrEmpty(DisplayString, TextualConvention):
    subtypeSpec = DisplayString.subtypeSpec+ConstraintsUnion(ValueSizeConstraint(0,0),ValueSizeConstraint(3,3),)
class TmnxMobMncOrEmpty(DisplayString, TextualConvention):
    subtypeSpec = DisplayString.subtypeSpec+ConstraintsUnion(ValueSizeConstraint(0,0),ValueSizeConstraint(2,2),ValueSizeConstraint(3,3),)
class TmnxMobUeState(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2, 3, 4, 5, 6,)
    namedValues = NamedValues(("idle", 1), ("active", 2), ("paging", 3), ("init", 4), ("suspend", 5), ("ddnDamp", 6),)

class TmnxMobUeRat(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2, 3, 4, 5, 6, 7, 8, 9, 10,)
    namedValues = NamedValues(("utran", 1), ("geran", 2), ("wlan", 3), ("gan", 4), ("hspa", 5), ("eutran", 6), ("ehrpd", 7), ("hrpd", 8), ("oneXrtt", 9), ("umb", 10),)

class TmnxMobUeSubType(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2, 3,)
    namedValues = NamedValues(("homer", 1), ("roamer", 2), ("visitor", 3),)

class TmnxMobPdnType(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2, 3,)
    namedValues = NamedValues(("ipv4", 1), ("ipv6", 2), ("ipv4v6", 3),)

class TmnxMobPgwSigProtocol(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2,)
    namedValues = NamedValues(("gtp", 1), ("pmip", 2),)

class TmnxMobPdnSessionState(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13,)
    namedValues = NamedValues(("invalid", 0), ("init", 1), ("waitPcrfResponse", 2), ("waitPgwResponse", 3), ("waitEnodebUpdate", 4), ("connected", 5), ("ulDelPending", 6), ("dlDelPending", 7), ("idleMode", 8), ("pageMode", 9), ("dlHandover", 10), ("incomingHandover", 11), ("outgoingHandover", 12), ("stateMax", 13),)

class TmnxMobPdnSessionEvent(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22,)
    namedValues = NamedValues(("sessionInvalid", 0), ("gtpCreateSessReq", 1), ("gtpUpdateBearerReq", 2), ("gtpDeleteSessReq", 3), ("gtpDeleteBearerResp", 4), ("gtpUpdateBearerResp", 5), ("gtpModifyActiveToIdle", 6), ("gtpResrcAllocCmd", 7), ("gtpModifyQosCmd", 8), ("gtpX1eNodeBTeidUpdate", 9), ("gtpX2SrcSgwDeleteSessReq", 10), ("gtpS1CreateIndirectTunnel", 11), ("dlPktRecvIndication", 12), ("dlPktNotificationAck", 13), ("dlPktNotificationFail", 14), ("pcrfSessEstResp", 15), ("pcrfSessTerminateRsp", 16), ("pcrfProvQosRules", 17), ("pmipSessResp", 18), ("pmipSessUpdate", 19), ("pmipSessDeleteRsp", 20), ("pmipSessDeleteReq", 21), ("eventMax", 22),)

class TmnxMobBearerId(Unsigned32, TextualConvention):
    subtypeSpec = Unsigned32.subtypeSpec+ValueRangeConstraint(1,15)

class TmnxMobBearerType(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2,)
    namedValues = NamedValues(("default", 1), ("dedicated", 2),)

class TmnxMobQci(Unsigned32, TextualConvention):
    subtypeSpec = Unsigned32.subtypeSpec+ValueRangeConstraint(0,9)

class TmnxMobArp(Unsigned32, TextualConvention):
    subtypeSpec = Unsigned32.subtypeSpec+ValueRangeConstraint(0,15)

class TmnxMobSdf(Unsigned32, TextualConvention):
    subtypeSpec = Unsigned32.subtypeSpec+ValueRangeConstraint(0,255)

class TmnxMobSdfFilter(Unsigned32, TextualConvention):
    subtypeSpec = Unsigned32.subtypeSpec+ValueRangeConstraint(0,16)

class TmnxMobSdfFilterNum(Unsigned32, TextualConvention):
    subtypeSpec = Unsigned32.subtypeSpec+ValueRangeConstraint(0,16)

class TmnxMobSdfRuleName(DisplayString, TextualConvention):
    subtypeSpec = DisplayString.subtypeSpec+ValueSizeConstraint(1,64)

class TmnxMobSdfFilterDirection(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(0, 1, 2, 3,)
    namedValues = NamedValues(("preRel7", 0), ("downLink", 1), ("upLink", 2), ("biDir", 3),)

class TmnxMobSdfFilterProtocol(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(-1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140,)
    namedValues = NamedValues(("any", -1), ("ipv6HopByOpOpt", 0), ("icmp", 1), ("igmp", 2), ("ggp", 3), ("ip", 4), ("st", 5), ("tcp", 6), ("cbt", 7), ("egp", 8), ("igp", 9), ("bbnRccMon", 10), ("nvp2", 11), ("pup", 12), ("argus", 13), ("emcon", 14), ("xnet", 15), ("chaos", 16), ("udp", 17), ("mux", 18), ("dcnMeas", 19), ("hmp", 20), ("prm", 21), ("xnsIdp", 22), ("trunk1", 23), ("trunk2", 24), ("leaf1", 25), ("leaf2", 26), ("rdp", 27), ("irdp", 28), ("isoTp4", 29), ("netblt", 30), ("mfeNsp", 31), ("meritInp", 32), ("dccp", 33), ("pc3", 34), ("idpr", 35), ("xtp", 36), ("ddp", 37), ("idprCmtp", 38), ("tpplusplus", 39), ("il", 40), ("ipv6", 41), ("sdrp", 42), ("ipv6Route", 43), ("ipv6Frag", 44), ("idrp", 45), ("rsvp", 46), ("gre", 47), ("dsr", 48), ("bna", 49), ("esp", 50), ("ah", 51), ("iNlsp", 52), ("swipe", 53), ("narp", 54), ("mobile", 55), ("tlsp", 56), ("skip", 57), ("ipv6Icmp", 58), ("ipv6NoNxt", 59), ("ipv6Opts", 60), ("anyHostIntl", 61), ("cftp", 62), ("anyLocalNet", 63), ("satExpak", 64), ("kryptolan", 65), ("rvd", 66), ("ippc", 67), ("anyDFS", 68), ("satMon", 69), ("visa", 70), ("ipcv", 71), ("cpnx", 72), ("cphb", 73), ("wsn", 74), ("pvp", 75), ("brSatMon", 76), ("sunNd", 77), ("wbMon", 78), ("wbExpak", 79), ("isoIp", 80), ("vmtp", 81), ("secureVmpt", 82), ("vines", 83), ("ttp", 84), ("nsfnetIgp", 85), ("dgp", 86), ("tcf", 87), ("eiGrp", 88), ("ospfIgp", 89), ("spriteRpc", 90), ("larp", 91), ("mtp", 92), ("ax25", 93), ("ipip", 94), ("micp", 95), ("sccSp", 96), ("etherIp", 97), ("encap", 98), ("anyPEC", 99), ("gmtp", 100), ("ifmp", 101), ("pnni", 102), ("pim", 103), ("aris", 104), ("scps", 105), ("qnx", 106), ("activeNet", 107), ("ipComp", 108), ("snp", 109), ("compaqPeer", 110), ("ipxInIp", 111), ("vrrp", 112), ("pgm", 113), ("any0hop", 114), ("l2tp", 115), ("ddx", 116), ("iatp", 117), ("stp", 118), ("srp", 119), ("uti", 120), ("smp", 121), ("sm", 122), ("ptp", 123), ("isis", 124), ("fire", 125), ("crtp", 126), ("crudp", 127), ("sscopmce", 128), ("iplt", 129), ("sps", 130), ("pipe", 131), ("sctp", 132), ("fc", 133), ("rsvpE2eIgnore", 134), ("mobHeader", 135), ("udpLite", 136), ("mplsInIp", 137), ("manet", 138), ("hip", 139), ("shim6", 140),)

class TmnxMobPathMgmtState(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(0, 1, 2, 3, 4, 5,)
    namedValues = NamedValues(("disabled", 0), ("up", 1), ("reqTimeOut", 2), ("fault", 3), ("idle", 4), ("restart", 5),)

class TmnxMobDiaPathMgmtState(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(0, 1, 2, 3,)
    namedValues = NamedValues(("shutDown", 0), ("shuttingDown", 1), ("inactive", 2), ("active", 3),)

class TmnxMobDiaDetailPathMgmtState(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(0, 1, 2, 3, 4, 5, 6, 7, 8, 9,)
    namedValues = NamedValues(("error", 0), ("idle", 1), ("closed", 2), ("localShutdown", 3), ("remoteClosing", 4), ("waitConnAck", 5), ("waitCea", 6), ("open", 7), ("openCoolingDown", 8), ("waitDns", 9),)

class TmnxMobGwType(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2, 3,)
    namedValues = NamedValues(("sgw", 1), ("pgw", 2), ("wlanGw", 3),)

class TmnxMobChargingProfile(Unsigned32, TextualConvention):
    subtypeSpec = Unsigned32.subtypeSpec+ValueRangeConstraint(0,255)

class TmnxMobChargingProfileOrInherit(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(-1,-1),ValueRangeConstraint(0,255),)
class TmnxMobAuthType(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2,)
    namedValues = NamedValues(("radius", 1), ("diameter", 2),)

class TmnxMobAuthUserName(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2, 3,)
    namedValues = NamedValues(("imsi", 1), ("msisdn", 2), ("pco", 3),)

class TmnxMobProfGbrRate(Unsigned32, TextualConvention):
    subtypeSpec = Unsigned32.subtypeSpec+ValueRangeConstraint(0,100000)

class TmnxMobProfMbrRate(Unsigned32, TextualConvention):
    subtypeSpec = Unsigned32.subtypeSpec+ValueRangeConstraint(0,100000)

class TmnxMobPeerType(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2, 3,)
    namedValues = NamedValues(("sgw", 1), ("pgw", 2), ("hsgw", 3),)

class TmnxMobRfAcctLevel(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2,)
    namedValues = NamedValues(("pdnLevel", 1), ("qciLevel", 2),)

class TmnxMobProfPolReportingLevel(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2,)
    namedValues = NamedValues(("servId", 1), ("ratingGrp", 2),)

class TmnxMobProfPolChargingMethod(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(0, 1, 2, 3,)
    namedValues = NamedValues(("profChargingMtd", 0), ("online", 1), ("offline", 2), ("both", 3),)

class TmnxMobProfPolMeteringMethod(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2, 3,)
    namedValues = NamedValues(("timeBased", 1), ("volBased", 2), ("both", 3),)

class TmnxMobServerState(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(0, 1, 2,)
    namedValues = NamedValues(("na", 0), ("up", 1), ("down", 2),)

class TmnxMobChargingBearerType(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2, 3,)
    namedValues = NamedValues(("home", 1), ("visiting", 2), ("roaming", 3),)

class TmnxMobChargingLevel(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2,)
    namedValues = NamedValues(("pdn", 1), ("bearer", 2),)

class TmnxMobIpCanType(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2,)
    namedValues = NamedValues(("epc3gpp", 1), ("gprs3gpp", 2),)

class TmnxMobStaticPolPrecedence(Unsigned32, TextualConvention):
    subtypeSpec = Unsigned32.subtypeSpec+ValueRangeConstraint(1,65536)

class TmnxMobStaticPolPrecedenceOrZero(Unsigned32, TextualConvention):
    subtypeSpec = Unsigned32.subtypeSpec+ValueRangeConstraint(0,65535)

class TmnxMobDualStackPref(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2, 3,)
    namedValues = NamedValues(("ipv4", 1), ("ipv6", 2), ("useCplane", 3),)

class TmnxMobDfPeerId(Unsigned32, TextualConvention):
    subtypeSpec = Unsigned32.subtypeSpec+ValueRangeConstraint(1,16)

class TmnxMobLiTarget(OctetString, TextualConvention):
    subtypeSpec = OctetString.subtypeSpec+ValueSizeConstraint(8,8)
    fixedLength = 8

class TmnxMobLiTargetType(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2, 3,)
    namedValues = NamedValues(("imsi", 1), ("msisdn", 2), ("imei", 3),)

class TmnxReasContextVal(Unsigned32, TextualConvention):
    subtypeSpec = Unsigned32.subtypeSpec+ValueRangeConstraint(0,31)

class TmnxVdoStatInt(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2,)
    namedValues = NamedValues(("current", 1), ("interval", 2),)

class TmnxVdoOutputFormat(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2,)
    namedValues = NamedValues(("udp", 1), ("rtp-udp", 2),)

class TmnxVdoAnalyzerAlarm(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(0, 1, 2, 3,)
    namedValues = NamedValues(("none", 0), ("tnc", 1), ("qos", 2), ("poa", 3),)

class TmnxVdoAnalyzerAlarmStates(OctetString, TextualConvention):
    subtypeSpec = OctetString.subtypeSpec+ValueSizeConstraint(10,10)
    fixedLength = 10

class SvcISID(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(-1,-1),ValueRangeConstraint(0,16777215),)
class TIngPolicerId(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ValueRangeConstraint(1,32)

class TIngPolicerIdOrNone(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(0,0),ValueRangeConstraint(1,32),)
class TEgrPolicerId(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ValueRangeConstraint(1,8)

class TEgrPolicerIdOrNone(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(0,0),ValueRangeConstraint(1,8),)
class TFIRRate(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(-1,-1),ValueRangeConstraint(1,100000000),)
class TBurstSizeBytes(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(-1,-1),ValueRangeConstraint(0,134217728),)
class THSMDABurstSizeBytes(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(-1,-1),ValueRangeConstraint(0,2688000),)
class THSMDAQueueBurstLimit(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(-1,-1),ValueRangeConstraint(1,1000000),)
class TClassBurstLimit(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(-1,-1),ValueRangeConstraint(1,327680),)
class TPlcrBurstSizeBytes(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(-1,-1),ValueRangeConstraint(0,4194304),)
class TBurstSizeBytesOverride(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(-2,-2),ValueRangeConstraint(-1,-1),ValueRangeConstraint(0,134217728),)
class THSMDABurstSizeBytesOverride(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(-2,-2),ValueRangeConstraint(-1,-1),ValueRangeConstraint(0,2688000),)
class TPlcrBurstSizeBytesOverride(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(-2,-2),ValueRangeConstraint(-1,-1),ValueRangeConstraint(0,4194304),)
class TmnxBfdSessOperState(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2, 3, 4, 5, 6,)
    namedValues = NamedValues(("unknown", 1), ("connected", 2), ("broken", 3), ("peerDetectsDown", 4), ("notConfigured", 5), ("noResources", 6),)

class TmnxIngPolicerStatMode(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(0, 1, 2, 3, 4, 5, 6, 7, 8, 9,)
    namedValues = NamedValues(("noStats", 0), ("minimal", 1), ("offeredProfileNoCIR", 2), ("offeredTotalCIR", 3), ("offeredPrioNoCIR", 4), ("offeredProfileCIR", 5), ("offeredPrioCIR", 6), ("offeredLimitedProfileCIR", 7), ("offeredProfileCapCIR", 8), ("offeredLimitedCapCIR", 9),)

class TmnxIngPolicerStatModeOverride(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(-1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9,)
    namedValues = NamedValues(("noOverride", -1), ("noStats", 0), ("minimal", 1), ("offeredProfileNoCIR", 2), ("offeredTotalCIR", 3), ("offeredPrioNoCIR", 4), ("offeredProfileCIR", 5), ("offeredPrioCIR", 6), ("offeredLimitedProfileCIR", 7), ("offeredProfileCapCIR", 8), ("offeredLimitedCapCIR", 9),)

class TmnxEgrPolicerStatMode(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(0, 1, 2, 3, 4, 5, 6,)
    namedValues = NamedValues(("noStats", 0), ("minimal", 1), ("offeredProfileNoCIR", 2), ("offeredTotalCIR", 3), ("offeredProfileCIR", 4), ("offeredLimitedCapCIR", 5), ("offeredProfileCapCIR", 6),)

class TmnxEgrPolicerStatModeOverride(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(-1, 0, 1, 2, 3, 4, 5, 6,)
    namedValues = NamedValues(("noOverride", -1), ("noStats", 0), ("minimal", 1), ("offeredProfileNoCIR", 2), ("offeredTotalCIR", 3), ("offeredProfileCIR", 4), ("offeredLimitedCapCIR", 5), ("offeredProfileCapCIR", 6),)

class TmnxTlsGroupId(Unsigned32, TextualConvention):
    subtypeSpec = Unsigned32.subtypeSpec+ValueRangeConstraint(1,4094)

class TSubHostId(Unsigned32, TextualConvention):
    pass

class TDirection(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(0, 1, 2,)
    namedValues = NamedValues(("both", 0), ("ingress", 1), ("egress", 2),)

class TBurstLimit(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(-1,-1),ValueRangeConstraint(1,14000000),)
class TMacFilterType(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2, 3,)
    namedValues = NamedValues(("normal", 1), ("isid", 2), ("vid", 3),)

class TmnxPwGlobalId(Unsigned32, TextualConvention):
    subtypeSpec = Unsigned32.subtypeSpec+ValueRangeConstraint(1,4294967295)

class TmnxPwGlobalIdOrZero(Unsigned32, TextualConvention):
    pass

class TmnxPwPathHopId(Unsigned32, TextualConvention):
    subtypeSpec = Unsigned32.subtypeSpec+ValueRangeConstraint(1,16)

class TmnxPwPathHopIdOrZero(Unsigned32, TextualConvention):
    subtypeSpec = Unsigned32.subtypeSpec+ValueRangeConstraint(0,16)

class TmnxSpokeSdpId(Unsigned32, TextualConvention):
    subtypeSpec = Unsigned32.subtypeSpec+ValueRangeConstraint(1,4294967295)

class TmnxSpokeSdpIdOrZero(Unsigned32, TextualConvention):
    pass

class TmnxMsPwPeSignaling(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2,)
    namedValues = NamedValues(("auto", 1), ("master", 2),)

class TmnxLdpFECType(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2, 3, 128, 129, 130,)
    namedValues = NamedValues(("addrWildcard", 1), ("addrPrefix", 2), ("addrHost", 3), ("vll", 128), ("vpws", 129), ("vpls", 130),)

class TmnxSvcOperGrpCreationOrigin(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2,)
    namedValues = NamedValues(("manual", 1), ("mvrp", 2),)

class TmnxOperGrpHoldUpTime(Unsigned32, TextualConvention):
    subtypeSpec = Unsigned32.subtypeSpec+ValueRangeConstraint(0,3600)

class TmnxOperGrpHoldDownTime(Unsigned32, TextualConvention):
    subtypeSpec = Unsigned32.subtypeSpec+ValueRangeConstraint(0,3600)

class TmnxSrrpPriorityStep(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ValueRangeConstraint(0,10)

class TmnxAiiType(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2,)
    namedValues = NamedValues(("aiiType1", 1), ("aiiType2", 2),)

class ServObjDesc(DisplayString, TextualConvention):
    subtypeSpec = DisplayString.subtypeSpec+ValueSizeConstraint(0,80)

class TMplsLspExpProfMapID(TPolicyID, TextualConvention):
    subtypeSpec = TPolicyID.subtypeSpec+ValueRangeConstraint(1,65535)

class TSysResource(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ConstraintsUnion(ValueRangeConstraint(-1,-1),ValueRangeConstraint(0,11),)
class TmnxSpbFid(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ValueRangeConstraint(1,4095)

class TmnxSpbFidOrZero(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ValueRangeConstraint(0,4095)

class TmnxSpbBridgePriority(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ValueRangeConstraint(0,15)

class TmnxSlopeMap(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(0, 1, 2, 3,)
    namedValues = NamedValues(("none", 0), ("low", 1), ("high", 2), ("highLow", 3),)

class TmnxCdrType(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2, 3,)
    namedValues = NamedValues(("pgwCdr", 1), ("gCdr", 2), ("eGCdr", 3),)

class TmnxThresholdGroupType(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2, 3, 4, 5, 6, 7,)
    namedValues = NamedValues(("brMgmtLimit", 1), ("brMgmtCfSuccess", 2), ("brMgmtCfFailure", 3), ("brMgmtTraffic", 4), ("pathMgmt", 5), ("cpmSystem", 6), ("mgIsmSystem", 7),)

class TmnxMobUeId(OctetString, TextualConvention):
    subtypeSpec = OctetString.subtypeSpec+ValueSizeConstraint(8,8)
    fixedLength = 8

class TmnxMobUeIdType(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(0, 1, 2,)
    namedValues = NamedValues(("imsi", 0), ("imei", 1), ("msisdn", 2),)

class TmnxMobImsiStr(DisplayString, TextualConvention):
    subtypeSpec = DisplayString.subtypeSpec+ConstraintsUnion(ValueSizeConstraint(0,0),ValueSizeConstraint(9,15),)
class TmnxVpnIpBackupFamily(Bits, TextualConvention):
    namedValues = NamedValues(("ipv4", 0), ("ipv6", 1),)

class TmnxTunnelGroupId(Unsigned32, TextualConvention):
    subtypeSpec = Unsigned32.subtypeSpec+ValueRangeConstraint(1,16)

class TmnxTunnelGroupIdOrZero(Unsigned32, TextualConvention):
    subtypeSpec = Unsigned32.subtypeSpec+ValueRangeConstraint(0,16)

class TmnxMobRatingGrpState(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2, 3, 4, 5, 6, 7, 8,)
    namedValues = NamedValues(("allowFlow", 1), ("disallowFlow", 2), ("redWebPortal", 3), ("allowResRules", 4), ("iom1stPktTrigger", 5), ("dis1stPktTrigger", 6), ("creditsToppedUp", 7), ("waitForFpt", 8),)

class TmnxMobPresenceState(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(0, 1,)
    namedValues = NamedValues(("absent", 0), ("present", 1),)

class TmnxMobPdnGyChrgTriggerType(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29,)
    namedValues = NamedValues(("sgsnIpAddrRecvd", 0), ("qosRecvd", 1), ("locRecvd", 2), ("ratRecvd", 3), ("qosTrfClsRecvd", 4), ("qosRlbClsRecvd", 5), ("qosDlyClsRecvd", 6), ("qosPeakThrptRecvd", 7), ("qosPrcClsRecvd", 8), ("qosMeanTrptRecvd", 9), ("qosMxBtRtUplnkRecvd", 10), ("qosMxBtRtDllnkRecvd", 11), ("qosResBerRecvd", 12), ("qosSduErrRatRecvd", 13), ("qosTransDelayRecvd", 14), ("qosTrfHndPriRecvd", 15), ("qosGrtBtRtUplnkRecvd", 16), ("qosGrtBtRtDllnkRecvd", 17), ("locMccRecvd", 18), ("locMncRecvd", 19), ("locRacRecvd", 20), ("locLacRecvd", 21), ("locCellIdRecvd", 22), ("medCompRecvd", 23), ("partcNmbRecvd", 24), ("thrldPartcNmbRecvd", 25), ("usrPartcTypeRecvd", 26), ("servCondRecvd", 27), ("servNodeRecvd", 28), ("usrCsgInfoRecvd", 29),)

class TmnxMobPdnRefPointType(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2, 3, 4, 5,)
    namedValues = NamedValues(("s5", 1), ("s8", 2), ("gn", 3), ("s2a", 4), ("gp", 5),)

class TmnxQosBytesHex(OctetString, TextualConvention):
    displayHint = '2x '
    subtypeSpec = OctetString.subtypeSpec+ValueSizeConstraint(0,30)

class TSiteOperStatus(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2, 3,)
    namedValues = NamedValues(("up", 1), ("down", 2), ("outOfResource", 3),)

class TmnxSpbFdbLocale(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2, 3, 4,)
    namedValues = NamedValues(("local", 1), ("sap", 2), ("sdp", 3), ("unknown", 4),)

class TmnxSpbFdbState(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(0, 1, 2, 3, 4, 5, 6,)
    namedValues = NamedValues(("ok", 0), ("addModPending", 1), ("delPending", 2), ("sysFdbLimit", 3), ("noFateShared", 4), ("svcFdbLimit", 5), ("noUcast", 6),)

class TmnxMobServRefPointType(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2, 4,)
    namedValues = NamedValues(("s5", 1), ("s8", 2), ("s2a", 4),)

class TmnxMobAccessType(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2, 3,)
    namedValues = NamedValues(("eps", 1), ("gprs", 2), ("non3gpp", 3),)

class TmnxMobUeStrPrefix(DisplayString, TextualConvention):
    subtypeSpec = DisplayString.subtypeSpec+ValueSizeConstraint(4,15)

class TmnxCdrDiagnosticAction(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2,)
    namedValues = NamedValues(("included", 1), ("excluded", 2),)

class TmnxMplsTpGlobalID(Unsigned32, TextualConvention):
    pass

class TmnxMplsTpNodeID(Unsigned32, TextualConvention):
    pass

class TmnxMplsTpTunnelType(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1,)
    namedValues = NamedValues(("mplsTpStatic", 1),)

class TmnxVwmCardType(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44,)
    namedValues = NamedValues(("not-provisioned", 0), ("not-equipped", 1), ("sfc1A", 2), ("sfc1B", 3), ("sfc1C", 4), ("sfc1D", 5), ("sfc1E", 6), ("sfc1F", 7), ("sfc1G", 8), ("sfc1H", 9), ("sfc2AandB", 10), ("sfc2CandD", 11), ("sfc2EandF", 12), ("sfc2GandH", 13), ("sfc4A-D", 14), ("sfc4E-H", 15), ("sfc8", 16), ("sfd8A-R", 17), ("sfd8B-R", 18), ("sfd8C-R", 19), ("sfd8D-R", 20), ("sfd4A-R", 21), ("sfd4B-R", 22), ("sfd4C-R", 23), ("sfd4D-R", 24), ("sfd4E-R", 25), ("sfd4F-R", 26), ("sfd4G-R", 27), ("sfd4H-R", 28), ("sfd2A-R", 29), ("sfd2B-R", 30), ("sfd2C-R", 31), ("sfd2D-R", 32), ("sfd2E-R", 33), ("sfd2F-R", 34), ("sfd2G-R", 35), ("sfd2H-R", 36), ("sfd2I-R", 37), ("sfd2L-R", 38), ("sfd2M-R", 39), ("sfd2N-R", 40), ("sfd2O-R", 41), ("sfd2P-R", 42), ("sfd2Q-R", 43), ("sfd2R-R", 44),)

mibBuilder.exportSymbols("TIMETRA-TC-MIB", TmnxMobChargingProfileOrInherit=TmnxMobChargingProfileOrInherit, QTagFullRangeOrNone=QTagFullRangeOrNone, TEgressHsmdaQueueId=TEgressHsmdaQueueId, TmnxMldVersion=TmnxMldVersion, TmnxMobImsi=TmnxMobImsi, TmnxSpbFdbLocale=TmnxSpbFdbLocale, QTagFullRange=QTagFullRange, TmnxMobDiaDetailPathMgmtState=TmnxMobDiaDetailPathMgmtState, THsmdaWeightOverride=THsmdaWeightOverride, THPolPIRRate=THPolPIRRate, TNonZeroWeight=TNonZeroWeight, TmnxTimeInSec=TmnxTimeInSec, THsmdaPIRKRateOverride=THsmdaPIRKRateOverride, TmnxVdoOutputFormat=TmnxVdoOutputFormat, TmnxOperGrpHoldUpTime=TmnxOperGrpHoldUpTime, TPlcyMode=TPlcyMode, TmnxMobSdfFilterNum=TmnxMobSdfFilterNum, ServObjDesc=ServObjDesc, TSysResource=TSysResource, TmnxMobMnc=TmnxMobMnc, TmnxMobStaticPolPrecedence=TmnxMobStaticPolPrecedence, TmnxBsxAarpServiceRefType=TmnxBsxAarpServiceRefType, TmnxMobAuthUserName=TmnxMobAuthUserName, TBWRateType=TBWRateType, TmnxMobUeState=TmnxMobUeState, TmnxMobNai=TmnxMobNai, TmnxTunnelID=TmnxTunnelID, THsmdaPIRKRate=THsmdaPIRKRate, TSapEgrEncapGroupType=TSapEgrEncapGroupType, TmnxVRtrIDOrZero=TmnxVRtrIDOrZero, TBurstPercent=TBurstPercent, TmnxPppoeSessionInfoOrigin=TmnxPppoeSessionInfoOrigin, TmnxSlaProfileString=TmnxSlaProfileString, TEgressQPerPacketOffset=TEgressQPerPacketOffset, TIngPolicerId=TIngPolicerId, TmnxVcIdOrNone=TmnxVcIdOrNone, TmnxAncpStringOrZero=TmnxAncpStringOrZero, TmnxSubMgtOrgStrOrZero=TmnxSubMgtOrgStrOrZero, TmnxMobSdfFilterDirection=TmnxMobSdfFilterDirection, TIngressHsmdaPerPacketOffset=TIngressHsmdaPerPacketOffset, TNamedItem=TNamedItem, TmnxIkePolicyOwnAuthMethod=TmnxIkePolicyOwnAuthMethod, THPolVirtualSchePIRRate=THPolVirtualSchePIRRate, TmnxMobMcc=TmnxMobMcc, TmnxSubRadiusAttrType=TmnxSubRadiusAttrType, TmnxVdoGrpIdIndex=TmnxVdoGrpIdIndex, TmnxSubRadiusVendorId=TmnxSubRadiusVendorId, TQosOverrideType=TQosOverrideType, TPlcrBurstSizeBytes=TPlcrBurstSizeBytes, TmnxSpokeSdpIdOrZero=TmnxSpokeSdpIdOrZero, TmnxMobBufferLimit=TmnxMobBufferLimit, THsmdaCIRMRateOverride=THsmdaCIRMRateOverride, TmnxMobPdnSessionState=TmnxMobPdnSessionState, TSapIngressPolicyID=TSapIngressPolicyID, TFIRRate=TFIRRate, THSMDABurstSizeBytesOverride=THSMDABurstSizeBytesOverride, TmnxSubMgtIntDestId=TmnxSubMgtIntDestId, TItemDescription=TItemDescription, TmnxMobAccessType=TmnxMobAccessType, TEgressHsmdaCounterId=TEgressHsmdaCounterId, TmnxSlaProfileStringOrEmpty=TmnxSlaProfileStringOrEmpty, TmnxSpbBridgePriority=TmnxSpbBridgePriority, TmnxServId=TmnxServId, TPortSchedulerPIR=TPortSchedulerPIR, TmnxPppoeSessionType=TmnxPppoeSessionType, TmnxMobUeId=TmnxMobUeId, TmnxMobMncOrEmpty=TmnxMobMncOrEmpty, TmnxLdpFECType=TmnxLdpFECType, TmnxMobDiaPathMgmtState=TmnxMobDiaPathMgmtState, PYSNMP_MODULE_ID=timetraTCMIBModule, THPolCIRRate=THPolCIRRate, TmnxReasContextVal=TmnxReasContextVal, TmnxMobGwId=TmnxMobGwId, SvcISID=SvcISID, TmnxVcId=TmnxVcId, TPolicyID=TPolicyID, TmnxBinarySpecification=TmnxBinarySpecification, TmnxMobPresenceState=TmnxMobPresenceState, TSapEgrEncapGrpQosPolicyIdOrZero=TSapEgrEncapGrpQosPolicyIdOrZero, TDSCPValueOrNone=TDSCPValueOrNone, TmnxIngPolicerStatMode=TmnxIngPolicerStatMode, TmnxMobChargingBearerType=TmnxMobChargingBearerType, TLNamedItemOrEmpty=TLNamedItemOrEmpty, TmnxMobSdfFilterProtocol=TmnxMobSdfFilterProtocol, TBurstLimit=TBurstLimit, TPIRRateOrZero=TPIRRateOrZero, TNetworkIngressMeterId=TNetworkIngressMeterId, TmnxSpbFdbState=TmnxSpbFdbState, TmnxRadiusServerOperState=TmnxRadiusServerOperState, TmnxMobProfPolReportingLevel=TmnxMobProfPolReportingLevel, TCpmProtPolicyIDOrDefault=TCpmProtPolicyIDOrDefault, TMeterMode=TMeterMode, TmnxMobDiaRetryCount=TmnxMobDiaRetryCount, TmnxMldGroupFilterMode=TmnxMldGroupFilterMode, TPIRRate=TPIRRate, TQueueIdOrAll=TQueueIdOrAll, TmnxOperGrpHoldDownTime=TmnxOperGrpHoldDownTime, TmnxAncpString=TmnxAncpString, TmnxMobPdnRefPointType=TmnxMobPdnRefPointType, TmnxMobDiaTransTimer=TmnxMobDiaTransTimer, TBurstSizeBytesOverride=TBurstSizeBytesOverride, SdpBindId=SdpBindId, TmnxCdrDiagnosticAction=TmnxCdrDiagnosticAction, TmnxBfdSessOperState=TmnxBfdSessOperState, THsmdaSchedulerPolicyGroupId=THsmdaSchedulerPolicyGroupId, TmnxMobRtrAdvtInterval=TmnxMobRtrAdvtInterval, TmnxBgpRouteTarget=TmnxBgpRouteTarget, TPrecValue=TPrecValue, TmnxSubNasPortPrefixType=TmnxSubNasPortPrefixType, TmnxActionType=TmnxActionType, QTagOrZero=QTagOrZero, TPIRRateOverride=TPIRRateOverride, TmnxVdoPortNumber=TmnxVdoPortNumber, THsmdaPIRMRateOverride=THsmdaPIRMRateOverride, TPerPacketOffsetOvr=TPerPacketOffsetOvr, TProfile=TProfile, TmnxOperState=TmnxOperState, TmnxMdaQos=TmnxMdaQos, TEgrHsmdaPerPacketOffsetOvr=TEgrHsmdaPerPacketOffsetOvr, TOperator=TOperator, TmnxMobChargingProfile=TmnxMobChargingProfile, TPlcrBurstSizeBytesOverride=TPlcrBurstSizeBytesOverride, THSMDABurstSizeBytes=THSMDABurstSizeBytes, TmnxRadiusPendingReqLimit=TmnxRadiusPendingReqLimit, TmnxIngPolicerStatModeOverride=TmnxIngPolicerStatModeOverride, TBurstSizeBytes=TBurstSizeBytes, TmnxAccessLoopEncaps2=TmnxAccessLoopEncaps2, TmnxVdoIfName=TmnxVdoIfName, TLevelOrDefault=TLevelOrDefault, THPolCIRRateOverride=THPolCIRRateOverride, TRemarkType=TRemarkType, TEgressHsmdaCounterIdOrZero=TEgressHsmdaCounterIdOrZero, TmnxPwGlobalId=TmnxPwGlobalId, TProfileOrDei=TProfileOrDei, TmnxMobArpValue=TmnxMobArpValue, TDEProfile=TDEProfile, TmnxDHCP6MsgType=TmnxDHCP6MsgType, TmnxVPNRouteDistinguisher=TmnxVPNRouteDistinguisher, TmnxMobProfPolMeteringMethod=TmnxMobProfPolMeteringMethod, TmnxIgmpGroupType=TmnxIgmpGroupType, TmnxMsPwPeSignaling=TmnxMsPwPeSignaling, TAtmTdpDescrType=TAtmTdpDescrType, TAdaptationRule=TAdaptationRule, TmnxIgmpVersion=TmnxIgmpVersion, TmnxSlopeMap=TmnxSlopeMap, TPortSchedulerCIR=TPortSchedulerCIR, TmnxBsxTransitIpPolicyId=TmnxBsxTransitIpPolicyId, TmnxMobGwType=TmnxMobGwType, TmnxAppProfileStringOrEmpty=TmnxAppProfileStringOrEmpty, TPolicyStatementNameOrEmpty=TPolicyStatementNameOrEmpty, TFCType=TFCType, TPriority=TPriority, TmnxVcType=TmnxVcType, TmnxMobUeIdType=TmnxMobUeIdType, TmnxSubNasPortSuffixType=TmnxSubNasPortSuffixType, TmnxMobNode=TmnxMobNode, TmnxMobImsiStr=TmnxMobImsiStr, TEntryIndicator=TEntryIndicator, THPolPIRRateOverride=THPolPIRRateOverride, THsmdaCounterIdOrZeroOrAll=THsmdaCounterIdOrZeroOrAll, TmnxMobUeStrPrefix=TmnxMobUeStrPrefix, TmnxEnabledDisabled=TmnxEnabledDisabled, TmnxTunnelGroupId=TmnxTunnelGroupId, TmnxIpSecIsaOperFlags=TmnxIpSecIsaOperFlags, TDSCPFilterActionValue=TDSCPFilterActionValue, TmnxAccPlcyOECounters=TmnxAccPlcyOECounters, TmnxMobProfMbrRate=TmnxMobProfMbrRate, TSdpIngressPolicyID=TSdpIngressPolicyID, TmnxQosBytesHex=TmnxQosBytesHex, TmnxMobUeRat=TmnxMobUeRat, TmnxMobQciValueOrZero=TmnxMobQciValueOrZero, THsmdaPIRMRate=THsmdaPIRMRate, TmnxSrrpPriorityStep=TmnxSrrpPriorityStep, TmnxAccPlcyQICounters=TmnxAccPlcyQICounters, TQosQGrpInstanceIDorZero=TQosQGrpInstanceIDorZero, TSiteOperStatus=TSiteOperStatus, TmnxCdrType=TmnxCdrType, TFCName=TFCName, TmnxSubAleOffset=TmnxSubAleOffset, TIngressHsmdaCounterId=TIngressHsmdaCounterId, TPolicerWeight=TPolicerWeight, TmnxSubAleOffsetMode=TmnxSubAleOffsetMode, TAdvCfgRate=TAdvCfgRate, TmnxMobPdnType=TmnxMobPdnType, TmnxMobProfName=TmnxMobProfName, TmnxAdminState=TmnxAdminState, TmnxDhcpOptionType=TmnxDhcpOptionType, TmnxMobImei=TmnxMobImei, TmnxMobArp=TmnxMobArp, TBurstPercentOrDefaultOverride=TBurstPercentOrDefaultOverride, TmnxPwPathHopId=TmnxPwPathHopId, TmnxEgrPolicerStatModeOverride=TmnxEgrPolicerStatModeOverride, TCpmProtPolicyID=TCpmProtPolicyID, TClassBurstLimit=TClassBurstLimit, TmnxMobDualStackPref=TmnxMobDualStackPref, TmnxSpbFid=TmnxSpbFid, TmnxSubNasPortTypeType=TmnxSubNasPortTypeType, TmnxManagedRouteStatus=TmnxManagedRouteStatus, TmnxMobQueueLimit=TmnxMobQueueLimit, TmnxTunnelType=TmnxTunnelType, TmnxVRtrMplsLspID=TmnxVRtrMplsLspID, TmnxTlsGroupId=TmnxTlsGroupId, TmnxVdoFccServerMode=TmnxVdoFccServerMode, TLNamedItem=TLNamedItem, TmnxAccessLoopEncaps1=TmnxAccessLoopEncaps1, TMlpppQoSProfileId=TMlpppQoSProfileId, TmnxMobProfGbrRate=TmnxMobProfGbrRate, TmnxMobPgwSigProtocol=TmnxMobPgwSigProtocol, TSdpEgressPolicyID=TSdpEgressPolicyID, TmnxMobProfIpTtl=TmnxMobProfIpTtl, TmnxRsvpDSTEClassType=TmnxRsvpDSTEClassType, TmnxDefSubIdSource=TmnxDefSubIdSource, TmnxPwGlobalIdOrZero=TmnxPwGlobalIdOrZero, TmnxBgpPreference=TmnxBgpPreference, TMaxDecRate=TMaxDecRate, TmnxMobIpCanType=TmnxMobIpCanType, TmnxAiiType=TmnxAiiType, TmnxBsxTransPrefPolicyIdOrZero=TmnxBsxTransPrefPolicyIdOrZero, TmnxBgpLocalPreference=TmnxBgpLocalPreference, TBurstPercentOrDefault=TBurstPercentOrDefault, TmnxMobQci=TmnxMobQci, TBurstSizeOverride=TBurstSizeOverride, TRateType=TRateType, TmnxBgpAutonomousSystem=TmnxBgpAutonomousSystem, TQWeight=TQWeight, TmnxMobRfAcctLevel=TmnxMobRfAcctLevel, TPIRPercentOverride=TPIRPercentOverride, TNetworkPolicyID=TNetworkPolicyID, TEgressQueueId=TEgressQueueId, TmnxSpbFidOrZero=TmnxSpbFidOrZero, TmnxMobMsisdn=TmnxMobMsisdn, TmnxBsxAarpIdOrZero=TmnxBsxAarpIdOrZero, TMcFrQoSProfileId=TMcFrQoSProfileId, TmnxBGPFamilyType=TmnxBGPFamilyType, TmnxMobDfPeerId=TmnxMobDfPeerId, TPortSchedulerPIRRate=TPortSchedulerPIRRate, TmnxMobBearerType=TmnxMobBearerType, TSapIngressMeterId=TSapIngressMeterId, TmnxMobPdnSessionEvent=TmnxMobPdnSessionEvent, TmnxMobPdnGyChrgTriggerType=TmnxMobPdnGyChrgTriggerType, TDEProfileOrDei=TDEProfileOrDei, TCIRRate=TCIRRate, TmnxMobRatingGrpState=TmnxMobRatingGrpState, TmnxOspfInstance=TmnxOspfInstance, TmnxMobStaticPolPrecedenceOrZero=TmnxMobStaticPolPrecedenceOrZero, THsmdaPolicyScheduleClass=THsmdaPolicyScheduleClass, TmnxMobPeerType=TmnxMobPeerType, TCIRRateOverride=TCIRRateOverride, Dot1PPriorityMask=Dot1PPriorityMask, TmnxVwmCardType=TmnxVwmCardType, THsmdaWrrWeightOverride=THsmdaWrrWeightOverride, TmnxMplsTpNodeID=TmnxMplsTpNodeID, TmnxAccPlcyOICounters=TmnxAccPlcyOICounters, TmnxMobArpValueOrZero=TmnxMobArpValueOrZero)
mibBuilder.exportSymbols("TIMETRA-TC-MIB", TmnxMacSpecification=TmnxMacSpecification, TIpProtocol=TIpProtocol, TmnxMobPathMgmtState=TmnxMobPathMgmtState, TEntryId=TEntryId, TTmplPolicyID=TTmplPolicyID, TmnxMobApnOrZero=TmnxMobApnOrZero, TmnxStrSapId=TmnxStrSapId, TDirection=TDirection, TmnxMlpppEpClass=TmnxMlpppEpClass, TmnxMobMccOrEmpty=TmnxMobMccOrEmpty, TFCSet=TFCSet, TRatePercent=TRatePercent, TmnxCustId=TmnxCustId, TmnxIgmpGroupFilterMode=TmnxIgmpGroupFilterMode, TmnxMobServerState=TmnxMobServerState, TmnxMplsTpGlobalID=TmnxMplsTpGlobalID, TmnxMobQciValue=TmnxMobQciValue, QTag=QTag, TNamedItemOrEmpty=TNamedItemOrEmpty, TItemMatch=TItemMatch, TPIRRatePercent=TPIRRatePercent, TMatchCriteria=TMatchCriteria, TSapEgrEncapGroupActionType=TSapEgrEncapGroupActionType, TmnxEncapVal=TmnxEncapVal, TProfileOrNone=TProfileOrNone, TWeight=TWeight, timetraTCMIBModule=timetraTCMIBModule, TmnxIPsecTunnelTemplateId=TmnxIPsecTunnelTemplateId, TmnxEgrPolicerStatMode=TmnxEgrPolicerStatMode, TmnxSubMgtIntDestIdOrEmpty=TmnxSubMgtIntDestIdOrEmpty, TEgrPolicerId=TEgrPolicerId, BgpPeeringStatus=BgpPeeringStatus, TmnxIkePolicyAuthMethod=TmnxIkePolicyAuthMethod, TmnxAccPlcyQECounters=TmnxAccPlcyQECounters, TmnxIPsecTunnelTemplateIdOrZero=TmnxIPsecTunnelTemplateIdOrZero, TmnxMobProfNameOrEmpty=TmnxMobProfNameOrEmpty, THPolVirtualScheCIRRate=THPolVirtualScheCIRRate, TPriorityOrUndefined=TPriorityOrUndefined, TPriorityOrDefault=TPriorityOrDefault, TmnxMobSdfFilter=TmnxMobSdfFilter, TmnxVdoStatInt=TmnxVdoStatInt, TBurstSize=TBurstSize, TmnxVdoAnalyzerAlarm=TmnxVdoAnalyzerAlarm, TmnxSubIdentString=TmnxSubIdentString, TLspExpValue=TLspExpValue, ServiceAdminStatus=ServiceAdminStatus, TPolicerRateType=TPolicerRateType, TIngressHsmdaQueueId=TIngressHsmdaQueueId, TEgrPolicerIdOrNone=TEgrPolicerIdOrNone, TIngPolicerIdOrNone=TIngPolicerIdOrNone, TQueueId=TQueueId, TDSCPName=TDSCPName, TmnxSubProfileStringOrEmpty=TmnxSubProfileStringOrEmpty, TmnxMobRtrAdvtLifeTime=TmnxMobRtrAdvtLifeTime, TExpSecondaryShaperPIRRate=TExpSecondaryShaperPIRRate, TmnxThresholdGroupType=TmnxThresholdGroupType, TmnxMobAuthType=TmnxMobAuthType, TmnxVdoAnalyzerAlarmStates=TmnxVdoAnalyzerAlarmStates, IpAddressPrefixLength=IpAddressPrefixLength, TAdaptationRuleOverride=TAdaptationRuleOverride, TmnxAsciiSpecification=TmnxAsciiSpecification, TPerPacketOffset=TPerPacketOffset, THsmdaCIRKRateOverride=THsmdaCIRKRateOverride, TmnxPppoeSessionId=TmnxPppoeSessionId, TmnxVpnIpBackupFamily=TmnxVpnIpBackupFamily, THsmdaWeight=THsmdaWeight, TEgrRateModType=TEgrRateModType, TmnxPppoePadoDelay=TmnxPppoePadoDelay, TSapEgressPolicyID=TSapEgressPolicyID, TSecondaryShaper10GPIRRate=TSecondaryShaper10GPIRRate, THsmdaCIRMRate=THsmdaCIRMRate, TmnxBsxTransitIpPolicyIdOrZero=TmnxBsxTransitIpPolicyIdOrZero, TmnxSvcOperGrpCreationOrigin=TmnxSvcOperGrpCreationOrigin, TmnxMobChargingLevel=TmnxMobChargingLevel, TmnxPppNcpProtocol=TmnxPppNcpProtocol, TmnxSubProfileString=TmnxSubProfileString, TIngHsmdaPerPacketOffsetOvr=TIngHsmdaPerPacketOffsetOvr, THsmdaWrrWeight=THsmdaWrrWeight, TmnxMldGroupType=TmnxMldGroupType, THSMDAQueueBurstLimit=THSMDAQueueBurstLimit, TCIRPercentOverride=TCIRPercentOverride, TmnxSubIdentStringOrEmpty=TmnxSubIdentStringOrEmpty, TTcpUdpPort=TTcpUdpPort, TQGroupType=TQGroupType, TFCNameOrEmpty=TFCNameOrEmpty, TItemLongDescription=TItemLongDescription, TMplsLspExpProfMapID=TMplsLspExpProfMapID, TmnxAppProfileString=TmnxAppProfileString, TmnxAccessLoopEncapDataLink=TmnxAccessLoopEncapDataLink, TmnxSubMgtOrgString=TmnxSubMgtOrgString, TmnxMobApn=TmnxMobApn, TmnxVdoGrpId=TmnxVdoGrpId, TItemScope=TItemScope, TIpOption=TIpOption, TmnxSpokeSdpId=TmnxSpokeSdpId, TPlcyQuanta=TPlcyQuanta, THsmdaPolicyIncludeQueues=THsmdaPolicyIncludeQueues, TmnxMobSdfRuleName=TmnxMobSdfRuleName, TMacFilterType=TMacFilterType, TmnxMobBearerId=TmnxMobBearerId, TIngressQueueId=TIngressQueueId, TmnxFilterProfileStringOrEmpty=TmnxFilterProfileStringOrEmpty, TIngressHsmdaCounterIdOrZero=TIngressHsmdaCounterIdOrZero, TmnxPppoeUserNameOrEmpty=TmnxPppoeUserNameOrEmpty, TmnxBsxTransPrefPolicyId=TmnxBsxTransPrefPolicyId, Dot1PPriority=Dot1PPriority, ServiceOperStatus=ServiceOperStatus, TSubHostId=TSubHostId, TmnxEnabledDisabledOrInherit=TmnxEnabledDisabledOrInherit, TDSCPValue=TDSCPValue, THsmdaCounterIdOrZero=THsmdaCounterIdOrZero, TmnxMobUeSubType=TmnxMobUeSubType, TmnxPppoeUserName=TmnxPppoeUserName, TmnxStatus=TmnxStatus, TmnxMobLiTargetType=TmnxMobLiTargetType, TmnxTunnelGroupIdOrZero=TmnxTunnelGroupIdOrZero, TmnxMobAddrScheme=TmnxMobAddrScheme, TmnxMplsTpTunnelType=TmnxMplsTpTunnelType, TmnxMobSdf=TmnxMobSdf, TFrameType=TFrameType, TLevel=TLevel, TQueueMode=TQueueMode, TIngressMeterId=TIngressMeterId, TmnxMulticastAddrFamily=TmnxMulticastAddrFamily, TmnxAccPlcyAACounters=TmnxAccPlcyAACounters, TmnxMobLiTarget=TmnxMobLiTarget, TExpSecondaryShaperClassRate=TExpSecondaryShaperClassRate, TmnxMobProfPolChargingMethod=TmnxMobProfPolChargingMethod, TProfileUseDEOrNone=TProfileUseDEOrNone, THsmdaCIRKRate=THsmdaCIRKRate, ServiceAccessPoint=ServiceAccessPoint, TmnxSubRadServAlgorithm=TmnxSubRadServAlgorithm, TPrecValueOrNone=TPrecValueOrNone, TmnxVRtrID=TmnxVRtrID, TBurstHundredthsOfPercent=TBurstHundredthsOfPercent, TDEValue=TDEValue, TmnxPortID=TmnxPortID, TmnxBsxAarpId=TmnxBsxAarpId, InterfaceIndex=InterfaceIndex, TDSCPNameOrEmpty=TDSCPNameOrEmpty, TmnxDefInterDestIdSource=TmnxDefInterDestIdSource, TTcpUdpPortOperator=TTcpUdpPortOperator, THsmdaWeightClass=THsmdaWeightClass, TmnxMobDiaPeerHost=TmnxMobDiaPeerHost, TmnxVdoGrpIdOrInherit=TmnxVdoGrpIdOrInherit, TEgressHsmdaPerPacketOffset=TEgressHsmdaPerPacketOffset, TmnxPwPathHopIdOrZero=TmnxPwPathHopIdOrZero, TmnxMobServRefPointType=TmnxMobServRefPointType)
