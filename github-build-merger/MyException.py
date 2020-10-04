
class MyException:
  class branch_not_found_except(Exception):
    explain = "error during checkout branch '{}', is the branch exist ?"

  class command_error(Exception):
    explain = "error found during running command"
