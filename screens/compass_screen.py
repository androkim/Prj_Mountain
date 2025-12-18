# screens/compass_screen.py
from kivymd.uix.screen import MDScreen
from kivy.properties import NumericProperty
from kivymd.app import MDApp
from kivy.clock import Clock

# plyer 라이브러리의 compass 모듈 임포트
# 안드로이드에서는 sensors 모듈을 통해 Compass 기능을 사용할 수 있습니다.
from plyer import compass, uniqueid # uniqueid는 에러 체크용


class CompassScreen(MDScreen):
    name = "compass_screen"
    current_azimuth = NumericProperty(0) # 현재 방위각 (0~360도)
    _compass_running = False # 나침반 센서가 현재 실행 중인지 여부

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print("DEBUG: CompassScreen __init__ called.")

    def on_enter(self):
        # 화면에 진입할 때 나침반 센서를 시작합니다.
        print("DEBUG: CompassScreen on_enter called. Starting compass.")
        self.start_compass()

    def on_leave(self):
        # 화면에서 나갈 때 나침반 센서를 중지합니다.
        print("DEBUG: CompassScreen on_leave called. Stopping compass.")
        self.stop_compass()

    def start_compass(self):
        if self._compass_running:
            return

        try:
            # uniqueid.id은 임시로 센서 기능 확인용으로도 사용
            # 실제 compass 센서는 compass.enable()
            if compass.status == 'ready':
                compass.enable()
                self._compass_running = True
                Clock.schedule_interval(self.get_compass_data, 1/30.) # 30fps로 업데이트
                app = MDApp.get_running_app()
                app.show_toast("나침반 센서 시작", 1)
                print("DEBUG: Compass sensor enabled.")
            else:
                app = MDApp.get_running_app()
                app.show_toast("나침반 센서 사용 불가", 2)
                print(f"ERROR: Compass sensor not available. Status: {compass.status}")
                self.stop_compass() # 센서 사용 불가 시 중지
        except Exception as e:
            app = MDApp.get_running_app()
            app.show_toast(f"나침반 센서 오류: {e}", 3)
            print(f"ERROR: Failed to enable compass sensor: {e}")
            self.stop_compass() # 오류 시 중지


    def stop_compass(self):
        if not self._compass_running:
            return

        try:
            compass.disable()
            self._compass_running = False
            Clock.unschedule(self.get_compass_data)
            app = MDApp.get_running_app()
            app.show_toast("나침반 센서 중지", 1)
            print("DEBUG: Compass sensor disabled.")
        except Exception as e:
            app = MDApp.get_running_app()
            app.show_toast(f"나침반 센서 중지 오류: {e}", 3)
            print(f"ERROR: Failed to disable compass sensor: {e}")


    def get_compass_data(self, dt):
        """ 나침반 센서 데이터를 가져와 UI를 업데이트합니다. """
        try:
            # compass.orientation은 (x, y, z) 형태의 튜플 반환 (x: 방위각, y: 피치, z: 롤)
            # 여기서는 방위각(heading)만 사용합니다.
            if compass.orientation is not None:
                # 방위각은 0~360도 사이의 값을 가지며, 북쪽이 0도입니다.
                self.current_azimuth = compass.orientation[0]
            else:
                print("DEBUG: Compass orientation data is None.")
        except Exception as e:
            print(f"ERROR: Error getting compass data: {e}")
            self.stop_compass() # 오류 발생 시 센서 중지

    def _go_back_to_main_screen(self):
        app = MDApp.get_running_app()
        app.root.current = "main_screen"