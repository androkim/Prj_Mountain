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
# NDK 버전을 GitHub Actions Workflow와 일치시키고 명시적으로 변경
# 25.2.9519653은 일반적으로 NDK r25b에 해당하지만, 명시적 버전 사용
android.ndk = 25.2.9519653
android.app_version = 0.1
android.app_version_code = 1
# 이전 오류의 원인이었던 공백과 주석을 반드시 제거했습니다.
android.archs = arm64-v8a 
# Kivy 컴파일 안정성을 위해 python3, kivy 버전을 명시적으로 고정
# requests 라이브러리는 pyopenssl과 idna 등을 요구할 수 있으므로, https 통신 시 이들을 추가하는 것이 좋습니다.
requirements = python3==3.10.9,kivy==2.2.1,kivymd==1.1.1,requests,plyer,certifi,openssl
android.permissions = INTERNET,ACCESS_FINE_LOCATION,ACCESS_NETWORK_STATE,ACCESS_COARSE_LOCATION,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE
android.add_src =
android.add_libs =
# android.ndk_api는 android.minapi와 일치시키는 것이 일반적이지만, 26으로 유지합니다.
android.ndk_api = 26
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
# CI 환경에서 SDK/NDK 경로를 수동으로 지정할 필요 없음 (Buildozer가 관리)
# android.sdk_path = 
# android.ndk_path = 
android.build_tool = gradle
buildozer.build_debug = 1
android.extra_libs =
android.enable_push = 0
# android.api와 android.targetsdk를 일치시킵니다.
android.targetsdk = 33
android.python_version = 3
android.ndk_build_tools_version =
android.debug = 1
android.ext_libs =
# Build Tools 버전도 Workflow와 일치시킵니다.
android.build_tools_version = 33.0.2

[buildozer]
log_level = 2