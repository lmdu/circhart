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
cp ../src/icons/logo.svg ./logo.svg
cp ../src/icons/alogo.svg ./alogo.svg

if [ "$packager" = "deb" ]
then
  ./nfpm pkg -t Circhart-v$version-linux.deb
elif [ "$packager" = "rpm" ]
then
  ./nfpm pkg -t Circhart-v$version-linux.rpm
else
  echo $version
fi

#build appimage
wget --no-check-certificate --quiet https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
chmod +x appimagetool-x86_64.AppImage

cp circhart.desktop Circhart
cp logo.svg Circhart/circhart.svg

mkdir -p Circhart/usr/share/icons/hicolor/scalable/apps
cp logo.svg Circhart/usr/share/icons/hicolor/scalable/apps/circhart.svg

cat > Circhart/AppRun <<'EOF'
#!/bin/bash

appdir=$(dirname $0)

exec "$appdir/Circhart" "$@"

EOF
chmod 755 Circhart/AppRun

cat > Circhart/circhart.desktop <<EOF
[Desktop Entry]
Name=Circhart
Comment=a user-friendly tool for drawing circos and snail plots
Keywords=Circos;Snail;Genome
Exec=Circhart %F
Icon=circhart
Terminal=false
Type=Application
Categories=Education
MimeType=application/x-circ
X-AppImage-Version=${version}
EOF

mkdir -p Circhart/usr/share/metainfo
cat > Circhart/usr/share/metainfo/circhart.appdata.xml <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<component type="desktop-application">
<id>com.dulab.Circhart</id>
<metadata_license>CC0-1.0</metadata_license>
<project_license>MIT</project_license>
<name>Circhart</name>
<summary>Drawing Circos and Snail plots</summary>
<description>
  <p>Circhart is a user-friendly tool for drawing circos and snail plots</p>
</description>
<screenshots>
  <screenshot type="default">
    <caption>Circhart</caption>
    <image>https://raw.githubusercontent.com/lmdu/circhart/main/src/icons/logo.svg</image>
  </screenshot>
</screenshots>
<url type="homepage">https://github.com/lmdu/circhart</url>
</component>
EOF

./appimagetool-x86_64.AppImage --appimage-extract-and-run Circhart Circhart-v$version-linux-${packager}.AppImage
rm appimagetool-x86_64.AppImage

#./nfpm pkg -t Dockey-v${version}-amd64.rpm

#if [ "$packager" = "deb" ]
#then
#  ./nfpm pkg -t Dockey-v${version}-amd64.deb
#  #tar -czvf Dockey-v${version}-ubuntu.tar.gz Dockey
#elif [ "$packager" = "rpm" ]
#then
#  ./nfpm pkg -t Dockey-v${version}-amd64.rpm
#  #tar -czvf Dockey-v${version}-centos.tar.gz Dockey
#else
#  echo $version
#fi