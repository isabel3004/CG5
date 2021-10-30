attribute vec3 a_position;
attribute vec2 a_uv;

uniform mat4 u_model_matrix;
uniform mat4 u_view_matrix;
uniform mat4 u_projection_matrix;

varying vec2 v_uv;

void main(void) {
	vec4 position = vec4(a_position.x, a_position.y, a_position.z, 1.0); // local coordinates
	
	v_uv = a_uv; // UV coords sent into per-pixel use

	position = u_model_matrix * position; // global coordinates
	position = u_view_matrix * position; // eye coordinates
	position = u_projection_matrix * position; // clip coordinates

	gl_Position = position;
}
