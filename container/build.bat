@echo off
Rem Local build script. Used for debugging purpose.
echo ***
echo *** Compilation 64bits
echo ***
mkdir build-win64
cd build-win64
cmake .. -A x64
cmake --build . --config Release
cd ..
rmdir /s /q  build-win64


echo ***
echo *** DONE
echo ***