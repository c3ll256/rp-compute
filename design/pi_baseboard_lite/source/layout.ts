// Prototype board envelope retained; final enclosure fit is not qualified.
export const board = { width: "70mm", height: "104mm" };
// Provisional M2 fixture holes; do not infer existing shell boss compatibility.
export const mountingHoles = [
 {name:"H1",x:-30,y:47},{name:"H2",x:30,y:47},
 {name:"H3",x:-30,y:-47},{name:"H4",x:30,y:-47}
];
export function rotationForOpening(native: "up" | "right" | "down" | "left", target: "up" | "right" | "down" | "left") {
 const angle = {right:0, up:90, left:180, down:270};
 return (angle[target] - angle[native] + 360) % 360;
}
export const interfaces = {
 piDock: {x:-13.5,y:15.2,rotation:90,side:"bottom"},
 displayFpc: {x:0,y:6.7,rotation:rotationForOpening("down","down"),side:"top",contactFace:"toward PCB",opening:"-Y in board top view"},
 // Native female socket origin is pin 1; opposite row order to male header; center (0,-34).
 frontModule: {x:-3.81,y:-32.73,rotation:90,side:"top",mating:"+Z"}
};
