class FileUtil():
    def convert_bytes(self, bytes: int) -> str:
        file_size = 0
        pow = 1
        sizes = ["B", "KB", "MB", "GB"]

        while True:
            if bytes < 1024:
                file_size = bytes
                break
            if bytes / (1024 ** pow) < 1:
                break
            file_size = bytes / (1024 ** pow)
            pow += 1

        return f"{file_size:.2f} {sizes[pow - 1]}"