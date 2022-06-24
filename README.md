# ncmDumper
解锁网易云ncm文件

## 特色
- 使用多线程进行解锁，速度更快

## 使用
在音乐目录下运行代码，将自动解锁该目录下的所有ncm文件，并存放在`./unlock`目录下

#### 快速使用

下载 `Latest Release` 中的可执行文件，将其放在存放 `ncm` 文件的目录下，然后运行应用即可开始解锁

解锁后的音频文件存放在 `./unlock` 目录下

------



## 注意

你可以使用release中提供的exe文件运行，也可以直接使用源代码文件运行程序

- 使用源代码文件时，请确保你的控制台运行目录与待解锁文件目录相同
- 在使用前，请安装`pycryptodome`，这是必须的，如下：
```shell
pip install pip -U
pip install pycryptodome
```
- 运行：
```shell
cd /.../你的ncm文件存放目录
python3 /.../项目目录/ncmdump.py
```
