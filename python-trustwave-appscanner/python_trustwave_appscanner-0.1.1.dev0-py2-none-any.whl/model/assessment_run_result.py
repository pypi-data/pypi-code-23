from datetime import datetime
from collections import UserList

from lxml import etree


class SmartAttackInfo:
    def __init__(self, PolicyId, PolicyVersion, CenzicId, Severity,
                 VulnerabilityIds, SmartAttackName, Description,
                 TechnicalDescription, HowItWorks, Impact, Remediation):
        self.PolicyId = PolicyId
        self.PolicyVersion = PolicyVersion
        self.CenzicId = CenzicId
        self.Severity = Severity
        self.VulnerabilityIds = VulnerabilityIds
        self.SmartAttackName = SmartAttackName
        self.Description = Description
        self.TechnicalDescription = TechnicalDescription
        self.HowItWorks = HowItWorks
        self.Impact = Impact
        self.Remediation = Remediation

    @staticmethod
    def from_etree(xml_etree):
        assert isinstance(xml_etree, etree._Element)

        PolicyId = xml_etree.attrib.get('PolicyId')
        PolicyVersion = xml_etree.attrib.get('PolicyVersion')
        CenzicId = xml_etree.attrib.get('CenzicId')
        Severity = xml_etree.attrib.get('Severity')
        VulnerabilityIds = xml_etree.attrib.get('VulnerabilityIds')
        SmartAttackName = xml_etree.find('SmartAttackName').text.strip()
        Description = xml_etree.find('Description').text.strip()
        TechnicalDescription = xml_etree.find('TechnicalDescription').text.strip()
        HowItWorks = xml_etree.find('HowItWorks').text.strip()
        Impact = xml_etree.find('Impact').text.strip()
        Remediation = xml_etree.find('Remediation').text.strip()

        return SmartAttackInfo(PolicyId, PolicyVersion, CenzicId, Severity,
                               VulnerabilityIds, SmartAttackName, Description,
                               TechnicalDescription, HowItWorks, Impact,
                               Remediation)


class ReportItem:
    def __init__(self, Id, ReportItemType, ReportItemCreateDate, Severity,
                 HarmScore, CVSSBaseScore, ComputedHarmScore, Count,
                 Message, GlobalizedMessage, Url, TraversalName,
                 Filtered, HttpRequest, HttpResponse, StructuredData):

        self.Id = Id
        self.ReportItemType = ReportItemType
        self.ReportItemCreateDate = ReportItemCreateDate
        self.Severity = Severity
        self.HarmScore = HarmScore
        self.CVSSBaseScore = CVSSBaseScore
        self.ComputedHarmScore = ComputedHarmScore
        self.Count = Count
        self.Message = Message
        self.GlobalizedMessage = GlobalizedMessage
        self.Url = Url
        self.TraversalName = TraversalName
        self.Filtered = Filtered
        self.HttpRequest = HttpRequest
        self.HttpResponse = HttpResponse
        self.StructuredData = StructuredData

    @staticmethod
    def from_etree(xml_etree):
        assert isinstance(xml_etree, etree._Element)

        Id = xml_etree.attrib['Id']
        ReportItemType = xml_etree.find('ReportItemType').text.strip()
        ReportItemCreateDate = datetime.strptime(
            xml_etree.find('ReportItemCreateDate').text.strip(),
            "%m/%d/%Y %I:%M:%S %p")
        Severity = xml_etree.find('Severity').text.strip()
        HarmScore = int(xml_etree.find('HarmScore').text.strip())
        CVSSBaseScore = xml_etree.find('CVSSBaseScore').text
        ComputedHarmScore = int(xml_etree.find('ComputedHarmScore').text.strip())
        Count = int(xml_etree.find('Count').text.strip())
        Message = xml_etree.find('Message').text.strip()
        GlobalizedMessage = xml_etree.find('GlobalizedMessage').text.strip()
        Url = xml_etree.find('Url').text
        TraversalName = xml_etree.find('TraversalName').text.strip()
        Filtered = int(xml_etree.find('Filtered').text.strip())
        HttpRequest = xml_etree.find('HttpRequest').text
        HttpResponse = xml_etree.find('HttpResponse').text
        StructuredData = xml_etree.find('StructuredData').text

        return ReportItem(Id, ReportItemType, ReportItemCreateDate, Severity,
                          HarmScore, CVSSBaseScore, ComputedHarmScore, Count,
                          Message, GlobalizedMessage, Url, TraversalName,
                          Filtered, HttpRequest, HttpResponse, StructuredData)


class Category:
    def __init__(self, Name):
        self.Name = Name

    @staticmethod
    def from_etree(xml_etree):
        assert isinstance(xml_etree, etree._Element)

        Name = xml_etree.find('Name').text

        return Category(Name)


class Categories(UserList):
    @staticmethod
    def from_etree(xml_etree):
        assert isinstance(xml_etree, etree._Element)
        assert xml_etree.tag == 'Categories'

        categories = [Category(category) for category in xml_etree.findall('Category')]

        return Categories(categories)


class PagesVisited(UserList):
    @staticmethod
    def from_etree(xml_etree):
        assert isinstance(xml_etree, etree._Element)
        assert xml_etree.tag == 'PagesVisited'

        Urls = [url.text for url in xml_etree.findall('Url')]

        return PagesVisited(Urls)


class ReportItems(UserList):
    @staticmethod
    def from_etree(xml_etree):
        assert isinstance(xml_etree, etree._Element)
        assert xml_etree.tag == 'ReportItems'

        report_items = [ReportItem.from_etree(item) for item in xml_etree.findall('ReportItem')]

        return ReportItems(report_items)


class SmartAttacksData:
    def __init__(self, smart_attack_info, report_items, categories):
        self.SmartAttackInfo = smart_attack_info
        self.ReportItems = report_items
        self.Categories = categories

    @staticmethod
    def from_etree(xml_etree):
        assert isinstance(xml_etree, etree._Element)
        assert xml_etree.tag == 'SmartAttacksData'

        smart_attack_info = SmartAttackInfo.from_etree(
            xml_etree.find('Assessment'))
        report_items = ReportItems.from_etree(
            xml_etree.find('ReportItems'))
        categories = Categories(xml_etree.find('Categories'))

        return SmartAttacksData(smart_attack_info, report_items,
                                categories)


class SmartAttacks(UserList):
    @staticmethod
    def from_etree(xml_etree):
        assert isinstance(xml_etree, etree._Element)
        assert xml_etree.tag == 'SmartAttacks'

        smart_attacks = [SmartAttacksData.from_etree(item) for item in xml_etree.findall('SmartAttacksData')]

        return SmartAttacks(smart_attacks)


class AssessmentRunInfo:
    def __init__(self, HarmScore, RiskFactor, Status, AttackCount,
                 MaxPagesVisited, StartTime, EndTime):
        self.HarmScore = HarmScore
        self.RiskFactor = RiskFactor
        self.Status = Status
        self.AttackCount = AttackCount
        self.MaxPagesVisited = MaxPagesVisited
        self.StartTime = StartTime
        self.EndTime = EndTime

    @staticmethod
    def from_etree(xml_etree):
        assert isinstance(xml_etree, etree._Element)

        HarmScore = int(xml_etree.find('HarmScore').text.strip())
        RiskFactor = int(xml_etree.find('RiskFactor').text.strip())
        Status = xml_etree.find('Status').text.strip()
        AttackCount = int(xml_etree.find('AttackCount').text.strip())
        MaxPagesVisited = int(xml_etree.find('MaxPagesVisited').text.strip())
        StartTime = datetime.strptime(xml_etree.find('StartTime').text.strip(),
                                      '%m/%d/%Y %H:%M:%S')
        EndTime = datetime.strptime(xml_etree.find('EndTime').text.strip(),
                                    '%m/%d/%Y %H:%M:%S')

        return AssessmentRunInfo(HarmScore, RiskFactor, Status, AttackCount,
                                 MaxPagesVisited, StartTime, EndTime)


class AssessmentRunData:
    def __init__(self, request_id, assessment_run_id, assessment_name,
                 application_name, application_id, application_url,
                 assessment_run_info, smart_attacks, pages_visited):
        self.RequestId = request_id
        self.AssessmentRunId = assessment_run_id
        self.AssessmentName = assessment_name
        self.ApplicationName = application_name
        self.ApplicationId = application_id
        self.ApplicationUrl = application_url
        self.AssessmentRunInfo = assessment_run_info
        self.SmartAttacks = smart_attacks
        self.PagesVisited = pages_visited

    @staticmethod
    def from_etree(xml_etree):
        assert isinstance(xml_etree, etree._Element)

        request_id = xml_etree.attrib['RequestId']
        assessment_run_id = xml_etree.attrib['AssessmentRunId']
        assessment_name = xml_etree.attrib['AssessmentName']
        application_name = xml_etree.attrib['ApplicationName']
        application_id = xml_etree.attrib['ApplicationId']
        application_url = xml_etree.attrib['ApplicationUrl']

        assessment_run_info = AssessmentRunInfo.from_etree(xml_etree.find('AssessmentRunInfo'))
        smart_attacks = SmartAttacks.from_etree(xml_etree.find('SmartAttacks'))
        pages_visited = PagesVisited.from_etree(xml_etree.find('PagesVisited'))

        return AssessmentRunData(request_id, assessment_run_id, assessment_name,
                                 application_name, application_id,
                                 application_url, assessment_run_info,
                                 smart_attacks, pages_visited)