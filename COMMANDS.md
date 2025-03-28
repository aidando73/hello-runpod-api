```bash
source ~/miniconda3/bin/activate && conda create --prefix ./env python=3.10
source ~/miniconda3/bin/activate && conda activate ./env
pip install -r requirements.txt

python -m playwright install chromium

cp sample.envrc .envrc
cursor .envrc
```



Runpod watcher:
```
cat /var/log/cloud-init-output.log

vim /var/log/runpod-watcher.log

sudo systemctl status runpod-watcher


```