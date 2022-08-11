# UserFolder - 1.1.0

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
| [`plyer`](https://pypi.org/project/plyer/) | Plyer is a platform-independent api to use features commonly found on various platforms, notably mobile ones, in Python. |
| [`uuid`](https://pypi.org/project/uuid/) | UUID object and generation functions (Python 2.3 or higher) |

## License

MIT License

## Planning to add

- User.open in write mode will create any folders that are needed.
