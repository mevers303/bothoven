from collections import deque
from functools import reduce
import mido


class MidiToolbox:

    def __init__(self, toolset = deque()):

        self.tools = toolset
        self.do_prerun = reduce(lambda result, tool: result and tool.do_prerun, self.tools)


    def add_tool(self, tool):

        if tool.priority == "first":
            self.tools.append(tool)
        elif tool.priority == "last":
            self.tools.appendleft(tool)
        else:
            raise ValueError("MidiTool.priority must be \"first\" or \"last\".")


    def prerun(self, mid):

        for tool in self.tools:
            tool.prerun_file_event(mid)

        for track in mid.tracks:

            for tool in self.tools:
                tool.prerun_track_event(track)

            for msg in track:
                for tool in self.tools:
                    tool.prerun_message_event(msg)


    def process_midi_file(self, mid):

        if self.do_prerun:
            self.prerun(mid)



class MidiTool:

    def __init__(self, priority = "first", do_prerun = False):

        self.priority = priority
        self.do_prerun = do_prerun

    def prerun_file_event(self, mid):
        pass

    def prerun_track_event(self, track):
        pass

    def prerun_message_event(self, track):
        pass

    def file_event(self, mid):
        pass

    def track_event(self, track):
        pass

    def message_event(self, track):
        pass
