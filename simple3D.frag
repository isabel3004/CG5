uniform sampler2D u_tex01;
uniform sampler2D u_tex02;

uniform float u_using_texture;

varying vec4 v_normal;
varying vec4 v_s_01;
varying vec4 v_h_01;
varying vec4 v_s_02;
varying vec4 v_h_02;
varying vec4 v_s_03;
varying vec4 v_h_03;

varying vec2 v_uv;

uniform vec4 u_light_specular;
uniform vec4 u_light_diffuse;
uniform vec4 u_mat_specular;
uniform vec4 u_mat_diffuse;
uniform float u_mat_shininess;

uniform vec4 u_start_fog;
uniform vec4 u_end_fog;
uniform vec4 u_fog_color;
varying vec4 v_position;

void main(void) {
	vec4 mat_diffuse = u_mat_diffuse;
	vec4 mat_specular = u_mat_specular;
	float opacity = u_mat_diffuse.a;

	if (u_using_texture == 1.0) {
		mat_diffuse *= texture2D(u_tex01, v_uv);
		opacity = 1.0 - texture2D(u_tex02, v_uv).r;
	}

	if (opacity < 0.01) {
		discard;
	}

	float fog_factor;
	if (length(v_position) <= length(u_start_fog)) {
		fog_factor = 0.0;
	} else if (length(v_position) >= length(u_end_fog)) {
		fog_factor = 1.0;
	} else {
		fog_factor = ( length(v_position) - length(u_start_fog) ) / ( length(u_end_fog) - length(u_start_fog) );
	}

	float s_len_01 = length(v_s_01);
	float s_len_02 = length(v_s_02);
	float s_len_03 = length(v_s_03);
	float h_len_01 = length(v_h_01);
	float h_len_02 = length(v_h_02);
	float h_len_03 = length(v_h_03);

	float n_len = length(v_normal);
	
	float lambert_01 = max(dot(v_normal, v_s_01) / (n_len * s_len_01), 0.0);
	float lambert_02 = max(dot(v_normal, v_s_02) / (n_len * s_len_02), 0.0);
	float lambert_03 = max(dot(v_normal, v_s_03) / (n_len * s_len_03), 0.0);

	float phong_01 = max(dot(v_normal, v_h_01) / (n_len * h_len_01), 0.0);
	float phong_02 = max(dot(v_normal, v_h_02) / (n_len * h_len_02), 0.0);
	float phong_03 = max(dot(v_normal, v_h_03) / (n_len * h_len_03), 0.0);

	vec4 fire_01 = lambert_01 * u_light_diffuse * mat_diffuse 
		+ pow(phong_01, u_mat_shininess) * u_light_specular * mat_specular;
	vec4 fire_02 = lambert_02 * u_light_diffuse * mat_diffuse 
		+ pow(phong_02, u_mat_shininess) * u_light_specular * mat_specular;
	vec4 fire_03 = lambert_03 * u_light_diffuse * mat_diffuse 
		+ pow(phong_03, u_mat_shininess) * u_light_specular * mat_specular;

	vec4 global_ambient = vec4(0.1, 0.1, 0.1, 1.0);

	vec4 frag_color = fire_01 + fire_02 + fire_03 + global_ambient;

	gl_FragColor = (1.0 - fog_factor) * frag_color + fog_factor * u_fog_color;
	gl_FragColor.a = opacity;
}
