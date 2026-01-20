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
	--window-size 690 503 \
	--icon-size 120 \
	--icon "Circhart.app" 196 281 \
	--app-drop-link 544 281 \
	--hdiutil-quiet \
	"Circhart-v${version}-macos-${arch}.dmg" \
	"Circhart.app"

pkgbuild \
	--identifier dulab.big.circhart \
	--component \
	Circhart.app \
	Circhart-Component.pkg \
	--install-location /Applications

productbuild \
	--synthesize \
	--package Circhart-Component.pkg \
	Circhart-distribution.xml

productbuild \
	--distribution Circhart-distribution.xml \
	--package-path . \
	Circhart-v${version}-macos-${arch}.pkg