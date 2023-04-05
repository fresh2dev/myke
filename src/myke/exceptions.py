from __future__ import annotations


class MykeNotFoundError(Exception):
    ...


class TaskAlreadyRegisteredError(Exception):
    ...


class NoTasksFoundError(Exception):
    ...


#  class CalledProcessError(subprocess.CalledProcessError):
#      def __str__(self) -> str:
#          if self.returncode and self.returncode < 0:
#              return super().__str__()
#          else:
#              msg: str = (
#                  f"Command '{self.cmd}' returned non-zero exit status {self.returncode}:"
#              )
#              for attr in "stdout", "stderr":
#                  attr_value: str = getattr(self, attr)
#                  if attr_value:
#                      attr_value_trimmed: str = attr_value.rstrip("\n")
#                      if attr_value_trimmed:
#                          msg += f"\n{attr}:\n{attr_value_trimmed}"
#              return msg
