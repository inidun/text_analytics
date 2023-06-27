#!/bin/bash

echo "Upgrading humlab-inidun PyPI package"
sudo pip install humlab-inidun --upgrade

echo "Refreshing notebooks..."
mkdir -p /home/jovyan/tmp

cd /home/jovyan/tmp

git clone https://github.com/inidun/text_analytics.git
rm -rf /home/jovyan/work/text_analytics/notebooks
mv /home/jovyan/tmp/text_analytics/notebooks /home/jovyan/work/text_analytics/

rm -rf /home/jovyan/tmp

echo "Done!"
