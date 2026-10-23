import manifest from './paris-lift.json';
import type { Object3D } from 'three';
import type { PlayerController } from 'engine/player/PlayerController.js';
import type { GameHUD } from './GameHUD.js';

/** Two-way elevator with a short enclosed-cabin transition. No input repeats while held. */
export class ParisLift {
    private held = false;
    private remaining = 0;
    private destination = 0;
    private arrived = false;
    get traveling(): boolean { return this.remaining > 0; }
    private overlay: HTMLDivElement;
    constructor(private controller: PlayerController, private hud: GameHUD) {
        controller.registerCustomAction({ action: 'parisLift', desktop: { keys: ['KeyL'] }, mobile: { label: 'LIFT', behavior: 'tap' } });
        hud.createIconText('paris-lift', { anchor: 'bottom-center', icon: '', text: '' });
        this.overlay = document.createElement('div');
        this.overlay.style.cssText = 'position:absolute;inset:0;background:#080b10;opacity:0;pointer-events:none;z-index:100;display:flex;align-items:center;justify-content:center;color:#e9c58a;font:16px Georgia,serif;letter-spacing:3px;transition:opacity .25s';
        document.body.appendChild(this.overlay);
    }
    update(dt: number, player: Object3D): void {
        const pressed = !!this.controller.keys.parisLift;
        const fresh = pressed && !this.held;
        this.held = pressed;
        if (this.remaining > 0) {
            this.remaining = Math.max(0, this.remaining - dt);
            if (this.remaining <= .6 && !this.arrived) {
                const landing = this.destination > 0 ? manifest.paris.liftTop : manifest.paris.liftGround;
                this.controller.teleportTo(landing[0]!, landing[1]!, landing[2]!);
                this.arrived = true;
            }
            if (this.remaining <= .35) this.overlay.style.opacity = '0';
            if (this.remaining === 0) {
                this.overlay.textContent = '';
                this.hud.showToast(this.destination > 0 ? 'Eiffel observation deck • 140 m above the Strip' : 'Paris casino • Ground floor', { variant: 'success' });
            }
            return;
        }
        const p = player.position;
        const cx = manifest.paris.towerCenter[0]!, cz = manifest.paris.towerCenter[2]!;
        const c = Math.cos(manifest.paris.towerYaw), s = Math.sin(manifest.paris.towerYaw);
        const localX = c * (p.x - cx) - s * (p.z - cz);
        const localZ = s * (p.x - cx) + c * (p.z - cz);
        const inCabin = Math.abs(localX) < 1.8 && Math.abs(localZ) < 1.45;
        const atGround = Math.abs(p.y) < 2;
        const atTop = Math.abs(p.y - 140) < 2;
        const available = inCabin && (atGround || atTop) && !this.controller.isPlayerInVehicle();
        this.hud.updateIconText('paris-lift', { text: available ? `L / LIFT • ${atGround ? 'Ascend to observation deck · 140 m' : 'Return to Paris casino'}` : '' });
        if (available && fresh) {
            this.arrived = false;
            this.destination = atGround ? 140 : 0;
            this.remaining = 1.5;
            this.overlay.textContent = atGround ? 'EIFFEL TOWER  /  ASCENDING' : 'EIFFEL TOWER  /  DESCENDING';
            this.overlay.style.opacity = '1';
        }
    }
    dispose(): void { this.overlay.remove(); }
}
