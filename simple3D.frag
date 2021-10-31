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

// fog
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

	float s_len = length(v_s);
	float n_len = length(v_normal);
	float h_len = length(v_h);
	
	float lambert = max(dot(v_normal, v_s) / (n_len * s_len), 0.0);
	float phong = max(dot(v_normal, v_h) / (n_len * h_len), 0.0);

	vec4 frag_color = lambert * u_light_diffuse * mat_diffuse
        + pow(phong, u_mat_shininess) * u_light_specular * mat_specular;
	gl_FragColor = (1.0 - fog_factor) * frag_color + fog_factor * u_fog_color;
	gl_FragColor.a = opacity;
}
