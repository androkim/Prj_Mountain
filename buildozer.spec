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
android.ndk = 25b
android.app_version = 0.1
android.app_version_code = 1
android.archs = arm64-v8a
# Kivy 컴파일 안정성을 위해 python3, kivy 버전을 명시적으로 고정
requirements = python3==3.10.9,kivy==2.2.1,kivymd==1.1.1,requests,plyer
android.permissions = INTERNET,ACCESS_FINE_LOCATION,ACCESS_NETWORK_STATE,ACCESS_COARSE_LOCATION
android.add_src =
android.add_libs =
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
# CI 환경에서 Buildozer가 자체 경로에 SDK를 설치하므로, 여기서는 경로 지정 제거
# android.sdk_path = /opt/hostedtoolcache/Android/sdk
# android.ndk_path = /opt/hostedtoolcache/Android/ndk
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

[buildozer]
log_level = 2