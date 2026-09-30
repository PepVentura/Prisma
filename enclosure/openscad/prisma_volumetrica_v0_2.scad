include <parametros.scad>;
$fn=64;

// Prisma — volumétrico v0.2
// Maqueta de distribución, no carcasa final.

module envelope(){
    color([0.7,0.7,0.7,0.18])
    hull(){
        cube([outer_w,outer_d,18]);
        translate([8,0,outer_h-18])
            cube([outer_w-16,outer_d,18]);
    }
}

module screen(){
    color([0.08,0.08,0.08])
        cube([screen_w,screen_t,screen_h]);
    // PCB posterior aproximada
    color([0.05,0.3,0.08])
        translate([0,screen_t,8])
            cube([screen_w,6,screen_h-16]);
    // zona provisional de conectores
    color([0.85,0.55,0.1])
        translate([screen_w-18,screen_t+6,screen_h*0.30])
            cube([18,18,35]);
}

module pi5(){ color([0.1,0.3,0.1]) cube([pi_w,pi_d,pi_h]); }
module kabd(){ color([0.2,0.2,0.22]) cube([kabd_w,kabd_d,kabd_h]); }
module dac(){ color([0.25,0.35,0.55]) cube([dac_w,dac_d,dac_h]); }
module buck(){ color([0.55,0.35,0.1]) cube([buck_w,buck_d,buck_h]); }

module speaker(){
    color([0.18,0.18,0.18])
    rotate([90,0,0]) cylinder(d=speaker_d,h=speaker_depth);
}
module pr(){
    color([0.22,0.22,0.22])
    rotate([90,0,0]) cylinder(d=pr_d,h=pr_depth);
}

// Pantalla
if(show_screen)
translate([(outer_w-screen_w)/2,10,outer_h-145])
rotate([-screen_angle,0,0]) screen();

// Altavoz frontal inferior
if(show_audio)
translate([outer_w/2,12,48]) rotate([90,0,0]) speaker();

// Radiador trasero
if(show_audio)
translate([outer_w/2,outer_d-5,65]) rotate([90,0,0]) pr();

// Electrónica
if(show_electronics){
    translate([15,62,outer_h-55]) pi5();
    translate([105,62,outer_h-55]) kabd();
    translate([105,105,outer_h-55]) dac();
    translate([25,105,outer_h-58]) buck();
}

if(show_envelope) envelope();
