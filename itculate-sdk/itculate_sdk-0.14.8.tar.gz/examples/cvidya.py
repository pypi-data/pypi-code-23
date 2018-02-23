import itculate_sdk as itsdk
from unix_dates import UnixDate

api_key = "1KLYSW4Y5REHJRM0JKPQE3ZXN"
api_secret = "YU6Rls24bV7tyeAU5HMGV0KL9o8GAlg+kHaxBaoec0Y"

server_url = "https://api.itculate.io/api/v1"

engine_key = "ETL Engine 1"

log_file = "RecordsEngine_VOICE_0 - Copy.log"


def get_value_between_string(line, start_sub, end_sub):
    """
    :type line: str
    :type start_sub: str
    :type end_sub: str
    :rtype: float
    """
    start_index = line.find(start_sub)
    if start_index == -1:
        return None
    end_index = line.find(end_sub, start_index)
    if end_index == -1:
        return None

    result = line[start_index + len(start_sub): end_index]
    return float(result)


if __name__ == '__main__':

    itsdk.init(server_url=server_url, api_key=api_key, api_secret=api_secret)

    with open(log_file) as f:
        line = f.readline()

        current_mtime = None
        current_size = []
        current_waited = []

        while line:
            line = f.readline()
            if line and len(line) > 100:
                line = line.strip()
                if line.startswith("Recieved File"):
                    mtime = float(line[-1 * len("1484077522"):])
                    size = get_value_between_string(line=line, start_sub="fvv of size :", end_sub=", Index")
                    waited = get_value_between_string(line=line, start_sub="be handled for :", end_sub=" seconds")

                    if current_mtime is None:
                        current_mtime = mtime

                    elif current_mtime != mtime:
                        total_file_size = sum(current_size)
                        max_file_size = max(current_size)

                        max_waited = max(current_waited)

                        files_count = len(current_waited)

                        itsdk.add_sample(vertex=engine_key,
                                                 timestamp=current_mtime,
                                                 counter="max-waited",
                                                 value=itsdk.DurationDataType.value(value=max_waited,
                                                                                    unit=itsdk.Units.SEC))
                        itsdk.add_sample(vertex=engine_key,
                                                 timestamp=current_mtime,
                                                 counter="total-file-size",
                                                 value=itsdk.CapacityDataType.value(value=total_file_size,
                                                                                    unit=itsdk.Units.BYTES))
                        itsdk.add_sample(vertex=engine_key,
                                                 timestamp=current_mtime,
                                                 counter="files",
                                                 value=itsdk.CountDataType.value(value=files_count))

                        print ("{} : Process {} files ".format(UnixDate.to_datetime(current_mtime), files_count))
                        current_mtime = mtime
                        current_size = []
                        current_waited = []

                    current_size.append(size)
                    current_waited.append(waited)

                    itsdk.flush_all()
