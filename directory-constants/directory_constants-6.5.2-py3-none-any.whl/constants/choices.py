from directory_constants.constants import exred_articles, lead_generation, \
    sectors


SPECIFIC = 'specific'
OPEN_ENDED = 'open_ended'
DISTRIBUTION = 'distribution'
WHOLESALE = 'wholesale'
RETAIL = 'retail'
HOSPITALITY = 'hospitality'
CATERING = 'catering'
MANUFACTURING = 'manufacturing'

TYPE_OF_ENQUIRIES = (
    (SPECIFIC, 'Specific'),
    (OPEN_ENDED, 'Open-ended'),
)

FOOD_LEAD_GENERATION_BUSINESS_MODELS = (
    (DISTRIBUTION, 'Distribution'),
    (WHOLESALE, 'Wholesale'),
    (RETAIL, 'Retail'),
)

FOOD_LEAD_GENERATION_SECTORS = (
    (RETAIL, 'Retail'),
    (HOSPITALITY, 'Hospitality'),
    (CATERING, 'Catering'),
    (MANUFACTURING, 'Manufacturing'),
)

LEGAL_LEAD_GENERATION_SECTORS = (
    (sectors.TECHNOLOGY, 'Technology'),
    (sectors.FOOD_AND_DRINK, 'Food and drink'),
    (sectors.RETAIL_AND_LUXURY, 'Retail'),
    (
        sectors.FINANCIAL_AND_PROFESSIONAL_SERVICES,
        (
            'Professional services (for example, financial '
            'services or business consulting'
        )
    ),
    (sectors.MARINE, 'Marine'),
    (sectors.ENERGY, 'Energy'),
)

LEGAL_LEAD_GENERATION_NEED = (
    (
        'General-business-advice-and-partnership',
        'General business advice and partnership'
    ),
    ('Business-start-up-advice', 'Business start-up advice'),
    ('Drafting-of-contracts', 'Drafting of contracts'),
    ('Mergers-and-acquisitions', 'Mergers and acquisitions'),
    ('Immigration', 'Immigration'),
    ('Dispute-resolution', 'Dispute resolution'),
)

LEAD_GENERATION_EXPORT_DESTINATIONS = (
    ('CN', 'China'),
    ('DE', 'Germany'),
    ('IN', 'India'),
    ('JP', 'Japan'),
    ('US', 'United States'),
)

INDUSTRIES = (
    (sectors.AEROSPACE, 'Aerospace'),
    (sectors.ADVANCED_MANUFACTURING, 'Advanced manufacturing'),
    (sectors.AIRPORTS, 'Airports'),
    (
        sectors.AGRICULTURE_HORTICULTURE_AND_FISHERIES,
        'Agriculture, horticulture and fisheries'
    ),
    (sectors.AUTOMOTIVE, 'Automotive'),
    (
        sectors.BIOTECHNOLOGY_AND_PHARMACEUTICALS,
        'Biotechnology and pharmaceuticals'
    ),
    (
        sectors.BUSINESS_AND_CONSUMER_SERVICES,
        'Business and consumer services'
    ),
    (sectors.CHEMICALS, 'Chemicals'),
    (sectors.CLOTHING_FOOTWEAR_AND_FASHION, 'Clothing, footwear and fashion'),
    (sectors.COMMUNICATIONS, 'Communications'),
    (sectors.CONSTRUCTION, 'Construction'),
    (sectors.CREATIVE_AND_MEDIA, 'Creative and media'),
    (sectors.EDUCATION_AND_TRAINING, 'Education and training'),
    (sectors.ELECTRONICS_AND_IT_HARDWARE, 'Electronics and IT hardware'),
    (sectors.ENVIRONMENT, 'Environment'),
    (
        sectors.FINANCIAL_AND_PROFESSIONAL_SERVICES,
        'Financial and professional services'
    ),
    (sectors.FOOD_AND_DRINK, 'Food and drink'),
    (
        sectors.GIFTWARE_JEWELLERY_AND_TABLEWARE,
        'Giftware, jewellery and tableware'
    ),
    (sectors.GLOBAL_SPORTS_INFRASTRUCTURE, 'Global sports infrastructure'),
    (sectors.HEALTHCARE_AND_MEDICAL, 'Healthcare and medical'),
    (
        sectors.HOUSEHOLD_GOODS_FURNITURE_AND_FURNISHINGS,
        'Household goods, furniture and furnishings'
    ),
    (sectors.LIFE_SCIENCES, 'Life sciences'),
    (sectors.LEISURE_AND_TOURISM, 'Leisure and tourism'),
    (sectors.LEGAL_SERVICES, 'Legal services'),
    (sectors.MARINE, 'Marine'),
    (
        sectors.MECHANICAL_ELECTRICAL_AND_PROCESS_ENGINEERING,
        'Mechanical electrical and process engineering'
    ),
    (sectors.METALLURGICAL_PROCESS_PLANT, 'Metallurgical process plant'),
    (sectors.METALS_MINERALS_AND_MATERIALS, 'Metals, minerals and materials'),
    (sectors.MINING, 'Mining'),
    (sectors.OIL_AND_GAS, 'Oil and gas'),
    (sectors.PORTS_AND_LOGISTICS, 'Ports and logistics'),
    (sectors.POWER, 'Power'),
    (sectors.RAILWAYS, 'Railways'),
    (sectors.RENEWABLE_ENERGY, 'Renewable energy'),
    (sectors.RETAIL_AND_LUXURY, 'Retail and luxury'),
    (sectors.SECURITY, 'Security'),
    (sectors.SOFTWARE_AND_COMPUTER_SERVICES, 'Software and computer services'),
    (
        sectors.TEXTILES_INTERIOR_TEXTILES_AND_CARPETS,
        'Textiles, interior textiles and carpets'
    ),
    (sectors.WATER, 'Water'),
)

EMPLOYEES = (
    ('', 'Please select an option'),
    ('1-10', '1-10'),
    ('11-50', '11-50'),
    ('51-200', '51-200'),
    ('201-500', '201-500'),
    ('501-1000', '501-1,000'),
    ('1001-10000', '1,001-10,000'),
    ('10001+', '10,001+'),
)

CONTACT_OPTIONS = (
    ('EMAIL', 'Email'),
    ('PHONE', 'Phone'),
)

FOOD_LEAD_GENERATION_PRODUCT_TYPES = (
    ('DISCOUNT', 'Discount'),
    ('PREMIUM', 'Premium'),
)

ORDER_SIZE_OPTIONS = (
    ('1-1000', '1-1,000 items'),
    ('1000-10000', '1,000-10,000 items'),
    ('10000-100000', '10,001-100,000 items'),
    ('100000+', '100,001+ items'),
)

ORDER_DEADLINE_OPTIONS = (
    ('1-3 MONTHS', '1 to 3 months'),
    ('3-6 MONTHS', '3 to 6 months'),
    ('6-12 MONTHS', '6 months to a year'),
    ('NA', 'N/A'),
)

LEAD_GENERATION_COUNTRIES = [
    (lead_generation.FRANCE, 'France'),
    (lead_generation.SINGAPORE, 'Singapore'),
]

LEAD_GENERATION_CAMPAIGNS = [
    (lead_generation.FOOD_IS_GREAT, lead_generation.FOOD_IS_GREAT),
    (lead_generation.LEGAL_IS_GREAT, lead_generation.LEGAL_IS_GREAT),
]

EXREAD_ARTICLES_CHOICES = (
    (
        exred_articles.ANALYSE_THE_COMPETITION,
        'ANALYSE_THE_COMPETITION'
    ),
    (
        exred_articles.BORROW_AGAINST_ASSETS,
        'BORROW_AGAINST_ASSETS'
    ),
    (
        exred_articles.CHOOSE_THE_RIGHT_FINANCE,
        'CHOOSE_THE_RIGHT_FINANCE'
    ),
    (
        exred_articles.CHOOSING_AGENT_OR_DISTRIBUTOR,
        'CHOOSING_AGENT_OR_DISTRIBUTOR'
    ),
    (
        exred_articles.CONSIDER_HOW_PAID,
        'CONSIDER_HOW_PAID'
    ),
    (
        exred_articles.DECIDE_WHEN_PAID,
        'DECIDE_WHEN_PAID'
    ),
    (
        exred_articles.DEFINE_MARKET_POTENTIAL,
        'DEFINE_MARKET_POTENTIAL'
    ),
    (
        exred_articles.DO_FIELD_RESEARCH,
        'DO_FIELD_RESEARCH'
    ),
    (
        exred_articles.DO_RESEARCH_FIRST,
        'DO_RESEARCH_FIRST'
    ),
    (
        exred_articles.FIND_A_ROUTE_TO_MARKET,
        'FIND_A_ROUTE_TO_MARKET'
    ),
    (
        exred_articles.FRANCHISE_YOUR_BUSINESS,
        'FRANCHISE_YOUR_BUSINESS'
    ),
    (
        exred_articles.GET_EXPORT_FINANCE,
        'GET_EXPORT_FINANCE'
    ),
    (
        exred_articles.GET_GOVERNMENT_FINANCE_SUPPORT,
        'GET_GOVERNMENT_FINANCE_SUPPORT'
    ),
    (
        exred_articles.GET_MONEY_TO_EXPORT,
        'GET_MONEY_TO_EXPORT'
    ),
    (
        exred_articles.GET_YOUR_EXPORT_DOCUMENTS_RIGHT,
        'GET_YOUR_EXPORT_DOCUMENTS_RIGHT'
    ),
    (
        exred_articles.GUIDANCE_BUSINESS_PLANNING,
        'GUIDANCE_BUSINESS_PLANNING'
    ),
    (
        exred_articles.GUIDANCE_CUSTOMER_INSIGHT,
        'GUIDANCE_CUSTOMER_INSIGHT'
    ),
    (
        exred_articles.GUIDANCE_FINANCE,
        'GUIDANCE_FINANCE'
    ),
    (
        exred_articles.GUIDANCE_GETTING_PAID,
        'GUIDANCE_GETTING_PAID'
    ),
    (
        exred_articles.GUIDANCE_MARKET_RESEARCH,
        'GUIDANCE_MARKET_RESEARCH'
    ),
    (
        exred_articles.GUIDANCE_OPERATIONS_AND_COMPLIANCE,
        'GUIDANCE_OPERATIONS_AND_COMPLIANCE'
    ),
    (
        exred_articles.INSURE_AGAINST_NON_PAYMENT,
        'INSURE_AGAINST_NON_PAYMENT'
    ),
    (
        exred_articles.INTELLECTUAL_PROPERTY_PROTECTION,
        'INTELLECTUAL_PROPERTY_PROTECTION'
    ),
    (
        exred_articles.INTERLECTUAL_PROPERTY_PROTECTION,
        'INTERLECTUAL_PROPERTY_PROTECTION'
    ),
    (
        exred_articles.INTERNATIONALISE_WESBITE,
        'INTERNATIONALISE_WESBITE'
    ),
    (
        exred_articles.INVOICE_CURRENCY_AND_CONTENTS,
        'INVOICE_CURRENCY_AND_CONTENTS'
    ),
    (
        exred_articles.KNOW_WHAT_INTELLECTUAL_PROPERTY_YOU_HAVE,
        'KNOW_WHAT_INTELLECTUAL_PROPERTY_YOU_HAVE'
    ),
    (
        exred_articles.KNOW_WHAT_INTERLECTUAL_PROPERTY_YOU_HAVE,
        'KNOW_WHAT_INTERLECTUAL_PROPERTY_YOU_HAVE'
    ),
    (
        exred_articles.KNOW_YOUR_CUSTOMER,
        'KNOW_YOUR_CUSTOMER'
    ),
    (
        exred_articles.LICENCE_AND_FRANCHISING,
        'LICENCE_AND_FRANCHISING'
    ),
    (
        exred_articles.LICENCE_YOUR_PRODUCT_OR_SERVICE,
        'LICENCE_YOUR_PRODUCT_OR_SERVICE'
    ),
    (
        exred_articles.MAKE_EXPORTING_PLAN,
        'MAKE_EXPORTING_PLAN'
    ),
    (
        exred_articles.MANAGE_LANGUAGE_DIFFERENCES,
        'MANAGE_LANGUAGE_DIFFERENCES'
    ),
    (
        exred_articles.MATCH_YOUR_WEBSITE_TO_YOUR_AUDIENCE,
        'MATCH_YOUR_WEBSITE_TO_YOUR_AUDIENCE'
    ),
    (
        exred_articles.MEET_YOUR_CUSTOMER,
        'MEET_YOUR_CUSTOMER'
    ),
    (
        exred_articles.PAYMENT_METHODS,
        'PAYMENT_METHODS'
    ),
    (
        exred_articles.PLAN_THE_LOGISTICS,
        'PLAN_THE_LOGISTICS'
    ),
    (
        exred_articles.RAISE_MONEY_BY_BORROWING,
        'RAISE_MONEY_BY_BORROWING'
    ),
    (
        exred_articles.RAISE_MONEY_WITH_INVESTMENT,
        'RAISE_MONEY_WITH_INVESTMENT'
    ),
    (
        exred_articles.SETUP_OVERSEAS_OPERATION,
        'SETUP_OVERSEAS_OPERATION'
    ),
    (
        exred_articles.START_JOINT_VENTURE,
        'START_JOINT_VENTURE'
    ),
    (
        exred_articles.TYPES_OF_INTELLECTUAL_PROPERTY,
        'TYPES_OF_INTELLECTUAL_PROPERTY'
    ),
    (
        exred_articles.TYPES_OF_INTERLECTUAL_PROPERTY,
        'TYPES_OF_INTERLECTUAL_PROPERTY'
    ),
    (
        exred_articles.UNDERSTAND_YOUR_CUSTOMERS_CULTURE,
        'UNDERSTAND_YOUR_CUSTOMERS_CULTURE'
    ),
    (
        exred_articles.USE_DISTRIBUTOR,
        'USE_DISTRIBUTOR'
    ),
    (
        exred_articles.USE_FREIGHT_FORWARDER,
        'USE_FREIGHT_FORWARDER'
    ),
    (
        exred_articles.USE_INCOTERMS_IN_CONTRACTS,
        'USE_INCOTERMS_IN_CONTRACTS'
    ),
    (
        exred_articles.USE_OVERSEAS_AGENT,
        'USE_OVERSEAS_AGENT'
    ),
    (
        exred_articles.VISIT_TRADE_SHOW,
        'VISIT_TRADE_SHOW'
    ),
    (
        exred_articles.WHAT_INTELLECTUAL_PROPERTY_IS,
        'WHAT_INTELLECTUAL_PROPERTY_IS'
    ),
    (
        exred_articles.SELL_OVERSEAS_DIRECTLY,
        'SELL_OVERSEAS_DIRECTLY'
    ),
    (
        exred_articles.NEXT_STEPS_NEW_EXPORTER,
        'NEXT_STEPS_NEW_EXPORTER',
    ),
    (
        exred_articles.NEXT_STEPS_OCCASIONAL_EXPORTER,
        'NEXT_STEPS_OCCASIONAL_EXPORTER'
    ),
    (
        exred_articles.NEXT_STEPS_REGULAR_EXPORTER,
        'NEXT_STEPS_REGULAR_EXPORTER'
    )
)
