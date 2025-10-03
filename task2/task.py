import math
import itertools
import numpy as np



def read_csv(path: str) -> str:
    """Чтение графа из CSV файла"""
    with open(path, 'r') as csv:
        return ''.join(csv.readlines())



def compute_r1(adj_matr: np.ndarray) -> np.ndarray:
    return adj_matr.astype(int)



def compute_r2(r1: np.ndarray) -> np.ndarray:
    return r1.T



def compute_r3(adj_matr: np.ndarray) -> np.ndarray:
    r3 = adj_matr.copy()
    n = adj_matr.shape[0]
    
    for _ in range(n - 1):
        r3 = r3 | (r3 @ adj_matr)
    
    r3 = (r3 & ~adj_matr).astype(int)
    return r3



def compute_r4(r3: np.ndarray) -> np.ndarray:
    return r3.T



def compute_r5(r2: np.ndarray) -> np.ndarray:
    r2_bool = r2.astype(bool)
    n = r2.shape[0]
    r5 = np.zeros((n, n), dtype=int)
    
    for i in range(n):
        for j in range(i + 1, n):
            if np.any(r2_bool[i] & r2_bool[j]):
                r5[i, j] = 1
                r5[j, i] = 1
    return r5



def calculate_entropy(perm_edges, vert_index) -> tuple[float, float]:
    n = len(vert_index)
    adj = np.zeros((n, n), dtype=bool)
    for v1, v2 in perm_edges:
        i = vert_index[v1]
        j = vert_index[v2]
        adj[i, j] = True

    r1 = compute_r1(adj)
    r2 = compute_r2(r1)
    r3 = compute_r3(adj)
    r4 = compute_r4(r3)
    r5 = compute_r5(r2)
    r_union = [r1, r2, r3, r4, r5]

    n = r_union[0].shape[0]
    total_entropy = 0.0
    
    for matrix in r_union:
        for i in range(n):
            for j in range(n):
                if i != j:
                    p_ij = matrix[i, j] / (n - 1)
                    if p_ij > 0:
                        total_entropy += p_ij * math.log2(p_ij)
    
    H = -total_entropy
    H_max = (1 / math.e) * n * len(r_union)

    if H_max > 0:
        h = H / H_max
    else:
        h = 0
    
    return H, h


def generate_edge_permutations(edges: list[tuple[str, str]], vertexes: list[str]) -> list[list[tuple[str, str]]]:
    all_possible_edges = [
        (v1, v2) for v1 in vertexes for v2 in vertexes 
        if v1 != v2
    ]

    existing_edges_set = set(edges)
    possible_new_edges = [edge for edge in all_possible_edges if edge not in existing_edges_set]
    
    permutations = []
    for remove_idx, new_edge in itertools.product(range(len(edges)), possible_new_edges):
        new_edges = edges.copy()
        new_edges[remove_idx] = new_edge
        permutations.append(new_edges)
    
    return permutations



def main(s: str, e: str) -> tuple[float, float]:
    edges: list[tuple[str, str]] = [tuple(edge.split(',')) for edge in s.split('\n')]
    vertexes = set()

    for edge in edges:
        v1, v2 = edge[0], edge[1]
        vertexes.update(v1, v2)
    
    vertexes = sorted(list(vertexes))

    vert2indx = {v: i for i, v in enumerate(vertexes)}

    all_permutations = generate_edge_permutations(edges, vertexes)
    
    best_H = -float('inf')
    best_h = 0
    best_edges = None
    
    for perm_edges in all_permutations:
        H, h_val = calculate_entropy(perm_edges, vert2indx)
        
        if H > best_H:
            best_H = H
            best_h = h_val
            best_edges = perm_edges.copy()

    if best_edges:
        print(f"\nНайдена лучшая перестановка:\nБыло: {edges}\nСтало: {best_edges}")
    
    return best_H, best_h



if __name__ == "__main__":
    csv_path = 'data/task2.csv'

    graph_string: str = read_csv(csv_path)
    
    eroot = '1'
    
    # Оптимизация графа
    H, h = main(graph_string, eroot)
    
    print(f"H(M, R): {H}")
    print(f"h(M, R): {h}")