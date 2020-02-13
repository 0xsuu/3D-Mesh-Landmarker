#version 330
layout(location = 0) in vec4 position;

uniform mat4 projection;
uniform mat4 view;

out vec3 color;

void main()
{
    gl_Position = projection * view * position;
    color = 0.5 + 0.5 * position.xyz;
}
