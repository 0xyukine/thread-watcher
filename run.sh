sudo docker build -t threadwatcher .
sudo docker run -it -v ~/code/thread-watcher/src:/app threadwatcher bash
