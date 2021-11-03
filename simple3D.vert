attribute vec3 a_position;
attribute vec3 a_normal;
attribute vec2 a_uv;

uniform mat4 u_model_matrix;
uniform mat4 u_view_matrix;
uniform mat4 u_projection_matrix;

uniform vec4 u_eye_position;

varying vec4 v_normal;

uniform vec4 u_fire_01_position;
uniform vec4 u_fire_02_position;
uniform vec4 u_fire_03_position;

varying vec4 v_s_01;
varying vec4 v_h_01;
varying vec4 v_s_02;
varying vec4 v_h_02;
varying vec4 v_s_03;
varying vec4 v_h_03;

varying vec2 v_uv;

varying vec4 v_position;

void main(void)
{
	vec4 position = vec4(a_position.x, a_position.y, a_position.z, 1.0);
	vec4 normal = vec4(a_normal.x, a_normal.y, a_normal.z, 0.0);
	
	v_uv = a_uv; // UV coords sent into per-pixel use

	position = u_model_matrix * position; // global coordinates
	v_normal = normalize(u_model_matrix * normal);

	v_s_01 = normalize(u_fire_01_position - position);
	v_s_02 = normalize(u_fire_02_position - position);
	v_s_03 = normalize(u_fire_03_position - position);
	
	vec4 v = normalize(u_eye_position - position);
	v_h_01 = normalize(v_s_01 + v);
	v_h_02 = normalize(v_s_02 + v);
	v_h_03 = normalize(v_s_03 + v);

	position = u_view_matrix * position; // eye coordinates
	v_position = position;
	position = u_projection_matrix * position; // clip coordinates

	gl_Position = position;
}
