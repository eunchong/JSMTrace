#/home/v8/v8/out/x64.release/d8 --test --random-seed=720068450 --nohard-abort --nodead-code-elimination --nofold-constants /home/v8/v8/test/benchmarks/data/octane/base.js /home/v8/v8/test/benchmarks/data/octane/splay.js -e BenchmarkSuite.RunSuites\({}\) 2> out.log
v8/out/Release/d8 --expose-gc array_test.js 2> out.log
#/home/v8/v8/out/x64.release/d8 --test --random-seed=720068450 --nohard-abort --nodead-code-elimination --nofold-constants /home/v8/v8/test/benchmarks/data/octane/base.js /home/v8/v8/test/benchmarks/data/octane/richards.js -e BenchmarkSuite.RunSuites\({}\)
./js_symbolizer.py out.log sOut.log
#cat sOut.log | ./asan_symbolizer.py > symbolOut.log
