import UserFolder
from time import sleep

def progress(e: UserFolder.TrackEvent):  # Print the current status.
    percent = int(e.percentage)
    done = int(e.percentage/10)*5
    fill = 10*5 - done
    if percent != 100:
        end = '\r'  # Print on same line until 100%
    else:
        end = None
    print('Progress: |{0}{1}| {2}% Complete'.format('█'*done, '-'*fill, percent), end=end)
    # Slow down the progress so you can actually see the progress.
    sleep(.5)

user = UserFolder.User('_test')

if user.exists('UserFolder-1.0.2')==False:
    user.download('https://github.com/legopitstop/UserFolder/archive/refs/tags/v1.0.2.zip', 'package.zip', trackcommand=progress)
    user.unarchive('package.zip', trackcommand=progress)
