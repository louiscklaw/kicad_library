#!/usr/bin/env python

# reference build https://travis-ci.org/louiscklaw/test_git_repo/builds/625335510
# https://docs.travis-ci.com/user/environment-variables/

import os, re, subprocess
import slack

from fabric.api import local, shell_env, lcd, run, settings

SLACK_TOKEN = os.environ['SLACK_TOKEN']

BRANCH_TO_MERGE_INTO='develop'
BRANCH_TO_MERGE_REGEX='^feature'
TRAVIS_BRANCH = os.environ['TRAVIS_BRANCH']
TRAVIS_COMMIT = os.environ['TRAVIS_COMMIT']
TRAVIS_BUILD_NUMBER = os.environ['TRAVIS_BUILD_NUMBER']
GITHUB_REPO = os.environ['TRAVIS_REPO_SLUG']
GITHUB_SECRET_TOKEN = os.environ['GITHUB_SECRET_TOKEN']
TRAVIS_COMMIT_MESSAGE = os.environ['TRAVIS_COMMIT_MESSAGE']

PUSH_URI="https://{}@github.com/{}".format(GITHUB_SECRET_TOKEN, GITHUB_REPO)

TEMP_DIR = local('mktemp -d', capture=True)
local('git clone "{}" "{}"'.format(PUSH_URI, TEMP_DIR))

def slack_message(message, channel):
  client = slack.WebClient(token=SLACK_TOKEN)
  response = client.chat_postMessage(
      channel=channel,
      text=message,
      username='TravisMergerBot',
      icon_url=':sob:'
      )

def run_command(command_body):
  command_result = local(command_body, capture=True)
  print(command_result, command_result.stderr)
  return command_result

m = re.match(BRANCH_TO_MERGE_REGEX, TRAVIS_BRANCH)
if (m == None ) :
  print('skipping merge for branch {}'.format(TRAVIS_BRANCH))
  slack_message('skip merging for BUILD #{} `{}` from `{}` to `{}`'.format(TRAVIS_BUILD_NUMBER, GITHUB_REPO, TRAVIS_BRANCH, BRANCH_TO_MERGE_INTO), '#travis-build-result')

else:
  with lcd(TEMP_DIR), settings(warn_only=True):
    with( shell_env( GIT_COMMITTER_EMAIL='travis@travis', GIT_COMMITTER_NAME='Travis CI' ) ):
      print('checkout {} branch'.format(BRANCH_TO_MERGE_INTO))
      run_command('git checkout {}'.format(BRANCH_TO_MERGE_INTO))

      print('Merging "{}"'.format(TRAVIS_COMMIT))
      result_to_check = run_command('git merge --ff-only "{}"'.format(TRAVIS_COMMIT))
      if result_to_check.failed:
        slack_message('error found during merging BUILD{} `{}` from `{}` to `{}`'.format(TRAVIS_BUILD_NUMBER, GITHUB_REPO, TRAVIS_BRANCH, BRANCH_TO_MERGE_INTO), '#travis-build-result')
      else:
        slack_message('merging BUILD{} from {} `{}` to `{}` done, commit message "{}"'.format(TRAVIS_BUILD_NUMBER, GITHUB_REPO, TRAVIS_BRANCH, BRANCH_TO_MERGE_INTO, TRAVIS_COMMIT_MESSAGE), '#travis-build-result')


      print('push commit')
      run_command("git push {} {}".format(PUSH_URI, BRANCH_TO_MERGE_INTO))