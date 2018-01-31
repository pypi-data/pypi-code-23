import copy
import datetime


class ReportDefinition:
    GRANULARITIES = ["hour", "day", "week", "month", "quarter", "year"]

    def __init__(self, metrics, dimensions, segments=None, date_from=None,
                 date_to=None, last_days=None, granularity=None, **kwargs):
        # mandatory fields
        self.dimensions = dimensions
        self.metrics = metrics
        self.segments = segments

        self.date_from = date_from
        self.date_to = date_to
        self.last_days = last_days

        # optional fields
        self.granularity = granularity
        self.kwargs = kwargs

    def inject_suite_id(self, suite_id):
        assert isinstance(suite_id, str)

        raw_definition = copy.deepcopy(self.raw)
        raw_definition["reportSuiteID"] = suite_id
        return raw_definition

    @property
    def raw(self):
        self._determine_dates()
        report_definition = self._base_definition()
        report_definition = self._inject_optional_fields(report_definition)
        return report_definition

    def _determine_dates(self):
        self._validate_date_input()

        if self.last_days:
            self._calculate_dates_from_relative()

    def _validate_date_input(self):
        dates_are_relative = self.last_days is not None
        dates_are_absolute = (self.date_from is not None) or (self.date_to is not None)

        assert dates_are_relative or dates_are_absolute, "No time range specified."
        assert not (dates_are_relative and dates_are_absolute), "Either absolute dates or relative dates."

    def _calculate_dates_from_relative(self):
        self.date_from = self._date_days_ago(days=self.last_days)
        self.date_to = self._date_days_ago(days=1)
        self.last_days = None

    @staticmethod
    def _date_days_ago(days):
        date = datetime.date.today() - datetime.timedelta(days=days)
        return date.isoformat()

    def _base_definition(self):
        report_definition = {
            "reportSuiteID": None,  # will be replaced
            "elements": self._prepare_dimensions(),
            "metrics": self._prepare_metrics(),
            "dateFrom": self.date_from,
            "dateTo": self.date_to
        }
        return report_definition

    def _prepare_metrics(self):
        return self._prepare_abstract(variable=self.metrics, name="metrics")

    def _prepare_segments(self):
        return self._prepare_abstract(variable=self.segments, name="segments")

    def _prepare_dimensions(self):
        return self._prepare_abstract(variable=self.dimensions, name="dimensions")

    @staticmethod
    def _prepare_abstract(variable, name):
        """
        Dimensions, metrics and segments should either be provided as str or list. the str
        """
        error_msg = "{} must be str or list.".format(name)
        assert isinstance(variable, (str, list)), error_msg

        if isinstance(variable, str):
            variable = [variable]
        return [ReportDefinition._clean_field(entry) for entry in variable]

    @staticmethod
    def _clean_field(field):
        """
        Dimension can be passed as dictionary or str. str works as abbreviation for basic requests
        and will be converted to proper dictionary form.
        """
        if isinstance(field, str):
            return {"id": field}
        elif isinstance(field, dict):
            return field
        else:
            raise ValueError("Unexpected type of dimension. Please use str or dict.")

    def _inject_optional_fields(self, report_definition):
        if self.segments is not None:
            report_definition["segments"] = self._prepare_segments()

        if self.granularity is not None:
            self._validate_granularity()
            report_definition["dateGranularity"] = self.granularity

        if self.kwargs:
            report_definition.update(self.kwargs)
        return report_definition

    def _validate_granularity(self):
        assert self.granularity in self.GRANULARITIES, "Granularity must be in: {}.".format(self.GRANULARITIES)
