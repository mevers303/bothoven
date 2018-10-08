import copy
from collections import deque
from functools import reduce


class MidiToolbox:

    def __init__(self, tool_list):

        self.tool_list = tool_list
        self.tools = deque()
        self.do_prerun = False


    def build_tools(self):

        self.tools.clear()

        if not len(self.tool_list):
            return

        for tool_type in self.tool_list[::-1]:

            tool = tool_type()

            if tool.priority == "first":
                self.tools.appendleft(tool)
            elif tool.priority == "last":
                self.tools.append(tool)
            else:
                raise ValueError("MidiTool.priority must be \"first\" or \"last\".")

        self.do_prerun = reduce(lambda result, this_tool: result or this_tool.do_prerun, self.tools, self.tools[0].do_prerun)


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
                tool.track_event(track)

                for msg in track:
                    tool.message_event(msg)

                tool.post_track_event(track)

            tool.post_process(mid)

        return mid


    def prerun(self, mid):

        for tool in self.tools:
            tool.prerun_file_event(mid)

            for track in mid.tracks:
                tool.prerun_track_event(track)

                for msg in track:
                    tool.prerun_message_event(msg)

                tool.prerun_post_track_event(track)

            tool.prerun_post_process(mid)


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

    def prerun_post_process(self, mid):
        pass

    def file_event(self, mid):
        pass

    def track_event(self, track):
        pass

    def message_event(self, msg):
        pass

    def post_track_event(self, track):
        pass

    def post_process(self, mid):
        pass
