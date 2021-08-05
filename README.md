# pysta-MetalShaderView


[Pythonista3](http://omz-software.com/pythonista/) で、Metal Shader を気軽に実行


## 使い方

- [metalShaderView.py](https://github.com/pome-ta/pysta-MetalShaderView/metalShaderView.py) をPythonista へ
- [Editor Action](http://omz-software.com/pythonista/docs/ios/editor.html#module-editor) を設定
- 編集しているShader コード上でActionを実行


## Shader コードについて

拡張子は、`.metal` でも、`.js` `.py` でも何でも読み取り可能 🙆‍♀️


エディタ上で、編集しやすい拡張子を選んで 📝


### 注意

```
kernel void compute(texture2d<float, access::write> output [[texture(0)]],
                    constant float &timer [[buffer(1)]],
                    uint2 gid [[thread_position_in_grid]])
```

のこ形式は守ること😤

細かいことは、[Using MetalKit part 12](https://metalkit.org/2016/05/18/using-metalkit-part-12/) を読んで欲しい



`kernel` でやってる


## todo

- [ ] touch 対応
- [ ] アスペクトのGLSL 的なお作法とか
- [ ] Metal 全体的な対応
- [ ] コード整理

