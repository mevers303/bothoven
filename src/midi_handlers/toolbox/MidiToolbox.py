from collections import deque
from functools import reduce
import mido


class MidiToolbox:

    def __init__(self, tool_list):

        self.tool_list = tool_list
        self.tools = deque()
        self.do_prerun = reduce(lambda result, tool: result and tool.do_prerun, self.tools)


    def build_tools(self):

        self.tools.clear()

        for tool_type in self.tool_list:

            tool = tool_type()

            if tool.priority == "first":
                self.tools.append(tool)
            elif tool.priority == "last":
                self.tools.appendleft(tool)
            else:
                raise ValueError("MidiTool.priority must be \"first\" or \"last\".")


    def process_midi_file(self, mid):

        self.build_tools()

        if self.do_prerun:
            self.prerun(mid)


    def prerun(self, mid):

        for tool in self.tools:
            tool.prerun_file_event(mid)

        for track in mid.tracks:

            for tool in self.tools:
                tool.prerun_track_event(track)

            for msg in track:
                for tool in self.tools:
                    tool.prerun_message_event(msg)



class MidiTool:

    def __init__(self, priority = "first", do_prerun = False):

        self.priority = priority
        self.do_prerun = do_prerun

    def prerun_file_event(self, mid):
        pass

    def prerun_track_event(self, track):
        pass

    def prerun_message_event(self, msg):
        pass

    def file_event(self, mid):
        pass

    def track_event(self, track):
        pass

    def message_event(self, msg):
        pass

    def post_process(self):
        pass
