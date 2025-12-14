import json


def read_json_file(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as json_file:
        json_content = json_file.read()
    return json_content


def parse_fuzzy_terms_json(json_string: str) -> dict:
    parsed_data = json.loads(json_string)
    temperature_terms = parsed_data['температура']
    
    fuzzy_terms_dict = dict()
    for term_data in temperature_terms:
        term_id = term_data["id"]
        term_points = term_data["points"]
        fuzzy_terms_dict[term_id] = term_points
    
    return fuzzy_terms_dict


def linear_interpolation(x_start: float, y_start: float, 
                         x_end: float, y_end: float, 
                         x_value: float) -> float:
    """
    Выполняет линейную интерполяцию между двумя точками
    
    Параметры:
    x_start, y_start: координаты начальной точки
    x_end, y_end: координаты конечной точки
    x_value: координата X для которой вычисляется Y
    
    Возвращает:
    Интерполированное значение Y для заданного X
    """
    if x_start == x_end:
        return y_start
    return y_start + (y_end - y_start) * (x_value - x_start) / (x_end - x_start)


def calculate_trapezoidal_membership(fuzzy_terms: dict, 
                                     term_name: str, 
                                     input_value: float) -> float:
    """
    Вычисляет значение функции принадлежности для трапециевидного терма
    """
    if term_name not in fuzzy_terms:
        return 0.0
    
    # Извлекаем координаты вершин трапеции
    (x1, y1), (x2, y2), (x3, y3), (x4, y4) = fuzzy_terms[term_name]
    
    # Проверяем области определения трапециевидной функции
    if input_value <= x1:
        return y1  # Левая граница
    
    elif input_value >= x4:
        return y4  # Правая граница
    
    elif x1 <= input_value <= x2:
        # Восходящий склон трапеции
        return linear_interpolation(x1, y1, x2, y2, input_value)
    
    elif x2 <= input_value <= x3:
        # Верхнее плато трапеции
        return linear_interpolation(x2, y2, x3, y3, input_value)
    
    elif x3 <= input_value <= x4:
        # Нисходящий склон трапеции
        return linear_interpolation(x3, y3, x4, y4, input_value)
    
    else:
        return 0.0


def determine_output_range(terms_dict: dict) -> tuple[float, float]:
    """
    Определяет диапазон выходной переменной на основе всех терминов
    """
    all_x_coordinates = []
    for term_points in terms_dict.values():
        for x_coord, _ in term_points:
            all_x_coordinates.append(x_coord)
    
    return min(all_x_coordinates), max(all_x_coordinates)


def generate_discrete_domain(min_value: float, max_value: float, 
                             num_points: int = 1000) -> list[float]:
    return [
        min_value + i * (max_value - min_value) / (num_points - 1)
        for i in range(num_points)
    ]


def load_all_input_data(temperature_json: str, 
                        heat_level_json: str, 
                        mapping_json: str):

    temperature_terms = parse_fuzzy_terms_json(temperature_json)
    heat_level_terms = parse_fuzzy_terms_json(heat_level_json)
    inference_rules = json.loads(mapping_json)
    
    return temperature_terms, heat_level_terms, inference_rules


def apply_fuzzy_inference_rules(temperature_terms: dict, 
                                heat_level_terms: dict, 
                                inference_rules: list, 
                                current_temperature: float, 
                                output_domain: list[float]) -> list[float]:
    """
    Применяет все правила нечёткого вывода для агрегации результатов
    """
    aggregated_membership = [0.0] * len(output_domain)
    
    for rule in inference_rules:
        temperature_term, heat_level_term = rule[0], rule[1]
        
        # Вычисляем степень активации правила (min-активация)
        rule_activation = calculate_trapezoidal_membership(
            temperature_terms, temperature_term, current_temperature
        )
        
        # Если правило активировано, применяем его
        if rule_activation > 0:
            for i, output_value in enumerate(output_domain):
                # Вычисляем принадлежность выходного терма
                output_membership = calculate_trapezoidal_membership(
                    heat_level_terms, heat_level_term, output_value
                )
                
                # Агрегируем результаты по максимуму (max-агрегация)
                aggregated_membership[i] = max(
                    aggregated_membership[i], 
                    min(rule_activation, output_membership)  # Операция min для импликации
                )
    
    return aggregated_membership


def defuzzify_centroid(aggregated_membership: list[float], 
                       output_domain: list[float], 
                       min_value: float, 
                       max_value: float) -> float:
    #Выполняет дефаззификацию методом центра тяжести
    max_membership = max(aggregated_membership)
    
    # Если ни одно правило не сработало
    if max_membership == 0:
        return (min_value + max_value) / 2  # Возвращаем середину диапазона
    
    # Ищем первое значение с максимальной принадлежностью
    for i, membership_value in enumerate(aggregated_membership):
        if membership_value == max_membership:
            return output_domain[i]
    
    return output_domain[0]


def main(temperature_json: str, 
         heat_level_json: str, 
         mapping_json: str, 
         current_temperature: float) -> float:

    #Основная функция нечёткого вывода

    # Загружаем и парсим входные данные
    temperature_terms, heat_level_terms, inference_rules = load_all_input_data(
        temperature_json, heat_level_json, mapping_json
    )
    
    # Определяем диапазон выходной переменной
    output_min, output_max = determine_output_range(heat_level_terms)
    
    # Генерируем дискретный диапазон для выходной переменной
    output_domain_values = generate_discrete_domain(output_min, output_max)
    
    # Применяем правила нечёткого вывода
    aggregated_membership_values = apply_fuzzy_inference_rules(
        temperature_terms, heat_level_terms, inference_rules, 
        current_temperature, output_domain_values
    )
    
    # Выполняем дефаззификацию
    optimal_control_value = defuzzify_centroid(
        aggregated_membership_values, output_domain_values, 
        output_min, output_max
    )
    
    return optimal_control_value


if __name__ == "__main__":
    temperature_json_content = read_json_file("task4/temperature.json")
    heat_level_json_content = read_json_file("task4/heat_lvl.json")
    mapping_json_content = read_json_file("task4/mapping.json")

    current_measured_temperature = 23.0
    
    optimal_control_signal = main(
        temperature_json_content, 
        heat_level_json_content, 
        mapping_json_content, 
        current_measured_temperature
    )

    print(f"Текущая температура: {current_measured_temperature}°C")
    print(f"Оптимальное значение управления = {optimal_control_signal}")
    print(f"Рекомендуемый уровень нагрева: {optimal_control_signal}")