

from pyemaps import PKG_TYPE, TYPE_FREE, TYPE_FULL, TYPE_UIUC

def test_pkg_type():
    if PKG_TYPE == TYPE_FULL:
        print(f'Current package type is full')
        return TYPE_FULL
    
    if PKG_TYPE == TYPE_FREE:
        print(f'Current package type is free')
        return TYPE_FREE

    if PKG_TYPE == TYPE_UIUC:
        print(f'Current package type is UIUC')
        return TYPE_UIUC

    print(f'Current package type is UNKNOWNN!')
    return -1

def main():
    # import sys
    print('\n*****unit test for package types started*****\n')
    
    pType = test_pkg_type()
    if pType == TYPE_FREE:
        print("*******Free package detected, no license required")
        print("####SUCCESS####")
        return 0
    
    try:
        from pyemaps import stem4d
    except stem4d.EmapsLicenseError as e:
        print(f'License check error: {e}')
    except RuntimeError as e:
        print(f"4d stem module import runtime error: {e}")
    except Exception as e:
        print(f"Other 4d stem module import error: {e}")

    print(f'*****License check successful!')
    
if __name__ == '__main__':
    print(f'beginning of testing')
    main()