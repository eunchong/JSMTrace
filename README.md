# JSMTrace

JSMTrace is a new tool for Javascript memory tracing which helps users to analyze memory information in V8 engine. To support users efficiently, JSMTrace provides memory accessing information with two types of view by referring to two references; the first is source code, and the other is unique ID. We call each view as a source code view and unique ID view. 

Unique ID is a concept which we used for tracking memory group. In JSMTrace, allocated memory areas have unique IDs respectively. These IDs are quickly obtained by exploiting shadow memory structure. Whenever the memory allocation occurs, a unique ID is assigned to a memory group respectively.

In source code view, JSMTrace grasps the information which code line tries to access to memory from Javascript code. Then, it shows which code lines accesses to each memory with some information such as access type, unique IDs, address, etc. 
<p align="center">
<img src="https://cloud.githubusercontent.com/assets/2150106/21038134/8974142c-be16-11e6-97bd-6be909a3a1d8.png" width="480">
</p>
On the other hands, the unique ID view has a similar information, but in different point of view. In this mode, JSMTrace shows memory accessing information based on memory group, sorting by unique ID.

<p align="center">
<img src="https://cloud.githubusercontent.com/assets/2150106/21038127/7d94ee2e-be16-11e6-8540-5a02c6f2ba87.png" width="480">
</p>
For implementation, we firstly used shadow memory technique from LLVM AddressSanitizer. It was a significant technique for linear performance. Then, by referring to SourcePositionTable and RuntimeTrace in V8 engine, we attempted to track the Javascript code line which we need to know.

<p align="center">
<img src="https://cloud.githubusercontent.com/assets/2150106/21038223/3e775596-be17-11e6-89c4-b9cdce2a4a69.png" width="480">
</p>

For the benchmarking performance of JSMTrace, we used google's Octane benchmark tool. The result performance were calculated as 3.1x, 1.2x in each enable log output, disable log output mode.

<p align="center">
<img src="https://cloud.githubusercontent.com/assets/2150106/21038330/13441886-be18-11e6-9040-745326929690.jpeg" width="480">
<img src="https://cloud.githubusercontent.com/assets/2150106/21038329/1343ea6e-be18-11e6-9b08-a6dc7ffedd92.jpeg" width="480">
</p>

## Work left to do

- [X] Modify llvm ASan for JSMTrace
- [X] Modify v8 for JSMTrace
- [X] Apply git submodule llvm and v8
- [X] Develop JSMTrace prototype for memory trace and visualize
- [X] Improve JSMTrace prototype from logfile based process to using Database
- [X] Develop Web UI, For interaction with JMSTrace. 
- [ ] Make options of JSMTrace trace and analyze
- [ ] Divide the JSMTrace LLVM from ASan Module


## License
JSMTrace is released under the [MIT License](http://www.opensource.org/licenses/MIT).
