#!/usr/bin/env python3

import os,sys
import unittest

from pprint import pprint
from fabric.api import local, shell_env, lcd, run, settings
from chalk import red, green, yellow

import tempfile

PWD = os.getcwd()
sys.path.append(PWD)
# sys.path.append(os.path.join(PWD,'_util'))

from merge import *
from common import *

class TestFunctionExist(unittest.TestCase):
  def test_import(self):
    import common
    import merge
    test_func_list = [
      'push_commit',
      'merge_to_develop_branch',
      'merge_to_feature_branch',
      'merge_to_master_branch',
      'merge_to_pre_merge_branch',
      'merge_to_pre_merge_master_branch'
      ]
    for test_item in test_func_list:
      self.assertTrue(test_item in dir(merge), 'function {} missing'.format(test_item))

class TestMerger(unittest.TestCase):
  def test_get_branch_name(self):
    self.assertTrue(get_branch_name('1/2/3/4/5')=='2/3/4/5', 'test get branch name')

  def test_helloworld(self):
    self.assertTrue(helloworld()=='helloworld test', 'helloworld self test failed')

  def test_CategorizeBranch_fix(self):
    self.assertTrue(categorize_branch('fix/123321')==CONST_BRANCH_FIX,'categorize_branch fix failed')

  def test_CategorizeBranch_develop(self):
    self.assertTrue(categorize_branch('develop')==CONST_BRANCH_DEVELOP,'categorize_branch fix failed')

  def test_CategorizeBranch_pre_merge_master(self):
    self.assertTrue(categorize_branch('pre-merge-master')==CONST_BRANCH_PRE_MERGE_MASTER,'categorize_branch fix failed')

  def test_CategorizeBranch_feature(self):
    self.assertTrue(categorize_branch('feature/123321')==CONST_BRANCH_FEATURE,'categorize_branch fix failed')

  def test_CategorizeBranch_test(self):
    self.assertTrue(categorize_branch('test/123321')==CONST_BRANCH_TEST,'categorize_branch fix failed')

  def test_CategorizeBranch_pre_merge(self):
    self.assertTrue(categorize_branch('pre-merge/123321')==CONST_BRANCH_PRE_MERGE,'categorize_branch fix failed')

  def test_CategorizeBranch_dependabot(self):
    self.assertTrue(categorize_branch('dependabot/npm_and_yarn/preact-graphviz-tryout/lodash')==CONST_BRANCH_DEPENDABOT,'categorize_branch dependabot failed')

class TestWithGitRepo(unittest.TestCase):
  def setUp(self):
    TMP_DIR=tempfile.mkdtemp()
    self.test_git_dir = TMP_DIR+'/test_git_repo'
    local('./scripts/prepare_git.sh {}'.format(self.test_git_dir))
    # self.test_git_dir = os.path.join(os.getcwd(),'test_git_repo')

  def tearDown(self):
    # local('rm -rf test_git_repo',shell=True)
    pass

  def test_create_branch_if_not_exist_not_exist_branch(self):
    self.assertFalse(check_branch_exist('not_exist', self.test_git_dir), 'check_branch_exist return true with non exist branch')

  def test_create_branch_if_not_exist_exist_branch(self):
    self.assertTrue(check_branch_exist('test/test_1', self.test_git_dir),'check_branch_exist return false with exist branch')
    pass

  def test_CreateNewBranch(self):
    self.assertFalse(check_branch_exist('this-is-new_branch', self.test_git_dir))
    if check_branch_exist('this-is-new_branch', self.test_git_dir):
      self.assertTrue(False, "shouldn't be here")
    else:
      create_new_branch('this-is-new_branch',self.test_git_dir)
      self.assertTrue(check_branch_exist('this-is-new_branch', self.test_git_dir),
        'cannot find created branch'
      )

  def test_create_branch_if_not_exist(self):
    self.assertFalse(check_branch_exist('this-is-new_branch', self.test_git_dir))
    create_branch_if_not_exist('this-is-new_branch', self.test_git_dir)
    self.assertTrue(check_branch_exist('this-is-new_branch', self.test_git_dir),
        'cannot find created branch'
      )

class TestStringMethods(unittest.TestCase):

    def test_upper(self):
        self.assertEqual('foo'.upper(), 'FOO')

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)

if __name__ == '__main__':
    unittest.main()
