[app]

# (str) Title of your application
title = AI Image Generator

# (str) Package name
package.name = aiimagegenerator

# (str) Package domain (needed for android packaging)
package.domain = org.example

# (str) Source code where the main.py lives
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,jpeg,webp,json,txt

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy==2.3.0,requests,urllib3,certifi,idna,charset-normalizer,openssl,android

# (str) Custom source folders for requirements
# It may be useful to fill this if you have custom packages
# requirements.source.kivy = ../../kivy

# (list) Permissions
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Android NDK version to use
# android.ndk = 25b

# (bool) Use --private data directory (True) or --dir public directory (False)
# android.private_storage = True

# (bool) Accept SDK license without identifying manually
android.accept_sdk_license = True

# (list) The Android architectures to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.archs = arm64-v8a

# (str) Application versioning (method 1)
version.filename = %(source.dir)s/version.txt

# (int) Log level (0 = error only, 1 = info, 2 = debug and gigatons of toast)
log_level = 2

# (int) Fullscreen mode
fullscreen = 0
