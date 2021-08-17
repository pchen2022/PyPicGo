
import sys
from pypicgo.core.config import Settings
from pypicgo.core.execute import create_uploader

def action():
    argv = sys.argv
    settings = Settings()
    uploader = settings.uploader_class
    uploader_config = settings.uploader_config
    plugins = settings.plugins
    with create_uploader(uploader, uploader_config, plugins) as uploader:
        files = argv[1:]
        for filepath in files:
            uploader.do(filepath)

if __name__ == '__main__':
    action()