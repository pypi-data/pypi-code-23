#!/usr/bin/env python

from __future__ import print_function

"""
Peach API Security Slack notifier

This tool is used to post completion notices to
a slack channel.

Installation:

  Installation of this tool has two steps.
  
  1. Create the app and webhook in Slack
  2. Install peach2slack

    pip install peachapisec-slack
  
  3. Start using the tool

Syntax:

  peach2slack \
    --api http://192.168.1.100 \
    --api_token=xxxx \
    --slack_webhook https://hooks.slack.com/services/xxxxx

"""

'''
Copyright 2017 Peach Tech

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

try:
	import click
	import peachapisec
	import pystache
	import requests
except:
    print("Error, missing dependencies.")
    print("Use 'pip install -r requirements.txt'")
    exit(-1)

import sys
import os
import json

# Global, slack webhook url
g_slack_webhook = None

def postMessage(data):
	'''
	Send notification via Peach API Security Notification app
	web hook
	'''

	global g_slack_webhook

	response = requests.post(
		g_slack_webhook, data=json.dumps(data),
		headers={'Content-Type': 'application/json'}
	)
	if response.status_code != 200:
		raise ValueError(
			'Request to slack returned an error %s, the response is:\n%s'
			% (response.status_code, response.text)
		)

@click.command(help="Peach API Security Slack Integration")
@click.option("--api", help="Peach API Security API URL. Defaults to PEACH_API environ.")
@click.option("--api_token", help="Peach API Security API Token. Defaults to PEACH_API_TOKEN environ.")
@click.option("--slack_webhook", help="Slack webhook URL. Defaults to PEACH_SLACK_WEBHOOK environ.")
@click.option(
	"--msg", 
	help="Message template to post when no issues are found. Defaults to PEACH_MSG environ.",
	default="Security testing completed succesfully, no issues found after {{tests_count}} tests.")
@click.option(
	"--failmsg", 
	help="Message template to post when issues are found. Defaults to PEACH_FAILMSG environ.",
	default="A total of {{failure_count}} failures from {{tests_count}} tests were found.")
@click.option(
	"--errormsg", 
	help="Error message template to post when job did't complete. Defaults to PEACH_ERRORMSG environ.",
	default="Error: {{reason}}")
def cli(api, api_token, slack_webhook, msg, failmsg, errormsg, **kwargs):

	if not api:
		print("Error, must supply --api parameter.")
		return 1
	if not api_token:
		print("Error, must supply --api_token parameter.")
		return 1
	if not slack_webhook:
		print("Error, must supply --slack_webhook parameter.")
		return 1

	global g_slack_webhook
	g_slack_webhook = slack_webhook

	peachapisec.set_peach_api(api)
	peachapisec.set_peach_api_token(api_token)

	jobs = peachapisec.get_jobs()
	if len(jobs) == 0:
		print(" - No jobs found, exiting")
		return 1

	# Use the most recent job
	job = jobs[0]

	tags = job['Tags']
	tag_str = ""
	for tag in tags:
		tag_str += "%s," % tag
	if len(tag_str) > 0: tag_str[:-1]

	data = {
		"project":job['Name'],
		"job_id" : job['Id'],
		"job_url" : api + "/jobs/"+job['Id'],
		"job_tags" : tag_str,
		"reason" : job['Reason'],
		"failure_count" : job['FaultCount'],
		"tests_count" : job['TotalTestCount'],
	}

	if len(tag_str) > 0:
		data["job_tags2"] = " - "+tag_str
	else:
		data["job_tags2"] = ""

	state = job['State']
	if state == 'Finished':
		if job['HasFaults']:
			msg = failmsg
			title = "Testing of {{project}}{{job_tags2}} completed with failures"
			color = "#f44141"
		else:
			msg = msg
			title = "Testing of {{project}}{{job_tags2}} completed with no failures"
			color = "#7CD197"
	else:
		msg = errormsg
		title = "Testing of {{project}}{{job_tags2}} failed due to an error"
		color = "#f1f441"

	title = pystache.render(title, data)
	msg = pystache.render(msg, data)

	slack_data = {
		'attachments':[
			{
				"title": title,
				"title_link": api + "/jobs/"+job['Id'],
				"text": msg,
				"color": color,
			},
		]}

	postMessage(slack_data)

def run():
	cli(auto_envvar_prefix='PEACH')

if __name__ == '__main__':
    run()

# end
