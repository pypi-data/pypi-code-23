def enum(*vals, **enums):
    """
    Enum without third party libs and compatible with py2 and py3 versions.
    """
    enums.update(dict(zip(vals, vals)))
    return type('Enum', (), enums)


CV_METHOD = enum(RANDOM='random',
                 STRATIFIED='stratified',
                 USER='user',
                 GROUP='group',
                 DATETIME='datetime')


SCORING_TYPE = enum(validation='validation',
                    cross_validation='crossValidation')


DATETIME_AUTOPILOT_DATA_SELECTION_METHOD = enum(ROW_COUNT='rowCount', DURATION='duration')


VERBOSITY_LEVEL = enum(SILENT=0,
                       VERBOSE=2)

# This is deprecated, to be removed in 3.0.
MODEL_JOB_STATUS = enum(
    QUEUE='queue',
    INPROGRESS='inprogress',
    ERROR='error')

# This is the job/queue status enum we want to keep.
# In 3.0 this will be INITIALIZED, RUNNING, ABORTED, COMPLETED, ERROR.
# And maybe the name will change to JobStatus.
QUEUE_STATUS = enum(QUEUE='queue',
                    INPROGRESS='inprogress',
                    ERROR='error',
                    ABORTED='ABORTED',
                    COMPLETED='COMPLETED')

AUTOPILOT_MODE = enum(
    FULL_AUTO='auto',
    MANUAL='manual',
    QUICK='quick'
)

PROJECT_STAGE = enum(EMPTY='empty',
                     EDA='eda',
                     AIM='aim',
                     MODELING='modeling')

ASYNC_PROCESS_STATUS = enum(INITIALIZED='INITIALIZED',
                            RUNNING='RUNNING',
                            COMPLETED='COMPLETED',
                            ERROR='ERROR',
                            ABORTED='ABORTED')

LEADERBOARD_SORT_KEY = enum(PROJECT_METRIC='metric',
                            SAMPLE_PCT='samplePct')

# This is deprecated, to be removed in 3.0.
PREDICT_JOB_STATUS = enum(
    QUEUE='queue',
    INPROGRESS='inprogress',
    ERROR='error',
    ABORTED='ABORTED')


JOB_TYPE = enum(
    MODEL='model',
    PREDICT='predict',
    FEATURE_IMPACT='featureImpact',
    PRIME_RULESETS='primeRulesets',
    PRIME_MODEL='primeModel',
    PRIME_VALIDATION='primeDownloadValidation',
    MODEL_EXPORT='modelExport',
    REASON_CODES_INITIALIZATION='reasonCodesInitialization',
    REASON_CODES='reasonCodes'
)


PRIME_LANGUAGE = enum(
    PYTHON='Python',
    JAVA='Java'
)


VARIABLE_TYPE_TRANSFORM = enum(
    NUMERIC='numeric',
    CATEGORICAL='categorical',
    CATEGORICAL_INT='categoricalInt',
    TEXT='text'
)


DATE_EXTRACTION = enum(
    YEAR='year',
    YEAR_DAY='yearDay',
    MONTH='month',
    MONTH_DAY='monthDay',
    WEEK='week',
    WEEK_DAY='weekDay'
)


POSTGRESQL_DRIVER = enum(
    UNICODE='PostgreSQL Unicode',
    ANSI='PostgreSQL ANSI'
)

BLENDER_METHOD = enum(
    PLS='PLS',
    GLM='GLM',
    ENET='ENET',
    MEDIAN='MED',
    AVERAGE='AVG',
    MAE='MAE',
    MAEL1='MAEL1'
)

CHART_DATA_SOURCE = enum(
    VALIDATION='validation',
    CROSSVALIDATION='crossValidation',
    HOLDOUT='holdout'
)

DEFAULT_MAX_WAIT = 600


# Time in seconds after which to conclude the server isn't responding anymore
DEFAULT_READ_TIMEOUT = 60
