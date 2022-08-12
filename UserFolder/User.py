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

class User():
    def __init__(self,id:str,setupcommand=None):
        """
        Will create the file path inside the Users folder. Your id should be a unique string just for your script.
        
        Attrubutes
        ---
        `id` - The uuid of the project. Recomended to use a backwords url: 'com.username.project_name'

        `setupcommand` - Runs the first time the program has ever ran on this user. This can be used to install any required files.
        """
        self._setup = setupcommand
        def trim(s:str): return re.sub(r'[^a-z._\-0-9]','',str(s).lower().strip().replace(' ','_'))
        ROOT = os.path.join(plyer.storagepath.get_home_dir(), '.python')
        self.path = os.path.join(ROOT,trim(id))

        if os.path.isdir(self.path) == False:
            os.makedirs(self.path, exist_ok=True)
            # Call setup command
            self._setup(self)

    def join(self,*paths:str):
        """
        Join user path
        """
        return os.path.join(self.path, *paths)
        
    def uninstall(self):
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
        except: return False
    
    def exists(self,*paths:str):
        """
        Checks if the file exists inside the scripts user folder.

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

        Returns
        ---
        list[str] - A list of all files that are currently inside the scripts user folder.

        `None` - Failed to list the directory
        """
        try: return os.listdir(self.join(*paths))
        except: return None
    list = listdir
            
    def show(self,*paths:str):
        """
        Opens the file in your devices default editor. If filename is undefined it will open the scripts user folder.

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
        return self.join(*paths)

    def download(self,package:str,filename:str=None):
        """Download file from the web."""
        r = requests.get(package, allow_redirects=True)
        if filename==None:
            filename = os.path.basename(package)
        if r.status_code==200:
            open(self.join(filename), 'wb').write(r.content)
            return self
        else:
            raise PackageNotFoundError('Package returned status %s'%(r.status_code))

    def unarchive(self,src:str,dst:str=None):
        """
        Unarchive a zip or gz file.
        
        Returns
        ---
        `True` - Successfully unarchived package.

        `False` - Failed to unarchive package

        """
        src = self.join(src)

        if dst==None: dst = self.path
        else: dst = self.join(dst)
        if src.endswith('.zip'):
            file = zipfile.ZipFile(src,'r')
            file.extractall(dst)
            file.close()
            os.remove(src)
            return True
        elif src.endswith('.gz'):
            file = tarfile.open(src)
            file.extractall(dst)
            file.close()
            os.remove(src)
            return True
        else:
            print('Unsupported file! supported file types: .zip, .gz')
            return False

class Storage():
    def __init__(self,user:User,filename:str):
        """Create a file to store key/value pairs."""
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
        """Returns the current value associated with the given key, or null if the given key does not exist."""
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
        """Sets the value of the pair identified by key to value, creating a new key/value pair if none existed for key previously."""
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
        """Removes the key/value pair with the given key, if a key/value pair with the given key exists."""
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
        """Removes all key/value pairs, if there are any."""
        wrt = self.user.open(self.file,'w')
        wrt.write('')
        wrt.close()

    def key(self,index:int):
        """Returns the name of the nth key, or None if n is greater than or equal to the number of key/value pairs."""
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
        """Checks if key/value pair exists"""
        try:
            self.getItem(key)
            return True
        except KeyError: return False

    def show(self):
        """Open the storage file"""
        return os.startfile(self.file)

class localStorage(Storage):
    def __init__(self,user:User):
        """General storage class. Allows you to store key/values in the user folder"""
        super().__init__(user, 'localStorage.yaml')

class sessionStorage(Storage):
    def __init__(self,user:User):
        """Simlar to localStorage but gets cleared everytime the program starts"""
        super().__init__(user, '.session/%s.yaml'%(uuid.uuid4().hex))

class Config():
    def __init__(self, user:User, section:str='DEFAULT'):
        """General config file for program settings"""
        self.user = user
        self._section = section
        self.file = user.get('.cfg')
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

    def section(self, name:str):
        """The section in the config"""
        return Config(self.user, name)

    def setItem(self, key:str, value:str):
        """Sets the value of the pair identified by key to value, creating a new key/value pair if none existed for key previously."""
        self.config.set(self._section, str(key), value)
        self._write()

    def getItem(self, key:str):
        """Returns the current value associated with the given key, or null if the given key does not exist."""
        return self.config.get(self._section, str(key))

    def removeItem(self, key:str):
        return self.config.remove_option(self._section, str(key))

def example():
    def setup(u:User): # Download all required files and packages
        print('Getting things ready for you!')
        u.download('https://github.com/legopitstop/UserFolder/archive/refs/tags/v1.0.2.zip','package.zip').unarchive('package.zip')

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