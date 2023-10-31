import httpx
import asyncio
import aiofiles
import hashlib
import os
import random

from datetime import datetime

from .utils import WebhookClient
from .utils import FileUtil

SERVER_URL = "https://disboxserver.azurewebsites.net"

class DisBox():
    def __init__(self, webhook_url: str) -> None:
        """
        It's a simple DisBox client written in Python.
        
        Parameters:
        -----------
            webhook_url (``str``):
                A URL of your Discord Webhook.
        """
        self.webhook_client = WebhookClient(webhook_url)
        self.webhook_id = hashlib.sha256(bytes(webhook_url, "utf-8")).hexdigest()
        self.file_util = FileUtil()

    async def __get_data(self, from_folder: str = None):
        async with httpx.AsyncClient() as client:
            res = await client.get(f"{SERVER_URL}/files/get/{self.webhook_id}")
            res = res.json()["children"]

            if from_folder:
                try:
                    folders = from_folder.split("/")
                    for folder in folders:
                        res = res[folder]["children"]
                except KeyError as err:
                    raise KeyError(f"Invalid folder name: {err}.") from None
            
            await client.aclose()

            return res
    
    async def get_file_info(self, file: int | str, from_folder: str = None) -> dict:
        """
        Returns an information about file.

        Parameters:
        -----------
            file (``int`` || ``str``):
                An ID or name of your file.

            from_folder (``str``, *optional*):
                A path to your folder with files.
        """
        if type(file) not in [str, int]:
            raise TypeError("Invalid type of 'file' argument.")

        if type(from_folder) != str and from_folder != None:
            raise TypeError("Invalid type of 'from_folder' argument.")

        data = await self.__get_data(from_folder)

        match file:
            case int():
                for key in data:
                    if data[key]["id"] == file and data[key]["type"] == "file":
                        data = data[key]
                        break
                else:
                    raise Exception(f"Can't find a file with ID: {file}.")
            case str():
                try:
                    if data[file]["type"] == "file":
                        data = data[file]
                    else:
                        raise Exception(f"{file} is not a file.")
                except KeyError as err:
                    raise KeyError(f"Invalid file name: {err}.") from None

        data["content"] = data["content"].strip("[]").replace("\"", "").split(",")

        return data

    async def get_all_files(self, from_folder: str = None) -> list[dict]:
        """
        Returns a list of all files.

        Parameters:
        -----------
            from_folder (``str``, *optional*):
                A path to your folder with files.
        """
        if type(from_folder) != str and from_folder != None:
            raise TypeError("Invalid type of 'from_folder' argument.")

        data = await self.__get_data(from_folder)

        del_folders = []
        for key in data:
            if data[key]["type"] == "directory":
                del_folders.append(key)
            else:
                data[key]["content"] = data[key]["content"].strip("[]").replace("\"", "").split(",")

        for folder in del_folders:
            del data[folder]

        return [*data.values()]

    async def get_random_file(self, from_folder: str = None) -> dict:
        """
        Returns a dictionary of random file information.

        Parameters:
        -----------
            from_folder (``str``, *optional*):
                A path to your folder with files.
        """
        files = await self.get_all_files(from_folder)
        return files[random.randint(0, len(files) - 1)]

    async def download_file(self, file: int | str, from_folder: str = None, to_folder: str = None, is_redownload: bool = False) -> None:
        """
        Downloads a file.

        Parameters:
        -----------
            file (``int`` || ``str``):
                An ID or name of your file.

            from_folder (``str``, *optional*):
                A path to your folder with files.

            to_folder (``str``, *optional*):
                A path to place your file.

            is_redownload(``bool``, *optional*):
                If the file exists, then redownloads it (if ``is_redownload`` enabled).
        """
        if type(to_folder) != str and to_folder != None:
            raise TypeError("Invalid type of 'to_folder' argument.")

        if type(is_redownload) != bool and is_redownload != None:
            raise TypeError("Invalid type of 'is_redownload' argument.")

        file_info = await self.get_file_info(file, from_folder)
        file_path = file_info["name"]

        if to_folder:
            file_path = f"{to_folder}/{file_info['name']}"
            os.makedirs(to_folder, exist_ok=True)

        if is_redownload and os.path.exists(file_path):
            os.remove(file_path)

        if not os.path.exists(file_path):
            async with aiofiles.open(file_path, "ab") as f:
                for content in file_info["content"]:
                    await f.write(await self.webhook_client.get_attachment_bytes(content))
                print(f"[FILE] {file_info['name']} file is successfully downloaded! ({self.file_util.convert_bytes(file_info['size'])})")
                await f.close()
        else:
            print(f"[FILE] {file_info['name']} is already exists.")

    async def download_folder(self, folder: str, is_redownload: bool = False) -> None:
        """
        Downloads a folder with files.

        Parameters:
        -----------
            folder (``str``):
                The folder which you want to download.

            is_redownload(``bool``, *optional*):
                If the file exists, then redownloads it (if ``is_redownload`` enabled).
        """
        if type(folder) != str:
            raise TypeError("Invalid type of 'folder' argument.")

        if type(is_redownload) != bool and is_redownload != None:
            raise TypeError("Invalid type of 'is_redownload' argument.")

        os.makedirs(folder, exist_ok=True)
        
        tasks = []
        for file in await self.get_all_files(folder):
            task = asyncio.create_task(self.download_file(file["name"], folder, folder, is_redownload))
            tasks.append(task)
            await asyncio.sleep(0.35)

        await asyncio.gather(*tasks)

    async def __update_file(self, file_id: int, changes: dict) -> None:
        if type(changes) != dict:
            raise TypeError("Invalid type of 'changes' argument.")

        changes["updated_at"] = f"{datetime.now().isoformat()[:-3]}Z"

        async with httpx.AsyncClient() as client:
            res = await client.post(f"{SERVER_URL}/files/update/{self.webhook_id}/{file_id}", json=changes, headers={"Content-Type": "application/json"})

            if res.status_code != 200:
                raise Exception("Invalid key in 'changes' argument.")

            await client.aclose()

    # IN DEV
    def rename_file(self, file: int | str, new_name: str, from_folder: str = None) -> None:
        """
        Renames a file.

        Parameters:
        -----------
            file (``int`` || ``str``):
                An ID or name of your file.

            new_name (``str``):
                A new name for your file.

            from_folder (``str``, *optional*):
                A path to your folder with files.
        """
        if type(new_name) != str or not new_name:
            raise TypeError("Invalid type of 'new_name' argument.")

        file_info = self.get_file_info(file, from_folder)

        try:
            if self.get_file_info(new_name, from_folder):
                raise Exception("This file name is already exist.")
        except KeyError:
            self.__update_file(file_info["id"], { "name": new_name })