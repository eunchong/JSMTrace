print('Hello MTrace')

function str2ab(str) {
  var buf = new ArrayBuffer(str.length*2);
  var bufView = new Uint16Array(buf);
  for (var i=0, strLen=str.length; i < strLen; i++) {
    bufView[i] = str.charCodeAt(i);
  }
  return buf;
}

b = str2ab('deadbeef')

print(b[0])
var bufView = new Uint16Array(b);
print(bufView[0])
print(bufView[5])
print(bufView[1])
print(bufView[2])
bufView[4] = 'cafebabe'.charCodeAt(3);
print(bufView[4])
print(bufView[0])

print('End MTrace')

