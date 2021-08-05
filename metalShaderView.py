import pathlib
import ctypes

from objc_util import c, create_objc_class, ObjCClass, ObjCInstance
import ui
import editor


shader_path = pathlib.Path(editor.get_path())
#shader_path = pathlib.Path('./Shaders.js')

# --- load objc classes
MTKView = ObjCClass('MTKView')

# --- initialize MetalDevice
MTLCreateSystemDefaultDevice = c.MTLCreateSystemDefaultDevice
MTLCreateSystemDefaultDevice.argtypes = []
MTLCreateSystemDefaultDevice.restype = ctypes.c_void_p

err_ptr = ctypes.c_void_p()


class MetalView(ui.View):
  def __init__(self, *args, **kwargs):
    ui.View.__init__(self, *args, **kwargs)
    interval = 60
    self.update_interval = 1 / interval
    self.bg_color = '#242424'
    self.view_did_load()
    self.set_log()

  def set_log(self):
    self.log_view = ui.View()
    self.log_view.flex = 'W'
    self.log_view.bg_color = 'blue'
    self.log_text = ui.TextView()
    self.log_text.font = ('Source Code Pro', 16)
    self.log_text.editable = False
    self.log_text.flex = 'W'
    self.tx = 0.0
    self.ty = 0.0
    self.log_view.add_subview(self.log_text)
    self.add_subview(self.log_view)

  def update(self):
    self.log_text.text = f'time\t\t: {str(self.time.value)}\ntouch_x\t: {str(self.tx)}\ntouch_y\t: {str(self.ty)}'

  def touch_began(self, touch):
    _x, _y = touch.location
    self.tx = _x
    self.ty = _y

  def touch_moved(self, touch):
    _x, _y = touch.location
    self.tx = _x
    self.ty = _y

  def touch_ended(self, touch):
    pass

  def view_did_load(self):
    mtkView = MTKView.alloc()
    _device = MTLCreateSystemDefaultDevice()
    devices = ObjCInstance(_device)

    # todo: 端末サイズにて要調整
    _uw, _uh = ui.get_window_size()
    _w = min(_uw, _uh) * 0.88
    _x = (_uw - _w) * 0.5
    _y = _uh * 0.25
    _frame = ((_x, _y), (_w, _w))

    mtkView.initWithFrame_device_(_frame, devices)
    #mtkView.setAutoresizingMask_((1 << 1) | (1 << 4))
    renderer = self.renderer_init(PyRenderer, mtkView)
    mtkView.delegate = renderer

    #mtkView.enableSetNeedsDisplay = True
    mtkView.framebufferOnly = False
    #mtkView.setNeedsDisplay()
    
    self.objc_instance.addSubview_(mtkView)

  def renderer_init(self, delegate, _mtkView):
    renderer = delegate.alloc().init()
    device = _mtkView.device()
    renderer.commandQueue = device.newCommandQueue()

    # --- registerShaders
    source = shader_path.read_text('utf-8')
    library = device.newLibraryWithSource_options_error_(source, err_ptr, err_ptr)
    kernel = library.newFunctionWithName_('compute')

    # maxTotalThreadsPerThreadgroup: 1024
    # threadExecutionWidth: 32
    renderer.cps = device.newComputePipelineStateWithFunction_error_(kernel, err_ptr)
    renderer.tew = renderer.cps.threadExecutionWidth()
    renderer.mttpt = renderer.cps.maxTotalThreadsPerThreadgroup()

    renderer.timer = ctypes.c_float(0.0)
    renderer.timerBuffer = device.newBufferWithLength_options_(ctypes.sizeof(renderer.timer), 0)
    self.time = renderer.timer

    renderer.mouse = (ctypes.c_float * 2)(0.0, 0.0)
    renderer.mouseBuffer = device.newBufferWithLength_options_(ctypes.sizeof(renderer.mouse), 0)

    return renderer


# --- MTKViewDelegate
def drawInMTKView_(_self, _cmd, _view):
  self = ObjCInstance(_self)
  view = ObjCInstance(_view)

  drawable = view.currentDrawable()
  commandBuffer = self.commandQueue.commandBuffer()
  commandEncoder = commandBuffer.computeCommandEncoder()
  commandEncoder.setComputePipelineState_(self.cps)
  commandEncoder.setTexture_atIndex_(drawable.texture(), 0)

  commandEncoder.setBuffer_offset_atIndex_(self.mouseBuffer, 0, 2)
  commandEncoder.setBuffer_offset_atIndex_(self.timerBuffer, 0, 1)

  # --- update
  self.timer.value += 0.01
  bufferPointer = self.timerBuffer.contents()
  ctypes.memmove(bufferPointer,
                 ctypes.byref(self.timer), ctypes.sizeof(self.timer))

  bufferPointer = self.mouseBuffer.contents()
  ctypes.memmove(bufferPointer,
                 ctypes.byref(self.mouse), ctypes.sizeof(self.mouse))

  _width = 8
  _height = 8
  _depth = 1
  threadGroupCount = (_width, _height, _depth)
  t_w = drawable.texture().width()
  t_h = drawable.texture().height()
  threadGroups = (-(-t_w // _width), -(-t_h // _height), 1)
  commandEncoder.dispatchThreadgroups_threadsPerThreadgroup_(threadGroups, threadGroupCount)

  commandEncoder.endEncoding()
  commandBuffer.presentDrawable_(drawable)
  commandBuffer.commit()
  #commandBuffer.waitUntilCompleted()


def mtkView_drawableSizeWillChange_(_self, _cmd, _view, _size):
  self = ObjCInstance(_self)
  view = ObjCInstance(_view)


PyRenderer = create_objc_class(
  name='PyRenderer',
  methods=[drawInMTKView_, mtkView_drawableSizeWillChange_],
  protocols=['MTKViewDelegate'])

if __name__ == '__main__':
  view = MetalView()
  view.present(style='fullscreen', orientations=['portrait'])

