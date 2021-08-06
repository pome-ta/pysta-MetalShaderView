#include <metal_stdlib>
using namespace metal;


float dist(float2 point, float2 center, float radius)
{
    return length(point - center) - radius;
}

kernel void compute(texture2d<float, access::write> output [[texture(0)]],
                    constant float &timer [[buffer(1)]],
                    constant float2 &mouse [[buffer(2)]],
                    uint2 gid [[thread_position_in_grid]])
{
  int width = output.get_width();
  int height = output.get_height();
  float red = float(gid.x) / float(width);
  float green = float(gid.y) / float(height);

  float2 uv = float2(gid) / float2(width, height);
  float distToCircle = dist(uv, float2(mouse.x, mouse.y), 0.05);
  bool inside = distToCircle < 0;
  output.write(inside ? float4(0) : float4(red, green, abs(sin(timer)), 1), gid); 
}
