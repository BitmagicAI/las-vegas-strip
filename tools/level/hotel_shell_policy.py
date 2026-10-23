"""Keep streamed guest clearance separate from the exterior's render shell."""
from mathutils import Vector


def preserve_render_shell(obj):
    # Bellagio's tower starts above the 8.0 m casino ceiling. Its shell is
    # explicitly hidden by BuildingVisibility while occupying guest interiors;
    # cutting it as well exposes the uninstantiated rooms to the street.
    # Keep the podium/ceiling cuts, which connect the casino to the stairs.
    return (obj.type == 'MESH' and obj.name.startswith('Bellagio ')
            and min((obj.matrix_world @ Vector(p)).z for p in obj.bound_box) >= 8.299)
