"""Hello Analytics Reporting API V4."""

from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
import yaml

SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
KEY_FILE_LOCATION = 'client_secrets.json'

def initialize_analyticsreporting():
    """Initializes an Analytics Reporting API V4 service object.

    Returns:
      An authorized Analytics Reporting API V4 service object.
    """
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        KEY_FILE_LOCATION, SCOPES)

    # Build the service object.
    analytics = build('analyticsreporting', 'v4', credentials=credentials)

    return analytics


def get_report(analytics, site, pageToken=None):
    """Queries the Analytics Reporting API V4.

    Args:
      analytics: An authorized Analytics Reporting API V4 service object.
    Returns:
      The Analytics Reporting API V4 response.

    """

    return analytics.reports().batchGet(
        body={
            'reportRequests': [
                {
                    'viewId': site['view'],
                    'dateRanges': [{'startDate': '2019-01-01', 'endDate': '2019-12-31'}],
                    'metrics': [{'expression': 'ga:pageviews'}],
                    'dimensions': [{'name': 'ga:pagePath'}],
                    'dimensionFilterClauses': [{
                        'filters': get_path_filters(site)
                    }],
                    'orderBys': [{'fieldName': 'ga:pageviews', 'sortOrder': 'DESCENDING'}],

                    'pageSize': 10000,
                    'pageToken': pageToken
                }]
        }
    ).execute()


def get_path_filters(site):
    filters = []
    for f in site['filters']:
        filters.append(get_path_filter(f))
    return filters


def get_path_filter(regex):
    return {"dimensionName": "ga:pagePath",
            "operator": "REGEXP",
            "expressions": [regex]}


def print_response(response, output):
    """Parses and prints the Analytics Reporting API V4 response.

    Args:
      response: An Analytics Reporting API V4 response.
    """
    for report in response.get('reports', []):
        columnHeader = report.get('columnHeader', {})
        metricHeaders = columnHeader.get('metricHeader', {}).get('metricHeaderEntries', [])

        for row in report.get('data', {}).get('rows', []):
            dimensions = row.get('dimensions', [])
            metrics = row.get('metrics', [])

            for i, values in enumerate(metrics):
                for metricHeader, value in zip(metricHeaders, values.get('values')):
                    output.write(dimensions[0] + '\t' + value + "\n")


def main():
    with open("sites.yaml") as file:
        sites = yaml.full_load(file)

    analytics = initialize_analyticsreporting()

    for key in sites:
        site = sites[key]
        # paginate through reports to get all
        print("Fetching " + site['name'])
        responses = [get_report(analytics, site)]
        while responses[-1].get('reports')[0].get('nextPageToken') is not None:
            print("Fetching " + site['name'] + " " + responses[-1].get('reports')[0].get('nextPageToken'))
            responses.append(get_report(analytics, site, responses[-1].get('reports')[0].get('nextPageToken')))

        output = open(site['filename'], "w+", encoding="utf-8")
        for response in responses:
            print_response(response, output)
        output.close()


if __name__ == '__main__':
    main()
