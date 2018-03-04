#
# PySNMP MIB module ATM-TC-MIB (http://pysnmp.sf.net)
# ASN.1 source file://C:\MIBS\text_mibs\ATM-TC-MIB
# Produced by pysmi-0.0.6 at Wed May 31 13:17:40 2017
# On host ? platform ? version ? by user ?
# Using Python version 2.7.9 (default, Dec 10 2014, 12:24:55) [MSC v.1500 32 bit (Intel)]
#
( Integer, ObjectIdentifier, OctetString, ) = mibBuilder.importSymbols("ASN1", "Integer", "ObjectIdentifier", "OctetString")
( NamedValues, ) = mibBuilder.importSymbols("ASN1-ENUMERATION", "NamedValues")
( ConstraintsUnion, SingleValueConstraint, ConstraintsIntersection, ValueSizeConstraint, ValueRangeConstraint, ) = mibBuilder.importSymbols("ASN1-REFINEMENT", "ConstraintsUnion", "SingleValueConstraint", "ConstraintsIntersection", "ValueSizeConstraint", "ValueRangeConstraint")
( NotificationGroup, ModuleCompliance, ) = mibBuilder.importSymbols("SNMPv2-CONF", "NotificationGroup", "ModuleCompliance")
( Integer32, MibScalar, MibTable, MibTableRow, MibTableColumn, NotificationType, MibIdentifier, mib_2, IpAddress, TimeTicks, Counter64, Unsigned32, iso, Gauge32, ModuleIdentity, ObjectIdentity, Bits, Counter32, ) = mibBuilder.importSymbols("SNMPv2-SMI", "Integer32", "MibScalar", "MibTable", "MibTableRow", "MibTableColumn", "NotificationType", "MibIdentifier", "mib-2", "IpAddress", "TimeTicks", "Counter64", "Unsigned32", "iso", "Gauge32", "ModuleIdentity", "ObjectIdentity", "Bits", "Counter32")
( DisplayString, TextualConvention, ) = mibBuilder.importSymbols("SNMPv2-TC", "DisplayString", "TextualConvention")
atmTCMIB = ModuleIdentity((1, 3, 6, 1, 2, 1, 37, 3))
class AtmAddr(OctetString, TextualConvention):
    displayHint = '1x'
    subtypeSpec = OctetString.subtypeSpec+ValueSizeConstraint(0,40)

class AtmConnCastType(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2, 3,)
    namedValues = NamedValues(("p2p", 1), ("p2mpRoot", 2), ("p2mpLeaf", 3),)

class AtmConnKind(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2, 3, 4, 5,)
    namedValues = NamedValues(("pvc", 1), ("svcIncoming", 2), ("svcOutgoing", 3), ("spvcInitiator", 4), ("spvcTarget", 5),)

class AtmIlmiNetworkPrefix(OctetString, TextualConvention):
    subtypeSpec = OctetString.subtypeSpec+ConstraintsUnion(ValueSizeConstraint(8,8),ValueSizeConstraint(13,13),)
class AtmInterfaceType(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13,)
    namedValues = NamedValues(("other", 1), ("autoConfig", 2), ("ituDss2", 3), ("atmfUni3Dot0", 4), ("atmfUni3Dot1", 5), ("atmfUni4Dot0", 6), ("atmfIispUni3Dot0", 7), ("atmfIispUni3Dot1", 8), ("atmfIispUni4Dot0", 9), ("atmfPnni1Dot0", 10), ("atmfBici2Dot0", 11), ("atmfUniPvcOnly", 12), ("atmfNniPvcOnly", 13),)

class AtmServiceCategory(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2, 3, 4, 5, 6,)
    namedValues = NamedValues(("other", 1), ("cbr", 2), ("rtVbr", 3), ("nrtVbr", 4), ("abr", 5), ("ubr", 6),)

class AtmSigDescrParamIndex(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ValueRangeConstraint(0,2147483647)

class AtmTrafficDescrParamIndex(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ValueRangeConstraint(0,2147483647)

class AtmVcIdentifier(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ValueRangeConstraint(0,65535)

class AtmVpIdentifier(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+ValueRangeConstraint(0,4095)

class AtmVorXAdminStatus(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2,)
    namedValues = NamedValues(("up", 1), ("down", 2),)

class AtmVorXLastChange(TimeTicks, TextualConvention):
    pass

class AtmVorXOperStatus(Integer32, TextualConvention):
    subtypeSpec = Integer32.subtypeSpec+SingleValueConstraint(1, 2, 3,)
    namedValues = NamedValues(("up", 1), ("down", 2), ("unknown", 3),)

atmTrafficDescriptorTypes = MibIdentifier((1, 3, 6, 1, 2, 1, 37, 1, 1))
atmObjectIdentities = MibIdentifier((1, 3, 6, 1, 2, 1, 37, 3, 1))
atmNoTrafficDescriptor = ObjectIdentity((1, 3, 6, 1, 2, 1, 37, 1, 1, 1))
atmNoClpNoScr = ObjectIdentity((1, 3, 6, 1, 2, 1, 37, 1, 1, 2))
atmClpNoTaggingNoScr = ObjectIdentity((1, 3, 6, 1, 2, 1, 37, 1, 1, 3))
atmClpTaggingNoScr = ObjectIdentity((1, 3, 6, 1, 2, 1, 37, 1, 1, 4))
atmNoClpScr = ObjectIdentity((1, 3, 6, 1, 2, 1, 37, 1, 1, 5))
atmClpNoTaggingScr = ObjectIdentity((1, 3, 6, 1, 2, 1, 37, 1, 1, 6))
atmClpTaggingScr = ObjectIdentity((1, 3, 6, 1, 2, 1, 37, 1, 1, 7))
atmClpNoTaggingMcr = ObjectIdentity((1, 3, 6, 1, 2, 1, 37, 1, 1, 8))
atmClpTransparentNoScr = ObjectIdentity((1, 3, 6, 1, 2, 1, 37, 1, 1, 9))
atmClpTransparentScr = ObjectIdentity((1, 3, 6, 1, 2, 1, 37, 1, 1, 10))
atmNoClpTaggingNoScr = ObjectIdentity((1, 3, 6, 1, 2, 1, 37, 1, 1, 11))
atmNoClpNoScrCdvt = ObjectIdentity((1, 3, 6, 1, 2, 1, 37, 1, 1, 12))
atmNoClpScrCdvt = ObjectIdentity((1, 3, 6, 1, 2, 1, 37, 1, 1, 13))
atmClpNoTaggingScrCdvt = ObjectIdentity((1, 3, 6, 1, 2, 1, 37, 1, 1, 14))
atmClpTaggingScrCdvt = ObjectIdentity((1, 3, 6, 1, 2, 1, 37, 1, 1, 15))
mibBuilder.exportSymbols("ATM-TC-MIB", atmNoClpNoScr=atmNoClpNoScr, AtmConnCastType=AtmConnCastType, atmClpNoTaggingScr=atmClpNoTaggingScr, atmClpNoTaggingScrCdvt=atmClpNoTaggingScrCdvt, atmNoClpScrCdvt=atmNoClpScrCdvt, atmObjectIdentities=atmObjectIdentities, AtmServiceCategory=AtmServiceCategory, AtmVorXAdminStatus=AtmVorXAdminStatus, atmClpNoTaggingMcr=atmClpNoTaggingMcr, atmNoClpTaggingNoScr=atmNoClpTaggingNoScr, atmNoClpNoScrCdvt=atmNoClpNoScrCdvt, AtmVorXOperStatus=AtmVorXOperStatus, atmClpTransparentScr=atmClpTransparentScr, AtmAddr=AtmAddr, AtmVorXLastChange=AtmVorXLastChange, atmClpTaggingScr=atmClpTaggingScr, atmClpNoTaggingNoScr=atmClpNoTaggingNoScr, atmNoClpScr=atmNoClpScr, AtmVpIdentifier=AtmVpIdentifier, AtmInterfaceType=AtmInterfaceType, PYSNMP_MODULE_ID=atmTCMIB, AtmSigDescrParamIndex=AtmSigDescrParamIndex, atmClpTaggingScrCdvt=atmClpTaggingScrCdvt, AtmVcIdentifier=AtmVcIdentifier, AtmIlmiNetworkPrefix=AtmIlmiNetworkPrefix, AtmConnKind=AtmConnKind, atmNoTrafficDescriptor=atmNoTrafficDescriptor, atmTrafficDescriptorTypes=atmTrafficDescriptorTypes, atmTCMIB=atmTCMIB, atmClpTransparentNoScr=atmClpTransparentNoScr, atmClpTaggingNoScr=atmClpTaggingNoScr, AtmTrafficDescrParamIndex=AtmTrafficDescrParamIndex)
