#!/usr/bin/env bash

set -e


export TRAVIS_BRANCH=test/test_2
export TRAVIS_COMMIT=0edef86
export TRAVIS_BUILD_NUMBER=1
export TRAVIS_REPO_SLUG=louiscklaw/test_on_github.git
# export GITHUB_TOKEN=token

# # git checkout develop
# cp ../_util/merge.py .
# cp ../_util/test_merger.py .
# pipenv run python3 ./merge.py -d

# # # # # conflict should happen here !
# # # # git merge --ff-only test/test_3


find . |entr -c -s "./test/run_test.sh"