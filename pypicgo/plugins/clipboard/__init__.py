from pypicgo.core.base.plugin import AfterPlugin
from pypicgo.core.base.result import Result
from .clipbrd import ClipBoard


class ClipBoardPlugin(AfterPlugin):
    name = 'Notify'

    def execute(self, result: Result):
        if result.status:
            ClipBoard.writer(result.message)