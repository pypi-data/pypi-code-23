def enum(*vals, **enums):
    """
    Enum without third party libs and compatible with py2 and py3 versions.
    """
    enums.update(dict(zip(vals, vals)))
    return type('Enum', (), enums)


CV_METHOD = enum(
    DATETIME='datetime',
    GROUP='group',
    RANDOM='random',
    STRATIFIED='stratified',
    USER='user',
)


SCORING_TYPE = enum(
    cross_validation='crossValidation',
    validation='validation',
)


DATETIME_AUTOPILOT_DATA_SELECTION_METHOD = enum(
    DURATION='duration',
    ROW_COUNT='rowCount',
)


VERBOSITY_LEVEL = enum(
    SILENT=0,
    VERBOSE=2,
)


# This is deprecated, to be removed in 3.0.
MODEL_JOB_STATUS = enum(
    ERROR='error',
    INPROGRESS='inprogress',
    QUEUE='queue',
)


# This is the job/queue status enum we want to keep.
# In 3.0 this will be INITIALIZED, RUNNING, ABORTED, COMPLETED, ERROR.
# And maybe the name will change to JobStatus.
QUEUE_STATUS = enum(
    ABORTED='ABORTED',
    COMPLETED='COMPLETED',
    ERROR='error',
    INPROGRESS='inprogress',
    QUEUE='queue',
)


AUTOPILOT_MODE = enum(
    FULL_AUTO='auto',
    MANUAL='manual',
    QUICK='quick',
)


PROJECT_STAGE = enum(
    AIM='aim',
    EDA='eda',
    EMPTY='empty',
    MODELING='modeling',
)


ASYNC_PROCESS_STATUS = enum(
    ABORTED='ABORTED',
    COMPLETED='COMPLETED',
    ERROR='ERROR',
    INITIALIZED='INITIALIZED',
    RUNNING='RUNNING',
)


LEADERBOARD_SORT_KEY = enum(
    PROJECT_METRIC='metric',
    SAMPLE_PCT='samplePct',
)


TARGET_TYPE = enum(
    BINARY='Binary',
    MULTICLASS='Multiclass',
    REGRESSION='Regression',
)


JOB_TYPE = enum(
    FEATURE_IMPACT='featureImpact',
    MODEL='model',
    MODEL_EXPORT='modelExport',
    PREDICT='predict',
    TRAINING_PREDICTIONS='trainingPredictions',
    PRIME_MODEL='primeModel',
    PRIME_RULESETS='primeRulesets',
    PRIME_VALIDATION='primeDownloadValidation',
    REASON_CODES='reasonCodes',
    REASON_CODES_INITIALIZATION='reasonCodesInitialization',
    RATING_TABLE_VALIDATION='validateRatingTable',
)


PREDICT_JOB_STATUS = enum(
    ABORTED='ABORTED',
    ERROR='error',
    INPROGRESS='inprogress',
    QUEUE='queue',
)

PREDICTION_PREFIX = enum(
    DEFAULT='class_'
)

PRIME_LANGUAGE = enum(
    JAVA='Java',
    PYTHON='Python',
)


VARIABLE_TYPE_TRANSFORM = enum(
    CATEGORICAL='categorical',
    CATEGORICAL_INT='categoricalInt',
    NUMERIC='numeric',
    TEXT='text',
)


DATE_EXTRACTION = enum(
    MONTH='month',
    MONTH_DAY='monthDay',
    WEEK='week',
    WEEK_DAY='weekDay',
    YEAR='year',
    YEAR_DAY='yearDay',
)


POSTGRESQL_DRIVER = enum(
    ANSI='PostgreSQL ANSI',
    UNICODE='PostgreSQL Unicode',
)


BLENDER_METHOD = enum(
    AVERAGE='AVG',
    ENET='ENET',
    GLM='GLM',
    MAE='MAE',
    MAEL1='MAEL1',
    MEDIAN='MED',
    PLS='PLS',
)


CHART_DATA_SOURCE = enum(
    CROSSVALIDATION='crossValidation',
    HOLDOUT='holdout',
    VALIDATION='validation',
)


SCALEOUT_MODELING_MODE = enum(
    AUTOPILOT='autopilot',
    DISABLED='disabled',
    REPOSITORY_ONLY='repositoryOnly',
)


DATA_SUBSET = enum(
    ALL='all',
    VALIDATION_AND_HOLDOUT='validationAndHoldout',
    HOLDOUT='holdout',
)

DEFAULT_MAX_WAIT = 600

# default time out values in seconds for waiting response from client
DEFAULT_TIMEOUT = enum(
    CONNECT=6.05,  # time in seconds for the connection to server to be established
    READ=60,  # time in seconds after which to conclude the server isn't responding anymore
    UPLOAD=600,  # time in seconds after which to conclude that project dataset cannot be uploaded
)

# Time in seconds after which to conclude the server isn't responding anymore
# same as in DEFAULT_TIMEOUT, keeping for backwards compatibility
DEFAULT_READ_TIMEOUT = DEFAULT_TIMEOUT.READ
