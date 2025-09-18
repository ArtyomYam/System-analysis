def main(graph_string: str) -> list[list[bool]]:
    #Преобразует строковое представление графа в матрицу смежности

    edges = graph_string.strip().split('\n')

    # Определяем множество всех вершин графа
    vertices = set()
    for edge in edges:
        if edge:
            v1, v2 = edge.split(',')
            vertices.update([v1, v2])

    adjacency_matrix = []
    num_vertices = len(vertices)
    
    for i in range(num_vertices):
        adjacency_matrix.append([0] * num_vertices)

    # Заполняем матрицу смежности на основе ребер
    for edge in edges:
        if edge:  # Пропускаем пустые строки
            v1, v2 = edge.split(',')
            # Преобразуем номера вершин в индексы (начиная с 0)
            idx1, idx2 = int(v1) - 1, int(v2) - 1
            
            # Устанавливаем симметричные значения для неориентированного графа
            adjacency_matrix[idx1][idx2] = 1
            adjacency_matrix[idx2][idx1] = 1

    return adjacency_matrix


def read_csv(file_path: str) -> str:
    graph_data = ""
    
    with open(file_path, 'r', encoding='utf-8') as csv_file:
        graph_data = ''.join(csv_file.readlines())
    
    return graph_data


def test1():
    """
    Тестирующая функция для проверки корректности работы main()
    Сравнивает результат работы функции с ожидаемой матрицей смежности
    """
    csv_file_path = 'data/task2.csv'
    
    # Ожидаемая матрица смежности для тестового графа
    expected_adjacency_matrix = [
        [0, 1, 1, 0, 0],
        [1, 0, 0, 0, 0],
        [1, 0, 0, 1, 1],
        [0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0]
    ]

    result_matrix = main(read_csv(csv_file_path))

    assert expected_adjacency_matrix == result_matrix, "Полученная матрица не соответствует ожидаемой!"


if __name__ == "__main__":
    try:
        test1()
    except AssertionError:
        print("Тест не пройден")
    else:
        print("Тест пройден успешно!")