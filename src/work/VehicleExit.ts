/** Candidate feet positions in the vehicle's projected forward/right basis.
 * +Z is vehicle forward; never derive the side from a camera yaw or Euler.y. */
export function vehicleExitCandidates(position: { x: number; y: number; z: number }, forward: { x: number; z: number }, radius: number): { x: number; y: number; z: number }[] {
    const length = Math.hypot(forward.x, forward.z);
    const fx = length > .001 ? forward.x / length : 0;
    const fz = length > .001 ? forward.z / length : 1;
    const result = [];
    // Door sides first, then the opposite side, rear and front with more room.
    for (const clearance of [1.25 + radius + .25, 2.5 + radius, 4 + radius]) {
        for (const [side, along] of [[1, .15], [-1, .15], [1, -1.2], [-1, -1.2], [0, -3], [0, 3]]) {
            result.push({ x: position.x + fz * side! * clearance + fx * along!, y: position.y,
                z: position.z - fx * side! * clearance + fz * along! });
        }
    }
    return result;
}
