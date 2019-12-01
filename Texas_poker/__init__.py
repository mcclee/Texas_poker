import heapq


class Solution:
    def minPushBox(self, grid) -> int:

        def push_dirs(i, j):
            faces = []
            for d in ((0, 1), (0, -1), (-1, 0), (1, 0)):
                r, c = i + d[0], j + d[1]
                if not -1 < r < len(grid) or not -1 < c < len(grid[0]) or grid[r][c] in ('#', 'B'):
                    continue
                faces.append((r, c))
            return faces

        def reachable(m, n, i, j, b1, b2, flt):
            '''
            p: i, j can reach box's face r, c or not
            '''
            args = (m, n, i, j, b1, b2)
            if args in flt:
                return flt[args]
            if i == m and j == n:
                flt[args] = True
                return True
            for d in ((0, 1), (0, -1), (-1, 0), (1, 0)):
                r, c = i + d[0], j + d[1]
                if not -1 < r < len(grid) or not -1 < c < len(grid[0]) or grid[r][c] in ('#', 'B'):
                    continue
                pre = grid[r][c]
                grid[r][c] = '#'
                if reachable(m, n, r, c, b1, b2, flt):
                    grid[r][c] = pre
                    flt[args] = True
                    return True
                grid[r][c] = pre
            flt[args] = False
            return False

        p = [-1, -1]
        b = [-1, -1]
        win = (-1, -1)
        for i in range(len(grid)):
            for j in range(len(grid[0])):
                if grid[i][j] == 'T':
                    win = (i, j)
                if grid[i][j] != 'S' and grid[i][j] != 'B':
                    continue
                if grid[i][j] == 'S':
                    p = [i, j]
                if grid[i][j] == 'B':
                    b = [i, j]
                grid[i][j] = '.'
                if p != [-1, -1] and b != [-1, -1] and win != (-1, -1):
                    break

        if p == [-1, -1] or b == [-1, -1] or win == (-1, -1):
            return -1
        dic = {}
        heap = []
        faces = push_dirs(b[0], b[1])
        for f in faces:
            if reachable(f[0], f[1], p[0], p[1], b[0], b[1], {}):
                dic[(f[0], f[1], b[0], b[1])] = 0
                heap.append([(0, f[0], f[1], b[0], b[1])])

        while heap:
            pos = heapq.heappop(heap)
            if (pos[3], pos[4]) == win:
                return pos[0]
            s1 = grid[pos[1]][pos[2]]
            s2 = grid[pos[3]][pos[4]]
            grid[pos[1]][pos[2]] = 'S'
            grid[pos[3]][pos[4]] = 'B'
            faces = push_dirs(pos[3], pos[4])
            for f in faces:
                d = (f[0] - pos[3], f[1] - pos[4])
                nb = (pos[3] - d[0], pos[4] - d[1])
                if not -1 < nb[0] < len(grid) or not -1 < nb[1] < len(grid[0]) or grid[nb[0]][nb[1]] in ('#', 'B'):
                    continue
                np = (pos[3], pos[4])
                if (np[0], np[1], nb[0], nb[1]) in dic and dic[(np[0], np[1], nb[0], nb[1])] <= pos[0] + 1:
                    continue
                dic[(np[0], np[1], nb[0], nb[1])] = pos[0] + 1
                heapq.heappush(heap, (pos[0] + 1, np[0], np[1], nb[0], nb[1]))
            grid[pos[1]][pos[2]] = s1
            grid[pos[3]][pos[4]] = s2
        return -1


if __name__ == '__main__':
    s = Solution()
    g = [[".",".",".",".",".",".",".",".",".",".",".","."],
         [".",".",".","#","#",".","B",".",".",".",".","."],
         [".",".",".","#",".",".",".",".","#","#",".","."],
         [".",".","#",".",".",".",".",".",".",".",".","."],
         ["#",".","#",".",".",".",".",".",".",".","#","."],
         [".",".",".",".",".",".",".",".","S",".","T","#"],
         [".","#",".",".",".","#",".",".",".",".",".","#"],
         ["#",".",".",".",".","#",".",".","#",".",".","."],
         ["#",".",".","#","#",".",".",".",".",".",".","."],
         [".",".",".",".","#",".","#",".",".",".","#","."],
         [".",".","#",".","#",".",".",".",".",".",".","."],
         [".",".",".",".",".",".",".",".",".",".",".","#"]]
    print(s.minPushBox(g))