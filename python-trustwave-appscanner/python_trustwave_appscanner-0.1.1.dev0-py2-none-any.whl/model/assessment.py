from collections import UserList

from lxml import etree


class Assessment:
    def __init__(self, assessment_id, assessment_name, is_api_safe, url,
                 application_id):
        self.AssessmentId = assessment_id
        self.AssessmentName = assessment_name
        self.IsApiSafe = is_api_safe
        self.Url = url
        self.ApplicationId = application_id

    @staticmethod
    def from_etree(xml_etree):
        assert isinstance(xml_etree, etree._Element)

        assessment_id = xml_etree.find('AssessmentId').text
        assessment_name = xml_etree.find('AssessmentName').text
        is_api_safe = bool(xml_etree.find('IsApiSafe').text)
        url = xml_etree.find('Url').text
        application_id = xml_etree.find('ApplicationId').text

        return Assessment(assessment_id, assessment_name, is_api_safe, url,
                          application_id)


class Assessments(UserList):
    @staticmethod
    def from_etree(xml_etree):
        assert isinstance(xml_etree, etree._Element)
        assert xml_etree.tag == 'Assessments'

        assessments = [Assessment.from_etree(assessment) for assessment in xml_etree.findall('Assessment')]

        return Assessments(assessments)