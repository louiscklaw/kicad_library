#!/usr/bin/env python3

import sys
import os, re, subprocess
import slack
import chalk

from fabric.api import local, shell_env, lcd, run, settings

def get_branch_name(branch_in):
  temp = branch_in.split('/')
  if len(temp) > 1:
    return '/'.join(temp[1:])
  else:
    return branch_in

def create_temp_dir():
  TEMP_DIR = local('mktemp -d', capture=True)
  print(f'create temp directory: {TEMP_DIR}')
  return TEMP_DIR

OS_CWD=os.getcwd()

CONST_BRANCH_UNKNOWN = -1
CONST_BRANCH_FIX = 0
CONST_BRANCH_FEATURE = 1
CONST_BRANCH_TEST = 2
CONST_BRANCH_PRE_MERGE = 3
CONST_BRANCH_DEVELOP = 4
CONST_BRANCH_PRE_MERGE_MASTER = 5
CONST_BRANCH_DEPENDABOT = 6

DRY_RUN=False

merge_direction = {
  '^dependabot/(.+?)$': 'feature',
  '^test/(.+?)$': 'feature',
  '^feature/(.+?)$' : 'develop',
  '^fix/(.+?)$' : 'pre-merge',
  '^pre-merge/(.+?)$' : 'develop',
  # 'develop': 'master'
}

ERR_DRY_RUN_EXPLAIN='DRY RUN ACCEPTED'

GIT_ERR_128_EXPLAIN="error found during creating new branch, check if token is possible to create branch in repo (private repo ?)"

GIT_ERR_CANNOT_CHECKOUT_BRANCH_EXPLAIN="error during checkout branch '{}', is the branch exist ?"
