#!/usr/bin/env python

# reference build https://travis-ci.org/louiscklaw/test_git_repo/builds/625335510
# https://docs.github.com/en/actions/configuring-and-managing-workflows/using-environment-variables

import sys
import os, re
from subprocess import run
import shlex

ERR_EXIT='error found during updating merger'

if __name__ == "__main__":
  try:
    if ('-u' in sys.argv):
      print('update merger')

      run(shlex.split('rsync -avzh --progress /home/logic/_workspace/github-playlist/github-build-merger-tryout/update_merger.py ./github-build-merger/update_merger.py'))

      run(shlex.split('rsync -avzh --progress /home/logic/_workspace/github-playlist/github-build-merger-tryout/merge.py ./github-build-merger/merge.py'))

      sys.exit()

  except Exception as e:
    print(ERR_EXIT)
    raise e
