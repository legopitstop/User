## CHANGELOG v1.1.1

### General
- No longer using plyer as it does not work properly when converted to exe file.

## CHANGELOG v1.1.0

### General

- User id will only use the following characters in regex:`[a-z._\-0-9]`. If the id contains an invalid character it will be removed, except for spaces that will be replaced with underscores.
- Now uses `plyer` to get the user folder, which should make it more cross-platform friendly (only tested on Windows 10)

### Changes

- `User.open(file, mode)` Renamed `filename` arg to `file`
- `User.list(*paths)` Renamed to `listdir(*path)`
- The following now except multiple paths in the user folder.
  - `User.exists(*paths)`
  - `User.show(*paths)`
  - `User.get(*paths)` DEPFRIVED! use .join instead

### New

- `User.download(package, filename)`  Download file from the web.
- `User.unarchive(src, dst)` Unarchive a zip or gz file.
- `User.join(*paths)` Join user path. Just list os.path.join() but automatically includes the path to the user folder. This is used for all other methods that use *paths
- `Storage(user, filename)` Create a file to store key/value pairs.
  - `localStorage(user)` General storage class. Allows you to store key/values in the user folder
  - `sessionStorage(user)` Simlar to localStorage but gets cleared everytime the program starts
- `Config(user)` General config file for program settings
