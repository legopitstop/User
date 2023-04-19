import UserFolder
import uuid


user = UserFolder.User('_test')

# localStorage
ls = UserFolder.localStorage()
if ls.exists('key') == False:
    ls.setItem('key', uuid.uuid4().hex)
print(ls.getItem('key'))

# sessionStorage - Creates a new session storage when the script first starts.
ss = UserFolder.sessionStorage()
ss.setItem('key', uuid.uuid4().hex)
print(ss.getItem('key'))


# Clear session storage when script has been closed.