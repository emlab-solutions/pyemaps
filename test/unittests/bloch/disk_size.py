from pyemaps import PKG_TYPE, DEF_DSIZE_LIMITS, TYPE_FREE
free_max_disk_size = 0.5
full_max_disk_size = 1.0


if __name__ == '__main__':
    from pyemaps import dif

    if PKG_TYPE == TYPE_FREE:
        assert abs(DEF_DSIZE_LIMITS[1] - free_max_disk_size) < 0.001, \
        f'Disk max limit set at: {free_max_disk_size} does not match defined limit {DEF_DSIZE_LIMITS[1]}'
        print(f'Disk max limit set at: {free_max_disk_size} matches free package limit {DEF_DSIZE_LIMITS[1]}')
    else:
        assert abs(DEF_DSIZE_LIMITS[1] - full_max_disk_size) < 0.001, \
        f'Disk max limit set at: {full_max_disk_size} does not match defined limit {DEF_DSIZE_LIMITS[1]}'
        print(f'Disk max limit set at: {full_max_disk_size} matches free package limit {DEF_DSIZE_LIMITS[1]}')