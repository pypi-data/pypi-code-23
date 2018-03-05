import requests

class GTMetrixUtils:
    API_BASE_URL = "https://gtmetrix.com/api/0.1"

    def __init__(self, username, api_key):
        self.username = username
        self.api_key = api_key


    '''
    Runs a new GTMetrix test.

    @param test_url: the URL to test
    @return: the test response in JSON format.
    '''
    def run_test(self, test_url):
        req_data = {
            'url': test_url
        }
        r = requests.post(f'{self.API_BASE_URL}/test', auth=(self.username, self.api_key), data=req_data)
        return r.json()


    '''
    Retrieves test state and results/resources for a given test

    @param test_id: the test to lookup
    @return: the test results/resources in JSON format.
    '''
    def get_results_resources(self, test_id):
        r = requests.get(f'{self.API_BASE_URL}/test/{test_id}', auth=(self.username, self.api_key))
        return r.json()


    '''
    Retrieves results for a given test in JSON format.

    @param url: the URL of the results
    @return: the results in JSON format.
    '''
    def get_results(self, url):
        r = requests.get(url, auth=(self.username, self.api_key))
        return r.json()


    '''
    Downloads a file at the given URL and saves it to the given file.

    @param url: the file to download
    @param output_file: the path to where the file should be saved
    '''
    def download_file(self, url, ouput_file):
        r = requests.get(url, auth=(self.username, self.api_key), stream=True)

        with open(ouput_file, 'wb') as f:
            f.write(r.content)
