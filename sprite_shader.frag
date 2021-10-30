uniform sampler2D u_tex01;
uniform sampler2D u_tex02;

uniform float u_opacity;
uniform float u_using_alpha_texture;

varying vec2 v_uv;

void main(void) {
	vec4 color = texture2D(u_tex01, v_uv);
	float opacity = u_opacity;

	if (u_using_alpha_texture == 1.0) {
		opacity *= texture2D(u_tex02, v_uv).r;
	}

	if (opacity < 0.01) {
		discard;
	}

	gl_FragColor = color;
	gl_FragColor.a = opacity;
}
