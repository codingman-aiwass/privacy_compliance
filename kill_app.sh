#!/bin/bash
pkgName=$1
echo "Start clear $pkgName"
adb shell am force-stop $pkgName
echo "Clear $pkgName done."
exit