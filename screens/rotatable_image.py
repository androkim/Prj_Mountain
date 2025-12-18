# screens/rotatable_image.py
from kivy.uix.image import Image
from kivy.properties import NumericProperty

class RotatableImage(Image):
    """
    Kivy의 기본 Image 위젯을 상속받아 회전 각도를 제어할 수 있는 'angle' 속성을 추가한 위젯.
    """
    angle = NumericProperty(0) # 각도 값을 저장할 NumericProperty 추가