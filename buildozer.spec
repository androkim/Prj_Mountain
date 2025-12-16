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
android.api = 32
android.minapi = 21
android.ndk = 25
android.app_version = 0.1
android.app_version_code = 1
android.archs = arm64-v8a
requirements = python3,kivy==2.2.1,kivymd==1.1.1,requests,plyer
android.permissions = INTERNET,ACCESS_FINE_LOCATION,ACCESS_NETWORK_STATE,ACCESS_COARSE_LOCATION
android.add_src =
android.add_libs =
android.ndk_api = 32
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
android.targetsdk = 32
android.python_version = 3
android.ndk_build_tools_version =
android.debug = 1
android.ext_libs =
android.build_tools_version = 33.0.2
android.extra_args = --allow-minsdk-ndkapi-mismatch

[buildozer]
log_level = 1