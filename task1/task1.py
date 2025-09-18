import numpy as np


def read_csv(file_path: str) -> str:
    graph_content = ""

    with open(file_path, 'r') as csv_file:
        graph_content = ''.join(csv_file.readlines())

    return graph_content


def make_orient_adj_matrix(graph_string: str) -> np.ndarray[bool]:
    #Создаёт матрицу смежности для ориентированного графа.

    # Преобразуем строку в список ребер (кортежей вершин)
    edge_list: list[tuple[str, str]] = [tuple(edge.split(',')) for edge in graph_string.strip().split('\n') if edge]

    # Определяем множество всех уникальных вершин
    vertex_set = set()
    
    for edge in edge_list:
        source_vertex, target_vertex = edge[0], edge[1]
        vertex_set.update([source_vertex, target_vertex])
    

    sorted_vertices = sorted(list(vertex_set))

    vertex_to_index = {vertex: idx for idx, vertex in enumerate(sorted_vertices)}
    
    adjacency_matrix = np.zeros((len(sorted_vertices), len(sorted_vertices)), dtype=bool)
    
    # Заполняем матрицу смежности на основе ребер
    for edge in edge_list:
        source_vertex, target_vertex = edge[0], edge[1]
        # Устанавливаем связь от источника к цели (ориентированный граф)
        adjacency_matrix[vertex_to_index[source_vertex], vertex_to_index[target_vertex]] = True

    return adjacency_matrix


def compute_r1(adjacency_matrix: np.ndarray[bool]) -> np.ndarray[int]:
    return adjacency_matrix.astype(int)


def compute_r2(r1_matrix: np.ndarray[int]) -> np.ndarray[int]:
    #Вычисляет матрицу R2 - транспонированную матрицу R1
    return r1_matrix.T


def compute_r3(adjacency_matrix: np.ndarray[bool]) -> np.ndarray[int]:
    r3_matrix = adjacency_matrix.copy()

    # Вычисляем транзитивное замыкание для путей длины до n-1
    for _ in range(adjacency_matrix.shape[0] - 1):
        # Используем матричное умножение с логическим ИЛИ для булевой алгебры
        r3_matrix = r3_matrix | (r3_matrix @ adjacency_matrix)

    r3_matrix = (r3_matrix & ~adjacency_matrix).astype(int)

    return r3_matrix


def compute_r4(r3_matrix: np.ndarray[int]) -> np.ndarray[int]:
    return r3_matrix.T


def compute_r5(r2_matrix: np.ndarray[int]) -> np.ndarray[int]:

    r2_bool = r2_matrix.copy().astype(bool)
    matrix_size = r2_bool.shape[0]
    r5_matrix = np.zeros((matrix_size, matrix_size), dtype=int)

    # Проверяем каждую пару вершин на наличие общего родителя
    for i in range(matrix_size):
        for j in range(i + 1, matrix_size):
            # Если есть хотя бы один общий элемент в строках (общий родитель)
            if np.any(r2_bool[i] & r2_bool[j]):
                r5_matrix[i, j], r5_matrix[j, i] = 1, 1  # Симметричная матрица
    
    return r5_matrix


def main(graph_string: str, root_vertex: str) -> tuple[list[list[int]], list[list[int]], list[list[int]], list[list[int]], list[list[int]]]:
    # Создаем матрицу смежности ориентированного графа
    adjacency_matrix = make_orient_adj_matrix(graph_string)
    
    # Вычисляем все матрицы отношений
    r1_matrix = compute_r1(adjacency_matrix)
    r2_matrix = compute_r2(r1_matrix)
    r3_matrix = compute_r3(adjacency_matrix)
    r4_matrix = compute_r4(r3_matrix)
    r5_matrix = compute_r5(r2_matrix)


    return (
        r1_matrix.tolist(),
        r2_matrix.tolist(),
        r3_matrix.tolist(),
        r4_matrix.tolist(),
        r5_matrix.tolist()
    )


if __name__ == "__main__":

    csv_file_path = 'data/task2.csv'
    

    result_matrices = main(read_csv(csv_file_path), '1')
    

    for i, matrix in enumerate(result_matrices):
        print(f"Матрица R{i+1}:")
        for row in matrix:
            print(row)
        print("\n" + "="*40 + "\n")