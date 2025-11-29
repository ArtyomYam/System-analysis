import json
import numpy as np


def read_json_file(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as file:
        file_content = file.read().strip()
        return file_content


def warshall_algorithm(matrix: np.ndarray) -> np.ndarray:
    """
    Алгоритм Уоршелла для вычисления транзитивного замыкания матрицы
    """
    matrix_size = len(matrix)
    transitive_closure = matrix.copy()
    
    for intermediate in range(matrix_size):
        for source in range(matrix_size):
            for target in range(matrix_size):
                # Если существует путь source->intermediate и intermediate->target
                transitive_closure[source, target] = transitive_closure[source, target] or \
                    (transitive_closure[source, intermediate] and transitive_closure[intermediate, target])
    
    return transitive_closure


def find_connected_components(closure_matrix: np.ndarray) -> list[list[int]]:
    """
    Находит сильно связные компоненты в графе на основе матрицы достижимости
    """
    matrix_size = len(closure_matrix)
    visited_vertices = [False] * matrix_size
    connected_components = []
    
    for current_vertex in range(matrix_size):
        if not visited_vertices[current_vertex]:
            # Начинаем новую компоненту связности
            current_component = []
            for other_vertex in range(matrix_size):
                # Вершины сильно связаны, если достижимы в обе стороны
                if closure_matrix[current_vertex, other_vertex] and closure_matrix[other_vertex, current_vertex]:
                    current_component.append(other_vertex + 1)  # +1 для перехода к 1-индексации
                    visited_vertices[other_vertex] = True
            connected_components.append(sorted(current_component))
    
    return connected_components


def compare_clusters(cluster1: list[int], cluster2: list[int], precedence_matrix: np.ndarray) -> int:
    """
    Сравнивает два кластера на основе матрицы предшествования
    
    Параметры:
    cluster1: первый кластер (список вершин)
    cluster2: второй кластер (список вершин)
    precedence_matrix: матрица предшествования C
    
    Возвращает:
    -1 если cluster1 предшествует cluster2,
    1 если cluster2 предшествует cluster1,
    0 если отношение не определено
    """
    vertex1 = cluster1[0] - 1  # Переход к 0-индексации
    vertex2 = cluster2[0] - 1  # Переход к 0-индексации
    
    if precedence_matrix[vertex1, vertex2] == 1 and precedence_matrix[vertex2, vertex1] == 0:
        return -1  # cluster1 предшествует cluster2
    elif precedence_matrix[vertex1, vertex2] == 0 and precedence_matrix[vertex2, vertex1] == 1:
        return 1   # cluster2 предшествует cluster1
    else:
        return 0   # Отношение не определено


def main(json_ranking_a: str, json_ranking_b: str) -> dict:
    """
    Основная функция для согласования двух ранжировок
    
    Параметры:
    json_ranking_a: JSON-строка с первой ранжировкой
    json_ranking_b: JSON-строка со второй ранжировкой
    
    Возвращает:
    Словарь с ядром противоречий и согласованной ранжировкой
    """
    # Загружаем ранжировки из JSON
    ranking_a = json.loads(json_ranking_a)
    ranking_b = json.loads(json_ranking_b)
    
    # Определяем множество всех объектов из обеих ранжировок
    all_objects = set()
    for ranking in [ranking_a, ranking_b]:
        for cluster in ranking:
            if not isinstance(cluster, list):
                cluster = [cluster]
            all_objects.update(cluster)
    
    # Если нет объектов, возвращаем пустой результат
    if not all_objects:
        return {"kernel": [], "consistent_ranking": []}
    
    # Определяем максимальный номер объекта
    max_object_id = max(all_objects)
    
    def build_precedence_matrix(ranking: list) -> np.ndarray:
        #Стрит матрицу предшествования на основе ранжировки
        # Позиция каждого объекта в ранжировке
        object_positions = [0] * max_object_id
        current_position = 0
        
        # Присваиваем позиции объектам
        for cluster in ranking:
            if not isinstance(cluster, list):
                cluster = [cluster]
            for obj in cluster:
                object_positions[obj - 1] = current_position
            current_position += 1
        
        # Строим матрицу предшествования
        precedence_matrix = np.zeros((max_object_id, max_object_id), dtype=int)
        for i in range(max_object_id):
            for j in range(max_object_id):
                # Объект i предшествует объекту j, если его позиция >= позиции j
                if object_positions[i] >= object_positions[j]:
                    precedence_matrix[i, j] = 1
        
        return precedence_matrix
    
    # Строим матрицы предшествования для обеих ранжировок
    precedence_matrix_a = build_precedence_matrix(ranking_a)
    precedence_matrix_b = build_precedence_matrix(ranking_b)
    
    # Вычисляем матрицу согласованности (логическое И)
    consistency_matrix = precedence_matrix_a * precedence_matrix_b
    
    # Транспонированные матрицы
    transposed_matrix_a = precedence_matrix_a.T
    transposed_matrix_b = precedence_matrix_b.T
    
    # Матрица противоречий (логическое И транспонированных матриц)
    conflict_matrix = transposed_matrix_a * transposed_matrix_b
    
    # Находим ядро противоречий - пары объектов без определенных отношений
    kernel_contradictions = []
    for i in range(max_object_id):
        for j in range(i + 1, max_object_id):
            if consistency_matrix[i, j] == 0 and conflict_matrix[i, j] == 0:
                kernel_contradictions.append([i + 1, j + 1])
    
    # Матрицы частичного порядка
    partial_order_1 = precedence_matrix_a * transposed_matrix_b
    partial_order_2 = transposed_matrix_a * precedence_matrix_b
    
    # Объединенная матрица частичного порядка
    partial_order_union = np.logical_or(partial_order_1, partial_order_2).astype(int)
    
    # Матрица предпочтения (общая согласованность)
    preference_matrix = precedence_matrix_a * precedence_matrix_b
    
    # Добавляем в матрицу предпочтения пары из ядра противоречий
    for pair in kernel_contradictions:
        i, j = pair[0] - 1, pair[1] - 1
        preference_matrix[i, j] = 1
        preference_matrix[j, i] = 1
    
    # Матрица эквивалентности
    equivalence_matrix = preference_matrix * preference_matrix.T
    
    # Транзитивное замыкание матрицы эквивалентности
    equivalence_closure = warshall_algorithm(equivalence_matrix)
    
    # Находим сильно связные компоненты (кластеры эквивалентности)
    equivalence_clusters = find_connected_components(equivalence_closure)
    
    # Строим матрицу порядка между кластерами
    num_clusters = len(equivalence_clusters)
    cluster_order_matrix = np.zeros((num_clusters, num_clusters), dtype=int)
    
    for i in range(num_clusters):
        for j in range(num_clusters):
            if i != j:
                # Берем первый элемент каждого кластера для сравнения
                element_i = equivalence_clusters[i][0] - 1
                element_j = equivalence_clusters[j][0] - 1
                if preference_matrix[element_i, element_j] == 1:
                    cluster_order_matrix[i, j] = 1
    
    # Топологическая сортировка кластеров
    visited_clusters = [False] * num_clusters
    topological_order = []
    
    def topological_sort(current_cluster: int):
        """Рекурсивная функция топологической сортировки"""
        visited_clusters[current_cluster] = True
        for next_cluster in range(num_clusters):
            if cluster_order_matrix[current_cluster, next_cluster] == 1 and not visited_clusters[next_cluster]:
                topological_sort(next_cluster)
        topological_order.append(current_cluster)
    
    for cluster_idx in range(num_clusters):
        if not visited_clusters[cluster_idx]:
            topological_sort(cluster_idx)
    
    topological_order.reverse()
    
    # Строим согласованную ранжировку
    consistent_ranking = []
    for cluster_idx in topological_order:
        current_cluster = equivalence_clusters[cluster_idx]
        if len(current_cluster) == 1:
            consistent_ranking.append(current_cluster[0])
        else:
            consistent_ranking.append(current_cluster)
    
    return {
        "kernel": kernel_contradictions,
        "consistent_ranking": consistent_ranking
    }


if __name__ == "__main__":
    json_ranking_a = read_json_file('range_a.json')
    json_ranking_b = read_json_file('range_b.json')
    json_ranking_c = read_json_file('range_c.json')
    
    print("СРАВНЕНИЕ РАНЖИРОВОК")
    print("=" * 50)
    
    # Сравнение ранжировок A и B
    print("\nСравнение range_a.json и range_b.json:")
    comparison_result_ab = main(json_ranking_a, json_ranking_b)
    print(f"Ядро противоречий: {comparison_result_ab['kernel']}")
    print(f"Согласованная ранжировка: {comparison_result_ab['consistent_ranking']}")
    
    # Сравнение ранжировок A и C
    print("\nСравнение range_a.json и range_c.json:")
    comparison_result_ac = main(json_ranking_a, json_ranking_c)
    print(f"Ядро противоречий: {comparison_result_ac['kernel']}")
    print(f"Согласованная ранжировка: {comparison_result_ac['consistent_ranking']}")
    
    # Сравнение ранжировок B и C
    print("\nСравнение range_b.json и range_c.json:")
    comparison_result_bc = main(json_ranking_b, json_ranking_c)
    print(f"Ядро противоречий: {comparison_result_bc['kernel']}")
    print(f"Согласованная ранжировка: {comparison_result_bc['consistent_ranking']}")
    
    print("\n" + "=" * 50)