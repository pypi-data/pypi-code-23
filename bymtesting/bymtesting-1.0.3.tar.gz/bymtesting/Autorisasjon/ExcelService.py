from bymtesting.Lib.Api import Api
import xlrd


class ExcelService:

    def __init__(self, filename):
        self.filename = filename

    def parse(self):
        d = {}
        wb = xlrd.open_workbook(self.filename)
        sh = wb.sheet_by_index(0)
        for i in range(sh.ncols):
            # forventer roller på rad nr 1 dvs. rad nr 2 i excell
            # todo finne bedre måte å gjøre det på
            rowWithRoles = 1
            rolle = str(sh.cell(rowWithRoles, i).value)
            if not (rolle == ''):
                list = []
                for row in range(sh.nrows):
                    apiEndpoint = sh.cell(row, 0).value
                    if not (apiEndpoint == ''):
                        apiClasse = Api(
                            apiEndpoint.lower(), self.mapResult(sh.cell(row, i).value))
                        list.append(apiClasse)
                d[rolle] = list

        return d

    def mapResult(self, statusCode):
        if('x' in statusCode.lower()):
            return 1
        else:
            return 0
