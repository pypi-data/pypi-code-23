INFO_SEPARATOR = '|'

VARIANT_GRID_ID = 'VARIANT_GRID_ID'
VARIANTCLASSIFICATION_ID = "VARIANTCLASSIFICATION_ID" 
VARIANTCLASSIFICATION_ZYGOSITY = "VARIANTCLASSIFICATION_ZYGOSITY"
VARIANTCLASSIFICATION_GROUP = "VARIANTCLASSIFICATION_GROUP"
CLASSIFICATION = "CLASSIFICATION"

MULTIPLES = " multiple values joined with a %s" % INFO_SEPARATOR

VARIANT_GRID_INFO_DICT = {VARIANT_GRID_ID : {'number' : 1,
                                             'type' : 'Integer',
                                             'description' : 'VariantGrid primary column',},
                          VARIANTCLASSIFICATION_ID : {'number' : 1,
                                                      'type' : 'String',
                                                      'description' : 'Unique Classification ID' + MULTIPLES,},
                          VARIANTCLASSIFICATION_ZYGOSITY : {'number' : 1,
                                                            'type' : 'String',
                                                            'description' : 'Sample Zygosity of classification (E=HET, O=HOM)' + MULTIPLES,},
                          VARIANTCLASSIFICATION_GROUP : {'number' : 1,
                                                         'type' : 'String',
                                                         'description' : 'Group performing classification' + MULTIPLES,},
                          CLASSIFICATION : {'number' : 1,
                                            'type' : 'String',
                                            'description' : 'Pathogenicity according to ACMG guidelines. 1-Benign, 2-Likely Benign, 3-VUS, 4-Likely Pathogenic, 5-Pathogenic' + MULTIPLES,},}
