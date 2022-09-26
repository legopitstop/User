import setuptools

with open('README.md') as f:
    long_description = f.read()

required_modules = ["requests"]

setuptools.setup(
    name='UserFolder',
    version='1.1.1',
    author='Legopitstop',
    description='This library allows you to write and save files to the users folder. Useful for when you convert this script to a onefile exe program.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/legopitstop/UserFolder/',
    packages=setuptools.find_packages(),
    install_requires=required_modules,
    license='MIT',
    keywords=['filemanagement', 'user folder', 'easy'],
    author_email='officiallegopitstop@gmail.com',
    classifiers=[
        'Development Status :: 5 - Production/Stable', # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3.9',
    ],
    python_requires='>=3.6'
)