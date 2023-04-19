# UserFolder

## What is this?

This is a simple library that allows you to read, write and create files within your own folder inside the user folder (`C:/User/USER/.python/PACKAGE_ID`)

## Features

- Automatically creates the directory.
- Read and write to files inside the User folder.
- Includes an uninstall function that will delete all files inside your directory.
- A function to open the directory or open the file that is inside the directory.

## Install

`pip install UserFolder`

## Requirements

| Name | Descirption |
|--|--|
| [`requests`](https://pypi.org/project/requests/) | **Requests** is a simple, yet elegant, HTTP library. |
| [`uuid`](https://pypi.org/project/uuid/) | UUID object and generation functions (Python 2.3 or higher) |

## License

MIT License


## Examples
Download needed assets

```Python
import UserFolder

user = UserFolder.User('com.legopitstop.example') # Create user folder

if user.exists('UserFolder-1.0.2')==False: # Check if folder already exists
    # Download ZIP
    user.download('https://github.com/legopitstop/UserFolder/archive/refs/tags/v1.0.2.zip', 'package.zip')
    # Unarchive ZIP
    user.unarchive('package.zip')


```

Universal config
```Python
import tkinter
import UserFolder
from UserFolder import dialog
from enum import Enum

user = UserFolder.User('com.legopitstop.example') # Create user folder

# Define values
class values(Enum):
    item1 = 'item1'
    item2 = 'item2'
    item3 = 'item3'
    item4 = 'item4'
    item5 = 'item5'

# Create config with section "metadata"
config = UserFolder.Config(section='metadata')

# Register options
config.registerItem('option1', 'value1', str, 'Option1', 'String config item')
config.registerItem('option2', True, bool, 'Option2', 'Boolean config item')
config.registerItem('option3', 1, int, 'Option3', 'Integer config item', from_=0, to=10)
config.registerItem('option4', 1.0, float, 'Option4', 'Float config item', from_=0.0, to=1.0)
config.registerItem('option5', 50, range, 'Option5', 'Range config item')
config.registerItem('option6', values.item1, values, 'Option6', 'Enum config item')

# Tkinter UI
root = tkinter.Tk()
root.title('Main Window')
root.minsize(500, 500)

# Open config dialog when pressed
tkinter.Button(root, text='Open ConfigDialog', command=lambda: dialog.ConfigDialog(parent=root)).pack()

# Open user folder when pressed
tkinter.Button(root, text='Open User Folder', command=user.show).pack()
root.mainloop()
```