fn verify_phase1(x: [Field; 150], y: [Field; 150]) {
    for i in 0..x.len() {
        assert(x[i] == y[i], "x and y must be equal");
    }
}

fn verify_phase2(x: [Field; 150], y: [Field; 150]) {
    for i in 0..x.len() {
        assert(x[i] == y[i], "x and y must be different");
    }
}

fn verify_gkr(x: [Field; 150], y: [Field; 150]) {
    for i in 0..x.len() {
        assert(x[i] == y[i], "x and y must be equal");
    }
}

fn verify_input(x: [Field; 150], y: [Field; 150]) {
    for i in 0..x.len() {
        assert(x[i] == y[i], "x and y must be equal");
    }
}

fn main(
    phase_1_left: [Field; 150],
    phase_1_right: [Field; 150],
    phase_2_left: [Field; 150],
    phase_2_right: [Field; 150],
    gkr_left: [Field; 150],
    gkr_right: [Field; 150],
    input_left: [Field; 150],
    input_right: [Field; 150]
) {
    verify_phase1(phase_1_left, phase_1_right);
    verify_phase2(phase_2_left, phase_2_right);
    verify_gkr(gkr_left, gkr_right);
    verify_input(input_left, input_right);
}

