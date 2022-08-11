# CHANGELOG v1.1.0

## General

- User id will only use the following characters in regex:`[a-z._\-0-9]`. If the id contains an invalid character it will be removed, except for spaces that will be replaced with underscores.
- Now uses `plyer` to get the user folder

## Changes

- `user = User(id, config)` if `config` is defined it will create a config file that can be used by calling `user.config(mode)`
- `user.open()` will create any directories that are needed for the file.

## New

- `user.download()`  Download files or archives to the user's folder.
- `user.unarchive()` Unarchives (unzips) the archived file.
