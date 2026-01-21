#!/bin/bash

version=$1
packager=$2

cd dist

wget https://github.com/goreleaser/nfpm/releases/download/v2.44.1/nfpm_2.44.1_Linux_x86_64.tar.gz
tar xzvf nfpm_2.44.1_Linux_x86_64.tar.gz
rm nfpm_2.44.1_Linux_x86_64.tar.gz

cat > Circhart.desktop <<EOF
[Desktop Entry]
Version=${version}
Name=Circhart
Comment=a user-friendly tool for drawing circos and snail plots
GenericName=Circos Charts
Keywords=Cirocs;Snail;Genome
Exec=/usr/lib/Circhart/Circhart %f
Icon=circhart.svg
Terminal=false
Type=Application
Categories=Education
StartupNotify=true
MimeType=application/x-circ
EOF

cat > application-x-circ.xml <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<mime-info xmlns="http://www.freedesktop.org/standards/shared-mime-info">
  <mime-type type="application/x-circ">
    <comment>Circhart Project File</comment>
    <glob pattern="*.circ"/>
  </mime-type>
</mime-info>
EOF

cat > nfpm.yaml <<EOF
name: Circhart
arch: amd64
platform: linux
version: v${version}
section: default
priority: extra
maintainer: lmdu <adullb@qq.com>
description: a user-friendly tool for drawing circos and snail plots
vendor: Bioinformatics and Integrative Genomics
homepage: https://github.com/lmdu/circhart
license: MIT
contents:
  - src: ./Circhart
    dst: /usr/lib/Circhart
  - src: ./circhart.desktop
    dst: /usr/share/applications/circhart.desktop
  - src: ./application-x-circ.xml
    dst: /usr/share/mime/packages/application-x-circ.xml
  - src: ./logo.svg
    dst: /usr/share/icons/hicolor/scalable/apps/circhart.svg
  - src: ./alogo.svg
    dst: /usr/share/icons/hicolor/scalable/mimetypes/application-x-circ.svg
rpm:
  compression: zstd
deb:
  compression: zstd
EOF

# copy logo file
#cp ../src/icons/logo.svg ./logo.svg
#cp ../src/icons/alogo.svg ./alogo.svg

#if [ "$packager" = "deb" ]
#then
#  ./nfpm pkg -t Circhart-v$version-linux.deb
#elif [ "$packager" = "rpm" ]
#then
#  ./nfpm pkg -t Circhart-v$version-linux.rpm
#else
#  echo $version
#fi

#build appimage
sudo apt install coreutils binutils patchelf desktop-file-utils fakeroot fuse squashfs-tools strace util-linux zsync libgdk-pixbuf2.0-dev -y
wget --no-check-certificate --quiet https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage -O $GITHUB_WORKSPACE/appimagetool
chmod +x $GITHUB_WORKSPACE/appimagetool

pip install git+https://github.com/Frederic98/appimage-builder.git
echo "$GITHUB_WORKSPACE" >> $GITHUB_PATH

cat > AppImageBuilder.yml <<EOF
version: 1

AppDir:
  path: ./AppDir
  
  app_info:
    id: dulab.big.circhart
    name: Circhart
    icon: circhart-icon.svg
    version: ${version}
    exec: Circhart
    exec_args: $@
  
  apt:
    arch:
      - amd64
    
    allow_unauthenticated: true

    sources:
      - sourceline: deb http://archive.ubuntu.com/ubuntu/ jammy main restricted universe multiverse
      - sourceline: deb http://archive.ubuntu.com/ubuntu/ jammy-updates main restricted universe multiverse
      - sourceline: deb http://security.ubuntu.com/ubuntu jammy-security main restricted universe multiverse
    
    include:
      - xdg-desktop-portal-kde
      - libgtk-3-0
      - librsvg2-2
      - librsvg2-common
      - libgdk-pixbuf2.0-0
      - libgdk-pixbuf2.0-bin
      - libgdk-pixbuf2.0-common
      - shared-mime-info
      - gnome-icon-theme-symbolic
      - hicolor-icon-theme
    
    exclude: []
  
  files:
    include: []

    exclude:
      - usr/share/man
      - usr/share/doc/*/README.*
      - usr/share/doc/*/changelog.*
      - usr/share/doc/*/NEWS.*
      - usr/share/doc/*/TODO.*
      - usr/lib/x86_64-linux-gnu/libssl.so*

  runtime:
    env:
      APPDIR_LIBRARY_PATH: "$APPDIR:$APPDIR/runtime/compat/:$APPDIR/usr/lib/x86_64-linux-gnu:$APPDIR/lib/x86_64-linux-gnu:$APPDIR/usr/lib:$APPDIR/usr/lib/x86_64-linux-gnu/gdk-pixbuf-2.0/2.10.0/loaders"
      LD_LIBRARY_PATH: "$APPDIR:$APPDIR/runtime/compat/:$APPDIR/usr/lib/x86_64-linux-gnu:$APPDIR/lib/x86_64-linux-gnu:$APPDIR/usr/lib:$APPDIR/usr/lib/x86_64-linux-gnu/gdk-pixbuf-2.0/2.10.0/loaders"
      PYTHONPATH: "$APPDIR"
      GDK_PIXBUF_MODULEDIR: $APPDIR/usr/lib/x86_64-linux-gnu/gdk-pixbuf-2.0/2.10.0/loaders
      GDK_PIXBUF_MODULE_FILE: $APPDIR/usr/lib/x86_64-linux-gnu/gdk-pixbuf-2.0/2.10.0/loaders.cache

    path_mappings:
      - /usr/share:$APPDIR/usr/share

  test:
    fedora-30:
      image: appimagecrafters/tests-env:fedora-30
      command: ./AppRun
      use_host_x: True

    debian-stable:
      image: appimagecrafters/tests-env:debian-stable
      command: ./AppRun
      use_host_x: True
    
    archlinux-latest:
      image: appimagecrafters/tests-env:archlinux-latest
      command: ./AppRun
      use_host_x: True
    
    centos-7:
      image: appimagecrafters/tests-env:centos-7
      command: ./AppRun
      use_host_x: True
    
    ubuntu-xenial:
      image: appimagecrafters/tests-env:ubuntu-xenial
      command: ./AppRun
      use_host_x: True

AppImage:
  arch: x86_64
  file_name: Circhart-v${version}-linux-x64.AppImage
  update-information: guess
  comp: gzip

EOF

mv Circhart AppDir
icon_file=../src/icons/logo.svg
icon_dir=./AppDir/usr/share/icons/hicolor
mkdir -p ${icon_dir}/{scalable,64x64,128x128,256x256}/apps
cp ${icon_file} ${icon_dir}/scalable/apps/circhart-icon.svg
cp ${icon_file} ./AppDir/circhart-icon.svg

sudo apt install imagemagick

for s in 64 128 256
do
  convert -size ${s}x${s} ${icon_file} ${icon_dir}/${s}x${s}/apps/circhart-icon.png
done

appimage-builder --recipe AppImageBuilder.yml --skip-test

#cp circhart.desktop Circhart
#cp logo.svg Circhart/circhart.svg

#mkdir -p Circhart/usr/share/icons/hicolor/scalable/apps
#cp logo.svg Circhart/usr/share/icons/hicolor/scalable/apps/circhart.svg

#cat > Circhart/AppRun <<'EOF'
##!/bin/bash

#appdir=$(dirname $0)

#exec "$appdir/Circhart" "$@"

#EOF
#chmod 755 Circhart/AppRun

#cat > Circhart/circhart.desktop <<EOF
#[Desktop Entry]
#Name=Circhart
#Comment=a user-friendly tool for drawing circos and snail plots
#Keywords=Circos;Snail;Genome
#Exec=Circhart %F
#Icon=circhart
#Terminal=false
#Type=Application
#Categories=Education
#MimeType=application/x-circ
#X-AppImage-Version=${version}
#EOF

#mkdir -p Circhart/usr/share/metainfo
#cat > Circhart/usr/share/metainfo/circhart.appdata.xml <<EOF
#<?xml version="1.0" encoding="UTF-8"?>
#<component type="desktop-application">
#<id>com.dulab.Circhart</id>
#<metadata_license>CC0-1.0</metadata_license>
#<project_license>MIT</project_license>
#<name>Circhart</name>
#<summary>Drawing Circos and Snail plots</summary>
#<description>
#  <p>Circhart is a user-friendly tool for drawing circos and snail plots</p>
#</description>
#<screenshots>
#  <screenshot type="default">
#    <caption>Circhart</caption>
#    <image>https://raw.githubusercontent.com/lmdu/circhart/main/src/icons/logo.svg</image>
#  </screenshot>
#</screenshots>
#<url type="homepage">https://github.com/lmdu/circhart</url>
#</component>
#EOF

