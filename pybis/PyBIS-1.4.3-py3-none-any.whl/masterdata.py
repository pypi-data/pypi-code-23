class Vocabulary():

    def __init__(self, data):
        self.data = data

    @property
    def terms_kv(self):
         return [ 
            {voc["code"]:voc["label"] }
            for voc 
            in sorted(self.data['objects'], key=lambda v: v["ordinal"]) 
        ]

    @property
    def terms(self):
         return [ 
            voc["code"]
            for voc 
            in sorted(self.data['objects'], key=lambda v: v["ordinal"]) 
        ]


    def _repr_html_(self):
        html = """
            <table border="1" class="dataframe">
            <thead>
                <tr style="text-align: right;">
                <th>vocabulary term</th>
                <th>label</th>
                <th>description</th>
                <th>vocabulary</th>
                </tr>
            </thead>
            <tbody>
        """

        for voc in sorted(
            self.data['objects'], 
            key=lambda v: (v["permId"]["vocabularyCode"], v["ordinal"])
        ):

            html += "<tr> <td>{}</td> <td>{}</td> <td>{}</td> <td>{}</td> </tr>".format(
                voc['code'],
                voc['label'],
                voc['description'],
                voc['permId']['vocabularyCode']
            )

        html += """
            </tbody>
            </table>
        """
        return html

