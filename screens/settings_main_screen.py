# screens/settings_main_screen.py
from kivymd.uix.screen import MDScreen
from kivy.properties import StringProperty
from kivymd.app import MDApp
from kivy.clock import Clock
import requests
import json
from threading import Thread
import urllib.parse
import xml.etree.ElementTree as ET # XML 파싱을 위해 사용

class SettingsMainScreen(MDScreen):
    name = StringProperty("settings_main")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print("DEBUG: SettingsMainScreen __init__ called.")

    def on_enter(self, *args):
        # 화면에 진입할 때 프로그레스바 상태 초기화
        app = MDApp.get_running_app()
        app.api_update_progress.is_running = 0
        app.api_update_progress.progress_value = 0
        app.api_update_progress.progress_text = "준비 중..."
        app.api_update_progress.total_items_to_fetch = 0
        app.api_update_progress.current_items_fetched = 0
        app._update_progress_ui(None, None) # UI 강제 업데이트


    def _go_back_to_main_screen(self):
        app = MDApp.get_running_app()
        app.root.current = "main_screen"
        

    def update_mountain_data_from_api(self):
        """전국 산행 정보 업데이트 버튼 클릭 시 호출됩니다."""
        app = MDApp.get_running_app()

        if app.FOREST_API_KEY == "YOUR_PUBLIC_DATA_API_KEY_HERE" or not app.FOREST_API_KEY:
            app.show_toast("API 키를 'main.py'에 입력해주세요!", 3)
            print("ERROR: API key not set in main.py")
            # 진행 상태 오류로 변경
            app.api_update_progress.is_running = -1
            Clock.schedule_once(lambda dt: app._update_progress_ui(None,None), 0)
            return

        # 업데이트 시작 상태로 변경
        app.api_update_progress.is_running = 1
        app.api_update_progress.progress_value = 0
        app.api_update_progress.current_items_fetched = 0
        app.api_update_progress.total_items_to_fetch = 0 # 아직 모름
        Clock.schedule_once(lambda dt: app._update_progress_ui(None,None), 0)
        
        app.show_toast("산행 정보를 업데이트 중입니다. 잠시만 기다려 주세요...", 3)
        print("DEBUG: Starting mountain data update process...")

        # UI가 멈추지 않도록 별도의 스레드에서 API 호출
        Thread(target=self._fetch_and_save_mountain_data_threaded).start()

    def _fetch_and_save_mountain_data_threaded(self):
        """API에서 산행 데이터를 비동기적으로 가져와 저장합니다."""
        app = MDApp.get_running_app()
        all_mountain_data = []
        pageNo = 1
        
        try:
            while True: 
                # 서비스 키 URL 인코딩
                encoded_service_key = urllib.parse.quote(app.FOREST_API_KEY, safe='')

                params = {
                    'serviceKey': encoded_service_key,
                    'pageNo': str(pageNo),
                    'numOfRows': str(app.API_PAGE_SIZE),
                }
                print(f"DEBUG: Requesting page {pageNo} with {app.API_PAGE_SIZE} rows from {app.MOUNTAIN_INFO_API_URL}...")
                
                response = requests.get(app.MOUNTAIN_INFO_API_URL, params=params, timeout=10)
                response.raise_for_status() 

                root = ET.fromstring(response.text)
                
                body_tag = root.find('body')
                if body_tag is not None:
                    total_count_tag = body_tag.find('totalCount')
                    if total_count_tag is not None and total_count_tag.text:
                        current_total_count = int(total_count_tag.text)
                        if pageNo == 1: 
                            app.api_update_progress.total_items_to_fetch = current_total_count
                            Clock.schedule_once(lambda dt: app._update_progress_ui(None,None), 0) # 총 개수 업데이트 반영
                            print(f"DEBUG: Total records found from API: {current_total_count}")

                    items_container = body_tag.find('items')
                    if items_container is not None:
                        current_page_items = []
                        for item_tag in items_container.findall('item'):
                            mountain_info = {
                                'mntiname': item_tag.findtext('mntiname', '이름 없음'),
                                'mntiadd': item_tag.findtext('mntiadd', '위치 정보 없음'),
                                'mntihigh': item_tag.findtext('mntihigh', '높이 정보 없음'),
                                'mntidetails': item_tag.findtext('mntidetails', '자세한 설명 없음'),
                            }
                            current_page_items.append(mountain_info)
                        
                        all_mountain_data.extend(current_page_items)
                        
                        # 진행 상황 업데이트
                        app.api_update_progress.current_items_fetched = len(all_mountain_data)
                        Clock.schedule_once(lambda dt: app._update_progress_ui(None,None), 0)
                        print(f"DEBUG: Fetched {len(current_page_items)} items on page {pageNo}. Total collected: {len(all_mountain_data)}")

                        if len(current_page_items) < app.API_PAGE_SIZE:
                            print(f"DEBUG: Less than {app.API_PAGE_SIZE} items on page {pageNo}, assumed end of data.")
                            break
                        if app.api_update_progress.total_items_to_fetch > 0 and \
                           len(all_mountain_data) >= app.api_update_progress.total_items_to_fetch:
                             print(f"DEBUG: All {app.api_update_progress.total_items_to_fetch} items collected.")
                             break
                    else: 
                        print(f"DEBUG: No 'items' container found on page {pageNo}, assumed end of data.")
                        break
                else: 
                    print(f"DEBUG: No 'body' tag found in API response on page {pageNo}.")
                    break

                pageNo += 1
                if pageNo > 100: 
                    print(f"WARNING: Max 100 pages reached to prevent excessive API calls. Current collected: {len(all_mountain_data)} items.")
                    break

        except requests.exceptions.RequestException as e:
            Clock.schedule_once(lambda dt, error=e: app.show_toast(f"데이터 통신 오류: {error}", 5), 0)
            print(f"ERROR: Request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"API Response Status: {e.response.status_code}")
                print(f"API Response Text: {e.response.text[:500]}...")
            app.api_update_progress.is_running = -1 # 오류 상태
            Clock.schedule_once(lambda dt: app._update_progress_ui(None,None), 0)
            return
        except ET.ParseError as e: 
            Clock.schedule_once(lambda dt, error=e: app.show_toast(f"API 응답 XML 파싱 오류: {error}", 5), 0)
            print(f"ERROR: XML parsing failed: {e}")
            if 'response' in locals() and response is not None:
                print(f"Raw response text (first 500 chars): {response.text[:500]}...")
            app.api_update_progress.is_running = -1 # 오류 상태
            Clock.schedule_once(lambda dt: app._update_progress_ui(None,None), 0)
            return
        except Exception as e:
            Clock.schedule_once(lambda dt, error=e: app.show_toast(f"알 수 없는 오류 발생: {error}", 5), 0)
            print(f"ERROR: An unexpected error occurred: {e}")
            app.api_update_progress.is_running = -1 # 오류 상태
            Clock.schedule_once(lambda dt: app._update_progress_ui(None,None), 0)
            return

        # 데이터 저장
        file_path = app._get_mountain_data_file_path()
        if app.save_json_data(file_path, all_mountain_data):
            Clock.schedule_once(lambda dt: app.show_toast(f"산행 정보 {len(all_mountain_data)}개 업데이트 완료!", 3), 0)
            print(f"DEBUG: Mountain data update successful. Total {len(all_mountain_data)} records saved to {file_path}")
            app.api_update_progress.is_running = 2 # 완료 상태
            Clock.schedule_once(lambda dt: app._update_progress_ui(None,None), 0)
        else:
            Clock.schedule_once(lambda dt: app.show_toast("산행 정보 저장 실패!", 3), 0)
            print(f"ERROR: Failed to save mountain data to {file_path}.")
            app.api_update_progress.is_running = -1 # 오류 상태
            Clock.schedule_once(lambda dt: app._update_progress_ui(None,None), 0)
