from pyemaps import PKG_TYPE, DEF_DSIZE_LIMITS
free_max_disk_size = 0.5
full_max_disk_size = 1.0


if __name__ == '__main__':
    from pyemaps import dif
    TYPE_FREE = 1
    TYPE_FULL = 2
    TYPE_UIUC = 3

#     pkg_type = dif.get_pkgtype()
    
    assert PKG_TYPE == TYPE_FREE and DEF_DSIZE_LIMITS[1] == free_max_disk_size, \
        f'Disk max limit set at: {free_max_disk_size} does not match defined limit {DEF_DSIZE_LIMITS[1]}'
    
    print(f'Disk max limit set at: {free_max_disk_size} matches free package limit {DEF_DSIZE_LIMITS[1]}')

    assert PKG_TYPE == TYPE_FULL and DEF_DSIZE_LIMITS[1] == full_max_disk_size, \
        f'Disk max limit set at: {full_max_disk_size} does not match defined limit {DEF_DSIZE_LIMITS[1]}'
    
    
    print(f'Disk max limit set at: {full_max_disk_size} matches free package limit {DEF_DSIZE_LIMITS[1]}')