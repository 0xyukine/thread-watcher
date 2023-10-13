import threadWatcher

tw = threadWatcher.ThreadWatcher()
print(tw.get_catalog("vt")[:5])
