## CHANGELOG v1.2.0

### General
- Improved method docs
- Added `ConfigDialog` class which is a tkinter Toplevel window that shows all the configureable options
- Added `Config.exists(key)` method
- Added `Cache` class for caching any file.
- Added get methods that will return the root class.
  - getUser
  - getConfig
  - getSessionStorage
  - getLocalStorage
  - getCache

### Changes
#### UserFolder.User
- Added 'path' argument so you can define the custom user path. default `C:\Users\<user>\.python\<id>`
    - Note that defining the custom path will not include ID at the end
- `id` is now optional, if unset it will use a sha1 of the filename.

#### UserFolder.Config
- `user` arg is optional. When undefined it will use the root user
- Define a custom path for the user folder using `path`. If set to "%appdata%" it will use the AppData/Roaming folder instead.
- Added `.registerItem` method.
- Added atlas names for the following methods
    - `.set()` => `.setItem()`
    - `.get()` => `.getItem()`
    - `.remove()` => `.removeItem()`
- `.getItem()` has a new argument "default". If the key is not defined in the config it will return this value. default: None

#### UserFolder.Storage
- `user` arg is optional. When undefined it will use the root user
- `filename` arg is optional. default: "storage.yaml"
- Added atlas names for the following methods
    - `.set()` => `.setItem()`
    - `.get()` => `.getItem()`
    - `.remove()` => `.removeItem()`

#### UserFolder.sessionStorage
- When the script ends it will now remove all session storages.


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
