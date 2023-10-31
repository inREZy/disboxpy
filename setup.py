from setuptools import setup, find_packages

setup(
   name = 'disboxpy',
   version = '1.0.0',
   description = 'A perfectly asynchronous DisBox API framework.',
   long_description = open('README.md', 'r').read(),
   packages = find_packages(),
   author = 'inREZy',
   author_email = 'xardmax2000@gmail.com',
   url = 'https://github.com/inREZy/disboxpy',
   packages = ['disboxpy'],
   install_requires = ['httpx', 'asyncio', 'aiofiles', 'hashlib', 'os', 'random', 'datetime']
)
