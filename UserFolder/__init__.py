from io import TextIOWrapper
import os
import requests
import tarfile
import zipfile
import yaml
import re
import uuid
import configparser
import hashlib
import threading
import atexit
import json
import tempfile

__version__ = '1.2.0'
__temp__ = []
__root__ = {'sessionStorage': [], 'cache': []}

class UnsupportedArchiveError(Exception): pass
class CacheError(Exception): pass

class TrackEvent():
    def __init__(self, member: zipfile.ZipInfo, count: int, total: int):
        """
        The track event returned by trackcommand.

        Arguments
        ---
        `member` - The Zip.Info or filename

        `count` - The current member of total

        `total` - The total number of members
        """
        self.member = member
        self.count = count
        self.total = total
        self.percentage = count * 100 / total

class User():
    def __init__(self, id:str=None, setupcommand=None, path:str=None):
        """
        Will create the file path inside the Users folder. Your id should be a unique string just for your script.

        Arguments
        ---
        `id` - The uuid of the project. Recomended to use a backwords url: 'com.username.project_name'

        `setupcommand` - Runs the first time the program has ever ran on this user. This can be used to install any required files.
        
        `path` - The path that it should use. by default it is your userfolder 'C:/Users/<user>/.python/<id>'. If set to '%appdata%' it will use the appdata folder instead 'C:/Users/<user>/AppData/Roaming/<id>'

        Methods
        ---
        join, uninstall, exists, open, listdir, show, download, unarchive, copy, remove
        """
        self._setup = setupcommand
        if id is None:
            stringM = os.path.basename(__file__)
            byteM = bytes(stringM, encoding='utf')
            id = hashlib.sha1(byteM).hexdigest()

        def trim(s: str): return re.sub(
            r'[^a-z._\-0-9]', '', str(s).lower().strip().replace(' ', '_'))
        self.id = trim(id)
        self.path = os.path.join(os.path.expanduser('~'), '.python', self.id) # Default path
        if path != None:
            match path:
                case '%appdata%': self.path = os.path.join(os.path.expanduser('~'), 'AppData', 'Roaming', self.id)
                case _: self.path

        if os.path.isdir(self.path) == False:
            os.makedirs(self.path, exist_ok=True)
            if self._setup is not None:
                self._setup(self)  # Call setup command

        # Root
        global __root__
        __root__['user'] = self

    def __str__(self):
        return f'User(id={self.id})'

    def _download(self, package, filename, trackcommand):
        r = requests.get(package, allow_redirects=True)
        if filename == None:
            filename = os.path.basename(package)
        if r.status_code == 200:
            open(self.join(filename), 'wb').write(r.content)
        return r

    def _unarchive(self, src, dst, members, format, deletesrc, trackcommand):
        """Internal Function"""
        src = self.join(src)
        if dst == None: dst = self.path
        else: dst = self.join(dst)
        # Get format
        if format is None:  # Auto detect format
            if src.endswith('.zip'):
                format = 'zip'
            elif src.endswith('.gz'):
                format = 'gz'
        else:
            format = format.upper()
        match format.casefold():
            case 'zip':
                with zipfile.ZipFile(src, 'r') as file:
                    if members is None:
                        MEMBERS = file.namelist()
                    else:
                        MEMBERS = members
                    total = len(MEMBERS)
                    count = 1
                    for member in MEMBERS:
                        file.extract(member, dst)
                        event = TrackEvent(member, count, total)
                        if trackcommand != None:
                            trackcommand(event)
                        count += 1
                if deletesrc:
                    os.remove(src)
                return True
            
            case 'gz':
                with tarfile.open(src) as file:
                    if members is None:
                        MEMBERS = file.getmembers()
                    else:
                        MEMBERS = members
                    total = len(MEMBERS)
                    count = 1
                    for member in MEMBERS:
                        event = TrackEvent(member, count, total)
                        if trackcommand != None:
                            trackcommand(event)
                        file.extract(member, dst)
                        count += 1
                    file.close()
                if deletesrc:
                    os.remove(src)
                return True
            case _:
                raise UnsupportedArchiveError('Unsupported archive! Supported archive types: .zip, .gz')

    def join(self, *paths: str) -> str:
        """
        Join user path

        Arguments
        ---
        `paths` - A list of each folder in path

        Returns
        ---
        str - The combined user path
        """
        return os.path.join(self.path, *paths)
    get = join

    def uninstall(self) -> bool:
        """
        Will delete the scripts user folder.

        Returns
        ---
        `True` - Successfully deleted the scripts user folder.

        `False` - Failed to delete the scripts user folder, A file is still being prossessed.
        """
        try:
            for filename in self.list():
                os.remove(self.path+filename)
            os.rmdir(self.path)
            return True
        except:
            return False

    def exists(self, *paths: str) -> bool:
        """
        Checks if the file exists inside the scripts user folder.

        Arguments
        ---
        `paths` - A list of each folder in path

        Returns
        ---
        `True` - The file exists.

        `False` - The file does not exist.
        """
        try:
            if os.path.exists(self.join(*paths)):
                return True
            else:
                return False
        except:
            return False

    def open(self, file: str, mode: str = 'r') -> TextIOWrapper:
        """
        Opens the file that is in the scripts user folder.

        Arguments
        ---
        `file` - A list of each folder in path

        `mode` - The mode to open this file in

        Returns
        ---
        TextIOWrapper - The contents of the file.

        Character	Meaning
        ---

        'r'	open for reading (default)

        'w'	open for writing, truncating the file first

        'x'	create a new file and open it for writing

        'a'	open for writing, appending to the end of the file if it exists

        'b'	binary mode

        't'	text mode (default)

        '+'	open a disk file for updating (reading and writing)

        'U'	universal newline mode (deprecated)
        """
        PATH = self.join(file)
        if mode == 'w' or mode == 'a':
            DIR = os.path.dirname(PATH)
            os.makedirs(DIR, exist_ok=True)
            try:
                return open(PATH, mode)
            except FileNotFoundError:
                raise FileNotFoundError(f"No File or directory: '{PATH}'")
        else:
            try:
                return open(PATH, mode)
            except FileNotFoundError:
                raise FileNotFoundError(f"No File or directory: '{PATH}'")

    def listdir(self, *paths: str) -> list[str]|None:
        """
        Returns a list of all files that are in the scripts users folder.

        Arguments
        ---
        `paths` - A list of each folder in path

        Returns
        ---
        list[str] - A list of all files that are currently inside the scripts user folder.

        `None` - Failed to list the directory
        """
        try:
            return os.listdir(self.join(*paths))
        except:
            return None

    def show(self, *paths: str) -> bool:
        """
        Opens the file in your devices default editor. If filename is undefined it will open the scripts user folder.

        Arguments
        ---
        `paths` - A list of each folder in path

        Returns
        ---
        `True` - Successfully showed the file or folder.

        `False` - Failed to show file or folder.
        """
        try:
            os.startfile(self.join(*paths))
            return True
        except:
            return False

    def download(self, package: str, filename: str = None, trackcommand=None, thread:bool=False) -> requests.Response:
        """
        Download file from the web. If request returns status code '404' it will not download the file.

        Arguments
        ---
        `package` - The URL to the package to download.

        `filename` - The filename of the package.

        `trackcommand` - The callback command for downloading the file.
        
        `thread` - If true it will run in a new thread.

        Returns
        ---
        requests.Response - Response from the download.
        """
        if thread:
            t = threading.Thread(target=self._download, args=[package, filename, trackcommand])
            t.start()
        else: self._download(package, filename, trackcommand)

    def unarchive(self, src: str, dst: str = None, members: list = None, format: str = None, deletesrc: bool = True, trackcommand=None, thread:bool=False) -> bool:
        """
        Unarchive a zip or gz file. It's recomended to call this method in a thread.

        Arguments
        ---
        `src` - The path to the archive

        `dst` - The destination to drop the unarchived folders.

        `members` - The members to unarchive. Will otherwise extract all members

        `format` - The archive format. 'zip' or 'gz'

        `deletesrc` - Delete the orgional source file after it is done unarchiving.

        `trackcommand` - The callback command for every member in archive.
        
        `thread` - If true it will run in a new thread.

        Returns
        ---
        `True` - Successfully unarchived package.

        `False` - Failed to unarchive package
        """
        
        if thread:
            t = threading.Thread(target=self._unarchive, args=[src, dst, members, format, deletesrc, trackcommand])
            t.start()
        else:
            self._unarchive(src, dst, members, format, deletesrc, trackcommand)

    def copy(self, src:str, dst:str, delete_src:bool=False, delete_files:bool=False):
        """
        Copy a file or directory from src to dst
        
        Arguments
        ---
        `src` - The source path to copy

        `dst` - The destination path to paste the source path.

        `delete_src` - When true it will delete the source path.

        `delete_files` - Delete all files in directory. (Can only delete empty directories).
        """
        _src = self.join(src)
        _dst = self.join(dst)
        if os.path.isfile(src):
            with open(_src, 'rb') as rb:
                os.makedirs(os.path.dirname(_dst), exist_ok=True) # Make the path
                with open(_dst, 'wb') as wb: wb.write(rb.read())
        else:
            for dir in os.listdir(_src):
                src_path = os.path.join(_src, dir)
                dst_path = os.path.join(_dst, dir)
                self.copy(src_path, dst_path, delete_src)

        if delete_src: self.remove(_src, delete_files)
        return self

    def remove(self, path:str, delete_files:bool=False):
        """
        Removes a directory or a file from the UserFolder.
        
        Arguments
        ---
        `path` - The file or directory to delete.

        `delete_files` - Delete all files in directory. (Can only delete empty directories).
        """
        _path = self.join(path)
        if os.path.isfile(_path):
            os.remove(_path)
        else:
            if delete_files:
                for file in os.listdir(_path):
                    fp = os.path.join(_path, file)
                    self.remove(fp, delete_files)
            try: os.rmdir(_path)
            except OSError as err: raise OSError(str(err)+'. You must set delete_files argument to True.')
        return self

class Storage():
    def __init__(self, user: User = None, filename: str = 'storage.yaml'):
        """
        Create a file to store key/value pairs.

        Arguments
        ---
        `user` - The User class for the storage.

        `filename` - The name of the file to store all values.

        Methods
        ---
        getItem, setItem, removeItem, clear, key, exists, show
        """
        if user is None:
            user = getUser()
        self.user = user
        self.filename = filename
        self.file = user.join(filename)
        self.first = False
        # Create file
        if os.path.exists(self.file) == False:
            wrt = self.user.open(self.file, 'w')
            wrt.write('')
            wrt.close()
            self.first = True

        self.length = self._len()

    def __str__(self):
        name  = os.path.basename(self.filename)
        return f'Storage(filename="{name}")'
    
    def _len(self):
        opn = self.user.open(self.file, 'r')
        data = yaml.load(opn, yaml.FullLoader)
        opn.close()
        if data != None:
            count = 0
            for i in data:
                count += 1
            return count
        else:
            return 0

    def getItem(self, key: str):
        """
        Returns the current value associated with the given key, or null if the given key does not exist.

        Arguments
        ---
        `key` - Get the value of the key
        """
        opn = self.user.open(self.file, 'r')
        data = yaml.load(opn, yaml.FullLoader)
        opn.close()
        if data != None:
            if str(key) in data:
                return data[str(key)]
            else:
                raise KeyError(key)
        else:
            raise KeyError(key)
    get = getItem

    def setItem(self, key: str, value: str):
        """
        Sets the value of the pair identified by key to value, creating a new key/value pair if none existed for key previously.

        Arguments
        ---
        `key` - The key to set

        `value` - The value of the key to set
        """
        opn = self.user.open(self.file, 'r')
        data = yaml.load(opn, yaml.FullLoader)
        opn.close()

        if data != None:
            data[str(key)] = value
        else:
            data = {}
            data[str(key)] = value

        wrt = self.user.open(self.file, 'w')
        wrt.write(yaml.dump(data))
        wrt.close()
        return self
    set = setItem

    def removeItem(self, key: str):
        """
        Removes the key/value pair with the given key, if a key/value pair with the given key exists.

        Arguments
        ---
        `key` - The key/value pair to remove.
        """
        opn = self.user.open(self.file, 'r')
        data = yaml.load(opn, yaml.FullLoader)
        opn.close()

        if data != None:
            if str(key) in data:
                del data[str(key)]
            else:
                raise KeyError(key)

            wrt = self.user.open(self.file, 'w')
            wrt.write(yaml.dump(data))
            wrt.close()
        return self
    remove = removeItem

    def clear(self):
        """
        Removes all key/value pairs, if there are any.
        """
        wrt = self.user.open(self.file, 'w')
        wrt.write('')
        wrt.close()
        return self

    def key(self, index: int) -> str|None:
        """
        Returns the name of the nth key, or None if n is greater than or equal to the number of key/value pairs.

        Arguments
        ---
        `index` - The index in the store to get the key from.

        Returns
        ---
        str - Name of the key

        None - Index out of bounds error
        """
        opn = self.user.open(self.file, 'r')
        data = yaml.load(opn, yaml.FullLoader)
        opn.close()
        if data != None:
            # get all keys in a list
            keys = []
            for k in data:
                keys.append(k)
            try:
                return keys[int(index)]
            except IndexError:
                return None
        else:
            return None

    def exists(self, key: str):
        """
        Checks if key/value pair exists

        Arguemnts
        ---
        `key` - The key to test for
        """
        try:
            self.getItem(key)
            return True
        except KeyError:
            return False

    def show(self):
        """
        Open the storage file
        """
        return os.startfile(self.file)

    def destroy(self):
        """Delete this storage file"""
        try: self.user.remove(self.file)
        except OSError: pass
        del self

class localStorage(Storage):
    def __init__(self, user: User = None):
        """
        General storage class. Allows you to store key/values in the user folder

        Arguments
        ---
        `user` - The User class for the local storage.

        Methods
        ---
        getItem, setItem, removeItem, clear, key, exists, show
        """
        super().__init__(user, 'localStorage.yaml')
        global __root__
        __root__['localStorage'] = self

class sessionStorage(Storage):
    def __init__(self, user: User = None):
        """
        Simlar to localStorage but gets cleared everytime the program starts

        Arguments
        ---
        `user` - The User class for the session storage.

        Methods
        ---
        getItem, setItem, removeItem, clear, key, exists, show
        """
        super().__init__(user, '.session/%s.yaml' % (uuid.uuid4().hex))

        global __root__
        __root__['sessionStorage'].append(self)

class Config():
    def __init__(self, user: User = None, section: str = None):
        """
        General config file for program settings

        Arguments
        ---
        `user` - The User class for the config.

        `section` - Teh configs section. default value; DEFAULT

        Methods
        ---
        section, setItem, getItem, removeItem, registerItem, unregisterItem
        """
        if user is None: user = getUser()
        self.user = user
        self.registry = {}

        # Default section is the user id
        if section is None: section = self.user.id
        self._section = section
        self.file = user.join('.cfg')
        self.config = configparser.ConfigParser()

        # Create config file
        if os.path.exists(self.file) == False:
            self._write()
        else:
            self._read()

        # Create section if missing
        if section not in self.config:
            self.config[str(section)] = {}
            self._write()

            
        # Root
        global __root__
        __root__['config'] = self

    def _read(self):
        with self.user.open('.cfg') as configfile:
            self.config.read_string(configfile.read())

    def _write(self):
        with self.user.open('.cfg', 'w') as configfile:
            self.config.write(configfile)

    def section(self, name:str):
        """
        The section in the config

        Arguments
        ---
        `name` - The name of the section.
        """
        return Config(self.user, name)

    def exists(self, key: str) -> bool:
        """
        Checks if the key is already defined
        
        Arguments
        ---
        `key` - The key to check.

        Returns
        ---
        `True` - Exists

        `False` - Does not exist
        """
        return str(key) in self.config.keys()

    def registerItem(self, key:str, default=None, datatype=None, title: str = None, description: str = None, from_: float = None, to: float = None):
        """
        Sets the value of the pair identified by key to value, creating a new key/value pair if none existed for key previously.

        Arguemnts
        ---
        `key` - The key to set

        `default` - The fallback value to use.

        `datatype` - The datatype to use for this value.

        `title` - Title of this option.

        `description` - Description about this option.

        `from_` - The minimum allowed value.

        `to` - The maximum allowed value.
        """
        self.registry[str(key)] = {'title': title, 'description': description, 'datatype': datatype, 'from_': from_, 'to': to}
        try: self.config.get('DEFAULT',key)
        except configparser.NoOptionError:
            self.config.set('DEFAULT',str(key), str(default))
            self._write()
        return self

    def unregisterItem(self, key:str):
        """
        Removes this item from the registry
        
        Arguments
        ---
        `key` - The key to remove
        """
        return self.registry.pop(key)

    def setItem(self, key: str, value):
        """
        Sets the value of the pair identified by key to value, creating a new key/value pair if none existed for key previously.

        Arguemnts
        ---
        `key` - The key to set

        `value` - The value of the key to set.
        """
        # Validate
        self.config.set(self._section, str(key), str(value))
        self._write()
        return self
    set = setItem

    def getItem(self, key: str, default=None):
        """
        Returns the current value associated with the given key, or null if the given key does not exist.

        Arguments
        ---
        `key` - The key/value pair to get.

        `default` - The value to return if the option cannot be found.
        """
        try: return self.config.get(self._section, str(key))
        except configparser.NoOptionError: return default
    get = getItem

    def removeItem(self, key: str) -> bool:
        """
        Removes the key/value pair

        Arguments
        ---
        `key` - The key/value pair to remove.
        """
        result = self.config.remove_option(self._section, str(key))
        self._write()
        return result
    remove = removeItem

class Cache():
    def __init__(self, id:str=None, user:User=None, root_path:str=None):
        """
        Cache any file.

        Methods
        ---
        exists, key, add_file, add_directory, remove_file, get_file
        """
        global __root__
        if id is None: id = len(__root__['cache'])
        self.id = id

        if user is None: user = getUser()
        self.user = user

        if root_path is None: root_path = os.path.expanduser('~')
        self.root_path = root_path.replace('\\', '/')

        self.index_path = user.join('.cache', 'indexes', str(self.id)+'.json')
        self.objects_path = user.join('.cache', 'objects')
        self.objects = {}
        # Create
        if user.exists(self.index_path)==False:
            os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
            self._write_index()

        # Open index
        self._read_index()

        __root__['cache'].append(self)

    def _cache_path(self, hash:str):
        return self.user.join('.cache', 'objects', hash[0:2], hash)

    def _read_index(self):
        with open(self.index_path, 'r') as r:
            objs = json.load(r).get('objects')
            if objs!=None: self.objects = objs

    def _write_index(self):
        obj = {"objects": self.objects}
        with open(self.index_path, 'w') as w: w.write(json.dumps(obj))

    def exists(self, *path:str) -> bool:
        """
        Checks if the file is already cached
        
        Arguments
        ---
        `path` - Path to test.

        Returns
        ---
        `True` - Cached

        `False` - Not cached
        """
        fp = self.key(*path)
        return fp in self.objects

    def key(self, *path) -> str:
        """
        Returns the index key from the path
        
        Arguments
        ---
        `path` - The full path to the file.
        """
        rep = os.path.join(*path).replace('\\', '/').replace(self.root_path, '')
        return re.sub(r'^[a-zA-Z]:', '', rep)

    def add_file(self, *path:str, rewrite:bool=False):
        """
        Add file to cache
        
        Arguments
        ---
        `path` - The file to cache

        `rewrite` - When true it will re-cache this file even if its already cached.
        """
        fp = os.path.join(*path)
        if os.path.exists(fp) and os.path.isfile(fp):
            hash = uuid.uuid4().hex
            if self.exists(fp) and rewrite:
                key = self.key(fp)
                hash = self.objects[key]['hash']

            if self.exists(fp)==False or rewrite:
                cache_path = self._cache_path(hash)
                # Copy file
                with open(fp, 'rb') as rb: dat = rb.read()
                os.makedirs(os.path.dirname(cache_path), exist_ok=True)
                with open(cache_path, 'wb') as wb: wb.write(dat)
                # Add file to index
                key = self.key(fp)
                self.objects[str(key)] = {"hash": hash, "size": os.path.getsize(fp)}
                self._write_index()
        else: raise CacheError(f"No such file: '{fp}'")
        return self

    def add_directory(self, *path:str, rewrite:bool=False):
        """
        Add all files in directory to cache.
        
        Arguments
        ---
        `path` - The directory to cache

        `rewrite` - When true it will re-cache this directory even if its already cached.
        """
        p = os.path.join(*path)
        if os.path.exists(p) and os.path.isdir(p):
            for file in os.listdir(p):
                fp = os.path.join(p, file)
                if os.path.isfile(fp): self.add_file(fp, rewrite=rewrite)
                else: self.add_directory(fp, rewrite=rewrite)
        else: raise CacheError(f"No such directory: '{os.path.join(*path)}'")
        return self

    def remove_file(self, *path):
        """
        Delete a file from cache.

        Arguments
        ---
        `path` - The file to delete from cache.
        """
        key = self.key(*path)
        index = self.objects.get(key)
        if index is not None:
            cache_path = self._cache_path(index['hash'])
            os.remove(cache_path)
            del self.objects[key]
            self._write_index()
        else: raise CacheError(f"No such file: '{os.path.join(*path)}'")
        return self
    
    def get_file(self, *path) -> str:
        """
        Returns a temp file path.

        Arguments
        ---
        `path` - The file to get from cache.
        """
        key = self.key(*path)
        index = self.objects.get(key)
        if index is not None:
            fp = self._cache_path(index['hash'])
            # Make sure filesize matches
            if index.get('size') == os.path.getsize(fp):
                suffix = os.path.splitext(key)[1]
                tmp = tempfile.NamedTemporaryFile(suffix=suffix,delete=False)
                global __temp__
                __temp__.append(tmp)
                with open(fp, 'rb') as rb: tmp.write(rb.read())
                return tmp.name
            raise CacheError(f"File has been modified or is corrupt: '{fp}'")
        raise CacheError(f"No such file: '{os.path.join(*path)}'")

def _cleanup():
    # destroy sessionStorage
    stores = getSessionStorage(False)
    if stores is not None:
        for store in stores: store.destroy()

    # Delete temp files
    global __temp__
    for tmp in __temp__:
        tmp.close()
        os.unlink(tmp.name)

atexit.register(_cleanup)

def getUser(create: bool=True) -> User|None:
    """"
    Returns the root user. If not defined it will create a user

    Arguments
    ---
    `create` - If no user can be found create one.
    """
    if __root__.get('user') is not None:
        return __root__['user']
    if create: return User()
    return None

def getConfig(create: bool=True) -> Config|None:
    """
    Returns the root config. If not defined it will create the config

    Arguments
    ---
    `create` - If no config can be found create one.
    """
    if __root__.get('config') is not None:
        return __root__['config']
    if create: return Config()
    return None

def getSessionStorage(create: bool=True) -> list[sessionStorage]|None:
    """
    Returns the root session storage. If not defined it will create one

    Arguments
    ---
    `create` - If no storage can be found create one.
    """
    if __root__.get('sessionStorage') is not None and len(__root__['sessionStorage'])>=1:
        return __root__['sessionStorage']
    if create: return sessionStorage()
    return None

def getCache(create:bool=True) -> list[Cache]|None:
    """
    Returns the root cache. If not defined it will create one.

    Arguments
    ---
    `create` - If no cache can be found create one.
    """
    if __root__.get('cache') is not None and len(__root__['cache'])>=1:
        return __root__['cache']
    if create: return Cache()
    return None

def getLocalStorage(create: bool=True) -> localStorage|None:
    """
    Returns the root local storage. If not defined it will create one

    Arguments
    ---
    `create` - If no storage can be found create one.
    """
    if __root__.get('localStorage') is not None:
        return __root__['localStorage']
    if create: return localStorage()
    return None
