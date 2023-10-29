# PyBox
A perfectly asynchronous DisBox API framework.
## How to install
- install this package with pip (later)
```sh
pip install pybox
```
- import to your Python project
```python
from pybox import PyBox

pb_client = PyBox(your_webhook_url_here)
```
## How to use
### For example, you can get information about any file by id or file's name.
```python
import asyncio

async def main():
  print(await pb_client.get_file_info(10704, "test folder"))

if __name__ == "__main__":
  asyncio.run(main())
```
Output:
```
{
  'id': 10704,
  'parent_id': 10636,
  'name': 'test_image.jpg',
  'type': 'file',
  'size': 48367,
  'content': ['1164839406260203542'],
  'created_at': '2023-10-20T08:15:55.292Z',
  'updated_at': '2023-10-26T17:31:29.159Z'
}
```
### Or if you want to download something
```python
import asyncio

async def main():
  await pb_client.download_file(10704, "test folder")

if __name__ == "__main__":
  asyncio.run(main())
```
Output:
```
[FILE] test_image.jpg file is successfully downloaded! (47.23 KB)
```

Other examples in `examples` directory (not now). You can check it.
## Todo
- upload_file & upload_folder
- delete_file & delete_folder
- rename_file & rename_folder
