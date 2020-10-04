import sys
import os, re, subprocess
import slack
import chalk

from fabric.api import local, shell_env, lcd, run, settings

TRAVIS_BRANCH=os.environ['GITHUB_REF']
GITHUB_REF=os.environ['GITHUB_REF']
TRIGGERING_BRANCH=GITHUB_REF.replace('refs/heads/','')

GITHUB_REPO = os.environ['GITHUB_REPOSITORY']
GITHUB_TOKEN = os.environ['MY_GITHUB_TOKEN']

PUSH_URI="https://{}@github.com/{}".format(GITHUB_TOKEN, GITHUB_REPO)
