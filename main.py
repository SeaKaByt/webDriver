import rpa as r

from src.core.driver import BaseDriver

r.init(visual_automation=True)
d = BaseDriver()
r.click(d.home)