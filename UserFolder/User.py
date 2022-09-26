"""This library allows you to read and write files to the current user folder. Useful for when you convert this script to a onefile exe program."""
import os
import requests
import tarfile
import zipfile
import yaml
import re
import plyer
import uuid
import configparser

__version__ = '1.1.0'

class PackageNotFoundError(Exception): pass
class UnsupportedArchiveError(Exception): pass

class TrackEvent():
    def __init__(self, member:zipfile.ZipInfo, count:int, total:int):
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
    def __init__(self,id:str,setupcommand=None):
        """
        Will create the file path inside the Users folder. Your id should be a unique string just for your script.
        
        Arguments
        ---
        `id` - The uuid of the project. Recomended to use a backwords url: 'com.username.project_name'

        `setupcommand` - Runs the first time the program has ever ran on this user. This can be used to install any required files.

        Methods
        ---
        join, uninstall, exists, open, listdir, show,download, unarchive
        """
        self._setup = setupcommand
        def trim(s:str): return re.sub(r'[^a-z._\-0-9]','',str(s).lower().strip().replace(' ','_'))
        self.id = trim(id)
        ROOT = os.path.join(plyer.storagepath.get_home_dir(), '.python')
        self.path = os.path.join(ROOT,self.id)

        if os.path.isdir(self.path) == False:
            os.makedirs(self.path, exist_ok=True)
            # Call setup command
            self._setup(self)

    def join(self,*paths:str):
        """
        Join user path

        Arguments
        ---
        `paths` - A list of each folder in path
        """
        return os.path.join(self.path, *paths)
        
    def uninstall(self):
        """
        Will delete the scripts user folder.

        Arguments
        ---
        `paths` - A list of each folder in path

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
        except: return False
    
    def exists(self,*paths:str):
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
            if os.path.isfile(self.join(*paths)): return True
            else: return False
        except: return False

    def open(self,file:str,mode:str='r'):
        """
        Opens the file that is in the scripts user folder.

        Arguments
        ---
        `file` - A list of each folder in path

        `mode` - The mode to open this file in

        Returns
        ---
        TextIOWrapper - The contents of the file.

        `None` - Could not find the file.

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
        if mode=='w' or mode=='a':
            DIR = os.path.dirname(PATH)
            os.makedirs(DIR, exist_ok=True)
            try: return open(PATH,mode)
            except: return None
        else:
            try: return open(PATH,mode)
            except: return None

    def listdir(self,*paths:str):
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
        try: return os.listdir(self.join(*paths))
        except: return None
            
    def show(self,*paths:str):
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
        except: return False

    def get(self, *paths:str):
        """DEPRIVED: use .join() instead"""
        print('.get method is deprived! use .join instead')
        return self.join(*paths)

    def download(self,package:str,filename:str=None):
        """
        Download file from the web.
        
        Arguments
        ---
        `package` - The URL to the package to download.

        `filename` - The filename of the package
        """
        r = requests.get(package, allow_redirects=True)
        if filename==None:
            filename = os.path.basename(package)
        if r.status_code==200:
            open(self.join(filename), 'wb').write(r.content)
            return self
        else:
            raise PackageNotFoundError('Package returned status %s'%(r.status_code))

    def unarchive(self,src:str,dst:str=None, members:list=None, format:str=None, deletesrc:bool=True,trackcommand=None):
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

        Returns
        ---
        `True` - Successfully unarchived package.

        `False` - Failed to unarchive package

        """
        src = self.join(src)

        if dst==None: dst = self.path
        else: dst = self.join(dst)

        # Get format
        if format is None: # Auto detect format
            if src.endswith('.zip'): format='ZIP'
            elif src.endswith('.gz'): format='GZ'
        else: format = format.upper()

        if format=='ZIP':
            with zipfile.ZipFile(src,'r') as file:
                if members is None:  MEMBERS = file.namelist()
                else: MEMBERS = members
                total = len(MEMBERS)

                count=1
                for member in MEMBERS:
                    file.extract(member, dst)
                    event = TrackEvent(member, count, total)
                    if trackcommand!=None: trackcommand(event) 
                    count+=1

            if deletesrc: os.remove(src)
            return True

        elif format=='GZ':
            with tarfile.open(src) as file:
                if members is None: MEMBERS = file.getmembers()
                else: MEMBERS = members
                total = len(MEMBERS)

                count=1
                for member in MEMBERS:
                    event = TrackEvent(member, count, total)
                    if trackcommand!=None: trackcommand(event)
                    file.extract(member, dst)
                    count+=1

                file.close()
            if deletesrc: os.remove(src)
            return True
        else:
            raise UnsupportedArchiveError('Unsupported archive! Supported archive types: .zip, .gz')

class Storage():
    def __init__(self,user:User,filename:str):
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
        self.user = user
        self.file = user.join(filename)
        self.first = False
        # Create file
        if os.path.exists(self.file)==False:
            wrt = self.user.open(self.file, 'w')
            wrt.write('')
            wrt.close()
            self.first = True

        self.length = self.__len()

    def __len(self):
        opn = self.user.open(self.file,'r')
        data = yaml.load(opn, yaml.FullLoader)
        opn.close()
        if data!=None:
            count=0
            for i in data:
                count+=1
            return count
        else:
            return 0

    def getItem(self,key:str):
        """
        Returns the current value associated with the given key, or null if the given key does not exist.
        
        Arguments
        ---
        `key` - Get the value of the key
        """
        opn = self.user.open(self.file,'r')
        data = yaml.load(opn, yaml.FullLoader)
        opn.close()
        if data!=None:
            if str(key) in data:
                return data[str(key)]
            else: 
                raise KeyError(key)
        else:
            raise KeyError(key)

    def setItem(self,key:str, value:str):
        """
        Sets the value of the pair identified by key to value, creating a new key/value pair if none existed for key previously.

        Arguments
        ---
        `key` - The key to set

        `value` - The value of the key to set
        """
        opn = self.user.open(self.file,'r')
        data = yaml.load(opn, yaml.FullLoader)
        opn.close()

        if data!=None:
            data[str(key)] = value
        else:
            data = {}
            data[str(key)] = value

        wrt = self.user.open(self.file,'w')
        wrt.write(yaml.dump(data))
        wrt.close()

    def removeItem(self,key:str):
        """
        Removes the key/value pair with the given key, if a key/value pair with the given key exists.
        
        Arguments
        ---
        `key` - The key/value pair to remove.
        """
        opn = self.user.open(self.file,'r')
        data = yaml.load(opn, yaml.FullLoader)
        opn.close()

        if data!=None:
            if str(key) in data:
                del data[str(key)]
            else:
                raise KeyError(key)

            wrt = self.user.open(self.file,'w')
            wrt.write(yaml.dump(data))
            wrt.close()

    def clear(self):
        """
        Removes all key/value pairs, if there are any.
        """
        wrt = self.user.open(self.file,'w')
        wrt.write('')
        wrt.close()

    def key(self,index:int):
        """
        Returns the name of the nth key, or None if n is greater than or equal to the number of key/value pairs.

        Arguments
        ---
        `index` - The index in the store to get the key from.
        """
        opn = self.user.open(self.file,'r')
        data = yaml.load(opn, yaml.FullLoader)
        opn.close()
        if data!=None:
            # get all keys in a list
            keys=[]
            for k in data:
                keys.append(k)
            try:
                return keys[int(index)]
            except IndexError:
                return None
        else:
            return None

    def exists(self,key:str):
        """
        Checks if key/value pair exists

        Arguemnts
        ---
        `key` - The key to test for
        """
        try:
            self.getItem(key)
            return True
        except KeyError: return False

    def show(self):
        """
        Open the storage file
        """
        return os.startfile(self.file)

class localStorage(Storage):
    def __init__(self,user:User):
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

class sessionStorage(Storage):
    def __init__(self,user:User):
        """
        Simlar to localStorage but gets cleared everytime the program starts

        Arguments
        ---
        `user` - The User class for the session storage.

        Methods
        ---
        getItem, setItem, removeItem, clear, key, exists, show
        """
        super().__init__(user, '.session/%s.yaml'%(uuid.uuid4().hex))

class Config():
    def __init__(self, user:User, section:str=None):
        """
        General config file for program settings

        Arguments
        ---
        `user` - The User class for the config.

        `section` - Teh configs section. default value; DEFAULT

        Methods
        ---
        section, setItem, getItem, removeItem
        """
        self.user = user

        # Default section is the user id
        if section==None: self._section = self.user.id
        else: self._section = section
        self.file = user.join('.cfg')
        self.config = configparser.ConfigParser()

        # Create config file
        if os.path.exists(self.file)==False:
            self._write()
        else: self._read()

        # Create section if missing
        if section not in self.config:
            self.config[str(section)] = {}
            self._write()

    def _read(self):
        """Internal function"""
        with self.user.open('.cfg') as configfile:
            self.config.read_string(configfile.read())

    def _write(self):
        """Internal function"""
        with self.user.open('.cfg', 'w') as configfile:
            self.config.write(configfile)

    def section(self, name:str='DEFAULT'):
        """
        The section in the config
        
        Arguments
        ---
        `name` - The name of the section.
        """
        return Config(self.user, name)

    def setItem(self, key:str, value:str):
        """
        Sets the value of the pair identified by key to value, creating a new key/value pair if none existed for key previously.

        Arguemnts
        ---
        `key` - The key to set

        `value` - The value of the key to set.
        """
        self.config.set(self._section, str(key), value)
        self._write()

    def getItem(self, key:str):
        """
        Returns the current value associated with the given key, or null if the given key does not exist.

        Arguments
        ---
        `key` - The key/value pair to get.
        """
        return self.config.get(self._section, str(key))

    def removeItem(self, key:str):
        """
        Removes the key/value pair
        
        Arguments
        ---
        `key` - The key/value pair to remove.
        """
        result = self.config.remove_option(self._section, str(key))
        self._write()
        return result

def example():
    from time import sleep

    def progress(e: TrackEvent): # Print the current status.
        percent = int(e.percentage)
        done = int(e.percentage/10)*5
        fill = 10*5 - done

        if percent!=100: end='\r' # Print on same line until 100%
        else: end=None

        print('Progress: |{0}{1}| {2}% Complete'.format('█'*done, '-'*fill, percent), end=end)
        sleep(.5) # Slow down the progress so you can actually see the progress.

    def setup(u:User): # Download all required files and packages
        u.download('https://github.com/legopitstop/UserFolder/archive/refs/tags/v1.0.2.zip','package.zip')
        u.unarchive('package.zip', trackcommand=progress)

    user = User('_test', setup)

    # Config
    default = Config(user)
    default.setItem('my_option', "fallback") # set fallback value. If my_option is missing this key it will use this value.

    config = default.section('metadata')
    config.removeItem('my_option')
    config.setItem('my_option', 'Hello World') # Comment me out to see fallback value

    print('my_option =',config.getItem('my_option'))

    ls = localStorage(user)
    ss = sessionStorage(user)

    if ls.exists('version')==False:
        ls.setItem('version', __version__)
    
    print('version:',ls.getItem('version'))
    ss.setItem('key', 'test')

    print('Ready!')

    user.show()

if __name__ == '__main__':
    example()