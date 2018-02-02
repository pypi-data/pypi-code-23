import sys
import os
import gspread
import httplib2
from datetime import datetime
from oauth2client.client import OAuth2WebServerFlow
from oauth2client import file, tools
import pandas as pd
from time import sleep

filename = "oauth.dat"
client_id =     "769904540573-knscs3mhvd56odnf7i8h3al13kiqulft.apps.googleusercontent.com"
client_secret = "D2F1D--b_yKNLrJSPmrn2jik"

def create_google_service(filename, api_name, version):
    """Return instance of Google Service object."""

    from apiclient.discovery import build
    path = os.path.dirname(os.path.realpath('__file__'))
    path_filename = os.path.join(path, filename)
    storage = file.Storage(path_filename)
    credentials = storage.get()
    http = credentials.authorize(http=httplib2.Http())
    service = build(api_name, version, http=http)
    return service


def creds():
    """Create Google OAuth credential object for resources that need it."""

    path = os.path.dirname(os.path.realpath('__file__'))
    path_filename = os.path.join(path, filename)
    storage = file.Storage(path_filename)
    credentials = storage.get()
    return credentials


def oauth():
    """Create a fully authenticated GSheet connection."""

    import argparse
    import json
    scopes = ["https://www.googleapis.com/auth/analytics.readonly",
              "https://www.googleapis.com/auth/webmasters.readonly",
              "https://www.googleapis.com/auth/yt-analytics.readonly",
              "https://www.googleapis.com/auth/youtube.readonly",
              "https://spreadsheets.google.com/feeds/",
              "https://www.googleapis.com/auth/gmail.modify",
              "https://www.googleapis.com/auth/userinfo.email"]

    path = os.path.dirname(os.path.realpath('__file__'))
    path_filename = os.path.join(path, filename)
    flow = OAuth2WebServerFlow(client_id, client_secret, scopes,
                               redirect_uri='urn:ietf:wg:oauth:2.0:oob',
                               response_type='code',
                               prompt='consent',
                               access_type='offline')
    storage = file.Storage(path_filename)
    credentials = storage.get()
    argparser = argparse.ArgumentParser(add_help=False)
    parents = [argparser]
    parent_parsers = [tools.argparser]
    parent_parsers.extend(parents)
    parser = argparse.ArgumentParser(
        description="__doc__",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=parent_parsers)
    flags = parser.parse_args(['--noauth_local_webserver'])
    try:
        http = credentials.authorize(http=httplib2.Http())
    except AttributeError:
        pass
    if credentials is None or credentials.invalid:
        credentials = tools.run_flow(flow, storage, flags)
    else:
        credentials.refresh(http)
    with open(path_filename) as json_file:
        jdata = json.load(json_file)
    token = jdata['access_token']
    access = AccessToken(access_token=token)
    connect = gspread.authorize(access)
    return connect


def ga():
    """Return instance of Google Analytics object."""
    return create_google_service(filename, "analytics", "v3")


def gsc():
    """Return instance of Google Search Console object."""
    return create_google_service(filename, "webmasters", "v3")


def name(name):
    """Return instance of GSheet by document name"""
    return oauth().open(name)


def spreadsheet(key):
    """Return instance of GSheet by key."""
    return oauth().open_by_key(key)


def key(key):
    """Alias to Return instance of GSheet by key."""
    return oauth().open_by_key(key)


class AccessToken(object):
    """Return authentication object given access_token."""
    def __init__(self, access_token=None):
        self.access_token = access_token


def get_email():
    """Return email given provided Google OAuth account."""
    service = create_google_service(filename, "oauth2", "v2")
    user_document = service.userinfo().get().execute()
    email = user_document['email']
    return email


def link(gsheet_key):
    """Return GSheet URL for data from Web UI."""
    return 'https://docs.google.com/spreadsheets/d/%s/edit' % gsheet_key


def Log(yval, xval, sheet):
    """Insert date into 'log' tab at by row/col named index."""

    logsheet = sheet.worksheet('logs')
    row_count = logsheet.row_count
    col_list = logsheet.row_values(1)
    col_count = len(col_list)
    log_cells = logsheet.range(1, 1, row_count, col_count)
    for i, a_cell in enumerate(log_cells):
        m = i % col_count
        if not m and a_cell.value:
            ydex = a_cell.value
            if ydex == yval:
                cell_dex = i+col_list.index(xval)
                cell_value = human_date(datetime.now())
                log_cells[cell_dex].value = cell_value
                logsheet.update_cells(log_cells)
                break


def Check(yval, xval, sheet):
    """Checks if today's date arleady in row/col named index."""

    logsheet = sheet.worksheet('logs')
    return_truth = False
    row_count = logsheet.row_count
    col_list = logsheet.row_values(1)
    col_count = len(col_list)
    log_cells = logsheet.range(1, 1, row_count, col_count)
    for i, a_cell in enumerate(log_cells):
        m = i % col_count
        if not m and a_cell.value:
            ydex = a_cell.value
            if ydex == yval:
                cell_dex = i+col_list.index(xval)
                today_human = human_date(datetime.now())
                cell_value = log_cells[cell_dex].value
                if cell_value == today_human:
                    return_truth = True
                break
    return return_truth


def ga_url(gaid, start, end, path):
    """Return Google Analytics metrics for a URL."""

    path = path.replace(',', r'\,')
    service = ga()
    metrics = ['users', 'newUsers', 'sessions', 'bounceRate',
               'pageviewsPerSession', 'avgSessionDuration']
    metrics = ''.join(['ga:%s,' % x for x in metrics])[:-1]
    ga_request = service.data().ga().get(
        ids='ga:'+gaid,
        start_date=start,
        end_date=end,
        metrics=metrics,
        dimensions='ga:pagePath',
        sort='-ga:users',
        filters='ga:pagePath=='+path,
        segment='sessions::condition::ga:medium==organic',
        max_results=1
    )
    ga_response = ga_request.execute()
    rval = []
    if 'rows' in ga_response:
        raw_rows = ga_response['rows'][0]
        rval = raw_rows
    return rval


def gsc_url_keyword(prop, start, end, query, url):
    service = gsc()
    request = {
      "startDate": start,
      "endDate": end,
      "dimensions": [
        "query",
        "page"
      ],
      "dimensionFilterGroups": [
        {
          "filters": [
            {
              "operator": "equals",
              "expression": url,
              "dimension": "page"
            },
            {
              "operator": "equals",
              "expression": query,
              "dimension": "query"
            }
          ]
        }
      ]
    }
    dat = service.searchanalytics().query(siteUrl=prop, body=request).execute()
    val = []
    if 'rows' in dat:  # For the foolish Hobgoblins of PEP8 consistency
        r = dat['rows'][0]
        val = [start] + [r['keys'][0]] + [r['keys'][1]] + [
            r['position']] + [r['clicks']] + [r['impressions']] + [r['ctr']]
    return val


# NEW FUNCTIONS FOR GSHEET/PANDAS


def cl_df_from_sheet(sheet, row1, col1, col2, row2=False, columns=False, guess=False):
    """Return cell list and dataframe (tuple) from Google Sheet."""

    if row2:
        cl = get_cl(sheet=sheet, row1=row1, col1=col1, col2=col2, row2=row2)
    elif guess:
        cl = get_cl(sheet=sheet, row1=row1, col1=col1, col2=col2, guess=True)
    else:
        cl = get_cl(sheet=sheet, row1=row1, col1=col1, col2=col2)
    list_of_tuples = cl_to_tuples(cl)
    if columns:
        column_names = sheet.range(columns, aa(col1), columns, aa(col2))
        column_names = [x.value for x in column_names]
    else:
        column_names = sheet.range(row1, aa(col1), row1, aa(col2))
        column_names = [cc(x.col) for x in column_names]
    df = pd.DataFrame(list_of_tuples, columns=column_names)
    print("Success! You can now look at your df. It's shape is %s rows x %s cols." % df.shape) 
    print("Do pandas stuff like df['B'] = 'foo', but keep its shape.") 
    print("Update GSheet with changes: gs.populate(cl, df)")
    return cl, df


def pipulate(sheet, rows=(2,), cols=('a','b')):
    """Alias for what I belive will be the most common use of pipulate"""

    left = cols[0]
    right = cols[1]
    row2 = False
    guess=True
    if len(rows) > 1 and rows[1]:
        row2 = rows[1]
        guess = False
    return cl_df_from_sheet(sheet, rows[0], left, right, guess=guess, row2=row2)


def cl_df_to_sheet(sheet, cl, df):
    """Update existing GSpread cell list with a same-shaped dataframe."""
    success = False
    if cl_df_fits(cl, df):
        lol = df.values.tolist()
        flat = [y for x in lol for y in x]
        for i, cell in enumerate(cl):
            cell.value = flat[i]
            success = True
        sheet.update_cells(cl)
    return success


def populate(sheet, cl, df):
    """Alias for cl_df_to_sheet"""
    return cl_df_to_sheet(sheet, cl, df)


def cl_lol_to_sheet(cell_list, lol, sheet):
    """Update existing Gspread scell list with a same-shaped list of lists."""

    flat = [y for x in lol for y in x]
    for i, cell in enumerate(cell_list):
        cell.value = flat[i]
    sheet.update_cells(cell_list)


def cl_to_tuples(cell_list):
    """Return a list of tuples given a GSpread cell list.."""

    list_of_tuples = list()
    num_cols = max([x.col for x in cell_list])
    for i, cell in enumerate(cell_list):
        col = i % num_cols
        if not col:
            a_tuple = tuple([x.value for x in cell_list[i:i+num_cols]])
            list_of_tuples.append(a_tuple)
    return list_of_tuples


def cl_df_fits(cl, df):
    """Check if GSpread cell list same shape as Pandas dataframe."""

    cl_rows = len(set([x.row for x in cl]))
    cl_cols = max([x.col for x in cl])
    print('GSpread cell_list (cl) shape: (%s, %s)' % (cl_rows, cl_cols))
    print('Pandas  DataFrame (dl) shape: (%s, %s)' % df.shape)
    if df.shape == (cl_rows, cl_cols):
        return True
    return False


def get_cl(sheet, row1, col1, col2, guess=False, row2=False):
    """Return GSpread cell list given kk"""

    last_row = sheet.row_count
    if row2:
        last_row = row2
    elif guess:
        last_row = len(list(filter(None, sheet.col_values(1))))
    col1 = aa(col1)
    col2 = aa(col2)
    cell_list = sheet.range(row1, col1, last_row, col2)
    return(cell_list)


def aa(column_letter):
    """Return the column letter for numeric column index."""
    return gspread.utils.a1_to_rowcol('%s1' % column_letter)[1]


def cc(c):
    """Return the column numeric index given column letter index."""
    return gspread.utils.rowcol_to_a1(1, c)[:-1]


def df_to_lol(df):
    """Return a list of lists from Pandas dataframe."""
    return [list(x) for x in df.values]


def api_date(a_datetime, time=False):
    """Return datetime string in Google API friendly format."""
    if time:
        return ('{0:%Y-%m-%d %H:%M:%S}'.format(a_datetime))
    else:
        return ('{0:%Y-%m-%d}'.format(a_datetime))

    
def human_date(a_datetime, time=False):
    """Return datetime object as American-friendly string."""
    if time:
        return ('{0:%m/%d/%Y %H:%M:%S}'.format(a_datetime))
    else:
        return ('{0:%m/%d/%Y}'.format(a_datetime))


class Unbuffered(object):
    """Provides more real-time streaming in Jupyter Notebook"""

    def __init__(self, stream):
        self.stream = stream

    def write(self, data):
        self.stream.write(data)
        self.stream.flush()

    def __getattr__(self, attr):
        return getattr(self.stream, attr)


# Importing pipulate initiates Web-based Google login.
force_it = oauth()

# Forces Jupyter Notebook to not buffer output (like streaming).
sys.stdout = Unbuffered(sys.stdout)
