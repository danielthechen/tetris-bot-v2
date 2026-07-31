import copy
from kicks import I_OFFSET_DATA, O_OFFSET_DATA, JLTSZ_OFFSET_DATA, KICKS_180

def bfs_move_piece(grid, piece, move_x, move_y):
    if grid.can_fit_shape(
        piece.shape, piece.x + move_x, piece.y + move_y
    ):
        piece.move(move_x, move_y)
        return True
    return False

def bfs_rotate_piece(grid, piece, old_orientation, idx):
    new_shape = piece.rotate(idx)
    new_orientation = (old_orientation - idx) % 4

    if idx != 2:
        if piece.name == 'I':
            data = I_OFFSET_DATA
        elif piece.name == 'O':
            data = O_OFFSET_DATA
        else:
            data = JLTSZ_OFFSET_DATA
        offsets = [tuple(a - b for a,b in zip(t1, t2)) for t1,t2 in zip(data[old_orientation],data[new_orientation])]
    else:
        offsets = KICKS_180[old_orientation]


    for dx, dy in offsets:
        if grid.can_fit_shape(new_shape, piece.x + dx, piece.y + dy):
            piece.shape = new_shape
            piece.x += dx
            piece.y += dy
            return new_orientation
    return old_orientation

def bfs_positions(state):
    queue = [(state.piece.x, state.piece.y, state.rotation_idx, state.piece.shape)]
    visited = set()
    legal_positions = []

    while queue:
        (x, y, rot, shape) = queue.pop()
        if (x, y, rot) in visited:
            continue
        visited.add((x, y, rot)) 

        if not state.grid.can_fit_shape(shape, x, y+1):
            legal_positions.append((x, y, rot, shape))

        for action in ["left", "right", "down", "cw", "ccw", "rot180"]:
            temp_state = copy.deepcopy(state)
            temp_state.piece.x = x
            temp_state.piece.y = y
            temp_state.rotation_idx = rot
            temp_state.piece.shape = copy.deepcopy(shape)

            valid = False
            if action == "left":
                valid = bfs_move_piece(temp_state.grid, temp_state.piece, -1, 0)
            elif action == "right":
                valid = bfs_move_piece(temp_state.grid, temp_state.piece, 1, 0)
            elif action == "down":
                valid = bfs_move_piece(temp_state.grid, temp_state.piece, 0, 1)
            elif action == "cw":
                new_rot = bfs_rotate_piece(temp_state.grid, temp_state.piece, rot, 1)
                valid = new_rot != rot
                temp_state.rotation_idx = new_rot
            elif action == "ccw":
                new_rot = bfs_rotate_piece(temp_state.grid, temp_state.piece, rot, -1)
                valid = new_rot != rot
                temp_state.rotation_idx = new_rot
            elif action == "rot180":
                new_rot = bfs_rotate_piece(temp_state.grid, temp_state.piece, rot, 2)
                valid = new_rot != rot
                temp_state.rotation_idx = new_rot
            if valid:
                queue.append((temp_state.piece.x,
                              temp_state.piece.y,
                              temp_state.rotation_idx,
                              temp_state.piece.shape))
    return legal_positions