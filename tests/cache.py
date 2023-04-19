import UserFolder
import os
from PIL import Image

user = UserFolder.User('_test')

PATH = os.path.dirname(os.path.realpath(__file__))

cache = UserFolder.Cache()
cache.add_directory(os.path.join(PATH))

file = cache.get_file('/Documents/GitHub/Python/UserFolder/assets/example1.png')
print(file)

img = Image.open(file)
img.show()