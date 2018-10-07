from wwts_globals import progress_bar
import time

for x in range(11):
    progress_bar(x, 10, "WOOHOO!", False)
    time.sleep(.5)

print("done!")
