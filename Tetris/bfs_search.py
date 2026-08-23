from collections import deque
from rotation_masks import ROTATIONS
from bfs_kicks import KICK_DIFFS

def bfs_positions(state):
    queue = deque([(state.piece.x, state.piece.y, state.rotation_idx)])
    visited = set()
    legal_positions = []

    while queue:
        (x, y, rot) = queue.pop()
        if (x, y, rot) in visited:
            continue
        visited.add((x, y, rot)) 

        shape = ROTATIONS[state.piece.name][rot]
        if not state.grid.can_fit_shape(shape, x, y+1):
            legal_positions.append((x, y, rot))

        for action in ["left", "right", "down", "cw", "ccw", "rot180"]:
            nx, ny, nrot = x, y, rot
            nshape = shape
            valid = False

            if action == "left":
                nx -= 1
                valid = state.grid.can_fit_shape(nshape, nx, ny)
            elif action == "right":
                nx += 1
                valid = state.grid.can_fit_shape(nshape, nx, ny)
            elif action == "down":
                ny += 1
                valid = state.grid.can_fit_shape(nshape, nx, ny)

            elif action in ["cw", "ccw", "rot180"]:
                # if state.piece.name == 1:
                #     continue
                idx = 1 if action == "cw" else -1 if action == "ccw" else 2
                nrot = (rot - idx) % 4
                new_shape = ROTATIONS[state.piece.name][nrot]
                if idx != 2 and state.piece.name != 1:
                    if state.piece.name == 7:
                        offsets = KICK_DIFFS['I'][rot][nrot]
                    else:
                        offsets = KICK_DIFFS['JLTSZ'][rot][nrot]
                else:
                    if state.piece.name == 1:
                        offsets = KICK_DIFFS['O'][rot][nrot]
                    else:
                        offsets = KICK_DIFFS['180'][rot]

                for dx, dy in offsets:
                    nx, ny = x + dx, y + dy
                    success = state.grid.can_fit_shape(new_shape, x + dx, y + dy)
                    if success:
                        nshape = new_shape
                        valid = True
                        break

            if valid and (nx,ny,nrot) not in visited:
                queue.append((nx, ny, nrot))
    return legal_positions