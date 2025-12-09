from models.Matrices import Matrices
import traceback

tests = {
    'example3': [[1,3,-3],[2,0,1],[-1,4,-2]],
    '4x4': [[2,3,4,5],[1,0,-1,2],[0,-2,1,0],[3,0,2,1]],
    '4x4_bad': [[1,2,3,4],[5,6,7,8],[9,10,11,12],[13,14,15,16]],
    '5x5': [[1,2,3,4,5],[0,1,2,3,4],[1,0,1,0,1],[2,1,0,1,0],[0,1,2,1,0]]
}

for name, m in tests.items():
    print('\n=== TEST', name, 'size', len(m), 'x', len(m[0]) if m else 0)
    try:
        det, pasos = Matrices.determinant_cofactor_with_steps(m)
        print('det =', det)
        for i, line in enumerate(pasos):
            print(line)
            if i>80:
                break
    except Exception as e:
        print('ERROR:', e)
        traceback.print_exc()
