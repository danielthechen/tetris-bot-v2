from collections import deque
from rotation_masks import ROTATIONS, ROTATION_OFFSETS
from dfs_kicks import KICK_DIFFS

def dfs_positions(state):
    queue = deque([(state.piece.x, state.piece.y, state.rotation_idx)])
    visited = set()
    legal_positions = []

    while queue:
        (x, y, rot) = queue.pop()
        if (x, y, rot) in visited:
            continue
        visited.add((x, y, rot)) 

        shape_offsets = ROTATION_OFFSETS[state.piece.name][rot]
        if not state.grid.can_fit_shape_offsets(shape_offsets, x, y+1):
            legal_positions.append((x, y, rot))

        for action in [1, #left
                       2,  #right
                       3,  # down
                       4,  #cw
                       5,  #ccw
                       6 #rot180
                       ]:
            nx, ny, nrot = x, y, rot
            noffsets = shape_offsets
            valid = False

            if action == 1:
                nx -= 1
                valid = state.grid.can_fit_shape_offsets(noffsets, nx, ny)
            elif action == 2:
                nx += 1
                valid = state.grid.can_fit_shape_offsets(noffsets, nx, ny)
            elif action == 3:
                ny += 1
                valid = state.grid.can_fit_shape_offsets(noffsets, nx, ny)

            elif action in [4, 5, 6]:
                # if state.piece.name == 1:
                #     continue
                idx = 1 if action == 4 else -1 if action == 5 else 2
                nrot = (rot - idx) % 4
                new_offsets = ROTATION_OFFSETS[state.piece.name][nrot]
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
                    success = state.grid.can_fit_shape_offsets(new_offsets, x + dx, y + dy)
                    if success:
                        noffsets = new_offsets
                        valid = True
                        break

            if valid and (nx,ny,nrot) not in visited:
                queue.append((nx, ny, nrot))
    return legal_positions