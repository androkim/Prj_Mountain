# main.py
# -*- coding: utf-8 -*-
import os
import json
import requests
from threading import Thread

# KivyMD 앱 및 UI 관련 임포트
from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.core.text import LabelBase, DEFAULT_FONT
from kivy.clock import Clock
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivy.metrics import dp

# Kivy의 EventDispatcher를 사용하여 화면 간 신호 전달 (프로그레스바 업데이트용)
from kivy.event import EventDispatcher
from kivy.properties import NumericProperty, StringProperty, ObjectProperty

from screens.rotatable_image import RotatableImage


# plyer.compass 임포트
try:
    from plyer import compass
except ImportError:
    compass = None # plyer 설치되지 않았거나 플랫폼 미지원 시 처리
    print("WARNING: 'plyer' module not found or compass sensor not supported. Compass feature will be disabled.")


# --- 필요한 Screen 클래스를 모두 임포트합니다. ---
# 각 화면에 해당하는 .py 파일 (예: screens/main_screen.py)에 해당 클래스가 정의되어 있어야 합니다.
from screens.main_screen import MainScreen
from screens.announce_main_screen import AnnounceMainScreen
from screens.settings_main_screen import SettingsMainScreen
from screens.compass_screen import CompassScreen
# --- 기타 화면들도 여기에 임포트해야 합니다 ---
# from screens.information_main_screen import InformationMainScreen
# from screens.mypage_main_screen import MyPageMainScreen
# from screens.tracking_main_screen import TrackingMainScreen


# 앱 화면 크기 설정
Window.size = (360, 640)


# --- 한글 폰트 등록 ---
font_path = os.path.join(os.path.dirname(__file__), 'fonts', 'NotoSansKR-Regular.ttf')
if os.path.exists(font_path):
    LabelBase.register(name="NotoSansKR", fn_regular=font_path)
    LabelBase.register(DEFAULT_FONT, font_path) # Kivy의 기본 폰트도 NotoSansKR로 지정
    print(f"DEBUG: Korean font registered as NotoSansKR and DEFAULT_FONT: {font_path}")
else:
    print(f"WARNING: Korean font not found at {font_path}. Fallback to default Kivy font.")
    print("WARNING: Please ensure 'NotoSansKR-Regular.ttf' is in a 'fonts' folder next to main.py.")


# --- API 데이터 업데이트 상태를 관리할 Dispatcher 클래스 ---
class ApiUpdateProgress(EventDispatcher):
    progress_value = NumericProperty(0) # 0.0 ~ 1.0 (0~100%)
    progress_text = StringProperty("준비 중...")
    is_running = NumericProperty(0) # 0: 대기, 1: 실행 중, 2: 완료, -1: 오류
    total_items_to_fetch = NumericProperty(0) # 총 가져올 아이템 수
    current_items_fetched = NumericProperty(0) # 현재 가져온 아이템 수

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.register_event_type('on_progress_update')

    def on_progress_update(self, *args):
        pass


class AlpineApp(MDApp):
    FOREST_API_KEY = "76586aad2943c239fec03cf5a33319ec3005db010e91f6902772cd854d1a1c3a"
    MOUNTAIN_INFO_API_URL = "https://apis.data.go.kr/1400000/service/cultureInfoService2/mntInfoOpenAPI2"
    API_PAGE_SIZE = 100
    announcements_data = []
    toast_dialog = None

    api_update_progress = ApiUpdateProgress()
    
    # 나침반 방위각(UI 회전용 각도)을 저장할 속성 추가 (Kivy Rotate canvas instruction에 적합한 값)
    compass_azimuth = NumericProperty(0)
    
    # 나침반 센서가 활성화되었는지 확인하는 속성
    compass_sensor_enabled = ObjectProperty(None) # plyer.compass 객체를 저장

    def build(self):
        self.title = "걷고 오르고"
        print("DEBUG: Loading menu_screen.kv as the root UI.")
        
        # --- [중요!] menu_screen.kv 파일을 로드합니다. ---
        self.root = Builder.load_file("menu_screen.kv")
        
        print("DEBUG: menu_screen.kv loaded. Root is:", self.root)
        
        # 앱의 루트 위젯이 로드된 후, 나침반 각도 프로퍼티의 변화를 감지하도록 바인딩
        # self.compass_azimuth가 변경되면 _update_compass_image_angle을 호출합니다.
        self.bind(compass_azimuth=self._update_compass_image_angle)
        
        return self.root

    def on_start(self):
        Clock.schedule_once(self._post_build_init, 0)
        # API 업데이트 진행 상황 이벤트 리스너 등록
        self.api_update_progress.bind(
            progress_value=self._update_progress_ui,
            progress_text=self._update_progress_ui,
            is_running=self._update_progress_ui,
            total_items_to_fetch=self._update_progress_ui,
            current_items_fetched=self._update_progress_ui
        )
        
        # 나침반 센서 활성화 및 이벤트 바인딩
        if compass:
            try:
                compass.enable()
                self.compass_sensor_enabled = compass
                compass.bind(on_compass_change=self.on_compass_data)
                print("DEBUG: Compass sensor enabled and bound.")
            except Exception as e:
                print(f"ERROR: Could not enable compass sensor: {e}")
                self.compass_sensor_enabled = None
        else:
            print("WARNING: Plyer Compass module not available or platform not supported.")

    def on_stop(self):
        # 앱 종료 시 나침반 센서 비활성화
        if self.compass_sensor_enabled:
            compass.disable()
            print("DEBUG: Compass sensor disabled.")

    def on_compass_data(self, *args, **kwargs):
        """나침반 센서 데이터가 변경될 때 호출됩니다."""
        azimuth = 0
        if args and isinstance(args[0], (int, float)):
            azimuth = float(args[0])
        elif 'azimuth' in kwargs and isinstance(kwargs['azimuth'], (int, float)):
            azimuth = float(kwargs['azimuth'])
        
        # Kivy의 Rotate canvas instruction은 양수 각도를 반시계 방향으로 회전합니다.
        # 센서 azimuth는 시계 방향으로 증가하는 값(0~360)입니다.
        # 나침반 아이콘이 자북(0도)을 가리키는 것처럼 보이게 하려면,
        # 센서값이 N도를 가리킬 때 아이콘을 -N도 회전시켜야 합니다.
        self.compass_azimuth = (-azimuth) % 360 

        # DEBUG: print(f"DEBUG: Compass Azimuth: {azimuth:.2f}° (Kivy Rotate Angle: {self.compass_azimuth:.2f}°)")

    # --- [새로 추가] 나침반 이미지 각도 업데이트 메서드 ---
    def _update_compass_image_angle(self, instance, value):
        """
        app.compass_azimuth 프로퍼티가 변경될 때 호출되며,
        상단 앱바의 나침반 이미지 각도를 업데이트합니다.
        """
        # root.ids로 menu_screen.kv에서 부여한 ID를 찾아 위젯에 접근합니다.
        if self.root and 'top_app_bar_compass_image' in self.root.ids:
            self.root.ids.top_app_bar_compass_image.angle = value
            # print(f"DEBUG: Compass image angle updated to: {value:.2f}°")
        else:
            print("WARNING: 'top_app_bar_compass_image' not found in self.root.ids. Check menu_screen.kv")


    def _post_build_init(self, dt):
        """앱의 모든 UI 요소가 빌드된 후 실행될 초기화 작업"""
        print("DEBUG: _post_build_init called. Initializing app data.")
        self.load_announcements_from_file()        

    def show_toast(self, text, duration=2):
        """ 사용자에게 짧은 메시지를 보여주는 토스트 메시지 기능 """
        if self.toast_dialog:
            self.toast_dialog.dismiss()
            self.toast_dialog = None

        toast_content = MDBoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(48)
        )
        toast_content.add_widget(
            MDLabel(
                text=text,
                halign="center",
                font_name=DEFAULT_FONT,
                markup=True,
                theme_text_color="Custom",
                text_color=(1, 1, 1, 1) # 흰색 텍스트
            )
        )
        self.toast_dialog = MDDialog(
            type="custom",
            content_cls=toast_content,
            auto_dismiss=False,
            md_bg_color=(0.2, 0.2, 0.2, 0.8),
        )
        self.toast_dialog.open()
        Clock.schedule_once(lambda *args: self.dismiss_toast(), duration)                                            

    def dismiss_toast(self):
        if self.toast_dialog:
            self.toast_dialog.dismiss()
            self.toast_dialog = None        

    def _get_data_dir_path(self):
        """데이터 저장 폴더 경로를 반환합니다. 없으면 생성합니다."""
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        os.makedirs(data_dir, exist_ok=True) # 폴더가 없으면 생성
        return data_dir

    def _get_announcements_file_path(self):
        return os.path.join(self._get_data_dir_path(), 'announcements.json') # data 폴더 안에 저장

    def _get_mountain_data_file_path(self):
        return os.path.join(self._get_data_dir_path(), 'mountain_data.json') # data 폴더 안에 저장

    def load_announcements_from_file(self):
        """announcements.json 파일을 로드합니다."""
        file_path = self._get_announcements_file_path()
        print(f"DEBUG: Attempting to load announcements from: {file_path}")
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                try:
                    self.announcements_data = json.load(f)
                    print(f"DEBUG: Successfully loaded {len(self.announcements_data)} announcements.")
                except json.JSONDecodeError as e:
                    print(f"ERROR: announcements.json decoding failed: {e}. Initializing with empty list.")
                    self.announcements_data = []
                    self.show_toast("공지사항 파일 손상! 새로 생성됩니다.", duration=3)
        else:
            print("DEBUG: announcements.json not found. Initializing with empty list.")
            self.announcements_data = []
            self.save_announcements_to_file()
            self.show_toast("공지사항 파일이 없어 새로 생성되었습니다.", duration=3)

    def save_announcements_to_file(self):
        """현재 공지사항 리스트를 announcements.json 파일에 저장합니다."""
        file_path = self._get_announcements_file_path()
        print(f"DEBUG: Saving {len(self.announcements_data)} announcements to: {file_path}")
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.announcements_data, f, ensure_ascii=False, indent=4)
            print("DEBUG: Announcements saved successfully.")
        except Exception as e:
            print(f"ERROR: Failed to save announcements to file: {e}")
            self.show_toast("공지사항 저장 실패!", duration=3)

    def save_json_data(self, file_path, data):
        """주어진 데이터를 JSON 파일에 저장합니다."""
        print(f"DEBUG: Saving data to: {file_path}")
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            print(f"ERROR: Failed to save data to {file_path}: {e}")
            return False
        except Exception as e: # <-- 'except Exception as e:' 다음에 콜론(:)이 있어야 하고,
            print(f"ERROR: Failed to save data to {file_path}: {e}") # <-- 이 줄은 'except' 블록 안에 들여쓰기 되어야 합니다.
            return False         

    def _update_progress_ui(self, instance, value):
        # self.root는 menu_screen.kv의 MDBoxLayout이므로, id로 screen_manager에 접근합니다.
        screen_manager_widget = self.root.ids.get('screen_manager')
        if not screen_manager_widget:
            print("WARNING: screen_manager not found in self.root.ids")
            return

        settings_screen = screen_manager_widget.get_screen('settings_main')
        if settings_screen:
            # 프로그레스바 값과 텍스트 업데이트
            if self.api_update_progress.is_running == 1: # 실행 중
                total = self.api_update_progress.total_items_to_fetch
                current = self.api_update_progress.current_items_fetched
                progress = (current / total) * 100 if total > 0 else 0

                # 프로그레스바와 텍스트 위젯을 가져와 업데이트
                if settings_screen.ids.get('update_progress_bar'):
                    settings_screen.ids.update_progress_bar.value = progress
                if settings_screen.ids.get('update_status_label'):
                    settings_screen.ids.update_status_label.text = \
                        f"산 정보 업데이트 중... {current}/{total}개 ({int(progress)}%)"
            elif self.api_update_progress.is_running == 2: # 완료
                if settings_screen.ids.get('update_progress_bar'):
                    settings_screen.ids.update_progress_bar.value = 100
                if settings_screen.ids.get('update_status_label'):
                    settings_screen.ids.update_status_label.text = "업데이트 완료!"
            elif self.api_update_progress.is_running == -1: # 오류
                if settings_screen.ids.get('update_status_label'):
                    settings_screen.ids.update_status_label.text = "업데이트 실패!"
            else: # 초기 상태 (0)
                if settings_screen.ids.get('update_progress_bar'):
                    settings_screen.ids.update_progress_bar.value = 0
                if settings_screen.ids.get('update_status_label'):
                    settings_screen.ids.update_status_label.text = "준비 중..."


if __name__ == "__main__":
    AlpineApp().run()