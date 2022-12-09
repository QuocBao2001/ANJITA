# ANJITA - Cooking recipes suggester

## Requirements
<br/>

Make new dir in this project and name it `weight`.

Go to 
```shell
https://drive.google.com/drive/folders/15PlXWkFheuBxJOYkwm9iS_aZCcr8L0A7
```
Download `yolov5l.pt` into `weight` folder.

We many thanks to repo author of `https://github.com/lannguyen0910/food-recognition` for providing weight file.

Try to create new anaconda enviroments with ```python>=3.8```.

install flask:

```shell
pip  install flask
```

install pymongo
```shell
pip install pymongo
```

Then install `pytorch` that match your cuda if you have, if not you can use torch for cpu (`PyTorch>=1.7`).

Install yolov5 dependencies: 

```shell 
pip install -qr https://raw.githubusercontent.com/ultralytics/yolov5/master/requirements.txt  # install dependencies
```

if something missing, try to read error and figure out name of missing packages. You can refer to my pip requirements.txt or anaconda enviroment.yml to find out.

<br/>
<br/>

## User guide
<br/>

- Step 1: acctive your conda enviroments.
- Step 2: run `python server.py`.
- Step 3: go to `0.0.0.0:5000` and try to upload.