
# llvm build

cd llvm/
git submodule init
git submodule update
mkdir build
cd build/
cmake ../ -G Ninja -DCMAKE_BUILD_TYPE=Release
ninja -j4
cd ../../

# v8 gclient setting

# "url": "https://github.com/eunchong/v8.git@origin/JSMTrace",
gclient config --spec 'solutions = [
  {
    "url": "ssh://git@github.com/eunchong/v8.git@origin/JSMTrace",
    "managed": False,
    "name": "v8",
    "deps_file": "DEPS",
    "custom_deps": {},
  },
]
'
gclient sync

rm -rf v8/third_party/llvm-build/Release+Asserts/bin
rm -rf v8/third_party/llvm-build/Release+Asserts/lib
mkdir -p v8/third_party/llvm-build/Release+Asserts
cp -rf llvm/build/bin v8/third_party/llvm-build/Release+Asserts/bin
cp -rf llvm/build/lib v8/third_party/llvm-build/Release+Asserts/lib

# v8 build

cd v8/
rm -rf ./out/Release/d8
export GYP_DEFINES="asan=1 v8_enable_disassembler=1 v8_object_print=1"
export GYP_GENERATORS=ninja
#GYP_DEFINES="v8_enable_disassembler=1 v8_object_print=1"
gypfiles/gyp_v8 -Dv8_target_arch=x64 -S.x64.release  -Dv8_enable_backtrace=1 -Dv8_use_snapshot='false' -Dv8_enable_gdbjit=0 -Dwerror='' -Darm_fpu=default -Darm_float_abi=default
ninja -C out/Release d8 -j8
cd ../

