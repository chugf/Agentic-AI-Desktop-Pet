from threading import Thread

from . import actions
from . import adult

from . import webapi
from . import webui

Thread(target=webapi.run).start()
