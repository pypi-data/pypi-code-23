import json
from collections import defaultdict

class StatusField(object):
    """
    some alias.
    """
    failed = "failed"
    succeed = "succeed"
    status = "status"
    getNothingDefaultValue = "-999999"


class Result(object):
    """
    Result that store result and some info about it.
    """

    def __init__(self, result, status, message=None):
        self.result = result
        self.status = status
        self.message = message


class InfoParser(object):
    """
    you can code different Parser for one Result.
    """

    @staticmethod
    def PaymentInfoParser(paymentInfoList_Result):
        previous_result = paymentInfoList_Result.result
        previous_status = paymentInfoList_Result.status

        if previous_status == StatusField.failed:
            return Result({}, previous_status)

        return_value = {
            "monthOfPayment": len(previous_result),
        }
        return Result(return_value, StatusField.succeed)

    @staticmethod
    def BillInfoParser(billInfoList_Result):
        previous_result = billInfoList_Result.result
        previous_status = billInfoList_Result.status

        if previous_status == StatusField.failed:
            return Result({}, previous_status)

        return_value = {
            "monthOfBill": str(len(previous_result)),
        }
        return Result(return_value, StatusField.succeed)

    @staticmethod
    def AccountInfoParser(AccountInfo_Result):
        previous_result = AccountInfo_Result.result
        previous_status = AccountInfo_Result.status

        if previous_status == StatusField.failed:
            return Result({}, previous_status)

        return_value = {
            "net_age": previous_result.get("net_age", StatusField.getNothingDefaultValue)
        }
        return Result(return_value, StatusField.succeed)

    @staticmethod
    def CallInfoParser(CallInfoList_Result):
        previous_result = CallInfoList_Result.result
        previous_status = CallInfoList_Result.status

        if previous_status == StatusField.failed:
            return Result({}, previous_status)

        call_count_dict = {}
        for call_detail_monthly in previous_result:
            call_cycle = call_detail_monthly.get("call_cycle")
            if call_cycle is None:
                continue
            call_count_dict[call_cycle] = {
                "callsMonthly": call_detail_monthly.get("total_call_count", StatusField.getNothingDefaultValue),
                "callsTimeMonthly": call_detail_monthly.get("total_call_time", StatusField.getNothingDefaultValue),
            }

        return_value = call_count_dict
        return Result(return_value, StatusField.succeed)

    @staticmethod
    def OtherNodesAndRelationshipsFromCallInfoParser(CallInfoList_Result):
        previous_result = CallInfoList_Result.result
        previous_status = CallInfoList_Result.status

        if previous_status == StatusField.failed:
            return Result({}, previous_status)

        # calling dict called dict othernodes set
        calling_relationships_dict = defaultdict(list)
        called_relationships_dict = defaultdict(list)
        OtherNumbersSetCollector = set()
        for call_records_monthly in previous_result:
            each_call_records = call_records_monthly.get("call_record", [])
            for record in each_call_records:
                otherNumber = record.get("call_other_number", "UNKONWN")
                if (otherNumber is None) or (otherNumber == "UNKONWN"):
                    continue
                OtherNumbersSetCollector.add(otherNumber)

                call_type_name = record.get("call_type_name", "UNKONWN")
                one_relationships_dict = {
                    "call_address": record.get("call_address", "UNKONWN"),
                    "call_land_type": record.get("call_land_type", "UNKONWN"),
                    "call_start_time": record.get("call_start_time", "UNKONWN"),
                    "call_time": record.get("call_time", "UNKONWN"),
                }
                if call_type_name == "calling":
                    calling_relationships_dict[otherNumber].append(one_relationships_dict)
                if call_type_name == "called":
                    called_relationships_dict[otherNumber].append(one_relationships_dict)
        return_value = (calling_relationships_dict, called_relationships_dict, OtherNumbersSetCollector)
        return Result(return_value, StatusField.succeed)


class GetInfoFromCalldetail(object):
    """
    the class consists of call_detail_str json_obejct from which some inner objects are created.
    """

    def __init__(self, call_detail_str):
        """
        form dictStructure by nested objects.
        items of different levels shouldn't have same name.
        items have buffers for not get repeatedly.
        """

        # top_level should be in the front of structureList
        structureList = [
            ("user_mobile", str, None),
            ("real_name", str, None),
            ("channel_attr", str, None),
            ("channel_src", str, None),
            ("task_data", dict, None),
            ("bill_info", list, "task_data"),
            ("account_info", list, "task_data"),
            ("payment_info", list, "task_data"),
            ("call_info", list, "task_data")
        ]

        def inner_get(self, defaultValue=StatusField.getNothingDefaultValue):
            try:
                if self.context is not None:
                    return self.context
                return self.holder.get(self)
            except Exception as e:
                return Result(defaultValue, StatusField.failed)
                print(e)

        for name_str, type_class, pLevel_str in structureList:
            setattr(self, name_str, type(
                name_str,
                (object,),
                {
                    "name": name_str,
                    "type": type_class,
                    "pLevel": None if pLevel_str is None else getattr(self, pLevel_str),
                    "context": None,
                    "get": inner_get,
                    "holder": self,
                })()
                    )

        self.call_detail_dict = json.loads(call_detail_str)
        self.getNothingDefaultValue = StatusField.getNothingDefaultValue
        self.MainNode = None
        self.OtherNodesAndRelations = None

    def get(self, innerClassInstance=None):
        result = self.call_detail_dict

        if innerClassInstance is None:
            return result
        if innerClassInstance.context is not None:
            print("cached")
            return innerClassInstance.context

        get_list = [innerClassInstance.name, ]
        classIterator = innerClassInstance
        while (classIterator.pLevel is not None):
            classIterator = innerClassInstance.pLevel
            get_list.insert(0, classIterator.name)
        for name in get_list:
            try:
                result = result.get(name, self.getNothingDefaultValue)
            except Exception as e:
                finalResult = Result(result, StatusField.failed, (get_list, e))
                innerClassInstance.context = finalResult
                return finalResult
        finalResult = Result(result, StatusField.succeed)
        innerClassInstance.context = finalResult
        return finalResult

    def getMainNode(self):
        # InfoBuffer
        if self.MainNode is not None:
            print("cached")
            return self.MainNode
        result = {}
        try:
            get_list = [
                self.user_mobile, self.real_name, self.channel_attr, self.channel_src,
            ]
            for getItem in get_list:
                getResult = self.get(getItem)
                item_result = getResult.result
                item_status = getResult.status
                result[getItem.name] = item_result

            get_parser_list = [
                self.payment_info, self.bill_info, self.account_info, self.call_info,
            ]
            parser_list = [
                InfoParser.PaymentInfoParser,
                InfoParser.BillInfoParser,
                InfoParser.AccountInfoParser,
                InfoParser.CallInfoParser,

            ]
            for getParseItem, parserItem in zip(get_parser_list, parser_list):
                getResult = parserItem(self.get(getParseItem))
                item_result = getResult.result
                item_status = getResult.status
                result[getParseItem.name] = item_result

        except Exception as e:
            raise e

        finally:
            self.MainNode = result

        return result

    def getOtherNodesAndRelations(self):
        # InfoBuffer
        if self.OtherNodesAndRelations is not None:
            print("cached")
            return self.OtherNodesAndRelations
        try:
            get_parsed = self.call_info
            parser = InfoParser.OtherNodesAndRelationshipsFromCallInfoParser
            getResult = parser(self.get(get_parsed))
            result = getResult.result
            status = getResult.status
        except Exception as e:
            raise e
        finally:
            self.OtherNodesAndRelations = result

        return result

    def getOtherNodes(self):
        pass

    def getRelations(self):
        pass