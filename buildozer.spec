# buildozer.spec
[app]
title = 걷고 오르고
version = 0.1
package.name = chungahmalpine
package.domain = org.chungahmalumni
icon.filename = %(source.dir)s/images/mountain_icon.png
source.dir = .
main.py = %(source.dir)s/main.py
source.include_exts = py,kv,png,jpg,json,ttf
android.api = 33
android.minapi = 21
android.ndk = 25 # 25b 대신 25로 명시 (P4A가 더 잘 처리할 수 있도록)
android.app_version = 0.1
android.app_version_code = 1
android.archs = arm64-v8a
# android.ndk_path는 삭제된 상태 유지
requirements = python3==3.10.9,kivy==2.2.1,kivymd==1.1.1,requests,plyer
android.permissions = INTERNET,ACCESS_FINE_LOCATION,ACCESS_NETWORK_STATE,ACCESS_COARSE_LOCATION
android.add_src =
android.add_libs =
android.ndk_api = 33 # android.api와 동일하게 33으로 설정
android.extra_system_libs =
android.java_compiler = javac
android.optimizations = 0
android.optimize_bytes = 0
android.enable_external_storage = 1
logcat.add_default_filter = python
blacklist =
whitelist =
path.prefix =
android.manifest.extra_opts =
android.gradle.extra_opts =
android.build_tool = gradle
buildozer.build_debug = 1
android.extra_libs =
android.enable_push = 0
android.targetsdk = 33
android.python_version = 3
android.ndk_build_tools_version =
android.debug = 1
android.ext_libs =
android.build_tools_version = 33.0.2
android.extra_args = --allow-minsdk-ndkapi-mismatch # P4A에 직접 플래그 전달

[buildozer]
log_level = 2