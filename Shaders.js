#include <metal_stdlib>
using namespace metal;


kernel void compute(texture2d<float, access::write> output [[texture(0)]],
                    constant float &timer [[buffer(1)]],
                    constant float2 &mouse [[buffer(2)]],
                    uint2 gid [[thread_position_in_grid]])
{
  int width = output.get_width();
  int height = output.get_height();
  float red = float(gid.x) / float(width);
  float green = float(gid.y) / float(height);
  float blue = abs(sin(timer));
  output.write(float4(red, green, blue, 1.0), gid);
}
