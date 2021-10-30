uniform sampler2D u_tex01;
uniform sampler2D u_tex02;

uniform float u_using_texture;

varying vec4 v_normal;
varying vec4 v_s;
varying vec4 v_h;
varying vec2 v_uv;

uniform vec4 u_light_specular;
uniform vec4 u_light_diffuse;
uniform vec4 u_mat_specular;
uniform vec4 u_mat_diffuse;
uniform float u_mat_shininess;

void main(void)
{
	vec4 mat_diffuse = u_mat_diffuse;
	vec4 mat_specular = u_mat_specular;
	float opacity = u_mat_diffuse.a;

	if (u_using_texture == 1.0) {
		mat_diffuse *= texture2D(u_tex01, v_uv);
		opacity = 1.0 - texture2D(u_tex02, v_uv).r; // land, w/o '1.0-' water
	}

	if (opacity < 0.01) {
		discard;
	}

	// lit opposite side
	// vec4 normal;
	// if (dot(v_v, v_normal) < 0.0) {
	// 	normal = - v_normal;
	// } else {
	// 	normal = v_normal;
	// }

	// if (dot(v_v, v_normal) < 0.0) {
	// 	discard;
	// }

	float s_len = length(v_s);
	float n_len = length(v_normal);
	// vec4 h = v_s + v_v;
	float h_len = length(v_h);
	
	float lambert = max(dot(v_normal, v_s) / (n_len * s_len), 0.0);
	float phong = max(dot(v_normal, v_h) / (n_len * h_len), 0.0);

	gl_FragColor = lambert * u_light_diffuse * mat_diffuse
        + pow(phong, u_mat_shininess) * u_light_specular * mat_specular;
	gl_FragColor.a = opacity;
}
