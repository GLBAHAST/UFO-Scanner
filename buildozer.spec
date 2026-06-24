[app]
title = UFO Scanner
package.name = ufoscanner
package.domain = org.ufo

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 1.0

requirements = python3,kivy,opencv,pillow,numpy

orientation = portrait
fullscreen = 0

android.permissions = CAMERA,INTERNET
android.api = 29
android.minapi = 21
android.ndk = 23b

[buildozer]
log_level = 2
warn_on_root = 1
