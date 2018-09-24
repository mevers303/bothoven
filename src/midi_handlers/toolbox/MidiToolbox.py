import copy
from collections import deque
from functools import reduce
import mido


class MidiToolbox:

    def __init__(self, tool_list):

        self.tool_list = tool_list
        self.tools = deque()
        self.do_prerun = False


    def build_tools(self):

        self.tools.clear()

        for tool_type in self.tool_list[::-1]:

            tool = tool_type()

            if tool.priority == "first":
                self.tools.append(tool)
            elif tool.priority == "last":
                self.tools.appendleft(tool)
            else:
                raise ValueError("MidiTool.priority must be \"first\" or \"last\".")

        self.do_prerun = reduce(lambda result, tool: result or tool.do_prerun, self.tools, self.tools[0].do_prerun)


    def process_midi_file(self, original_mid):

        mid = copy.deepcopy(original_mid)
        self.build_tools()

        # do the pre-run
        if self.do_prerun:
            self.prerun(mid)

        # now for regular processing
        for tool in self.tools:
            tool.file_event(mid)

        for track in mid.tracks:

            for tool in self.tools:
                tool.track_event(track)

            for msg in track:
                for tool in self.tools:
                    tool.message_event(msg)

            for tool in self.tools:
                tool.post_track_event(track)

        for tool in self.tools:
            tool.post_process()

        return mid


    def prerun(self, mid):

        for tool in self.tools:
            tool.prerun_file_event(mid)

        for track in mid.tracks:

            for tool in self.tools:
                tool.prerun_track_event(track)

            for msg in track:
                for tool in self.tools:
                    tool.prerun_message_event(msg)

            for tool in self.tools:
                tool.prerun_post_track_event(track)

        for tool in self.tools:
            tool.prerun_post_process()


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

    def prerun_post_track_event(self, track):
        pass

    def prerun_post_process(self):
        pass

    def file_event(self, mid):
        pass

    def track_event(self, track):
        pass

    def message_event(self, msg):
        pass

    def post_track_event(self, track):
        pass

    def post_process(self):
        pass
