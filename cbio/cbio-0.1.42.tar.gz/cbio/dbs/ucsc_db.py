import pymysql
import cbio


class connect_ucsc():
    def __init__(self):
        """
        Function to establish connection with UCSC server.

        Parameters
        ----------
        None

        Returns
        -------
        cur : cursor
            Connection to the database

        """

        self.db = 'hg19'

        user_data = {
            'hostname' : 'genome-mysql.cse.ucsc.edu',
            'username' : 'genome',
            'password' : '',
            'database' : 'hg19',
        }

        # Create the connection
        conn = pymysql.connect( host = user_data['hostname'],
                                user = user_data['username'],
                                passwd = user_data['password'],
                                db = user_data['database'] )

        cur = conn.cursor()
        self.cur = cur
        return None

    # Simple routine to run a query on a database and print the results:
    def execute_query(self, query):
        """
        Execute query against the database

        Parameters
        ----------
        query : str
            String with the query to execute

        Returns
        -------
        data : tuple
            Data recovered from the database

        """

        if query == "" or query is None:
            raise Exception("Query is empty")

        self.cur.execute(query)

        data = self.cur.fetchall()

        return data

    def queryStructureByNm(self, inputs, remove_utr=False):
        """
        Get the information of the regions of a NM

        Parameters
        ----------
        remove_utr : boolean
            Boolean to activate or not the removal of the UTRs

        Returns
        -------
        data : list
            List that contains all the regions (chr, start, end, gene, nm)
        """

        # If getting nms from file, parse it
        if type(inputs) == str:
            nm_list = cbio.utils.parse_nms_fromfile(inputs)
        # Else, just use the provided list
        else:
            nm_list = inputs

        chroms = ['chr' + str(i) for i in range(1, 23)] + ['chrX', 'chrY']

        query = "select * from refGene where name IN (\"" +\
            ("\",\"").join(nm_list) + "\") AND chrom IN (\"" +\
            ("\",\"").join(chroms) + "\")"

        data = self.execute_query(query)
        print(data)

        if remove_utr is True:
            data, nm_recovered = self._remove_utrs(data)

            not_found_nms = list(set(nm_list) - set(nm_recovered))
            if len(not_found_nms) > 0:
                print("#[ERR]: " + str(len(not_found_nms)) +\
                        " NMs not found in refseq -> " + str(not_found_nms))


        return data


    def queryFullRefseq(self, remove_utr=False):
        """
        Get the information of the regions of a NM

        Parameters
        ----------
        remove_utr : boolean
            Boolean to activate or not the removal of the UTRs

        Returns
        -------
        data : list
            List that contains all the regions (chr, start, end, gene, nm)
        """

        chroms = ['chr' + str(i) for i in range(1, 23)] + ['chrX', 'chrY']

        query = "select * from refGene"

        data = self.execute_query(query)

        if remove_utr is True:
            data, nm_recovered = self._remove_utrs(data)

        return data


    def _remove_utrs(self, data):
        """
        Remove UTRs from the regions

        Parameters
        ----------
        data : tuple
            Tuple with the information of all the regions

        Returns
        -------
        regions : list
            List that contains all the regions (chr, start, end, gene, nm)
        nm_list : list
            List of NMs that have been recovered

        """

        regions = []
        nm_list = []
        c = 0

        for line in data:

            nm_list.append(line[1])

            # Get the start and end of the exons in two lists
            exons_start = line[9].decode('UTF-8').split(',')[0:-1]
            exons_end = line[10].decode('UTF-8').split(',')[0:-1]

            # Get the coding start and the coding end of the transcript
            cdsStart, cdsEnd = int(line[6]), int(line[7])

            if cdsStart == cdsEnd:
                cdsStart = int(line[4])
                cdsEnd = int(line[5])

            for start, end in zip(exons_start, exons_end):
                start = int(start)
                end = int(end)
                region = list(line)

                region[2] = region[2].strip("chr")

                # Regions that are 5UTR or 3UTR
                if start < cdsStart and end < cdsStart:
                    continue
                if start > cdsEnd and end > cdsEnd:
                    continue

                # Regions of just one gene
                if start <= cdsStart and end >= cdsEnd:
                    region[9] = cdsStart
                    region[10] = cdsEnd
                    regions.append([str(region[2]), str(region[9]), str(region[10]),
                                    str(region[12]), str(region[1])])
                    continue

                # Cutting in 5'
                if start <= cdsStart and end >= cdsStart:
                    region[9] = cdsStart
                    region[10] = end
                    regions.append([str(region[2]), str(region[9]), str(region[10]),
                                    str(region[12]), str(region[1])])
                    continue

                # Cutting in 3'
                if start < cdsEnd and end > cdsEnd:
                    region[9] = start
                    region[10] = cdsEnd
                    regions.append([str(region[2]), str(region[9]), str(region[10]),
                                    str(region[12]), str(region[1])])
                    continue

                # Normal Exon
                if start > cdsStart and end < cdsEnd:
                    region[9] = start
                    region[10] = end
                    regions.append([str(region[2]), str(region[9]), str(region[10]),
                                    str(region[12]), str(region[1])])
                    continue

            c += 1

        print("#[LOG]: Extracted " + str(c) + " NMs")
        return regions, nm_list
