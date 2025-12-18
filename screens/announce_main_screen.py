# screens/announce_main_screen.py
import os
import json
# from kivy.lang import Builder # <-- 불필요하므로 제거 (chungahmalpine.kv에서 include합니다)
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.list import MDList, TwoLineListItem
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivy.core.text import DEFAULT_FONT
from kivy.properties import StringProperty
from kivy.clock import Clock
# from kivy.factory import Factory # <-- 사용하지 않으므로 제거


class AnnounceMainScreen(MDScreen):
    name = StringProperty("announce_main")


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print("DEBUG: AnnounceMainScreen __init__ called.")
        # [CRITICAL FIX] KV 내용을 문자열로 직접 빌드하거나 로드하는 부분은 모두 제거되었습니다.


    def on_kv_post(self, base_widget):
        """KV 파일이 로드되고 self.ids가 채워진 후에 호출됩니다."""
        print("DEBUG: AnnounceMainScreen on_kv_post called. IDs should now be available.")
        super().on_kv_post(base_widget)
        # [수정] 앱 시작 시점에 load_announcements를 호출하는 것을 on_enter로 이동하여
        # 화면이 실제로 보일 때만 데이터를 로드하도록 변경합니다.
        # self.load_announcements() # <-- 이 줄은 제거합니다.


    def on_enter(self):
        print("DEBUG: AnnounceMainScreen: on_enter() called. Refreshing announcements.")
        # [수정] 화면이 활성화될 때마다 공지사항을 로드합니다.
        self.load_announcements()


    def _go_back_to_main_screen(self):
        app = MDApp.get_running_app()
        app.root.current = "main_screen"


    def load_announcements(self):
        app = MDApp.get_running_app()
        print("DEBUG: load_announcements called.")

        # [CRITICAL CHECK] self.ids에 'announcement_scroll_view'가 존재하는지 확인합니다.
        if "announcement_scroll_view" not in self.ids:
            print("CRITICAL ERROR: 'announcement_scroll_view' ID not found in AnnounceMainScreen. Check KV file structure. [CODE F]")
            app.show_toast("오류: 공지사항 화면 UI 로드 실패! (ID: announcement_scroll_view)", 5)
            return

        # ScrollView 내의 MDList 찾기
        scroll_view = self.ids.announcement_scroll_view
        md_list = None
        # ScrollView.children[0]이 MDBoxLayout이고, 그 MDBoxLayout.children[0]이 MDList일 것이라 가정.
        # 즉, <ScrollView><MDBoxLayout><MDList></MDList></MDBoxLayout></ScrollView> 구조
        if hasattr(scroll_view, 'children') and len(scroll_view.children) > 0:
            inner_box = scroll_view.children[0] # MDBoxLayout
            if hasattr(inner_box, 'children') and len(inner_box.children) > 0:
                # MDList가 MDBoxLayout의 맨 아래에 있으므로 children[0] 일 수 있습니다.
                for child in inner_box.children:
                    if isinstance(child, MDList):
                        md_list = child
                        break
        
        # [이전 코드는 .walk() 사용했으나, 자식 위젯을 직접 접근하는 것으로 수정]
        # for child in scroll_view.walk(): # <-- 이전 코드 (walk는 불필요하게 광범위)
        #     if isinstance(child, MDList):
        #         md_list = child
        #         break


        if md_list is None:
            print("CRITICAL ERROR: MDList not found inside ScrollView (expected MDBoxLayout > MDList structure). Check KV structure. [CODE G]")
            app.show_toast("오류: 공지사항 목록 UI 로드 실패! (MDList)", 5)
            return


        md_list.clear_widgets() # 기존 목록 삭제


        # 데이터 없을 때 처리
        if not app.announcements_data:
            md_list.add_widget(
                MDLabel(text="등록된 공지사항이 없습니다.", halign="center", font_name=DEFAULT_FONT)
            )
            print("DEBUG: No announcements found.")
            return


        # 공지사항 UI 채우기
        for i, ann in enumerate(app.announcements_data):
            item = TwoLineListItem(
                text=ann["title"],
                secondary_text=ann["content"],
                on_release=lambda x, title=ann["title"], content=ann["content"], index=i:
                    self.show_announcement_detail_and_options(title, content, index)
            )
            md_list.add_widget(item)


        print(f"DEBUG: Successfully loaded {len(app.announcements_data)} announcements to UI.")


    def show_announcement_detail_and_options(self, title, content, index):
        app = MDApp.get_running_app()
        # [수정] MDLabel의 높이 설정 시 text_size 바인딩 순서 변경
        dialog_label = MDLabel(
            text=f"[b]{title}[/b]\n\n{content}",
            halign="left",
            valign="top",
            markup=True,
            font_name=DEFAULT_FONT,
            size_hint_y=None,
        )
        # 먼저 text_size를 바인딩하고, 그 후에 texture_size에 따라 height를 설정합니다.
        dialog_label.bind(width=lambda instance, value: setattr(instance, 'text_size', (value, None)))
        dialog_label.bind(texture_size=lambda instance, size: setattr(instance, 'height', size[1] + dp(20)))

        dialog_scroll_content = ScrollView(
            size_hint_y=None,
            height=dp(300),
            bar_width='7dp',
            bar_color=app.theme_cls.primary_color,
            bar_inactive_color=(0.5,0.5,0.5,0.3)
        )
        dialog_scroll_content.add_widget(dialog_label)


        self.detail_dialog = MDDialog(
            title="공지사항 상세",
            type="custom",
            content_cls=dialog_scroll_content,
            buttons=[
                MDFlatButton(
                    text="닫기",
                    font_name=DEFAULT_FONT,
                    on_release=lambda x: self.detail_dialog.dismiss()
                ),
                MDRaisedButton(
                    text="수정",
                    font_name=DEFAULT_FONT,
                    on_release=lambda x, idx=index: self.show_edit_announcement_dialog(idx)
                ),
                MDRaisedButton(
                    text="삭제",
                    font_name=DEFAULT_FONT,
                    on_release=lambda x, idx=index: self.delete_announcement_from_detail(idx)
                ),
            ],
        )
        self.detail_dialog.open()


    def delete_announcement_from_detail(self, index):
        if hasattr(self, 'detail_dialog') and self.detail_dialog:
            self.detail_dialog.dismiss()
        self.show_delete_confirmation_dialog(index)


    def show_edit_announcement_dialog(self, index):
        app = MDApp.get_running_app()
        if not (0 <= index < len(app.announcements_data)):
            app.show_toast("수정할 공지사항을 찾을 수 없습니다.")
            return


        current_announcement = app.announcements_data[index]
        self.edit_title_field = MDTextField(
            hint_text="제목",
            font_name=DEFAULT_FONT,
            text=current_announcement["title"],
            multiline=False,
            size_hint_y=None, height=dp(48)
        )
        self.edit_content_field = MDTextField(
            hint_text="내용",
            font_name=DEFAULT_FONT,
            text=current_announcement["content"],
            multiline=True,
            size_hint_y=None, height=dp(100)
        )


        dialog_content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(10),
            size_hint_y=None,
            height=dp(180)
        )
        dialog_content.add_widget(self.edit_title_field)
        dialog_content.add_widget(self.edit_content_field)


        self.edit_dialog = MDDialog(
            title="공지사항 수정",
            type="custom",
            content_cls=dialog_content,
            buttons=[
                MDFlatButton(text="취소", font_name=DEFAULT_FONT, on_release=lambda x: self.edit_dialog.dismiss()),
                MDRaisedButton(text="저장", font_name=DEFAULT_FONT, on_release=lambda x, idx=index: self._save_edited_announcement(idx)),
            ],
        )
        if hasattr(self, 'detail_dialog') and self.detail_dialog:
            self.detail_dialog.dismiss()
        self.edit_dialog.open()


    def _save_edited_announcement(self, index):
        app = MDApp.get_running_app()
        new_title = self.edit_title_field.text.strip()
        new_content = self.edit_content_field.text.strip()


        if new_title and new_content:
            app.announcements_data[index]["title"] = new_title
            app.announcements_data[index]["content"] = new_content
            app.save_announcements_to_file()
            self.load_announcements()
            app.show_toast("공지사항이 수정되었습니다.")
            self.edit_dialog.dismiss()
        else:
            app.show_toast("제목과 내용을 모두 입력해 주세요.")


    def show_add_announcement_dialog(self):
        app = MDApp.get_running_app()


        self.add_title_field = MDTextField(
            hint_text="제목",
            font_name=DEFAULT_FONT,
            multiline=False,
            size_hint_y=None, height=dp(48)
        )
        self.add_content_field = MDTextField(
            hint_text="내용",
            font_name=DEFAULT_FONT,
            multiline=True,
            size_hint_y=None, height=dp(100)
        )


        dialog_content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(10),
            size_hint_y=None,
            height=dp(180)
        )
        dialog_content.add_widget(self.add_title_field)
        dialog_content.add_widget(self.add_content_field)


        self.add_dialog = MDDialog(
            title="새 공지사항 추가",
            type="custom",
            content_cls=dialog_content,
            buttons=[
                MDFlatButton(text="취소", font_name=DEFAULT_FONT, on_release=lambda x: self.add_dialog.dismiss()),
                MDRaisedButton(text="추가", font_name=DEFAULT_FONT, on_release=self._add_new_announcement),
            ],
        )
        self.add_dialog.open()


    def _add_new_announcement(self, *args):
        app = MDApp.get_running_app()
        title = self.add_title_field.text.strip()
        content = self.add_content_field.text.strip()


        if title and content:
            app.announcements_data.append({"title": title, "content": content})
            app.save_announcements_to_file()
            self.load_announcements()
            app.show_toast("공지사항이 추가되었습니다.")
            self.add_dialog.dismiss()
        else:
            app.show_toast("제목과 내용을 모두 입력해 주세요.")


    def show_delete_confirmation_dialog(self, index):
        app = MDApp.get_running_app()
        title_to_delete = app.announcements_data[index]["title"] if 0 <= index < len(app.announcements_data) else "알 수 없음"


        self.delete_dialog = MDDialog(
            title="공지사항 삭제",
            text=f"'{title_to_delete}' 공지사항을 삭제하시겠습니까?",
            type="confirmation",
            buttons=[
                MDFlatButton(text="취소", font_name=DEFAULT_FONT, on_release=lambda x: self.delete_dialog.dismiss()),
                MDRaisedButton(
                    text="삭제",
                    font_name=DEFAULT_FONT,
                    on_release=lambda x, idx=index: self._delete_announcement(idx)
                ),
            ],
        )
        if hasattr(self, 'edit_dialog') and self.edit_dialog:
            self.edit_dialog.dismiss()
        self.delete_dialog.open()


    def _delete_announcement(self, index):
        app = MDApp.get_running_app()
        if 0 <= index < len(app.announcements_data):
            deleted_title = app.announcements_data[index]["title"]
            del app.announcements_data[index]
            app.save_announcements_to_file()
            self.load_announcements()
            app.show_toast(f"'{deleted_title}' 공지사항이 삭제되었습니다.")
        else:
            app.show_toast("삭제할 공지사항을 찾을 수 없습니다.")
        self.delete_dialog.dismiss()