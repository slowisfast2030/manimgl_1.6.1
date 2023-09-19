# 思考

## bubble
每种bubble无非就是一些点集，可以单独建立一份文件，里面有不同类型的bubble的点集

## alphabet creatures
每种生物的都是由3部分构成
- body
- eyeu
- mouth

#### eyes和mouth的类型
eyes和mouth有几种类型，可以读取不同类型的eyes和mouth，并将其保存为点集，存入文件

#### eyes和mouth的位置
不同字母的eyes和mouth的位置需要调整，可以新建一份文件，存入不同字母的eyes和mouth的位置
（body默认在ORIGIN）

## 文件
格式: yml

在AlphabetCreature类初始化的时候读入这份文件
```
bubble:
    speaking:
        points:
    thought:
        points:
eyes:
    plain:
    happy:
    sad:
mouth:
    plain:
    happy:
    sad:
alphabet:
    A:
        eyes_location:
        mouth_location:
    B:
        eyes_location:
        mouth_location:
    C:
        eyes_location:
        mouth_location:
    pi:
        eyes_location:
        mouth_location:
    mu:
        eyes_location:
        mouth_location:

```
