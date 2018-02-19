"""
7セグディスプレイをコントロールするための関数群


Author:  Atsushi Shibata
         shibata@m-info.co.jp
Licence: MIT

Copyright (c) 2017 Atsushi Shibata
"""
import time

__all__ = ['start', 'turn_on', 'turn_off', 'sleep']


def prepare():
    """
    7セグディスプレイの準備をする
    Adafruitsベースのクラスをインポートしてみる
    例外が出たらJavaScriptベースのクラスを使う
    生成したクラスインスタンスを戻り値として返す
    """

    # 7セグディスプレイをコントロールするためのクラスインスタンス
    
    display = None
    
    try:
        # AFSevenSegmentをインポート
        from .AFSevenSegment import AF_7segdisplay
        # インスタンスを生成
        display = AF_7segdisplay()
        # 7セグディスプレイが使えるかどうかを確認
        if not display.check_availability():
            # 7セグディスプレイが使えなかったので，displayをNoneに
            display = None
    except ImportError:
        # Raspberry Piでなく，Win/Macでこのモジュールを使っている場合
        pass
    
    # もしdisplayがNoneなら，JavaScriptベースのインスンタスを生成
    if display is None:
        from .JSSevenSegment import JS_7segdisplay
        display = JS_7segdisplay()

    return display

# 7セグディスプレイコントロール用のインスタンスを生成
display = prepare()

# 7セグディスプレイコントロール用の関数

def start():
    """
    7セグディスプレイを全ての桁を消灯した状態で初期化
    """
    display.init_display()


def turn_on(position):
    """
    7セグディスプレイのLEDを個別に点ける
    positionに値を与えて，位置を指定する
    点灯済みのLEDを指定してもなにも起こらない
    右の桁からはじめて，0から7までで1つの桁のAからDPまでを
    指定する
    8が二桁目のA，35までの数値を指定する
    """
    display.turn_on(position)


def turn_off(position):
    """
    7セグディスプレイのLEDを個別に消す
    positionの扱いはturn_on()と同じ
    消灯済みのLEDを指定してもなにも起こらない
    """
    display.turn_off(position)


def sleep(duration):
    """
    指定の時間待つ
    time.sleep()を呼び出す
    """
    time.sleep(duration)

