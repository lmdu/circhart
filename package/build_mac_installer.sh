#!/bin/bash

version=$1
arch=$2

brew install create-dmg
cd dist
create-dmg \
	--volname "Circhart Installer" \
	--volicon "../src/icons/logo.icns" \
	--background "../package/dmg_bg.png" \
	--window-pos 640 360 \
	--window-size 921 672 \
	--icon-size 90 \
	--icon "Circhart.app" 262 375 \
	--app-drop-link 726 375 \
	--hdiutil-quiet \
	"Circhart-v${version}-macos-${arch}.dmg" \
	"Circhart.app"
